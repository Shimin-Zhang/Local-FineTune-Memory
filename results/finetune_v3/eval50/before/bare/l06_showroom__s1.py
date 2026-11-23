import bpy
import math
import mathutils

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a glossy floor
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "GlossyFloor"

floor_mat = bpy.data.materials.new(name="GlossyFloorMat")
floor_mat.use_nodes = True
nodes = floor_mat.node_tree.nodes
links = floor_mat.node_tree.links

bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf.inputs["Roughness"].default_value = 0.05
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Specular IOR Level"].default_value = 1.0
# Add a slight clearcoat for extra gloss
if "Coat Weight" in bsdf.inputs:
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Coat Roughness"].default_value = 0.03

floor.data.materials.append(floor_mat)

# Create a simple red sports car using a collection of primitives
car_collection = bpy.data.collections.new("SportsCar")
bpy.context.scene.collection.children.link(car_collection)

def add_to_car(obj):
    for col in obj.users_collection:
        col.objects.unlink(obj)
    car_collection.objects.link(obj)

# Car body (scaled cube)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.35))
body = bpy.context.active_object
body.name = "CarBody"
body.scale = (1.8, 0.9, 0.45)
bpy.ops.object.transform_apply(scale=True)

# Cabin (smaller cube on top)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.2, 0, 0.75))
cabin = bpy.context.active_object
cabin.name = "CarCabin"
cabin.scale = (1.0, 0.8, 0.35)
bpy.ops.object.transform_apply(scale=True)

# Hood (slightly lower, front)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.8, 0, 0.5))
hood = bpy.context.active_object
hood.name = "CarHood"
hood.scale = (0.8, 0.85, 0.2)
bpy.ops.object.transform_apply(scale=True)

# Trunk (rear)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.0, 0, 0.5))
trunk = bpy.context.active_object
trunk.name = "CarTrunk"
trunk.scale = (0.6, 0.85, 0.25)
bpy.ops.object.transform_apply(scale=True)

# Wheels (cylinders)
wheel_positions = [(-1.2, -0.7, 0.25), (-1.2, 0.7, 0.25), (1.2, -0.7, 0.25), (1.2, 0.7, 0.25)]
for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.2, location=pos, rotation=(0, math.pi/2, 0))
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    wheel.scale = (1, 1, 1)
    bpy.ops.object.transform_apply(scale=True)

# Red car material
car_mat = bpy.data.materials.new(name="RedCarMat")
car_mat.use_nodes = True
car_nodes = car_mat.node_tree.nodes
car_links = car_mat.node_tree.links
car_bsdf = car_nodes["Principled BSDF"]
car_bsdf.inputs["Base Color"].default_value = (0.8, 0.0, 0.0, 1.0)
car_bsdf.inputs["Metallic"].default_value = 0.8
car_bsdf.inputs["Roughness"].default_value = 0.15
if "Coat Weight" in car_bsdf.inputs:
    car_bsdf.inputs["Coat Weight"].default_value = 1.0
    car_bsdf.inputs["Coat Roughness"].default_value = 0.05

# Apply red material to body parts
for obj_name in ["CarBody", "CarCabin", "CarHood", "CarTrunk"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        obj.data.materials.clear()
        obj.data.materials.append(car_mat)

# Dark material for wheels
wheel_mat = bpy.data.materials.new(name="WheelMat")
wheel_mat.use_nodes = True
w_bsdf = wheel_mat.node_tree.nodes["Principled BSDF"]
w_bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
w_bsdf.inputs["Metallic"].default_value = 0.9
w_bsdf.inputs["Roughness"].default_value = 0.3

for i in range(4):
    wheel = bpy.data.objects.get(f"Wheel_{i}")
    if wheel:
        wheel.data.materials.clear()
        wheel.data.materials.append(wheel_mat)

# Add all car parts to car collection
for obj in [body, cabin, hood, trunk] + [bpy.data.objects.get(f"Wheel_{i}") for i in range(4)]:
    if obj:
        add_to_car(obj)

# Showroom lighting: long soft area lights overhead
# Main overhead light (long, soft)
bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
main_light = bpy.context.active_object
main_light.name = "MainShowroomLight"
main_light.data.shape = 'RECTANGLE'
main_light.data.size = 6.0   # length
main_light.data.size_y = 1.5 # width
main_light.data.energy = 3000
main_light.data.color = (1.0, 1.0, 1.0)
main_light.rotation_euler = (0, 0, 0)

# Secondary overhead light (slightly offset, warmer)
bpy.ops.object.light_add(type='AREA', location=(0, 2, 4.5))
sec_light = bpy.context.active_object
sec_light.name = "SecondaryShowroomLight"
sec_light.data.shape = 'RECTANGLE'
sec_light.data.size = 5.0
sec_light.data.size_y = 1.0
sec_light.data.energy = 1500
sec_light.data.color = (1.0, 0.95, 0.9)
sec_light.rotation_euler = (0, 0, 0)

# Accent light from the side (cool blue-ish for showroom feel)
bpy.ops.object.light_add(type='AREA', location=(-4, 0, 3))
accent_light = bpy.context.active_object
accent_light.name = "AccentLight"
accent_light.data.shape = 'RECTANGLE'
accent_light.data.size = 2.0
accent_light.data.size_y = 4.0
accent_light.data.energy = 800
accent_light.data.color = (0.7, 0.8, 1.0)
accent_light.rotation_euler = (0, math.pi/2, 0)

# Set world background to dark
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs["Color"].default_value = (0.02, 0.02, 0.03, 1.0)
bg_node.inputs["Strength"].default_value = 0.5

# Set render engine to Cycles for better lighting
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# Set camera
bpy.ops.object.camera_add(location=(4, 4, 2), rotation=(math.radians(60), 0, math.radians(-45)))
camera = bpy.context.active_object
camera.name = "ShowroomCamera"
bpy.context.scene.camera = camera

# Set film to transparent off, use glossy
bpy.context.scene.render.film_transparent = False
bpy.context.scene.view_settings.look = 'AgX - Punchy'
bpy.context.scene.view_settings.exposure = 0.0
