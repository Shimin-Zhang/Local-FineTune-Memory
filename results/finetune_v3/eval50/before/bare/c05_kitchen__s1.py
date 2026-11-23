import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a helper function to add a box
def add_box(name, location, scale, color=(0.8, 0.8, 0.8, 1.0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    # Add material
    mat = bpy.data.materials.new(name=name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    obj.data.materials.append(mat)
    return obj

# --- Counter (long L-shape or straight) ---
# Main counter body
counter_body = add_box("Counter_Body", (0, 0, 0.45), (3.0, 0.6, 0.9), color=(0.2, 0.2, 0.2, 1.0))
# Counter top (slightly larger)
counter_top = add_box("Counter_Top", (0, 0, 0.92), (3.1, 0.65, 0.04), color=(0.9, 0.9, 0.9, 1.0))

# --- Sink (recessed look: a box on top with a darker inset) ---
# Sink basin (slightly inset)
sink_basin = add_box("Sink_Basin", (1.0, 0, 0.94), (0.5, 0.4, 0.02), color=(0.3, 0.3, 0.3, 1.0))
# Sink rim
sink_rim = add_box("Sink_Rim", (1.0, 0, 0.96), (0.55, 0.45, 0.02), color=(0.6, 0.6, 0.6, 1.0))
# Faucet
faucet_base = add_box("Faucet_Base", (1.0, -0.25, 1.0), (0.05, 0.05, 0.1), color=(0.7, 0.7, 0.7, 1.0))
faucet_arm = add_box("Faucet_Arm", (1.0, -0.15, 1.05), (0.04, 0.2, 0.04), color=(0.7, 0.7, 0.7, 1.0))
faucet_spout = add_box("Faucet_Spout", (1.0, -0.05, 1.02), (0.04, 0.04, 0.06), color=(0.7, 0.7, 0.7, 1.0))

# --- Stove (on the counter) ---
stove_body = add_box("Stove_Body", (-1.0, 0, 0.95), (0.6, 0.5, 0.06), color=(0.1, 0.1, 0.1, 1.0))
# Burners (4 small cylinders)
for i, (x, y) in enumerate([(-1.2, 0.15), (-0.8, 0.15), (-1.2, -0.15), (-0.8, -0.15)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.02, location=(x, y, 0.99))
    burner = bpy.context.active_object
    burner.name = f"Burner_{i}"
    mat = bpy.data.materials.new(name=f"Burner_{i}_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
    burner.data.materials.append(mat)

# --- Fridge (tall box on the side) ---
fridge = add_box("Fridge", (2.5, 0, 1.1), (0.7, 0.7, 2.2), color=(0.85, 0.85, 0.85, 1.0))
# Fridge handle
handle = add_box("Fridge_Handle", (2.15, 0, 1.1), (0.03, 0.03, 0.8), color=(0.5, 0.5, 0.5, 1.0))

# --- Two Stools ---
def add_stool(name, location):
    # Seat
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.05, location=(location[0], location[1], 0.6))
    seat = bpy.context.active_object
    seat.name = name + "_Seat"
    mat = bpy.data.materials.new(name=name + "_Seat_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.6, 0.3, 0.1, 1.0)  # Wood color
    seat.data.materials.append(mat)
    
    # Leg (single central leg for simplicity)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.6, location=(location[0], location[1], 0.3))
    leg = bpy.context.active_object
    leg.name = name + "_Leg"
    mat = bpy.data.materials.new(name=name + "_Leg_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.4, 0.4, 0.4, 1.0)  # Metal
    leg.data.materials.append(mat)
    
    # Base
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.02, location=(location[0], location[1], 0.01))
    base = bpy.context.active_object
    base.name = name + "_Base"
    mat = bpy.data.materials.new(name=name + "_Base_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.4, 0.4, 0.4, 1.0)
    base.data.materials.append(mat)

# Place stools in front of the counter
add_stool("Stool_1", (0.5, 0.8, 0))
add_stool("Stool_2", (-0.5, 0.8, 0))

# Add a floor
floor = add_box("Floor", (0, 0, -0.01), (6, 4, 0.02), color=(0.7, 0.7, 0.7, 1.0))

# Add a back wall
wall = add_box("Back_Wall", (0, -1.0, 1.5), (6, 0.05, 3.0), color=(0.9, 0.9, 0.9, 1.0))

# Set up camera
bpy.ops.object.camera_add(location=(0, 5, 2))
camera = bpy.context.active_object
camera.name = "Kitchen_Camera"
bpy.context.scene.camera = camera
# Point camera at the kitchen
direction = (0, 0, 1) - camera.location
camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

# Add a light
bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
sun = bpy.context.active_object
sun.data.energy = 5
sun.rotation_euler = (0, 0, 0)

print("Kitchen scene built successfully!")
