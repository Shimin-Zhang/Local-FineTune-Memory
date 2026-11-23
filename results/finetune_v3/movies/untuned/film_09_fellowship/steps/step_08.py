import bpy
import math
import random
from mathutils import Vector

# The scene is still showing as a flat grey. The issue is that the camera might be 
# inside geometry or the world background is dominating. Let's do a final fix.

# 1. Set world background to black
world = bpy.context.scene.world
if world and world.use_nodes:
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        bg_node.inputs[1].default_value = 1.0

# 2. Move camera to a clear position and verify it sees the scene
camera = bpy.data.objects.get("Main_Camera")
if camera:
    # Position camera clearly outside any geometry
    camera.location = (-8, 6, 4)
    target = Vector((1.0, 0, 1.5))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    camera.data.lens = 50
    camera.data.clip_start = 0.1
    camera.data.clip_end = 1000
else:
    bpy.ops.object.camera_add(location=(-8, 6, 4))
    camera = bpy.context.object
    camera.name = "Main_Camera"
    target = Vector((1.0, 0, 1.5))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    camera.data.lens = 50
    camera.data.clip_start = 0.1
    camera.data.clip_end = 1000

bpy.context.scene.camera = camera

# 3. Boost all lights one more time
for light_obj in bpy.data.objects:
    if light_obj.type == 'LIGHT':
        if "Fire" in light_obj.name or "Torch" in light_obj.name:
            light_obj.data.energy = max(light_obj.data.energy, 5000)
        elif "Rim" in light_obj.name:
            light_obj.data.energy = max(light_obj.data.energy, 3000)
        elif "Ambient" in light_obj.name:
            light_obj.data.energy = max(light_obj.data.energy, 1.0)

# 4. Make sure emission is very strong
for mat_name in ["Fire", "FireInner", "BalrogFire", "BalrogEye", "Glow"]:
    mat = bpy.data.materials.get(mat_name)
    if mat:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Emission Strength"].default_value = 100.0

# 5. Add a bright point light right at the Balrog's mouth
bpy.ops.object.light_add(type='POINT', location=(3.0, 0, 2.8))
mouth_light = bpy.context.object
mouth_light.name = "Mouth_Fire_Light"
mouth_light.data.energy = 10000
mouth_light.data.color = (1.0, 0.3, 0.05)
mouth_light.data.shadow_soft_size = 0.5

# 6. Add more fire for visibility
mat_fire = bpy.data.materials.get("Fire")
mat_fire_inner = bpy.data.materials.get("FireInner")

# Large visible fireballs
for i in range(20):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0.5, 4.0)
    x = 4.5 + dist * math.cos(angle)
    y = dist * math.sin(angle)
    z = 0.2 + random.uniform(0.3, 4.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.3, 0.6), location=(x, y, z))
    fire = bpy.context.object
    fire.name = f"FireFinal_{i}"
    fire.data.materials.append(mat_fire_inner if random.random() > 0.3 else mat_fire)

# Fire stream
for i in range(25):
    t = i / 24.0
    x = 3.0 - t * 5.0
    y = (i % 4 - 1.5) * 0.1
    z = 2.5 - t * 1.8 + random.uniform(-0.1, 0.1)
    size = 0.4 - t * 0.25
    bpy.ops.mesh.primitive_uv_sphere_add(radius=max(0.05, size), location=(x, y, z))
    fire = bpy.context.object
    fire.name = f"FireStreamFinal_{i}"
    fire.data.materials.append(mat_fire_inner if t < 0.5 else mat_fire)

# 7. Add more smoke
mat_smoke = bpy.data.materials.get("Smoke")
if mat_smoke:
    for i in range(20):
        x = 4.0 + random.uniform(-2, 2)
        y = random.uniform(-1.5, 1.5)
        z = 4.0 + i * 0.35
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35 + i * 0.04, location=(x, y, z))
        smoke = bpy.context.object
        smoke.name = f"SmokeFinal_{i}"
        smoke.data.materials.append(mat_smoke)

# 8. Add embers
mat_ember = bpy.data.materials.get("FireInner")
if mat_ember:
    for i in range(40):
        x = random.uniform(-6, 7)
        y = random.uniform(-4, 4)
        z = random.uniform(0.5, 8)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.02, 0.06), location=(x, y, z))
        ember = bpy.context.object
        ember.name = f"EmberFinal_{i}"
        ember.data.materials.append(mat_ember)

# 9. Final render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.view_settings.exposure = 2.0
scene.view_settings.gamma = 1.0
scene.view_settings.look = 'AgX - Punchy'

print("Final fix: black background, camera repositioned, lights boosted, more fire/smoke/embers, mouth light added")
