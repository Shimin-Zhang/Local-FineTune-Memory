import bpy
import math
import random
from mathutils import Vector

# Get scene
scene = bpy.context.scene

# Remove existing lights and reposition them better
for obj in list(scene.objects):
    if obj.type == 'LIGHT':
        scene.objects.unlink(obj)
        obj.data.free()

# Create new materials for better visibility
def make_material(name, color, roughness=0.5, metallic=0.0, emission=0.0, emission_color=None):
    if emission_color is None:
        emission_color = color
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission > 0:
        bsdf.inputs['Emission Color'].default_value = (*emission_color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs[0], out.inputs[0])
    return mat

# Better materials
mat_asphalt_bright = make_material("AsphaltBright", (0.08, 0.08, 0.09), roughness=0.85)
mat_concrete_bright = make_material("ConcreteBright", (0.2, 0.2, 0.19), roughness=0.75)
mat_metal_bright = make_material("MetalBright", (0.4, 0.4, 0.42), roughness=0.35, metallic=0.7)
mat_dark_metal_bright = make_material("DarkMetalBright", (0.15, 0.15, 0.17), roughness=0.45, metallic=0.6)
mat_glass_bright = make_material("GlassBright", (0.7, 0.8, 0.9), roughness=0.05, metallic=0.0)
mat_coat_dark_bright = make_material("CoatDarkBright", (0.12, 0.12, 0.14), roughness=0.55)
mat_coat_light_bright = make_material("CoatLightBright", (0.3, 0.28, 0.24), roughness=0.55)
mat_hat_bright = make_material("HatBright", (0.15, 0.12, 0.09), roughness=0.45)
mat_skin_bright = make_material("SkinBright", (0.6, 0.45, 0.35), roughness=0.35)
mat_car_body_bright = make_material("CarBodyBright", (0.05, 0.05, 0.06), roughness=0.25, metallic=0.5)
mat_car_glass_bright = make_material("CarGlassBright", (0.3, 0.35, 0.4), roughness=0.08)
mat_hangar_wall_bright = make_material("HangarWallBright", (0.18, 0.18, 0.2), roughness=0.55, metallic=0.25)
mat_hangar_door_bright = make_material("HangarDoorBright", (0.22, 0.22, 0.24), roughness=0.45, metallic=0.35)
mat_light_warm_bright = make_material("LightWarmBright", (1.0, 0.85, 0.5), roughness=0.4, emission=8.0, emission_color=(1.0, 0.85, 0.5))
mat_light_cold_bright = make_material("LightColdBright", (0.7, 0.8, 1.0), roughness=0.4, emission=5.0, emission_color=(0.7, 0.8, 1.0))
mat_tire_bright = make_material("TireBright", (0.03, 0.03, 0.03), roughness=0.85)
mat_prop_bright = make_material("PropellerBright", (0.15, 0.15, 0.15), roughness=0.35, metallic=0.4)
mat_fuselage_bright = make_material("FuselageBright", (0.35, 0.35, 0.38), roughness=0.25, metallic=0.4)
mat_wing_bright = make_material("WingBright", (0.3, 0.3, 0.32), roughness=0.25, metallic=0.4)
mat_engine_bright = make_material("EngineBright", (0.2, 0.2, 0.2), roughness=0.35, metallic=0.6)
mat_wood_bright = make_material("WoodBright", (0.4, 0.3, 0.15), roughness=0.65)

# Update existing objects with brighter materials
for obj in scene.objects:
    if obj.name.startswith("Ground"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_asphalt_bright)
    elif obj.name.startswith("Marking"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_concrete_bright)
    elif obj.name.startswith("HangarBody") or obj.name.startswith("HangarRoof"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_hangar_wall_bright)
    elif obj.name.startswith("HangarDoor") or obj.name.startswith("DoorFrame"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_hangar_door_bright)
    elif obj.name.startswith("HangarWin"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_glass_bright)
    elif obj.name.startswith("Fuselage") or obj.name.startswith("Nose") or obj.name.startswith("Tail") or obj.name.startswith("VStab") or obj.name.startswith("HStab"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_fuselage_bright)
    elif obj.name.startswith("Wing"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_wing_bright)
    elif obj.name.startswith("Engine"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_engine_bright)
    elif obj.name.startswith("PropHub") or obj.name.startswith("Blade"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_prop_bright)
    elif obj.name.startswith("Gear") or obj.name.startswith("Wheel") or obj.name.startswith("TailWheel"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_tire_bright)
    elif obj.name.startswith("CockpitWin") or obj.name.startswith("PaxWin"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_glass_bright)
    elif obj.name.startswith("CarBody") or obj.name.startswith("CarRoof") or obj.name.startswith("Hood") or obj.name.startswith("Trunk"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_car_body_bright)
    elif obj.name.startswith("CarWin") or obj.name.startswith("Windshield") or obj.name.startswith("RearWindow"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_car_glass_bright)
    elif obj.name.startswith("CarWheel"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_tire_bright)
    elif obj.name.startswith("Hubcap"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_metal_bright)
    elif obj.name.startswith("Headlight"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_light_warm_bright)
    elif obj.name.startswith("Taillight"):
        obj.data.materials.clear()
        obj.data.materials.append(make_material(f"TaillightBright_{obj.name}", (1.0, 0.3, 0.2), roughness=0.4, emission=3.0, emission_color=(1.0, 0.3, 0.2)))
    elif obj.name.startswith("Rick"):
        if "Head" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_skin_bright)
        elif "Hat" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_hat_bright)
        else:
            obj.data.materials.clear()
            obj.data.materials.append(mat_coat_dark_bright)
    elif obj.name.startswith("Ilsa"):
        if "Head" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_skin_bright)
        elif "Hat" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_hat_bright)
        else:
            obj.data.materials.clear()
            obj.data.materials.append(mat_coat_light_bright)
    elif obj.name.startswith("LightPole"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_dark_metal_bright)
    elif obj.name.startswith("LightFixture"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_light_warm_bright)
    elif obj.name.startswith("Crate"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_wood_bright)
    elif obj.name.startswith("Drum"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_dark_metal_bright)
    elif obj.name.startswith("EdgeLight"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_light_cold_bright)
    elif obj.name.startswith("SignPole"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_dark_metal_bright)
    elif obj.name.startswith("SignBoard"):
        obj.data.materials.clear()
        obj.data.materials.append(mat_concrete_bright)

# Add new lights - much brighter
# Main airfield floodlights
flood_positions = [
    (-12, 8, 7),
    (12, 8, 7),
    (-12, -8, 7),
    (12, -8, 7),
    (0, 12, 8),
    (0, -12, 8)
]

for i, pos in enumerate(flood_positions):
    light_data = bpy.data.lights.new(f"FloodLight{i}", type='POINT')
    light_data.energy = 2000
    light_data.color = (1.0, 0.85, 0.5)
    light_data.shadow_soft_size = 1.0
    light_obj = bpy.data.objects.new(f"FloodLightObj{i}", light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = pos

# Hangar interior light
hangar_light_data = bpy.data.lights.new("HangarInteriorLight", type='POINT')
hangar_light_data.energy = 1500
hangar_light_data.color = (0.8, 0.85, 1.0)
hangar_light_data.shadow_soft_size = 2.0
hangar_light_obj = bpy.data.objects.new("HangarInteriorLightObj", hangar_light_data)
scene.collection.objects.link(hangar_light_obj)
hangar_light_obj.location = (15, 17, 5)

# Car headlights
for side in [-1, 1]:
    hl_data = bpy.data.lights.new(f"CarHeadlight{side}", type='SPOT')
    hl_data.energy = 500
    hl_data.color = (1.0, 0.9, 0.5)
    hl_data.spot_size = math.radians(40)
    hl_data.shadow_soft_size = 0.3
    hl_obj = bpy.data.objects.new(f"CarHeadlightObj{side}", hl_data)
    scene.collection.objects.link(hl_obj)
    hl_obj.location = (-7.8, -2 + side * 0.6, 0.5)
    hl_obj.rotation_euler = (0, math.radians(-90), 0)

# Moonlight - stronger
moon_data = bpy.data.lights.new("Moonlight", type='SUN')
moon_data.energy = 1.5
moon_data.color = (0.6, 0.7, 1.0)
moon_data.shadow_soft_size = 2.0
moon_obj = bpy.data.objects.new("MoonlightObj", moon_data)
scene.collection.objects.link(moon_obj)
moon_obj.rotation_euler = (math.radians(50), math.radians(15), 0)

# Add a key light to illuminate the figures
key_light_data = bpy.data.lights.new("KeyLight", type='AREA')
key_light_data.energy = 300
key_light_data.color = (0.9, 0.85, 0.7)
key_light_data.size = 3
key_light_obj = bpy.data.objects.new("KeyLightObj", key_light_data)
scene.collection.objects.link(key_light_obj)
key_light_obj.location = (3, -5, 5)
key_light_obj.rotation_euler = (math.radians(60), 0, math.radians(30))

# Fill light
fill_light_data = bpy.data.lights.new("FillLight", type='AREA')
fill_light_data.energy = 150
fill_light_data.color = (0.7, 0.75, 0.85)
fill_light_data.size = 4
fill_light_obj = bpy.data.objects.new("FillLightObj", fill_light_data)
scene.collection.objects.link(fill_light_obj)
fill_light_obj.location = (-3, -8, 4)
fill_light_obj.rotation_euler = (math.radians(70), 0, math.radians(-20))

# Rim light for the plane
rim_light_data = bpy.data.lights.new("RimLight", type='AREA')
rim_light_data.energy = 200
rim_light_data.color = (0.8, 0.85, 1.0)
rim_light_data.size = 2
rim_light_obj = bpy.data.objects.new("RimLightObj", rim_light_data)
scene.collection.objects.link(rim_light_obj)
rim_light_obj.location = (8, 8, 6)
rim_light_obj.rotation_euler = (math.radians(45), math.radians(30), 0)

# Adjust camera for better framing
cam = scene.camera
if cam:
    cam.location = (8, -12, 3.5)
    cam.rotation_euler = (math.radians(85), 0, math.radians(15))
    cam.data.lens = 35
else:
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (8, -12, 3.5)
    cam.rotation_euler = (math.radians(85), 0, math.radians(15))
    cam.data.lens = 35
    scene.camera = cam

# Add more detail - additional objects
# Runway centerline
for i in range(8):
    x = -25 + i * 7
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0.01))
    line = bpy.context.active_object
    line.scale = (2, 0.15, 0.01)
    line.name = f"CenterLine{i}"
    line.data.materials.append(mat_concrete_bright)

# Taxiway markings
for i in range(5):
    x = -15 + i * 8
    y = 5
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.01))
    mark = bpy.context.active_object
    mark.scale = (1.5, 0.1, 0.01)
    mark.name = f"TaxiMark{i}"
    mark.data.materials.append(mat_concrete_bright)

# Add a control tower in the distance
tower_x = -30
tower_y = 25
bpy.ops.mesh.primitive_cylinder_add(radius=2, depth=15, location=(tower_x, tower_y, 7.5))
tower_body = bpy.context.active_object
tower_body.name = "ControlTower"
tower_body.data.materials.append(mat_hangar_wall_bright)

# Tower top
bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=3, location=(tower_x, tower_y, 16.5))
tower_top = bpy.context.active_object
tower_top.name = "ControlTowerTop"
tower_top.data.materials.append(mat_hangar_wall_bright)

# Tower windows
for i in range(4):
    angle = i * math.pi / 2
    wx = tower_x + math.sin(angle) * 2.5
    wy = tower_y + math.cos(angle) * 2.5
    bpy.ops.mesh.primitive_cube_add(size=1, location=(wx, wy, 16.5))
    win = bpy.context.active_object
    win.scale = (0.5, 0.1, 1.5)
    win.rotation_euler = (0, 0, angle)
    win.name = f"TowerWin{i}"
    win.data.materials.append(mat_glass_bright)

# Tower light
tower_light_data = bpy.data.lights.new("TowerLight", type='POINT')
tower_light_data.energy = 500
tower_light_data.color = (1.0, 0.2, 0.2)
tower_light_obj = bpy.data.objects.new("TowerLightObj", tower_light_data)
scene.collection.objects.link(tower_light_obj)
tower_light_obj.location = (tower_x, tower_y, 18)

# Add more crates and equipment near hangar
for i in range(5):
    cx = 5 + i * 1.5
    cy = 12
    crate = bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, 0.5))
    crate = bpy.context.active_object
    crate.scale = (1, 1, 1)
    crate.name = f"ExtraCrate{i}"
    crate.data.materials.append(mat_wood_bright)

# Add a ladder leaning against hangar
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=4, location=(10, 14, 2), rotation=(0, math.radians(75), 0))
ladder = bpy.context.active_object
ladder.name = "Ladder"
ladder.data.materials.append(mat_metal_bright)

# Add some barrels
for i in range(3):
    bx = 20 + i * 1.2
    by = 10
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.2, location=(bx, by, 0.6))
    barrel = bpy.context.active_object
    barrel.name = f"Barrel{i}"
    barrel.data.materials.append(mat_dark_metal_bright)

# Add a bench
bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, -5, 0.4))
bench = bpy.context.active_object
bench.scale = (2, 0.5, 0.8)
bench.name = "Bench"
bench.data.materials.append(mat_wood_bright)

# Add a trash can
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.8, location=(-9, -5, 0.4))
trash = bpy.context.active_object
trash.name = "TrashCan"
trash.data.materials.append(mat_dark_metal_bright)

# Add more fog - larger, more diffuse
for i in range(12):
    fx = random.uniform(-25, 25)
    fy = random.uniform(-20, 20)
    fz = random.uniform(0.5, 4)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, fy, fz))
    fog_patch = bpy.context.active_object
    fog_patch.scale = (random.uniform(4, 10), random.uniform(4, 10), random.uniform(1, 3))
    fog_patch.name = f"FogPatch{i}"
    fog_mat = bpy.data.materials.new(f"FogMat{i}")
    fog_mat.use_nodes = True
    fnodes = fog_mat.node_tree.nodes
    flinks = fog_mat.node_tree.links
    fnodes.clear()
    fvol = fnodes.new('ShaderNodeVolumePrincipled')
    fvol.inputs['Color'].default_value = (0.06, 0.07, 0.09, 1.0)
    fvol.inputs['Density'].default_value = random.uniform(0.03, 0.1)
    fvol.inputs['Anisotropy'].default_value = 0.2
    fout = fnodes.new('ShaderNodeOutputMaterial')
    flinks.new(fvol.outputs[0], fout.inputs['Volume'])
    fog_patch.data.materials.append(fog_mat)

# Add distant city lights
for i in range(15):
    lx = random.uniform(-50, 50)
    ly = random.uniform(35, 50)
    lz = random.uniform(1, 5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(lx, ly, lz))
    city_light = bpy.context.active_object
    city_light.name = f"CityLight{i}"
    city_light.data.materials.append(make_material(f"CityLightMat{i}", (1.0, 0.8, 0.4), roughness=0.5, emission=2.0, emission_color=(1.0, 0.8, 0.4)))

# Update render settings
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.cycles.volume_bounces = 3
scene.cycles.volume_step_rate = 0.5
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 4
scene.cycles.transparent_max_bounces = 8

# Set film exposure
scene.view_settings.exposure = 1.5
scene.view_settings.look = 'AgX - Medium High Contrast'

print("Scene refined with better lighting and more detail!")
