import bpy
import math
import random
from mathutils import Vector, Matrix

# --- Setup ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# --- Lighting: Dusk ---
# Sun
sun_data = bpy.data.lights.new("DuskSun", 'SUN')
sun_data.energy = 1.5
sun_data.color = (1.0, 0.5, 0.2)  # warm orange
sun_obj = bpy.data.objects.new("DuskSun", sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(60), math.radians(20), math.radians(0))

# Ambient
world = bpy.data.worlds.new("DuskWorld")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
bg_node.inputs[0].default_value = (0.15, 0.1, 0.15, 1.0)  # dim purple-blue dusk
bg_node.inputs[1].default_value = 0.3

# --- Materials ---
def make_mat(name, color, rough=0.8):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    return mat

clay_mat = make_mat("Clay", (0.55, 0.3, 0.15), 0.9)
brick_mat = make_mat("Brick", (0.7, 0.35, 0.15), 0.85)
dried_brick_mat = make_mat("DriedBrick", (0.8, 0.45, 0.2), 0.8)
wood_mat = make_mat("Wood", (0.4, 0.25, 0.1), 0.7)
cloth_mat = make_mat("Cloth", (0.9, 0.85, 0.7), 0.95)
cloth_mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.7
smoke_mat = make_mat("Smoke", (0.3, 0.25, 0.2), 1.0)
smoke_mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.4
kiln_bricks_mat = make_mat("KilnBricks", (0.5, 0.2, 0.1), 0.9)
kiln_glow_mat = make_mat("KilnGlow", (1.0, 0.4, 0.0), 1.0)
kiln_glow_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (1.0, 0.4, 0.0)
kiln_glow_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 5.0
pit_mat = make_mat("PitClay", (0.45, 0.25, 0.1), 0.95)
ground_mat = make_mat("Ground", (0.35, 0.25, 0.12), 0.95)

# --- Ground ---
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(ground_mat)

# --- Clay Pit ---
# A rectangular depression
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, -10, 0.5))
pit = bpy.context.active_object
pit.name = "ClayPit"
pit.scale = (4, 3, 0.5)
# Make it a hole: use a box with inward normals or just place a lower plane
bpy.ops.object.transform_apply(scale=True)
# Create pit walls
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, -10, 0))
pit_wall = bpy.context.active_object
pit_wall.name = "ClayPitWalls"
pit_wall.scale = (4.2, 3.2, 0.6)
bpy.ops.object.transform_apply(scale=True)
# Make it hollow: use solidify or just place inner floor
bpy.ops.mesh.primitive_plane_add(size=1, location=(15, -10, -0.3))
pit_floor = bpy.context.active_object
pit_floor.name = "ClayPitFloor"
pit_floor.scale = (4, 3, 1)
pit_floor.data.materials.append(pit_mat)
pit_wall.data.materials.append(clay_mat)
# Remove the top face of pit_wall to make it look like a pit
# For simplicity, just place a slightly smaller inner box
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, -10, -0.3))
pit_inner = bpy.context.active_object
pit_inner.name = "ClayPitInner"
pit_inner.scale = (3.8, 2.8, 0.4)
bpy.ops.object.transform_apply(scale=True)
pit_inner.data.materials.append(pit_mat)
# Delete the original pit cube
bpy.data.objects.remove(pit, do_unlink=True)
bpy.data.objects.remove(pit_wall, do_unlink=True)

# --- Moulding Tables ---
for i in range(3):
    x = -10 + i * 5
    y = -5
    # Table top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 1.0))
    table = bpy.context.active_object
    table.name = f"MouldingTable_{i}"
    table.scale = (2.5, 1.2, 0.1)
    table.data.materials.append(wood_mat)
    # Legs
    for lx in [-1, 1]:
        for ly in [-0.5, 0.5]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x + lx * 1.1, y + ly * 0.9, 0.5))
            leg = bpy.context.active_object
            leg.name = f"TableLeg_{i}_{lx}_{ly}"
            leg.scale = (0.08, 0.08, 0.5)
            leg.data.materials.append(wood_mat)
    # Some clay lumps on table
    for j in range(4):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x - 0.8 + j * 0.5, y + random.uniform(-0.3, 0.3), 1.15))
        lump = bpy.context.active_object
        lump.name = f"ClayLump_{i}_{j}"
        lump.scale = (1, 0.8, 0.6)
        lump.data.materials.append(clay_mat)

# --- Bricks Drying in Rows Under Cloth ---
def make_brick(x, y, z, mat, scale=(0.3, 0.15, 0.1)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    brick = bpy.context.active_object
    brick.name = "Brick"
    brick.scale = scale
    brick.data.materials.append(mat)
    return brick

# Rows of drying bricks
row_y_start = 5
for row in range(5):
    y = row_y_start + row * 1.2
    # Cloth sheet
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y, 2.5))
    cloth = bpy.context.active_object
    cloth.name = f"DryingCloth_{row}"
    cloth.scale = (8, 1.5, 1)
    cloth.data.materials.append(cloth_mat)
    # Support posts
    for px in [-4, 0, 4]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2.5, location=(px, y, 1.25))
        post = bpy.context.active_object
        post.name = f"ClothPost_{row}_{px}"
        post.data.materials.append(wood_mat)
    # Bricks in this row
    for col in range(12):
        x = -3.5 + col * 0.65
        z = 0.1
        # Stack 2-3 bricks
        for stack in range(random.randint(2, 3)):
            bz = z + stack * 0.11
            make_brick(x, y + random.uniform(-0.2, 0.2), bz, dried_brick_mat)

# --- Clamp Kiln (Smouldering at Dusk) ---
kiln_x = 20
kiln_y = 5
# Kiln base (large rectangular brick structure)
bpy.ops.mesh.primitive_cube_add(size=1, location=(kiln_x, kiln_y, 1.5))
kiln_body = bpy.context.active_object
kiln_body.name = "ClampKiln"
kiln_body.scale = (5, 4, 1.5)
kiln_body.data.materials.append(kiln_bricks_mat)

# Kiln top (slightly smaller, to suggest a roof)
bpy.ops.mesh.primitive_cube_add(size=1, location=(kiln_x, kiln_y, 3.1))
kiln_top = bpy.context.active_object
kiln_top.name = "KilnTop"
kiln_top.scale = (4.5, 3.5, 0.3)
kiln_top.data.materials.append(kiln_bricks_mat)

# Chimney / smoke stack
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=2, location=(kiln_x + 2, kiln_y + 1, 4))
chimney = bpy.context.active_object
chimney.name = "KilnChimney"
chimney.data.materials.append(kiln_bricks_mat)

# Glow from inside (emissive plane at base)
bpy.ops.mesh.primitive_plane_add(size=1, location=(kiln_x, kiln_y, 0.05))
glow = bpy.context.active_object
glow.name = "KilnGlow"
glow.scale = (4.5, 3.5, 1)
glow.data.materials.append(kiln_glow_mat)

# Smoke particles (simple spheres)
for i in range(8):
    t = i / 8.0
    sx = kiln_x + 2 + t * 1.5 + random.uniform(-0.3, 0.3)
    sy = kiln_y + 1 + t * 0.8 + random.uniform(-0.3, 0.3)
    sz = 4 + t * 4
    r = 0.3 + t * 0.8
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(sx, sy, sz))
    smoke = bpy.context.active_object
    smoke.name = f"Smoke_{i}"
    smoke.data.materials.append(smoke_mat)

# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = (-15, 15, 8)
cam_obj.rotation_euler = (math.radians(70), 0, math.radians(-30))
scene.camera = cam_obj

# --- Render settings ---
scene.render.film_transparent = False
scene.cycles.use_denoising = True
