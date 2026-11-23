import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the mug body (red)
bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=2.0, location=(0, 0, 1.0))
mug = bpy.context.active_object
mug.name = "Mug"

# Create the handle (white)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.8,
    minor_radius=0.15,
    location=(1.0, 0, 1.0),
    rotation=(0, math.pi/2, 0)
)
handle = bpy.context.active_object
handle.name = "Handle"

# Create red material
red_mat = bpy.data.materials.new(name="Red")
red_mat.use_nodes = True
red_bsdf = red_mat.node_tree.nodes["Principled BSDF"]
red_bsdf.inputs["Base Color"].default_value = (1.0, 0.0, 0.0, 1.0)

# Create white material
white_mat = bpy.data.materials.new(name="White")
white_mat.use_nodes = True
white_bsdf = white_mat.node_tree.nodes["Principled BSDF"]
white_bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)

# Assign materials
mug.data.materials.append(red_mat)
handle.data.materials.append(white_mat)
