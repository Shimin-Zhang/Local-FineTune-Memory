import bpy
import math
import random
from mathutils import Vector, Euler

# --- Setup ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# Lighting
bpy.ops.object.light_add(type='SUN', location=(50, -50, 100))
sun = bpy.context.object
sun.data.energy = 3.0
sun.rotation_euler = Euler((math.radians(45), math.radians(20), math.radians(0)))

# --- Materials ---
def get_mat(name, color, rough=0.8, metal=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = rough
            bsdf.inputs["Metallic"].default_value = metal
    return mat

mat_water = get_mat("Water", (0.05, 0.15, 0.25), rough=0.1, metal=0.1)
mat_wood = get_mat("Wood", (0.4, 0.25, 0.15), rough=0.9)
mat_wood_dark = get_mat("WoodDark", (0.2, 0.12, 0.08), rough=0.9)
mat_rope = get_mat("Rope", (0.6, 0.5, 0.3), rough=1.0)
mat_hull = get_mat("Hull", (0.1, 0.2, 0.5), rough=0.5)
mat_deck = get_mat("Deck", (0.5, 0.4, 0.3), rough=0.8)
mat_crane = get_mat("Crane", (0.8, 0.1, 0.1), rough=0.4)
mat_house_wall = get_mat("HouseWall", (0.9, 0.85, 0.8), rough=0.9)
mat_house_roof = get_mat("HouseRoof", (0.6, 0.2, 0.1), rough=0.8)
mat_ground = get_mat("Ground", (0.3, 0.4, 0.2), rough=1.0)
mat_mussel = get_mat("Mussel", (0.1, 0.1, 0.15), rough=0.7)

# --- Water ---
bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 0, -0.5))
water = bpy.context.object
water.data.materials.append(mat_water)
water.name = "RiaWater"

# --- Helpers ---
def add_box(name, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj

def add_cylinder(name, loc, r, depth, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj

# --- Mussel Rafts ---
def create_mussel_raft(x, y, rot_z, name_prefix):
    """Create a wooden raft with hanging mussel ropes."""
    objs = []
    # Main platform: 2x3 grid of wooden floats
    for i in range(3):
        for j in range(2):
            px = x + (i - 1) * 2.2
            py = y + (j - 0.5) * 2.2
            # Rotate position around raft center
            dx, dy = px - x, py - y
            rx = x + dx * math.cos(rot_z) - dy * math.sin(rot_z)
            ry = y + dx * math.sin(rot_z) + dy * math.cos(rot_z)
            float_obj = add_box(f"{name_prefix}_float_{i}_{j}", (rx, ry, 0), (1.8, 1.8, 0.3), mat_wood)
            objs.append(float_obj)

    # Cross beams
    for i in range(2):
        bx = x + (i - 0.5) * 2.2
        by = y
        dx, dy = bx - x, by - y
        rx = x + dx * math.cos(rot_z) - dy * math.sin(rot_z)
        ry = y + dx * math.sin(rot_z) + dy * math.cos(rot_z)
        beam = add_box(f"{name_prefix}_beam_{i}", (rx, ry, 0.15), (5.5, 0.3, 0.25), mat_wood_dark)
        beam.rotation_euler = (0, 0, rot_z)
        objs.append(beam)

    # Hanging ropes with mussel bags
    num_rope_cols = 4
    num_rope_rows = 3
    for i in range(num_rope_cols):
        for j in range(num_rope_rows):
            rx = x + (i - 1.5) * 1.5
            ry = y + (j - 1) * 1.8
            dx, dy = rx - x, ry - y
            px = x + dx * math.cos(rot_z) - dy * math.sin(rot_z)
            py = y + dx * math.sin(rot_z) + dy * math.cos(rot_z)
            # Rope (thin cylinder going down)
            rope = add_cylinder(f"{name_prefix}_rope_{i}_{j}", (px, py, -1.5), 0.03, 3.0, mat_rope)
            objs.append(rope)
            # Mussel bag (scaled sphere)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(px, py, -3.2), segments=12, ring_count=8)
            bag = bpy.context.object
            bag.name = f"{name_prefix}_mussel_{i}_{j}"
            bag.scale = (0.6, 0.6, 1.0)
            bag.data.materials.append(mat_mussel)
            objs.append(bag)

    # Group
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.group_make()
    grp = bpy.context.active_group
    grp.name = f"Raft_{name_prefix}"
    return grp

# Place rafts in the ria
raft_positions = [
    (-20, -10, 0.2, "R1"),
    (-15, 5, -0.3, "R2"),
    (-25, 15, 0.5, "R3"),
    (-10, -20, -0.1, "R4"),
    (-30, -5, 0.4, "R5"),
    (-5, 10, -0.4, "R6"),
]
for x, y, rz, nm in raft_positions:
    create_mussel_raft(x, y, rz, nm)

# --- Workboat ---
def create_workboat(x, y, rot_z, name):
    objs = []
    # Hull (elongated box)
    hull = add_box(f"{name}_hull", (x, y, 0.5), (6, 2, 1.2), mat_hull)
    hull.rotation_euler = (0, 0, rot_z)
    objs.append(hull)

    # Deck
    deck = add_box(f"{name}_deck", (x, y, 1.2), (5.5, 1.8, 0.15), mat_deck)
    deck.rotation_euler = (0, 0, rot_z)
    objs.append(deck)

    # Cabin
    dx, dy = 1.5 * math.cos(rot_z), 1.5 * math.sin(rot_z)
    cabin = add_box(f"{name}_cabin", (x + dx, y + dy, 1.8), (1.5, 1.5, 1.2), mat_wood)
    cabin.rotation_euler = (0, 0, rot_z)
    objs.append(cabin)

    # Mast
    mx, my = -1.0 * math.cos(rot_z), -1.0 * math.sin(rot_z)
    mast = add_cylinder(f"{name}_mast", (x + mx, y + my, 3.0), 0.08, 4.0, mat_wood_dark)
    objs.append(mast)

    # Small crane arm on boat
    cx, cy = -2.0 * math.cos(rot_z), -2.0 * math.sin(rot_z)
    crane_base = add_box(f"{name}_crane_base", (x + cx, y + cy, 1.5), (0.4, 0.4, 0.6), mat_crane)
    crane_base.rotation_euler = (0, 0, rot_z)
    objs.append(crane_base)
    crane_arm = add_box(f"{name}_crane_arm", (x + cx - 1.0*math.cos(rot_z), y + cy - 1.0*math.sin(rot_z), 2.2), (2.5, 0.2, 0.2), mat_crane)
    crane_arm.rotation_euler = (0, 0, rot_z + math.radians(20))
    objs.append(crane_arm)

    # Group
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.group_make()
    grp = bpy.context.active_group
    grp.name = f"Workboat_{name}"
    return grp

create_workboat(10, -5, math.radians(30), "WB1")
create_workboat(-5, 20, math.radians(-45), "WB2")

# --- Lifting Crane (on shore) ---
def create_shore_crane(x, y, name):
    objs = []
    # Base
    base = add_box(f"{name}_base", (x, y, 1), (3, 3, 2), mat_crane)
    objs.append(base)
    # Tower
    tower = add_box(f"{name}_tower", (x, y, 6), (1.5, 1.5, 10), mat_crane)
    objs.append(tower)
    # Jib arm
    jib = add_box(f"{name}_jib", (x + 6, y, 11), (12, 0.8, 0.8), mat_crane)
    objs.append(jib)
    # Counter-jib
    cjib = add_box(f"{name}_cjib", (x - 3, y, 11), (6, 0.8, 0.8), mat_crane)
    objs.append(cjib)
    # Counterweight
    cw = add_box(f"{name}_cw", (x - 5.5, y, 10), (1.5, 1.5, 1.5), mat_wood_dark)
    objs.append(cw)
    # Cable
    cable = add_cylinder(f"{name}_cable", (x + 8, y, 8), 0.05, 6, mat_rope)
    objs.append(cable)
    # Hook block
    hook = add_box(f"{name}_hook", (x + 8, y, 5), (0.5, 0.5, 0.5), mat_crane)
    objs.append(hook)

    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.group_make()
    grp = bpy.context.active_group
    grp.name = f"ShoreCrane_{name}"
    return grp

create_shore_crane(25, 15, "SC1")

# --- Village on the shore ---
def create_house(x, y, rot_z, name, w=3, d=3, h=2.5):
    objs = []
    # Walls
    wall = add_box(f"{name}_wall", (x, y, h/2), (w, d, h), mat_house_wall)
    wall.rotation_euler = (0, 0, rot_z)
    objs.append(wall)
    # Roof (pyramid-like)
    bpy.ops.mesh.primitive_cone_add(radius1=max(w,d)/2, radius2=0, depth=h*0.6, location=(x, y, h + h*0.3), vertices=4)
    roof = bpy.context.object
    roof.name = f"{name}_roof"
    roof.rotation_euler = (0, 0, rot_z + math.radians(45))
    roof.scale = (w/(max(w,d)), d/(max(w,d)), 1)
    roof.data.materials.append(mat_house_roof)
    objs.append(roof)
    # Door
    door = add_box(f"{name}_door", (x, y - d/2 - 0.05, 0.8), (0.8, 0.1, 1.6), mat_wood_dark)
    door.rotation_euler = (0, 0, rot_z)
    objs.append(door)

    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.group_make()
    grp = bpy.context.active_group
    grp.name = f"House_{name}"
    return grp

# Shore ground
bpy.ops.mesh.primitive_plane_add(size=80, location=(40, 20, 0.1))
shore = bpy.context.object
shore.name = "Shore"
shore.scale = (1, 1.2, 1)
shore.rotation_euler = (0, 0, math.radians(-20))
shore.data.materials.append(mat_ground)

# Village houses
village_houses = [
    (30, 10, 0.1, "H1"),
    (35, 12, -0.2, "H2"),
    (32, 18, 0.3, "H3"),
    (38, 15, -0.1, "H4"),
    (28, 14, 0.0, "H5"),
    (36, 20, 0.2, "H6"),
    (40, 10, -0.3, "H7"),
    (33, 22, 0.1, "H8"),
]
for x, y, rz, nm in village_houses:
    create_house(x, y, rz, nm)

# --- Camera ---
bpy.ops.object.camera_add(location=(0, -60, 15))
cam = bpy.context.object
cam.name = "MainCam"
cam.rotation_euler = Euler((math.radians(75), 0, 0))
scene.camera = cam

# --- World background ---
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.6, 0.7, 0.85, 1.0)
    bg.inputs["Strength"].default_value = 0.8
