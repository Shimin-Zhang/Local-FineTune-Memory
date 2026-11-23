import bpy
import math
from mathutils import Vector

# The camera keeps ending up pointing up. Let me set it with explicit euler angles.
cam = bpy.data.objects.get("Camera")
if cam:
    # Put camera at a clear position in front of the maze
    # Maze is centered around z=0, hotel at z=-55
    # Camera should be at positive z, looking toward negative z
    cam.location = (30, 20, 45)
    
    # Explicitly set rotation: look toward the scene
    # We want to look in the -Z direction and slightly down
    # Camera default looks down -Z. So we need to tilt it to look at the scene.
    # Target point: middle of the maze area
    target = Vector((0, 3, -15))
    d = target - cam.location
    # d points from camera to target
    # Camera's -Z axis should point along d
    # Use to_track_quat: the first arg is the axis to align with the vector
    quat = d.to_track_quat('-Z', 'Y')
    cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = quat
    
    # Verify: print the resulting euler
    euler = quat.to_euler()
    print(f"Camera euler: {euler.x:.2f}, {euler.y:.2f}, {euler.z:.2f}")
    print(f"Camera loc: {cam.location.x:.1f}, {cam.location.y:.1f}, {cam.location.z:.1f}")
    print(f"Target: {target.x:.1f}, {target.y:.1f}, {target.z:.1f}")
    print(f"Direction: {d.x:.1f}, {d.y:.1f}, {d.z:.1f}")

# Also make sure the fog box isn't blocking the view
fog_box = bpy.data.objects.get("Cube")
# The fog box might be the last cube added - let's find it by material
for obj in bpy.context.collection.objects:
    if obj.type == 'MESH' and len(obj.data.materials) > 0:
        if obj.data.materials[0].name == "fog_mat":
            # Make it not block camera
            obj.visible_camera = False
            print(f"Fog box found: {obj.name}")

# Add a few more details: snow-covered mailbox, and a small sign
mat_sign = bpy.data.materials.new("sign_mat")
mat_sign.use_nodes = True
mat_sign.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.7, 0.5, 1.0)
mat_sign.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.7

# Sign post near the path
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.5, location=(-5, 0.75, -3))
sign_post = bpy.context.active_object
sign_post.data.materials.append(bpy.data.materials.get("trunk_mat"))

# Sign board
bpy.ops.mesh.primitive_cube_add(size=1, location=(-5, 1.5, -3))
sign_board = bpy.context.active_object
sign_board.scale = (1.2, 0.05, 0.6)
sign_board.data.materials.append(mat_sign)

# Snow on sign
bpy.ops.mesh.primitive_cube_add(size=1, location=(-5, 1.55, -3))
sign_snow = bpy.context.active_object
sign_snow.scale = (1.2, 0.1, 0.6)
sign_snow.data.materials.append(bpy.data.materials.get("snow"))

# Mailbox
bpy.ops.mesh.primitive_cube_add(size=1, location=(5, 1, -3))
mailbox = bpy.context.active_object
mailbox.scale = (0.5, 0.5, 0.4)
mailbox.data.materials.append(bpy.data.materials.get("trunk_mat"))

bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1, location=(5, 0.5, -3))
mb_post = bpy.context.active_object
mb_post.data.materials.append(bpy.data.materials.get("trunk_mat"))

# Snow on mailbox
bpy.ops.mesh.primitive_cube_add(size=1, location=(5, 1.25, -3))
mb_snow = bpy.context.active_object
mb_snow.scale = (0.5, 0.15, 0.4)
mb_snow.data.materials.append(bpy.data.materials.get("snow"))

# Add a few more warm point lights inside the hotel to make windows glow more
for wx in [-8, 0, 8]:
    bpy.ops.object.light_add(type='POINT', location=(wx, 10, -55))
    il = bpy.context.active_object
    il.data.energy = 30
    il.data.color = (1.0, 0.7, 0.3)
    il.data.shadow_soft_size = 5

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0.3
scene.frame_set(100)

print("Camera should now look at the scene. Added sign, mailbox, interior lights.")
