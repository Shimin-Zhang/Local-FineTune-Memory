import bpy
import math
import random
from mathutils import Vector

# The scene is still too dark. Let's aggressively fix lighting.

# 1. Remove or drastically reduce volume scatter - it's blocking light
world = bpy.context.scene.world
if world and world.use_nodes:
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    # Remove volume scatter nodes
    for node in list(nodes):
        if node.type == 'VOLUME_SCATTER':
            # Disconnect and remove
            for link in list(links):
                if link.to_node == node:
                    links.remove(link)
            nodes.remove(node)

# 2. Boost all lights dramatically
fire_light = bpy.data.objects.get("Fire_Light")
if fire_light:
    fire_light.data.energy = 10000
    fire_light.data.shadow_soft_size = 2.0

for i in range(4):
    tl = bpy.data.objects.get(f"Torch_Light_{i}")
    if tl:
        tl.data.energy = 1000

rim_light = bpy.data.objects.get("Rim_Light")
if rim_light:
    rim_light.data.energy = 3000

sun = bpy.data.objects.get("Ambient_Sun")
if sun:
    sun.data.energy = 5.0

# 3. Add a strong area light to illuminate the whole scene
bpy.ops.object.light_add(type='AREA', location=(0, 0, 8))
area_light = bpy.context.object
area_light.name = "Scene_Fill_Light"
area_light.data.energy = 5000
area_light.data.color = (1.0, 0.6, 0.3)
area_light.data.size = 10
area_light.rotation_euler = (0, 0, 0)

# 4. Boost emission on all fire/glow materials
mat_names = ["Fire", "FireInner", "BalrogFire", "BalrogEye", "Glow"]
for mat_name in mat_names:
    mat = bpy.data.materials.get(mat_name)
    if mat:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Emission Strength"].default_value = 50.0

# 5. Adjust view settings for brighter image
scene = bpy.context.scene
scene.view_settings.exposure = 3.0
scene.view_settings.gamma = 1.2
scene.view_settings.look = 'AgX - Base'  # Try a different look

# 6. Make sure camera is pointing correctly
camera = bpy.data.objects.get("Main_Camera")
if camera:
    # Position camera to see both Gandalf and Balrog clearly
    camera.location = (-4, 3, 2.5)
    target = Vector((1.5, 0, 1.5))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    # Set focal length for wider view
    camera.data.lens = 35

# 7. Add more visible fire - large fireballs near Balrog
mat_fire = bpy.data.materials.get("Fire")
mat_fire_inner = bpy.data.materials.get("FireInner")

for i in range(12):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0.5, 2.5)
    x = 4.5 - 1.0 + dist * math.cos(angle)
    y = dist * math.sin(angle)
    z = 0.2 + random.uniform(0.3, 2.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.2, 0.4), location=(x, y, z))
    fire = bpy.context.object
    fire.name = f"FireLarge_{i}"
    fire.data.materials.append(mat_fire_inner if random.random() > 0.3 else mat_fire)

# 8. Add a large glowing fire plane under the Balrog area
if mat_fire_inner:
    bpy.ops.mesh.primitive_plane_add(size=1, location=(4.0, 0, 0.25))
    fire_plane = bpy.context.object
    fire_plane.name = "Fire_Floor"
    fire_plane.scale = (3.0, 2.5, 1)
    fire_plane.data.materials.append(mat_fire_inner)
    bpy.ops.object.transform_apply(scale=True)

# 9. Add stone texture details - more cracks on bridge
mat_stone_dark = bpy.data.materials.get("StoneDark")
if mat_stone_dark:
    for i in range(30):
        x = random.uniform(-5.5, 5.5)
        y = random.uniform(-0.8, 0.8)
        z = 0.21
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
        crack = bpy.context.object
        crack.name = f"Bridge_Crack_{i}"
        crack.scale = (random.uniform(0.03, 0.1), random.uniform(0.03, 0.1), 0.01)
        crack.data.materials.append(mat_stone_dark)
        bpy.ops.object.transform_apply(scale=True)

# 10. Add more architectural details - carved faces on pillars
mat_stone_pillar = bpy.data.materials.get("PillarStone")
if mat_stone_pillar:
    # Add carved face details on the end pillars
    for px, py in [(-6, -1.5), (-6, 1.5), (6, -1.5), (6, 1.5)]:
        # Face indentation
        bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, 1.5))
        face = bpy.context.object
        face.name = f"Pillar_Face_{px}_{py}"
        face.scale = (0.3, 0.4, 0.5)
        face.data.materials.append(mat_stone_dark)
        bpy.ops.object.transform_apply(scale=True)

# 11. Add Gandalf's pointed shoes
mat_cloth_dark = bpy.data.materials.get("ClothDark")
if mat_cloth_dark:
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.02, depth=0.2, location=(-1.5, -0.1, 0.22))
    shoe_l = bpy.context.object
    shoe_l.name = "Gandalf_Shoe_L"
    shoe_l.rotation_euler = (0, math.radians(90), 0)
    shoe_l.data.materials.append(mat_cloth_dark)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.02, depth=0.2, location=(-1.5, 0.1, 0.22))
    shoe_r = bpy.context.object
    shoe_r.name = "Gandalf_Shoe_R"
    shoe_r.rotation_euler = (0, math.radians(90), 0)
    shoe_r.data.materials.append(mat_cloth_dark)

# 12. Add Balrog's horned head detail
mat_balrog_body = bpy.data.materials.get("BalrogBody")
if mat_balrog_body:
    # Horns
    bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0.02, depth=0.5, location=(4.5 - 1.2, -0.3, 0.2 + 3.8))
    horn_l = bpy.context.object
    horn_l.name = "Balrog_Horn_L"
    horn_l.rotation_euler = (math.radians(-30), 0, 0)
    horn_l.data.materials.append(mat_balrog_body)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0.02, depth=0.5, location=(4.5 - 1.2, 0.3, 0.2 + 3.8))
    horn_r = bpy.context.object
    horn_r.name = "Balrog_Horn_R"
    horn_r.rotation_euler = (math.radians(-30), 0, 0)
    horn_r.data.materials.append(mat_balrog_body)

# 13. Add more smoke columns
mat_smoke = bpy.data.materials.get("Smoke")
if mat_smoke:
    for i in range(6):
        x = 4.5 - 0.5 + random.uniform(-0.5, 0.5)
        y = random.uniform(-0.5, 0.5)
        for j in range(5):
            z = 3.5 + j * 0.6
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25 + j * 0.05, location=(x, y, z))
            smoke = bpy.context.object
            smoke.name = f"SmokeCol_{i}_{j}"
            smoke.data.materials.append(mat_smoke)

# 14. Add a subtle blue moonlight from above for contrast
bpy.ops.object.light_add(type='SUN', location=(0, -5, 10))
moon_light = bpy.context.object
moon_light.name = "Moon_Light"
moon_light.data.energy = 1.0
moon_light.data.color = (0.3, 0.4, 0.6)
moon_light.rotation_euler = (math.radians(30), 0, 0)

# 15. Add more embers
mat_ember = bpy.data.materials.get("FireInner")
if mat_ember:
    for i in range(20):
        x = random.uniform(-3, 5)
        y = random.uniform(-2, 2)
        z = random.uniform(0.5, 5)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.02, 0.04), location=(x, y, z))
        ember = bpy.context.object
        ember.name = f"Ember2_{i}"
        ember.data.materials.append(mat_ember)

# 16. Add a distant mountain backdrop
mat_stone_dark = bpy.data.materials.get("StoneDark")
if mat_stone_dark:
    for i in range(5):
        x = random.uniform(-10, 10)
        y = random.uniform(-15, -8)
        z = random.uniform(-2, 2)
        bpy.ops.mesh.primitive_cone_add(radius1=random.uniform(2, 5), radius2=0, depth=random.uniform(3, 8), location=(x, y, z))
        mountain = bpy.context.object
        mountain.name = f"Mountain_{i}"
        mountain.scale = (1, 0.5, 1)
        mountain.data.materials.append(mat_stone_dark)
        bpy.ops.object.transform_apply(scale=True)

print("Major lighting fix: removed volume scatter, boosted all lights, added fill light, adjusted exposure, added more fire/smoke/detail")
