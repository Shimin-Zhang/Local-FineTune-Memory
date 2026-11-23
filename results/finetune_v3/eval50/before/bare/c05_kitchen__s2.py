import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_mat(name, color, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

mat_counter = make_mat("Counter", (0.7, 0.7, 0.7, 1), 0.3)
mat_cabinet = make_mat("Cabinet", (0.85, 0.8, 0.7, 1), 0.6)
mat_sink = make_mat("Sink", (0.9, 0.9, 0.9, 1), 0.1)
mat_stove = make_mat("Stove", (0.1, 0.1, 0.1, 1), 0.2)
mat_burner = make_mat("Burner", (0.05, 0.05, 0.05, 1), 0.1)
mat_fridge = make_mat("Fridge", (0.85, 0.85, 0.88, 1), 0.15)
mat_stool_seat = make_mat("StoolSeat", (0.6, 0.4, 0.2, 1), 0.5)
mat_stool_leg = make_mat("StoolLeg", (0.3, 0.3, 0.3, 1), 0.4)
mat_floor = make_mat("Floor", (0.6, 0.55, 0.5, 1), 0.7)

# Floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Floor"
floor.data.materials.append(mat_floor)

# Counter (L-shape or straight run along back wall)
# Base cabinet
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.5, 0.45))
cabinet = bpy.context.object
cabinet.name = "Counter_Cabinet"
cabinet.scale = (2.0, 0.6, 0.45)
cabinet.data.materials.append(mat_cabinet)

# Counter top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.5, 0.925))
top = bpy.context.object
top.name = "Counter_Top"
top.scale = (2.1, 0.65, 0.05)
top.data.materials.append(mat_counter)

# Sink (basin) - inset into counter
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5, -1.5, 0.9))
sink = bpy.context.object
sink.name = "Sink_Basin"
sink.scale = (0.4, 0.35, 0.08)
sink.data.materials.append(mat_sink)

# Sink faucet
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.3, location=(-0.5, -1.35, 1.05))
faucet = bpy.context.object
faucet.name = "Sink_Faucet"
faucet.data.materials.append(mat_sink)
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.15, location=(-0.5, -1.42, 1.2), rotation=(math.radians(90), 0, 0))
faucet_spout = bpy.context.object
faucet_spout.name = "Sink_Faucet_Spout"
faucet_spout.data.materials.append(mat_sink)

# Stove
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.8, -1.5, 0.45))
stove_base = bpy.context.object
stove_base.name = "Stove_Base"
stove_base.scale = (0.6, 0.6, 0.45)
stove_base.data.materials.append(mat_stove)

# Stove top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.8, -1.5, 0.925))
stove_top = bpy.context.object
stove_top.name = "Stove_Top"
stove_top.scale = (0.65, 0.65, 0.05)
stove_top.data.materials.append(mat_stove)

# Burners (4)
burner_positions = [
    (0.65, -1.35),
    (0.95, -1.35),
    (0.65, -1.65),
    (0.95, -1.65)
]
for i, (bx, by) in enumerate(burner_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.01, location=(bx, by, 0.955))
    burner = bpy.context.object
    burner.name = f"Burner_{i}"
    burner.data.materials.append(mat_burner)

# Fridge
bpy.ops.mesh.primitive_cube_add(size=1, location=(2.5, -1.5, 1.0))
fridge = bpy.context.object
fridge.name = "Fridge"
fridge.scale = (0.7, 0.7, 1.0)
fridge.data.materials.append(mat_fridge)

# Fridge handle
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.4, location=(2.15, -1.5, 1.0), rotation=(0, math.radians(90), 0))
handle = bpy.context.object
handle.name = "Fridge_Handle"
handle.data.materials.append(mat_sink)

# Two stools
def create_stool(x, y, name):
    # Seat
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.05, location=(x, y, 0.65))
    seat = bpy.context.object
    seat.name = f"{name}_Seat"
    seat.data.materials.append(mat_stool_seat)
    # Leg
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.65, location=(x, y, 0.325))
    leg = bpy.context.object
    leg.name = f"{name}_Leg"
    leg.data.materials.append(mat_stool_leg)
    # Foot ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.01, location=(x, y, 0.2))
    ring = bpy.context.object
    ring.name = f"{name}_Ring"
    ring.data.materials.append(mat_stool_leg)

create_stool(-0.5, -0.5, "Stool1")
create_stool(0.5, -0.5, "Stool2")

# Add a light
bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
sun = bpy.context.object
sun.name = "Kitchen_Light"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(20), 0)

# Camera
bpy.ops.object.camera_add(location=(0, 2, 1.8))
cam = bpy.context.object
cam.name = "Kitchen_Camera"
cam.rotation_euler = (math.radians(70), 0, 0)
bpy.context.scene.camera = cam

print("Kitchen scene built successfully.")
