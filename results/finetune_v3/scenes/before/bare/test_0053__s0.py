import bpy
import math
import mathutils
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set units
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

# Helper: add material
def make_mat(name, color, rough=0.8, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat

# Materials
mat_wall   = make_mat("Wall",   (0.85, 0.82, 0.75, 1), 0.9)
mat_floor  = make_mat("Floor",  (0.55, 0.40, 0.28, 1), 0.9)
mat_cheese = make_mat("Cheese", (0.95, 0.80, 0.20, 1), 0.4)
mat_wood   = make_mat("Wood",   (0.45, 0.28, 0.15, 1), 0.7)
mat_red    = make_mat("Red",    (0.70, 0.10, 0.10, 1), 0.6)
mat_blue   = make_mat("Blue",   (0.10, 0.20, 0.60, 1), 0.6)
mat_green  = make_mat("Green",  (0.10, 0.50, 0.20, 1), 0.6)
mat_cloth  = make_mat("Cloth",  (0.90, 0.90, 0.95, 1), 0.95)
mat_thread = make_mat("Thread", (0.80, 0.60, 0.30, 1), 0.9)
mat_candle = make_mat("Candle", (0.95, 0.93, 0.88, 1), 0.3)
mat_flame  = make_mat("Flame",  (1.0, 0.6, 0.1, 1), 0.2)
mat_crumbs = make_mat("Crumbs", (0.85, 0.75, 0.55, 1), 0.9)
mat_door   = make_mat("Door",   (0.35, 0.22, 0.12, 1), 0.8)
mat_stone  = make_mat("Stone",  (0.60, 0.58, 0.55, 1), 0.9)

# ------------------------------------------------------------------
# ROOM  –  corner of two walls + floor
# ------------------------------------------------------------------
W = 2.0   # room width (x)
D = 2.0   # room depth (z)
H = 1.5   # wall height

# Floor
bpy.ops.mesh.primitive_plane_add(size=1, location=(W/2, 0, D/2))
floor = bpy.context.object
floor.name = "Floor"
floor.scale = (W, D, 1)
floor.data.materials.append(mat_floor)

# Back wall (along x, at z=0)
bpy.ops.mesh.primitive_plane_add(size=1, location=(W/2, H/2, 0))
back_wall = bpy.context.object
back_wall.name = "BackWall"
back_wall.scale = (W, H, 1)
back_wall.rotation_euler = (math.radians(90), 0, 0)
back_wall.data.materials.append(mat_wall)

# Left wall (along z, at x=0)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, H/2, D/2))
left_wall = bpy.context.object
left_wall.name = "LeftWall"
left_wall.scale = (D, H, 1)
left_wall.rotation_euler = (0, math.radians(90), 0)
left_wall.data.materials.append(mat_wall)

# ------------------------------------------------------------------
# ARCHED DOOR  –  on the left wall (x=0), near the back corner
# ------------------------------------------------------------------
door_cx = 0.0          # x of wall
door_cz = 0.45         # z position along wall
door_w  = 0.22         # width
door_h  = 0.30         # straight part height
arch_r  = door_w / 2   # arch radius

# Door frame (dark rectangle + arch)
# Straight sides
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(door_cx, door_h/2, door_cz + side*door_w/2))
    s = bpy.context.object
    s.name = f"DoorFrameSide{side}"
    s.scale = (0.03, door_h, 0.03)
    s.data.materials.append(mat_door)

# Top lintel (straight part of arch)
bpy.ops.mesh.primitive_cube_add(size=1, location=(door_cx, door_h, door_cz))
lintel = bpy.context.object
lintel.name = "DoorLintel"
lintel.scale = (0.03, 0.03, door_w)
lintel.data.materials.append(mat_door)

# Arch (half torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=arch_r, minor_radius=0.02,
    major_segments=32, minor_segments=8,
    location=(door_cx, door_h, door_cz)
)
arch = bpy.context.object
arch.name = "DoorArch"
arch.scale = (1, 1, 1)
# Cut to half: delete lower half vertices
import bmesh
bm = bmesh.new()
bm.from_mesh(arch.data)
for v in list(bm.verts):
    if v.co.y < -0.001:
        bm.verts.remove(v)
bm.to_mesh(arch.data)
bm.free()
arch.data.materials.append(mat_door)

# Door panel (slightly recessed)
bpy.ops.mesh.primitive_cube_add(size=1, location=(door_cx + 0.01, door_h/2, door_cz))
door_panel = bpy.context.object
door_panel.name = "DoorPanel"
door_panel.scale = (0.01, door_h, door_w * 0.9)
door_panel.data.materials.append(mat_stone)

# Arch opening in door panel (boolean would be complex; add a dark inset)
bpy.ops.mesh.primitive_cylinder_add(radius=arch_r, depth=0.02, location=(door_cx+0.015, door_h, door_cz))
arch_inset = bpy.context.object
arch_inset.name = "DoorArchInset"
arch_inset.rotation_euler = (0, math.radians(90), 0)
arch_inset.data.materials.append(mat_door)

# ------------------------------------------------------------------
# CHEESE WHEEL TABLE  –  small round table with a cheese wheel on top
# ------------------------------------------------------------------
tx, tz = 0.7, 0.7
th = 0.18  # table height

# Table top
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.02, location=(tx, th, tz))
table_top = bpy.context.object
table_top.name = "TableTop"
table_top.data.materials.append(mat_wood)

# Table leg
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=th, location=(tx, th/2, tz))
table_leg = bpy.context.object
table_leg.name = "TableLeg"
table_leg.data.materials.append(mat_wood)

# Cheese wheel
cheese_r = 0.08
cheese_h = 0.06
bpy.ops.mesh.primitive_cylinder_add(radius=cheese_r, depth=cheese_h, location=(tx, th + 0.01 + cheese_h/2, tz))
cheese = bpy.context.object
cheese.name = "CheeseWheel"
cheese.data.materials.append(mat_cheese)

# Cheese holes (small spheres embedded)
import random
random.seed(42)
for i in range(8):
    ang = random.uniform(0, 2*math.pi)
    rad = random.uniform(0.01, cheese_r*0.6)
    hx = tx + rad * math.cos(ang)
    hz = tz + rad * math.sin(ang)
    hy = th + 0.01 + random.uniform(0.005, cheese_h - 0.005)
    hr = random.uniform(0.008, 0.015)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=hr, segments=12, ring_count=8, location=(hx, hy, hz))
    hole = bpy.context.object
    hole.name = f"CheeseHole{i}"
    hole.data.materials.append(mat_wood)  # dark to look like hole

# ------------------------------------------------------------------
# MATCHBOX BEDS  –  two small boxes with tiny pillows
# ------------------------------------------------------------------
def make_matchbox_bed(bx, bz, color_mat, name):
    bw, bd, bh = 0.12, 0.08, 0.03
    # Box
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, bh/2, bz))
    bed = bpy.context.object
    bed.name = f"{name}_Box"
    bed.scale = (bw, bh, bd)
    bed.data.materials.append(color_mat)
    # Pillow
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx + bw/2 - 0.015, bh + 0.008, bz))
    pillow = bpy.context.object
    pillow.name = f"{name}_Pillow"
    pillow.scale = (0.03, 0.016, bd*0.7)
    pillow.data.materials.append(mat_cloth)
    # Blanket (thin slab on top)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx - bw/6, bh + 0.004, bz))
    blanket = bpy.context.object
    blanket.name = f"{name}_Blanket"
    blanket.scale = (bw*0.6, 0.008, bd*0.9)
    blanket.data.materials.append(mat_cloth)

make_matchbox_bed(1.3, 0.35, mat_red,  "Bed1")
make_matchbox_bed(1.3, 0.55, mat_blue, "Bed2")

# ------------------------------------------------------------------
# THREAD SPOOLS  –  small cylinders with thread wound around
# ------------------------------------------------------------------
def make_thread_spool(sx, sz, color_mat, name):
    sr = 0.025
    sh = 0.05
    # Core
    bpy.ops.mesh.primitive_cylinder_add(radius=sr, depth=sh, location=(sx, sh/2, sz))
    core = bpy.context.object
    core.name = f"{name}_Core"
    core.data.materials.append(mat_wood)
    # Thread (slightly larger cylinder, colored)
    bpy.ops.mesh.primitive_cylinder_add(radius=sr*0.85, depth=sh*0.7, location=(sx, sh/2, sz))
    thread = bpy.context.object
    thread.name = f"{name}_Thread"
    thread.data.materials.append(color_mat)
    # Top & bottom caps
    for dy in [sh/2, -sh/2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=sr*1.15, depth=0.005, location=(sx, sh/2+dy, sz))
        cap = bpy.context.object
        cap.name = f"{name}_Cap{dy}"
        cap.data.materials.append(mat_wood)

make_thread_spool(0.35, 0.25, mat_thread, "Spool1")
make_thread_spool(0.35, 0.40, mat_red,    "Spool2")
make_thread_spool(0.50, 0.30, mat_green,  "Spool3")

# ------------------------------------------------------------------
# CANDLE  –  small cylinder with a flame
# ------------------------------------------------------------------
cx, cz = 1.5, 0.15
ch = 0.08
# Candle body
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=ch, location=(cx, ch/2, cz))
candle = bpy.context.object
candle.name = "Candle"
candle.data.materials.append(mat_candle)
# Wick
bpy.ops.mesh.primitive_cylinder_add(radius=0.002, depth=0.015, location=(cx, ch + 0.007, cz))
wick = bpy.context.object
wick.name = "Wick"
wick.data.materials.append(mat_wood)
# Flame (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.008, radius2=0.0, depth=0.025, location=(cx, ch + 0.025, cz))
flame = bpy.context.object
flame.name = "Flame"
flame.data.materials.append(mat_flame)
# Point light for candle glow
light_data = bpy.data.lights.new("CandleLight", type='POINT')
light_data.energy = 5
light_data.color = (1.0, 0.7, 0.3)
light_data.shadow_soft_size = 0.05
light_obj = bpy.data.objects.new("CandleLight", light_data)
light_obj.location = (cx, ch + 0.03, cz)
bpy.context.collection.objects.link(light_obj)

# ------------------------------------------------------------------
# TRAIL OF CRUMBS  –  small spheres scattered from door to cheese table
# ------------------------------------------------------------------
import random
random.seed(99)
start = Vector((0.05, 0.02, door_cz))
end   = Vector((tx - 0.1, 0.02, tz))
num_crumbs = 25
for i in range(num_crumbs):
    t = i / (num_crumbs - 1)
    pos = start.lerp(end, t)
    # Add some scatter
    pos.x += random.uniform(-0.02, 0.02)
    pos.z += random.uniform(-0.03, 0.03)
    pos.y = 0.005
    r = random.uniform(0.004, 0.009)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=8, ring_count=6, location=pos)
    crumb = bpy.context.object
    crumb.name = f"Crumb{i}"
    crumb.data.materials.append(mat_crumbs)

# ------------------------------------------------------------------
# LIGHTING  –  ambient + sun
# ------------------------------------------------------------------
# Sun
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3
sun_data.color = (1.0, 0.95, 0.85)
sun_obj = bpy.data.objects.new("Sun", sun_data)
sun_obj.rotation_euler = (math.radians(45), math.radians(20), 0)
bpy.context.collection.objects.link(sun_obj)

# Fill light
fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 20
fill_data.size = 1.0
fill_obj = bpy.data.objects.new("Fill", fill_data)
fill_obj.location = (W/2, H + 0.5, D/2)
fill_obj.rotation_euler = (0, 0, 0)
bpy.context.collection.objects.link(fill_obj)

# World background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.15, 0.12, 0.10, 1)
    bg.inputs[1].default_value = 1.0

# Camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50
cam_obj = bpy.data.objects.new("Camera", cam_data)
cam_obj.location = (1.8, 1.2, 1.2)
cam_obj.rotation_euler = (math.radians(55), 0, math.radians(140))
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

print("Mouse house scene built successfully!")
