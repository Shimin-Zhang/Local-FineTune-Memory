import bpy
import math
import random
from mathutils import Vector

# The scene is now too bright (daytime look). We need to bring it back to night
# while keeping the bathhouse visible. Let's rebalance.

# 1. Darken the world back to night
world = bpy.context.scene.world
if world and world.use_nodes:
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.01, 0.02, 0.05, 1.0)
        bg_node.inputs[1].default_value = 0.5

# 2. Reduce the massive area light and sun
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        if obj.name in ["VeryBrightSun", "MassiveArea", "BrightMoon", "BrightKeyLight", "HugeFill"]:
            if obj.data.type == 'SUN':
                obj.data.energy = 2.0
            elif obj.data.type == 'AREA':
                obj.data.energy = 2000
        elif obj.name in ["CenterBright", "EntranceBright", "Backlight", "LeftBright", "RightBright", "RimBright"]:
            obj.data.energy = 5000
        elif "BridgeBright" in obj.name or "BridgeLight" in obj.name:
            obj.data.energy = 3000
        elif "LanternGlow" in obj.name or "BigBridgeLanternLight" in obj.name:
            obj.data.energy = 1000

# 3. Set view to proper night exposure
scene = bpy.context.scene
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.5

# 4. Make sure the bathhouse geometry is actually visible - check if objects are hidden
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.hide_render = False
        obj.hide_viewport = False

# 5. Reposition camera to a good viewing angle
camera = bpy.data.objects.get("MainCamera")
if camera:
    # Position to see the bathhouse from the bridge direction
    camera.location = (0, 120, 15)
    # Look at the bathhouse center
    target = Vector((0, 5, 10))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    camera.data.lens = 40

# 6. Add a moderate key light to illuminate the bathhouse
bpy.ops.object.light_add(type='POINT', location=(0, 30, 20))
key_mod = bpy.context.active_object
key_mod.name = "KeyModerate"
key_mod.data.energy = 8000
key_mod.data.color = (1.0, 0.7, 0.4)
key_mod.data.shadow_soft_size = 10

# 7. Add a cool fill from the moon direction
bpy.ops.object.light_add(type='SUN', location=(50, -100, 100))
moon_fill = bpy.context.active_object
moon_fill.name = "MoonFill"
moon_fill.data.energy = 1.5
moon_fill.data.color = (0.6, 0.7, 1.0)
moon_fill.rotation_euler = (math.radians(40), math.radians(20), 0)

# 8. Make the bathhouse wood material a bit brighter for visibility
for obj in bpy.data.objects:
    if obj.type == 'MESH' and ("Bathhouse" in obj.name or "Bridge" in obj.name or "Torii" in obj.name):
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    # Boost base color slightly
                    bc = bsdf.inputs["Base Color"].default_value
                    bsdf.inputs["Base Color"].default_value = (
                        min(bc[0] * 1.3, 1.0),
                        min(bc[1] * 1.3, 1.0),
                        min(bc[2] * 1.3, 1.0),
                        1.0
                    )

# 9. Ensure windows and lanterns are glowing strongly
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    if "Window" in obj.name or "Lantern" in obj.name or "Glow" in obj.name:
                        bsdf.inputs["Emission Strength"].default_value = 25.0

# 10. Add a subtle fog for atmosphere
# Remove old fog if exists
old_fog = bpy.data.objects.get("FogVolume")
if old_fog:
    bpy.data.objects.remove(old_fog, do_unlink=True)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 50, 10))
fog = bpy.context.active_object
fog.name = "NightFog"
fog.scale = (200, 150, 40)
mat_fog = bpy.data.materials.new("NightFogMat")
mat_fog.use_nodes = True
mat_fog.blend_method = 'BLEND'
bsdf = mat_fog.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.05, 0.08, 0.15, 1.0)
bsdf.inputs["Alpha"].default_value = 0.08
bsdf.inputs["Roughness"].default_value = 1.0
fog.data.materials.append(mat_fog)

# 11. Add water reflections - make water surface reflective
water = bpy.data.objects.get("WaterSurface")
if water:
    for mat in water.data.materials:
        if mat.use_nodes:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.02, 0.05, 0.12, 1.0)
                bsdf.inputs["Roughness"].default_value = 0.05
                bsdf.inputs["Metallic"].default_value = 0.8

# 12. Add a few more detail elements - bamboo stalks near the bridge
for i in range(10):
    x = random.uniform(-15, 15)
    y = random.uniform(35, 50)
    height = random.uniform(5, 10)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=height, location=(x, y, height/2))
    bamboo = bpy.context.active_object
    bamboo.name = f"Bamboo_{i}"
    mat_bamboo = bpy.data.materials.new(f"BambooMat_{i}")
    mat_bamboo.use_nodes = True
    bsdf = mat_bamboo.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.2, 0.35, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
    bamboo.data.materials.append(mat_bamboo)

# 13. Add a small stone path along the bridge
for i in range(20):
    y = 42 + i * 4
    x = random.uniform(-2, 2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.3))
    stone = bpy.context.active_object
    stone.name = f"PathStone_{i}"
    stone.scale = (1.5, 1.5, 0.2)
    mat_stone = bpy.data.materials.new(f"PathStoneMat_{i}")
    mat_stone.use_nodes = True
    bsdf = mat_stone.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.4, 0.38, 0.35, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    stone.data.materials.append(mat_stone)

# 14. Final camera check - make sure we're looking at the right place
if camera:
    # Adjust to frame the bathhouse and bridge nicely
    camera.location = (0, 130, 18)
    target = Vector((0, 10, 8))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    camera.data.lens = 45
