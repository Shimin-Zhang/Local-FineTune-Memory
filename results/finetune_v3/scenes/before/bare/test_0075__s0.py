import bpy
import math
import random
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set units
bpy.context.scene.unit_settings.system = 'METRIC'

# Camera setup
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
cam.location = (18, 22, 6)
cam.rotation_euler = (math.radians(75), 0, math.radians(-45))
cam_data.lens = 35

# World - drizzle overcast
world = bpy.data.worlds.new("DrizzleWorld")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.55, 0.58, 0.62, 1.0)  # grey drizzle sky
bg.inputs[1].default_value = 1.0

# Sun (dim, diffuse)
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 0.3
sun_data.angle = math.radians(15)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(180))

# Materials
def make_mat(name, color, rough=0.8, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat

mat_cottage_wall = make_mat("CottageWall", (0.75, 0.72, 0.68), rough=0.9)
mat_roof_slate = make_mat("SlateRoof", (0.15, 0.18, 0.22), rough=0.6)
mat_chimney = make_mat("Chimney", (0.35, 0.28, 0.22), rough=0.95)
mat_door = make_mat("Door", (0.2, 0.15, 0.1), rough=0.8)
mat_window = make_mat("Window", (0.4, 0.45, 0.5), rough=0.3)
mat_wall_stone = make_mat("WalledYard", (0.45, 0.42, 0.38), rough=0.95)
mat_spoil = make_mat("GreySpoil", (0.35, 0.36, 0.38), rough=1.0)
mat_ground = make_mat("Ground", (0.25, 0.3, 0.18), rough=1.0)
mat_ewe = make_mat("Ewe", (0.9, 0.88, 0.85), rough=0.9)
mat_lamb = make_mat("Lamb", (0.95, 0.93, 0.9), rough=0.9)
mat_gate = make_mat("Gate", (0.15, 0.12, 0.1), rough=0.7)

# Helper: add cube
def add_box(name, loc, scale, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj

# Ground
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object
ground.data.materials.append(mat_ground)

# Hillside of grey spoil behind cottage
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, -25, 3))
hill = bpy.context.active_object
hill.rotation_euler = (math.radians(-15), 0, 0)
hill.data.materials.append(mat_spoil)
# Add some displacement feel with extra boxes
for i in range(15):
    x = random.uniform(-15, 15)
    y = random.uniform(-40, -15)
    z = random.uniform(0, 6)
    add_box(f"spoil_{i}", (x, y, z), (random.uniform(2,5), random.uniform(2,4), random.uniform(1,3)), mat_spoil)

# Cottage
cottage_loc = (0, -5, 0)
# Main walls
add_box("CottageBody", (cottage_loc[0], cottage_loc[1], 2), (4, 3, 2), mat_cottage_wall)

# Roof (slate) - two sloped planes
roof_w, roof_d, roof_h = 4.5, 3.5, 1.5
# Left slope
bpy.ops.mesh.primitive_plane_add(size=1, location=(cottage_loc[0] - roof_w/4, cottage_loc[1], 2 + roof_h))
roof_l = bpy.context.active_object
roof_l.scale = (roof_w/2, roof_d, 1)
roof_l.rotation_euler = (0, math.radians(30), 0)
roof_l.data.materials.append(mat_roof_slate)

# Right slope
bpy.ops.mesh.primitive_plane_add(size=1, location=(cottage_loc[0] + roof_w/4, cottage_loc[1], 2 + roof_h))
roof_r = bpy.context.active_object
roof_r.scale = (roof_w/2, roof_d, 1)
roof_r.rotation_euler = (0, math.radians(-30), 0)
roof_r.data.materials.append(mat_roof_slate)

# Ridge
add_box("Ridge", (cottage_loc[0], cottage_loc[1], 2 + roof_h + 0.1), (0.2, roof_d, 0.15), mat_roof_slate)

# Chimney
add_box("Chimney", (cottage_loc[0] + 2.5, cottage_loc[1] - 1, 3.5), (0.5, 0.5, 1.5), mat_chimney)
add_box("ChimneyCap", (cottage_loc[0] + 2.5, cottage_loc[1] - 1, 4.3), (0.6, 0.6, 0.15), mat_chimney)

# Door
add_box("Door", (cottage_loc[0] - 1, cottage_loc[1] + 3.01, 1), (0.5, 0.05, 1), mat_door)

# Windows
add_box("WindowL", (cottage_loc[0] - 2, cottage_loc[1] + 3.01, 1.5), (0.6, 0.05, 0.6), mat_window)
add_box("WindowR", (cottage_loc[0] + 1.5, cottage_loc[1] + 3.01, 1.5), (0.6, 0.05, 0.6), mat_window)

# Walled yard
yard_w, yard_d = 12, 10
wall_h = 1.5
# Front wall (with gap for gate)
add_box("YardWallL", (-yard_w/4, yard_d/2 - 5, wall_h/2), (yard_w/4 - 0.5, 0.3, wall_h/2), mat_wall_stone)
add_box("YardWallR", (yard_w/4, yard_d/2 - 5, wall_h/2), (yard_w/4 - 0.5, 0.3, wall_h/2), mat_wall_stone)
# Gate posts
add_box("GatePostL", (-0.8, yard_d/2 - 5, wall_h/2 + 0.2), (0.2, 0.2, wall_h/2 + 0.2), mat_gate)
add_box("GatePostR", (0.8, yard_d/2 - 5, wall_h/2 + 0.2), (0.2, 0.2, wall_h/2 + 0.2), mat_gate)
# Gate bars
for i in range(5):
    x = -0.6 + i * 0.3
    add_box(f"GateBar_{i}", (x, yard_d/2 - 5, wall_h/2), (0.05, 0.05, wall_h/2), mat_gate)
# Side walls
add_box("YardWallSideL", (-yard_w/2, 0, wall_h/2), (0.3, yard_d/2, wall_h/2), mat_wall_stone)
add_box("YardWallSideR", (yard_w/2, 0, wall_h/2), (0.3, yard_d/2, wall_h/2), mat_wall_stone)
# Back wall (partial, behind cottage)
add_box("YardWallBack", (0, -yard_d/2, wall_h/2), (yard_w/2, 0.3, wall_h/2), mat_wall_stone)

# Ewe
ewe_loc = (-1.5, 3.5, 0)
add_box("EweBody", (ewe_loc[0], ewe_loc[1], 0.6), (0.5, 0.8, 0.4), mat_ewe)
add_box("EweHead", (ewe_loc[0], ewe_loc[1] + 0.9, 0.7), (0.2, 0.3, 0.25), mat_ewe)
add_box("EweLeg1", (ewe_loc[0] - 0.2, ewe_loc[1] - 0.3, 0.2), (0.08, 0.08, 0.2), mat_ewe)
add_box("EweLeg2", (ewe_loc[0] + 0.2, ewe_loc[1] - 0.3, 0.2), (0.08, 0.08, 0.2), mat_ewe)
add_box("EweLeg3", (ewe_loc[0] - 0.2, ewe_loc[1] + 0.3, 0.2), (0.08, 0.08, 0.2), mat_ewe)
add_box("EweLeg4", (ewe_loc[0] + 0.2, ewe_loc[1] + 0.3, 0.2), (0.08, 0.08, 0.2), mat_ewe)

# Lamb
lamb_loc = (-0.5, 4.0, 0)
add_box("LambBody", (lamb_loc[0], lamb_loc[1], 0.35), (0.3, 0.5, 0.25), mat_lamb)
add_box("LambHead", (lamb_loc[0], lamb_loc[1] + 0.55, 0.4), (0.12, 0.2, 0.15), mat_lamb)
add_box("LambLeg1", (lamb_loc[0] - 0.12, lamb_loc[1] - 0.2, 0.1), (0.05, 0.05, 0.1), mat_lamb)
add_box("LambLeg2", (lamb_loc[0] + 0.12, lamb_loc[1] - 0.2, 0.1), (0.05, 0.05, 0.1), mat_lamb)
add_box("LambLeg3", (lamb_loc[0] - 0.12, lamb_loc[1] + 0.2, 0.1), (0.05, 0.05, 0.1), mat_lamb)
add_box("LambLeg4", (lamb_loc[0] + 0.12, lamb_loc[1] + 0.2, 0.1), (0.05, 0.05, 0.1), mat_lamb)

# Drizzle effect - small particles (approximated with tiny planes/lines)
# Use a particle system or just scatter small dark specks
for i in range(200):
    x = random.uniform(-20, 20)
    y = random.uniform(-20, 20)
    z = random.uniform(0.5, 8)
    bpy.ops.mesh.primitive_plane_add(size=0.02, location=(x, y, z))
    drop = bpy.context.active_object
    drop.rotation_euler = (math.radians(random.uniform(70, 90)), 0, 0)
    drop.data.materials.append(make_mat(f"drop_{i}", (0.6, 0.65, 0.7), rough=0.2, metal=0.3))

# Enable soft shadows
bpy.context.scene.render.use_shadows = True
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
