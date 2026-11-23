import bpy
import math
import random
from mathutils import Vector, noise

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set units
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# --- Materials ---
# Black stone material
stone_mat = bpy.data.materials.new("BlackStone")
stone_mat.use_nodes = True
nodes = stone_mat.node_tree.nodes
links = stone_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
bsdf.inputs["Roughness"].default_value = 0.95
# Add noise for texture
tex_coord = nodes.new("ShaderNodeTexCoord")
mapping = nodes.new("ShaderNodeMapping")
noise_node = nodes.new("ShaderNodeTexNoise")
noise_node.inputs["Scale"].default_value = 15.0
noise_node.inputs["Detail"].default_value = 8.0
links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])
links.new(mapping.outputs["Vector"], noise_node.inputs["Vector"])
links.new(noise_node.outputs["Fac"], bsdf.inputs["Roughness"])

# Corrugated iron material
iron_mat = bpy.data.materials.new("CorrugatedIron")
iron_mat.use_nodes = True
nodes = iron_mat.node_tree.nodes
links = iron_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.4, 0.4, 0.42, 1.0)
bsdf.inputs["Metallic"].default_value = 0.8
bsdf.inputs["Roughness"].default_value = 0.4
# Corrugation via wave texture
tex_coord = nodes.new("ShaderNodeTexCoord")
wave = nodes.new("ShaderNodeTexWave")
wave.inputs["Scale"].default_value = 20.0
wave.inputs["Distortion"].default_value = 0.0
wave.wave_type = 'BANDS'
wave.bands_direction = 'Z'
links.new(tex_coord.outputs["Object"], wave.inputs["Vector"])
links.new(wave.outputs["Fac"], bsdf.inputs["Roughness"])

# Ash material
ash_mat = bpy.data.materials.new("Ash")
ash_mat.use_nodes = True
nodes = ash_mat.node_tree.nodes
links = ash_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.62, 1.0)
bsdf.inputs["Roughness"].default_value = 1.0
tex_coord = nodes.new("ShaderNodeTexCoord")
noise_node = nodes.new("ShaderNodeTexNoise")
noise_node.inputs["Scale"].default_value = 50.0
noise_node.inputs["Detail"].default_value = 10.0
links.new(tex_coord.outputs["Object"], noise_node.inputs["Vector"])
links.new(noise_node.outputs["Fac"], bsdf.inputs["Roughness"])

# Crater lava material
lava_mat = bpy.data.materials.new("Lava")
lava_mat.use_nodes = True
nodes = lava_mat.node_tree.nodes
links = lava_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 0.2, 0.0, 1.0)
bsdf.inputs["Emission Color"].default_value = (1.0, 0.3, 0.0, 1.0)
bsdf.inputs["Emission Strength"].default_value = 5.0
bsdf.inputs["Roughness"].default_value = 0.8

# Wood material for pole and rails
wood_mat = bpy.data.materials.new("Wood")
wood_mat.use_nodes = True
nodes = wood_mat.node_tree.nodes
links = wood_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.3, 0.15, 0.05, 1.0)
bsdf.inputs["Roughness"].default_value = 0.8
tex_coord = nodes.new("ShaderNodeTexCoord")
wave = nodes.new("ShaderNodeTexWave")
wave.inputs["Scale"].default_value = 5.0
wave.wave_type = 'BANDS'
wave.bands_direction = 'Y'
links.new(tex_coord.outputs["Object"], wave.inputs["Vector"])
links.new(wave.outputs["Fac"], bsdf.inputs["Roughness"])

# Marker sign material
sign_mat = bpy.data.materials.new("MarkerSign")
sign_mat.use_nodes = True
nodes = sign_mat.node_tree.nodes
links = sign_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.6, 0.1, 1.0)
bsdf.inputs["Roughness"].default_value = 0.5

# --- Helper functions ---
def create_cylinder(name, radius, depth, location, material, segments=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

def create_box(name, size, location, material):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# --- Ground / Ash Layer ---
# Large ground plane
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "AshGround"
ground.data.materials.append(ash_mat)
# Subdivide and displace for ash texture
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=50)
bpy.ops.object.mode_set(mode='OBJECT')
# Add displacement modifier
disp_mod = ground.modifiers.new("AshDisp", 'DISPLACE')
texture = bpy.data.textures.new("AshTex", 'CLOUDS')
texture.noise_scale = 2.0
disp_mod.texture = texture
disp_mod.strength = 0.3
disp_mod.mid_level = 0.5

# --- Volcano Crater (behind the hut) ---
# Create a cone shape for the volcano
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=30, radius2=5, depth=20, location=(0, -40, 10))
volcano = bpy.context.active_object
volcano.name = "Volcano"
volcano.data.materials.append(stone_mat)
# Subdivide for better shape
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=3)
bpy.ops.object.mode_set(mode='OBJECT')
# Add displacement for rocky look
disp_mod = volcano.modifiers.new("RockDisp", 'DISPLACE')
texture = bpy.data.textures.new("RockTex", 'CLOUDS')
texture.noise_scale = 1.5
disp_mod.texture = texture
disp_mod.strength = 2.0

# Crater hole - create a torus at the top to suggest the rim
bpy.ops.mesh.primitive_torus_add(major_radius=5, minor_radius=1.5, location=(0, -40, 20), major_segments=64, minor_segments=16)
crater_rim = bpy.context.active_object
crater_rim.name = "CraterRim"
crater_rim.data.materials.append(stone_mat)

# Lava pool inside crater
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=4.5, depth=0.5, location=(0, -40, 19.5))
lava = bpy.context.active_object
lava.name = "LavaPool"
lava.data.materials.append(lava_mat)

# --- Steam Particles ---
# Create a particle system for steam
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=16, radius=0.5, location=(0, -40, 22))
steam_source = bpy.context.active_object
steam_source.name = "SteamSource"
# Make it invisible but keep as emitter
steam_source.display_type = 'WIRE'
# Create particle system
psys_mod = steam_source.modifiers.new("SteamPS", 'PARTICLE_SYSTEM')
psys = steam_source.particle_systems[0]
psys.particle_count = 200
psys.frame_start = 1
psys.frame_end = 250
psys.lifetime = 100
psys.particle_size = 0.5
psys.size_random = 0.5
# Set velocity
psys.effector_weights.gravity = 0.0
psys.normal_factor = 0.5
psys.factor_random = 0.3
# Create steam material
steam_mat = bpy.data.materials.new("Steam")
steam_mat.use_nodes = True
nodes = steam_mat.node_tree.nodes
links = steam_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
bsdf.inputs["Alpha"].default_value = 0.3
bsdf.inputs["Roughness"].default_value = 1.0
steam_mat.blend_method = 'BLEND'
# Assign to particles
psys.settings.render_type = 'OBJECT'
# Create a small sphere for particles
bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=8, radius=0.3, location=(100, 100, 100))
particle_obj = bpy.context.active_object
particle_obj.name = "SteamParticle"
particle_obj.data.materials.append(steam_mat)
particle_obj.hide_render = True
particle_obj.hide_viewport = True
psys.settings.instance_object = particle_obj
psys.settings.particle_size = 1.0
psys.settings.size_random = 0.5

# --- Hut: Black Stone Walls ---
# Hut location
hut_x, hut_y = 10, 0
hut_width = 6
hut_depth = 5
hut_height = 3

# Front wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x, hut_y + hut_depth/2, hut_height/2))
front_wall = bpy.context.active_object
front_wall.name = "HutFrontWall"
front_wall.scale = (hut_width/2, 0.3, hut_height/2)
front_wall.data.materials.append(stone_mat)

# Back wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x, hut_y - hut_depth/2, hut_height/2))
back_wall = bpy.context.active_object
back_wall.name = "HutBackWall"
back_wall.scale = (hut_width/2, 0.3, hut_height/2)
back_wall.data.materials.append(stone_mat)

# Left wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x - hut_width/2, hut_y, hut_height/2))
left_wall = bpy.context.active_object
left_wall.name = "HutLeftWall"
left_wall.scale = (0.3, hut_depth/2, hut_height/2)
left_wall.data.materials.append(stone_mat)

# Right wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x + hut_width/2, hut_y, hut_height/2))
right_wall = bpy.context.active_object
right_wall.name = "HutRightWall"
right_wall.scale = (0.3, hut_depth/2, hut_height/2)
right_wall.data.materials.append(stone_mat)

# Floor
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x, hut_y, 0.1))
floor = bpy.context.active_object
floor.name = "HutFloor"
floor.scale = (hut_width/2, hut_depth/2, 0.1)
floor.data.materials.append(stone_mat)

# Door opening (front wall, cut out by adding a dark rectangle)
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x, hut_y + hut_depth/2 + 0.05, 1.0))
door = bpy.context.active_object
door.name = "HutDoor"
door.scale = (0.8, 0.1, 1.0)
door.data.materials.append(bpy.data.materials["MarkerSign"])  # Use sign color for door frame

# --- Corrugated Iron Roof ---
# Create a sloped roof
bpy.ops.mesh.primitive_plane_add(size=1, location=(hut_x, hut_y, hut_height + 0.5))
roof = bpy.context.active_object
roof.name = "HutRoof"
roof.scale = (hut_width/2 + 0.5, hut_depth/2 + 0.5, 1)
roof.rotation_euler = (math.radians(15), 0, 0)
roof.data.materials.append(iron_mat)

# Add corrugation by subdividing and displacing
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')
# Displace for corrugated effect
disp_mod = roof.modifiers.new("Corrugation", 'DISPLACE')
texture = bpy.data.textures.new("CorrugTex", 'WOOD')
texture.wood_type = 'BANDS'
texture.noise_scale = 0.1
texture.noise_depth = 2
disp_mod.texture = texture
disp_mod.strength = 0.05
disp_mod.direction = 'Z'

# Second roof panel (opposite slope)
bpy.ops.mesh.primitive_plane_add(size=1, location=(hut_x, hut_y, hut_height + 0.5))
roof2 = bpy.context.active_object
roof2.name = "HutRoof2"
roof2.scale = (hut_width/2 + 0.5, hut_depth/2 + 0.5, 1)
roof2.rotation_euler = (math.radians(-15), 0, 0)
roof2.data.materials.append(iron_mat)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')
disp_mod = roof2.modifiers.new("Corrugation", 'DISPLACE')
disp_mod.texture = texture
disp_mod.strength = 0.05
disp_mod.direction = 'Z'

# Ridge beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x, hut_y, hut_height + 1.0))
ridge = bpy.context.active_object
ridge.name = "RoofRidge"
ridge.scale = (hut_width/2 + 0.5, 0.2, 0.1)
ridge.data.materials.append(iron_mat)

# --- Marker Pole ---
pole_x, pole_y = 5, 3
# Pole
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=2.5, location=(pole_x, pole_y, 1.25))
pole = bpy.context.active_object
pole.name = "MarkerPole"
pole.data.materials.append(wood_mat)

# Sign board
bpy.ops.mesh.primitive_cube_add(size=1, location=(pole_x, pole_y, 2.2))
sign = bpy.context.active_object
sign.name = "MarkerSignBoard"
sign.scale = (0.8, 0.05, 0.3)
sign.data.materials.append(sign_mat)

# --- Railed Path ---
# Path from front of hut going forward (toward viewer)
path_start_y = hut_y + hut_depth/2
path_end_y = hut_y + hut_depth/2 + 15
path_x = hut_x

# Path surface (ash/dirt)
bpy.ops.mesh.primitive_plane_add(size=1, location=(path_x, (path_start_y + path_end_y)/2, 0.05))
path_surface = bpy.context.active_object
path_surface.name = "PathSurface"
path_surface.scale = (1.0, (path_end_y - path_start_y)/2, 1)
path_surface.data.materials.append(ash_mat)

# Left rail posts
num_posts = 8
for i in range(num_posts):
    t = i / (num_posts - 1)
    py = path_start_y + t * (path_end_y - path_start_y)
    px = path_x - 1.2
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=1.0, location=(px, py, 0.5))
    post = bpy.context.active_object
    post.name = f"LeftRailPost_{i}"
    post.data.materials.append(wood_mat)

# Right rail posts
for i in range(num_posts):
    t = i / (num_posts - 1)
    py = path_start_y + t * (path_end_y - path_start_y)
    px = path_x + 1.2
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=1.0, location=(px, py, 0.5))
    post = bpy.context.active_object
    post.name = f"RightRailPost_{i}"
    post.data.materials.append(wood_mat)

# Left top rail
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=path_end_y - path_start_y, location=(path_x - 1.2, (path_start_y + path_end_y)/2, 1.0))
left_rail = bpy.context.active_object
left_rail.name = "LeftTopRail"
left_rail.rotation_euler = (math.radians(90), 0, 0)
left_rail.data.materials.append(wood_mat)

# Right top rail
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=path_end_y - path_start_y, location=(path_x + 1.2, (path_start_y + path_end_y)/2, 1.0))
right_rail = bpy.context.active_object
right_rail.name = "RightTopRail"
right_rail.rotation_euler = (math.radians(90), 0, 0)
right_rail.data.materials.append(wood_mat)

# Left middle rail
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=path_end_y - path_start_y, location=(path_x - 1.2, (path_start_y + path_end_y)/2, 0.5))
left_mid_rail = bpy.context.active_object
left_mid_rail.name = "LeftMidRail"
left_mid_rail.rotation_euler = (math.radians(90), 0, 0)
left_mid_rail.data.materials.append(wood_mat)

# Right middle rail
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=path_end_y - path_start_y, location=(path_x + 1.2, (path_start_y + path_end_y)/2, 0.5))
right_mid_rail = bpy.context.active_object
right_mid_rail.name = "RightMidRail"
right_mid_rail.rotation_euler = (math.radians(90), 0, 0)
right_mid_rail.data.materials.append(wood_mat)

# --- Additional Ash Piles ---
# Scatter some ash mounds
random.seed(42)
for i in range(15):
    rx = random.uniform(-20, 20)
    ry = random.uniform(-20, 20)
    # Avoid hut area
    if abs(rx - hut_x) < 5 and abs(ry - hut_y) < 5:
        continue
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=16, radius=random.uniform(0.5, 1.5), location=(rx, ry, 0))
    mound = bpy.context.active_object
    mound.name = f"AshMound_{i}"
    mound.scale = (1, 1, 0.3)
    mound.data.materials.append(ash_mat)

# --- Lighting ---
# Sun light
bpy.ops.object.light_add(type='SUN', location=(20, 20, 30))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3.0
sun.data.color = (1.0, 0.95, 0.85)
sun.rotation_euler = (math.radians(45), math.radians(20), 0)

# Point light for lava glow
bpy.ops.object.light_add(type='POINT', location=(0, -40, 20))
lava_light = bpy.context.active_object
lava_light.name = "LavaLight"
lava_light.data.energy = 500
lava_light.data.color = (1.0, 0.3, 0.0)
lava_light.data.shadow_soft_size = 2.0

# --- Camera ---
bpy.ops.object.camera_add(location=(15, 15, 8))
camera = bpy.context.active_object
camera.name = "MainCamera"
# Point camera toward the scene center
direction = Vector((hut_x, hut_y, 1.5)) - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera

# --- World Background ---
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs["Color"].default_value = (0.1, 0.1, 0.12, 1.0)
    bg_node.inputs["Strength"].default_value = 0.5

print("Volcano rim hut scene built successfully.")
