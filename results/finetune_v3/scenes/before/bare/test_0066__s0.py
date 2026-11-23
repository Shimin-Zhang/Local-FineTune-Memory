import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.object.select_all(action='DESELECT')

# Lighting / world
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.65, 0.68, 0.72, 1.0)
bg.inputs[1].default_value = 1.0

# Sun (soft, rainy)
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 1.2
sun_data.color = (0.85, 0.88, 0.92)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))

# Materials
def mat(name, color, rough=0.8, metal=0.0, alpha=1.0, emissive=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND'
    if emissive > 0:
        bsdf.inputs["Emission Color"].default_value = (1,1,1,1)
        bsdf.inputs["Emission Strength"].default_value = emissive
    return m

water_mat = mat("Water", (0.15, 0.25, 0.35), rough=0.15, alpha=0.85)
stone_mat = mat("Stone", (0.55, 0.53, 0.50), rough=0.9)
wood_mat = mat("Wood", (0.35, 0.22, 0.12), rough=0.85)
roof_mat = mat("Roof", (0.25, 0.15, 0.10), rough=0.7)
leaf_mat = mat("WillowLeaf", (0.15, 0.35, 0.10), rough=0.9)
trunk_mat = mat("Trunk", (0.25, 0.18, 0.10), rough=0.95)
bank_mat = mat("Bank", (0.30, 0.28, 0.22), rough=1.0)

# Lake (large plane)
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
lake = bpy.context.active_object
lake.name = "Lake"
lake.data.materials.append(water_mat)

# Causeway: long raised path across the lake
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))
causeway = bpy.context.active_object
causeway.name = "Causeway"
causeway.scale = (1.5, 40, 0.5)
causeway.data.materials.append(stone_mat)

# Pavilion halfway along (at y=0)
# Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
plat = bpy.context.active_object
plat.name = "PavilionPlatform"
plat.scale = (3, 3, 0.2)
plat.data.materials.append(stone_mat)

# Pillars
for px in [-1.5, 1.5]:
    for py in [-1.5, 1.5]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.5, location=(px, py, 2.75))
        p = bpy.context.active_object
        p.name = "Pillar"
        p.data.materials.append(wood_mat)

# Roof (pyramid-ish)
bpy.ops.mesh.primitive_cone_add(radius=3.2, depth=1.5, vertices=4, location=(0, 0, 4.5))
roof = bpy.context.active_object
roof.name = "PavilionRoof"
roof.rotation_euler = (0, 0, math.radians(45))
roof.data.materials.append(roof_mat)

# Stone arched bridge (at y=15)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, 1.2))
bridge = bpy.context.active_object
bridge.name = "Bridge"
bridge.scale = (2, 6, 0.4)
bridge.data.materials.append(stone_mat)
# Arch opening (boolean or just visual: add a dark inset)
bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=4, location=(0, 15, 1.2), rotation=(0, math.radians(90), 0))
arch = bpy.context.active_object
arch.name = "ArchCut"
# Use as visual: make it dark to simulate opening
arch.data.materials.append(mat("Dark", (0.05,0.05,0.05)))

# Pagoda-less bank (a raised earthy mound on one side, no pagoda)
bpy.ops.mesh.primitive_uv_sphere_add(radius=8, location=(-20, -20, 0))
bank = bpy.context.active_object
bank.name = "Bank"
bank.scale = (1, 1, 0.4)
bank.data.materials.append(bank_mat)

# Willows along the causeway
random.seed(42)
for i in range(12):
    y = -35 + i * 6.5
    x = random.choice([-2.5, 2.5])
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=3, location=(x, y, 2.5))
    trunk = bpy.context.active_object
    trunk.name = "WillowTrunk"
    trunk.data.materials.append(trunk_mat)
    # Drooping foliage: several elongated spheres
    for j in range(5):
        fx = x + random.uniform(-0.8, 0.8)
        fy = y + random.uniform(-0.8, 0.8)
        fz = 3.5 - j * 0.4
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(fx, fy, fz))
        leaf = bpy.context.active_object
        leaf.name = "WillowLeaf"
        leaf.scale = (1, 1, 1.5 + j * 0.2)
        leaf.data.materials.append(leaf_mat)

# Light rain: many small falling cylinders/planes
rain_mat = mat("Rain", (0.8, 0.85, 0.9), rough=0.3, alpha=0.4)
for i in range(300):
    rx = random.uniform(-40, 40)
    ry = random.uniform(-40, 40)
    rz = random.uniform(2, 15)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.6, location=(rx, ry, rz))
    drop = bpy.context.active_object
    drop.name = "Raindrop"
    drop.rotation_euler = (math.radians(5), math.radians(5), 0)
    drop.data.materials.append(rain_mat)

# Camera
bpy.ops.object.camera_add(location=(0, -50, 8))
cam = bpy.context.active_object
cam.name = "Camera"
cam.rotation_euler = (math.radians(80), 0, 0)
bpy.context.scene.camera = cam

# Render settings
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.film_transparent = False
