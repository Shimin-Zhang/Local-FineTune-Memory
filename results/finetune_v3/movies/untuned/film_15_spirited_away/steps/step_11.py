import bpy
import math
from mathutils import Vector

# The test cube is at (0,5,5) and should be visible. The camera is at (0,135,18) looking at (0,5,10).
# The issue might be that the camera is looking in the wrong direction or the objects are behind the camera.
# Let's verify by checking the camera's forward direction.

camera = bpy.data.objects.get("MainCamera")
if camera:
    # Get camera forward vector
    forward = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    print(f"Camera forward: {forward}")
    print(f"Camera location: {camera.location}")
    
    # The camera should be looking in the -Y direction (from y=135 towards y=5)
    # Forward should be approximately (0, -1, 0)
    
    # Let's try setting the rotation manually
    camera.rotation_euler = (math.radians(90), 0, 0)  # Look straight down -Y
    print(f"New camera rotation: {camera.rotation_euler}")

# Remove the test cube
test_cube = bpy.data.objects.get("TestCube")
if test_cube:
    bpy.data.objects.remove(test_cube, do_unlink=True)

# Set a proper night scene
world = bpy.context.scene.world
if world and world.use_nodes:
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.02, 0.03, 0.08, 1.0)
        bg_node.inputs[1].default_value = 1.0

# Add strong lighting
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        if obj.data.type == 'SUN':
            obj.data.energy = 5.0
        elif obj.data.type == 'POINT':
            obj.data.energy = max(obj.data.energy, 20000)
        elif obj.data.type == 'AREA':
            obj.data.energy = max(obj.data.energy, 10000)

# Set view
scene = bpy.context.scene
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.5

# Make sure bathhouse is bright
for obj in bpy.data.objects:
    if obj.type == 'MESH' and ("Bathhouse" in obj.name or "Bridge" in obj.name or "Torii" in obj.name):
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = (0.5, 0.25, 0.1, 1.0)
                    bsdf.inputs["Roughness"].default_value = 0.5
    elif obj.type == 'MESH' and ("Window" in obj.name or "Lantern" in obj.name or "Glow" in obj.name):
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Emission Color"].default_value = (1.0, 0.5, 0.15, 1.0)
                    bsdf.inputs["Emission Strength"].default_value = 50.0
    elif obj.type == 'MESH' and "Water" in obj.name:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = (0.05, 0.1, 0.2, 1.0)
                    bsdf.inputs["Roughness"].default_value = 0.05
                    bsdf.inputs["Metallic"].default_value = 0.8
