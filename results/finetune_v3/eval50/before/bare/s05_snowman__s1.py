import bpy
import math
import mathutils

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
# White snow material
mat_snow = bpy.data.materials.new("Snow")
mat_snow.use_nodes = True
nodes = mat_snow.node_tree.nodes
links = mat_snow.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.97, 1.0)
bsdf.inputs["Roughness"].default_value = 0.6

# Black hat material
mat_hat = bpy.data.materials.new("BlackHat")
mat_hat.use_nodes = True
nodes = mat_hat.node_tree.nodes
links = mat_hat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf.inputs["Roughness"].default_value = 0.4

# Orange carrot material
mat_carrot = bpy.data.materials.new("Carrot")
mat_carrot.use_nodes = True
nodes = mat_carrot.node_tree.nodes
links = mat_carrot.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 0.4, 0.0, 1.0)
bsdf.inputs["Roughness"].default_value = 0.5

# --- Snowman Body (two spheres) ---
# Lower body
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1.0), segments=32, ring_count=16)
lower_body = bpy.context.active_object
lower_body.name = "Snowman_Bottom"
lower_body.data.materials.append(mat_snow)
bpy.ops.object.shade_smooth()

# Upper body
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(0, 0, 2.1), segments=32, ring_count=16)
upper_body = bpy.context.active_object
upper_body.name = "Snowman_Top"
upper_body.data.materials.append(mat_snow)
bpy.ops.object.shade_smooth()

# --- Black Top Hat ---
# Hat brim (flat cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.05, location=(0, 0, 2.75), vertices=32)
hat_brim = bpy.context.active_object
hat_brim.name = "Hat_Brim"
hat_brim.data.materials.append(mat_hat)
bpy.ops.object.shade_smooth()

# Hat crown (taller cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(0, 0, 3.05), vertices=32)
hat_crown = bpy.context.active_object
hat_crown.name = "Hat_Crown"
hat_crown.data.materials.append(mat_hat)
bpy.ops.object.shade_smooth()

# --- Orange Carrot Nose ---
# Cone shape for the carrot
bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.0, depth=0.35, location=(0, 0.55, 2.1), vertices=16)
carrot = bpy.context.active_object
carrot.name = "Carrot_Nose"
carrot.rotation_euler = (math.radians(-90), 0, 0)  # Point forward (+Y)
carrot.data.materials.append(mat_carrot)
bpy.ops.object.shade_smooth()

# --- Eyes (small black spheres) ---
mat_eye = bpy.data.materials.new("Eye")
mat_eye.use_nodes = True
nodes = mat_eye.node_tree.nodes
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3

# Left eye
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(-0.15, 0.55, 2.25), segments=16, ring_count=8)
left_eye = bpy.context.active_object
left_eye.name = "Left_Eye"
left_eye.data.materials.append(mat_eye)
bpy.ops.object.shade_smooth()

# Right eye
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0.15, 0.55, 2.25), segments=16, ring_count=8)
right_eye = bpy.context.active_object
right_eye.name = "Right_Eye"
right_eye.data.materials.append(mat_eye)
bpy.ops.object.shade_smooth()

# --- Buttons on the upper body ---
for i, z in enumerate([1.9, 2.1, 2.3]):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(0, 0.63, z), segments=16, ring_count=8)
    btn = bpy.context.active_object
    btn.name = f"Button_{i+1}"
    btn.data.materials.append(mat_eye)
    bpy.ops.object.shade_smooth()

# --- Arms (cylinders) ---
mat_stick = bpy.data.materials.new("Stick")
mat_stick.use_nodes = True
nodes = mat_stick.node_tree.nodes
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.3, 0.15, 0.05, 1.0)
bsdf.inputs["Roughness"].default_value = 0.8

# Left arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.8, location=(-0.8, 0, 2.0), vertices=12)
left_arm = bpy.context.active_object
left_arm.name = "Left_Arm"
left_arm.rotation_euler = (0, math.radians(30), 0)
left_arm.data.materials.append(mat_stick)
bpy.ops.object.shade_smooth()

# Right arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.8, location=(0.8, 0, 2.0), vertices=12)
right_arm = bpy.context.active_object
right_arm.name = "Right_Arm"
right_arm.rotation_euler = (0, math.radians(-30), 0)
right_arm.data.materials.append(mat_stick)
bpy.ops.object.shade_smooth()

# Set viewport to look at the snowman
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        region_3d = area.spaces.active.region_3d
        region_3d.view_location = (0, 0, 2.0)
        region_3d.view_distance = 6
        region_3d.view_rotation = mathutils.Euler((math.radians(75), 0, 0)).to_quaternion()
