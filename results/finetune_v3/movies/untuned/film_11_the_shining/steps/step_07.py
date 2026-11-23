import bpy
import math
import random
from mathutils import Vector

# The camera is pointing up. Fix it to look down at the scene.
cam = bpy.data.objects.get("Camera")
if cam:
    # Position camera high and in front, looking down at the maze and hotel
    cam.location = (25, 25, 50)
    # Target a point in the middle of the scene
    target = Vector((0, 5, -20))
    d = target - cam.location
    # Use to_track_quat with -Z as forward
    quat = d.to_track_quat('-Z', 'Y')
    cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = quat
    bpy.context.scene.camera = cam
else:
    bpy.ops.object.camera_add(location=(25, 25, 50))
    cam = bpy.context.active_object
    target = Vector((0, 5, -20))
    d = target - cam.location
    quat = d.to_track_quat('-Z', 'Y')
    cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = quat
    bpy.context.scene.camera = cam

# Make sure camera is linked to scene
if cam.name not in [o.name for o in bpy.context.collection.objects]:
    bpy.context.collection.objects.link(cam)

# --- ADD MORE HEDGE MAZE DETAIL: vary hedge heights slightly ---
for obj in bpy.context.collection.objects:
    if obj.type == 'MESH':
        # Check if it's a hedge (scale.y between 2 and 4, has hedge material)
        if 2.5 < obj.scale.y < 3.5:
            # Add slight random variation
            obj.scale.y = obj.scale.y + random.uniform(-0.2, 0.2)

# --- ADD MORE TREES in clusters ---
mat_snow_tree = bpy.data.materials.get("snow_tree_mat")
mat_trunk = bpy.data.materials.get("trunk_mat")

def add_tree(x, z, scale=1.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3*scale, depth=3*scale, location=(x, 1.5*scale, z))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_trunk)
    for i in range(4):
        h = 2.5 + i * 1.5
        r = (2.5 - i * 0.5) * scale
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=2.0*scale, location=(x, h*scale, z))
        cone = bpy.context.active_object
        cone.data.materials.append(mat_snow_tree)

# More trees around the perimeter
random.seed(99)
for _ in range(20):
    angle = random.uniform(0, 2*math.pi)
    dist = random.uniform(40, 70)
    tx = math.cos(angle) * dist
    tz = math.sin(angle) * dist
    if abs(tx) < 25 and tz < -35:
        continue
    add_tree(tx, tz, scale=random.uniform(0.7, 1.6))

# --- ADD SNOW-COVERED BENCHES near the path ---
mat_bench = bpy.data.materials.new("bench_mat")
mat_bench.use_nodes = True
mat_bench.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.12, 0.06, 1.0)
mat_bench.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8

for bz in [-8, -18, -28]:
    for bx in [-6, 6]:
        # Bench seat
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, 0.8, bz))
        seat = bpy.context.active_object
        seat.scale = (1.5, 0.4, 0.8)
        seat.data.materials.append(mat_bench)
        # Bench legs
        for lx in [-0.5, 0.5]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(bx + lx, 0.4, bz))
            leg = bpy.context.active_object
            leg.scale = (0.15, 0.4, 0.8)
            leg.data.materials.append(mat_bench)
        # Snow on bench
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, 1.1, bz))
        b_snow = bpy.context.active_object
        b_snow.scale = (1.5, 0.2, 0.8)
        b_snow.data.materials.append(bpy.data.materials.get("snow"))

# --- ADD LAMP POSTS along the path ---
mat_lamp = bpy.data.materials.new("lamp_mat")
mat_lamp.use_nodes = True
mat_lamp.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
mat_lamp.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5
mat_lamp.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.8

mat_lamp_glow = bpy.data.materials.new("lamp_glow")
mat_lamp_glow.use_nodes = True
bsdf_lg = mat_lamp_glow.node_tree.nodes["Principled BSDF"]
bsdf_lg.inputs["Emission Color"].default_value = (1.0, 0.8, 0.4, 1.0)
bsdf_lg.inputs["Emission Strength"].default_value = 5.0
bsdf_lg.inputs["Base Color"].default_value = (1.0, 0.8, 0.4, 1.0)

for lz in [-5, -15, -25, -35]:
    for lx in [-4, 4]:
        # Pole
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=4, location=(lx, 2, lz))
        pole = bpy.context.active_object
        pole.data.materials.append(mat_lamp)
        # Lamp head
        bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, 4.2, lz))
        head = bpy.context.active_object
        head.scale = (0.4, 0.4, 0.4)
        head.data.materials.append(mat_lamp)
        # Glow
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(lx, 4.0, lz))
        glow = bpy.context.active_object
        glow.data.materials.append(mat_lamp_glow)
        # Point light
        bpy.ops.object.light_add(type='POINT', location=(lx, 4, lz))
        pl = bpy.context.active_object
        pl.data.energy = 15
        pl.data.color = (1.0, 0.75, 0.35)
        pl.data.shadow_soft_size = 1

# --- ADD MORE SNOW DRIFTS ---
for _ in range(20):
    dx = random.uniform(-40, 40)
    dz = random.uniform(-30, 30)
    if abs(dx) < 5 and dz > -10:
        continue
    dr = random.uniform(1.5, 4)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=dr, location=(dx, 0, dz))
    drift = bpy.context.active_object
    drift.scale = (1, 0.25, 1)
    drift.data.materials.append(bpy.data.materials.get("snow"))

# --- ADD HOTEL SIDE WINGS ---
hotel_x = 0
hotel_z = -55
hotel_depth = 20
hotel_height = 25

# Left wing
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x - 25, hotel_height*0.6/2, hotel_z))
left_wing = bpy.context.active_object
left_wing.scale = (10, hotel_height*0.6, hotel_depth*0.8)
left_wing.data.materials.append(bpy.data.materials.get("hotel_wall"))

# Left wing roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x - 25, hotel_height*0.6 + 0.5, hotel_z))
lw_roof = bpy.context.active_object
lw_roof.scale = (11, 1, hotel_depth*0.8 + 1)
lw_roof.data.materials.append(bpy.data.materials.get("hotel_roof"))

# Left wing snow
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x - 25, hotel_height*0.6 + 1.2, hotel_z))
lw_snow = bpy.context.active_object
lw_snow.scale = (11, 0.4, hotel_depth*0.8 + 1)
lw_snow.data.materials.append(bpy.data.materials.get("snow"))

# Left wing windows
front_z_lw = hotel_z + hotel_depth*0.8/2 + 0.1
for floor in range(3):
    y = 2 + floor * 4
    for x_off in range(-2, 3):
        x = hotel_x - 25 + x_off * 3
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, front_z_lw))
        win = bpy.context.active_object
        win.scale = (1.2, 1.5, 1)
        win.rotation_euler = (math.radians(90), 0, 0)
        if random.random() < 0.5:
            win.data.materials.append(bpy.data.materials.get("window_lit"))
        else:
            win.data.materials.append(bpy.data.materials.get("window_dark"))

# Right wing
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x + 25, hotel_height*0.6/2, hotel_z))
right_wing = bpy.context.active_object
right_wing.scale = (10, hotel_height*0.6, hotel_depth*0.8)
right_wing.data.materials.append(bpy.data.materials.get("hotel_wall"))

bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x + 25, hotel_height*0.6 + 0.5, hotel_z))
rw_roof = bpy.context.active_object
rw_roof.scale = (11, 1, hotel_depth*0.8 + 1)
rw_roof.data.materials.append(bpy.data.materials.get("hotel_roof"))

bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x + 25, hotel_height*0.6 + 1.2, hotel_z))
rw_snow = bpy.context.active_object
rw_snow.scale = (11, 0.4, hotel_depth*0.8 + 1)
rw_snow.data.materials.append(bpy.data.materials.get("snow"))

front_z_rw = hotel_z + hotel_depth*0.8/2 + 0.1
for floor in range(3):
    y = 2 + floor * 4
    for x_off in range(-2, 3):
        x = hotel_x + 25 + x_off * 3
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, front_z_rw))
        win = bpy.context.active_object
        win.scale = (1.2, 1.5, 1)
        win.rotation_euler = (math.radians(90), 0, 0)
        if random.random() < 0.5:
            win.data.materials.append(bpy.data.materials.get("window_lit"))
        else:
            win.data.materials.append(bpy.data.materials.get("window_dark"))

# --- RENDER ---
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0.3
scene.frame_set(100)

print("Camera fixed, wings, benches, lamp posts, more trees and drifts added!")
