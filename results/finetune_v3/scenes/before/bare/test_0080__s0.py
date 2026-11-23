import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create collections
scene = bpy.context.scene
for col_name in ["Asteroid", "DrillRig", "OreHopper", "CargoPod", "CrewDome", "Lights"]:
    if col_name not in scene.collection.children:
        col = bpy.data.collections.new(col_name)
        scene.collection.children.link(col)

def get_col(name):
    return bpy.data.collections[name]

def add_to_col(obj, col_name):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    get_col(col_name).objects.link(obj)

# Helper: create mesh object
def create_obj(name, mesh_data, col_name):
    mesh = mesh_data
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    add_to_col(obj, col_name)
    return obj

# ==================== ASTEROID ====================
# Irregular rock shape
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=5.0, location=(0, 0, 0))
asteroid = bpy.context.active_object
asteroid.name = "Asteroid"
add_to_col(asteroid, "Asteroid")

# Deform with noise for rocky look
import bmesh
bm = bmesh.new()
bm.from_mesh(asteroid.data)
for v in bm.verts:
    # Add noise displacement
    n = random.uniform(-0.8, 0.8)
    v.co += v.co.normalized() * n
bm.to_mesh(asteroid.data)
bm.free()

# Smooth shading
bpy.ops.object.shade_smooth()

# Material for asteroid
mat_ast = bpy.data.materials.new("AsteroidMat")
mat_ast.use_nodes = True
nodes = mat_ast.node_tree.nodes
links = mat_ast.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.35, 0.3, 0.25, 1)
bsdf.inputs["Roughness"].default_value = 0.9
bsdf.inputs["Metallic"].default_value = 0.1
asteroid.data.materials.append(mat_ast)

# ==================== DRILL RIG ====================
# Base platform
bpy.ops.mesh.primitive_cylinder_add(radius=2.5, depth=0.5, location=(0, 0, 5.2))
drill_base = bpy.context.active_object
drill_base.name = "DrillBase"
add_to_col(drill_base, "DrillRig")
bpy.ops.object.shade_smooth()

# Support struts (4 legs)
for i in range(4):
    angle = i * math.pi / 2 + math.pi/4
    x = math.cos(angle) * 2.0
    y = math.sin(angle) * 2.0
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.5, location=(x, y, 4.0))
    strut = bpy.context.active_object
    strut.name = f"Strut_{i}"
    strut.rotation_euler = (0, 0, angle)
    add_to_col(strut, "DrillRig")
    bpy.ops.object.shade_smooth()

# Drill housing
bpy.ops.mesh.primitive_cube_add(size=1.5, location=(0, 0, 6.5))
drill_house = bpy.context.active_object
drill_house.name = "DrillHousing"
add_to_col(drill_house, "DrillRig")
bpy.ops.object.shade_smooth()

# Drill shaft (down into asteroid)
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=3.0, location=(0, 0, 4.0))
drill_shaft = bpy.context.active_object
drill_shaft.name = "DrillShaft"
add_to_col(drill_shaft, "DrillRig")
bpy.ops.object.shade_smooth()

# Drill bit (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.05, depth=1.0, location=(0, 0, 2.3))
drill_bit = bpy.context.active_object
drill_bit.name = "DrillBit"
drill_bit.rotation_euler = (math.pi, 0, 0)
add_to_col(drill_bit, "DrillRig")
bpy.ops.object.shade_smooth()

# Bolts on base
for i in range(8):
    angle = i * math.pi / 4
    bx = math.cos(angle) * 2.2
    by = math.sin(angle) * 2.2
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.15, location=(bx, by, 5.5))
    bolt = bpy.context.active_object
    bolt.name = f"Bolt_{i}"
    add_to_col(bolt, "DrillRig")
    bpy.ops.object.shade_smooth()

# Drill rig material
mat_drill = bpy.data.materials.new("DrillMat")
mat_drill.use_nodes = True
bsdf_d = mat_drill.node_tree.nodes["Principled BSDF"]
bsdf_d.inputs["Base Color"].default_value = (0.6, 0.5, 0.3, 1)
bsdf_d.inputs["Roughness"].default_value = 0.4
bsdf_d.inputs["Metallic"].default_value = 0.7
for obj_name in ["DrillBase", "DrillHousing", "DrillShaft", "DrillBit"]:
    obj = bpy.data.objects[obj_name]
    obj.data.materials.append(mat_drill)
for i in range(4):
    bpy.data.objects[f"Strut_{i}"].data.materials.append(mat_drill)
for i in range(8):
    bpy.data.objects[f"Bolt_{i}"].data.materials.append(mat_drill)

# ==================== ORE HOPPER ====================
# Funnel shape
bpy.ops.mesh.primitive_cone_add(radius1=1.8, radius2=0.5, depth=2.0, location=(4.0, 0, 5.5))
hopper = bpy.context.active_object
hopper.name = "OreHopper"
add_to_col(hopper, "OreHopper")
bpy.ops.object.shade_smooth()

# Hopper support legs
for i in range(3):
    angle = i * 2 * math.pi / 3
    lx = 4.0 + math.cos(angle) * 1.2
    ly = math.sin(angle) * 1.2
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2.0, location=(lx, ly, 4.0))
    leg = bpy.context.active_object
    leg.name = f"HopperLeg_{i}"
    add_to_col(leg, "OreHopper")
    bpy.ops.object.shade_smooth()

# Pipe from hopper to cargo pod
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=4.0, location=(6.5, 0, 5.5))
pipe = bpy.context.active_object
pipe.name = "OrePipe"
pipe.rotation_euler = (0, math.pi/2, 0)
add_to_col(pipe, "OreHopper")
bpy.ops.object.shade_smooth()

# Ore material
mat_ore = bpy.data.materials.new("OreMat")
mat_ore.use_nodes = True
bsdf_o = mat_ore.node_tree.nodes["Principled BSDF"]
bsdf_o.inputs["Base Color"].default_value = (0.4, 0.35, 0.3, 1)
bsdf_o.inputs["Roughness"].default_value = 0.5
bsdf_o.inputs["Metallic"].default_value = 0.6
hopper.data.materials.append(mat_ore)
pipe.data.materials.append(mat_ore)
for i in range(3):
    bpy.data.objects[f"HopperLeg_{i}"].data.materials.append(mat_ore)

# ==================== CARGO POD ====================
# Main pod body (elongated sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(10.0, 0, 5.5), segments=32, ring_count=16)
cargo_pod = bpy.context.active_object
cargo_pod.name = "CargoPod"
cargo_pod.scale = (1.5, 1.0, 1.0)
add_to_col(cargo_pod, "CargoPod")
bpy.ops.object.shade_smooth()

# Pod docking collar
bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.5, location=(8.5, 0, 5.5))
docking = bpy.context.active_object
docking.name = "DockingCollar"
docking.rotation_euler = (0, math.pi/2, 0)
add_to_col(docking, "CargoPod")
bpy.ops.object.shade_smooth()

# Tether cable (curve)
curve_data = bpy.data.curves.new("TetherCurve", 'CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.05
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(2)
# From pod to asteroid surface
spline.bezier_points[0].co = (8.5, 0, 5.5)
spline.bezier_points[0].handle_left = (7.5, 0.5, 5.5)
spline.bezier_points[0].handle_right = (7.5, -0.5, 5.5)
spline.bezier_points[1].co = (6.0, 0, 4.0)
spline.bezier_points[1].handle_left = (7.0, 0.5, 4.5)
spline.bezier_points[1].handle_right = (5.0, -0.5, 3.5)
spline.bezier_points[2].co = (3.5, 0, 3.0)
spline.bezier_points[2].handle_left = (4.5, 0.5, 3.5)
spline.bezier_points[2].handle_right = (3.0, -0.5, 2.5)
tether_obj = bpy.data.objects.new("TetherCable", curve_data)
bpy.context.scene.collection.objects.link(tether_obj)
add_to_col(tether_obj, "CargoPod")

# Cargo pod material
mat_cargo = bpy.data.materials.new("CargoMat")
mat_cargo.use_nodes = True
bsdf_c = mat_cargo.node_tree.nodes["Principled BSDF"]
bsdf_c.inputs["Base Color"].default_value = (0.5, 0.5, 0.55, 1)
bsdf_c.inputs["Roughness"].default_value = 0.3
bsdf_c.inputs["Metallic"].default_value = 0.8
cargo_pod.data.materials.append(mat_cargo)
docking.data.materials.append(mat_cargo)

# Tether material
mat_tether = bpy.data.materials.new("TetherMat")
mat_tether.use_nodes = True
bsdf_t = mat_tether.node_tree.nodes["Principled BSDF"]
bsdf_t.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1)
bsdf_t.inputs["Roughness"].default_value = 0.6
tether_obj.data.materials.append(mat_tether)

# ==================== CREW DOME ====================
# Dome (half sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(-4.0, 0, 5.0), segments=32, ring_count=16)
crew_dome = bpy.context.active_object
crew_dome.name = "CrewDome"
add_to_col(crew_dome, "CrewDome")
# Cut bottom half
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
bm = bmesh.new()
bm.from_mesh(crew_dome.data)
for v in bm.verts:
    v.select = v.co.z < 0
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.select], context='VERTS')
bm.to_mesh(crew_dome.data)
bm.free()
bpy.ops.object.shade_smooth()

# Dome base ring
bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.15, location=(-4.0, 0, 5.0), major_segments=32, minor_segments=8)
dome_ring = bpy.context.active_object
dome_ring.name = "DomeRing"
add_to_col(dome_ring, "CrewDome")
bpy.ops.object.shade_smooth()

# Support legs for dome
for i in range(4):
    angle = i * math.pi / 2 + math.pi/4
    dx = -4.0 + math.cos(angle) * 1.3
    dy = math.sin(angle) * 1.3
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2.0, location=(dx, dy, 4.0))
    dleg = bpy.context.active_object
    dleg.name = f"DomeLeg_{i}"
    add_to_col(dleg, "CrewDome")
    bpy.ops.object.shade_smooth()

# Window on dome (small sphere cutout representation - just a small emissive circle)
bpy.ops.mesh.primitive_circle_add(radius=0.3, location=(-2.5, 0, 5.8), fill_type='NGON')
window = bpy.context.active_object
window.name = "DomeWindow"
window.rotation_euler = (0, math.pi/2, 0)
add_to_col(window, "CrewDome")

# Crew dome material (translucent/glass-like)
mat_dome = bpy.data.materials.new("DomeMat")
mat_dome.use_nodes = True
bsdf_dm = mat_dome.node_tree.nodes["Principled BSDF"]
bsdf_dm.inputs["Base Color"].default_value = (0.7, 0.8, 0.9, 1)
bsdf_dm.inputs["Roughness"].default_value = 0.1
bsdf_dm.inputs["Metallic"].default_value = 0.0
bsdf_dm.inputs["Transmission Weight"].default_value = 0.8
bsdf_dm.inputs["IOR"].default_value = 1.5
crew_dome.data.materials.append(mat_dome)
dome_ring.data.materials.append(mat_dome)
for i in range(4):
    bpy.data.objects[f"DomeLeg_{i}"].data.materials.append(mat_dome)

# Window material (emissive)
mat_window = bpy.data.materials.new("WindowMat")
mat_window.use_nodes = True
nodes_w = mat_window.node_tree.nodes
links_w = mat_window.node_tree.links
# Remove default BSDF, use emission
for n in list(nodes_w):
    if n.name != "Material Output":
        nodes_w.remove(n)
emission = nodes_w.new("ShaderNodeEmission")
emission.inputs["Color"].default_value = (1.0, 0.9, 0.7, 1)
emission.inputs["Strength"].default_value = 5.0
links_w.new(emission.outputs["Emission"], nodes_w["Material Output"].inputs["Surface"])
window.data.materials.append(mat_window)

# ==================== LIGHTS ====================
# Interior light for crew dome (point light inside)
light_data = bpy.data.lights.new("DomeLight", type='POINT')
light_data.energy = 100
light_data.color = (1.0, 0.9, 0.7)
light_data.shadow_soft_size = 0.5
light_obj = bpy.data.objects.new("DomeInteriorLight", light_data)
light_obj.location = (-4.0, 0, 5.5)
bpy.context.scene.collection.objects.link(light_obj)
add_to_col(light_obj, "Lights")

# Small light for drill rig
light_data2 = bpy.data.lights.new("DrillLight", type='POINT')
light_data2.energy = 50
light_data2.color = (1.0, 1.0, 1.0)
light_data2.shadow_soft_size = 0.3
light_obj2 = bpy.data.objects.new("DrillLight", light_data2)
light_obj2.location = (0, 0, 7.0)
bpy.context.scene.collection.objects.link(light_obj2)
add_to_col(light_obj2, "Lights")

# Sun light for overall scene
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 2.0
sun_data.color = (1.0, 1.0, 1.0)
sun_obj = bpy.data.objects.new("Sun", sun_data)
sun_obj.rotation_euler = (math.radians(45), math.radians(30), 0)
bpy.context.scene.collection.objects.link(sun_obj)
add_to_col(sun_obj, "Lights")

# ==================== CAMERA ====================
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
cam_obj.location = (15, 12, 8)
cam_obj.rotation_euler = (math.radians(70), 0, math.radians(-45))
bpy.context.scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Set world background to dark space
world = bpy.data