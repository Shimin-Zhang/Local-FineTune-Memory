import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set units
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# Create materials
def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

mat_ground = create_material("Ground", (0.15, 0.25, 0.08, 1.0), roughness=0.9)
mat_tent = create_material("Tent", (0.85, 0.7, 0.3, 1.0), roughness=0.6)
mat_fire = create_material("Fire", (1.0, 0.4, 0.1, 1.0), roughness=0.3)
mat_log = create_material("Log", (0.35, 0.2, 0.1, 1.0), roughness=0.85)
mat_stone = create_material("Stone", (0.4, 0.4, 0.38, 1.0), roughness=0.95)
mat_pine_trunk = create_material("PineTrunk", (0.3, 0.18, 0.08, 1.0), roughness=0.9)
mat_pine_leaf = create_material("PineLeaf", (0.05, 0.2, 0.08, 1.0), roughness=0.7)

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(mat_ground)
# Displace slightly for terrain feel
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')
import bmesh
me = ground.data
for v in me.vertices:
    v.co.z += random.uniform(-0.05, 0.05)

# --- Tent (triangular prism / A-frame) ---
tent_verts = [
    (-1.2, -1.0, 0.0),
    (1.2, -1.0, 0.0),
    (1.2, 1.0, 0.0),
    (-1.2, 1.0, 0.0),
    (0.0, -1.0, 1.5),
    (0.0, 1.0, 1.5),
]
tent_faces = [
    (0, 1, 4),      # front triangle
    (2, 3, 5),      # back triangle
    (0, 4, 5, 3),   # left slope
    (1, 2, 5, 4),   # right slope
    (0, 3, 2, 1),   # bottom
]
tent_mesh = bpy.data.meshes.new("TentMesh")
tent_mesh.from_pydata(tent_verts, [], tent_faces)
tent_mesh.update()
tent_obj = bpy.data.objects.new("Tent", tent_mesh)
bpy.context.collection.objects.link(tent_obj)
tent_obj.location = (0, 0, 0)
tent_obj.data.materials.append(mat_tent)

# --- Campfire ---
# Stones in a circle
for i in range(10):
    angle = i * 2 * math.pi / 10
    x = 3.0 + 0.5 * math.cos(angle)
    y = 0.0 + 0.5 * math.sin(angle)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.12, location=(x, y, 0.06))
    stone = bpy.context.object
    stone.name = f"Stone_{i}"
    stone.scale = (1.0, 1.0, 0.6)
    stone.data.materials.append(mat_stone)

# Fire logs (crossed)
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.2, location=(3.0, 0.0, 0.15), rotation=(0, math.pi/2, 0))
log1 = bpy.context.object
log1.name = "FireLog1"
log1.data.materials.append(mat_log)

bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.2, location=(3.0, 0.0, 0.25), rotation=(math.pi/2, 0, 0))
log2 = bpy.context.object
log2.name = "FireLog2"
log2.data.materials.append(mat_log)

# Fire flame (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.25, radius2=0.05, depth=0.6, location=(3.0, 0.0, 0.5))
flame = bpy.context.object
flame.name = "FireFlame"
flame.data.materials.append(mat_fire)

# Point light for fire
bpy.ops.object.light_add(type='POINT', location=(3.0, 0.0, 0.5))
fire_light = bpy.context.object
fire_light.name = "FireLight"
fire_light.data.energy = 50
fire_light.data.color = (1.0, 0.5, 0.2)
fire_light.data.shadow_soft_size = 0.3

# --- Log Bench ---
# Two horizontal logs as seat
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.0, location=(-3.0, 0.0, 0.3), rotation=(0, math.pi/2, 0))
bench_log1 = bpy.context.object
bench_log1.name = "BenchLog1"
bench_log1.data.materials.append(mat_log)

bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.0, location=(-3.0, 0.5, 0.3), rotation=(0, math.pi/2, 0))
bench_log2 = bpy.context.object
bench_log2.name = "BenchLog2"
bench_log2.data.materials.append(mat_log)

# Support logs (vertical)
for y_pos in [-0.8, 0.8]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.6, location=(-3.0, y_pos, 0.15))
    support = bpy.context.object
    support.name = f"BenchSupport_{y_pos}"
    support.data.materials.append(mat_log)

# --- Pine Trees ---
def create_pine_tree(x, y, scale=1.0):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15 * scale, depth=2.0 * scale, location=(x, y, 1.0 * scale))
    trunk = bpy.context.object
    trunk.name = f"PineTrunk_{x}_{y}"
    trunk.data.materials.append(mat_pine_trunk)

    # Foliage layers (cones)
    layers = 4
    for i in range(layers):
        h_offset = (1.5 + i * 0.6) * scale
        radius = (1.2 - i * 0.25) * scale
        depth = (1.0 - i * 0.1) * scale
        bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=0.0, depth=depth, location=(x, y, h_offset + depth/2))
        cone = bpy.context.object
        cone.name = f"PineLeaf_{x}_{y}_{i}"
        cone.data.materials.append(mat_pine_leaf)

# Place pine trees around the campsite
tree_positions = [
    (-8, -6, 1.2),
    (-10, 2, 1.0),
    (-6, 8, 1.3),
    (0, -10, 1.1),
    (5, -8, 1.0),
    (8, -4, 1.2),
    (10, 3, 1.1),
    (7, 8, 1.3),
    (-3, -9, 1.0),
    (-8, 5, 1.1),
    (3, 10, 1.2),
    (-5, -7, 1.0),
]

for tx, ty, ts in tree_positions:
    create_pine_tree(tx, ty, ts)

# Add a few more random trees in the background
random.seed(42)
for _ in range(15):
    tx = random.uniform(-20, 20)
    ty = random.uniform(-20, 20)
    # Keep away from center campsite
    if math.sqrt(tx**2 + ty**2) > 12:
        ts = random.uniform(0.8, 1.5)
        create_pine_tree(tx, ty, ts)

# Sun light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20), rotation=(math.radians(45), 0, math.radians(45)))
sun = bpy.context.object
sun.name = "Sun"
sun.data.energy = 3.0
sun.data.color = (1.0, 0.95, 0.85)

# World background
world = bpy.data.worlds.get("World")
if world is None:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs['Color'].default_value = (0.4, 0.6, 0.9, 1.0)
    bg.inputs['Strength'].default_value = 0.5

# Camera
bpy.ops.object.camera_add(location=(12, -12, 8), rotation=(math.radians(55), 0, math.radians(45)))
camera = bpy.context.object
camera.name = "CampsiteCamera"
scene.camera = camera

# Render settings
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'

print("Campsite scene created successfully!")
