import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Collections
for name in ["Terrain", "Water", "Machinery", "Heaps", "Pit"]:
    if name not in bpy.data.collections:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)

def get_coll(name):
    return bpy.data.collections[name]

def link_obj(obj, coll_name):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    get_coll(coll_name).objects.link(obj)

# ---------- MATERIALS ----------
def make_mat(name, color, rough=0.8, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return m

mat_ground   = make_mat("Ground",  (0.35, 0.30, 0.22, 1), rough=0.9)
mat_gravel   = make_mat("Gravel",  (0.55, 0.52, 0.48, 1), rough=0.95)
mat_water    = make_mat("Water",   (0.15, 0.35, 0.55, 1), rough=0.1, metal=0.1)
mat_water_pit= make_mat("WaterPit",(0.10, 0.25, 0.45, 1), rough=0.15)
mat_steel    = make_mat("Steel",   (0.4, 0.42, 0.45, 1), rough=0.3, metal=0.8)
mat_orange   = make_mat("Orange",  (0.9, 0.4, 0.1, 1), rough=0.6)
mat_dark     = make_mat("Dark",    (0.15, 0.15, 0.15, 1), rough=0.7)
mat_yellow   = make_mat("Yellow",  (0.9, 0.8, 0.1, 1), rough=0.5)
mat_heap_s   = make_mat("HeapS",   (0.6, 0.55, 0.5, 1), rough=0.95)
mat_heap_m   = make_mat("HeapM",   (0.5, 0.45, 0.4, 1), rough=0.95)
mat_heap_l   = make_mat("HeapL",   (0.4, 0.38, 0.35, 1), rough=0.95)

# ---------- TERRAIN ----------
# Base ground plane
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(mat_ground)
link_obj(ground, "Terrain")

# Gravel pit depression (excavated area)
# We'll use a mesh with a hole/depression via a grid
bpy.ops.mesh.primitive_grid_add(x_subdivisions=40, y_subdivisions=40, size=80, location=(0, 0, 0))
pit_mesh = bpy.context.object
pit_mesh.name = "PitSurface"
# Displace to create pit shape
import bmesh
bm = bmesh.from_edit_mesh(pit_mesh.data)
for v in bm.verts:
    x, y = v.co.x, v.co.y
    # Pit center at (-20, 0), radius ~25
    dist = math.sqrt((x + 20)**2 + y**2)
    if dist < 25:
        depth = 8 * (1 - (dist/25)**2)
        v.co.z = -depth
    else:
        v.co.z = 0
bmesh.update_edit_mesh(pit_mesh.data)
pit_mesh.data.materials.append(mat_gravel)
link_obj(pit_mesh, "Pit")

# Flooded pit behind (to the north, +Y)
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 40, -2))
flood = bpy.context.object
flood.name = "FloodedPit"
flood.scale = (1.5, 1.0, 1.0)
flood.data.materials.append(mat_water_pit)
link_obj(flood, "Water")

# Water in main pit (lower level)
bpy.ops.mesh.primitive_plane_add(size=45, location=(-20, 0, -5))
pit_water = bpy.context.object
pit_water.name = "PitWater"
pit_water.data.materials.append(mat_water)
link_obj(pit_water, "Water")

# ---------- GRAVEL HEAPS ----------
def make_heap(name, loc, radius, height, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=radius, location=loc)
    heap = bpy.context.object
    heap.name = name
    heap.scale = (1, 1, height/radius)
    # Cut bottom half by moving origin
    bpy.ops.object.transform_apply(scale=True)
    heap.data.materials.append(mat)
    link_obj(heap, "Heaps")
    return heap

# Small heaps
make_heap("HeapSmall1", (15, -15, 0), 3, 2, mat_heap_s)
make_heap("HeapSmall2", (18, -10, 0), 2.5, 1.5, mat_heap_s)
make_heap("HeapSmall3", (12, -20, 0), 3.5, 2.5, mat_heap_s)

# Medium heaps
make_heap("HeapMed1", (25, -5, 0), 6, 4, mat_heap_m)
make_heap("HeapMed2", (22, 5, 0), 5, 3.5, mat_heap_m)

# Large heaps
make_heap("HeapLarge1", (35, 15, 0), 10, 7, mat_heap_l)
make_heap("HeapLarge2", (30, 25, 0), 12, 8, mat_heap_l)

# ---------- DREDGER (floating in pit water) ----------
dredger_loc = (-20, 0, -4.5)

# Hull
bpy.ops.mesh.primitive_cube_add(size=1, location=dredger_loc)
hull = bpy.context.object
hull.name = "DredgerHull"
hull.scale = (8, 4, 1.5)
hull.data.materials.append(mat_orange)
link_obj(hull, "Machinery")

# Cabin
bpy.ops.mesh.primitive_cube_add(size=1, location=(dredger_loc[0]-2, dredger_loc[1], dredger_loc[2]+2.5))
cabin = bpy.context.object
cabin.name = "DredgerCabin"
cabin.scale = (3, 3, 2)
cabin.data.materials.append(mat_yellow)
link_obj(cabin, "Machinery")

# Dredge arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=10, location=(dredger_loc[0]+5, dredger_loc[1], dredger_loc[2]+1))
arm = bpy.context.object
arm.name = "DredgerArm"
arm.rotation_euler = (0, math.radians(45), 0)
arm.data.materials.append(mat_steel)
link_obj(arm, "Machinery")

# Dredge bucket
bpy.ops.mesh.primitive_cube_add(size=1, location=(dredger_loc[0]+9, dredger_loc[1], dredger_loc[2]-1))
bucket = bpy.context.object
bucket.name = "DredgerBucket"
bucket.scale = (2, 2, 1.5)
bucket.data.materials.append(mat_dark)
link_obj(bucket, "Machinery")

# ---------- CONVEYOR (from dredger to sorting plant) ----------
# Conveyor: long inclined structure
conv_start = Vector((dredger_loc[0]+10, dredger_loc[1], dredger_loc[2]+2))
conv_end   = Vector((15, -5, 5))  # to sorting plant area
conv_len = (conv_end - conv_start).length
conv_mid = (conv_start + conv_end) / 2
conv_dir = (conv_end - conv_start).normalized()
conv_angle = math.atan2(conv_dir.y, conv_dir.x)
conv_pitch = math.asin(conv_dir.z)

# Conveyor belt (box)
bpy.ops.mesh.primitive_cube_add(size=1, location=conv_mid)
belt = bpy.context.object
belt.name = "ConveyorBelt"
belt.scale = (conv_len/2, 1.5, 0.5)
belt.rotation_euler = (0, -conv_pitch, conv_angle)
belt.data.materials.append(mat_dark)
link_obj(belt, "Machinery")

# Conveyor legs
for t in [0.2, 0.5, 0.8]:
    leg_pos = conv_start.lerp(conv_end, t)
    leg_height = leg_pos.z
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=leg_height, location=(leg_pos.x, leg_pos.y, leg_height/2))
    leg = bpy.context.object
    leg.name = f"ConveyorLeg_{t}"
    leg.data.materials.append(mat_steel)
    link_obj(leg, "Machinery")

# ---------- SORTING PLANT ----------
plant_loc = (15, -5, 5)

# Main building
bpy.ops.mesh.primitive_cube_add(size=1, location=(plant_loc[0], plant_loc[1], plant_loc[2]+3))
plant = bpy.context.object
plant.name = "SortingPlant"
plant.scale = (8, 6, 3)
plant.data.materials.append(mat_steel)
link_obj(plant, "Machinery")

# Hopper
bpy.ops.mesh.primitive_cone_add(radius1=4, radius2=2, depth=4, location=(plant_loc[0]-5, plant_loc[1], plant_loc[2]+4))
hopper = bpy.context.object
hopper.name = "PlantHopper"
hopper.data.materials.append(mat_orange)
link_obj(hopper, "Machinery")

# Conveyor into plant
bpy.ops.mesh.primitive_cube_add(size=1, location=(plant_loc[0]-3, plant_loc[1], plant_loc[2]+2))
conv_in = bpy.context.object
conv_in.name = "PlantConveyor"
conv_in.scale = (4, 1.5, 0.5)
conv_in.data.materials.append(mat_dark)
link_obj(conv_in, "Machinery")

# ---------- ADDITIONAL DETAILS ----------
# Gravel texture on heaps via displacement (simple noise)
for heap in [obj for obj in bpy.data.objects if obj.name.startswith("Heap")]:
    tex = bpy.data.textures.new(f"GravelTex_{heap.name}", type='CLOUDS')
    tex.noise_scale = 0.5
    mod = heap.modifiers.new("GravelDisp", 'DISPLACE')
    mod.texture = tex
    mod.strength = 0.3

# Camera
bpy.ops.object.camera_add(location=(60, -60, 30))
cam = bpy.context.object
cam.name = "Camera"
# Point camera at scene center
direction = Vector((0, 0, 0)) - cam.location
cam.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# Sun light
bpy.ops.object.light_add(type='SUN', location=(50, -50, 80))
sun = bpy.context.object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# World background
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.7, 0.8, 0.9, 1)
bg.inputs[1].default_value = 1.0

print("Gravel pit scene built successfully.")
