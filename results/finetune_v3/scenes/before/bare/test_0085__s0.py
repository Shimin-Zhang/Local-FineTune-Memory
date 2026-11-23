import bpy
import math
import random
from mathutils import Vector, Matrix

# --- Clean scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# --- Collections ---
def get_or_create_collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

col_court = get_or_create_collection("Court")
col_glass = get_or_create_collection("GlassWalls")
col_net = get_or_create_collection("Net")
col_floodlights = get_or_create_collection("Floodlights")
col_benches = get_or_create_collection("Benches")
col_cooler = get_or_create_collection("DrinksCooler")
col_city = get_or_create_collection("CityLights")
col_rooftop = get_or_create_collection("Rooftop")

def link_to_collection(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)

# --- Materials ---
def make_material(name, color, metallic=0.0, roughness=0.5, transmission=0.0, alpha=1.0, emission=0.0, emission_color=(1,1,1,1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if transmission > 0:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        bsdf.inputs["Alpha"].default_value = alpha
    if emission > 0:
        bsdf.inputs["Emission Strength"].default_value = emission
        bsdf.inputs["Emission Color"].default_value = emission_color
    return mat

mat_asphalt = make_material("Asphalt", (0.05, 0.05, 0.05, 1), roughness=0.9)
mat_court_surface = make_material("CourtSurface", (0.0, 0.4, 0.8, 1), roughness=0.7)
mat_court_lines = make_material("CourtLines", (1, 1, 1, 1), roughness=0.5)
mat_glass = make_material("Glass", (0.9, 0.95, 1, 1), transmission=0.95, roughness=0.05, alpha=0.3)
mat_metal = make_material("Metal", (0.6, 0.6, 0.6, 1), metallic=0.9, roughness=0.3)
mat_net = make_material("Net", (0.9, 0.9, 0.9, 1), roughness=0.8, alpha=0.4)
mat_bench = make_material("Bench", (0.3, 0.2, 0.1, 1), roughness=0.7)
mat_bench_metal = make_material("BenchMetal", (0.4, 0.4, 0.4, 1), metallic=0.8, roughness=0.4)
mat_cooler_body = make_material("CoolerBody", (0.8, 0.8, 0.8, 1), metallic=0.3, roughness=0.4)
mat_cooler_glass = make_material("CoolerGlass", (0.9, 0.95, 1, 1), transmission=0.9, roughness=0.1, alpha=0.4)
mat_floodlight_pole = make_material("FloodlightPole", (0.2, 0.2, 0.2, 1), metallic=0.7, roughness=0.4)
mat_floodlight_head = make_material("FloodlightHead", (0.1, 0.1, 0.1, 1), metallic=0.5, roughness=0.5)
mat_floodlight_bulb = make_material("FloodlightBulb", (1, 1, 1, 1), emission=50.0, emission_color=(1, 0.95, 0.8, 1))
mat_city_building = make_material("CityBuilding", (0.05, 0.05, 0.08, 1), roughness=0.8)
mat_city_window = make_material("CityWindow", (1, 0.8, 0.3, 1), emission=2.0, emission_color=(1, 0.8, 0.3, 1))
mat_rooftop_edge = make_material("RooftopEdge", (0.15, 0.15, 0.15, 1), roughness=0.9)

# --- Rooftop platform ---
# Main platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.5))
platform = bpy.context.object
platform.name = "RooftopPlatform"
platform.scale = (20, 15, 1)  # 40m x 30m platform
platform.data.materials.append(mat_asphalt)
link_to_collection(platform, col_rooftop)

# Parapet walls around the edge
parapet_height = 1.2
parapet_thickness = 0.3
# North wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, 0.6))
p_n = bpy.context.object
p_n.name = "Parapet_N"
p_n.scale = (20, parapet_thickness/2, parapet_height/2)
p_n.data.materials.append(mat_rooftop_edge)
link_to_collection(p_n, col_rooftop)

# South wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -15, 0.6))
p_s = bpy.context.object
p_s.name = "Parapet_S"
p_s.scale = (20, parapet_thickness/2, parapet_height/2)
p_s.data.materials.append(mat_rooftop_edge)
link_to_collection(p_s, col_rooftop)

# East wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(20, 0, 0.6))
p_e = bpy.context.object
p_e.name = "Parapet_E"
p_e.scale = (parapet_thickness/2, 15, parapet_height/2)
p_e.data.materials.append(mat_rooftop_edge)
link_to_collection(p_e, col_rooftop)

# West wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(-20, 0, 0.6))
p_w = bpy.context.object
p_w.name = "Parapet_W"
p_w.scale = (parapet_thickness/2, 15, parapet_height/2)
p_w.data.materials.append(mat_rooftop_edge)
link_to_collection(p_w, col_rooftop)

# --- Padel Court ---
# Standard padel court: 20m x 10m
court_length = 20
court_width = 10
court_height = 4  # glass wall height

# Court floor
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.01))
floor = bpy.context.object
floor.name = "CourtFloor"
floor.scale = (court_length/2, court_width/2, 1)
floor.data.materials.append(mat_court_surface)
link_to_collection(floor, col_court)

# Court lines
def add_line(x1, y1, x2, y2, width=0.1, z=0.02):
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    angle = math.atan2(dy, dx)
    bpy.ops.mesh.primitive_plane_add(size=1, location=((x1+x2)/2, (y1+y2)/2, z))
    line = bpy.context.object
    line.scale = (length/2, width/2, 1)
    line.rotation_euler[2] = angle
    line.data.materials.append(mat_court_lines)
    link_to_collection(line, col_court)
    return line

# Boundary lines
add_line(-court_length/2, -court_width/2, court_length/2, -court_width/2)  # bottom
add_line(-court_length/2, court_width/2, court_length/2, court_width/2)    # top
add_line(-court_length/2, -court_width/2, -court_length/2, court_width/2)  # left
add_line(court_length/2, -court_width/2, court_length/2, court_width/2)    # right

# Service lines
service_dist = 6.65  # from net
add_line(-court_length/2, -service_dist, court_length/2, -service_dist)
add_line(-court_length/2, service_dist, court_length/2, service_dist)

# Center line
add_line(0, -service_dist, 0, service_dist)

# --- Glass Walls ---
glass_height = 4
glass_thickness = 0.05

# Four glass walls
# North wall (y = court_width/2)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, court_width/2, glass_height/2))
g_n = bpy.context.object
g_n.name = "GlassWall_N"
g_n.scale = (court_length/2, glass_thickness/2, glass_height/2)
g_n.data.materials.append(mat_glass)
link_to_collection(g_n, col_glass)

# South wall (y = -court_width/2)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -court_width/2, glass_height/2))
g_s = bpy.context.object
g_s.name = "GlassWall_S"
g_s.scale = (court_length/2, glass_thickness/2, glass_height/2)
g_s.data.materials.append(mat_glass)
link_to_collection(g_s, col_glass)

# East wall (x = court_length/2)
bpy.ops.mesh.primitive_cube_add(size=1, location=(court_length/2, 0, glass_height/2))
g_e = bpy.context.object
g_e.name = "GlassWall_E"
g_e.scale = (glass_thickness/2, court_width/2, glass_height/2)
g_e.data.materials.append(mat_glass)
link_to_collection(g_e, col_glass)

# West wall (x = -court_length/2)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-court_length/2, 0, glass_height/2))
g_w = bpy.context.object
g_w.name = "GlassWall_W"
g_w.scale = (glass_thickness/2, court_width/2, glass_height/2)
g_w.data.materials.append(mat_glass)
link_to_collection(g_w, col_glass)

# Metal frames for glass walls
frame_width = 0.1
# Vertical posts at corners and midpoints
def add_frame_post(x, y, height):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height/2))
    post = bpy.context.object
    post.name = f"FramePost_{x}_{y}"
    post.scale = (frame_width/2, frame_width/2, height/2)
    post.data.materials.append(mat_metal)
    link_to_collection(post, col_glass)

# Corner posts
add_frame_post(-court_length/2, -court_width/2, glass_height)
add_frame_post(court_length/2, -court_width/2, glass_height)
add_frame_post(-court_length/2, court_width/2, glass_height)
add_frame_post(court_length/2, court_width/2, glass_height)

# Midpoint posts on long sides
add_frame_post(0, -court_width/2, glass_height)
add_frame_post(0, court_width/2, glass_height)

# Top and bottom rails
def add_rail(x1, y1, x2, y2, z, width=frame_width):
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    angle = math.atan2(dy, dx)
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x1+x2)/2, (y1+y2)/2, z))
    rail = bpy.context.object
    rail.scale = (length/2, width/2, width/2)
    rail.rotation_euler[2] = angle
    rail.data.materials.append(mat_metal)
    link_to_collection(rail, col_glass)

# Bottom rails
add_rail(-court_length/2, -court_width/2, court_length/2, -court_width/2, 0.05)
add_rail(-court_length/2, court_width/2, court_length/2, court_width/2, 0.05)
add_rail(-court_length/2, -court_width/2, -court_length/2, court_width/2, 0.05)
add_rail(court_length/2, -court_width/2, court_length/2, court_width/2, 0.05)

# Top rails
add_rail(-court_length/2, -court_width/2, court_length/2, -court_width/2, glass_height)
add_rail(-court_length/2, court_width/2, court_length/2, court_width/2, glass_height)
add_rail(-court_length/2, -court_width/2, -court_length/2, court_width/2, glass_height)
add_rail(court_length/2, -court_width/2, court_length/2, court_width/2, glass_height)

# --- Net ---
net_height = 0.88  # at posts
net_center_height = 0.82
net_width = court_width + 1  # extends beyond court
net_depth = 0.1

# Net posts
post_height = 1.0
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=post_height, location=(-0.5, -court_width/2 - 0.5, post_height/2))
post_l = bpy.context.object
post_l.name = "NetPost_L"
post_l.data.materials.append(mat_metal)
link_to_collection(post_l, col_net)

bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=post_height, location=(-0.5, court_width/2 + 0.5, post_height/2))
post_r = bpy.context.object
post_r.name = "NetPost_R"
post_r.data.materials.append(mat_metal)
link_to_collection(post_r, col_net)

# Net mesh (simple plane)
bpy.ops.mesh.primitive_plane_add(size=1, location=(-0.5, 0, net_center_height))
net = bpy.context.object
net.name = "Net"
net.scale = (net_depth/2, net_width/2, 1)
net.rotation_euler[0] = math.pi/2
net.data.materials.append(mat_net)
link_to_collection(net, col_net)

# Net band (top edge)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5, 0, net_height))
band = bpy.context.object
band.name = "NetBand"
band.scale = (net_depth/2, net_width/2, 0.03)
band.data.materials.append(mat_court_lines)
link_to_collection(band, col_net)

# --- Floodlights ---
floodlight_positions = [
    (-court_length/2 - 3, -court_width/2 - 3),
    (court_length/2 + 3, -court_width/2 - 3),
    (-court_length/2 - 3, court_width/2 + 3),
    (court_length/2 + 3, court_width/2 + 3),
]

for i, (fx, fy) in enumerate(floodlight_positions):
    # Pole
    pole_height = 8
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=pole_height, location=(fx, fy, pole_height/2))
    pole = bpy.context.object
    pole.name = f"FloodlightPole_{i}"
    pole.data.materials.append(mat_floodlight_pole)
    link_to_collection(pole, col_floodlights)

    # Head (box)
    head_size = 0.8
    bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, fy, pole_height + head_size/2))
    head = bpy.context.object
    head.name = f"FloodlightHead_{i}"
    head.scale = (head_size/2, head_size/2, head_size/2)
    head.data.materials.append(mat_floodlight_head)
    link_to_collection(head, col_floodlights)

    # Bulb (emissive sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(fx, fy, pole_height + head_size/2))
    bulb = bpy.context.object
    bulb.name = f"FloodlightBulb_{i}"
    bulb.data.materials.append(mat_floodlight_bulb)
    link_to_collection(bulb, col_floodlights)

    # Point light for illumination
    light_data = bpy.data.lights.new(name=f"Flood