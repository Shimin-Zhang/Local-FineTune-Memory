import bpy
import math
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create white stage floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "StageFloor"

# Create white material for floor
floor_mat = bpy.data.materials.new(name="WhiteFloor")
floor_mat.use_nodes = True
bsdf = floor_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
bsdf.inputs["Roughness"].default_value = 0.5
floor.data.materials.append(floor_mat)

# Define spotlight positions and colors
spotlights = [
    {"name": "RedSpot", "location": (-2, -3, 5), "color": (1.0, 0.0, 0.0)},
    {"name": "GreenSpot", "location": (2, -3, 5), "color": (0.0, 1.0, 0.0)},
    {"name": "BlueSpot", "location": (0, -4, 5), "color": (0.0, 0.0, 1.0)},
]

for spot in spotlights:
    # Create spotlight
    bpy.ops.object.light_add(type='SPOT', location=spot["location"])
    light = bpy.context.active_object
    light.name = spot["name"]
    
    # Set light properties
    light.data.color = spot["color"]
    light.data.energy = 500  # Bright enough to see overlap
    light.data.spot_size = math.radians(60)  # Wide cone
    light.data.spot_blend = 0.5  # Soft edge
    
    # Aim the light down at the center of the floor
    target = Vector((0, 0, 0))
    direction = target - light.location
    light.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

print("Three colored spotlights (red, green, blue) created over a white stage floor.")
