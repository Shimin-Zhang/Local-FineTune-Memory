import bpy
import math
import random
from mathutils import Vector, noise

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.data.meshes.clear()
bpy.data.materials.clear()
bpy.data.cameras.clear()
bpy.data.lights.clear()

# --- Materials ---
def create_material(name, base_color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_sand = create_material("Sand", (0.75, 0.65, 0.45, 1.0), roughness=0.9)
mat_pavement = create_material("Pavement", (0.35, 0.35, 0.38, 1.0), roughness=0.7)
mat_water = create_material("Water", (0.1, 0.3, 0.4, 1.0), roughness=0.1, metallic=0.1)
mat_water.alpha = 0.6
mat_wood = create_material("Wood", (0.35, 0.2, 0.1, 1.0), roughness=0.8)
mat_metal = create_material("Metal", (0.5, 0.5, 0.5, 1.0), roughness=0.3, metallic=0.8)
mat_red = create_material("Red", (0.8, 0.1, 0.1, 1.0), roughness=0.5)
mat_white = create_material("White", (0.9, 0.9, 0.9, 1.0), roughness=0.5)

# --- Tidal Sand Ground ---
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
sand_obj = bpy.context.active_object
sand_obj.name = "TidalSands"
sand_obj.data.materials.append(mat_sand)

# Displace sand with noise
subdiv = sand_obj.modifiers.new("Subdiv", 'SUBSURF')
subdiv.subdivision_type = 'SIMPLE'
subdiv.levels = 6
subdiv.render_levels = 6

tex = bpy.data.textures.new("SandNoise", type='CLOUDS')
tex.noise_scale = 15.0
disp = sand_obj.modifiers.new("Displace", 'DISPLACE')
disp.texture = tex
disp.strength = 0.8
disp.mid_level = 0.5

# --- Paved Road ---
# Road runs along Y axis from y=-80 to y=80, width 8
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.15))
road_obj = bpy.context.active_object
road_obj.name = "Road"
road_obj.scale = (4, 80, 1)
bpy.ops.object.transform_apply(scale=True)
road_obj.data.materials.append(mat_pavement)

# Add subtle bump to road
subdiv_road = road_obj.modifiers.new("Subdiv", 'SUBSURF')
subdiv_road.subdivision_type = 'SIMPLE'
subdiv_road.levels = 4
tex_road = bpy.data.textures.new("RoadNoise", type='CLOUDS')
tex_road.noise_scale = 2.0
disp_road = road_obj.modifiers.new("Displace", 'DISPLACE')
disp_road.texture = tex_road
disp_road.strength = 0.05

# --- Water Creeping Across Pavement ---
# Shallow water pool on the road
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -10, 0.22))
water_obj = bpy.context.active_object
water_obj.name = "WaterPool"
water_obj.scale = (3.5, 25, 1)
bpy.ops.object.transform_apply(scale=True)
water_obj.data.materials.append(mat_water)

# Another smaller water patch
bpy.ops.mesh.primitive_plane_add(size=1, location=(1.5, 20, 0.22))
water_obj2 = bpy.context.active_object
water_obj2.name = "WaterPatch2"
water_obj2.scale = (2, 10, 1)
bpy.ops.object.transform_apply(scale=True)
water_obj2.data.materials.append(mat_water)

# --- Island at the end ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=15, location=(0, 85, -2), segments=32, ring_count=16)
island_obj = bpy.context.active_object
island_obj.name = "Island"
island_obj.scale = (1.2, 1.0, 0.4)
bpy.ops.object.transform_apply(scale=True)
island_obj.data.materials.append(mat_sand)

# Flatten top of island
island_obj.modifiers.new("Subdiv", 'SUBSURF').subdivision_type = 'SIMPLE'
island_obj.modifiers["Subdiv"].levels = 4
tex_island = bpy.data.textures.new("IslandNoise", type='CLOUDS')
tex_island.noise_scale = 8.0
disp_island = island_obj.modifiers.new("Displace", 'DISPLACE')
disp_island.texture = tex_island
disp_island.strength = 1.5

# --- Refuge Posts on Stilts ---
def create_refuge_post(x, y, z_base, height=3.0, post_height=2.0):
    """Create a refuge post on stilts"""
    # Stilts (4 legs)
    stilt_positions = [(-0.8, -0.8), (0.8, -0.8), (-0.8, 0.8), (0.8, 0.8)]
    for sx, sy in stilt_positions:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=height, location=(x + sx, y + sy, z_base + height/2))
        stilt = bpy.context.active_object
        stilt.name = f"Stilt_{x}_{y}_{sx}_{sy}"
        stilt.data.materials.append(mat_wood)

    # Platform
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z_base + height))
    platform = bpy.context.active_object
    platform.name = f"Platform_{x}_{y}"
    platform.scale = (2.0, 2.0, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    platform.data.materials.append(mat_wood)

    # Roof (simple pyramid)
    bpy.ops.mesh.primitive_cone_add(radius=1.8, depth=1.2, location=(x, y, z_base + height + 0.6 + 0.6), vertices=4)
    roof = bpy.context.active_object
    roof.name = f"Roof_{x}_{y}"
    roof.rotation_euler[2] = math.radians(45)
    roof.data.materials.append(mat_wood)

    # Small shelter walls
    for side in range(4):
        angle = math.radians(45 + side * 90)
        wx = x + 1.3 * math.cos(angle)
        wy = y + 1.3 * math.sin(angle)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(wx, wy, z_base + height + 0.6))
        wall = bpy.context.active_object
        wall.name = f"Wall_{x}_{y}_{side}"
        wall.scale = (0.08, 1.8, 0.5)
        wall.rotation_euler[2] = angle
        bpy.ops.object.transform_apply(scale=True)
        wall.data.materials.append(mat_wood)

# Place refuge posts
create_refuge_post(-6, -30, 0.0)
create_refuge_post(6, -15, 0.0)
create_refuge_post(-6, 10, 0.0)
create_refuge_post(6, 35, 0.0)

# --- Marker Poles ---
def create_marker_pole(x, y, z_base, height=2.5, color=mat_red):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=height, location=(x, y, z_base + height/2))
    pole = bpy.context.active_object
    pole.name = f"MarkerPole_{x}_{y}"
    pole.data.materials.append(mat_metal)

    # Top marker ball
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x, y, z_base + height), segments=16, ring_count=8)
    ball = bpy.context.active_object
    ball.name = f"MarkerBall_{x}_{y}"
    ball.data.materials.append(color)

# Place marker poles along the road
marker_positions = [
    (-3.5, -60, mat_red), (3.5, -60, mat_white),
    (-3.5, -40, mat_red), (3.5, -40, mat_white),
    (-3.5, -20, mat_red), (3.5, -20, mat_white),
    (-3.5, 0, mat_red), (3.5, 0, mat_white),
    (-3.5, 20, mat_red), (3.5, 20, mat_white),
    (-3.5, 40, mat_red), (3.5, 40, mat_white),
    (-3.5, 60, mat_red), (3.5, 60, mat_white),
]

for x, y, color in marker_positions:
    create_marker_pole(x, y, 0.15, 2.5, color)

# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0, -70, 8)
cam_obj.rotation_euler = (math.radians(85), 0, 0)
bpy.context.scene.camera = cam_obj

# --- Lighting ---
# Sun
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_data.angle = math.radians(5)
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(45), math.radians(10), math.radians(30))

# Fill light
fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 50
fill_data.size = 20
fill_obj = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (0, -50, 20)
fill_obj.rotation_euler = (0, 0, 0)

# --- World / Sky ---
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.4, 0.6, 0.8, 1.0)  # Light blue sky
    bg.inputs[1].default_value = 1.0

# --- Render Settings ---
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.cycles.samples = 128
scene.cycles.use_denoising = True

print("Scene created: Paved road across tidal sands to island with refuge posts, marker poles, and water on pavement.")
