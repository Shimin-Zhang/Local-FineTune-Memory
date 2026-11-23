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
scene.render.film_transparent = False
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

# Create materials
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
mat_glow = make_material("Glow", (1, 0.5, 0.2, 1), 0.0, 0.3, 3.0, (1, 0.5, 0.2, 1))

# ===================== ROAD =====================
# Main street
road = bpy.data.meshes.new("Road")
verts = [(-20, 0, -100), (20, 0, -100), (20, 0, 100), (-20, 0, 100)]
faces = [(0, 1, 2, 3)]
road.from_pydata(verts, [], faces)
road_obj = bpy.data.objects.new("Road", road)
scene.collection.objects.link(road_obj)
road_obj.data.materials.append(mat_wet_road)

# Road markings
for z in range(-90, 100, 15):
    marking = bpy.data.meshes.new("Marking")
    mverts = [(-0.3, 0.01, z), (0.3, 0.01, z), (0.3, 0.01, z+8), (-0.3, 0.01, z+8)]
    mfaces = [(0, 1, 2, 3)]
    marking.from_pydata(mverts, [], mfaces)
    mobj = bpy.data.objects.new("Marking", marking)
    scene.collection.objects.link(mobj)
    mobj.data.materials.append(mat_neon_yellow)

# ===================== BUILDINGS =====================
def create_building(x, z, width, depth, height, mat, floors=10):
    # Main structure
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, height/2, z))
    bld = bpy.context.active_object
    bld.scale = (width/2, height/2, depth/2)
    bld.data.materials.append(mat)
    
    # Windows
    window_mats = [mat_window, mat_window_dim]
    for fy in range(floors):
        for fx in range(int(width/2)):
            for fz in range(int(depth/2)):
                if random.random() > 0.3:
                    wx = x - width/2 + 1 + fx * 2
                    wy = 2 + fy * (height/floors)
                    wz = z - depth/2 + 1 + fz * 2
                    if wx > x - width/2 and wx < x + width/2 and wz > z - depth/2 and wz < z + depth/2:
                        bpy.ops.mesh.primitive_cube_add(size=1, location=(wx, wy, wz))
                        win = bpy.context.active_object
                        win.scale = (0.4, 0.3, 0.4)
                        win.data.materials.append(random.choice(window_mats))
    return bld

# Left side buildings
create_building(-15, -40, 10, 15, 60, mat_building_dark, 15)
create_building(-15, -20, 10, 15, 80, mat_building_mid, 20)
create_building(-15, 0, 10, 15, 100, mat_building_dark, 25)
create_building(-15, 20, 10, 15, 70, mat_building_light, 18)
create_building(-15, 40, 10, 15, 90, mat_building_mid, 22)
create_building(-15, 60, 10, 15, 55, mat_building_dark, 14)

# Right side buildings
create_building(15, -40, 10, 15, 75, mat_building_mid, 19)
create_building(15, -20, 10, 15, 95, mat_building_dark, 24)
create_building(15, 0, 10, 15, 65, mat_building_light, 16)
create_building(15, 20, 10, 15, 85, mat_building_mid, 21)
create_building(15, 40, 10, 15, 110, mat_building_dark, 28)
create_building(15, 60, 10, 15, 70, mat_building_light, 17)

# Background buildings
create_building(0, -60, 20, 20, 120, mat_building_dark, 30)
create_building(-30, -50, 15, 15, 90, mat_building_mid, 22)
create_building(30, -50, 15, 15, 100, mat_building_dark, 25)
create_building(0, 50, 25, 20, 130, mat_building_dark, 32)
create_building(-35, 40, 15, 15, 80, mat_building_mid, 20)
create_building(35, 40, 15, 15, 95, mat_building_dark, 24)

# ===================== NEON SIGNS =====================
def create_neon_sign(x, y, z, text, mat, size=2, rotation=0):
    # Sign background
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    sign = bpy.context.active_object
    sign.scale = (size*1.5, size*0.8, 0.3)
    sign.rotation_euler = (0, 0, rotation)
    sign.data.materials.append(mat_sign_bg)
    
    # Neon text (using simple emissive planes)
    for i, char in enumerate(text):
        cx = x - size*1.2 + i * size*0.6
        bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, y + 0.1, z))
        p = bpy.context.active_object
        p.scale = (0.3, 0.4, 1)
        p.rotation_euler = (math.pi/2, 0, rotation)
        p.data.materials.append(mat)
    return sign

# Noodle bar sign
create_neon_sign(-8, 8, -5, "NOODLE", mat_neon_pink, 3, 0)
create_neon_sign(-8, 6, -5, "BAR", mat_neon_cyan, 2, 0)

# More neon signs
create_neon_sign(8, 12, -3, "RAMEN", mat_neon_yellow, 2.5, 0)
create_neon_sign(-10, 15, 5, "SUSHI", mat_neon_green, 2, 0)
create_neon_sign(10, 18, 8, "BAR", mat_neon_purple, 2, 0)
create_neon_sign(-9, 22, 12, "CLUB", mat_neon_red, 2.5, 0)
create_neon_sign(9, 25, 15, "HOTEL", mat_neon_cyan, 3, 0)
create_neon_sign(-8, 30, 20, "CASINO", mat_neon_pink, 3.5, 0)
create_neon_sign(10, 35, 25, "MARTINI", mat_neon_yellow, 3, 0)
create_neon_sign(-10, 40, 30, "TOKYO", mat_neon_green, 3, 0)
create_neon_sign(8, 45, 35, "LAS VEGAS", mat_neon_purple, 4, 0)
create_neon_sign(-9, 50, 40, "NEO-TOKYO", mat_neon_red, 4, 0)

# ===================== ADVERTISING SCREENS =====================
def create_ad_screen(x, y, z, width, height, mat, rotation=0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
    screen = bpy.context.active_object
    screen.scale = (width/2, height/2, 1)
    screen.rotation_euler = (0, 0, rotation)
    screen.data.materials.append(mat)
    
    # Frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    frame = bpy.context.active_object
    frame.scale = (width/2 + 0.2, height/2 + 0.2, 0.1)
    frame.rotation_euler = (0, 0, rotation)
    frame.data.materials.append(mat_metal)
    return screen

# Large screens on towers
create_ad_screen(-12, 50, -45, 8, 5, mat_screen, 0)
create_ad_screen(12, 55, -45, 8, 5, mat_screen2, 0)
create_ad_screen(-12, 60, 45, 10, 6, mat_screen, 0)
create_ad_screen(12, 65, 45, 10, 6, mat_screen2, 0)
create_ad_screen(0, 70, -55, 12, 8, mat_screen, 0)
create_ad_screen(-25, 40, -55, 8, 5, mat_screen2, 0)
create_ad_screen(25, 45, -55, 8, 5, mat_screen, 0)
create_ad_screen(0, 75, 55, 14, 9, mat_screen2, 0)

# ===================== NOODLE BAR =====================
# Main structure
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

# Noodle bowls on counter
for i in range(4):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.15, location=(-9 + i*0.8, 1.8, -7))
    bowl = bpy.context.active_object
    bowl.data.materials.append(mat_noodle)

# ===================== CROWDS WITH UMBRELLAS =====================
def create_person_with_umbrella(x, z, umbrella_mat):
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
    
    # Umbrella handle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1, location=(x, 1.7, z))
    handle = bpy.context.active_object
    handle.data.materials.append(mat_metal)

# Create crowd
umbrella_mats = [mat_umbrella, mat_umbrella2, mat_umbrella3]
for i in range(30):
    x = random.uniform(-18, 18)
    z = random.uniform(-50, 50)
    # Avoid road center
    if abs(x) < 3:
        x += 4 * (1 if x > 0 else -1)
    create_person_with_umbrella(x, z, random.choice(umbrella_mats))

# ===================== FLYING POLICE CAR =====================
# Main body
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, -20))
car_body = bpy.context.active_object
car_body.scale = (2, 0.8, 3)
car_body.data.materials.append(mat_car_body)

# Cockpit
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 15.5, -18))
cockpit = bpy.context.active_object
cockpit.scale = (1.2, 0.6, 1.5)
cockpit.data.materials.append(mat_car_glass)

# Engine pods
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.5, location=(-1.5, 14.5, -22))
engine1 = bpy.context.active_object
engine1.rotation_euler = (0, math.pi/2, 0)
engine1.data.materials.append(mat_metal)

bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.5, location=(1.5, 14.5, -22))
engine2 = bpy.context.active_object
engine2.rotation_euler = (0, math.pi/2, 0)
engine2.data.materials.append(mat_metal)

# Police lights
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5, 16.2, -20))
light1 = bpy.context.active_object
light1.scale = (0.3, 0.2, 0.5)
light1.data.materials.append(mat_car_light)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0.5, 16.2, -20))
light2 = bpy.context.active_object
light2.scale = (0.3, 0.2, 0.5)
light2.data.materials.append(mat_car_light2)

# ===================== RAIN =====================
# Rain particles
rain_mesh = bpy.data.meshes.new("Rain")
rain_verts = []
for i in range(500):
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
# World
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.02, 0.02, 0.04, 1)
    bg.inputs[1].default_value = 1.0

# Key light (moonlight)
bpy.ops.object.light_add(type='SUN', location=(0, 30, 0))
sun = bpy.context.active_object
sun.data.energy = 0.5
sun.data.color = (0.5, 0.6, 0.8)
sun.rotation_euler = (math.radians(45), 0, 0)

# Neon lights
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

# Screen lights
for x, y, z in [(-12, 50, -45), (12, 55, -45), (-12, 60, 45), (12, 65, 45), (0, 70, -55)]:
    bpy.ops.object.light_add(type='AREA', location=(x, y, z))
    light = bpy.context.active_object
    light.data.energy = 200
    light.data.color = (0.3, 0.5, 0.8)
    light.data.size = 5
    light.rotation_euler = (math.pi/2, 0, 0)

# Police car lights
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
camera.rotation_euler = (math.radians(85), 0, 0)
scene.camera = camera

# Set camera to look down the street
camera.rotation_euler = (math.radians(80), 0, math.radians(5))

# ===================== FOG/ATMOSPHERE =====================
# Add volume scatter for atmosphere
world.node_tree.nodes.clear()
world_out = world.node_tree.nodes.new('ShaderNodeOutputWorld')
world_out.location = (300, 0)
bg = world.node_tree.nodes.new('ShaderNodeBackground')
bg.location = (0, 0)
bg.inputs[0].default_value = (0.02, 0.02, 0.04, 1)
bg.inputs[1].default_value = 1.0
world.node_tree.links.new(bg.outputs['Background'], world_out.inputs['Surface'])

# Add volume
volume = world.node_tree.nodes.new('ShaderNodeVolumeScatter')
volume.location = (150, -200)
volume.inputs['Color'].default_value = (0.1, 0.1, 0.15, 1)
volume.inputs['Density'].default_value = 0.02
world.node_tree.links.new(volume.outputs['Volume'], world_out.inputs['Volume'])

print("Blade Runner street scene created!")
