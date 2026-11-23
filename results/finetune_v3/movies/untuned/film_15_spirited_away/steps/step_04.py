import bpy
import math
import random
from mathutils import Vector

# The camera is too close and pointing at the wrong things. 
# The bathhouse is at y=5, bridge goes from y=40 to y=120.
# Camera should be positioned to see the whole scene from a good angle.

# Fix camera position - pull back and angle to see bathhouse + bridge
camera = bpy.data.objects.get("MainCamera")
if camera:
    camera.location = (0, 150, 25)
    camera.rotation_euler = (math.radians(80), 0, 0)
    camera.data.lens = 50

# Remove the broken glow lights that caused the error (they may have been partially created)
# Actually the error was on line setting distance, so the lights were created but without distance set
# Let's just make sure they work - point lights in Blender 5.x don't have 'distance' in the same way
# Actually in newer Blender, shadow_soft_size is the right property, distance was removed or renamed

# Let's clean up any problematic lights and add proper ones
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT' and "LanternGlow" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

# Recreate lantern glow lights properly
lantern_positions = []
for obj in bpy.data.objects:
    if "Lantern" in obj.name and obj.type == 'MESH' and "Post" not in obj.name and "Hanger" not in obj.name:
        lantern_positions.append(obj.location.copy())

for i, pos in enumerate(lantern_positions[:8]):
    bpy.ops.object.light_add(type='POINT', location=pos)
    glow = bpy.context.active_object
    glow.name = f"LanternGlow_{i}"
    glow.data.energy = 100
    glow.data.color = (1.0, 0.5, 0.1)
    glow.data.shadow_soft_size = 3

# Add more architectural detail to the bathhouse
# Balcony on upper floor
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 22, 14))
balcony = bpy.context.active_object
balcony.name = "UpperBalcony"
balcony.scale = (40, 3, 0.5)
mat_wood = bpy.data.materials.get("WoodBathMat")
if not mat_wood:
    mat_wood = bpy.data.materials.new("WoodBathMat")
    mat_wood.use_nodes = True
    bsdf = mat_wood.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.35, 0.18, 0.08, 1.0)
balcony.data.materials.append(mat_wood)

# Balcony railing
for x in range(-20, 21, 4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 23.5, 15.5))
    rail_post = bpy.context.active_object
    rail_post.name = f"BalconyRail_{x}"
    rail_post.scale = (0.3, 0.3, 1.5)
    rail_post.data.materials.append(mat_wood)

# Balcony top rail
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 23.5, 16.5))
balcony_rail = bpy.context.active_object
balcony_rail.name = "BalconyTopRail"
balcony_rail.scale = (40, 0.3, 0.3)
balcony_rail.data.materials.append(mat_wood)

# Add more windows on the sides
for side in [-1, 1]:
    for i in range(4):
        y = -10 + i * 10
        bpy.ops.mesh.primitive_cube_add(size=1, location=(side * 50.5, y + 5, 5))
        side_win = bpy.context.active_object
        side_win.name = f"SideWindow_{side}_{i}"
        side_win.scale = (0.5, 2, 2.5)
        mat_sw = bpy.data.materials.new(f"SideWindowMat_{side}_{i}")
        mat_sw.use_nodes = True
        bsdf = mat_sw.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (1.0, 0.6, 0.2, 1.0)
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.5, 0.15, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 4.0
        side_win.data.materials.append(mat_sw)

# Add a large torii-style gate at the bridge entrance (bigger)
# Remove old small torii
for name in ["ToriiLeft", "ToriiRight", "ToriiTop", "ToriiMid"]:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

# New larger torii gate
mat_torii = bpy.data.materials.get("ToriiRed")
if not mat_torii:
    mat_torii = bpy.data.materials.new("ToriiRed")
    mat_torii.use_nodes = True
    bsdf = mat_torii.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.7, 0.05, 0.05, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5

# Left pillar
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=10, location=(-5, 40, 5))
t_left = bpy.context.active_object
t_left.name = "ToriiLeftPillar"
t_left.data.materials.append(mat_torii)

# Right pillar
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=10, location=(5, 40, 5))
t_right = bpy.context.active_object
t_right.name = "ToriiRightPillar"
t_right.data.materials.append(mat_torii)

# Top beam (kasagi) - curved
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 40, 10.5))
t_kasagi = bpy.context.active_object
t_kasagi.name = "ToriiKasagi"
t_kasagi.scale = (8, 1.5, 1)
t_kasagi.data.materials.append(mat_torii)

# Second beam (nuki)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 40, 8))
t_nuki = bpy.context.active_object
t_nuki.name = "ToriiNuki"
t_nuki.scale = (6, 1, 0.8)
t_nuki.data.materials.append(mat_torii)

# Center strut
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 40, 9.2))
t_shimaki = bpy.context.active_object
t_shimaki.name = "ToriiShimaki"
t_shimaki.scale = (0.5, 0.8, 1.5)
t_shimaki.data.materials.append(mat_torii)

# Add lanterns on the torii gate
for x in [-5, 5]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(x, 40, 6))
    t_lantern = bpy.context.active_object
    t_lantern.name = f"ToriiLantern_{x}"
    t_lantern.scale = (1, 1, 1.3)
    mat_tl = bpy.data.materials.new(f"ToriiLanternMat_{x}")
    mat_tl.use_nodes = True
    bsdf = mat_tl.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.4, 0.1, 1.0)
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.5, 0.15, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 8.0
    t_lantern.data.materials.append(mat_tl)

# Add a reflection of the bathhouse in the water (simple mirrored geometry)
# Create a simple reflection plane with emission
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 20, -1.9))
reflection = bpy.context.active_object
reflection.name = "BathhouseReflection"
mat_refl = bpy.data.materials.new("ReflectionMat")
mat_refl.use_nodes = True
mat_refl.blend_method = 'BLEND'
bsdf = mat_refl.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.05, 0.08, 0.15, 1.0)
bsdf.inputs["Alpha"].default_value = 0.5
bsdf.inputs["Roughness"].default_value = 0.0
bsdf.inputs["Metallic"].default_value = 0.8
reflection.data.materials.append(mat_refl)

# Add warm light streaks on the water
for i in range(5):
    x = -20 + i * 10
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 30, -1.7))
    streak = bpy.context.active_object
    streak.name = f"WaterStreak_{i}"
    streak.scale = (2, 30, 1)
    mat_streak = bpy.data.materials.new(f"WaterStreakMat_{i}")
    mat_streak.use_nodes = True
    mat_streak.blend_method = 'BLEND'
    bsdf = mat_streak.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.5, 0.2, 1.0)
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.4, 0.1, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 1.0
    bsdf.inputs["Alpha"].default_value = 0.3
    streak.data.materials.append(mat_streak)

# Add more steam rising from the bathhouse - use a particle-like arrangement
for i in range(25):
    t = i / 25.0
    x = random.uniform(-15, 15) + math.sin(t * 10) * 5
    y = 20 + t * 15
    z = 15 + t * 25 + random.uniform(-2, 2)
    size = 2 + t * 3
    bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=(x, y, z))
    steam = bpy.context.active_object
    steam.name = f"SteamRising_{i}"
    mat_steam = bpy.data.materials.new(f"SteamRisingMat_{i}")
    mat_steam.use_nodes = True
    mat_steam.blend_method = 'BLEND'
    bsdf = mat_steam.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.9, 1.0)
    bsdf.inputs["Alpha"].default_value = 0.15 * (1 - t * 0.5)
    bsdf.inputs["Roughness"].default_value = 1.0
    steam.data.materials.append(mat_steam)

# Add a small dock/pier next to the bridge
bpy.ops.mesh.primitive_cube_add(size=1, location=(20, 50, 0))
dock = bpy.context.active_object
dock.name = "Dock"
dock.scale = (10, 15, 0.5)
mat_dock = bpy.data.materials.get("WoodDarkMat")
if not mat_dock:
    mat_dock = bpy.data.materials.new("WoodDarkMat")
    mat_dock.use_nodes = True
    bsdf = mat_dock.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.15, 0.08, 0.04, 1.0)
dock.data.materials.append(mat_dock)

# Dock posts
for x in [15, 25]:
    for y in [45, 55, 65]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=2, location=(x, y, -0.5))
        dpost = bpy.context.active_object
        dpost.name = f"DockPost_{x}_{y}"
        dpost.data.materials.append(mat_dock)

# Add a hanging sign on the bathhouse
bpy.ops.mesh.primitive_cube_add(size=1, location=(10, 21, 12))
hanging_sign = bpy.context.active_object
hanging_sign.name = "HangingSign"
hanging_sign.scale = (3, 0.3, 4)
mat_hs = bpy.data.materials.new("HangingSignMat")
mat_hs.use_nodes = True
bsdf = mat_hs.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.1, 0.05, 0.02, 1.0)
hanging_sign.data.materials.append(mat_hs)

# Sign glow
bpy.ops.mesh.primitive_cube_add(size=1, location=(10, 21.2, 12))
hanging_sign_glow = bpy.context.active_object
hanging_sign_glow.name = "HangingSignGlow"
hanging_sign_glow.scale = (2.5, 0.2, 3.5)
mat_hsg = bpy.data.materials.new("HangingSignGlowMat")
mat_hsg.use_nodes = True
bsdf = mat_hsg.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (1.0, 0.7, 0.3, 1.0)
bsdf.inputs["Emission Color"].default_value = (1.0, 0.6, 0.2, 1.0)
bsdf.inputs["Emission Strength"].default_value = 3.0
hanging_sign_glow.data.materials.append(mat_hsg)

# Add rope for hanging sign
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2, location=(10, 21, 14))
rope = bpy.context.active_object
rope.name = "SignRope"
mat_rope = bpy.data.materials.new("RopeMat")
mat_rope.use_nodes = True
bsdf = mat_rope.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.3, 0.2, 0.1, 1.0)
rope.data.materials.append(mat_rope)

# Final camera adjustment to frame everything nicely
if camera:
    camera.location = (0, 160, 30)
    camera.rotation_euler = (math.radians(78), 0, 0)
    camera.data.lens = 45
