import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set units
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0

# Blue hour world environment
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

bg = nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.02, 0.05, 0.15, 1.0)  # Deep blue
bg.inputs['Strength'].default_value = 0.5

out = nodes.new('ShaderNodeOutputWorld')
links.new(bg.outputs['Background'], out.inputs['Surface'])

# Camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0, 18, 6)
cam.rotation_euler = (math.radians(75), 0, 0)
bpy.context.scene.camera = cam

# Materials
def create_material(name, color, metallic=0.0, roughness=0.5, emission=0.0, emit_color=(0,0,0)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission > 0:
        bsdf.inputs['Emission Color'].default_value = (*emit_color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission
    return mat

mat_glass = create_material("Glass", (0.8, 0.85, 0.9), 0.0, 0.05)
mat_glass.node_tree.nodes["Principled BSDF"].inputs['Transmission Weight'].default_value = 1.0
mat_glass.node_tree.nodes["Principled BSDF"].inputs['IOR'].default_value = 1.5

mat_court = create_material("Court", (0.1, 0.25, 0.15), 0.0, 0.8)
mat_roof = create_material("Roof", (0.15, 0.15, 0.15), 0.0, 0.9)
mat_metal = create_material("Metal", (0.3, 0.3, 0.3), 0.8, 0.3)
mat_net = create_material("Net", (0.9, 0.9, 0.9), 0.0, 0.5)
mat_bench = create_material("Bench", (0.2, 0.15, 0.1), 0.0, 0.7)
mat_cooler = create_material("Cooler", (0.1, 0.1, 0.12), 0.5, 0.2)
mat_light_pole = create_material("LightPole", (0.2, 0.2, 0.2), 0.7, 0.3)
mat_light_bulb = create_material("LightBulb", (1.0, 0.9, 0.7), 0.0, 0.0, emission=5.0, emit_color=(1.0, 0.9, 0.7))
mat_city_light = create_material("CityLight", (1.0, 0.8, 0.4), 0.0, 0.0, emission=2.0, emit_color=(1.0, 0.8, 0.4))
mat_building = create_material("Building", (0.05, 0.06, 0.08), 0.0, 0.9)
mat_building_window = create_material("BuildingWindow", (1.0, 0.9, 0.5), 0.0, 0.0, emission=1.5, emit_color=(1.0, 0.9, 0.5))

# Rooftop platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.25))
roof = bpy.context.active_object
roof.name = "Rooftop"
roof.scale = (12, 18, 0.5)
roof.data.materials.append(mat_roof)

# Padel court floor (20m x 10m standard)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.01))
court = bpy.context.active_object
court.name = "Court"
court.scale = (10, 20, 0.02)
court.data.materials.append(mat_court)

# Court lines
def add_line(x, y, length, along_x):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.03))
    line = bpy.context.active_object
    if along_x:
        line.scale = (length/2, 0.05, 0.01)
    else:
        line.scale = (0.05, length/2, 0.01)
    mat_line = create_material("Line", (0.9, 0.9, 0.9), 0.0, 0.5)
    line.data.materials.append(mat_line)

# Boundary lines
add_line(0, -10, 20, False)  # Left
add_line(0, 10, 20, False)   # Right
add_line(-10, 0, 20, True)   # Back
add_line(10, 0, 20, True)    # Front
add_line(0, 0, 20, False)    # Center line
add_line(-10, -5, 10, True)  # Service line back
add_line(10, 5, 10, True)    # Service line front

# Glass walls (3m high)
def add_glass_wall(x, y, width, height, along_x):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height/2))
    wall = bpy.context.active_object
    if along_x:
        wall.scale = (width/2, 0.02, height/2)
    else:
        wall.scale = (0.02, width/2, height/2)
    wall.data.materials.append(mat_glass)

# Back wall (along X)
add_glass_wall(0, -10, 20, 3, True)
# Front wall (along X)
add_glass_wall(0, 10, 20, 3, True)
# Left wall (along Y)
add_glass_wall(-10, 0, 20, 3, False)
# Right wall (along Y)
add_glass_wall(10, 0, 20, 3, False)

# Metal frames for glass walls
def add_frame(x, y, width, height, along_x):
    # Bottom frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.05))
    frame = bpy.context.active_object
    if along_x:
        frame.scale = (width/2, 0.05, 0.1)
    else:
        frame.scale = (0.05, width/2, 0.1)
    frame.data.materials.append(mat_metal)
    # Top frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height - 0.05))
    frame = bpy.context.active_object
    if along_x:
        frame.scale = (width/2, 0.05, 0.1)
    else:
        frame.scale = (0.05, width/2, 0.1)
    frame.data.materials.append(mat_metal)

add_frame(0, -10, 20, 3, True)
add_frame(0, 10, 20, 3, True)
add_frame(-10, 0, 20, 3, False)
add_frame(10, 0, 20, 3, False)

# Net (1.5m high at posts, 1.0m at center)
# Net posts
for x in [-0.5, 0.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.5, location=(x, 0, 0.75))
    post = bpy.context.active_object
    post.data.materials.append(mat_metal)

# Net mesh (simplified as a plane)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.75))
net = bpy.context.active_object
net.scale = (0.5, 1.0, 1.0)
net.rotation_euler = (math.radians(90), 0, 0)
net.data.materials.append(mat_net)

# Floodlights (4 corners)
def add_floodlight(x, y):
    # Pole
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=8, location=(x, y, 4))
    pole = bpy.context.active_object
    pole.data.materials.append(mat_light_pole)
    # Light fixture
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 8.2))
    fixture = bpy.context.active_object
    fixture.scale = (0.5, 0.3, 0.15)
    fixture.data.materials.append(mat_light_pole)
    # Light bulb
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x, y, 8.0))
    bulb = bpy.context.active_object
    bulb.data.materials.append(mat_light_bulb)
    # Actual light source
    light_data = bpy.data.lights.new(f"Floodlight_{x}_{y}", type='AREA')
    light_data.energy = 5000
    light_data.size = 1.0
    light_data.color = (1.0, 0.9, 0.7)
    light_obj = bpy.data.objects.new(f"Floodlight_{x}_{y}", light_data)
    light_obj.location = (x, y, 8.0)
    light_obj.rotation_euler = (math.radians(45), 0, 0)
    bpy.context.collection.objects.link(light_obj)

add_floodlight(-12, -12)
add_floodlight(12, -12)
add_floodlight(-12, 12)
add_floodlight(12, 12)

# Spectators' benches
def add_bench(x, y, length, along_x):
    # Seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.45))
    seat = bpy.context.active_object
    if along_x:
        seat.scale = (length/2, 0.25, 0.05)
    else:
        seat.scale = (0.25, length/2, 0.05)
    seat.data.materials.append(mat_bench)
    # Legs
    for i in range(3):
        if along_x:
            lx = x - length/2 + i * length/2
            ly = y
        else:
            lx = x
            ly = y - length/2 + i * length/2
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.45, location=(lx, ly, 0.225))
        leg = bpy.context.active_object
        leg.data.materials.append(mat_metal)

# Benches on both sides
add_bench(-13, 0, 12, False)
add_bench(13, 0, 12, False)

# Drinks cooler
bpy.ops.mesh.primitive_cube_add(size=1, location=(11, 8, 0.6))
cooler = bpy.context.active_object
cooler.scale = (0.5, 0.5, 0.6)
cooler.data.materials.append(mat_cooler)
# Cooler door handle
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.3, location=(11, 8.52, 0.6))
handle = bpy.context.active_object
handle.rotation_euler = (0, math.radians(90), 0)
handle.data.materials.append(mat_metal)

# City lights beyond (background buildings with lit windows)
random.seed(42)
for i in range(15):
    x = random.uniform(-50, 50)
    y = random.uniform(30, 80)
    height = random.uniform(10, 40)
    width = random.uniform(5, 15)
    
    # Building
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height/2 - 2))
    building = bpy.context.active_object
    building.scale = (width/2, width/2, height/2)
    building.data.materials.append(mat_building)
    
    # Windows (emissive)
    for wy in range(0, int(height/3)):
        for wx in range(0, int(width/3)):
            if random.random() > 0.3:
                wx_pos = x - width/2 + 1.5 + wx * 3
                wy_pos = y - width/2 + 1.5 + wy * 3
                wz_pos = -2 + 1.5 + wy * 3
                bpy.ops.mesh.primitive_plane_add(size=1, location=(wx_pos, wy_pos, wz_pos))
                window = bpy.context.active_object
                window.scale = (0.8, 0.01, 1.0)
                window.rotation_euler = (math.radians(90), 0, 0)
                window.data.materials.append(mat_building_window)

# Additional city lights (point lights for atmosphere)
for i in range(8):
    x = random.uniform(-40, 40)
    y = random.uniform(40, 70)
    light_data = bpy.data.lights.new(f"CityLight_{i}", type='POINT')
    light_data.energy = 50
    light_data.color = (1.0, 0.8, 0.4)
    light_data.shadow_soft_size = 1.0
    light_obj = bpy.data.objects.new(f"CityLight_{i}", light_data)
    light_obj.location = (x, y, random.uniform(5, 20))
    bpy.context.collection.objects.link(light_obj)

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# Set film exposure for blue hour feel
bpy.context.scene.view_settings.exposure = -0.5
