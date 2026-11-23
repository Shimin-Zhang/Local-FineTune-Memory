import bpy
import math
import mathutils
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- MATERIALS ---
def get_or_create_mat(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_ocean = get_or_create_mat("Ocean", (0.02, 0.15, 0.25), roughness=0.1)
mat_rock = get_or_create_mat("Rock", (0.25, 0.22, 0.18), roughness=0.9)
mat_sand = get_or_create_mat("Sand", (0.75, 0.65, 0.45), roughness=0.8)
mat_wood = get_or_create_mat("Wood", (0.35, 0.2, 0.1), roughness=0.7)
mat_metal = get_or_create_mat("Metal", (0.4, 0.4, 0.45), roughness=0.3, metallic=1.0)
mat_bird = get_or_create_mat("Bird", (0.8, 0.8, 0.8), roughness=0.6)
mat_canoe = get_or_create_mat("Canoe", (0.5, 0.3, 0.15), roughness=0.6)
mat_post = get_or_create_mat("Post", (0.3, 0.15, 0.08), roughness=0.7)

# --- OCEAN ---
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.5))
ocean = bpy.context.object
ocean.name = "Ocean"
ocean.data.materials.append(mat_ocean)
# Add subdivision for waves
mod = ocean.modifiers.new("Subdiv", 'SUBSURF')
mod.levels = 3
mod.render_levels = 3
# Displace for waves
tex = bpy.data.textures.new("WaveTex", type='CLOUDS')
tex.noise_scale = 10
disp = ocean.modifiers.new("Displace", 'DISPLACE')
disp.texture = tex
disp.strength = 0.4
disp.mid_level = 0.5

# --- FISH-SHAPED ISLAND ---
# Create a fish-like profile using a curve/mesh
# Body: elongated oval, tail: forked
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.5))
island = bpy.context.object
island.name = "FishIsland"
island.scale = (1, 1, 1)
bpy.ops.object.transform_apply(scale=True)

# Build fish shape manually with vertices
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.5))
island = bpy.context.object
island.name = "FishIsland"

# Define fish body vertices (top view, X = length, Y = width)
# Fish faces +X direction
verts = [
    # Head (rounded front)
    (6, 0), (5.5, 1.5), (4.5, 2.5), (3, 3), (1, 3.2), (-1, 3), (-3, 2.5), (-4.5, 2),
    # Tail fork
    (-6, 1.5), (-7.5, 3), (-8, 1.5), (-8.5, 0),
    (-8, -1.5), (-7.5, -3), (-6, -1.5),
    # Back to head (bottom)
    (-4.5, -2), (-3, -2.5), (-1, -3), (1, -3.2), (3, -3), (4.5, -2.5), (5.5, -1.5),
]
edges = [(i, i+1) for i in range(len(verts)-1)] + [(len(verts)-1, 0)]

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.5))
island = bpy.context.object
island.name = "FishIsland"
# Clear default mesh
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.delete(type='FACE')
bpy.ops.object.mode_set(mode='OBJECT')

# Create mesh from verts
me = island.data
me.clear()
me.from_pydata(verts, edges, [])
me.update()

# Extrude to give height
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 1.5)})
bpy.ops.object.mode_set(mode='OBJECT')

# Add solidify and subsurf
mod = island.modifiers.new("Solid", 'SOLIDIFY')
mod.thickness = 0.3
mod2 = island.modifiers.new("Subdiv", 'SUBSURF')
mod2.levels = 2
mod2.render_levels = 3
island.data.materials.append(mat_rock)

# Sand top layer
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 1.6))
sand = bpy.context.object
sand.name = "SandTop"
# Scale to fish shape roughly
sand.scale = (0.9, 0.85, 1)
bpy.ops.object.transform_apply(scale=True)
# Use same profile but slightly smaller
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.delete(type='FACE')
bpy.ops.object.mode_set(mode='OBJECT')
me2 = sand.data
me2.clear()
verts2 = [(v[0]*0.85, v[1]*0.85) for v in verts]
edges2 = [(i, i+1) for i in range(len(verts2)-1)] + [(len(verts2)-1, 0)]
me2.from_pydata(verts2, edges2, [])
me2.update()
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 0.3)})
bpy.ops.object.mode_set(mode='OBJECT')
sand.data.materials.append(mat_sand)

# --- HUGE HOOK ---
# Create a large hook shape using a torus + cylinder
bpy.ops.mesh.primitive_torus_add(
    major_radius=8, minor_radius=0.8,
    major_segments=64, minor_segments=16,
    location=(10, 0, 8)
)
hook_torus = bpy.context.object
hook_torus.name = "HookBody"
# Cut the torus to make a C-shape (hook)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
# Delete part of the torus to create hook shape
# We'll use boolean or just leave it as a ring and add a straight bar
bpy.ops.object.mode_set(mode='OBJECT')

# Add a straight bar for the hook's shank
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.8, depth=12,
    location=(10, 0, 14)
)
hook_shank = bpy.context.object
hook_shank.name = "HookShank"
hook_shank.rotation_euler = (0, 0, 0)
# Connect shank to torus
# Add a point/barb at the tip of the hook
bpy.ops.mesh.primitive_cone_add(
    radius1=0.8, radius2=0, depth=3,
    location=(10, 5, 2)
)
hook_barb = bpy.context.object
hook_barb.name = "HookBarb"
hook_barb.rotation_euler = (math.radians(-90), 0, 0)

# Join hook parts
bpy.ops.object.select_all(action='DESELECT')
hook_torus.select_set(True)
hook_shank.select_set(True)
hook_barb.select_set(True)
bpy.context.view_layer.objects.active = hook_torus
bpy.ops.object.join()
hook = bpy.context.object
hook.name = "GiantHook"
hook.data.materials.append(mat_metal)

# --- CANOE ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=2, location=(15, 5, 0.3), segments=32, ring_count=16)
canoe = bpy.context.object
canoe.name = "Canoe"
canoe.scale = (2.5, 0.8, 0.5)
bpy.ops.object.transform_apply(scale=True)
# Flatten bottom
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.delete(type='VERT')
bpy.ops.object.mode_set(mode='OBJECT')
# Recreate as a simple elongated box
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 5, 0.4))
canoe = bpy.context.object
canoe.name = "Canoe"
canoe.scale = (4, 1, 0.6)
bpy.ops.object.transform_apply(scale=True)
# Round it a bit
mod = canoe.modifiers.new("Subdiv", 'SUBSURF')
mod.levels = 2
mod.render_levels = 3
canoe.data.materials.append(mat_canoe)

# --- CARVED POSTS ON SHORE ---
post_positions = [
    (3, 2.5, 1.8),
    (1, 3, 1.8),
    (-2, 2.5, 1.8),
    (-4, 1.5, 1.8),
    (3, -2.5, 1.8),
    (0, -3, 1.8),
]
for i, pos in enumerate(post_positions):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.3, depth=3,
        location=pos
    )
    post = bpy.context.object
    post.name = f"CarvedPost_{i}"
    # Add some "carving" detail with a slight taper
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 0.2)})
    bpy.ops.object.mode_set(mode='OBJECT')
    # Add a simple carved shape on top
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.35, radius2=0.1, depth=0.8,
        location=(pos[0], pos[1], pos[2] + 1.5)
    )
    cone = bpy.context.object
    cone.name = f"PostTop_{i}"
    # Join
    bpy.ops.object.select_all(action='DESELECT')
    post.select_set(True)
    cone.select_set(True)
    bpy.context.view_layer.objects.active = post
    bpy.ops.object.join()
    post.data.materials.append(mat_post)

# --- GULLS CIRCLING ---
for i in range(8):
    angle = (i / 8) * 2 * math.pi
    radius = 20 + (i % 3) * 5
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    z = 15 + (i % 4) * 3

    # Simple bird shape: two wings + body
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(x, y, z))
    body = bpy.context.object
    body.name = f"Gull_{i}_body"
    body.scale = (1.5, 0.3, 0.3)
    bpy.ops.object.transform_apply(scale=True)

    # Left wing
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x - 0.5, y, z))
    wing_l = bpy.context.object
    wing_l.name = f"Gull_{i}_wingL"
    wing_l.scale = (1.5, 0.8, 1)
    wing_l.rotation_euler = (0, math.radians(20), math.radians(30))
    bpy.ops.object.transform_apply(scale=True, rotation=True)

    # Right wing
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + 0.5, y, z))
    wing_r = bpy.context.object
    wing_r.name = f"Gull_{i}_wingR"
    wing_r.scale = (1.5, 0.8, 1)
    wing_r.rotation_euler = (0, math.radians(-20), math.radians(-30))
    bpy.ops.object.transform_apply(scale=True, rotation=True)

    # Join bird parts
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    wing_l.select_set(True)
    wing_r.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    bird = bpy.context.object
    bird.name = f"Gull_{i}"
    bird.data.materials.append(mat_bird)

# --- LIGHTING ---
bpy.ops.object.light_add(type='SUN', location=(30, -30, 40))
sun = bpy.context.object
sun.name = "Sun"
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), math.radians(20), 0)

bpy.ops.object.light_add(type='AREA', location=(0, 0, 30))
area = bpy.context.object
area.name = "FillLight"
area.data.energy = 500
area.data.size = 20

# --- CAMERA ---
bpy.ops.object.camera_add(location=(35, -35, 20))
cam = bpy.context.object
cam.name = "Camera"
# Point camera at the scene center
direction = Vector((0, 0, 5)) - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam

# --- WORLD ---
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.4, 0.6, 0.9, 1.0)
bg.inputs[1].default_value = 1.0

print("Scene created: Fish-shaped island with hook, canoe, carved posts, and gulls.")
