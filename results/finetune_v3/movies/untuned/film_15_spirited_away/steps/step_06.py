import bpy
import math
import random
from mathutils import Vector

# The scene is still very dark. Let's take a different approach:
# 1. Massively boost all lighting
# 2. Make sure the camera is pointing at the bathhouse
# 3. Add strong emissive materials to key elements

# First, let's check what's actually in the scene and where the bathhouse is
bathhouse = bpy.data.objects.get("BathhouseMain")
bridge = bpy.data.objects.get("BridgeDeck")
camera = bpy.data.objects.get("MainCamera")

print(f"Bathhouse: {bathhouse.location if bathhouse else 'NOT FOUND'}")
print(f"Bridge: {bridge.location if bridge else 'NOT FOUND'}")
print(f"Camera: {camera.location if camera else 'NOT FOUND'}")

# Boost ALL point lights dramatically
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        if obj.data.type == 'POINT':
            obj.data.energy = max(obj.data.energy, 5000)
        elif obj.data.type == 'SUN':
            obj.data.energy = max(obj.data.energy, 10)
        elif obj.data.type == 'AREA':
            obj.data.energy = max(obj.data.energy, 5000)
        elif obj.data.type == 'SPOT':
            obj.data.energy = max(obj.data.energy, 10000)

# Add a very bright sun to simulate moonlight
bpy.ops.object.light_add(type='SUN', location=(0, 0, 200))
bright_moon = bpy.context.active_object
bright_moon.name = "BrightMoon"
bright_moon.data.energy = 15
bright_moon.data.color = (0.8, 0.85, 1.0)
bright_moon.rotation_euler = (math.radians(45), math.radians(15), 0)

# Add a huge area light above the scene
bpy.ops.object.light_add(type='AREA', location=(0, 50, 80))
huge_fill = bpy.context.active_object
huge_fill.name = "HugeFill"
huge_fill.data.energy = 10000
huge_fill.data.color = (0.5, 0.6, 0.8)
huge_fill.data.size = 100
huge_fill.rotation_euler = (math.radians(90), 0, 0)

# Reposition camera to definitely see the bathhouse
# Bathhouse is at y=5, bridge goes from y=40 to y=120
# Camera should be at y=150, looking back at the bathhouse
if camera:
    camera.location = (0, 150, 25)
    camera.rotation_euler = (math.radians(80), 0, 0)
    camera.data.lens = 35

# Make the bathhouse windows much brighter
for obj in bpy.data.objects:
    if "Window" in obj.name and obj.type == 'MESH':
        for mat in obj.data.materials:
            if mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Emission Strength"].default_value = 20.0

# Make all lanterns very bright
for obj in bpy.data.objects:
    if "Lantern" in obj.name and obj.type == 'MESH' and "Post" not in obj.name and "Hanger" not in obj.name:
        for mat in obj.data.materials:
            if mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Emission Strength"].default_value = 30.0

# Add a very bright point light at the bathhouse entrance
bpy.ops.object.light_add(type='POINT', location=(0, 25, 10))
entrance_bright = bpy.context.active_object
entrance_bright.name = "EntranceBright"
entrance_bright.data.energy = 20000
entrance_bright.data.color = (1.0, 0.7, 0.3)
entrance_bright.data.shadow_soft_size = 10

# Add lights along the bridge
for i in range(5):
    y = 45 + i * 15
    bpy.ops.object.light_add(type='POINT', location=(0, y, 3))
    bridge_light = bpy.context.active_object
    bridge_light.name = f"BridgeLight_{i}"
    bridge_light.data.energy = 5000
    bridge_light.data.color = (1.0, 0.5, 0.1)
    bridge_light.data.shadow_soft_size = 5

# Make the roof more visible with a slightly lighter material
roof = bpy.data.objects.get("MainRoof")
if roof:
    for mat in roof.data.materials:
        if mat.use_nodes:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.25, 1.0)

# Add a strong rim light behind the bathhouse to silhouette it
bpy.ops.object.light_add(type='POINT', location=(0, -20, 20))
backlight = bpy.context.active_object
backlight.name = "Backlight"
backlight.data.energy = 15000
backlight.data.color = (0.3, 0.4, 0.8)
backlight.data.shadow_soft_size = 20

# Add a warm light from the left side
bpy.ops.object.light_add(type='POINT', location=(-60, 30, 15))
left_warm = bpy.context.active_object
left_warm.name = "LeftWarm"
left_warm.data.energy = 10000
left_warm.data.color = (1.0, 0.6, 0.3)
left_warm.data.shadow_soft_size = 10

# Add a warm light from the right side
bpy.ops.object.light_add(type='POINT', location=(60, 30, 15))
right_warm = bpy.context.active_object
right_warm.name = "RightWarm"
right_warm.data.energy = 10000
right_warm.data.color = (1.0, 0.6, 0.3)
right_warm.data.shadow_soft_size = 10

# Make the water surface more reflective and visible
water = bpy.data.objects.get("WaterSurface")
if water:
    for mat in water.data.materials:
        if mat.use_nodes:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.05, 0.1, 0.2, 1.0)
                bsdf.inputs["Roughness"].default_value = 0.0
                bsdf.inputs["Metallic"].default_value = 1.0

# Add a ground plane that's slightly lighter to give some contrast
ground = bpy.data.objects.get("WaterSurface")
if ground:
    # Make sure it's large enough
    ground.scale = (300, 300, 1)

# Add more stars
for i in range(30):
    x = random.uniform(-200, 200)
    y = random.uniform(-300, -100)
    z = random.uniform(50, 200)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x, y, z))
    star = bpy.context.active_object
    star.name = f"Star2_{i}"
    mat_star = bpy.data.materials.new(f"Star2Mat_{i}")
    mat_star.use_nodes = True
    bsdf = mat_star.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 20.0
    star.data.materials.append(mat_star)

# Set view transform to Filmic for better dynamic range
scene = bpy.context.scene
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 1.0
