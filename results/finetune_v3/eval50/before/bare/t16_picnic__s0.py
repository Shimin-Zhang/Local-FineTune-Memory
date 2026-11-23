import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the checkered picnic blanket
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, 0))
blanket = bpy.context.active_object
blanket.name = "Picnic_Blanket"

# Create a checkered texture using nodes
mat = bpy.data.materials.new(name="Checkered")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (600, 0)

diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
diffuse_node.location = (400, 0)

# Texture coordinate
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-400, 0)

# Mapping
mapping = nodes.new('ShaderNodeMapping')
mapping.location = (-200, 0)

# Checker texture
checker = nodes.new('ShaderNodeTexChecker')
checker.location = (0, 0)
checker.inputs['Color1'].default_value = (1, 1, 1, 1)  # White
checker.inputs['Color2'].default_value = (0.8, 0.1, 0.1, 1)  # Red
checker.inputs['Scale'].default_value = 8.0

# Links
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], checker.inputs['Vector'])
links.new(checker.outputs['Color'], diffuse_node.inputs['Color'])
links.new(diffuse_node.outputs['BSDF'], output_node.inputs['Surface'])

blanket.data.materials.append(mat)

# Create the wicker basket
# Basket body (cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.6, location=(0, 0, 0.3))
basket_body = bpy.context.active_object
basket_body.name = "Basket_Body"

# Add some subdivisions for a wicker-like look
subsurf = basket_body.modifiers.new("Subdivision", 'SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 2

# Basket material (wicker/brown)
basket_mat = bpy.data.materials.new(name="Wicker")
basket_mat.use_nodes = True
nodes_b = basket_mat.node_tree.nodes
links_b = basket_mat.node_tree.links

for node in nodes_b:
    nodes_b.remove(node)

output_b = nodes_b.new('ShaderNodeOutputMaterial')
output_b.location = (400, 0)

diffuse_b = nodes_b.new('ShaderNodeBsdfDiffuse')
diffuse_b.location = (200, 0)
diffuse_b.inputs['Color'].default_value = (0.4, 0.25, 0.1, 1)  # Brown

# Add some noise for wicker texture
tex_coord_b = nodes_b.new('ShaderNodeTexCoord')
tex_coord_b.location = (-200, 0)

noise = nodes_b.new('ShaderNodeTexNoise')
noise.location = (0, 0)
noise.inputs['Scale'].default_value = 20.0
noise.inputs['Detail'].default_value = 5.0

mix = nodes_b.new('ShaderNodeMixRGB')
mix.location = (100, 0)
mix.inputs['Fac'].default_value = 0.3
mix.inputs['Color1'].default_value = (0.4, 0.25, 0.1, 1)
mix.inputs['Color2'].default_value = (0.3, 0.18, 0.08, 1)

links_b.new(tex_coord_b.outputs['Object'], noise.inputs['Vector'])
links_b.new(noise.outputs['Fac'], mix.inputs['Fac'])
links_b.new(mix.outputs['Color'], diffuse_b.inputs['Color'])
links_b.new(diffuse_b.outputs['BSDF'], output_b.inputs['Surface'])

basket_body.data.materials.append(basket_mat)

# Basket rim (torus)
bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.05, location=(0, 0, 0.6))
basket_rim = bpy.context.active_object
basket_rim.name = "Basket_Rim"
basket_rim.data.materials.append(basket_mat)

# Basket handle (torus, partial)
bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.03, location=(0, 0, 0.75))
handle = bpy.context.active_object
handle.name = "Basket_Handle"
handle.rotation_euler[0] = math.radians(90)
handle.data.materials.append(basket_mat)

# Add some simple food items on the blanket
# Bread (scaled cube)
bpy.ops.mesh.primitive_cube_add(size=0.3, location=(-0.8, 0.5, 0.05))
bread = bpy.context.active_object
bread.name = "Bread"
bread.scale = (1, 0.6, 0.3)

bread_mat = bpy.data.materials.new(name="Bread")
bread_mat.use_nodes = True
nodes_br = bread_mat.node_tree.nodes
links_br = bread_mat.node_tree.links
for node in nodes_br:
    nodes_br.remove(node)
out_br = nodes_br.new('ShaderNodeOutputMaterial')
out_br.location = (200, 0)
diff_br = nodes_br.new('ShaderNodeBsdfDiffuse')
diff_br.location = (0, 0)
diff_br.inputs['Color'].default_value = (0.7, 0.5, 0.3, 1)
links_br.new(diff_br.outputs['BSDF'], out_br.inputs['Surface'])
bread.data.materials.append(bread_mat)

# Cheese (scaled cube)
bpy.ops.mesh.primitive_cube_add(size=0.25, location=(0.7, -0.4, 0.04))
cheese = bpy.context.active_object
cheese.name = "Cheese"
cheese.scale = (1, 0.8, 0.2)

cheese_mat = bpy.data.materials.new(name="Cheese")
cheese_mat.use_nodes = True
nodes_ch = cheese_mat.node_tree.nodes
links_ch = cheese_mat.node_tree.links
for node in nodes_ch:
    nodes_ch.remove(node)
out_ch = nodes_ch.new('ShaderNodeOutputMaterial')
out_ch.location = (200, 0)
diff_ch = nodes_ch.new('ShaderNodeBsdfDiffuse')
diff_ch.location = (0, 0)
diff_ch.inputs['Color'].default_value = (0.9, 0.7, 0.2, 1)
links_ch.new(diff_ch.outputs['BSDF'], out_ch.inputs['Surface'])
cheese.data.materials.append(cheese_mat)

# Add a simple ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground.name = "Ground"

ground_mat = bpy.data.materials.new(name="Grass")
ground_mat.use_nodes = True
nodes_g = ground_mat.node_tree.nodes
links_g = ground_mat.node_tree.links
for node in nodes_g:
    nodes_g.remove(node)
out_g = nodes_g.new('ShaderNodeOutputMaterial')
out_g.location = (200, 0)
diff_g = nodes_g.new('ShaderNodeBsdfDiffuse')
diff_g.location = (0, 0)
diff_g.inputs['Color'].default_value = (0.2, 0.5, 0.1, 1)
links_g.new(diff_g.outputs['BSDF'], out_g.inputs['Surface'])
ground.data.materials.append(ground_mat)

# Set up camera
bpy.ops.object.camera_add(location=(2, 2, 1.5))
camera = bpy.context.active_object
camera.name = "Camera"

# Point camera at the scene
direction = (0, 0, 0.3) - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Set camera as active
bpy.context.scene.camera = camera

# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)
