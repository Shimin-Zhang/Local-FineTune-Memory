import bpy
import math
import random
from mathutils import Vector

# Re-define passage dimensions
passage_length = 60
passage_width = 6
passage_height = 5
wall_thickness = 1.0

# --- MATERIALS (reuse existing) ---
stone_mat = bpy.data.materials.get("AncientStone")
dark_stone_mat = bpy.data.materials.get("DarkStone")
sand_mat = bpy.data.materials.get("Sand")
wood_mat = bpy.data.materials.get("OldWood")
leather_mat = bpy.data.materials.get("Leather")
skin_mat = bpy.data.materials.get("Skin")
cloth_mat = bpy.data.materials.get("Cloth")
hat_mat = bpy.data.materials.get("Hat")
torch_mat = bpy.data.materials.get("TorchFlame")
metal_mat = bpy.data.materials.get("Bronze")
rope_mat = bpy.data.materials.get("Rope")
dust_mat = bpy.data.materials.get("Dust")
hieroglyph_mat = bpy.data.materials.get("Hieroglyph")
crack_mat = bpy.data.materials.get("CrackDark")

# --- REBUILD LIGHTING (fix distance attribute) ---
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Torch lights along the walls
for i in range(8):
    y_pos = -passage_length/2 + 4 + i * 7
    for side in [-1, 1]:
        x = side * 2.9
        bpy.ops.object.light_add(type='POINT', location=(x, y_pos, 3.0))
        tl = bpy.context.active_object
        tl.data.energy = 80
        tl.data.color = (1.0, 0.5, 0.15)
        tl.data.shadow_soft_size = 0.3

# Key light - warm, from behind camera
bpy.ops.object.light_add(type='POINT', location=(-1, 14, 3.5))
key_light = bpy.context.active_object
key_light.data.energy = 800
key_light.data.color = (1.0, 0.65, 0.35)
key_light.data.shadow_soft_size = 0.8

# Boulder rim light
bpy.ops.object.light_add(type='POINT', location=(0, -13, 2.5))
rim_light = bpy.context.active_object
rim_light.data.energy = 400
rim_light.data.color = (1.0, 0.45, 0.15)
rim_light.data.shadow_soft_size = 1.0

# Top fill
bpy.ops.object.light_add(type='AREA', location=(0, 0, 4.9))
fill = bpy.context.active_object
fill.data.energy = 100
fill.data.color = (0.6, 0.5, 0.4)
fill.data.size = 8
fill.rotation_euler = (0, 0, 0)

# --- REPOSITION CAMERA to show full dramatic scene ---
cam = bpy.data.objects.get("Camera")
if cam:
    bpy.data.objects.remove(cam, do_unlink=True)

# Camera: low angle, behind and to the side of Indy, looking down the corridor toward the boulder
bpy.ops.object.camera_add(location=(-1.5, 12, 1.8))
camera = bpy.context.active_object
camera.name = "Camera"
target = Vector((0, -10, 2.0))
cam_loc = Vector((-1.5, 12, 1.8))
direction = target - cam_loc
rot_quat = direction.to_track_quat('Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()
camera.data.lens = 28
bpy.context.scene.camera = camera

# --- REPOSITION INDIANA JONES to be more visible ---
indy_parts = [o for o in bpy.data.objects if o.name.startswith("Indy_")]
indy_offset = Vector((-0.3, 1.0, 0))
for obj in indy_parts:
    obj.location = obj.location + indy_offset

# --- REPOSITION BOULDER ---
boulder = bpy.data.objects.get("GiantStoneBoulder")
if boulder:
    boulder.location = (0, -12, 2.5)
    boulder.scale = (1.1, 1.1, 1.1)

# --- ADD BOULDER'S TRAIL OF DESTRUCTION (cracked floor) ---
for i in range(10):
    y = -12 + i * 1.5
    x = random.uniform(-0.5, 0.5)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 0.01))
    patch = bpy.context.active_object
    patch.scale = (random.uniform(0.5, 1.5), random.uniform(0.3, 0.8), 1)
    patch.rotation_euler = (0, 0, random.uniform(-0.3, 0.3))
    patch.data.materials.append(crack_mat)

# --- ADD SCATTERED SAND/GRIT ---
for i in range(80):
    x = random.uniform(-2.5, 2.5)
    y = random.uniform(-15, 15)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.01, 0.03), subdivisions=0, location=(x, y, 0.01))
    bpy.context.active_object.data.materials.append(sand_mat)

# --- ADD HANGING VEGETATION / VINES ---
for i in range(12):
    y = random.uniform(-20, 20)
    x = random.uniform(-2, 2)
    length = random.uniform(0.5, 2.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=length, location=(x, y, 4.8 - length/2))
    vine = bpy.context.active_object
    vine.rotation_euler = (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 0)
    for j in range(3):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(x + random.uniform(-0.05, 0.05), y + random.uniform(-0.05, 0.05), 4.8 - length - 0.05))
        bpy.context.active_object.scale = (1.5, 1, 0.3)
        bpy.context.active_object.data.materials.append(cloth_mat)

# --- ADD MORE DUST CLOUD BEHIND BOULDER ---
for i in range(25):
    x = random.uniform(-2.5, 2.5)
    y = random.uniform(-14, -7)
    z = random.uniform(0.3, 3.5)
    r = random.uniform(0.3, 1.2)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z))
    dust_cloud = bpy.context.active_object
    dust_cloud.data.materials.append(dust_mat)

# --- ADD SMALLER DEBRIS BEING KICKED UP BY BOULDER ---
for i in range(30):
    x = random.uniform(-2.0, 2.0)
    y = random.uniform(-12, -8)
    z = random.uniform(0.1, 2.0)
    size = random.uniform(0.05, 0.2)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=size, subdivisions=1, location=(x, y, z))
    debris = bpy.context.active_object
    debris.scale = (random.uniform(0.7, 1.3), random.uniform(0.7, 1.3), random.uniform(0.5, 0.9))
    debris.data.materials.append(stone_mat)

# --- ADD FALLEN STONE SLABS ON FLOOR ---
for i in range(6):
    y = random.uniform(-20, 15)
    x = random.uniform(-1.5, 1.5)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.08))
    slab = bpy.context.active_object
    slab.scale = (random.uniform(0.4, 0.8), random.uniform(0.3, 0.6), 0.08)
    slab.rotation_euler = (0, 0, random.uniform(0, math.pi))
    slab.data.materials.append(dark_stone_mat)

# --- ADD ANCIENT SKELETON ---
skel_x = -2.2
skel_y = 18
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(skel_x, skel_y, 0.15))
bpy.context.active_object.scale = (1, 1.2, 1)
bpy.context.active_object.data.materials.append(sand_mat)
bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.02, location=(skel_x, skel_y - 0.3, 0.15))
bpy.context.active_object.rotation_euler = (math.radians(90), 0, 0)
bpy.context.active_object.data.materials.append(sand_mat)
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.4, location=(skel_x, skel_y - 0.5, 0.15))
bpy.context.active_object.rotation_euler = (math.radians(90), 0, 0)
bpy.context.active_object.data.materials.append(sand_mat)
bpy.ops.mesh.primitive_cube_add(size=0.15, location=(skel_x, skel_y - 0.75, 0.12))
bpy.context.active_object.data.materials.append(sand_mat)
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.3, location=(skel_x + 0.15, skel_y - 0.2, 0.12))
bpy.context.active_object.rotation_euler = (math.radians(45), 0, 0)
bpy.context.active_object.data.materials.append(sand_mat)
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.35, location=(skel_x + 0.05, skel_y - 1.0, 0.1))
bpy.context.active_object.rotation_euler = (math.radians(10), 0, 0)
bpy.context.active_object.data.materials.append(sand_mat)
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.35, location=(skel_x - 0.05, skel_y - 1.0, 0.1))
bpy.context.active_object.rotation_euler = (math.radians(-10), 0, 0)
bpy.context.active_object.data.materials.append(sand_mat)

# --- ADD ANCIENT VASE / POTTERY ---
for i in range(4):
    y = random.uniform(-15, 20)
    x = random.choice([-2.3, 2.3])
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.3, location=(x, y, 0.15))
    vase = bpy.context.active_object
    vase.data.materials.append(hieroglyph_mat)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.1, location=(x, y, 0.35))
    bpy.context.active_object.data.materials.append(hieroglyph_mat)

# --- ADD SCULPTED LION / BEAST HEADS ON WALLS ---
for i in range(4):
    y = -15 + i * 10
    for side in [-1, 1]:
        x = side * 2.9
        bpy.ops.mesh.primitive_cube_add(size=0.3, location=(x, y, 2.5))
        bpy.context.active_object.scale = (0.05, 0.2, 0.25)
        bpy.context.active_object.data.materials.append(hieroglyph_mat)
        for ey in [-0.06, 0.06]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(x - side*0.03, y + ey, 2.55))
            bpy.context.active_object.data.materials.append(crack_mat)
        bpy.ops.mesh.primitive_cube_add(size=0.15, location=(x - side*0.03, y, 2.35))
        bpy.context.active_object.scale = (0.04, 0.12, 0.08)
        bpy.context.active_object.data.materials.append(hieroglyph_mat)

# --- ADD MORE TORCHES ---
for i in range(4):
    y = -22 + i * 14
    for side in [-1, 1]:
        x = side * 2.9
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.6, location=(x, y, 2.0))
        bpy.context.active_object.rotation_euler = (0, math.radians(90 * side), 0)
        bpy.context.active_object.data.materials.append(wood_mat)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(x, y, 2.4))
        bpy.context.active_object.scale = (1, 1, 1.4)
        bpy.context.active_object.data.materials.append(torch_mat)

# --- UPDATE WORLD ---
world = bpy.context.scene.world
if world:
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.02, 0.015, 0.01, 1.0)
        bg_node.inputs[1].default_value = 0.5

# --- RENDER SETTINGS ---
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.render.use_motion_blur = True
bpy.context.scene.render.motion_blur_shutter = 0.5

bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.view_settings.exposure = -0.3

print(f"Scene refined! Objects: {len(bpy.data.objects)}")
