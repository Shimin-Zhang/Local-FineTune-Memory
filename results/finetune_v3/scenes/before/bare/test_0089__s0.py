import bpy
import math
import mathutils
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Settings ---
COLS_X = 8
COLS_Z = 6
COL_SPACING_X = 6.0
COL_SPACING_Z = 5.0
COLUMN_HEIGHT = 12.0
COLUMN_RADIUS = 1.2
SLAB_THICKNESS = 1.0
SLAB_SIZE_X = COL_SPACING_X
SLAB_SIZE_Z = COL_SPACING_Z
OPEN_RATIO = 0.4  # fraction of slabs open

# --- Materials ---
def create_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_stone = create_material("Sandstone", (0.75, 0.65, 0.45), 0.8, 0.0)
mat_stone_dark = create_material("SandstoneDark", (0.55, 0.45, 0.30), 0.85, 0.0)
mat_wood = create_material("Wood", (0.45, 0.30, 0.15), 0.7, 0.0)

# --- Helper: Create a papyrus-bud column ---
def create_papyrus_column(name, location, height, radius):
    """
    Creates a stylized papyrus-bud column:
    - Base: simple box
    - Shaft: tapered cylinder with vertical ridges (approximated)
    - Capital: flaring bud shape (cone/sphere combo)
    """
    objects = []
    
    # Base
    base_size = radius * 2.5
    base_height = 1.0
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location.x, location.y, location.z + base_height/2))
    base = bpy.context.active_object
    base.name = f"{name}_base"
    base.scale = (base_size, base_size, base_height)
    bpy.ops.object.transform_apply(scale=True)
    base.data.materials.append(mat_stone_dark)
    objects.append(base)
    
    # Shaft: use a cylinder with many segments and displace for ridges
    shaft_height = height - base_height - 2.5  # leave room for capital
    shaft_bottom = location.z + base_height
    shaft_center = shaft_bottom + shaft_height / 2
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=shaft_height,
        location=(location.x, location.y, shaft_center)
    )
    shaft = bpy.context.active_object
    shaft.name = f"{name}_shaft"
    
    # Add vertical ridges by editing vertices
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(shaft.data)
    
    # Apply a slight taper: narrower at top
    for v in bm.verts:
        # Taper: scale x,y based on z
        z_rel = (v.co.z + shaft_height/2) / shaft_height  # 0 at bottom, 1 at top
        taper = 1.0 - 0.15 * z_rel  # 15% narrower at top
        v.co.x *= taper
        v.co.y *= taper
        
        # Add vertical ridges: modulate radius based on angle
        angle = math.atan2(v.co.y, v.co.x)
        ridge = 1.0 + 0.08 * math.cos(12 * angle)  # 12 ridges
        v.co.x *= ridge
        v.co.y *= ridge
    
    bm.to_mesh(shaft.data)
    bm.free()
    
    shaft.data.materials.append(mat_stone)
    objects.append(shaft)
    
    # Capital: papyrus bud shape - use a cone + sphere
    cap_bottom = shaft_bottom + shaft_height
    cap_height = 2.5
    
    # Flaring cone (bud base)
    bpy.ops.mesh.primitive_cone_add(
        vertices=32,
        radius1=radius * 1.1,
        radius2=radius * 2.2,
        depth=cap_height * 0.6,
        location=(location.x, location.y, cap_bottom + cap_height * 0.3)
    )
    cap_cone = bpy.context.active_object
    cap_cone.name = f"{name}_cap_cone"
    cap_cone.data.materials.append(mat_stone)
    objects.append(cap_cone)
    
    # Bud top (sphere)
    bud_radius = radius * 1.5
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        radius=bud_radius,
        location=(location.x, location.y, cap_bottom + cap_height * 0.6 + bud_radius * 0.5)
    )
    bud = bpy.context.active_object
    bud.name = f"{name}_bud"
    bud.scale = (1.0, 1.0, 0.8)  # slightly flattened
    bpy.ops.object.transform_apply(scale=True)
    bud.data.materials.append(mat_stone)
    objects.append(bud)
    
    return objects

# --- Create columns in rows ---
hall_width_x = (COLS_X - 1) * COL_SPACING_X
hall_depth_z = (COLS_Z - 1) * COL_SPACING_Z
origin_x = -hall_width_x / 2
origin_z = -hall_depth_z / 2

column_positions = []
for i in range(COLS_X):
    for j in range(COLS_Z):
        x = origin_x + i * COL_SPACING_X
        z = origin_z + j * COL_SPACING_Z
        loc = Vector((x, 0, 0))
        name = f"Col_{i}_{j}"
        create_papyrus_column(name, loc, COLUMN_HEIGHT, COLUMN_RADIUS)
        column_positions.append((x, z))

# --- Create roof slabs (partly open) ---
roof_y = COLUMN_HEIGHT + 0.5
slab_offset_x = COL_SPACING_X / 2
slab_offset_z = COL_SPACING_Z / 2

# We'll create slabs between column centers
# Number of slabs: (COLS_X-1) x (COLS_Z-1)
import random
random.seed(42)  # reproducible

for i in range(COLS_X - 1):
    for j in range(COLS_Z - 1):
        # Center of this slab
        cx = origin_x + (i + 0.5) * COL_SPACING_X
        cz = origin_z + (j + 0.5) * COL_SPACING_Z
        
        # Decide if this slab is open (no slab)
        is_open = random.random() < OPEN_RATIO
        
        if not is_open:
            # Create slab
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(cx, roof_y, cz)
            )
            slab = bpy.context.active_object
            slab.name = f"Slab_{i}_{j}"
            slab.scale = (SLAB_SIZE_X * 0.95, SLAB_THICKNESS, SLAB_SIZE_Z * 0.95)
            bpy.ops.object.transform_apply(scale=True)
            slab.data.materials.append(mat_stone_dark)
            
            # Add a slight bevel for realism
            mod = slab.modifiers.new("Bevel", 'BEVEL')
            mod.width = 0.1
            mod.segments = 2
        else:
            # Open gap - optionally add a thin frame
            pass

# --- Create a floor ---
floor_size_x = hall_width_x + 4
floor_size_z = hall_depth_z + 4
bpy.ops.mesh.primitive_plane_add(
    size=1,
    location=(0, 0, 0)
)
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (floor_size_x, floor_size_z, 1)
bpy.ops.object.transform_apply(scale=True)
floor.data.materials.append(mat_stone_dark)

# --- Lighting: Noon sun ---
# Sun light from directly above (noon)
sun_data = bpy.data.lights.new("NoonSun", type='SUN')
sun_data.energy = 5.0
sun_data.angle = math.radians(1.5)  # slightly soft shadows
sun_data.color = (1.0, 0.95, 0.85)  # warm noon light

sun_obj = bpy.data.objects.new("NoonSun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (0, 0, 0)  # pointing straight down

# Ambient/world light
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.8, 0.85, 0.95, 1.0)  # sky blue ambient
    bg_node.inputs[1].default_value = 0.5

# --- Camera setup ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)

# Position camera at one end, looking into the hall
cam_obj.location = (0, -hall_depth_z/2 - 15, 8)
cam_obj.rotation_euler = (math.radians(85), 0, 0)  # looking slightly up

bpy.context.scene.camera = cam_obj

# --- Render settings ---
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# Enable shadows
bpy.context.scene.cycles.shadow_bounces = 4
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 2

print("Egyptian temple hall built successfully.")
