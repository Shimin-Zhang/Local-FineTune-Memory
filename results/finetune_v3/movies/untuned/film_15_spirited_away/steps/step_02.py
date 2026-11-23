import bpy
import math
import random
from mathutils import Vector

# Reposition camera to see the bathhouse
camera = bpy.data.objects.get("MainCamera")
if camera:
    camera.location = (0, 100, 15)
    camera.rotation_euler = (math.radians(75), 0, 0)

# Check if bathhouse objects exist
bathhouse = bpy.data.objects.get("BathhouseMain")
if not bathhouse:
    # Something went wrong, let's rebuild
    pass

# Add more detail - torii gate at start of bridge
bpy.ops.mesh.primitive_cube_add(size=1, location=(-3, 45, 4))
gate_left = bpy.context.active_object
gate_left.name = "ToriiLeft"
gate_left.scale = (0.5, 0.5, 4)
mat_red = bpy.data.materials.new("ToriiRed")
mat_red.use_nodes = True
bsdf = mat_red.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.7, 0.05, 0.05, 1.0)
bsdf.inputs["Roughness"].default_value = 0.5
gate_left.data.materials.append(mat_red)

bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 45, 4))
gate_right = bpy.context.active_object
gate_right.name = "ToriiRight"
gate_right.scale = (0.5, 0.5, 4)
gate_right.data.materials.append(mat_red)

# Torii top beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 45, 7))
gate_top = bpy.context.active_object
gate_top.name = "ToriiTop"
gate_top.scale = (5, 0.5, 0.5)
gate_top.data.materials.append(mat_red)

# Second torii beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 45, 6))
gate_mid = bpy.context.active_object
gate_mid.name = "ToriiMid"
gate_mid.scale = (4, 0.4, 0.3)
gate_mid.data.materials.append(mat_red)

# Add more lanterns on the bathhouse facade
for i in range(4):
    x = -18 + i * 12
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(x, 21, 8))
    facade_lantern = bpy.context.active_object
    facade_lantern.name = f"FacadeLantern_{i}"
    facade_lantern.scale = (1, 1, 1.2)
    mat_fl = bpy.data.materials.new(f"FacadeLanternMat_{i}")
    mat_fl.use_nodes = True
    bsdf = mat_fl.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.4, 0.1, 1.0)
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.5, 0.15, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 6.0
    facade_lantern.data.materials.append(mat_fl)

# Add hanging lanterns under the eaves
for i in range(5):
    x = -20 + i * 10
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1, location=(x, 22, 14))
    hanger = bpy.context.active_object
    hanger.name = f"LanternHanger_{i}"
    hanger.data.materials.append(mat_red)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x, 22, 13))
    hang_lantern = bpy.context.active_object
    hang_lantern.name = f"HangingLantern_{i}"
    hang_lantern.scale = (1, 1, 1.3)
    mat_hl = bpy.data.materials.new(f"HangingLanternMat_{i}")
    mat_hl.use_nodes = True
    bsdf = mat_hl.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.35, 0.08, 1.0)
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.45, 0.1, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 7.0
    hang_lantern.data.materials.append(mat_hl)

# Add more steam - larger and more visible
for i in range(15):
    x = random.uniform(-15, 15)
    y = random.uniform(18, 30)
    z = random.uniform(15, 35)
    size = random.uniform(2, 4)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=(x, y, z))
    steam = bpy.context.active_object
    steam.name = f"SteamLarge_{i}"
    mat_steam = bpy.data.materials.new(f"SteamMatLarge_{i}")
    mat_steam.use_nodes = True
    mat_steam.blend_method = 'BLEND'
    bsdf = mat_steam.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.9, 1.0)
    bsdf.inputs["Alpha"].default_value = 0.1
    bsdf.inputs["Roughness"].default_value = 1.0
    steam.data.materials.append(mat_steam)

# Add water reflection plane with slight transparency
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 50, -1.5))
water_reflect = bpy.context.active_object
water_reflect.name = "WaterReflection"
mat_wr = bpy.data.materials.new("WaterReflectMat")
mat_wr.use_nodes = True
mat_wr.blend_method = 'BLEND'
bsdf = mat_wr.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.05, 0.1, 0.2, 1.0)
bsdf.inputs["Alpha"].default_value = 0.7
bsdf.inputs["Roughness"].default_value = 0.05
bsdf.inputs["Metallic"].default_value = 0.5
water_reflect.data.materials.append(mat_wr)

# Add decorative elements - roof ornaments
for x in [-25, 0, 25]:
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=1.5, radius2=0.3, depth=3, location=(x, 5, 22))
    ornament = bpy.context.active_object
    ornament.name = f"RoofOrnament_{x}"
    ornament.data.materials.append(bpy.data.materials.get("GoldMat"))

# Add stone lanterns near the bridge
for x in [-8, 8]:
    for y in [42, 55, 68]:
        # Base
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.5))
        sl_base = bpy.context.active_object
        sl_base.name = f"StoneLanternBase_{x}_{y}"
        sl_base.scale = (1, 1, 0.5)
        mat_stone = bpy.data.materials.new("StoneMat")
        mat_stone.use_nodes = True
        bsdf = mat_stone.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.5, 0.45, 0.4, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
        sl_base.data.materials.append(mat_stone)
        
        # Pillar
        bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=2, location=(x, y, 1.5))
        sl_pillar = bpy.context.active_object
        sl_pillar.name = f"StoneLanternPillar_{x}_{y}"
        sl_pillar.data.materials.append(mat_stone)
        
        # Light box
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 3))
        sl_box = bpy.context.active_object
        sl_box.name = f"StoneLanternBox_{x}_{y}"
        sl_box.scale = (0.8, 0.8, 0.8)
        sl_box.data.materials.append(mat_stone)
        
        # Inner glow
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 3))
        sl_glow = bpy.context.active_object
        sl_glow.name = f"StoneLanternGlow_{x}_{y}"
        sl_glow.scale = (0.6, 0.6, 0.6)
        mat_slglow = bpy.data.materials.new(f"StoneLanternGlowMat_{x}_{y}")
        mat_slglow.use_nodes = True
        bsdf = mat_slglow.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (1.0, 0.7, 0.3, 1.0)
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.6, 0.2, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 4.0
        sl_glow.data.materials.append(mat_slglow)
        
        # Cap
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1, radius2=0.3, depth=1, location=(x, y, 3.8))
        sl_cap = bpy.context.active_object
        sl_cap.name = f"StoneLanternCap_{x}_{y}"
        sl_cap.rotation_euler = (0, 0, math.radians(45))
        sl_cap.data.materials.append(mat_stone)

# Add more bridge detail - curved top railings
for side in [-1, 1]:
    for i in range(12):
        y = 42 + i * 6
        # Curved top piece
        bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.1, location=(side * 4, y, 3))
        curve_rail = bpy.context.active_object
        curve_rail.name = f"BridgeCurveRail_{side}_{i}"
        curve_rail.rotation_euler = (math.radians(90), 0, 0)
        curve_rail.data.materials.append(bpy.data.materials.get("RedBridgeMat"))

# Add fish or koi in the water (simple shapes)
for i in range(5):
    x = random.uniform(-30, 30)
    y = random.uniform(30, 80)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x, y, -1))
    koi = bpy.context.active_object
    koi.name = f"Koi_{i}"
    koi.scale = (2, 0.8, 0.5)
    mat_koi = bpy.data.materials.new(f"KoiMat_{i}")
    mat_koi.use_nodes = True
    bsdf = mat_koi.node_tree.nodes.get("Principled BSDF")
    if i % 2 == 0:
        bsdf.inputs["Base Color"].default_value = (1.0, 0.5, 0.2, 1.0)
    else:
        bsdf.inputs["Base Color"].default_value = (1.0, 0.9, 0.8, 1.0)
    koi.data.materials.append(mat_koi)

# Add a large sign/plate above the entrance
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 21, 10))
sign = bpy.context.active_object
sign.name = "BathhouseSign"
sign.scale = (8, 0.5, 2)
mat_sign = bpy.data.materials.new("SignMat")
mat_sign.use_nodes = True
bsdf = mat_sign.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.1, 0.05, 0.02, 1.0)
bsdf.inputs["Roughness"].default_value = 0.5
sign.data.materials.append(mat_sign)

# Gold text on sign (emissive)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 21.3, 10))
sign_text = bpy.context.active_object
sign_text.name = "SignText"
sign_text.scale = (7, 0.3, 1.5)
mat_signtext = bpy.data.materials.new("SignTextMat")
mat_signtext.use_nodes = True
bsdf = mat_signtext.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (1.0, 0.8, 0.3, 1.0)
bsdf.inputs["Emission Color"].default_value = (1.0, 0.7, 0.2, 1.0)
bsdf.inputs["Emission Strength"].default_value = 2.0
sign_text.data.materials.append(mat_signtext)

# Add ambient light to brighten the scene slightly
bpy.ops.object.light_add(type='AREA', location=(0, 50, 50))
ambient = bpy.context.active_object
ambient.name = "AmbientLight"
ambient.data.energy = 100
ambient.data.color = (0.3, 0.4, 0.6)
ambient.data.size = 50
ambient.rotation_euler = (math.radians(90), 0, 0)

# Add more structural details - bracket supports under eaves
for x in [-40, -20, 0, 20, 40]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 21, 16))
    bracket = bpy.context.active_object
    bracket.name = f"EaveBracket_{x}"
    bracket.scale = (1, 0.5, 1.5)
    bracket.data.materials.append(bpy.data.materials.get("WoodBathMat"))

# Add a small boat near the bridge
bpy.ops.mesh.primitive_uv_sphere_add(radius=3, location=(15, 50, -0.5))
boat = bpy.context.active_object
boat.name = "Boat"
boat.scale = (1.5, 3, 0.5)
mat_boat = bpy.data.materials.new("BoatMat")
mat_boat.use_nodes = True
bsdf = mat_boat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.2, 0.1, 0.05, 1.0)
bsdf.inputs["Roughness"].default_value = 0.7
boat.data.materials.append(mat_boat)

# Lantern on the boat
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.5, location=(15, 50, 0.5))
boat_lpost = bpy.context.active_object
boat_lpost.name = "BoatLanternPost"
boat_lpost.data.materials.append(bpy.data.materials.get("WoodBathMat"))

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(15, 50, 1.5))
boat_lantern = bpy.context.active_object
boat_lantern.name = "BoatLantern"
boat_lantern.scale = (1, 1, 1.2)
mat_bl = bpy.data.materials.new("BoatLanternMat")
mat_bl.use_nodes = True
bsdf = mat_bl.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (1.0, 0.4, 0.1, 1.0)
bsdf.inputs["Emission Color"].default_value = (1.0, 0.5, 0.15, 1.0)
bsdf.inputs["Emission Strength"].default_value = 5.0
boat_lantern.data.materials.append(mat_bl)
