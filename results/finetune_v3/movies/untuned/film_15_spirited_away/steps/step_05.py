import bpy
import math
import random
from mathutils import Vector

# The scene is still very dark. Let's dramatically increase lighting and check camera.
# First, let's make sure we can see the bathhouse by boosting all lights significantly

# Boost all existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        if obj.data.type == 'POINT':
            obj.data.energy *= 3
        elif obj.data.type == 'SUN':
            obj.data.energy *= 2
        elif obj.data.type == 'AREA':
            obj.data.energy *= 3

# Add a very bright key light to illuminate the whole scene
bpy.ops.object.light_add(type='SUN', location=(0, 0, 100))
bright_sun = bpy.context.active_object
bright_sun.name = "BrightKeyLight"
bright_sun.data.energy = 5.0
bright_sun.data.color = (1.0, 0.85, 0.6)
bright_sun.rotation_euler = (math.radians(60), math.radians(10), 0)

# Add a warm fill from the front
bpy.ops.object.light_add(type='AREA', location=(0, 80, 20))
warm_fill = bpy.context.active_object
warm_fill.name = "WarmFill"
warm_fill.data.energy = 2000
warm_fill.data.color = (1.0, 0.7, 0.4)
warm_fill.data.size = 40
warm_fill.rotation_euler = (math.radians(90), 0, 0)

# Reposition camera to clearly see the bathhouse and bridge
camera = bpy.data.objects.get("MainCamera")
if camera:
    # Bathhouse is at y=5, bridge extends to y=120
    # Camera should be at a distance where we can see both
    camera.location = (0, 130, 20)
    camera.rotation_euler = (math.radians(82), 0, 0)
    camera.data.lens = 40

# Make sure the bathhouse main body is visible - check if it's being occluded
# Let's also add some edge lighting to define the bathhouse silhouette

# Add rim lights on the sides of the bathhouse
bpy.ops.object.light_add(type='POINT', location=(-55, 5, 15))
rim_left = bpy.context.active_object
rim_left.name = "RimLeft"
rim_left.data.energy = 1500
rim_left.data.color = (0.4, 0.5, 0.8)
rim_left.data.shadow_soft_size = 5

bpy.ops.object.light_add(type='POINT', location=(55, 5, 15))
rim_right = bpy.context.active_object
rim_right.name = "RimRight"
rim_right.data.energy = 1500
rim_right.data.color = (0.4, 0.5, 0.8)
rim_right.data.shadow_soft_size = 5

# Add a spotlight on the bathhouse entrance
bpy.ops.object.light_add(type='SPOT', location=(0, 35, 25))
spot_entrance = bpy.context.active_object
spot_entrance.name = "EntranceSpot"
spot_entrance.data.energy = 5000
spot_entrance.data.color = (1.0, 0.8, 0.5)
spot_entrance.data.spot_size = math.radians(60)
spot_entrance.data.shadow_soft_size = 3
# Point it at the entrance
direction = Vector((0, 20, 5)) - Vector((0, 35, 25))
spot_entrance.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

# Add more detailed roof tiles - create a pattern of small boxes on the roof
# This will give the roof more texture
roof_base = bpy.data.objects.get("MainRoof")
if roof_base:
    for i in range(20):
        x = -30 + i * 3
        for j in range(8):
            y = -15 + j * 4
            z = 18 + j * 0.5  # Slight slope
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 5, z))
            tile = bpy.context.active_object
            tile.name = f"RoofTile_{i}_{j}"
            tile.scale = (2.5, 3, 0.3)
            mat_tile = bpy.data.materials.get("RoofTileMat")
            if not mat_tile:
                mat_tile = bpy.data.materials.new("RoofTileMat")
                mat_tile.use_nodes = True
                bsdf = mat_tile.node_tree.nodes.get("Principled BSDF")
                bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.12, 1.0)
            tile.data.materials.append(mat_tile)

# Add decorative clouds in the sky (simple flat planes)
for i in range(8):
    x = random.uniform(-150, 150)
    y = random.uniform(-250, -150)
    z = random.uniform(60, 120)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
    cloud = bpy.context.active_object
    cloud.name = f"Cloud_{i}"
    cloud.scale = (random.uniform(20, 40), random.uniform(5, 15), 1)
    cloud.rotation_euler = (math.radians(90), 0, 0)
    mat_cloud = bpy.data.materials.new(f"CloudMat_{i}")
    mat_cloud.use_nodes = True
    mat_cloud.blend_method = 'BLEND'
    bsdf = mat_cloud.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.15, 0.18, 0.25, 1.0)
    bsdf.inputs["Alpha"].default_value = 0.4
    bsdf.inputs["Roughness"].default_value = 1.0
    cloud.data.materials.append(mat_cloud)

# Add a large moon with glow
moon = bpy.data.objects.get("Moon")
if moon:
    # Add a glow light around the moon
    bpy.ops.object.light_add(type='POINT', location=moon.location)
    moon_glow_light = bpy.context.active_object
    moon_glow_light.name = "MoonGlowLight"
    moon_glow_light.data.energy = 500
    moon_glow_light.data.color = (0.8, 0.85, 1.0)
    moon_glow_light.data.shadow_soft_size = 20

# Add a subtle fog effect using a large transparent cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 50, 10))
fog = bpy.context.active_object
fog.name = "FogVolume"
fog.scale = (200, 150, 40)
mat_fog = bpy.data.materials.new("FogMat")
mat_fog.use_nodes = True
mat_fog.blend_method = 'BLEND'
bsdf = mat_fog.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.1, 0.12, 0.18, 1.0)
bsdf.inputs["Alpha"].default_value = 0.05
bsdf.inputs["Roughness"].default_value = 1.0
fog.data.materials.append(mat_fog)

# Add more lanterns along the bridge - make them bigger and brighter
for i in range(8):
    y = 45 + i * 10
    for side in [-1, 1]:
        # Remove old lanterns at this position if they exist
        # Add new bigger lantern
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(side * 3.5, y, 3.5))
        big_lantern = bpy.context.active_object
        big_lantern.name = f"BigBridgeLantern_{side}_{i}"
        big_lantern.scale = (1, 1, 1.4)
        mat_bl = bpy.data.materials.new(f"BigBridgeLanternMat_{side}_{i}")
        mat_bl.use_nodes = True
        bsdf = mat_bl.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (1.0, 0.35, 0.08, 1.0)
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.45, 0.1, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 12.0
        big_lantern.data.materials.append(mat_bl)
        
        # Add a point light for each big lantern
        bpy.ops.object.light_add(type='POINT', location=(side * 3.5, y, 3.5))
        bl_light = bpy.context.active_object
        bl_light.name = f"BigBridgeLanternLight_{side}_{i}"
        bl_light.data.energy = 200
        bl_light.data.color = (1.0, 0.5, 0.1)
        bl_light.data.shadow_soft_size = 2

# Add a final polish - make the water more reflective with a mirror-like material
water = bpy.data.objects.get("WaterSurface")
if water:
    for mat in water.data.materials:
        if mat.use_nodes:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Roughness"].default_value = 0.02
                bsdf.inputs["Metallic"].default_value = 0.9
                bsdf.inputs["Base Color"].default_value = (0.02, 0.05, 0.15, 1.0)

# Set the scene to use a better render engine if available
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
