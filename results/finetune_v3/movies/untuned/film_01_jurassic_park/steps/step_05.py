import bpy
import math
import random
from mathutils import Vector

# Remove trees that are blocking the view
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.location.y < -5 and obj.location.x < 0:
        bpy.data.objects.remove(obj, do_unlink=True)

# Reposition camera to see the T. rex, cars, and fence
cam = bpy.context.scene.camera
if cam:
    cam.location = (18, -12, 4)
    # Point at the T. rex area
    target = Vector((-8, 0, 1.5))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    cam.data.lens = 50

# Boost lighting for visibility
for light in bpy.data.objects:
    if light.type == 'SUN':
        light.data.energy = 1.0
    elif light.type == 'SPOT':
        light.data.energy = 1500
    elif light.type == 'AREA':
        light.data.energy = 20

# Add more rain splashes
mat_rain_splash = bpy.data.materials.get("RainSplash")
if mat_rain_splash is None:
    mat_rain_splash = bpy.data.materials.new("RainSplash")
    mat_rain_splash.use_nodes = True
    bsdf = mat_rain_splash.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.6, 0.7, 0.9, 1.0)
    bsdf.inputs["Emission Color"].default_value = (0.4, 0.5, 0.8, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 0.5

for i in range(40):
    sx = random.uniform(-12, 12)
    sy = random.uniform(-12, 12)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(sx, sy, 0.05))
    splash = bpy.context.active_object
    splash.scale = (random.uniform(0.05, 0.15), random.uniform(0.05, 0.15), 1)
    splash.data.materials.append(mat_rain_splash)
    bpy.ops.object.transform_apply(scale=True)

# Add wet road reflection effect (darker puddles)
mat_puddle = bpy.data.materials.get("Puddle")
if mat_puddle:
    for i in range(10):
        px = random.uniform(-3, 3)
        py = random.uniform(-15, 15)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(px, py, 0.04))
        puddle = bpy.context.active_object
        puddle.scale = (random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), 1)
        puddle.data.materials.append(mat_puddle)
        bpy.ops.object.transform_apply(scale=True)

# Add broken fence debris more prominently
mat_wire = bpy.data.materials.get("Wire")
mat_metal_dark = bpy.data.materials.get("MetalDark")

for i in range(8):
    dx = random.uniform(-12, -8)
    dy = random.uniform(-5, 5)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=random.uniform(0.5, 2), location=(dx, dy, 0.05), rotation=(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)))
    debris = bpy.context.active_object
    debris.data.materials.append(mat_wire)

# Add some broken fence posts lying down
for i in range(4):
    dx = random.uniform(-12, -7)
    dy = random.uniform(-5, 5)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.5, location=(dx, dy, 0.15), rotation=(math.pi/2, 0, random.uniform(0, math.pi)))
    post = bpy.context.active_object
    post.data.materials.append(mat_metal_dark)

# Add T. rex footprints in mud
mat_dirt = bpy.data.materials.get("Dirt")
for i in range(6):
    fx = -8 + i * 1.5
    fy = random.uniform(-2, 2)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(fx, fy, 0.03))
    print_obj = bpy.context.active_object
    print_obj.scale = (0.5, 0.8, 1)
    print_obj.data.materials.append(mat_dirt)
    bpy.ops.object.transform_apply(scale=True)

# Add more rocks near the fence
mat_rock = bpy.data.materials.get("Rock")
for i in range(10):
    rx = random.uniform(-12, -6)
    ry = random.uniform(-8, 8)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(0.1, 0.3), location=(rx, ry, 0.1))
    rock = bpy.context.active_object
    rock.scale = (random.uniform(0.5, 1.2), random.uniform(0.5, 1.2), random.uniform(0.3, 0.6))
    rock.data.materials.append(mat_rock)
    bpy.ops.object.transform_apply(scale=True)

# Add a few more trees in the far background (not blocking view)
mat_tree = bpy.data.materials.get("Tree")
mat_trunk = bpy.data.materials.get("Trunk")
for i in range(10):
    tx = random.uniform(-25, 25)
    ty = random.uniform(-40, -25)
    if abs(tx) < 10:
        continue
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=3, location=(tx, ty, 1.5))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_trunk)
    bpy.ops.mesh.primitive_cone_add(radius1=1.5, radius2=0.1, depth=3, location=(tx, ty, 4))
    foliage = bpy.context.active_object
    foliage.data.materials.append(mat_tree)

# Add lightning flash effect (brief bright light)
bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
lightning = bpy.context.active_object
lightning.data.energy = 0  # Will be animated
lightning.data.color = (0.8, 0.8, 1.0)
lightning.rotation_euler = (math.radians(30), math.radians(10), 0)
lightning.name = "Lightning"

# Set up lightning animation
lightning.data.energy = 0
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250
# Keyframe lightning
lightning.data.energy = 0
lightning.keyframe_insert(data_path="energy", frame=1)
lightning.data.energy = 50
lightning.keyframe_insert(data_path="energy", frame=10)
lightning.data.energy = 0
lightning.keyframe_insert(data_path="energy", frame=15)
lightning.data.energy = 0
lightning.keyframe_insert(data_path="energy", frame=50)
lightning.data.energy = 30
lightning.keyframe_insert(data_path="energy", frame=55)
lightning.data.energy = 0
lightning.keyframe_insert(data_path="energy", frame=60)

# Add fog volume using a different approach - use world volume
world = bpy.context.scene.world
if world:
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    # Remove existing volume if any
    for node in nodes:
        if node.type == 'VOLUME_SCATTER':
            nodes.remove(node)
    # Add volume scatter
    vol_scatter = nodes.new('ShaderNodeVolumeScatter')
    vol_scatter.inputs['Color'].default_value = (0.5, 0.6, 0.8, 1.0)
    vol_scatter.inputs['Density'].default_value = 0.01
    bg = nodes.get('Background')
    if bg:
        # Connect volume to world output
        world_output = nodes.get('World Output')
        if world_output:
            links.new(vol_scatter.outputs['Volume'], world_output.inputs['Volume'])

# Final render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.view_settings.look = 'AgX - Punchy'
bpy.context.scene.view_settings.exposure = -0.2

print("Scene refined with camera fix, lightning, fog, and more details")
