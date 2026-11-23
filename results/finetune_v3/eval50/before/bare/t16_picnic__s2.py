import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up the scene
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 128
scene.eevee.taa_samples = 64

# Create a light
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10), rotation=(math.radians(45), 0, math.radians(45)))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Create a ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Ground material (grass green)
ground_mat = bpy.data.materials.new("Grass")
ground_mat.use_nodes = True
nodes = ground_mat.node_tree.nodes
links = ground_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.4, 0.1, 1.0)
bsdf.inputs["Roughness"].default_value = 0.8
ground.data.materials.append(ground_mat)

# Create the checkered picnic blanket
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0.01))
blanket = bpy.context.active_object
blanket.name = "PicnicBlanket"

# Subdivide the blanket for better UVs
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')

# Create checkered material using nodes
blanket_mat = bpy.data.materials.new("CheckeredBlanket")
blanket_mat.use_nodes = True
nodes = blanket_mat.node_tree.nodes
links = blanket_mat.node_tree.links

# Remove default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output = nodes.new("ShaderNodeOutputMaterial")
output.location = (600, 0)

mix = nodes.new("ShaderNodeMix")
mix.location = (400, 0)
mix.data_type = 'RGBA'

# UV Texture
uv = nodes.new("ShaderNodeUVMap")
uv.location = (-200, 0)

# Separate XYZ
sep = nodes.new("ShaderNodeSeparateXYZ")
sep.location = (0, 0)

# Math nodes for checkering
# Floor U * 4
math_u = nodes.new("ShaderNodeMath")
math_u.operation = 'MULTIPLY'
math_u.location = (150, 100)
math_u.inputs[1].default_value = 4.0

math_u_floor = nodes.new("ShaderNodeMath")
math_u_floor.operation = 'FLOOR'
math_u_floor.location = (300, 100)

# Floor V * 4
math_v = nodes.new("ShaderNodeMath")
math_v.operation = 'MULTIPLY'
math_v.location = (150, -100)
math_v.inputs[1].default_value = 4.0

math_v_floor = nodes.new("ShaderNodeMath")
math_v_floor.operation = 'FLOOR'
math_v_floor.location = (300, -100)

# Add U and V floors
math_add = nodes.new("ShaderNodeMath")
math_add.operation = 'ADD'
math_add.location = (450, 0)

# Modulo 2
math_mod = nodes.new("ShaderNodeMath")
math_mod.operation = 'MODULO'
math_mod.location = (550, 0)
math_mod.inputs[1].default_value = 2.0

# Greater Than 0.5 (for checkering)
math_gt = nodes.new("ShaderNodeMath")
math_gt.operation = 'GREATER_THAN'
math_gt.location = (650, 0)
math_gt.inputs[1].default_value = 0.5

# Color A (red)
color_a = nodes.new("ShaderNodeRGB")
color_a.location = (300, 200)
color_a.outputs[0].default_value = (0.8, 0.1, 0.1, 1.0)

# Color B (white)
color_b = nodes.new("ShaderNodeRGB")
color_b.location = (300, -200)
color_b.outputs[0].default_value = (0.95, 0.95, 0.95, 1.0)

# Mix shader based on checkering
mix_check = nodes.new("ShaderNodeMix")
mix_check.location = (800, 0)
mix_check.data_type = 'RGBA'

# Principled BSDF
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (1000, 0)
bsdf.inputs["Roughness"].default_value = 0.9

# Link nodes
links.new(uv.outputs["UV"], sep.inputs["Vector"])
links.new(sep.outputs["X"], math_u.inputs[0])
links.new(sep.outputs["Y"], math_v.inputs[0])
links.new(math_u.outputs[0], math_u_floor.inputs[0])
links.new(math_v.outputs[0], math_v_floor.inputs[0])
links.new(math_u_floor.outputs[0], math_add.inputs[0])
links.new(math_v_floor.outputs[0], math_add.inputs[1])
links.new(math_add.outputs[0], math_mod.inputs[0])
links.new(math_mod.outputs[0], math_gt.inputs[0])
links.new(math_gt.outputs[0], mix_check.inputs["Factor"])
links.new(color_a.outputs[0], mix_check.inputs["A"])
links.new(color_b.outputs[0], mix_check.inputs["B"])
links.new(mix_check.outputs["Result"], bsdf.inputs["Base Color"])
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

blanket.data.materials.append(blanket_mat)

# Create the wicker basket
# Basket body (cylinder with tapered top)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.6, depth=0.8, location=(0.5, 0.3, 0.41))
basket_body = bpy.context.active_object
basket_body.name = "BasketBody"

# Taper the top of the basket
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
# Select top face
bpy.ops.object.mode_set(mode='OBJECT')
import bmesh
bm = bmesh.new()
bm.from_mesh(basket_body.data)
# Scale top vertices
for v in bm.verts:
    if v.co.z > 0:
        v.co.x *= 0.7
        v.co.y *= 0.7
bm.to_mesh(basket_body.data)
bm.free()

# Wicker material
wicker_mat = bpy.data.materials.new("Wicker")
wicker_mat.use_nodes = True
nodes_w = wicker_mat.node_tree.nodes
links_w = wicker_mat.node_tree.links
bsdf_w = nodes_w["Principled BSDF"]
bsdf_w.inputs["Base Color"].default_value = (0.5, 0.3, 0.1, 1.0)
bsdf_w.inputs["Roughness"].default_value = 0.7

# Add a procedural texture for wicker look
noise = nodes_w.new("ShaderNodeTexNoise")
noise.location = (-300, 0)
noise.inputs["Scale"].default_value = 50.0
noise.inputs["Detail"].default_value = 8.0

bump = nodes_w.new("ShaderNodeBump")
bump.location = (-100, -200)
bump.inputs["Strength"].default_value = 0.3

links_w.new(noise.outputs["Fac"], bump.inputs["Height"])
links_w.new(bump.outputs["Normal"], bsdf_w.inputs["Normal"])

basket_body.data.materials.append(wicker_mat)

# Basket handle (torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.65, minor_radius=0.04,
    major_segments=32, minor_segments=8,
    location=(0.5, 0.3, 0.81)
)
handle = bpy.context.active_object
handle.name = "BasketHandle"
handle.rotation_euler = (0, math.radians(90), 0)
handle.data.materials.append(wicker_mat)

# Add some cloth/napkin inside the basket
bpy.ops.mesh.primitive_plane_add(size=0.8, location=(0.5, 0.3, 0.55))
napkin = bpy.context.active_object
napkin.name = "Napkin"
napkin.rotation_euler = (math.radians(10), 0, math.radians(15))

napkin_mat = bpy.data.materials.new("Napkin")
napkin_mat.use_nodes = True
nodes_n = napkin_mat.node_tree.nodes
bsdf_n = nodes_n["Principled BSDF"]
bsdf_n.inputs["Base Color"].default_value = (0.9, 0.85, 0.7, 1.0)
bsdf_n.inputs["Roughness"].default_value = 0.95
napkin.data.materials.append(napkin_mat)

# Add a few bread rolls / fruits for detail
# Bread roll
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0.3, 0.2, 0.55), segments=16, ring_count=8)
bread = bpy.context.active_object
bread.name = "BreadRoll"
bread.scale = (1.3, 1.0, 0.8)
bread_mat = bpy.data.materials.new("Bread")
bread_mat.use_nodes = True
bsdf_b = bread_mat.node_tree.nodes["Principled BSDF"]
bsdf_b.inputs["Base Color"].default_value = (0.7, 0.45, 0.2, 1.0)
bsdf_b.inputs["Roughness"].default_value = 0.8
bread.data.materials.append(bread_mat)

# Apple
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0.7, 0.4, 0.55), segments=16, ring_count=8)
apple = bpy.context.active_object
apple.name = "Apple"
apple.scale = (1.0, 1.0, 0.9)
apple_mat = bpy.data.materials.new("Apple")
apple_mat.use_nodes = True
bsdf_a = apple_mat.node_tree.nodes["Principled BSDF"]
bsdf_a.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1.0)
bsdf_a.inputs["Roughness"].default_value = 0.3
bsdf_a.inputs["Specular IOR Level"].default_value = 0.5
apple.data.materials.append(apple_mat)

# Set camera
bpy.ops.object.camera_add(location=(3, -3, 2.5), rotation=(math.radians(55), 0, math.radians(45)))
camera = bpy.context.active_object
camera.name = "Camera"
scene.camera = camera

# Adjust camera to frame the scene
camera.data.lens = 50

# Set render resolution
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Set output
scene.render.filepath = "/tmp/picnic_scene.png"
scene.render.image_settings.file_format = 'PNG'

print("Picnic scene created successfully!")
