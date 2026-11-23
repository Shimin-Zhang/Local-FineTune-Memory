import bpy
import math
import bmesh
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Create the mug body (red) ---
# Use a cylinder for the mug body
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=2.0,
    location=(0, 0, 1.0),
    vertices=64
)
mug_body = bpy.context.active_object
mug_body.name = "Mug_Body"

# Make the mug hollow (inner cavity)
# Add a boolean modifier to cut out the inside
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.85,
    depth=1.8,
    location=(0, 0, 1.1),
    vertices=64
)
cutter = bpy.context.active_object
cutter.name = "Cutter"

# Apply boolean modifier to mug body
mod = mug_body.modifiers.new(name="Boolean", type='BOOLEAN')
mod.object = cutter
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'

# Apply the modifier
bpy.context.view_layer.objects.active = mug_body
bpy.ops.object.modifier_apply(modifier="Boolean")

# Delete the cutter
bpy.data.objects.remove(cutter, do_unlink=True)

# Add a slight bevel to the top edge for a nicer look
bpy.ops.object.select_all(action='DESELECT')
mug_body.select_set(True)
bpy.context.view_layer.objects.active = mug_body

# Create a bevel modifier
bevel_mod = mug_body.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.02
bevel_mod.segments = 3
bpy.ops.object.modifier_apply(modifier="Bevel")

# Smooth shading
bpy.ops.object.shade_smooth()
# Add edge split for better appearance
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)

# --- Create the handle (white) ---
# Use a torus for the handle, scaled and positioned
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.5,
    minor_radius=0.12,
    location=(1.0, 0, 1.0),
    major_segments=32,
    minor_segments=16
)
handle = bpy.context.active_object
handle.name = "Mug_Handle"

# Rotate the handle to be vertical (around Y axis)
handle.rotation_euler[1] = math.radians(90)

# Scale to make it more elongated vertically
handle.scale = (1.0, 1.0, 1.4)

# Apply transforms
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Smooth shading
bpy.ops.object.shade_smooth()

# --- Create materials ---

# Red material for the mug body
red_mat = bpy.data.materials.new(name="Red_Mug")
red_mat.use_nodes = True
nodes = red_mat.node_tree.nodes
links = red_mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)

# Set red color
bsdf.inputs['Base Color'].default_value = (0.8, 0.0, 0.0, 1.0)
bsdf.inputs['Roughness'].default_value = 0.3

# Create output node
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)

# Link BSDF to output
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign red material to mug body
mug_body.data.materials.clear()
mug_body.data.materials.append(red_mat)

# White material for the handle
white_mat = bpy.data.materials.new(name="White_Handle")
white_mat.use_nodes = True
nodes_w = white_mat.node_tree.nodes
links_w = white_mat.node_tree.links

# Clear default nodes
for node in nodes_w:
    nodes_w.remove(node)

# Create Principled BSDF
bsdf_w = nodes_w.new(type='ShaderNodeBsdfPrincipled')
bsdf_w.location = (0, 0)

# Set white color
bsdf_w.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
bsdf_w.inputs['Roughness'].default_value = 0.2

# Create output node
output_w = nodes_w.new(type='ShaderNodeOutputMaterial')
output_w.location = (300, 0)

# Link BSDF to output
links_w.new(bsdf_w.outputs['BSDF'], output_w.inputs['Surface'])

# Assign white material to handle
handle.data.materials.clear()
handle.data.materials.append(white_mat)

# --- Add a simple light and camera for better visualization ---

# Add a point light
bpy.ops.object.light_add(type='POINT', location=(3, 3, 3))
light = bpy.context.active_object
light.data.energy = 1000
light.name = "Light"

# Add a camera
bpy.ops.object.camera_add(location=(4, 4, 2), rotation=(math.radians(60), 0, math.radians(-45)))
camera = bpy.context.active_object
camera.name = "Camera"

# Set camera as active
bpy.context.scene.camera = camera

# Print confirmation
print("Red mug with white handle created successfully!")
