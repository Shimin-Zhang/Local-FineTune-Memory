import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up world - dark showroom
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.01, 0.01, 0.015, 1.0)
    bg.inputs[1].default_value = 1.0

# Create glossy floor
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "GlossyFloor"

# Create glossy material for floor
floor_mat = bpy.data.materials.new("GlossyFloorMat")
floor_mat.use_nodes = True
nodes = floor_mat.node_tree.nodes
links = floor_mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create new nodes
bsdf = nodes.new("ShaderNodeBsdfGlossy")
bsdf.inputs["Roughness"].default_value = 0.05
bsdf.inputs["IOR"].default_value = 1.45

output = nodes.new("ShaderNodeOutputMaterial")

links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

floor.data.materials.append(floor_mat)

# Create a simple sports car (simplified geometry)
# Body
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
body = bpy.context.active_object
body.name = "CarBody"
body.scale = (2.2, 0.9, 0.4)
bpy.ops.object.transform_apply(scale=True)

# Cabin
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.85))
cabin = bpy.context.active_object
cabin.name = "CarCabin"
cabin.scale = (1.2, 0.8, 0.3)
bpy.ops.object.transform_apply(scale=True)

# Join car parts
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
cabin.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
car = bpy.context.active_object
car.name = "SportsCar"

# Add red car material
car_mat = bpy.data.materials.new("RedCarPaint")
car_mat.use_nodes = True
nodes = car_mat.node_tree.nodes
links = car_mat.node_tree.links

for node in nodes:
    nodes.remove(node)

bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.8, 0.0, 0.0, 1.0)
bsdf.inputs["Metallic"].default_value = 0.8
bsdf.inputs["Roughness"].default_value = 0.1
bsdf.inputs["Coat Weight"].default_value = 1.0
bsdf.inputs["Coat Roughness"].default_value = 0.05

output = nodes.new("ShaderNodeOutputMaterial")
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

car.data.materials.append(car_mat)

# Add wheels
wheel_positions = [
    (-1.3, 0.65, 0.25),
    (-1.3, -0.65, 0.25),
    (1.3, 0.65, 0.25),
    (1.3, -0.65, 0.25)
]

wheel_mat = bpy.data.materials.new("WheelMat")
wheel_mat.use_nodes = True
nodes = wheel_mat.node_tree.nodes
links = wheel_mat.node_tree.links

for node in nodes:
    nodes.remove(node)

bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
bsdf.inputs["Metallic"].default_value = 0.9
bsdf.inputs["Roughness"].default_value = 0.3

output = nodes.new("ShaderNodeOutputMaterial")
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, location=pos, rotation=(0, math.pi/2, 0))
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"
    wheel.data.materials.append(wheel_mat)

# Create long soft overhead lights (area lights)
# Main overhead light strip
bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
main_light = bpy.context.active_object
main_light.name = "MainOverheadLight"
main_light.data.shape = 'RECTANGLE'
main_light.data.size = 6.0
main_light.data.size_y = 2.0
main_light.data.energy = 2000
main_light.data.color = (1.0, 1.0, 1.0)

# Additional side accent lights
bpy.ops.object.light_add(type='AREA', location=(-3, 0, 3))
side_light1 = bpy.context.active_object
side_light1.name = "SideLight1"
side_light1.data.shape = 'RECTANGLE'
side_light1.data.size = 1.0
side_light1.data.size_y = 4.0
side_light1.data.energy = 800
side_light1.data.color = (1.0, 0.95, 0.9)
side_light1.rotation_euler = (0, math.radians(90), 0)

bpy.ops.object.light_add(type='AREA', location=(3, 0, 3))
side_light2 = bpy.context.active_object
side_light2.name = "SideLight2"
side_light2.data.shape = 'RECTANGLE'
side_light2.data.size = 1.0
side_light2.data.size_y = 4.0
side_light2.data.energy = 800
side_light2.data.color = (1.0, 0.95, 0.9)
side_light2.rotation_euler = (0, math.radians(-90), 0)

# Back fill light
bpy.ops.object.light_add(type='AREA', location=(0, -4, 3))
back_light = bpy.context.active_object
back_light.name = "BackFillLight"
back_light.data.shape = 'RECTANGLE'
back_light.data.size = 4.0
back_light.data.size_y = 1.0
back_light.data.energy = 500
back_light.data.color = (0.9, 0.95, 1.0)
back_light.rotation_euler = (math.radians(60), 0, 0)

# Set up camera
bpy.ops.object.camera_add(location=(5, -5, 2))
camera = bpy.context.active_object
camera.name = "ShowroomCamera"

# Point camera at the car
direction = (0, 0, 0.5) - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Set camera as active
bpy.context.scene.camera = camera

# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# Enable bloom for showroom glow
bpy.context.scene.view_settings.look = 'AgX - Punchy'
bpy.context.scene.view_settings.exposure = 0.3
