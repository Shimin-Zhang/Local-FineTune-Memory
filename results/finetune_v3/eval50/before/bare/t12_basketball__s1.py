import bpy
import math
import mathutils
from mathutils import Vector, noise

# Clean up scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create basketball base mesh (UV sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=128, ring_count=64)
ball = bpy.context.active_object
ball.name = "Basketball"

# Subdivide for more detail
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=2)
bpy.ops.object.mode_set(mode='OBJECT')

# Apply smooth shading
bpy.ops.object.shade_smooth()

# Create material
mat = bpy.data.materials.new(name="BasketballMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
tex_coord = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeMapping')
noise_node = nodes.new('ShaderNodeTexNoise')
bump_node = nodes.new('ShaderNodeBump')
principled = nodes.new('ShaderNodeBsdfPrincipled')
output = nodes.new('ShaderNodeOutputMaterial')

# Set noise for pebbled surface
noise_node.inputs['Scale'].default_value = 150.0
noise_node.inputs['Detail'].default_value = 8.0
noise_node.inputs['Roughness'].default_value = 0.7
noise_node.inputs['Lacunarity'].default_value = 2.0

# Bump for pebble texture
bump_node.inputs['Strength'].default_value = 0.05
bump_node.inputs['Distance'].default_value = 0.005

# Principled BSDF settings
principled.inputs['Base Color'].default_value = (0.75, 0.25, 0.05, 1.0)  # Orange
principled.inputs['Roughness'].default_value = 0.6
principled.inputs['Metallic'].default_value = 0.0

# Link nodes
links.new(tex_coord.outputs['Normal'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_node.inputs['Vector'])
links.new(noise_node.outputs['Fac'], bump_node.inputs['Height'])
links.new(bump_node.outputs['Normal'], principled.inputs['Normal'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to ball
ball.data.materials.append(mat)

# Now create the black lines using a separate mesh approach
# We'll use a shader trick: create line geometry as separate objects or use a procedural approach

# Better approach: Create the line pattern using a second material with procedural lines
# Let's create a node-based approach for the lines

# Add line pattern to the material using object coordinates
# We'll use a wave/checker pattern to simulate basketball lines

# Add a new texture for lines
line_noise = nodes.new('ShaderNodeTexNoise')
line_noise.inputs['Scale'].default_value = 1.0
line_noise.inputs['Detail'].default_value = 0.0

# Actually, let's use a different approach: create line meshes
# Basketball lines: 2 curved seams that form an X pattern + 2 straight-ish seams

# Create line curves
# Basketball has 4 main seams:
# 1. A horizontal great circle (equator)
# 2. Two curved lines that go from top to bottom, crossing at equator

# Let's create these as thin torus/curve objects

# Remove previous approach, use curve-based lines

# Create line 1: Equator (horizontal circle)
bpy.ops.curve.primitive_bezier_circle_add(radius=1.0, resolution=64)
eq_curve = bpy.context.active_object
eq_curve.name = "Line_Equator"
# Convert to mesh
bpy.ops.object.convert(target='MESH')
eq_mesh = bpy.context.active_object
# Make it thin
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(
    TRANSFORM_OT_translate={"value": (0, 0, 0.015), "orient_axis": 'Z', "orient_matrix": (1, 0, 0, 0, 1, 0, 0, 0, 1), "mirror": False, "proportional_edit": 'GLOBAL', "proportional_size": 1, "pivot_point": 'MEDIAN', "add": False, "use_accurate": False, "use_ambient_occlusion": False, "use_inverse_distance": False, "use_falloff": True, "use_clamp": True, "use_release": False}
)
bpy.ops.object.mode_set(mode='OBJECT')

# Actually, let's use a simpler approach: create thin torus rings for lines

# Delete the equator mesh we just made
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create lines as thin torus/curve objects

# Line 1: Equator
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.0, minor_radius=0.012,
    major_segments=128, minor_segments=8,
    rotation=(0, 0, 0)
)
line1 = bpy.context.active_object
line1.name = "Line_Equator"

# Line 2: Vertical seam (meridian)
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.0, minor_radius=0.012,
    major_segments=128, minor_segments=8,
    rotation=(0, math.radians(90), 0)
)
line2 = bpy.context.active_object
line2.name = "Line_Meridian1"

# Line 3: Another meridian at 90 degrees
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.0, minor_radius=0.012,
    major_segments=128, minor_segments=8,
    rotation=(math.radians(90), 0, 0)
)
line3 = bpy.context.active_object
line3.name = "Line_Meridian2"

# Basketball actually has specific curved seams, not just great circles
# Let's create the proper basketball seam pattern

# Delete the simple torus lines
for obj in [line1, line2, line3]:
    bpy.data.objects.remove(obj, do_unlink=True)

# Create proper basketball seams using curves
# Basketball seams: 
# - One great circle (let's say around Y axis)
# - Two symmetric curved seams that go from North pole to South pole

# Create seam 1: Great circle around Y axis (in XZ plane)
bpy.ops.curve.primitive_bezier_circle_add(radius=1.0, resolution=64)
seam1 = bpy.context.active_object
seam1.name = "Seam_GreatCircle"
# Rotate to be in XZ plane
seam1.rotation_euler = (0, 0, 0)
# Convert to mesh and give thickness
bpy.ops.object.convert(target='MESH')
seam1_mesh = bpy.context.active_object

# Create a bevel for the curve to make it a tube
# Actually, let's set bevel before converting
bpy.data.objects.remove(seam1_mesh, do_unlink=True)

# Better: create curves with bevel depth
bpy.ops.curve.primitive_bezier_circle_add(radius=1.0, resolution=64)
seam1 = bpy.context.active_object
seam1.name = "Seam1"
seam1.data.bevel_depth = 0.012
seam1.data.bevel_resolution = 4
seam1.data.use_fill_caps = True

# Seam 2: Curved seam from top to bottom
# Create a Bezier curve that goes from (0, 0, 1) to (0, 0, -1) with a curve
bpy.ops.curve.primitive_bezier_circle_add(radius=1.0, resolution=64)
seam2 = bpy.context.active_object
seam2.name = "Seam2"
# We need to reshape this into a curved path
# Let's delete and create manually

bpy.data.objects.remove(seam2, do_unlink=True)

# Create custom curve for curved seam
curve_data = bpy.data.curves.new(name="Seam2Curve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.012
curve_data.bevel_resolution = 4
curve_data.use_fill_caps = True

spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(2)  # 3 points total

# North pole
spline.bezier_points[0].co = (0, 0, 1)
spline.bezier_points[0].handle_left = (0, 0.1, 0.9)
spline.bezier_points[0].handle_right = (0, 0.1, 0.9)

# Middle (curved out)
spline.bezier_points[1].co = (0.3, 0, 0)
spline.bezier_points[1].handle_left = (0.1, 0, 0.3)
spline.bezier_points[1].handle_right = (0.5, 0, -0.3)

# South pole
spline.bezier_points[2].co = (0, 0, -1)
spline.bezier_points[2].handle_left = (0, -0.1, -0.9)
spline.bezier_points[2].handle_right = (0, -0.1, -0.9)

seam2_obj = bpy.data.objects.new(name="Seam2", object=curve_data)
bpy.context.collection.objects.link(seam2_obj)

# Seam 3: Mirror of seam 2
curve_data3 = bpy.data.curves.new(name="Seam3Curve", type='CURVE')
curve_data3.dimensions = '3D'
curve_data3.bevel_depth = 0.012
curve_data3.bevel_resolution = 4
curve_data3.use_fill_caps = True

spline3 = curve_data3.splines.new('BEZIER')
spline3.bezier_points.add(2)

spline3.bezier_points[0].co = (0, 0, 1)
spline3.bezier_points[0].handle_left = (0, -0.1, 0.9)
spline3.bezier_points[0].handle_right = (0, -0.1, 0.9)

spline3.bezier_points[1].co = (-0.3, 0, 0)
spline3.bezier_points[1].handle_left = (-0.1, 0, 0.3)
spline3.bezier_points[1].handle_right = (-0.5, 0, -0.3)

spline3.bezier_points[2].co = (0, 0, -1)
spline3.bezier_points[2].handle_left = (0, 0.1, -0.9)
spline3.bezier_points[2].handle_right = (0, 0.1, -0.9)

seam3_obj = bpy.data.objects.new(name="Seam3", object=curve_data3)
bpy.context.collection.objects.link(seam3_obj)

# Create black material for lines
black_mat = bpy.data.materials.new(name="BlackLineMaterial")
black_mat.use_nodes = True
nodes_b = black_mat.node_tree.nodes
links_b = black_mat.node_tree.links

for node in nodes_b:
    nodes_b.remove(node)

principled_b = nodes_b.new('ShaderNodeBsdfPrincipled')
output_b = nodes_b.new('ShaderNodeOutputMaterial')

principled_b.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
principled_b.inputs['Roughness'].default_value = 0.5

links_b.new(principled_b.outputs['BSDF'], output_b.inputs['Surface'])

# Assign black material to all seam objects
for obj in [seam1, seam2_obj, seam3_obj]:
    obj.data.materials.clear()
    obj.data.materials.append(black_mat)

# Make sure ball is on top / properly scaled
ball.location = (0, 0, 0)

# Set up camera and light for better view
# Add a light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
sun = bpy.context.active_object
sun.rotation_euler = (math.radians(45), math.radians(30), 0)
sun.data.energy = 3.0

# Add a camera
bpy.ops.object.camera_add(location=(0, -4, 1))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(75), 0, 0)
bpy.context.scene.camera = cam

# Set world background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)
    bg_node.inputs[1].default_value = 1.0
