import bpy
import math
import mathutils
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Create Terracotta Pot ---
# Profile for the pot (lathe)
# We'll create a pot by revolving a profile curve
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=1, location=(0, 0, 0))
pot = bpy.context.active_object
pot.name = "Terracotta_Pot"

# Delete the pot we just made and use a proper lathe approach
bpy.ops.object.delete(use_global=False)

# Create a mesh for the pot using a profile
# Pot profile: a tapered cylinder with a rim
import bmesh

mesh = bpy.data.meshes.new("PotMesh")
pot_obj = bpy.data.objects.new("Terracotta_Pot", mesh)
bpy.context.collection.objects.link(pot_obj)

bm = bmesh.new()
bm.from_mesh(mesh)

# Define pot profile points (x = radius, z = height)
# Bottom center to bottom edge, up the side, rim, inner rim, inner wall down to soil level
profile_points = [
    (0.0, 0.0),       # bottom center
    (0.8, 0.0),       # bottom edge
    (0.9, 0.1),       # slight taper
    (1.0, 1.5),       # top outer
    (1.05, 1.55),     # rim outer
    (1.05, 1.7),      # rim top
    (0.95, 1.7),      # rim inner top
    (0.9, 1.65),      # rim inner
    (0.85, 0.5),      # inner wall down to soil
    (0.0, 0.5),       # inner bottom center (soil level)
]

# Create vertices for the profile
verts = [bm.verts.new((x, 0, z)) for x, z in profile_points]

# Create edges
for i in range(len(verts) - 1):
    bm.edges.new((verts[i], verts[i + 1]))

# Spin the profile around the Z axis
geom = bm.verts[:] + bm.edges[:]
bmesh.ops.spin(bm, geom=geom, cent=(0, 0, 0), axis=(0, 0, 1),
               angle=math.radians(360), steps=32, use_merge=True)

# Remove duplicate vertices
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

# Recalculate normals
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

bm.to_mesh(mesh)
bm.free()

# Add material for terracotta
mat_terracotta = bpy.data.materials.new("Terracotta")
mat_terracotta.use_nodes = True
nodes = mat_terracotta.node_tree.nodes
links = mat_terracotta.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (300, 0)

# Set terracotta color (reddish-brown)
bsdf.inputs['Base Color'].default_value = (0.72, 0.35, 0.2, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Metallic'].default_value = 0.0

links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

pot_obj.data.materials.append(mat_terracotta)

# --- Create Soil ---
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.85, depth=0.3, location=(0, 0, 0.65))
soil = bpy.context.active_object
soil.name = "Soil"

mat_soil = bpy.data.materials.new("Soil")
mat_soil.use_nodes = True
nodes_s = mat_soil.node_tree.nodes
links_s = mat_soil.node_tree.links

for node in nodes_s:
    nodes_s.remove(node)

bsdf_s = nodes_s.new('ShaderNodeBsdfPrincipled')
bsdf_s.location = (0, 0)
output_s = nodes_s.new('ShaderNodeOutputMaterial')
output_s.location = (300, 0)

bsdf_s.inputs['Base Color'].default_value = (0.15, 0.1, 0.05, 1.0)
bsdf_s.inputs['Roughness'].default_value = 1.0

links_s.new(bsdf_s.outputs['BSDF'], output_s.inputs['Surface'])

soil.data.materials.append(mat_soil)

# --- Create Cactus ---
# Main body: elongated cylinder
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.4, depth=2.0, location=(0, 0, 1.65))
cactus_body = bpy.context.active_object
cactus_body.name = "Cactus_Body"

# Add a slight taper to the top
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Use simple deform to taper
mod_taper = cactus_body.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
mod_taper.deform_method = 'TAPER'
mod_taper.factor = 0.5
mod_taper.angle = math.radians(0)
mod_taper.deform_axis = 'Z'

bpy.ops.object.modifier_apply(modifier="Taper")

# Add slight rounding to top
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Bevel the top edge
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Add left arm
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.2, depth=0.8, location=(-0.5, 0, 1.8))
cactus_arm_l = bpy.context.active_object
cactus_arm_l.name = "Cactus_Arm_Left"
cactus_arm_l.rotation_euler = (0, math.radians(45), 0)

# Add right arm
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.2, depth=0.7, location=(0.45, 0, 1.5))
cactus_arm_r = bpy.context.active_object
cactus_arm_r.name = "Cactus_Arm_Right"
cactus_arm_r.rotation_euler = (0, math.radians(-40), 0)

# Add a smaller upper arm on the left
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.15, depth=0.5, location=(-0.75, 0, 2.2))
cactus_arm_l2 = bpy.context.active_object
cactus_arm_l2.name = "Cactus_Arm_Left2"
cactus_arm_l2.rotation_euler = (0, math.radians(30), 0)

# Join all cactus parts
bpy.ops.object.select_all(action='DESELECT')
cactus_body.select_set(True)
cactus_arm_l.select_set(True)
cactus_arm_r.select_set(True)
cactus_arm_l2.select_set(True)
bpy.context.view_layer.objects.active = cactus_body
bpy.ops.object.join()
cactus = bpy.context.active_object
cactus.name = "Cactus"

# Add a green material with some variation
mat_cactus = bpy.data.materials.new("Cactus_Green")
mat_cactus.use_nodes = True
nodes_c = mat_cactus.node_tree.nodes
links_c = mat_cactus.node_tree.links

for node in nodes_c:
    nodes_c.remove(node)

bsdf_c = nodes_c.new('ShaderNodeBsdfPrincipled')
bsdf_c.location = (0, 0)
output_c = nodes_c.new('ShaderNodeOutputMaterial')
output_c.location = (300, 0)

# Dark green color
bsdf_c.inputs['Base Color'].default_value = (0.1, 0.4, 0.1, 1.0)
bsdf_c.inputs['Roughness'].default_value = 0.6
bsdf_c.inputs['Bump'].default_value = 0.05

links_c.new(bsdf_c.outputs['BSDF'], output_c.inputs['Surface'])

cactus.data.materials.append(mat_cactus)

# Add some small spikes using icospheres scattered on the cactus surface
# We'll add a few small cones as spikes
import random
random.seed(42)

spikes = []
for i in range(40):
    # Random position on the cactus body
    angle = random.uniform(0, 2 * math.pi)
    height = random.uniform(1.2, 2.8)
    radius = 0.4 if height < 2.0 else 0.25
    
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = height
    
    # Check if this position is on an arm
    on_arm = False
    if abs(x + 0.5) < 0.3 and 1.5 < z < 2.2:
        on_arm = True
    if abs(x - 0.45) < 0.3 and 1.2 < z < 1.9:
        on_arm = True
    if abs(x + 0.75) < 0.25 and 2.0 < z < 2.5:
        on_arm = True
    
    if not on_arm and abs(x) > 0.45:
        continue
    
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.02, radius2=0.0, depth=0.08,
                                     location=(x, y, z))
    spike = bpy.context.active_object
    spike.rotation_euler = (0, math.radians(90), angle)
    spikes.append(spike)

# Join all spikes into one object
if spikes:
    bpy.ops.object.select_all(action='DESELECT')
    for s in spikes:
        s.select_set(True)
    bpy.context.view_layer.objects.active = spikes[0]
    bpy.ops.object.join()
    cactus_spikes = bpy.context.active_object
    cactus_spikes.name = "Cactus_Spikes"
    
    mat_spike = bpy.data.materials.new("Spike_White")
    mat_spike.use_nodes = True
    nodes_sp = mat_spike.node_tree.nodes
    links_sp = mat_spike.node_tree.links
    
    for node in nodes_sp:
        nodes_sp.remove(node)
    
    bsdf_sp = nodes_sp.new('ShaderNodeBsdfPrincipled')
    bsdf_sp.location = (0, 0)
    output_sp = nodes_sp.new('ShaderNodeOutputMaterial')
    output_sp.location = (300, 0)
    
    bsdf_sp.inputs['Base Color'].default_value = (0.9, 0.85, 0.7, 1.0)
    bsdf_sp.inputs['Roughness'].default_value = 0.3
    
    links_sp.new(bsdf_sp.outputs['BSDF'], output_sp.inputs['Surface'])
    
    cactus_spikes.data.materials.append(mat_spike)

# Add a small flower on top of the cactus
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.15, location=(0, 0, 2.75))
flower = bpy.context.active_object
flower.name = "Cactus_Flower"
flower.scale = (1, 1, 0.6)

mat_flower = bpy.data.materials.new("Flower_Pink")
mat_flower.use_nodes = True
nodes_f = mat_flower.node_tree.nodes
links_f = mat_flower.node_tree.links

for node in nodes_f:
    nodes_f.remove(node)

bsdf_f = nodes_f.new('ShaderNodeBsdfPrincipled')
bsdf_f.location = (0, 0)
output_f = nodes_f.new('ShaderNodeOutputMaterial')
output_f.location = (300, 0)

bsdf_f.inputs['Base Color'].default_value = (0.9, 0.3, 0.5, 1.0)
bsdf_f.inputs['Roughness'].default_value = 0.4
bsdf_f.inputs['Emission Color'].default_value = (0.9, 0.3, 0.5, 1.0)
bsdf_f.inputs['Emission Strength'].default_value = 0.1

links_f.new(bsdf_f.outputs['BSDF'], output_f.inputs['Surface'])

flower.data.materials.append(mat_flower)

# Set up camera
bpy.ops.object.camera_add(location=(3, -3, 2.5), rotation=(math.radians(60), 0, math.radians(45)))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Add a light
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Set up world background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.8, 0.85, 0.9, 1.0)
    bg_node.inputs[1].default_value = 1.0

print("Cactus in terracotta pot created successfully!")
