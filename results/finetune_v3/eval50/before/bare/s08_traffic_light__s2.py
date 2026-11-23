import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove default objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create the main body (black box)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
body = bpy.context.active_object
body.scale = (0.3, 0.3, 1.0)
body.name = "TrafficLight_Body"

# Create materials
def create_material(name, color, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Remove default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create Principled BSDF
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    
    # Set base color
    principled.inputs['Base Color'].default_value = color
    
    if emission is not None:
        principled.inputs['Emission Color'].default_value = emission
        principled.inputs['Emission Strength'].default_value = emission_strength
    
    # Create Material Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    # Link
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Black material for body
black_mat = create_material("Black", (0.02, 0.02, 0.02, 1.0))

# Red material with emission
red_mat = create_material("Red", (1.0, 0.0, 0.0, 1.0), emission=(1.0, 0.0, 0.0, 1.0), emission_strength=2.0)

# Yellow material with emission
yellow_mat = create_material("Yellow", (1.0, 0.8, 0.0, 1.0), emission=(1.0, 0.8, 0.0, 1.0), emission_strength=2.0)

# Green material with emission
green_mat = create_material("Green", (0.0, 1.0, 0.0, 1.0), emission=(0.0, 1.0, 0.0, 1.0), emission_strength=2.0)

# Apply black material to body
body.data.materials.append(black_mat)

# Create red light (top)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, 0.5))
red_light = bpy.context.active_object
red_light.name = "Red_Light"
red_light.data.materials.append(red_mat)

# Create yellow light (middle)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, 0.0))
yellow_light = bpy.context.active_object
yellow_light.name = "Yellow_Light"
yellow_light.data.materials.append(yellow_mat)

# Create green light (bottom)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, -0.5))
green_light = bpy.context.active_object
green_light.name = "Green_Light"
green_light.data.materials.append(green_mat)

# Add a pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.5, location=(0, 0, -1.25))
pole = bpy.context.active_object
pole.name = "Pole"
pole.data.materials.append(black_mat)

# Add a base
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, location=(0, 0, -2.05))
base = bpy.context.active_object
base.name = "Base"
base.data.materials.append(black_mat)

# Set up camera
bpy.ops.object.camera_add(location=(2, -2, 0.5))
camera = bpy.context.active_object
camera.name = "Camera"

# Point camera at the traffic light
direction = (0, 0, 0) - camera.location
rot_quat = direction.to_track_quat('Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Set camera as active
bpy.context.scene.camera = camera

# Add a light
bpy.ops.object.light_add(type='SUN', location=(3, -3, 5))
sun_light = bpy.context.active_object
sun_light.name = "Sun"
sun_light.data.energy = 3.0

# Set up world
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.1, 0.1, 0.15, 1.0)

print("Traffic light created successfully!")
