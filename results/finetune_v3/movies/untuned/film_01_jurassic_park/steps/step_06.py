import bpy
import math
import random
from mathutils import Vector

# Clean scene completely
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- MATERIALS ---
def make_mat(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (emission[0], emission[1], emission[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

mat_grass = make_mat("Grass", (0.05, 0.15, 0.02), 0.9)
mat_dirt = make_mat("Dirt", (0.15, 0.1, 0.05), 0.95)
mat_rock = make_mat("Rock", (0.3, 0.28, 0.25), 0.8)
mat_wood = make_mat("Wood", (0.2, 0.12, 0.05), 0.7)
mat_metal = make_mat("Metal", (0.4, 0.4, 0.42), 0.3, 0.8)
mat_metal_dark = make_mat("MetalDark", (0.15, 0.15, 0.17), 0.4, 0.9)
mat_car_body = make_mat("CarBody", (0.6, 0.6, 0.62), 0.2, 0.5)
mat_car_dark = make_mat("CarDark", (0.1, 0.1, 0.12), 0.3, 0.6)
mat_glass = make_mat("Glass", (0.7, 0.8, 0.9), 0.1, 0.0)
mat_headlight = make_mat("Headlight", (1.0, 0.95, 0.7), 0.1, 0.0, emission=(1.0, 0.95, 0.7), emission_strength=8.0)
mat_taillight = make_mat("Taillight", (1.0, 0.1, 0.05), 0.2, 0.0, emission=(1.0, 0.1, 0.05), emission_strength=5.0)
mat_skin = make_mat("TRexSkin", (0.15, 0.12, 0.08), 0.7)
mat_eye = make_mat("TRexEye", (0.9, 0.8, 0.3), 0.1, 0.0, emission=(0.9, 0.8, 0.3), emission_strength=3.0)
mat_tooth = make_mat("Tooth", (0.9, 0.88, 0.8), 0.3)
mat_rain = make_mat("Rain", (0.7, 0.8, 1.0), 0.0, 0.0, emission=(0.5, 0.6, 1.0), emission_strength=0.3)
mat_sign = make_mat("Sign", (0.8, 0.8, 0.7), 0.5)
mat_rubber = make_mat("Rubber", (0.05, 0.05, 0.05), 0.9)
mat_concrete = make_mat("Concrete", (0.4, 0.4, 0.38), 0.8)
mat_puddle = make_mat("Puddle", (0.1, 0.12, 0.15), 0.05, 0.0)
mat_wire = make_mat("Wire", (0.5, 0.5, 0.5), 0.3, 0.9)
mat_blood = make_mat("Blood", (0.3, 0.02, 0.02), 0.4)
mat_moon = make_mat("Moon", (0.9, 0.9, 1.0), 0.0, 0.0, emission=(0.8, 0.8, 1.0), emission_strength=5.0)
mat_tree = make_mat("Tree", (0.08, 0.15, 0.05), 0.9)
mat_trunk = make_mat("Trunk", (0.15, 0.1, 0.05), 0.8)
mat_rain_splash = make_mat("RainSplash", (0.6, 0.7, 0.9), 0.0, 0.0, emission=(0.4, 0.5, 0.8), emission_strength=0.5)

# --- GROUND ---
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.active_object
ground.data.materials.append(mat_grass)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=50)
bpy.ops.object.mode_set(mode='OBJECT')
tex = bpy.data.textures.new("GroundNoise", type='CLOUDS')
tex.noise_scale = 2.0
disp = ground.modifiers.new("Disp", 'DISPLACE')
disp.texture = tex
disp.strength = 0.5
disp.mid_level = 0.5

# --- ROAD ---
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.02))
road = bpy.context.active_object
road.scale = (8, 60, 1)
road.data.materials.append(mat_concrete)
bpy.ops.object.transform_apply(scale=True)

for i in range(-50, 51, 10):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, i, 0.03))
    mark = bpy.context.active_object
    mark.scale = (0.3, 3, 1)
    mark.data.materials.append(mat_sign)
    bpy.ops.object.transform_apply(scale=True)

# --- PADDICK FENCE ---
for i in range(-20, 21, 4):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.5, location=(-10, i, 1.25))
    post = bpy.context.active_object
    post.data.materials.append(mat_metal_dark)
    if i in [-4, 0, 4]:
        post.rotation_euler[0] = random.uniform(-0.3, 0.3)
        post.rotation_euler[2] = random.uniform(-0.2, 0.2)

for h in [0.5, 1.0, 1.5, 2.0, 2.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=40, location=(-10, 0, h), rotation=(0, math.pi/2, 0))
    wire = bpy.context.active_object
    wire.data.materials.append(mat_wire)
    if h in [1.0, 1.5]:
        bpy.ops.object.delete()
        for seg in range(-20, 20, 4):
            if random.random() > 0.3:
                bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=3, location=(-10, seg+2, h), rotation=(0, math.pi/2, 0))
                w = bpy.context.active_object
                w.data.materials.append(mat_wire)
                if random.random() > 0.5:
                    w.rotation_euler[2] = random.uniform(-0.5, 0.5)

for i in range(5):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=random.uniform(1, 3), location=(-10+random.uniform(-2,2), random.uniform(-5,5), 0.05), rotation=(random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)))
    piece = bpy.context.active_object
    piece.data.materials.append(mat_wire)

# --- TOUR CARS ---
def build_car(location, rotation=0, color=mat_car_body):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    body = bpy.context.active_object
    body.scale = (2.2, 4.5, 1.2)
    body.rotation_euler[2] = rotation
    body.data.materials.append(color)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1]-0.5, location[2]+0.8))
    cabin = bpy.context.active_object
    cabin.scale = (1.8, 2.5, 0.8)
    cabin.rotation_euler[2] = rotation
    cabin.data.materials.append(color)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.mesh.primitive_plane_add(size=1, location=(location[0], location[1]-2.0, location[2]+0.8))
    ws = bpy.context.active_object
    ws.scale = (1.5, 0.1, 0.6)
    ws.rotation_euler = (math.radians(-30), 0, rotation)
    ws.data.materials.append(mat_glass)
    bpy.ops.object.transform_apply(scale=True)
    
    for wx in [-1.0, 1.0]:
        for wy in [-1.5, 1.5]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.3, location=(location[0]+wx, location[1]+wy, location[2]-0.3), rotation=(0, math.pi/2, 0))
            wheel = bpy.context.active_object
            wheel.data.materials.append(mat_rubber)
    
    for hx in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(location[0]+hx, location[1]-2.25, location[2]))
        hl = bpy.context.active_object
        hl.data.materials.append(mat_headlight)
    
    for tx in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(location[0]+tx, location[1]+2.25, location[2]))
        tl = bpy.context.active_object
        tl.data.materials.append(mat_taillight)
    
    return body

car1 = build_car((3, -5, 0.6), rotation=math.radians(10), color=mat_car_body)
car2 = build_car((5, 5, 0.6), rotation=math.radians(-5), color=mat_car_dark)

# --- T. REX ---
def build_trex(location, scale=1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(location[0], location[1], location[2]+1.5))
    body = bpy.context.active_object
    body.scale = (1.2, 2.0, 1.0)
    body.data.materials.append(mat_skin)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0.5, depth=2.0, location=(location[0], location[1]-2.0, location[2]+2.5))
    neck = bpy.context.active_object
    neck.rotation_euler[0] = math.radians(30)
    neck.data.materials.append(mat_skin)
    bpy.ops.object.transform_apply(rotation=True)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(location[0], location[1]-3.5, location[2]+3.0))
    head = bpy.context.active_object
    head.scale = (0.8, 1.5, 0.7)
    head.data.materials.append(mat_skin)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1]-3.8, location[2]+2.5))
    jaw = bpy.context.active_object
    jaw.scale = (0.6, 1.2, 0.3)
    jaw.rotation_euler[0] = math.radians(15)
    jaw.data.materials.append(mat_skin)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    
    for ex in [-0.3, 0.3]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(location[0]+ex, location[1]-4.0, location[2]+3.2))
        eye = bpy.context.active_object
        eye.data.materials.append(mat_eye)
    
    for i in range(8):
        tx = location[0] - 0.4 + i * 0.12
        ty = location[1] - 4.2
        tz = location[2] + 2.8
        bpy.ops.mesh.primitive_cone_add(radius1=0.03, radius2=0.0, depth=0.2, location=(tx, ty, tz))
        tooth = bpy.context.active_object
        tooth.rotation_euler[0] = math.radians(180)
        tooth.data.materials.append(mat_tooth)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.6, radius2=0.1, depth=3.0, location=(location[0], location[1]+2.5, location[2]+1.2), rotation=(math.radians(-10), 0, 0))
    tail = bpy.context.active_object
    tail.data.materials.append(mat_skin)
    bpy.ops.object.transform_apply(rotation=True)
    
    for lx in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.5, location=(location[0]+lx, location[1]+0.5, location[2]+0.5))
        ul = bpy.context.active_object
        ul.data.materials.append(mat_skin)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.2, location=(location[0]+lx, location[1]+0.3, location[2]-0.3))
        ll = bpy.context.active_object
        ll.data.materials.append(mat_skin)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0]+lx, location[1]-0.2, location[2]-0.8))
        foot = bpy.context.active_object
        foot.scale = (0.5, 0.8, 0.2)
        foot.data.materials.append(mat_skin)
        bpy.ops.object.transform_apply(scale=True)
    
    for ax in [-0.5, 0.5]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.6, location=(location[0]+ax, location[1]-1.5, location[2]+1.0), rotation=(math.radians(45), 0, 0))
        arm = bpy.context.active_object
        arm.data.materials.append(mat_skin)
    
    return body

trex = build_trex((-8, 0, 0), scale=1.0)

# --- RAIN ---
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 20))
rain_plane = bpy.context.active_object
rain_plane.data.materials.append(mat_rain)
rain_plane.display_type = 'WIRE'

psys = rain_plane.modifiers.new("Rain", 'PARTICLE_SYSTEM')
psys.particle_system.settings.count = 5000
psys.particle_system.settings.frame_start = 1
psys.particle_system.settings.frame_end = 250
psys.particle_system.settings.lifetime = 30
psys.particle_system.settings.emit_from = 'FACE'
psys.particle_system.settings.normal_factor = 0
psys.particle_system.settings.factor_random = 0
psys.particle_system.settings.effector_weights.gravity = 1.0
psys.particle_system.settings.render_type = 'OBJECT'

bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.3, location=(0, 0, 0))
rain_drop = bpy.context.active_object
rain_drop.data.materials.append(mat_rain)
psys.particle_system.settings.instance_object = rain_drop

# --- LIGHTING ---
bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
sun = bpy.context.active_object
sun.data.energy = 1.0
sun.data.color = (0.6, 0.7, 1.0)
sun.rotation_euler = (math.radians(30), math.radians(10), 0)

bpy.ops.mesh.primitive_uv_sphere_add(radius=2, location=(30, 40, 40))
moon_obj = bpy.context.active_object
moon_obj.data.materials.append(mat_moon)

bpy.ops.object.light_add(type='SPOT', location=(3, -7.5, 0.6))
hl1 = bpy.context.active_object
hl1.data.energy = 1500
hl1.data.color = (1.0, 0.95, 0.7)
hl1.data.spot_size = math.radians(35)
hl1.data.spot_blend = 0.5
hl1.rotation_euler = (math.radians(80), 0, math.radians(10))

bpy.ops.object.light_add(type='SPOT', location=(5, 2.5, 0.6))
hl2 = bpy.context.active_object
hl2.data.energy = 1200
hl2.data.color = (1.0, 0.95, 0.7)
hl2.data.spot_size = math.radians(35)
hl2.data.spot_blend = 0.5
hl2.rotation_euler = (math.radians(80), 0, math.radians(-5))

bpy.ops.object.light_add(type='AREA', location=(0, 0, 10))
amb = bpy.context.active_object
amb.data.energy = 20
amb.data.color = (0.3, 0.4, 0.6)
amb.data.size = 50

# --- WORLD ---
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.02, 0.03, 0.05, 1.0)
bg.inputs[1].default_value = 1.0

# --- CAMERA ---
bpy.ops.object.camera_add(location=(18, -12, 4))
cam = bpy.context.active_object
bpy.context.scene.camera = cam
target = Vector((-8, 0, 1.5))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
cam.data.lens = 50

# --- DETAILS ---
for i in range(12):
    px = random.uniform(-3, 3)
    py = random.uniform(-15, 15)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(px, py, 0.04))
    puddle = bpy.context.active_object
    puddle.scale = (random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), 1)
    puddle.data.materials.append(mat_puddle)
    bpy.ops.object.transform_apply(scale=True)

for i in range(25):
    rx = random.uniform(-15, 15)
    ry = random.uniform(-20, 20)
    if abs(rx) < 5:
        continue
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(0.1, 0.4), location=(rx, ry, 0.1))
    rock = bpy.context.active_object
    rock.scale = (random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), random.uniform(0.3, 0.8))
    rock.data.materials.append(mat_rock)
    bpy.ops.object.transform_apply(scale=True)

for i in range(8):
    tx = random.uniform(-12, -5)
    ty = random.uniform(-10, 10)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=random.uniform(3, 6), location=(tx, ty, 0.1), rotation=(random.uniform(0, 0.3), random.uniform(