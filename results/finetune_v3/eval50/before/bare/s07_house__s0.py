import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
# Wall material
wall_mat = bpy.data.materials.new("Wall")
wall_mat.use_nodes = True
bsdf = wall_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.85, 0.75, 1.0)

# Roof material (red)
roof_mat = bpy.data.materials.new("Roof")
roof_mat.use_nodes = True
bsdf = roof_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1.0)

# Door material (brown)
door_mat = bpy.data.materials.new("Door")
door_mat.use_nodes = True
bsdf = door_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.35, 0.18, 0.08, 1.0)

# Window material
window_mat = bpy.data.materials.new("Window")
window_mat.use_nodes = True
bsdf = window_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.6, 0.8, 0.9, 1.0)
bsdf.inputs["Roughness"].default_value = 0.1

# --- House Body ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1))
house = bpy.context.active_object
house.scale = (2, 1.5, 1)
house.data.materials.append(wall_mat)
bpy.ops.object.transform_apply(scale=True)

# --- Roof (triangular prism) ---
# Create a custom mesh for the roof
roof_verts = [
    (-2.2, -1.7, 2.0),   # front left bottom
    (2.2, -1.7, 2.0),    # front right bottom
    (0, -1.7, 3.2),      # front peak
    (-2.2, 1.7, 2.0),    # back left bottom
    (2.2, 1.7, 2.0),     # back right bottom
    (0, 1.7, 3.2),       # back peak
]
roof_faces = [
    (0, 1, 2),           # front triangle
    (3, 5, 4),           # back triangle
    (0, 2, 5, 3),        # left slope
    (1, 4, 5, 2),        # right slope
    (0, 3, 4, 1),        # bottom (hidden)
]
roof_mesh = bpy.data.meshes.new("RoofMesh")
roof_mesh.from_pydata(roof_verts, [], roof_faces)
roof_obj = bpy.data.objects.new("Roof", roof_mesh)
bpy.context.collection.objects.link(roof_obj)
roof_obj.data.materials.append(roof_mat)

# --- Door ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.51, 0.5))
door = bpy.context.active_object
door.scale = (0.4, 0.02, 0.5)
door.data.materials.append(door_mat)
bpy.ops.object.transform_apply(scale=True)

# --- Windows ---
# Left window
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.8, -1.51, 1.0))
win_left = bpy.context.active_object
win_left.scale = (0.3, 0.02, 0.3)
win_left.data.materials.append(window_mat)
bpy.ops.object.transform_apply(scale=True)

# Right window
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.8, -1.51, 1.0))
win_right = bpy.context.active_object
win_right.scale = (0.3, 0.02, 0.3)
win_right.data.materials.append(window_mat)
bpy.ops.object.transform_apply(scale=True)

# --- Ground plane ---
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = bpy.data.materials.new("Ground")
ground_mat.use_nodes = True
bsdf = ground_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.3, 0.5, 0.2, 1.0)
ground.data.materials.append(ground_mat)

# --- Camera & Light ---
# Camera
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (4, -5, 3)
cam.rotation_euler = (math.radians(70), 0, math.radians(30))
bpy.context.scene.camera = cam

# Light
light_data = bpy.data.lights.new("Light", type='SUN')
light_data.energy = 3
light = bpy.data.objects.new("Light", light_data)
bpy.context.collection.objects.link(light)
light.location = (5, -5, 10)
light.rotation_euler = (math.radians(45), 0, math.radians(45))
