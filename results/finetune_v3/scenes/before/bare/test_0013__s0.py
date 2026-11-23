import bpy
import math
import mathutils
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- MATERIALS ---
def make_mat(name, color, metallic=0.0, roughness=0.5, alpha=1.0, transmission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'
    if transmission > 0:
        bsdf.inputs["Transmission Weight"].default_value = transmission
        bsdf.inputs["IOR"].default_value = 1.45
    return mat

glass_mat = make_mat("Glass", (0.8, 0.9, 1.0, 1.0), metallic=0.0, roughness=0.05, alpha=0.3, transmission=0.9)
steel_mat = make_mat("Steel", (0.5, 0.5, 0.55, 1.0), metallic=0.9, roughness=0.3)
rock_mat = make_mat("CliffRock", (0.35, 0.3, 0.25, 1.0), metallic=0.0, roughness=0.9)
cloud_mat = make_mat("Cloud", (1.0, 1.0, 1.0, 0.6), metallic=0.0, roughness=1.0, alpha=0.6)
gate_mat = make_mat("Gate", (0.1, 0.1, 0.1, 1.0), metallic=0.8, roughness=0.2)
floor_mat = make_mat("Floor", (0.7, 0.75, 0.8, 1.0), metallic=0.1, roughness=0.4)

# --- CLIFF (sheer rock face on the left) ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(-12, 0, -10))
cliff = bpy.context.active_object
cliff.name = "Cliff"
cliff.scale = (4, 30, 25)
cliff.data.materials.append(rock_mat)

# Make cliff face jagged-ish by moving some verts (simple approach: add a displace modifier)
mod = cliff.modifiers.new("Displace", 'DISPLACE')
mod.strength = 3.0
mod.mid_level = 0.5
# Use a texture for displacement
tex = bpy.data.textures.new("CliffNoise", type='CLOUDS')
tex.noise_scale = 0.5
mod.texture = tex

# --- WALKWAY (glass-floored, hung out from cliff) ---
# Walkway extends from cliff edge (x=-8) outward to x=10, width 4 (y -2 to 2), at z=0
walk_len = 18
walk_wid = 4
walk_z = 0

# Glass floor panels
bpy.ops.mesh.primitive_cube_add(size=1, location=(1, 0, -0.15))
floor = bpy.context.active_object
floor.name = "GlassFloor"
floor.scale = (walk_len / 2, walk_wid / 2, 0.15)
floor.data.materials.append(glass_mat)

# Steel support beams underneath
for i in range(5):
    x_pos = -7 + i * 4.5
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=walk_wid + 1, location=(x_pos, 0, -0.5))
    beam = bpy.context.active_object
    beam.name = f"SupportBeam_{i}"
    beam.rotation_euler = (math.radians(90), 0, 0)
    beam.data.materials.append(steel_mat)

# Vertical steel hangers from cliff to walkway
for i in range(4):
    x_pos = -6 + i * 5
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.0, location=(x_pos, 0, -0.25))
    hanger = bpy.context.active_object
    hanger.name = f"Hanger_{i}"
    hanger.data.materials.append(steel_mat)

# --- STEEL RAILING ---
rail_height = 1.0
rail_offset = 0.15  # distance from walkway edge

# Two side rails (left and right)
for side in [-1, 1]:
    y_pos = side * (walk_wid / 2 - rail_offset)
    # Horizontal top rail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=walk_len, location=(1, y_pos, rail_height))
    top_rail = bpy.context.active_object
    top_rail.name = f"TopRail_{'L' if side<0 else 'R'}"
    top_rail.rotation_euler = (0, math.radians(90), 0)
    top_rail.data.materials.append(steel_mat)

    # Horizontal middle rail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=walk_len, location=(1, y_pos, rail_height * 0.5))
    mid_rail = bpy.context.active_object
    mid_rail.name = f"MidRail_{'L' if side<0 else 'R'}"
    mid_rail.rotation_euler = (0, math.radians(90), 0)
    mid_rail.data.materials.append(steel_mat)

    # Vertical posts
    for j in range(7):
        x_pos = -7 + j * 3
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=rail_height, location=(x_pos, y_pos, rail_height / 2))
        post = bpy.context.active_object
        post.name = f"Post_{'L' if side<0 else 'R'}_{j}"
        post.data.materials.append(steel_mat)

# End cap rail (at the far end)
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=walk_wid - 0.3, location=(1 + walk_len/2 - 0.5, 0, rail_height))
end_rail_top = bpy.context.active_object
end_rail_top.name = "EndRailTop"
end_rail_top.rotation_euler = (math.radians(90), 0, 0)
end_rail_top.data.materials.append(steel_mat)

bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=walk_wid - 0.3, location=(1 + walk_len/2 - 0.5, 0, rail_height * 0.5))
end_rail_mid = bpy.context.active_object
end_rail_mid.name = "EndRailMid"
end_rail_mid.rotation_euler = (math.radians(90), 0, 0)
end_rail_mid.data.materials.append(steel_mat)

# --- TICKET GATE (at the cliff-side entrance) ---
gate_x = -7.5
gate_y = 0
gate_w = 2.5
gate_h = 2.2

# Two gate posts
for side in [-1, 1]:
    y_pos = side * (gate_w / 2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(gate_x, y_pos, gate_h / 2))
    post = bpy.context.active_object
    post.name = f"GatePost_{'L' if side<0 else 'R'}"
    post.scale = (0.3, 0.3, gate_h / 2)
    post.data.materials.append(gate_mat)

# Top bar of gate
bpy.ops.mesh.primitive_cube_add(size=1, location=(gate_x, 0, gate_h))
top_bar = bpy.context.active_object
top_bar.name = "GateTopBar"
top_bar.scale = (0.25, gate_w / 2, 0.15)
top_bar.data.materials.append(gate_mat)

# Ticket scanner box on one post
bpy.ops.mesh.primitive_cube_add(size=1, location=(gate_x, -gate_w/2 + 0.2, 1.2))
scanner = bpy.context.active_object
scanner.name = "TicketScanner"
scanner.scale = (0.15, 0.25, 0.2)
scanner.data.materials.append(gate_mat)

# --- SEA OF CLOUDS BELOW ---
# Create a large plane with displacement to look like clouds
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, -12))
clouds = bpy.context.active_object
clouds.name = "SeaOfClouds"
clouds.scale = (1, 1, 1)
clouds.data.materials.append(cloud_mat)

# Subdivide for displacement
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=30)
bpy.ops.object.mode_set(mode='OBJECT')

# Add displace modifier for cloud-like bumps
cloud_mod = clouds.modifiers.new("CloudDisplace", 'DISPLACE')
cloud_mod.strength = 4.0
cloud_mod.mid_level = 0.5
cloud_tex = bpy.data.textures.new("CloudNoise", type='CLOUDS')
cloud_tex.noise_scale = 0.3
cloud_tex.noise_depth = 3
cloud_mod.texture = cloud_tex

# Add a second, softer layer of clouds slightly higher
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -9))
clouds2 = bpy.context.active_object
clouds2.name = "SeaOfClouds_Upper"
clouds2.data.materials.append(cloud_mat)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=25)
bpy.ops.object.mode_set(mode='OBJECT')
cloud_mod2 = clouds2.modifiers.new("CloudDisplace2", 'DISPLACE')
cloud_mod2.strength = 3.0
cloud_mod2.mid_level = 0.5
cloud_mod2.texture = cloud_tex

# --- CAMERA ---
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (15, 8, 3)
cam.rotation_euler = (math.radians(75), 0, math.radians(-140))
bpy.context.scene.camera = cam

# --- LIGHTING ---
# Sun light
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_data.color = (1.0, 0.95, 0.85)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(20), 0)

# Fill light
fill_data = bpy.data.lights.new("Fill", type='POINT')
fill_data.energy = 50
fill_data.color = (0.8, 0.85, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (5, -5, 5)

# World background
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.5, 0.7, 1.0, 1.0)
bg.inputs[1].default_value = 1.0
