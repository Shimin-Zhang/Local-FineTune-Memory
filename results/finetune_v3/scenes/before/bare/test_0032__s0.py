import bpy
import math
import mathutils
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up world
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.7, 0.75, 0.85, 1.0)
    bg.inputs[1].default_value = 1.0

# Materials
def make_mat(name, color, metallic=0.0, rough=0.5, emission=0.0, emit_col=(1,1,1,1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = emit_col
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat

mat_stone = make_mat("WhiteStone", (0.92, 0.92, 0.90, 1.0), 0.0, 0.7)
mat_gold = make_mat("Gold", (1.0, 0.78, 0.2, 1.0), 1.0, 0.25, emission=0.3, emit_col=(1.0, 0.8, 0.3, 1.0))
mat_shield = make_mat("Shield", (0.15, 0.2, 0.5, 1.0), 0.3, 0.4)
mat_shield_rim = make_mat("ShieldRim", (0.8, 0.8, 0.8, 1.0), 1.0, 0.3)
mat_banner = make_mat("Banner", (0.7, 0.1, 0.1, 1.0), 0.0, 0.8)
mat_banner2 = make_mat("Banner2", (0.1, 0.1, 0.5, 1.0), 0.0, 0.8)
mat_water = make_mat("Water", (0.3, 0.6, 0.8, 1.0), 0.0, 0.1, emission=0.1, emit_col=(0.3, 0.7, 1.0, 1.0))
mat_mud = make_mat("Mud", (0.35, 0.25, 0.15, 1.0), 0.0, 0.95)
mat_well_stone = make_mat("WellStone", (0.8, 0.8, 0.78, 1.0), 0.0, 0.8)
mat_roof = make_mat("Roof", (0.3, 0.3, 0.35, 1.0), 0.2, 0.6)
mat_sunray = make_mat("SunRay", (1.0, 0.9, 0.5, 1.0), 0.0, 0.3, emission=1.5, emit_col=(1.0, 0.85, 0.4, 1.0))
mat_wood = make_mat("Wood", (0.4, 0.25, 0.1, 1.0), 0.0, 0.8)

# Helper: create a mesh object from vertices/faces
def make_obj(name, verts, faces, mat, location=(0,0,0)):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    obj.location = location
    bpy.context.collection.objects.link(obj)
    return obj

def make_box(name, size, mat, location=(0,0,0)):
    w, h, d = size
    v = [
        (-w/2, -h/2, -d/2), (w/2, -h/2, -d/2), (w/2, h/2, -d/2), (-w/2, h/2, -d/2),
        (-w/2, -h/2,  d/2), (w/2, -h/2,  d/2), (w/2, h/2,  d/2), (-w/2, h/2,  d/2),
    ]
    f = [
        (0,1,2,3), (7,6,5,4), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0),
    ]
    return make_obj(name, v, f, mat, location)

def make_cylinder(name, r, depth, mat, location=(0,0,0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=location, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

def make_sphere(name, r, mat, location=(0,0,0), segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=location, segments=segments, ring_count=rings)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj

# ============================================================
# GROUND: muddy field
# ============================================================
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "MuddyField"
ground.data.materials.clear()
ground.data.materials.append(mat_mud)

# Add some mud bumps
import random
random.seed(42)
for i in range(80):
    x = random.uniform(-40, 40)
    y = random.uniform(-40, 40)
    r = random.uniform(0.3, 1.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, 0.05), segments=12, ring_count=8)
    bump = bpy.context.active_object
    bump.scale = (1, 1, 0.3)
    bump.data.materials.clear()
    bump.data.materials.append(mat_mud)
    bump.name = f"MudBump_{i}"

# ============================================================
# CHAPEL: white stone building
# ============================================================
chapel_x = 0
chapel_y = -10
chapel_w = 16
chapel_h = 12
chapel_d = 20

# Main body
make_box("ChapelBody", (chapel_w, chapel_h, chapel_d), mat_stone, (chapel_x, chapel_y, chapel_h/2))

# Roof (pyramid-ish)
roof_verts = [
    (-chapel_w/2 - 1, chapel_y - chapel_d/2 - 1, chapel_h),
    ( chapel_w/2 + 1, chapel_y - chapel_d/2 - 1, chapel_h),
    ( chapel_w/2 + 1, chapel_y + chapel_d/2 + 1, chapel_h),
    (-chapel_w/2 - 1, chapel_y + chapel_d/2 + 1, chapel_h),
    (0, chapel_y, chapel_h + 6),
]
roof_faces = [
    (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4),
    (0, 3, 2, 1),
]
make_obj("ChapelRoof", roof_verts, roof_faces, mat_roof)

# Front face (facing +y direction, i.e., towards viewer at y=0)
# Door
make_box("Door", (3, 4, 0.3), mat_wood, (chapel_x, chapel_y + chapel_d/2 + 0.1, 2))
# Door frame
make_box("DoorFrame_L", (0.5, 4.5, 0.5), mat_stone, (chapel_x - 1.75, chapel_y + chapel_d/2 + 0.1, 2.25))
make_box("DoorFrame_R", (0.5, 4.5, 0.5), mat_stone, (chapel_x + 1.75, chapel_y + chapel_d/2 + 0.1, 2.25))
make_box("DoorFrame_T", (4.5, 0.5, 0.5), mat_stone, (chapel_x, chapel_y + chapel_d/2 + 0.1, 4.5))

# Windows on sides
for side in [-1, 1]:
    for i in range(3):
        wy = chapel_y - chapel_d/2 + 4 + i * 5
        make_box(f"SideWindow_{side}_{i}", (0.3, 2.5, 1.5), mat_gold, (chapel_x + side * chapel_w/2 * 0.98, wy, 5))

# ============================================================
# GOLDEN SUNBURST WINDOW (front face, above door)
# ============================================================
sunburst_center = (chapel_x, chapel_y + chapel_d/2 + 0.15, 8)
sunburst_r = 2.5

# Outer ring
bpy.ops.mesh.primitive_torus_add(major_radius=sunburst_r, minor_radius=0.3, location=sunburst_center, major_segments=64, minor_segments=12)
torus = bpy.context.active_object
torus.name = "SunburstRing"
torus.data.materials.clear()
torus.data.materials.append(mat_gold)

# Inner circle (glowing)
bpy.ops.mesh.primitive_circle_add(radius=sunburst_r * 0.8, fill_type='NGON', location=sunburst_center, vertices=64)
inner_circle = bpy.context.active_object
inner_circle.name = "SunburstCenter"
inner_circle.data.materials.clear()
inner_circle.data.materials.append(mat_sunray)

# Sun rays (triangular spikes radiating outward)
num_rays = 12
for i in range(num_rays):
    angle = i * (2 * math.pi / num_rays)
    ray_len = sunburst_r * 0.6
    ray_width = 0.25
    # Ray triangle in local coords, then position
    v1 = (0, 0, 0)
    v2 = (ray_len, ray_width, 0)
    v3 = (ray_len, -ray_width, 0)
    verts = [
        (v1[0], v1[1], v1[2]),
        (v2[0], v2[1], v2[2]),
        (v3[0], v3[1], v3[2]),
    ]
    faces = [(0, 1, 2)]
    obj = make_obj(f"SunRay_{i}", verts, faces, mat_sunray)
    obj.location = (
        sunburst_center[0] + math.cos(angle) * sunburst_r * 0.8,
        sunburst_center[1],
        sunburst_center[2] + math.sin(angle) * sunburst_r * 0.8
    )
    obj.rotation_euler = (0, -angle, 0)  # rotate in XZ plane

# ============================================================
# SHIELD RACK (outside, to the left of chapel)
# ============================================================
rack_x = chapel_x - chapel_w/2 - 4
rack_y = chapel_y + 3

# Rack posts
for dx in [-2, 2]:
    make_cylinder(f"RackPost_{dx}", 0.15, 3, mat_wood, (rack_x + dx, rack_y, 1.5))
# Top bar
make_box("RackTopBar", (4.5, 0.3, 0.3), mat_wood, (rack_x, rack_y, 3))

# Shields hanging
shield_positions = [
    (rack_x - 1.5, rack_y, 2.2),
    (rack_x,       rack_y, 2.2),
    (rack_x + 1.5, rack_y, 2.2),
]
for i, pos in enumerate(shield_positions):
    # Shield body (flat sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=pos, segments=24, ring_count=16)
    shield = bpy.context.active_object
    shield.name = f"Shield_{i}"
    shield.scale = (1, 1, 0.15)
    shield.data.materials.clear()
    shield.data.materials.append(mat_shield)
    # Shield rim
    bpy.ops.mesh.primitive_torus_add(major_radius=0.8, minor_radius=0.08, location=pos, major_segments=32, minor_segments=8)
    rim = bpy.context.active_object
    rim.name = f"ShieldRim_{i}"
    rim.scale = (1, 1, 0.15)
    rim.data.materials.clear()
    rim.data.materials.append(mat_shield_rim)
    # Shield emblem (small gold cross)
    make_box(f"ShieldCrossV_{i}", (0.15, 0.6, 0.05), mat_gold, (pos[0], pos[1], pos[2] + 0.12))
    make_box(f"ShieldCrossH_{i}", (0.6, 0.15, 0.05), mat_gold, (pos[0], pos[1], pos[2] + 0.12))

# ============================================================
# HEALING WELL (to the right of chapel)
# ============================================================
well_x = chapel_x + chapel_w/2 + 4
well_y = chapel_y + 3
well_r = 2.5

# Well base (cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=well_r, depth=2, location=(well_x, well_y, 1), vertices=32)
well_base = bpy.context.active_object
well_base.name = "WellBase"
well_base.data.materials.clear()
well_base.data.materials.append(mat_well_stone)

# Well opening (darker circle on top)
bpy.ops.mesh.primitive_cylinder_add(radius=well_r * 0.7, depth=0.3, location=(well_x, well_y, 2.05), vertices=32)
well_open = bpy.context.active_object
well_open.name = "WellOpening"
well_open.data.materials.clear()
well_open.data.materials.append(mat_water)

# Well roof posts
for dx in [-1.5, 1.5]:
    make_cylinder(f"WellPost_{dx}", 0.12, 3, mat_wood, (well_x + dx, well_y, 3.5))
# Well roof
roof_w = 4
roof_d = 3
well_roof_verts = [
    (well_x - roof_w/2, well_y - roof_d/2, 5),
    (well_x + roof_w/2, well_y - roof_d/2, 5),
    (well_x + roof_w/2, well_y + roof_d/2, 5),
    (well_x - roof_w/2, well_y + roof_d/2, 5),
    (well_x, well_y, 6.5),
]
well_roof_faces = [
    (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4),
    (0, 3, 2, 1),
]
make_obj("WellRoof", well_roof_verts, well_roof_faces, mat_roof)

# Bucket on well
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(well_x, well_y, 2.5), vertices=16)
bucket = bpy.context.active_object
bucket.name = "Bucket"
bucket.data.materials.clear()
bucket.data.materials.append(mat_wood)

# Rope
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=1.5, location=(well_x, well_y, 3.75), vertices=8)
rope = bpy.context.active_object
rope.name = "Rope"
rope.data.materials.clear()
rope.data.materials.append(mat_wood)

# ============================================================
# BANNERS FLYING OVER THE MUDdy FIELD
# ============================================================
banner_positions = [
    (-15, 5, 0, mat_banner),
    (-8, 8, 0, mat_banner2),
    (0, 12, 0, mat_banner),
    (8, 8, 0, mat_banner2),
    (15, 5, 0, mat_banner),
    (-20, 15, 0, mat_banner2),
   