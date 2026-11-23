import bpy
import math
import random
from mathutils import Vector

# Clean the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Set up world for sunrise
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create sunrise sky - use a gradient background for sunrise colors
bg_node = nodes.new('ShaderNodeBackground')
out_node = nodes.new('ShaderNodeOutputWorld')

# Create a warm sunrise color gradient
# Use a color ramp driven by sky direction
tex_coord = nodes.new('ShaderNodeTexCoord')
sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
map_range = nodes.new('ShaderNodeMapRange')
color_ramp = nodes.new('ShaderNodeValToRGB')

# Map Z (up) to create horizon gradient
links.new(tex_coord.outputs['Generated'], sep_xyz.inputs['Vector'])
links.new(sep_xyz.outputs['Z'], map_range.inputs['Value'])
map_range.inputs['From Min'].default_value = 0.0
map_range.inputs['From Max'].default_value = 1.0
map_range.inputs['To Min'].default_value = 0.0
map_range.inputs['To Max'].default_value = 1.0

# Sunrise colors: warm orange at horizon, blue at top
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[0].color = (1.0, 0.5, 0.2, 1)  # warm orange horizon
color_ramp.color_ramp.elements[1].position = 1.0
color_ramp.color_ramp.elements[1].color = (0.3, 0.5, 0.8, 1)  # blue sky top

# Add a middle stop for the transition
elem_mid = color_ramp.color_ramp.elements.new(0.3)
elem_mid.color = (0.9, 0.6, 0.3, 1)

links.new(map_range.outputs['Result'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bg_node.inputs['Color'])
bg_node.inputs['Strength'].default_value = 1.0
links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])

# Set scene properties
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# Lighting - warm sunrise sun
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_data.color = (1.0, 0.7, 0.4)
sun_data.angle = math.radians(2)
sun_obj = bpy.data.objects.new("Sun", sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(85), 0, math.radians(180))

# Ambient fill light
fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 50
fill_data.color = (0.6, 0.5, 0.4)
fill_data.size = 50
fill_obj = bpy.data.objects.new("Fill", fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.location = (0, 0, 30)
fill_obj.rotation_euler = (0, 0, 0)

# Ground - rocky savanna
def create_ground():
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    mod = ground.modifiers.new("Subdiv", 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 8
    mod.render_levels = 8
    
    tex = bpy.data.textures.new("GroundTex", type='CLOUDS')
    tex.noise_scale = 5.0
    tex.noise_depth = 4
    
    disp_mod = ground.modifiers.new("Displace", 'DISPLACE')
    disp_mod.texture = tex
    disp_mod.strength = 0.5
    disp_mod.mid_level = 0.5
    
    mat = bpy.data.materials.new("GroundMat")
    mat.use_nodes = True
    nodes_m = mat.node_tree.nodes
    links_m = mat.node_tree.links
    
    for node in nodes_m:
        nodes_m.remove(node)
    
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Specular IOR Level'].default_value = 0.1
    
    noise = nodes_m.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 2.0
    noise.inputs['Detail'].default_value = 8.0
    
    color_ramp_m = nodes_m.new('ShaderNodeValToRGB')
    color_ramp_m.color_ramp.elements[0].position = 0.3
    color_ramp_m.color_ramp.elements[0].color = (0.3, 0.2, 0.1, 1)
    color_ramp_m.color_ramp.elements[1].position = 0.7
    color_ramp_m.color_ramp.elements[1].color = (0.45, 0.35, 0.2, 1)
    
    links_m.new(noise.outputs['Fac'], color_ramp_m.inputs['Fac'])
    links_m.new(color_ramp_m.outputs['Color'], bsdf.inputs['Base Color'])
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    ground.data.materials.append(mat)
    return ground

ground = create_ground()

# Monolith
def create_monolith():
    width = 2.0
    height = 8.0
    depth = 0.444
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    monolith = bpy.context.active_object
    monolith.name = "Monolith"
    monolith.scale = (width/2, depth/2, height/2)
    bpy.ops.object.transform_apply(scale=True)
    
    bevel_mod = monolith.modifiers.new("Bevel", 'BEVEL')
    bevel_mod.width = 0.02
    bevel_mod.segments = 3
    
    mat = bpy.data.materials.new("MonolithMat")
    mat.use_nodes = True
    nodes_m = mat.node_tree.nodes
    links_m = mat.node_tree.links
    
    for node in nodes_m:
        nodes_m.remove(node)
    
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Metallic'].default_value = 0.3
    bsdf.inputs['Specular IOR Level'].default_value = 0.8
    bsdf.inputs['Coat Weight'].default_value = 0.5
    bsdf.inputs['Coat Roughness'].default_value = 0.05
    
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    monolith.data.materials.append(mat)
    return monolith

monolith = create_monolith()

# Rocks
def create_rock(location, scale, rotation_z=0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=location)
    rock = bpy.context.active_object
    rock.name = f"Rock_{random.randint(1000,9999)}"
    
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(rock.data)
    for vert in bm.verts:
        vert.co.x += random.uniform(-0.15, 0.15)
        vert.co.y += random.uniform(-0.15, 0.15)
        vert.co.z += random.uniform(-0.1, 0.1)
    bm.to_mesh(rock.data)
    bm.free()
    
    rock.scale = (scale[0], scale[1], scale[2])
    rock.rotation_euler = (0, 0, rotation_z)
    bpy.ops.object.transform_apply(scale=True)
    
    mod = rock.modifiers.new("Subdiv", 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 2
    mod.render_levels = 3
    
    tex = bpy.data.textures.new(f"RockTex_{rock.name}", type='CLOUDS')
    tex.noise_scale = 0.5
    tex.noise_depth = 3
    
    disp_mod = rock.modifiers.new("Displace", 'DISPLACE')
    disp_mod.texture = tex
    disp_mod.strength = 0.1
    
    mat = bpy.data.materials.new(f"RockMat_{rock.name}")
    mat.use_nodes = True
    nodes_m = mat.node_tree.nodes
    links_m = mat.node_tree.links
    
    for node in nodes_m:
        nodes_m.remove(node)
    
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Specular IOR Level'].default_value = 0.05
    
    noise = nodes_m.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 10.0
    
    color_ramp_m = nodes_m.new('ShaderNodeValToRGB')
    color_ramp_m.color_ramp.elements[0].position = 0.3
    color_ramp_m.color_ramp.elements[0].color = (0.25, 0.18, 0.12, 1)
    color_ramp_m.color_ramp.elements[1].position = 0.7
    color_ramp_m.color_ramp.elements[1].color = (0.4, 0.3, 0.2, 1)
    
    links_m.new(noise.outputs['Fac'], color_ramp_m.inputs['Fac'])
    links_m.new(color_ramp_m.outputs['Color'], bsdf.inputs['Base Color'])
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    rock.data.materials.append(mat)
    return rock

rock_positions = [
    ((3, 2, 0.3), (1.5, 1.2, 0.8), 0.5),
    ((-2.5, 3, 0.2), (1.0, 0.8, 0.6), 1.2),
    ((4, -1, 0.25), (1.2, 1.0, 0.7), 2.1),
    ((-3, -2, 0.3), (1.8, 1.4, 0.9), 3.5),
    ((1, 4, 0.2), (0.8, 0.7, 0.5), 0.8),
    ((-1.5, -3.5, 0.25), (1.1, 0.9, 0.65), 4.2),
    ((5, 3, 0.2), (0.9, 0.8, 0.55), 1.5),
    ((-4, 1, 0.3), (1.3, 1.1, 0.75), 2.8),
    ((2, -4, 0.2), (0.7, 0.6, 0.45), 0.3),
    ((-2, 4.5, 0.25), (1.0, 0.9, 0.6), 3.1),
    ((6, -2, 0.3), (1.4, 1.2, 0.85), 4.7),
    ((-5, -1, 0.2), (0.8, 0.7, 0.5), 1.9),
    ((3.5, 4.5, 0.25), (1.1, 0.9, 0.65), 0.6),
    ((-3.5, -4, 0.3), (1.2, 1.0, 0.7), 2.4),
    ((1.5, -5, 0.2), (0.6, 0.5, 0.4), 3.8),
]

for pos, scl, rot in rock_positions:
    create_rock(pos, scl, rot)

for i in range(30):
    angle = random.uniform(0, 2*math.pi)
    dist = random.uniform(4, 15)
    x = math.cos(angle) * dist
    y = math.sin(angle) * dist
    scale = random.uniform(0.2, 0.6)
    create_rock((x, y, scale*0.3), (scale, scale*0.8, scale*0.6), random.uniform(0, 2*math.pi))

# Ape builder
def create_ape(location, rotation_z, scale=1.0, sitting=False):
    objects = []
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.3, location=location)
    body = bpy.context.active_object
    body.name = f"Ape_Body_{random.randint(100,999)}"
    body.scale = (0.8, 0.7, 1.0)
    if sitting:
        body.location.z = location[2] + 0.2
    else:
        body.location.z = location[2] + 0.5
    bpy.ops.object.transform_apply(scale=True)
    
    head_loc = (location[0], location[1], location[2] + (0.7 if not sitting else 0.55))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.2, location=head_loc)
    head = bpy.context.active_object
    head.name = f"Ape_Head_{body.name}"
    head.scale = (0.9, 0.85, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    
    snout_loc = (head_loc[0], head_loc[1] - 0.15, head_loc[2] - 0.05)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.1, location=snout_loc)
    snout = bpy.context.active_object
    snout.name = f"Ape_Snout_{body.name}"
    snout.scale = (0.8, 1.2, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    
    arm_offset = 0.25
    for side in [-1, 1]:
        arm_loc = (location[0] + side*arm_offset, location[1], location[2] + (0.4 if not sitting else 0.3))
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=0.4, location=arm_loc)
        arm = bpy.context.active_object
        arm.name = f"Ape_Arm_{side}_{body.name}"
        arm.rotation_euler = (math.radians(20*side), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        objects.append(arm)
    
    if not sitting:
        for side in [-1, 1]:
            leg_loc = (location[0] + side*0.12, location[1], location[2] + 0.15)
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=0.35, location=leg_loc)
            leg = bpy.context.active_object
            leg.name = f"Ape_Leg_{side}_{body.name}"
            bpy.ops.object.transform_apply()
            objects.append(leg)
    else:
        for side in [-1, 1]:
            leg_loc = (location[0] + side*0.2, location[1] - 0.1, location[2] + 0.05)
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=0.3, location=leg_loc)
            leg = bpy.context.active_object
            leg.name = f"Ape_Leg_{side}_{body.name}"
            leg.rotation_euler = (math.radians(30*side), 0, 0)
            bpy.ops.object.transform_apply(rotation=True)
            objects.append(leg)
    
    all_parts = [body, head, snout] + objects
    for part in all_parts:
        part.rotation_euler = (0, 0, rotation_z)
    
    for part in all_parts:
        part.scale = (scale, scale, scale)
        bpy.context.view_layer.objects.active = part
        bpy.ops.object.transform_apply(scale=True)
    
    mat = bpy.data.materials.new(f"ApeMat_{body.name}")
    mat.use_nodes = True
    nodes_m = mat.node_tree.nodes
    links_m = mat.node_tree.links
    
    for node in nodes_m:
        nodes_m.remove(node)
    
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Specular IOR Level'].default_value = 0.1
    
    noise = nodes_m.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 8.0
    
    color_ramp_m = nodes_m.new('ShaderNodeValToRGB')
    color_ramp_m.color_ramp.elements[0].position = 0.3
    color_ramp_m.color_ramp.elements[0].color = (0.15, 0.08, 0.04, 1)
    color_ramp_m.color_ramp.elements[1].position = 0.7
    color_ramp_m.color_ramp.elements[1].color = (0.25, 0.15, 0.08, 1)
    
    links_m.new(noise.outputs['Fac'], color_ramp_m.inputs['Fac'])
    links_m.new(color_ramp_m.outputs['Color'], bsdf.inputs['Base Color'])
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    for part in all_parts:
        part.data.materials.clear()
        part.data.materials.append(mat)
    
    return all_parts

ape_positions = [
    ((1.5, 2.5, 0), math.radians(160), 1.0, False),
    ((-1.5, 2.5, 0), math.radians(200), 1.0, False),
    ((0.5, 3.0, 0), math.radians(180), 0.9, True),
    ((-0.5, 3.0, 0), math.radians(180), 0.95, False),
    ((2.5, 1.5, 0), math.radians(140), 1.0, False),
    ((-2.5, 1.5, 0), math.radians(220), 1.05, False),
    ((1.0, 1.0, 0), math.radians(170), 0.85, True),
    ((-1.0, 1.0, 0), math.radians(190), 0.9, False),
    ((3.0, 0, 0), math.radians(120), 1.0, False),
    ((-3.0, 0, 0), math.radians(240), 1.0, False),
    ((2.0, -1.0, 0), math.radians(100), 0.95, True),
    ((-2.0, -1.0, 0), math.radians(260), 1.0, False),
    ((3.5, -2.0, 0), math.radians(80), 1.0, False),
    ((-3.5, -2.0, 0), math.radians(280), 1.05, False),
    ((2.5, 3.5, 0), math.radians(150), 0.9, True),
    ((-2.5, 3.5, 0), math.radians(210), 1.0, False),
    ((4.5, 1.0, 0), math.radians(130), 0.95, False),
    ((-4.5, 1.0, 0), math.radians(230), 1.0, False),
    ((4.0, -1.5, 0), math.radians(110), 0.9, True),
    ((-4.0, -1.5, 0), math.radians(250), 1.0, False),
]

for pos, rot, scl, sit in ape_positions:
    create_ape(pos, rot, scl, sit)

# Grass tufts
def create_grass_tuft(location):
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.05, radius2=0.0, depth=0.3, location=location)
    grass = bpy.context.active_object
    grass.name = f"Grass_{random.randint(100,999)}"
    grass.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), 0)
    
    mat = bpy.data.materials.new(f"GrassMat_{grass.name}")
    mat.use_nodes = True
    nodes_m = mat.node_tree.nodes
    links_m = mat.node_tree.links
    
    for node in nodes_m:
        nodes_m.remove(node)
    
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.5, 0.4, 0.15, 1)
    bsdf.inputs['Roughness'].default_value = 0.9
    
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    grass.data.materials.append(mat)
    return grass

for i in range(50):
    angle = random.uniform(0, 2*math.pi)
    dist = random.uniform(2, 12)
    x = math.cos(angle) * dist
    y = math.sin(angle) * dist
    if abs(x) > 2 and abs(y) > 2:
        create_grass_tuft((x, y, 0.15))

# Camera
bpy.ops.object.camera_add(location=(8, 12, 1.5))
camera = bpy.context.active_object
camera.name = "MainCamera"

target = Vector((0, 0, 4))
direction = target - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

scene.camera = camera
camera.data.lens = 50
camera.data.sensor_width = 36
scene.render.resolution_percentage = 100

print("Scene built successfully!")
print(f"Objects in scene: {len(bpy.data.objects)}")
