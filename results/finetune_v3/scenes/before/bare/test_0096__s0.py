import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.object.select_all(action='DESELECT')

# ---- Materials ----
def make_mat(name, base, metallic=0.0, rough=0.6, spec=0.5, emission=0.0, em_color=(0,0,0,1)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = spec
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = em_color
        bsdf.inputs["Emission Strength"].default_value = emission
    return m

mat_ice      = make_mat("Ice",      (0.75, 0.85, 0.95, 1), 0.0, 0.05, 0.9)
mat_frame    = make_mat("Frame",    (0.85, 0.85, 0.90, 1), 0.9, 0.25, 0.8)
mat_seat     = make_mat("Seat",     (0.15, 0.15, 0.18, 1), 0.0, 0.7, 0.3)
mat_helmet   = make_mat("Helmet",   (0.95, 0.95, 0.95, 1), 0.0, 0.3, 0.7)
mat_hut_wall = make_mat("HutWall",  (0.55, 0.40, 0.28, 1), 0.0, 0.8, 0.2)
mat_hut_roof = make_mat("HutRoof",  (0.35, 0.25, 0.18, 1), 0.0, 0.85, 0.1)
mat_flag     = make_mat("Flag",     (0.95, 0.20, 0.10, 1), 0.0, 0.6, 0.4)
mat_pole     = make_mat("Pole",     (0.60, 0.60, 0.65, 1), 0.8, 0.3, 0.7)
mat_peg      = make_mat("Peg",      (0.40, 0.30, 0.20, 1), 0.0, 0.7, 0.3)
mat_snow     = make_mat("Snow",     (0.90, 0.93, 0.97, 1), 0.0, 0.9, 0.3)
mat_dark     = make_mat("Dark",     (0.05, 0.05, 0.05, 1), 0.0, 0.9, 0.2)
mat_glow     = make_mat("Glow",     (1.0, 0.85, 0.55, 1), 0.0, 0.5, 0.5, emission=2.0, em_color=(1.0, 0.8, 0.4, 1))

# ---- Ground / Ice Chute ----
# Main flat ground
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
ground = bpy.context.object
ground.data.materials.append(mat_snow)

# Ice chute – long sloped plane going into the distance
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 35, -3))
chute = bpy.context.object
chute.scale = (4, 50, 1)
chute.rotation_euler = (math.radians(-12), 0, 0)
chute.data.materials.append(mat_ice)

# Chute walls (two side rails)
for side in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(location=(side*4.2, 35, -1.5))
    wall = bpy.context.object
    wall.scale = (0.3, 50, 2.5)
    wall.rotation_euler = (math.radians(-12), 0, 0)
    wall.data.materials.append(mat_frame)

# Start ramp (raised platform where sled sits)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
ramp = bpy.context.object
ramp.scale = (5, 6, 0.5)
ramp.data.materials.append(mat_ice)

# Ramp edges / rails
for side in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(location=(side*5, 0, 0.8))
    rail = bpy.context.object
    rail.scale = (0.2, 6, 0.4)
    rail.data.materials.append(mat_frame)

# ---- Four-man Sled ----
# Sled base (metal frame)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.2))
sled_base = bpy.context.object
sled_base.scale = (1.8, 3.5, 0.15)
sled_base.data.materials.append(mat_frame)

# Sled runners (two long bars underneath)
for side in (-1, 1):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=4.0, location=(side*1.5, 0, 0.05), rotation=(0, math.radians(90), 0))
    runner = bpy.context.object
    runner.data.materials.append(mat_frame)

# Cross bars on frame
for i, z in enumerate([0.4, 0.6]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=3.6, location=(0, 0, z), rotation=(0, math.radians(90), 0))
    bar = bpy.context.object
    bar.data.materials.append(mat_frame)

# Seats (4 rows)
for i, y in enumerate([-1.2, -0.4, 0.4, 1.2]):
    bpy.ops.mesh.primitive_cube_add(location=(0, y, 0.75))
    seat = bpy.context.object
    seat.scale = (1.4, 0.35, 0.12)
    seat.data.materials.append(mat_seat)
    # Seat back
    bpy.ops.mesh.primitive_cube_add(location=(0, y + 0.25, 1.05))
    back = bpy.context.object
    back.scale = (1.4, 0.08, 0.35)
    back.data.materials.append(mat_seat)

# Front brake bar
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=3.8, location=(0, -2.0, 0.5), rotation=(0, math.radians(90), 0))
brake = bpy.context.object
brake.data.materials.append(mat_frame)

# ---- Hut beside the ramp ----
# Hut body
bpy.ops.mesh.primitive_cube_add(location=(-9, 2, 1.5))
hut_body = bpy.context.object
hut_body.scale = (3, 4, 1.5)
hut_body.data.materials.append(mat_hut_wall)

# Hut roof (prism-like: use a cone with 4 verts scaled)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=4.5, radius2=0, depth=2.0, location=(-9, 2, 3.5))
hut_roof = bpy.context.object
hut_roof.rotation_euler = (0, 0, math.radians(45))
hut_roof.scale = (1, 1.2, 1)
hut_roof.data.materials.append(mat_hut_roof)

# Hut door
bpy.ops.mesh.primitive_cube_add(location=(-9, 5.5, 1.0))
door = bpy.context.object
door.scale = (0.8, 0.1, 1.0)
door.data.materials.append(mat_dark)

# Hut window (glowing)
bpy.ops.mesh.primitive_cube_add(location=(-11, 5.5, 1.5))
window = bpy.context.object
window.scale = (0.6, 0.1, 0.5)
window.data.materials.append(mat_glow)

# Hut chimney
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.5, location=(-10, 1, 4.2))
chimney = bpy.context.object
chimney.data.materials.append(mat_dark)

# ---- Helmets on pegs (on a wall beside the ramp) ----
# Peg board
bpy.ops.mesh.primitive_cube_add(location=(7, 0, 1.5))
peg_board = bpy.context.object
peg_board.scale = (0.1, 3, 1.5)
peg_board.data.materials.append(mat_peg)

# 4 helmets on pegs
for i, y in enumerate([-1.5, -0.5, 0.5, 1.5]):
    # Peg
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.5, location=(6.7, y, 1.5), rotation=(0, math.radians(90), 0))
    peg = bpy.context.object
    peg.data.materials.append(mat_peg)
    # Helmet (UV sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(6.4, y, 1.5))
    helmet = bpy.context.object
    helmet.scale = (1, 1, 0.9)
    helmet.data.materials.append(mat_helmet)

# ---- Starter's Flag ----
# Flag pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=4.0, location=(3, -3, 2.0))
flag_pole = bpy.context.object
flag_pole.data.materials.append(mat_pole)

# Flag (plane)
bpy.ops.mesh.primitive_plane_add(size=1, location=(3.5, -3, 3.5))
flag = bpy.context.object
flag.scale = (1.2, 0.8, 1)
flag.rotation_euler = (0, math.radians(15), 0)
flag.data.materials.append(mat_flag)

# ---- Dawn Lighting ----
# Sun (low angle, warm)
bpy.ops.object.light_add(type='SUN', location=(0, -20, 5))
sun = bpy.context.object
sun.rotation_euler = (math.radians(75), 0, math.radians(20))
sun.data.energy = 3.0
sun.data.color = (1.0, 0.75, 0.5)
sun.data.angle = math.radians(5)

# Fill light (cool, from opposite)
bpy.ops.object.light_add(type='AREA', location=(10, 10, 8))
fill = bpy.context.object
fill.rotation_euler = (math.radians(45), 0, math.radians(135))
fill.data.energy = 50
fill.data.color = (0.5, 0.6, 0.9)
fill.data.size = 5

# Warm point light near hut window
bpy.ops.object.light_add(type='POINT', location=(-9, 5.8, 1.5))
window_light = bpy.context.object
window_light.data.energy = 30
window_light.data.color = (1.0, 0.8, 0.4)
window_light.data.shadow_soft_size = 0.5

# World – dawn sky gradient
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

bg = nodes.new('ShaderNodeBackground')
bg.inputs[1].default_value = 0.3

# Sky texture for dawn
sky = nodes.new('ShaderNodeTexSky')
sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(5)
sky.sun_rotation = math.radians(20)
sky.sun_intensity = 0.5
sky.altitude = 100

out = nodes.new('ShaderNodeOutputWorld')
links.new(sky.outputs[0], bg.inputs[0])
links.new(bg.outputs[0], out.inputs[0])

# Camera
bpy.ops.object.camera_add(location=(8, -12, 4))
cam = bpy.context.object
cam.rotation_euler = (math.radians(75), 0, math.radians(30))
cam.data.lens = 35
bpy.context.scene.camera = cam

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
