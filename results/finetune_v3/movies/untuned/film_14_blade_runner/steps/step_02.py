import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set up
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

# Materials
def make_material(name, base_color, metallic=0.0, roughness=0.5, emission=0.0, emission_color=(1,1,1,1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission > 0:
        bsdf.inputs['Emission Color'].default_value = emission_color
        bsdf.inputs['Emission Strength'].default_value = emission
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

mat_road = make_material("Road", (0.05, 0.05, 0.06, 1), 0.1, 0.9)
mat_building_dark = make_material("Building_Dark", (0.08, 0.08, 0.10, 1), 0.2, 0.7)
mat_building_mid = make_material("Building_Mid", (0.12, 0.10, 0.12, 1), 0.3, 0.6)
mat_building_light = make_material("Building_Light", (0.18, 0.15, 0.15, 1), 0.2, 0.5)
mat_neon_pink = make_material("Neon_Pink", (1, 0.1, 0.3, 1), 0.0, 0.3, 5.0, (1, 0.1, 0.3, 1))
mat_neon_cyan = make_material("Neon_Cyan", (0.1, 0.8, 1, 1), 0.0, 0.3, 5.0, (0.1, 0.8, 1, 1))
mat_neon_yellow = make_material("Neon_Yellow", (1, 0.9, 0.1, 1), 0.0, 0.3, 4.0, (1, 0.9, 0.1, 1))
mat_neon_green = make_material("Neon_Green", (0.1, 1, 0.3, 1), 0.0, 0.3, 4.0, (0.1, 1, 0.3, 1))
mat_neon_purple = make_material("Neon_Purple", (0.6, 0.1, 1, 1), 0.0, 0.3, 4.0, (0.6, 0.1, 1, 1))
mat_neon_red = make_material("Neon_Red", (1, 0.1, 0.1, 1), 0.0, 0.3, 4.0, (1, 0.1, 0.1, 1))
mat_screen = make_material("Screen", (0.1, 0.1, 0.15, 1), 0.0, 0.2, 2.0, (0.2, 0.4, 0.8, 1))
mat_screen2 = make_material("Screen2", (0.1, 0.1, 0.15, 1), 0.0, 0.2, 2.0, (0.8, 0.2, 0.4, 1))
mat_wet_road = make_material("Wet_Road", (0.03, 0.03, 0.04, 1), 0.8, 0.1)
mat_umbrella = make_material("Umbrella", (0.1, 0.1, 0.15, 1), 0.0, 0.8)
mat_umbrella2 = make_material("Umbrella2", (0.15, 0.05, 0.1, 1), 0.0, 0.8)
mat_umbrella3 = make_material("Umbrella3", (0.05, 0.1, 0.15, 1), 0.0, 0.8)
mat_person = make_material("Person", (0.08, 0.08, 0.1, 1), 0.0, 0.7)
mat_person2 = make_material("Person2", (0.1, 0.08, 0.08, 1), 0.0, 0.7)
mat_car_body = make_material("Car_Body", (0.05, 0.05, 0.08, 1), 0.8, 0.3)
mat_car_glass = make_material("Car_Glass", (0.1, 0.15, 0.2, 1), 0.5, 0.1)
mat_car_light = make_material("Car_Light", (1, 0.1, 0.1, 1), 0.0, 0.3, 8.0, (1, 0.1, 0.1, 1))
mat_car_light2 = make_material("Car_Light2", (0.1, 0.3, 1, 1), 0.0, 0.3, 8.0, (0.1, 0.3, 1, 1))
mat_rain = make_material("Rain", (0.7, 0.8, 1, 1), 0.0, 0.5, 0.3, (0.7, 0.8, 1, 1))
mat_noodle = make_material("Noodle", (1, 0.8, 0.3, 1), 0.0, 0.4, 2.0, (1, 0.8, 0.3, 1))
mat_steam = make_material("Steam", (0.8, 0.8, 0.9, 1), 0.0, 0.9, 0.5, (0.8, 0.8, 0.9, 1))
mat_concrete = make_material("Concrete", (0.15, 0.15, 0.16, 1), 0.1, 0.8)
mat_metal = make_material("Metal", (0.3, 0.3, 0.35, 1), 0.9, 0.3)
mat_window = make_material("Window", (0.2, 0.3, 0.4, 1), 0.0, 0.2, 1.5, (0.3, 0.5, 0.7, 1))
mat_window_dim = make_material("Window_Dim", (0.1, 0.1, 0.15, 1), 0.0, 0.3, 0.3, (0.2, 0.3, 0.4, 1))
mat_sign_bg = make_material("Sign_BG", (0.02, 0.02, 0.03, 1), 0.1, 0.5)

# ===================== ROAD =====================
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
road = bpy.context.active_object
road.scale = (20, 1, 100)
road.data.materials.append(mat_wet_road)

# Road markings
for z in range(-90, 100, 15):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.01, z))
    marking = bpy.context.active_object
    marking.scale = (0.3, 1, 4)
    marking.data.materials.append(mat_neon_yellow)

# ===================== BUILDINGS (simplified, no individual windows) =====================
def create_building_simple(x, z, width, depth, height, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, height/2, z))
    bld = bpy.context.active_object
    bld.scale = (width/2, height/2, depth/2)
    bld.data.materials.append(mat)
    return bld

# Left side
create_building_simple(-15, -40, 10, 15, 60, mat_building_dark)
create_building_simple(-15, -20, 10, 15, 80, mat_building_mid)
create_building_simple(-15, 0, 10, 15, 100, mat_building_dark)
create_building_simple(-15, 20, 10, 15, 70, mat_building_light)
create_building_simple(-15, 40, 10, 15, 90, mat_building_mid)
create_building_simple(-15, 60, 10, 15, 55, mat_building_dark)

# Right side
create_building_simple(15, -40, 10, 15, 75, mat_building_mid)
create_building_simple(15, -20, 10, 15, 95, mat_building_dark)
create_building_simple(15, 0, 10, 15, 65, mat_building_light)
create_building_simple(15, 20, 10, 15, 85, mat_building_mid)
create_building_simple(15, 40, 10, 15, 110, mat_building_dark)
create_building_simple(15, 60, 10, 15, 70, mat_building_light)

# Background
create_building_simple(0, -60, 20, 20, 120, mat_building_dark)
create_building_simple(-30, -50, 15, 15, 90, mat_building_mid)
create_building_simple(30, -50, 15, 15, 100, mat_building_dark)
create_building_simple(0, 50, 25, 20, 130, mat_building_dark)
create_building_simple(-35, 40, 15, 15, 80, mat_building_mid)
create_building_simple(35, 40, 15, 15, 95, mat_building_dark)

# ===================== NEON SIGNS (simple emissive planes) =====================
def create_neon_sign_simple(x, y, z, width, height, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
    sign = bpy.context.active_object
    sign.scale = (width/2, height/2, 1)
    sign.rotation_euler = (math.pi/2, 0, 0)
    sign.data.materials.append(mat)
    return sign

# Noodle bar sign
create_neon_sign_simple(-8, 8, -5, 4, 1.5, mat_neon_pink)
create_neon_sign_simple(-8, 6, -5, 3, 1, mat_neon_cyan)

# More signs
create_neon_sign_simple(8, 12, -3, 3, 1.2, mat_neon_yellow)
create_neon_sign_simple(-10, 15, 5, 2.5, 1, mat_neon_green)
create_neon_sign_simple(10, 18, 8, 2.5, 1, mat_neon_purple)
create_neon_sign_simple(-9, 22, 12, 3, 1.2, mat_neon_red)
create_neon_sign_simple(9, 25, 15, 3.5, 1.5, mat_neon_cyan)
create_neon_sign_simple(-8, 30, 20, 4, 1.5, mat_neon_pink)
create_neon_sign_simple(10, 35, 25, 3.5, 1.2, mat_neon_yellow)
create_neon_sign_simple(-10, 40, 30, 3, 1.2, mat_neon_green)
create_neon_sign_simple(8, 45, 35, 4.5, 1.5, mat_neon_purple)
create_neon_sign_simple(-9, 50, 40, 4, 1.5, mat_neon_red)

# ===================== ADVERTISING SCREENS =====================
def create_ad_screen_simple(x, y, z, width, height, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
    screen = bpy.context.active_object
    screen.scale = (width/2, height/2, 1)
    screen.rotation_euler = (0, 0, 0)
    screen.data.materials.append(mat)
    return screen

create_ad_screen_simple(-12, 50, -45, 8, 5, mat_screen)
create_ad_screen_simple(12, 55, -45, 8, 5, mat_screen2)
create_ad_screen_simple(-12, 60, 45, 10, 6, mat_screen)
create_ad_screen_simple(12, 65, 45, 10, 6, mat_screen2)
create_ad_screen_simple(0, 70, -55, 12, 8, mat_screen)
create_ad_screen_simple(-25, 40, -55, 8, 5, mat_screen2)
create_ad_screen_simple(25, 45, -55, 8, 5, mat_screen)
create_ad_screen_simple(0, 75, 55, 14, 9, mat_screen2)

# ===================== NOODLE BAR =====================
bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, 3, -5))
noodle_bar = bpy.context.active_object
noodle_bar.scale = (4, 3, 5)
noodle_bar.data.materials.append(mat_building_mid)

# Awning
bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, 6, -8))
awning = bpy.context.active_object
awning.scale = (4.5, 0.3, 2)
awning.data.materials.append(mat_neon_pink)

# Counter
bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, 1, -7))
counter = bpy.context.active_object
counter.scale = (3, 0.8, 1)
counter.data.materials.append(mat_concrete)

# Steam vents
for i in range(3):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(-9 + i*1, 4, -6))
    vent = bpy.context.active_object
    vent.data.materials.append(mat_steam)

# Noodle bowls
for i in range(4):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.15, location=(-9 + i*0.8, 1.8, -7))
    bowl = bpy.context.active_object
    bowl.data.materials.append(mat_noodle)

# ===================== CROWDS WITH UMBRELLAS =====================
def create_person_simple(x, z, umbrella_mat):
    # Body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.5, location=(x, 0.75, z))
    body = bpy.context.active_object
    body.data.materials.append(random.choice([mat_person, mat_person2]))
    
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x, 1.7, z))
    head = bpy.context.active_object
    head.data.materials.append(mat_person)
    
    # Umbrella
    bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0.1, depth=0.5, location=(x, 2.2, z))
    umbrella = bpy.context.active_object
    umbrella.data.materials.append(umbrella_mat)
    
    # Handle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1, location=(x, 1.7, z))
    handle = bpy.context.active_object
    handle.data.materials.append(mat_metal)

umbrella_mats = [mat_umbrella, mat_umbrella2, mat_umbrella3]
for i in range(25):
    x = random.uniform(-18, 18)
    z = random.uniform(-50, 50)
    if abs(x) < 3:
        x += 4 * (1 if x > 0 else -1)
    create_person_simple(x, z, random.choice(umbrella_mats))

# ===================== FLYING POLICE CAR =====================
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, -20))
car_body = bpy.context.active_object
car_body.scale = (2, 0.8, 3)
car_body.data.materials.append(mat_car_body)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 15.5, -18))
cockpit = bpy.context.active_object
cockpit.scale = (1.2, 0.6, 1.5)
cockpit.data.materials.append(mat_car_glass)

bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.5, location=(-1.5, 14.5, -22))
engine1 = bpy.context.active_object
engine1.rotation_euler = (0, math.pi/2, 0)
engine1.data.materials.append(mat_metal)

bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.5, location=(1.5, 14.5, -22))
engine2 = bpy.context.active_object
engine2.rotation_euler = (0, math.pi/2, 0)
engine2.data.materials.append(mat_metal)

bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5, 16.2, -20))
light1 = bpy.context.active_object
light1.scale = (0.3, 0.2, 0.5)
light1.data.materials.append(mat_car_light)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0.5, 16.2, -20))
light2 = bpy.context.active_object
light2.scale = (0.3, 0.2, 0.5)
light2.data.materials.append(mat_car_light2)

# ===================== RAIN =====================
rain_mesh = bpy.data.meshes.new("Rain")
rain_verts = []
for i in range(300):
    x = random.uniform(-30, 30)
    y = random.uniform(0, 20)
    z = random.uniform(-60, 60)
    rain_verts.append((x, y, z))
    rain_verts.append((x + random.uniform(-0.05, 0.05), y - 0.3, z + random.uniform(-0.05, 0.05)))
rain_faces = []
for i in range(0, len(rain_verts), 2):
    rain_faces.append((i, i+1))
rain.from_pydata(rain_verts, [], rain_faces)
rain_obj = bpy.data.objects.new("Rain", rain_mesh)
scene.collection.objects.link(rain_obj)
rain_obj.data.materials.append(mat_rain)

# ===================== LIGHTING =====================
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.02, 0.02, 0.04, 1)
    bg.inputs[1].default_value = 1.0

bpy.ops.object.light_add(type='SUN', location=(0, 30, 0))
sun = bpy.context.active_object
sun.data.energy = 0.5
sun.data.color = (0.5, 0.6, 0.8)
sun.rotation_euler = (math.radians(45), 0, 0)

neon_positions = [
    (-8, 8, -5, mat_neon_pink),
    (8, 12, -3, mat_neon_yellow),
    (-10, 15, 5, mat_neon_green),
    (10, 18, 8, mat_neon_purple),
    (-9, 22, 12, mat_neon_red),
    (9, 25, 15, mat_neon_cyan),
    (-8, 30, 20, mat_neon_pink),
    (10, 35, 25, mat_neon_yellow),
    (-10, 40, 30, mat_neon_green),
    (8, 45, 35, mat_neon_purple),
    (-9, 50, 40, mat_neon_red),
]

for x, y, z, mat in neon_positions:
    bpy.ops.object.light_add(type='POINT', location=(x, y, z))
    light = bpy.context.active_object
    light.data.energy = 50
    light.data.color = mat.node_tree.nodes.get("Principled BSDF").inputs['Emission Color'].default_value
    light.data.shadow_soft_size = 0.5

for x, y, z in [(-12, 50, -45), (12, 55, -45), (-12, 60, 45), (12, 65, 45), (0, 70, -55)]:
    bpy.ops.object.light_add(type='AREA', location=(x, y, z))
    light = bpy.context.active_object
    light.data.energy = 200
    light.data.color = (0.3, 0.5, 0.8)
    light.data.size = 5
    light.rotation_euler = (math.pi/2, 0, 0)

bpy.ops.object.light_add(type='SPOT', location=(-0.5, 16.2, -20))
police_light1 = bpy.context.active_object
police_light1.data.energy = 100
police_light1.data.color = (1, 0.1, 0.1)
police_light1.data.spot_size = math.radians(60)
police_light1.rotation_euler = (math.pi, 0, 0)

bpy.ops.object.light_add(type='SPOT', location=(0.5, 16.2, -20))
police_light2 = bpy.context.active_object
police_light2.data.energy = 100
police_light2.data.color = (0.1, 0.3, 1)
police_light2.data.spot_size = math.radians(60)
police_light2.rotation_euler = (math.pi, 0, 0)

# ===================== CAMERA =====================
bpy.ops.object.camera_add(location=(0, 3, 30))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(80), 0, math.radians(5))
scene.camera = camera

print("Blade Runner street scene created!")
