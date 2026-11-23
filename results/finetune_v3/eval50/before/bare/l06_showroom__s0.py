import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a simple sports car from primitives (stylized)
# Body
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
body = bpy.context.active_object
body.scale = (1.8, 0.9, 0.4)
body.name = "CarBody"

# Cabin
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.95))
cabin = bpy.context.active_object
cabin.scale = (1.0, 0.7, 0.3)
cabin.name = "CarCabin"

# Wheels (4 cylinders)
wheel_positions = [
    (-1.2, -0.7, 0.3),
    (-1.2, 0.7, 0.3),
    (1.2, -0.7, 0.3),
    (1.2, 0.7, 0.3),
]
for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=pos, rotation=(0, math.pi/2, 0))
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i}"

# Materials
# Red car paint
mat_red = bpy.data.materials.new("RedPaint")
mat_red.use_nodes = True
bsdf = mat_red.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.05, 0.05, 1.0)
bsdf.inputs["Metallic"].default_value = 0.8
bsdf.inputs["Roughness"].default_value = 0.1

# Apply red paint to body and cabin
for obj in [body, cabin]:
    obj.data.materials.append(mat_red)

# Wheel material (dark rubber)
mat_wheel = bpy.data.materials.new("WheelRubber")
mat_wheel.use_nodes = True
bsdf_w = mat_wheel.node_tree.nodes["Principled BSDF"]
bsdf_w.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
bsdf_w.inputs["Roughness"].default_value = 0.6
for i in range(4):
    obj = bpy.data.objects.get(f"Wheel_{i}")
    if obj:
        obj.data.materials.append(mat_wheel)

# Glossy floor
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "GlossyFloor"
mat_floor = bpy.data.materials.new("GlossyFloorMat")
mat_floor.use_nodes = True
bsdf_f = mat_floor.node_tree.nodes["Principled BSDF"]
bsdf_f.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
bsdf_f.inputs["Metallic"].default_value = 0.3
bsdf_f.inputs["Roughness"].default_value = 0.05
floor.data.materials.append(mat_floor)

# Showroom lighting: long soft area lights overhead
# Two long area lights running along the car
for i, y_offset in enumerate([-1.5, 1.5]):
    bpy.ops.object.light_add(type='AREA', location=(0, y_offset, 3.0))
    light = bpy.context.active_object
    light.name = f"ShowroomLight_{i}"
    light.data.shape = 'RECTANGLE'
    light.data.size = 6.0   # long along X
    light.data.size_y = 0.8 # narrow along Y
    light.data.energy = 500
    light.data.color = (1.0, 1.0, 1.0)
    light.rotation_euler = (0, 0, 0)

# Additional fill light from front
bpy.ops.object.light_add(type='AREA', location=(0, 5, 2.0))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.shape = 'RECTANGLE'
fill.data.size = 4.0
fill.data.size_y = 2.0
fill.data.energy = 200
fill.data.color = (1.0, 0.98, 0.95)
fill.rotation_euler = (math.radians(30), 0, 0)

# Camera
bpy.ops.object.camera_add(location=(4, 4, 1.5), rotation=(math.radians(70), 0, math.radians(45)))
cam = bpy.context.active_object
cam.name = "ShowroomCam"
bpy.context.scene.camera = cam

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
