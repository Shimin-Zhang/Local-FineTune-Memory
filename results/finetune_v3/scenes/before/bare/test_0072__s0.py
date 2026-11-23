import bpy
import math
import random
from mathutils import Vector, noise

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# --- MATERIALS ---
# Dark varnished rock material
mat_rock = bpy.data.materials.new(name="VarnishedRock")
mat_rock.use_nodes = True
nodes = mat_rock.node_tree.nodes
links = mat_rock.node_tree.links
nodes.clear()

out = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
tex_coord = nodes.new('ShaderNodeTexCoord')
noise1 = nodes.new('ShaderNodeTexNoise')
noise2 = nodes.new('ShaderNodeTexNoise')
ramp = nodes.new('ShaderNodeValToRGB')
bump = nodes.new('ShaderNodeBump')

links.new(tex_coord.outputs['Object'], noise1.inputs['Vector'])
links.new(tex_coord.outputs['Object'], noise2.inputs['Vector'])
noise1.inputs['Scale'].default_value = 8.0
noise1.inputs['Detail'].default_value = 10.0
noise2.inputs['Scale'].default_value = 20.0
noise2.inputs['Detail'].default_value = 15.0

links.new(noise1.outputs['Fac'], ramp.inputs['Fac'])
ramp.color_ramp.elements[0].position = 0.3
ramp.color_ramp.elements[0].color = (0.05, 0.04, 0.03, 1.0)  # Dark varnish
ramp.color_ramp.elements[1].position = 0.7
ramp.color_ramp.elements[1].color = (0.15, 0.12, 0.08, 1.0)  # Lighter rock

links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Metallic'].default_value = 0.0

links.new(noise2.outputs['Fac'], bump.inputs['Height'])
bump.inputs['Strength'].default_value = 0.5
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

# Petroglyph material (slightly lighter, carved look)
mat_petroglyph = bpy.data.materials.new(name="Petroglyph")
mat_petroglyph.use_nodes = True
nodes = mat_petroglyph.node_tree.nodes
links = mat_petroglyph.node_tree.links
nodes.clear()
out = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.25, 0.22, 0.18, 1.0)
bsdf.inputs['Roughness'].default_value = 0.9
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

# Dry wash material (sandy/rocky)
mat_wash = bpy.data.materials.new(name="DryWash")
mat_wash.use_nodes = True
nodes = mat_wash.node_tree.nodes
links = mat_wash.node_tree.links
nodes.clear()
out = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
tex_coord = nodes.new('ShaderNodeTexCoord')
noise = nodes.new('ShaderNodeTexNoise')
ramp = nodes.new('ShaderNodeValToRGB')
links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
noise.inputs['Scale'].default_value = 15.0
noise.inputs['Detail'].default_value = 8.0
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
ramp.color_ramp.elements[0].position = 0.2
ramp.color_ramp.elements[0].color = (0.45, 0.38, 0.28, 1.0)  # Sand
ramp.color_ramp.elements[1].position = 0.8
ramp.color_ramp.elements[1].color = (0.35, 0.30, 0.22, 1.0)  # Rocky
links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.95
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

# --- ROCK WALL ---
# Create a large rock wall using a subdivided plane with displacement
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 5))
wall = bpy.context.active_object
wall.name = "RockWall"
wall.scale = (8, 0.5, 6)  # Wide, thin, tall
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Subdivide for displacement
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=40)
bpy.ops.object.mode_set(mode='OBJECT')

# Add displacement modifier
disp = wall.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 1.5
disp.mid_level = 0.5
disp.direction = 'Y'

# Apply displacement
bpy.ops.object.modifier_apply(modifier="Displacement")

# Assign rock material
wall.data.materials.append(mat_rock)

# --- PETROGLYPHS ---
# Function to create spiral petroglyph
def create_spiral(name, location, scale=0.3, segments=200):
    bpy.ops.mesh.primitive_torus_add(major_radius=scale, minor_radius=scale*0.05, location=location, major_segments=segments, minor_segments=8)
    spiral = bpy.context.active_object
    spiral.name = name
    # Deform into spiral shape
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # Flatten and scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    # Scale to be flat
    spiral.scale = (1, 1, 0.1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    spiral.data.materials.append(mat_petroglyph)
    return spiral

# Function to create sheep petroglyph (simple silhouette)
def create_sheep(name, location, scale=0.4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    sheep = bpy.context.active_object
    sheep.name = name
    sheep.scale = (scale*1.5, scale*0.5, scale)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Add legs
    for i, (x, z) in enumerate([(-0.3, -0.4), (0.3, -0.4), (-0.3, 0.4), (0.3, 0.4)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=scale*0.08, depth=scale*0.5, location=(location[0]+x*scale, location[1], location[2]+z*scale-0.3))
        leg = bpy.context.active_object
        leg.select_set(True)
    sheep.select_set(True)
    bpy.context.view_layer.objects.active = sheep
    bpy.ops.object.join()
    sheep.data.materials.append(mat_petroglyph)
    return sheep

# Function to create hunter petroglyph (simple figure with spear)
def create_hunter(name, location, scale=0.5):
    bpy.ops.mesh.primitive_cylinder_add(radius=scale*0.1, depth=scale*1.2, location=location)
    hunter = bpy.context.active_object
    hunter.name = name
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=scale*0.15, location=(location[0], location[1], location[2]+scale*0.7))
    head = bpy.context.active_object
    # Spear
    bpy.ops.mesh.primitive_cylinder_add(radius=scale*0.03, depth=scale*1.5, location=(location[0]+scale*0.3, location[1], location[2]+scale*0.5), rotation=(0, math.radians(30), 0))
    spear = bpy.context.active_object
    # Join
    hunter.select_set(True)
    head.select_set(True)
    spear.select_set(True)
    bpy.context.view_layer.objects.active = hunter
    bpy.ops.object.join()
    hunter.data.materials.append(mat_petroglyph)
    return hunter

# Place petroglyphs on the wall
# Spirals
create_spiral("Spiral1", (-3, 0.3, 4), scale=0.4)
create_spiral("Spiral2", (-1.5, 0.3, 3.5), scale=0.3)
create_spiral("Spiral3", (2, 0.3, 4.5), scale=0.35)
create_spiral("Spiral4", (3.5, 0.3, 3), scale=0.25)

# Sheep
create_sheep("Sheep1", (-2.5, 0.3, 2), scale=0.5)
create_sheep("Sheep2", (-0.5, 0.3, 2.5), scale=0.45)
create_sheep("Sheep3", (1, 0.3, 2), scale=0.5)

# Hunters
create_hunter("Hunter1", (2.5, 0.3, 1.5), scale=0.6)
create_hunter("Hunter2", (4, 0.3, 2), scale=0.55)

# --- TRAIL ---
# Create a winding trail path
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 1, 0.1))
trail = bpy.context.active_object
trail.name = "Trail"
trail.scale = (0.5, 3, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Subdivide and deform
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')

# Create a curve for the trail
curve_data = bpy.data.curves.new(name="TrailCurve", type='CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(4)
points = [
    (0, 1, 0.1),
    (-1, 2, 0.1),
    (0.5, 3, 0.1),
    (-0.5, 4, 0.1),
    (0, 5, 0.1)
]
for i, pt in enumerate(points):
    spline.bezier_points[i].co = pt
    spline.bezier_points[i].handle_left_type = 'AUTO'
    spline.bezier_points[i].handle_right_type = 'AUTO'

trail_obj = bpy.data.objects.new(name="TrailPath", object=curve_data)
bpy.context.collection.objects.link(trail_obj)

# Convert trail to mesh and flatten
bpy.context.view_layer.objects.active = trail_obj
trail_obj.select_set(True)
bpy.ops.object.convert(target='MESH')
trail_obj = bpy.context.active_object
trail_obj.scale = (1, 1, 0.05)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
trail_obj.data.materials.append(mat_wash)

# --- SMALL FENCE ---
# Create a simple wooden fence
def create_fence_segment(name, location, length=2, height=0.8, posts=4):
    posts_list = []
    for i in range(posts):
        x = location[0] - length/2 + i * (length / (posts-1))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=height, location=(x, location[1], location[2]+height/2))
        post = bpy.context.active_object
        post.name = f"{name}_post_{i}"
        posts_list.append(post)
    
    # Horizontal rails
    for z_offset in [0.3, 0.6]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=length, location=(location[0], location[1], location[2]+z_offset), rotation=(0, math.radians(90), 0))
        rail = bpy.context.active_object
        rail.name = f"{name}_rail_{z_offset}"
        posts_list.append(rail)
    
    # Join all fence parts
    for obj in posts_list:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = posts_list[0]
    bpy.ops.object.join()
    fence = bpy.context.active_object
    fence.name = name
    
    # Create wood material
    mat_wood = bpy.data.materials.new(name="Wood")
    mat_wood.use_nodes = True
    nodes = mat_wood.node_tree.nodes
    links = mat_wood.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    fence.data.materials.append(mat_wood)
    return fence

create_fence_segment("Fence1", (-2, 1.5, 0), length=3, height=0.8, posts=4)
create_fence_segment("Fence2", (2, 1.5, 0), length=3, height=0.8, posts=4)

# --- DRY WASH ---
# Create a dry wash (wadi) below the wall
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 3, 0))
wash = bpy.context.active_object
wash.name = "DryWash"
wash.scale = (10, 2, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Subdivide and create a channel
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=30)
bpy.ops.object.mode_set(mode='OBJECT')

# Displace to create channel shape
disp = wash.modifiers.new(name="Channel", type='DISPLACE')
disp.strength = 0.5
disp.mid_level = 0.5
disp.direction = 'Z'
bpy.ops.object.modifier_apply(modifier="Channel")

# Flatten the center to create the wash
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
# Use proportional editing to flatten center
bpy.ops.object.mode_set(mode='OBJECT')
wash.scale = (1, 1, 0.3)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

wash.data.materials.append(mat_wash)

# --- LIGHTING ---
# Sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.data.color = (1.0, 0.95, 0.85)
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Ambient light
bpy.ops.object.light_add(type='AREA', location=(0, 0, 8))
area = bpy.context.active_object
area.name = "Ambient"
area.data.energy = 50
area.data.size = 10
area.rotation_euler = (0, 0, 0)

# --- CAMERA ---
bpy.ops.object.camera_add(location=(0, 8, 4))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (math.radians(75), 0, 0)
bpy.context.scene.camera = camera

# Set scene properties
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Scene created successfully")
