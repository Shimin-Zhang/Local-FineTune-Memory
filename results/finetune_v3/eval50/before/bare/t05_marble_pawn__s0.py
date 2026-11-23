import bpy
import math
import random
from mathutils import Vector

# Clear default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new collection for the pawn
pawn_collection = bpy.data.collections.new("ChessPawn")
bpy.context.scene.collection.children.link(pawn_collection)

# --- Build the Pawn Geometry using Lathe/Revolve ---
# Define profile points for a chess pawn (x, y) where x is radius, y is height
profile_points = [
    (0.0, 0.0),      # Bottom center
    (0.5, 0.0),      # Bottom edge
    (0.55, 0.05),    # Slight base flare
    (0.55, 0.15),    # Base side
    (0.45, 0.2),     # Taper inward
    (0.35, 0.4),     # Stem lower
    (0.3, 0.6),      # Stem middle
    (0.35, 0.8),     # Collar flare
    (0.4, 0.85),     # Collar top
    (0.3, 0.9),      # Neck
    (0.2, 1.0),      # Head lower
    (0.25, 1.15),    # Head middle
    (0.2, 1.3),      # Head upper
    (0.1, 1.4),      # Head top taper
    (0.0, 1.45),     # Top center
]

# Create mesh from profile
mesh = bpy.data.meshes.new("PawnMesh")
vertices = []
edges = []
faces = []

# We'll use a spin/lathe approach via bmesh
import bmesh

bm = bmesh.new()

# Create profile edge
profile_verts = []
for x, y in profile_points:
    v = bm.verts.new((x, 0, y))
    profile_verts.append(v)

# Create edges along profile
for i in range(len(profile_verts) - 1):
    bm.edges.new((profile_verts[i], profile_verts[i + 1]))

# Spin the profile around Z axis
bmesh.ops.spin(
    bm,
    geom=bm.verts[:] + bm.edges[:],
    cent=(0, 0, 0),
    axis=(0, 0, 1),
    angle=2 * math.pi,
    steps=64,
    use_merge=True,
    use_duplicate=False,
)

# Remove duplicates
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)

# Recalculate normals
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Create mesh object
mesh = bpy.data.meshes.new("PawnMesh")
bm.to_mesh(mesh)
bm.free()

pawn_obj = bpy.data.objects.new("ChessPawn", mesh)
pawn_collection.objects.link(pawn_obj)

# Set active object
bpy.context.view_layer.objects.active = pawn_obj
pawn_obj.select_set(True)

# --- Create White Marble Material with Grey Veins ---
# Use a procedural marble texture
marble_mat = bpy.data.materials.new("WhiteMarble")
marble_mat.use_nodes = True

nodes = marble_mat.node_tree.nodes
links = marble_mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output_node = nodes.new("ShaderNodeOutputMaterial")
output_node.location = (800, 0)

# Base color: white marble
bg_node = nodes.new("ShaderNodeBackground")
bg_node.location = (-400, 0)

# Texture coordinate
tex_coord = nodes.new("ShaderNodeTexCoord")
tex_coord.location = (-1200, 0)

# Mapping node for scaling
mapping_node = nodes.new("ShaderNodeMapping")
mapping_node.location = (-1000, 0)
mapping_node.inputs['Scale'].default_value = (1.0, 1.0, 1.0)

# Noise texture for marble veining
noise1 = nodes.new("ShaderNodeTexNoise")
noise1.location = (-800, 200)
noise1.inputs['Scale'].default_value = 3.0
noise1.inputs['Detail'].default_value = 8.0
noise1.inputs['Roughness'].default_value = 0.5
noise1.inputs['Lacunarity'].default_value = 2.0

# Second noise for more complex veins
noise2 = nodes.new("ShaderNodeTexNoise")
noise2.location = (-800, -100)
noise2.inputs['Scale'].default_value = 5.0
noise2.inputs['Detail'].default_value = 10.0
noise2.inputs['Roughness'].default_value = 0.6

# Combine noises
mix_noise = nodes.new("ShaderNodeMix")
mix_noise.location = (-600, 50)
mix_noise.data_type = 'FLOAT'
mix_noise.inputs['Factor'].default_value = 0.5

# ColorRamp to create vein pattern
color_ramp = nodes.new("ShaderNodeValToRGB")
color_ramp.location = (-400, 100)
color_ramp.color_ramp.elements[0].position = 0.4
color_ramp.color_ramp.elements[0].color = (0.95, 0.95, 0.95, 1.0)  # White
color_ramp.color_ramp.elements[1].position = 0.6
color_ramp.color_ramp.elements[1].color = (0.5, 0.5, 0.5, 1.0)     # Grey veins

# Add a third element for mid-tone
elem_mid = color_ramp.color_ramp.elements.new(0.5)
elem_mid.color = (0.85, 0.85, 0.85, 1.0)  # Light grey

# Principled BSDF
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (400, 0)
bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
bsdf.inputs['Roughness'].default_value = 0.15
bsdf.inputs['Metallic'].default_value = 0.0

# Link nodes
links.new(tex_coord.outputs['Object'], mapping_node.inputs['Vector'])
links.new(mapping_node.outputs['Vector'], noise1.inputs['Vector'])
links.new(mapping_node.outputs['Vector'], noise2.inputs['Vector'])
links.new(noise1.outputs['Fac'], mix_noise.inputs['A'])
links.new(noise2.outputs['Fac'], mix_noise.inputs['B'])
links.new(mix_noise.outputs['Result'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to pawn
pawn_obj.data.materials.append(marble_mat)

# Add a light for better visualization
light_data = bpy.data.lights.new("KeyLight", type='POINT')
light_data.energy = 500
light_data.color = (1.0, 0.95, 0.9)
light_obj = bpy.data.objects.new("KeyLight", light_data)
light_obj.location = (3, 3, 4)
bpy.context.scene.collection.objects.link(light_obj)

# Add a fill light
fill_light_data = bpy.data.lights.new("FillLight", type='POINT')
fill_light_data.energy = 200
fill_light_data.color = (0.9, 0.95, 1.0)
fill_light_obj = bpy.data.objects.new("FillLight", fill_light_data)
fill_light_obj.location = (-2, 2, 2)
bpy.context.scene.collection.objects.link(fill_light_obj)

# Add a simple ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground_name = "Ground"
ground.name = ground_name

ground_mat = bpy.data.materials.new("GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_links = ground_mat.node_tree.links
for node in ground_nodes:
    ground_nodes.remove(node)

g_output = ground_nodes.new("ShaderNodeOutputMaterial")
g_output.location = (300, 0)
g_bsdf = ground_nodes.new("ShaderNodeBsdfPrincipled")
g_bsdf.location = (0, 0)
g_bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)
g_bsdf.inputs['Roughness'].default_value = 0.8
ground_links.new(g_bsdf.outputs['BSDF'], g_output.inputs['Surface'])
ground.data.materials.append(ground_mat)

# Move pawn into its collection
for obj in bpy.context.scene.objects:
    if obj.name == "ChessPawn":
        for coll in obj.users_collection:
            coll.objects.unlink(obj)
        pawn_collection.objects.link(obj)

# Set viewport shading to material preview
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

print("Chess pawn with white marble and grey veins created successfully!")
