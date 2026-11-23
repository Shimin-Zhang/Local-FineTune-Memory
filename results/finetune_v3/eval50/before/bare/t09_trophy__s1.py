import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new scene
scene = bpy.context.scene

# Create a material for brushed gold
material = bpy.data.materials.new(name="BrushedGold")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (400, 0)

principled_node = nodes.new('ShaderNodeBsdfPrincipled')
principled_node.location = (100, 0)

# Set gold color
principled_node.inputs['Base Color'].default_value = (0.85, 0.65, 0.13, 1.0)
principled_node.inputs['Metallic'].default_value = 1.0
principled_node.inputs['Roughness'].default_value = 0.25
principled_node.inputs['Anisotropic'].default_value = 0.8
principled_node.inputs['Anisotropic Rotation'].default_value = 0.0

# Add noise texture for brushed effect
noise_node = nodes.new('ShaderNodeTexNoise')
noise_node.location = (-200, 0)
noise_node.inputs['Scale'].default_value = 50.0
noise_node.inputs['Detail'].default_value = 8.0
noise_node.inputs['Roughness'].default_value = 0.7

# Add mapping node for stretched noise (brushed effect)
mapping_node = nodes.new('ShaderNodeMapping')
mapping_node.location = (-400, 0)
mapping_node.inputs['Scale'].default_value = (1.0, 10.0, 1.0)  # Stretch along Y for brushed look

# Add texture coordinate
tex_coord_node = nodes.new('ShaderNodeTexCoord')
tex_coord_node.location = (-600, 0)

# Connect nodes
links.new(tex_coord_node.outputs['Object'], mapping_node.inputs['Vector'])
links.new(mapping_node.outputs['Vector'], noise_node.inputs['Vector'])
links.new(noise_node.outputs['Fac'], principled_node.inputs['Roughness'])
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# Create trophy cup using lathe/spin technique
# Define profile points for the trophy cup
profile_points = [
    (0.0, 0.0),      # bottom center
    (0.3, 0.0),      # bottom edge
    (0.3, 0.05),     # base
    (0.25, 0.1),     # base taper
    (0.15, 0.2),     # stem bottom
    (0.12, 0.3),     # stem
    (0.1, 0.4),      # stem top
    (0.15, 0.45),    # bowl bottom
    (0.25, 0.55),    # bowl
    (0.3, 0.65),     # bowl
    (0.32, 0.75),    # bowl top
    (0.35, 0.8),     # rim
    (0.33, 0.82),    # rim inner
    (0.3, 0.8),      # rim inner
    (0.28, 0.75),    # inner bowl
    (0.25, 0.65),    # inner bowl
    (0.2, 0.55),     # inner bowl
    (0.12, 0.45),    # inner stem top
    (0.1, 0.4),      # inner stem
    (0.12, 0.3),     # inner stem
    (0.15, 0.2),     # inner stem
    (0.2, 0.1),      # inner base
    (0.25, 0.05),    # inner base
    (0.25, 0.0),     # inner bottom
]

# Create mesh
mesh = bpy.data.meshes.new("TrophyCup")
object = bpy.data.objects.new("TrophyCup", mesh)
scene.collection.objects.link(object)

# Create vertices and edges for the profile
vertices = []
edges = []

for i, (x, y) in enumerate(profile_points):
    vertices.append((x, 0, y))

for i in range(len(profile_points) - 1):
    edges.append((i, i + 1))

mesh.from_pydata(vertices, edges, [])
mesh.update()

# Use spin modifier to create the cup
# First, select the object
bpy.context.view_layer.objects.active = object
object.select_set(True)

# Add spin modifier
spin_mod = object.modifiers.new(name="Spin", type='SPIN')
spin_mod.axis = 'Z'
spin_mod.steps = 64
spin_mod.use_merge_vertices = True
spin_mod.merge_threshold = 0.001

# Apply the modifier
bpy.ops.object.modifier_apply(modifier="Spin")

# Add handles
# Create left handle
handle_mesh = bpy.data.meshes.new("HandleLeft")
handle_obj = bpy.data.objects.new("HandleLeft", handle_mesh)
scene.collection.objects.link(handle_obj)

# Create a torus for the handle
bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.03, location=(0.4, 0, 0.65))
handle_left = bpy.context.active_object
handle_left.name = "HandleLeft"
handle_left.rotation_euler = (0, math.radians(90), 0)

# Create right handle
bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.03, location=(-0.4, 0, 0.65))
handle_right = bpy.context.active_object
handle_right.name = "HandleRight"
handle_right.rotation_euler = (0, math.radians(-90), 0)

# Apply material to all parts
for obj in [object, handle_left, handle_right]:
    obj.data.materials.append(material)

# Join handles with cup
bpy.ops.object.select_all(action='DESELECT')
object.select_set(True)
handle_left.select_set(True)
handle_right.select_set(True)
bpy.context.view_layer.objects.active = object
bpy.ops.object.join()

# Smooth shading
bpy.ops.object.shade_smooth()

# Set viewport to show the trophy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for region in area.regions:
            if region.type == 'WINDOW':
                override = bpy.context.copy()
                override['area'] = area
                override['region'] = region
                with bpy.context.temp_override(**override):
                    bpy.ops.view3d.view_selected()
