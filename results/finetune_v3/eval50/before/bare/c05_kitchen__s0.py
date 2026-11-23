import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Helper function to create a cube
def create_cube(name, location, scale, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    # Create material
    mat = bpy.data.materials.new(name=name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.5
    obj.data.materials.append(mat)
    return obj

# Helper function to create a cylinder
def create_cylinder(name, location, radius, depth, color):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.3
    obj.data.materials.append(mat)
    return obj

# Floor
floor = create_cube("Floor", (0, 0, 0), (10, 8, 0.1), (0.7, 0.6, 0.5, 1))

# Counter (main kitchen counter)
counter = create_cube("Counter", (0, -3, 1), (6, 1, 2), (0.8, 0.8, 0.8, 1))

# Counter top
counter_top = create_cube("CounterTop", (0, -3, 2.05), (6.2, 1.2, 0.1), (0.3, 0.3, 0.3, 1))

# Sink (basin in the counter)
sink = create_cube("Sink", (1.5, -3, 1.8), (1, 0.6, 0.3), (0.6, 0.6, 0.6, 1))
# Sink basin (inner)
sink_basin = create_cube("SinkBasin", (1.5, -3, 1.7), (0.9, 0.5, 0.25), (0.4, 0.4, 0.4, 1))

# Faucet
faucet_base = create_cylinder("FaucetBase", (1.5, -3.5, 2.2), 0.05, 0.4, (0.8, 0.8, 0.8, 1))
faucet_arm = create_cube("FaucetArm", (1.5, -3.35, 2.4), (0.05, 0.3, 0.05), (0.8, 0.8, 0.8, 1))

# Stove
stove = create_cube("Stove", (-1.5, -3, 1), (1.5, 1, 2), (0.2, 0.2, 0.2, 1))
# Stove top
stove_top = create_cube("StoveTop", (-1.5, -3, 2.05), (1.6, 1.1, 0.05), (0.1, 0.1, 0.1, 1))

# Burners (4 burners)
burner_positions = [(-2, -3.3), (-1, -3.3), (-2, -2.7), (-1, -2.7)]
for i, pos in enumerate(burner_positions):
    burner = create_cylinder(f"Burner{i}", (pos[0], pos[1], 2.1), 0.2, 0.02, (0.05, 0.05, 0.05, 1))

# Oven door
oven_door = create_cube("OvenDoor", (-1.5, -2.45, 1.2), (1.3, 0.05, 0.8), (0.3, 0.3, 0.3, 1))
# Oven handle
oven_handle = create_cube("OvenHandle", (-1.5, -2.4, 1.6), (1.0, 0.03, 0.05), (0.7, 0.7, 0.7, 1))

# Fridge
fridge = create_cube("Fridge", (5, -3, 1.5), (1.2, 1.5, 3), (0.7, 0.7, 0.7, 1))
# Fridge door line
fridge_line = create_cube("FridgeLine", (5, -2.25, 1.5), (1.22, 0.02, 3.02), (0.5, 0.5, 0.5, 1))
# Fridge handle
fridge_handle = create_cube("FridgeHandle", (4.4, -2.3, 2), (0.05, 0.05, 1), (0.3, 0.3, 0.3, 1))

# Stool 1
stool1_legs = [
    create_cylinder("Stool1Leg1", (-3, -1.5, 0.5), 0.05, 1, (0.4, 0.3, 0.2, 1)),
    create_cylinder("Stool1Leg2", (-2.5, -1.5, 0.5), 0.05, 1, (0.4, 0.3, 0.2, 1)),
    create_cylinder("Stool1Leg3", (-3, -1, 0.5), 0.05, 1, (0.4, 0.3, 0.2, 1)),
    create_cylinder("Stool1Leg4", (-2.5, -1, 0.5), 0.05, 1, (0.4, 0.3, 0.2, 1)),
]
stool1_seat = create_cylinder("Stool1Seat", (-2.75, -1.25, 1.05), 0.4, 0.1, (0.5, 0.4, 0.3, 1))

# Stool 2
stool2_legs = [
    create_cylinder("Stool2Leg1", (-3, 1, 0.5), 0.05, 1, (0.4, 0.3, 0.2, 1)),
    create_cylinder("Stool2Leg2", (-2.5, 1, 0.5), 0.05, 1, (0.4, 0.3, 0.2, 1)),
    create_cylinder("Stool2Leg3", (-3, 1.5, 0.5), 0.05, 1, (0.4, 0.3, 0.2, 1)),
    create_cylinder("Stool2Leg4", (-2.5, 1.5, 0.5), 0.05, 1, (0.4, 0.3, 0.2, 1)),
]
stool2_seat = create_cylinder("Stool2Seat", (-2.75, 1.25, 1.05), 0.4, 0.1, (0.5, 0.4, 0.3, 1))

# Add a light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 5))
light = bpy.context.active_object
light.name = "KitchenLight"
light.data.energy = 500

# Add camera
bpy.ops.object.camera_add(location=(0, 5, 3), rotation=(math.radians(70), 0, 0))
camera = bpy.context.active_object
camera.name = "KitchenCamera"
bpy.context.scene.camera = camera
