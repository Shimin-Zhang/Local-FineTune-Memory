import bpy
import math
import random
from mathutils import Vector

# Fix the view settings look
scene = bpy.context.scene
scene.view_settings.look = 'AgX - Base Contrast'
scene.view_settings.exposure = 2.0
scene.view_settings.gamma = 1.0

# The scene is showing as a flat grey - the fill light is too strong and washing everything out
# Let's rebalance: reduce fill, keep fire lights strong

# Reduce the area fill light
area_light = bpy.data.objects.get("Scene_Fill_Light")
if area_light:
    area_light.data.energy = 500  # Much lower

# Reduce moon light
moon_light = bpy.data.objects.get("Moon_Light")
if moon_light:
    moon_light.data.energy = 0.5

# Keep fire light strong
fire_light = bpy.data.objects.get("Fire_Light")
if fire_light:
    fire_light.data.energy = 5000

# Keep torches
for i in range(4):
    tl = bpy.data.objects.get(f"Torch_Light_{i}")
    if tl:
        tl.data.energy = 500

# Keep rim light
rim_light = bpy.data.objects.get("Rim_Light")
if rim_light:
    rim_light.data.energy = 2000

# Reduce sun ambient
sun = bpy.data.objects.get("Ambient_Sun")
if sun:
    sun.data.energy = 1.0

# Make sure emission is still strong
mat_names = ["Fire", "FireInner", "BalrogFire", "BalrogEye", "Glow"]
for mat_name in mat_names:
    mat = bpy.data.materials.get(mat_name)
    if mat:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Emission Strength"].default_value = 30.0

# Reposition camera to frame the scene properly
camera = bpy.data.objects.get("Main_Camera")
if camera:
    camera.location = (-5, 4, 3)
    target = Vector((1.5, 0, 1.5))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    camera.data.lens = 40

# Add more detail - stone texture on bridge with displacement-like bumps
# Add small rocks on the bridge surface
mat_stone = bpy.data.materials.get("Stone")
mat_stone_dark = bpy.data.materials.get("StoneDark")

if mat_stone and mat_stone_dark:
    for i in range(40):
        x = random.uniform(-5.5, 5.5)
        y = random.uniform(-0.7, 0.7)
        z = 0.21
        size = random.uniform(0.02, 0.08)
        bpy.ops.mesh.primitive_ico_sphere_add(radius=size, location=(x, y, z))
        rock = bpy.context.object
        rock.name = f"Bridge_Rock_{i}"
        rock.scale = (1, 1, 0.5)
        rock.data.materials.append(mat_stone_dark if random.random() > 0.5 else mat_stone)
        bpy.ops.object.transform_apply(scale=True)

# Add carved Dwarven runes along the bridge sides
mat_glow = bpy.data.materials.get("Glow")
if mat_glow:
    for i in range(10):
        x = -5 + i * 1.0
        # Left side
        bpy.ops.mesh.primitive_plane_add(size=0.1, location=(x, -0.95, 0.5))
        rune_l = bpy.context.object
        rune_l.name = f"Rune_L_{i}"
        rune_l.rotation_euler = (0, math.radians(90), 0)
        rune_l.data.materials.append(mat_glow)
        
        # Right side
        bpy.ops.mesh.primitive_plane_add(size=0.1, location=(x, 0.95, 0.5))
        rune_r = bpy.context.object
        rune_r.name = f"Rune_R_{i}"
        rune_r.rotation_euler = (0, math.radians(-90), 0)
        rune_r.data.materials.append(mat_glow)

# Add more fire - a stream of fire from Balrog toward Gandalf
mat_fire = bpy.data.materials.get("Fire")
mat_fire_inner = bpy.data.materials.get("FireInner")
if mat_fire and mat_fire_inner:
    for i in range(15):
        t = i / 14.0
        x = 4.5 - 1.5 - t * 4.0  # From Balrog mouth toward Gandalf
        y = (i % 3 - 1) * 0.2
        z = 0.2 + 2.5 - t * 1.5 + random.uniform(-0.2, 0.2)
        size = 0.3 - t * 0.15
        bpy.ops.mesh.primitive_uv_sphere_add(radius=max(0.05, size), location=(x, y, z))
        fire = bpy.context.object
        fire.name = f"FireStream_{i}"
        fire.data.materials.append(mat_fire_inner if t < 0.3 else mat_fire)

# Add Balrog's whip/tentacle
mat_balrog_body = bpy.data.materials.get("BalrogBody")
if mat_balrog_body:
    bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0.03, depth=3.0, location=(4.5 - 0.5, 0.5, 0.2 + 1.0))
    tentacle = bpy.context.object
    tentacle.name = "Balrog_Tentacle"
    tentacle.rotation_euler = (math.radians(30), math.radians(-20), 0)
    tentacle.data.materials.append(mat_balrog_body)

# Add more architectural details - arch above the bridge entrance
mat_stone_pillar = bpy.data.materials.get("PillarStone")
if mat_stone_pillar:
    # Left arch
    bpy.ops.mesh.primitive_torus_add(major_radius=2.0, minor_radius=0.3, location=(-6, 0, 2.0))
    arch_l = bpy.context.object
    arch_l.name = "Bridge_Arch_L"
    arch_l.rotation_euler = (0, math.radians(90), 0)
    arch_l.data.materials.append(mat_stone_pillar)
    
    # Right arch
    bpy.ops.mesh.primitive_torus_add(major_radius=2.0, minor_radius=0.3, location=(6, 0, 2.0))
    arch_r = bpy.context.object
    arch_r.name = "Bridge_Arch_R"
    arch_r.rotation_euler = (0, math.radians(90), 0)
    arch_r.data.materials.append(mat_stone_pillar)

# Add more smoke
mat_smoke = bpy.data.materials.get("Smoke")
if mat_smoke:
    for i in range(10):
        x = 4.0 + random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        z = 4.0 + i * 0.5
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3 + i * 0.05, location=(x, y, z))
        smoke = bpy.context.object
        smoke.name = f"SmokeTop_{i}"
        smoke.data.materials.append(mat_smoke)

# Add a subtle warm point light near Gandalf to show his face
bpy.ops.object.light_add(type='POINT', location=(-1.5, 0.5, 2.0))
gandalf_light = bpy.context.object
gandalf_light.name = "Gandalf_Face_Light"
gandalf_light.data.energy = 200
gandalf_light.data.color = (1.0, 0.7, 0.4)
gandalf_light.data.shadow_soft_size = 0.5

# Add more embers floating
mat_ember = bpy.data.materials.get("FireInner")
if mat_ember:
    for i in range(25):
        x = random.uniform(-4, 5)
        y = random.uniform(-2, 2)
        z = random.uniform(0.5, 6)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.015, 0.035), location=(x, y, z))
        ember = bpy.context.object
        ember.name = f"Ember3_{i}"
        ember.data.materials.append(mat_ember)

# Add distant glowing lava in the chasm
mat_fire = bpy.data.materials.get("Fire")
if mat_fire:
    for i in range(5):
        x = random.uniform(-3, 3)
        y = random.uniform(-6, 6)
        z = -8
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
        lava = bpy.context.object
        lava.name = f"Chasm_Lava_{i}"
        lava.scale = (random.uniform(1, 3), random.uniform(1, 3), 1)
        lava.data.materials.append(mat_fire)
        bpy.ops.object.transform_apply(scale=True)

print("Fixed view look, rebalanced lighting, added fire stream, runes, arches, tentacle, lava, face light, more embers")
