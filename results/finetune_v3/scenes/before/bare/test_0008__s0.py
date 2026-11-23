import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Materials
def mat(name, col, rough=0.8, metal=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = col
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
    return m

mat_ground   = mat("Ground",   (0.35, 0.25, 0.12, 1), 0.95)
mat_dirt     = mat("Dirt",     (0.28, 0.18, 0.08, 1), 0.95)
mat_stone    = mat("Stone",    (0.55, 0.52, 0.48, 1), 0.9)
mat_stone_d  = mat("StoneDark",(0.35, 0.33, 0.30, 1), 0.9)
mat_wood     = mat("Wood",     (0.45, 0.30, 0.15, 1), 0.85)
mat_wood_d   = mat("WoodDark", (0.30, 0.20, 0.10, 1), 0.85)
mat_roof     = mat("Roof",     (0.20, 0.15, 0.10, 1), 0.9)
mat_thatch   = mat("Thatch",   (0.55, 0.45, 0.20, 1), 0.95)
mat_linen    = mat("Linen",    (0.85, 0.82, 0.75, 1), 0.9)
mat_thread   = mat("Thread",   (0.70, 0.68, 0.60, 1), 0.9)
mat_pig      = mat("Pig",      (0.75, 0.55, 0.50, 1), 0.7)
mat_veg      = mat("Veg",      (0.20, 0.45, 0.15, 1), 0.9)
mat_veg2     = mat("Veg2",     (0.30, 0.50, 0.20, 1), 0.9)
mat_mud      = mat("Mud",      (0.20, 0.15, 0.10, 1), 0.95)

# ---------- GROUND ----------
bpy.ops.mesh.primitive_plane_add(size=30, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(mat_ground)

# Shallow pit under hut
bpy.ops.mesh.primitive_cylinder_add(radius=3.5, depth=0.4, location=(0,0,-0.15))
pit = bpy.context.active_object
pit.name = "Pit"
pit.data.materials.append(mat_dirt)

# ---------- TIMBER HUT ----------
# Four corner posts
post_h = 2.5
for px, py in [(-2.5,-2.5),(2.5,-2.5),(-2.5,2.5),(2.5,2.5)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=post_h, location=(px, py, post_h/2))
    p = bpy.context.active_object
    p.name = f"Post_{px}_{py}"
    p.data.materials.append(mat_wood_d)

# Horizontal beams (top frame)
beams = [
    (0, -2.5, post_h, 5.0, 0.12, 0.12),   # front top
    (0,  2.5, post_h, 5.0, 0.12, 0.12),   # back top
    (-2.5, 0, post_h, 0.12, 0.12, 5.0),   # left top
    ( 2.5, 0, post_h, 0.12, 0.12, 5.0),   # right top
]
for i,(x,y,z,lx,ly,lz) in enumerate(beams):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x,y,z))
    b = bpy.context.active_object
    b.name = f"Beam_{i}"
    b.scale = (lx/2, ly/2, lz/2)
    b.data.materials.append(mat_wood)

# Walls (plank style - simple boxes)
wall_thick = 0.08
# Front wall (with door gap)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.25, -2.5, 1.25))
w = bpy.context.active_object
w.name = "WallFront_L"
w.scale = (1.25/2, wall_thick/2, 1.25/2)
w.data.materials.append(mat_wood)

bpy.ops.mesh.primitive_cube_add(size=1, location=(1.25, -2.5, 1.25))
w = bpy.context.active_object
w.name = "WallFront_R"
w.scale = (1.25/2, wall_thick/2, 1.25/2)
w.data.materials.append(mat_wood)

# Top lintel over door
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2.5, 2.2))
w = bpy.context.active_object
w.name = "WallFront_Top"
w.scale = (1.0/2, wall_thick/2, 0.3/2)
w.data.materials.append(mat_wood)

# Back wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 2.5, 1.25))
w = bpy.context.active_object
w.name = "WallBack"
w.scale = (5.0/2, wall_thick/2, 1.25/2)
w.data.materials.append(mat_wood)

# Left wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(-2.5, 0, 1.25))
w = bpy.context.active_object
w.name = "WallLeft"
w.scale = (wall_thick/2, 5.0/2, 1.25/2)
w.data.materials.append(mat_wood)

# Right wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(2.5, 0, 1.25))
w = bpy.context.active_object
w.name = "WallRight"
w.scale = (wall_thick/2, 5.0/2, 1.25/2)
w.data.materials.append(mat_wood)

# Roof (thatched, sloped)
# Two sloped planes
for side in [-1, 1]:
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, side*1.3, post_h + 0.8))
    r = bpy.context.active_object
    r.name = f"Roof_{side}"
    r.scale = (5.5/2, 1.6/2, 1)
    r.rotation_euler = (math.radians(side * 30), 0, 0)
    r.data.materials.append(mat_thatch)

# Ridge beam
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=5.5, location=(0, 0, post_h + 1.5))
rb = bpy.context.active_object
rb.name = "RidgeBeam"
rb.rotation_euler = (0, math.radians(90), 0)
rb.data.materials.append(mat_wood_d)

# ---------- WARP-WEIGHTED LOOM ----------
# Loom frame: two horizontal bars with vertical supports
loom_x = -5.0
loom_y = -3.0

# Two vertical posts
for lx in [loom_x - 0.8, loom_x + 0.8]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.8, location=(lx, loom_y, 0.9))
    p = bpy.context.active_object
    p.name = f"LoomPost_{lx}"
    p.data.materials.append(mat_wood_d)

# Top horizontal bar
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.8, location=(loom_x, loom_y, 1.8))
tb = bpy.context.active_object
tb.name = "LoomTopBar"
tb.rotation_euler = (0, math.radians(90), 0)
tb.data.materials.append(mat_wood)

# Bottom horizontal bar (warp beam)
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.8, location=(loom_x, loom_y, 0.3))
bb = bpy.context.active_object
bb.name = "LoomBottomBar"
bb.rotation_euler = (0, math.radians(90), 0)
bb.data.materials.append(mat_wood)

# Warp threads (thin cylinders)
thread_count = 15
for i in range(thread_count):
    tx = loom_x - 0.7 + i * (1.4 / (thread_count - 1))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=1.5, location=(tx, loom_y, 1.05))
    t = bpy.context.active_object
    t.name = f"Thread_{i}"
    t.data.materials.append(mat_thread)

# Hanging stones (warp weights) - small rounded stones at bottom of threads
for i in range(thread_count):
    tx = loom_x - 0.7 + i * (1.4 / (thread_count - 1))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=12, ring_count=8, location=(tx, loom_y, 0.2))
    s = bpy.context.active_object
    s.name = f"WarpStone_{i}"
    s.scale = (1, 0.8, 1.2)
    s.data.materials.append(mat_stone)

# Weaving beam (horizontal bar mid-loom)
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.6, location=(loom_x, loom_y + 0.1, 1.0))
wb = bpy.context.active_object
wb.name = "WeavingBeam"
wb.rotation_euler = (0, math.radians(90), 0)
wb.data.materials.append(mat_wood)

# ---------- PIG PEN ----------
pen_cx = 5.0
pen_cy = 3.0
pen_w = 3.0
pen_d = 2.5

# Dirt floor
bpy.ops.mesh.primitive_plane_add(size=1, location=(pen_cx, pen_cy, 0.01))
pf = bpy.context.active_object
pf.name = "PenFloor"
pf.scale = (pen_w/2, pen_d/2, 1)
pf.data.materials.append(mat_mud)

# Fence posts (wooden)
fence_h = 1.2
for fx, fy in [(pen_cx - pen_w/2, pen_cy - pen_d/2), (pen_cx + pen_w/2, pen_cy - pen_d/2),
               (pen_cx - pen_w/2, pen_cy + pen_d/2), (pen_cx + pen_w/2, pen_cy + pen_d/2),
               (pen_cx, pen_cy - pen_d/2), (pen_cx, pen_cy + pen_d/2),
               (pen_cx - pen_w/2, pen_cy), (pen_cx + pen_w/2, pen_cy)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=fence_h, location=(fx, fy, fence_h/2))
    p = bpy.context.active_object
    p.name = f"FencePost_{fx}_{fy}"
    p.data.materials.append(mat_wood_d)

# Horizontal fence rails
for rail_z in [0.4, 0.8]:
    # Front and back rails
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=pen_w, location=(pen_cx, pen_cy - pen_d/2, rail_z))
    r = bpy.context.active_object
    r.name = f"RailFront_{rail_z}"
    r.rotation_euler = (0, math.radians(90), 0)
    r.data.materials.append(mat_wood)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=pen_w, location=(pen_cx, pen_cy + pen_d/2, rail_z))
    r = bpy.context.active_object
    r.name = f"RailBack_{rail_z}"
    r.rotation_euler = (0, math.radians(90), 0)
    r.data.materials.append(mat_wood)
    # Left and right rails
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=pen_d, location=(pen_cx - pen_w/2, pen_cy, rail_z))
    r = bpy.context.active_object
    r.name = f"RailLeft_{rail_z}"
    r.rotation_euler = (math.radians(90), 0, 0)
    r.data.materials.append(mat_wood)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=pen_d, location=(pen_cx + pen_w/2, pen_cy, rail_z))
    r = bpy.context.active_object
    r.name = f"RailRight_{rail_z}"
    r.rotation_euler = (math.radians(90), 0, 0)
    r.data.materials.append(mat_wood)

# Pigs (simple body + head)
for pig_i in range(2):
    pig_x = pen_cx - 0.5 + pig_i * 1.0
    pig_y = pen_cy + (0.3 if pig_i == 0 else -0.3)
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, segments=16, ring_count=12, location=(pig_x, pig_y, 0.25))
    body = bpy.context.active_object
    body.name = f"PigBody_{pig_i}"
    body.scale = (1.3, 0.9, 0.8)
    body.data.materials.append(mat_pig)
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, segments=12, ring_count=8, location=(pig_x + 0.45, pig_y, 0.3))
    head = bpy.context.active_object
    head.name = f"PigHead_{pig_i}"
    head.scale = (1.0, 0.8, 0.8)
    head.data.materials.append(mat_pig)
    # Snout
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, segments=8, ring_count=6, location=(pig_x + 0.65, pig_y, 0.28))
    snout = bpy.context.active_object
    snout.name = f"PigSnout_{pig_i}"
    snout.scale = (0.8, 1.0, 0.8)
    snout.data.materials.append(mat_pig)

# ---------- VEGETABLE PLOT ----------
veg_cx = -5.0
veg_cy = 4.0
veg_w = 3.5
veg_d = 2.5

# Raised bed border (stone)
for vx, vy in [(veg_cx - veg_w/2, veg_cy - veg_d/2), (veg_cx + veg_w/2, veg_cy - veg_d/2),
               (veg_cx - veg_w/2, veg_cy + veg_d/2), (veg_cx + veg_w/2, veg_cy + veg_d/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(vx, vy, 0.15))
    b = bpy.context.active_object
    b.name = f"VegBorder_{vx}_{vy}"
    b.scale = (0.15, 0.15, 0.15)
    b.data.materials.append(mat_stone)

# Soil
bpy.ops.mesh.primitive_plane_add(size=1, location=(veg_cx, veg_cy, 0.05))
soil = bpy.context.active_object
soil.name = "VegSoil"
soil.scale = (veg_w/2 - 0.15, veg_d/2 - 0.15, 1)
soil.data.materials.append(mat_dirt)

# Vegetable rows (small green bumps)
row_count = 4
for row_i in range(row_count):
    ry = veg_cy - veg_d/2 + 0.5 + row_i * (veg_d - 1.0) /