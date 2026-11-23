import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a material for the duck
mat = bpy.data.materials.new(name="YellowRubber")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (1.0, 0.85, 0.0, 1.0)  # Yellow
bsdf.inputs["Roughness"].default_value = 0.4
bsdf.inputs["Specular IOR Level"].default_value = 0.5

# Helper function to create a UV sphere and apply material
def create_sphere(name, radius, location, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=32, ring_count=16)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj

# Body (large sphere)
body = create_sphere("DuckBody", 1.0, (0, 0, 0), scale=(1.2, 1.0, 1.0))

# Head (smaller sphere on top)
head = create_sphere("DuckHead", 0.6, (0, 0.9, 0.8), scale=(1.0, 1.0, 1.0))

# Beak (cone or flattened sphere)
bpy.ops.mesh.primitive_cone_add(radius1=0.25, radius2=0.05, depth=0.5, location=(0, 1.4, 0.75), rotation=(math.radians(-90), 0, 0))
beak = bpy.context.active_object
beak.name = "DuckBeak"
beak.scale = (1.0, 1.0, 0.6)
beak.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Eyes (two small dark spheres)
eye_mat = bpy.data.materials.new(name="EyeBlack")
eye_mat.use_nodes = True
eye_nodes = eye_mat.node_tree.nodes
eye_bsdf = eye_nodes.get("Principled BSDF")
eye_bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
eye_bsdf.inputs["Roughness"].default_value = 0.3

for x in [-0.25, 0.25]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(x, 1.25, 0.95), segments=16, ring_count=8)
    eye = bpy.context.active_object
    eye.name = f"DuckEye_{x}"
    eye.data.materials.append(eye_mat)
    bpy.ops.object.shade_smooth()

# Wings (flattened spheres on sides)
for x in [-1.0, 1.0]:
    wing = create_sphere(f"DuckWing_{x}", 0.5, (x, -0.2, 0.2), scale=(0.5, 1.2, 0.8))

# Tail (small sphere at back)
tail = create_sphere("DuckTail", 0.3, (0, -1.0, 0.3), scale=(0.8, 1.0, 0.6))

# Set up a simple camera and light for viewing
bpy.ops.object.camera_add(location=(0, -4, 2), rotation=(math.radians(70), 0, 0))
cam = bpy.context.active_object
cam.name = "DuckCamera"
bpy.context.scene.camera = cam

bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
sun = bpy.context.active_object
sun.name = "DuckLight"
sun.data.energy = 3.0

# Set viewport to look at the duck
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                space.region_3d.view_location = (0, 0, 0)
                space.region_3d.view_distance = 6
                space.region_3d.view_rotation = (0.7071, 0.7071, 0, 0)
