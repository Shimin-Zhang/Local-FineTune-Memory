import bpy
import math
import random

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up scene
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 128

# Materials
def create_wood_material():
    mat = bpy.data.materials.new("Wood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.35, 0.2, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.7
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_mat_material():
    mat = bpy.data.materials.new("Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_hoop_material():
    mat = bpy.data.materials.new("Hoop")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.1, 0.5, 0.9, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.3
    bsdf.inputs['Roughness'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_stall_roof_material():
    mat = bpy.data.materials.new("StallRoof")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.9, 0.7, 0.1, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.8
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

wood_mat = create_wood_material()
mat_mat = create_mat_material()
hoop_mat = create_hoop_material()
stall_roof_mat = create_stall_roof_material()

# --- TALL WOODEN TOWER ---
tower_height = 8.0
tower_radius = 1.5
num_posts = 4
post_positions = []
for i in range(num_posts):
    angle = i * (2 * math.pi / num_posts)
    x = tower_radius * math.cos(angle)
    z = tower_radius * math.sin(angle)
    post_positions.append((x, z))

# Posts
for x, z in post_positions:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=tower_height, location=(x, tower_height/2, z))
    post = bpy.context.active_object
    post.data.materials.append(wood_mat)
    post.name = f"Post_{x:.2f}_{z:.2f}"

# Cross beams at various heights
beam_heights = [2.0, 4.0, 6.0, 7.5]
for h in beam_heights:
    for i in range(num_posts):
        x1, z1 = post_positions[i]
        x2, z2 = post_positions[(i+1) % num_posts]
        mid_x = (x1 + x2) / 2
        mid_z = (z1 + z2) / 2
        length = math.sqrt((x2-x1)**2 + (z2-z1)**2)
        angle = math.atan2(z2-z1, x2-x1)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=length, location=(mid_x, h, mid_z))
        beam = bpy.context.active_object
        beam.rotation_euler = (0, angle, 0)
        beam.data.materials.append(wood_mat)
        beam.name = f"Beam_{h}_{i}"

# Platform at top
bpy.ops.mesh.primitive_cylinder_add(radius=tower_radius + 0.3, depth=0.15, location=(0, tower_height, 0))
platform = bpy.context.active_object
platform.data.materials.append(wood_mat)
platform.name = "TopPlatform"

# Ladder
ladder_x = tower_radius + 0.3
ladder_z = 0
rung_count = 10
for i in range(rung_count):
    y = i * (tower_height / rung_count)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.6, location=(ladder_x, y, ladder_z))
    rung = bpy.context.active_object
    rung.rotation_euler = (0, math.pi/2, 0)
    rung.data.materials.append(wood_mat)
    rung.name = f"LadderRung_{i}"

# Ladder rails
for side in [-0.3, 0.3]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=tower_height, location=(ladder_x, tower_height/2, ladder_z + side))
    rail = bpy.context.active_object
    rail.data.materials.append(wood_mat)
    rail.name = f"LadderRail_{side}"

# --- SPIRAL SLIDE ---
slide_start_y = tower_height - 0.5
slide_end_y = 0.2
slide_turns = 2.5
slide_radius = tower_radius + 0.8
slide_width = 0.5
slide_segments = 100

# Create spiral slide using a curve
curve_data = bpy.data.curves.new("SpiralSlideCurve", 'CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('POLY')
spline.points.add(slide_segments)

for i in range(slide_segments + 1):
    t = i / slide_segments
    angle = t * slide_turns * 2 * math.pi
    y = slide_start_y - t * (slide_start_y - slide_end_y)
    x = slide_radius * math.cos(angle)
    z = slide_radius * math.sin(angle)
    spline.points[i].co = (x, y, z, 1.0)

slide_obj = bpy.data.objects.new("SpiralSlideCurve", curve_data)
bpy.context.collection.objects.link(slide_obj)

# Convert to mesh and give it width/depth
bpy.context.view_layer.objects.active = slide_obj
bpy.ops.object.select_all(action='DESELECT')
slide_obj.select_set(True)
bpy.ops.object.convert(target='MESH')
slide_mesh = bpy.context.active_object

# Extrude the slide to give it width
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(
    MOVE=(0, 0, slide_width),
    ROT=(0, 0, 0),
    scale=(1, 1, 1)
)
bpy.ops.object.mode_set(mode='OBJECT')

slide_mesh.data.materials.append(wood_mat)
slide_mesh.name = "SpiralSlide"

# Add side rails to slide
for offset in [-slide_width/2, slide_width/2]:
    curve_data2 = bpy.data.curves.new(f"SpiralRailCurve_{offset}", 'CURVE')
    curve_data2.dimensions = '3D'
    spline2 = curve_data2.splines.new('POLY')
    spline2.points.add(slide_segments)
    for i in range(slide_segments + 1):
        t = i / slide_segments
        angle = t * slide_turns * 2 * math.pi
        y = slide_start_y - t * (slide_start_y - slide_end_y)
        x = slide_radius * math.cos(angle)
        z = slide_radius * math.sin(angle) + offset
        spline2.points[i].co = (x, y, z, 1.0)
    rail_obj = bpy.data.objects.new(f"SpiralRail_{offset}", curve_data2)
    bpy.context.collection.objects.link(rail_obj)
    bpy.context.view_layer.objects.active = rail_obj
    bpy.ops.object.select_all(action='DESELECT')
    rail_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    rail_mesh = bpy.context.active_object
    rail_mesh.data.materials.append(wood_mat)
    rail_mesh.name = f"SpiralRail_{offset}"

# --- MATS AT THE BASE ---
# Place mats around the base of the tower
mat_positions = [
    (0, 0),
    (2.5, 0),
    (-2.5, 0),
    (0, 2.5),
    (0, -2.5),
    (2, 2),
    (-2, 2),
    (2, -2),
    (-2, -2),
]

for i, (mx, mz) in enumerate(mat_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.15, location=(mx, 0.075, mz))
    mat_obj = bpy.context.active_object
    mat_obj.data.materials.append(mat_mat)
    mat_obj.name = f"BaseMat_{i}"

# --- HOOP-LA STALL ---
stall_x = 6.0
stall_z = 0.0

# Stall base
bpy.ops.mesh.primitive_cube_add(size=1, location=(stall_x, 0.5, stall_z))
stall_base = bpy.context.active_object
stall_base.scale = (1.5, 1.0, 1.0)
stall_base.data.materials.append(wood_mat)
stall_base.name = "HoopStallBase"

# Stall posts
stall_post_positions = [
    (stall_x - 1.2, stall_z - 1.2),
    (stall_x + 1.2, stall_z - 1.2),
    (stall_x - 1.2, stall_z + 1.2),
    (stall_x + 1.2, stall_z + 1.2),
]
for i, (px, pz) in enumerate(stall_post_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.0, location=(px, 1.0, pz))
    post = bpy.context.active_object
    post.data.materials.append(wood_mat)
    post.name = f"StallPost_{i}"

# Stall roof
bpy.ops.mesh.primitive_cone_add(radius1=2.2, radius2=0, depth=1.0, location=(stall_x, 2.5, stall_z))
stall_roof = bpy.context.active_object
stall_roof.data.materials.append(stall_roof_mat)
stall_roof.name = "StallRoof"

# Hoop-la hoops displayed on the stall
hoop_colors = [
    (0.9, 0.1, 0.1, 1.0),
    (0.1, 0.9, 0.1, 1.0),
    (0.1, 0.1, 0.9, 1.0),
    (0.9, 0.9, 0.1, 1.0),
    (0.9, 0.1, 0.9, 1.0),
]

for i, color in enumerate(hoop_colors):
    hoop_mat_i = bpy.data.materials.new(f"HoopColor_{i}")
    hoop_mat_i.use_nodes = True
    nodes = hoop_mat_i.node_tree.nodes
    links = hoop_mat_i.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 0.2
    bsdf.inputs['Roughness'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    hoop_x = stall_x - 1.0 + i * 0.5
    hoop_z = stall_z - 1.5
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.4,
        minor_radius=0.03,
        major_segments=32,
        minor_segments=8,
        location=(hoop_x, 1.2, hoop_z)
    )
    hoop = bpy.context.active_object
    hoop.data.materials.append(hoop_mat_i)
    hoop.name = f"Hoop_{i}"

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = bpy.data.materials.new("Ground")
ground_mat.use_nodes = True
nodes = ground_mat.node_tree.nodes
links = ground_mat.node_tree.links
nodes.clear()
out = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.3, 0.5, 0.2, 1.0)
bsdf.inputs['Roughness'].default_value = 1.0
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
ground.data.materials.append(ground_mat)
ground.name = "Ground"

# Set up camera
bpy.ops.object.camera_add(location=(15, 8, 12))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(160))
scene.camera = camera

# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(10, 20, 15))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)
sun.name = "SunLight"

print("Playground scene created successfully!")
