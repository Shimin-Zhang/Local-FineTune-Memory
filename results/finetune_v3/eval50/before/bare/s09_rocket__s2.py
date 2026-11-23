import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 1. Create the rocket body (cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=4, location=(0, 0, 2))
body = bpy.context.active_object
body.name = "RocketBody"

# 2. Create the nose cone (cone)
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1, radius2=0, depth=2, location=(0, 0, 5))
nose = bpy.context.active_object
nose.name = "NoseCone"

# 3. Create the exhaust nozzle (cone, inverted)
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.6, radius2=0.3, depth=0.5, location=(0, 0, -0.25))
nozzle = bpy.context.active_object
nozzle.name = "Nozzle"

# 4. Create three fins
for i in range(3):
    angle = i * (2 * math.pi / 3)
    x = 1.0 * math.cos(angle)
    y = 1.0 * math.sin(angle)
    
    # Create a fin as a scaled and rotated plane/box
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.5))
    fin = bpy.context.active_object
    fin.name = f"Fin_{i+1}"
    
    # Scale the fin: thin in one direction, taller, and wider
    fin.scale = (0.1, 0.6, 1.5)
    
    # Rotate the fin to align radially
    fin.rotation_euler = (0, 0, angle)

# 5. Create the round window (a small cylinder embedded in the body)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.3, depth=0.1, location=(0, 1.0, 3))
window = bpy.context.active_object
window.name = "Window"
window.rotation_euler = (math.pi / 2, 0, 0)  # Rotate to face outward on the side

# 6. Create a window rim (slightly larger cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.35, depth=0.05, location=(0, 1.0, 3))
rim = bpy.context.active_object
rim.name = "WindowRim"
rim.rotation_euler = (math.pi / 2, 0, 0)

# Apply all transforms to clean up the mesh data
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

print("Rocket with three fins and a round window created successfully!")
