import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Create the Mug Body (Cylinder) ---
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=2.0, location=(0, 0, 1.0))
mug_body = bpy.context.active_object
mug_body.name = "Mug_Body"

# --- Create the Mug Interior (to make it look hollow) ---
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.9, depth=1.9, location=(0, 0, 1.05))
mug_inner = bpy.context.active_object
mug_inner.name = "Mug_Inner"

# Join the inner cylinder to the body (or keep separate for material assignment)
# Let's keep them separate for now, or better: use a solidify modifier on the body?
# Simpler approach for a visual mug: Just use a cylinder and a slightly smaller cylinder for the inside.
# Actually, the simplest way to make a "mug" look is a cylinder with a hole.
# Let's delete the inner one and use a different approach: 
# Create a cylinder, then use a boolean or just leave it as a solid cylinder for simplicity, 
# but a real mug has a hole. 
# Let's stick to the two-cylinder approach: Outer body and Inner rim.

# Let's refine: 
# Delete the inner cylinder we just made
bpy.ops.object.select_all(action='DESELECT')
mug_inner.select_set(True)
bpy.ops.object.delete()

# Create a new inner cylinder that is slightly smaller and positioned to create the rim
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.9, depth=2.0, location=(0, 0, 1.0))
mug_inner = bpy.context.active_object
mug_inner.name = "Mug_Inner"

# Now, to make it look like a mug, we need the top to be open.
# A common trick: Use a Solidify modifier on a plane or just accept a solid cylinder for a low-poly look.
# Let's do a proper mug: 
# 1. Outer Cylinder
# 2. Inner Cylinder (slightly smaller radius, same height)
# 3. We will assign materials.

# Let's delete the current inner and create a better setup.
# Actually, the easiest way to get a "mug" shape in Blender quickly:
# Create a cylinder, add a Solidify modifier, and move the top face down? No.
# Let's use the two cylinder method:
# Outer: Radius 1.0
# Inner: Radius 0.9
# They overlap. We'll just assign materials.

# Let's restart the object creation for clarity.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Mug Body (Red)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=2.0, location=(0, 0, 1.0))
mug_body = bpy.context.active_object
mug_body.name = "Mug_Body"

# 2. Mug Handle (White)
# Create a torus for the handle
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.6, 
    minor_radius=0.1, 
    major_segments=32, 
    minor_segments=16, 
    location=(1.0, 0, 1.0)  # Position it to the side of the mug
)
mug_handle = bpy.context.active_object
mug_handle.name = "Mug_Handle"

# Rotate the handle so it's vertical (default torus is in XY plane, we want it in YZ plane facing X)
mug_handle.rotation_euler = (0, math.radians(90), 0)

# Apply rotation to handle
bpy.ops.object.transform_apply(rotation=True)

# --- Materials ---

# Create Red Material
red_material = bpy.data.materials.new(name="Red_Mug")
red_material.use_nodes = True
bsdf = red_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.0, 0.0, 1.0)  # Red
bsdf.inputs["Roughness"].default_value = 0.5

# Create White Material
white_material = bpy.data.materials.new(name="White_Handle")
white_material.use_nodes = True
bsdf = white_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # White
bsdf.inputs["Roughness"].default_value = 0.3

# Assign Materials
mug_body.data.materials.append(red_material)
mug_handle.data.materials.append(white_material)

# --- Add a Light and Camera for context (optional but helpful) ---
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
bpy.ops.object.camera_add(location=(3, -5, 3))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Red mug with white handle created.")
