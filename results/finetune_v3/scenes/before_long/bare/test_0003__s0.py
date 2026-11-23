import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- MATERIALS ---
def get_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

mat_snow = get_material('Snow', (0.92, 0.94, 0.98), 0.95)
mat_lodge_wall = get_material('LodgeWall', (0.35, 0.2, 0.1), 0.8)
mat_lodge_roof = get_material('LodgeRoof', (0.15, 0.1, 0.08), 0.7)
mat_lodge_door = get_material('LodgeDoor', (0.2, 0.12, 0.06), 0.6)
mat_lodge_window = get_material('LodgeWindow', (0.6, 0.7, 0.85), 0.2, 0.3)
mat_heli_body = get_material('HeliBody', (0.85, 0.05, 0.05), 0.3, 0.2)
mat_heli_dark = get_material('HeliDark', (0.1, 0.1, 0.1), 0.4, 0.5)
mat_heli_glass = get_material('HeliGlass', (0.4, 0.5, 0.65), 0.1, 0.4)
mat_pad = get_material('Pad', (0.5, 0.5, 0.52), 0.8)
mat_pad_line = get_material('PadLine', (0.9, 0.9, 0.9), 0.5)
mat_rack = get_material('SkiRack', (0.3, 0.3, 0.35), 0.5, 0.6)
mat_ski_blue = get_material('SkiBlue', (0.1, 0.3, 0.7), 0.3)
mat_ski_red = get_material('SkiRed', (0.7, 0.1, 0.1), 0.3)
mat_ski_yellow = get_material('SkiYellow', (0.8, 0.7, 0.1), 0.3)
mat_fuel_tank = get_material('FuelTank', (0.15, 0.15, 0.18), 0.4, 0.3)
mat_fuel_pump = get_material('FuelPump', (0.5, 0.5, 0.55), 0.3, 0.7)
mat_wood = get_material('Wood', (0.4, 0.25, 0.12), 0.8)
mat_metal = get_material('Metal', (0.4, 0.4, 0.45), 0.4, 0.8)

# --- SNOW GROUND ---
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.active_object
ground.data.materials.append(mat_snow)
# Add slight noise displacement for terrain feel
mod = ground.modifiers.new('Noise', 'DISPLACE')
texture = bpy.data.textures.new('SnowNoise', 'CLOUDS')
texture.noise_scale = 15
mod.texture = texture
mod.strength = 1.5
bpy.ops.object.shade_smooth()

# --- LODGE ---
def make_lodge(loc):
    x, y, z = loc
    # Main body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + 2))
    body = bpy.context.active_object
    body.scale = (6, 4, 2)
    body.data.materials.append(mat_lodge_wall)
    
    # Roof (prism)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=5.5, radius2=0, depth=3, location=(x, y, z + 4.5))
    roof = bpy.context.active_object
    roof.scale = (1.1, 0.85, 1)
    roof.rotation_euler[2] = math.radians(45)
    roof.data.materials.append(mat_lodge_roof)
    
    # Door
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 2.01, z + 1))
    door = bpy.context.active_object
    door.scale = (0.8, 0.05, 1)
    door.data.materials.append(mat_lodge_door)
    
    # Windows
    for wx in [-3, -1.5, 1.5, 3]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x + wx, y + 2.01, z + 1.5))
        win = bpy.context.active_object
        win.scale = (0.6, 0.05, 0.7)
        win.data.materials.append(mat_lodge_window)
    
    # Chimney
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + 2, y - 1, z + 5))
    chim = bpy.context.active_object
    chim.scale = (0.5, 0.5, 1.5)
    chim.data.materials.append(mat_lodge_wall)
    
    # Front porch
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 3.5, z + 0.1))
    porch = bpy.context.active_object
    porch.scale = (5, 1.5, 0.1)
    porch.data.materials.append(mat_wood)
    
    # Porch pillars
    for px in [-2.5, 2.5]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2, location=(x + px, y + 4.2, z + 1))
        pil = bpy.context.active_object
        pil.data.materials.append(mat_wood)

make_lodge((-15, -10, 0))

# --- HELICOPTER PAD ---
def make_pad(loc):
    x, y, z = loc
    # Circular pad
    bpy.ops.mesh.primitive_cylinder_add(radius=6, depth=0.3, location=(x, y, z + 0.15))
    pad = bpy.context.active_object
    pad.data.materials.append(mat_pad)
    
    # H marking
    # Left bar
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x - 1.5, y, z + 0.32))
    lb = bpy.context.active_object
    lb.scale = (0.4, 3, 0.05)
    lb.data.materials.append(mat_pad_line)
    # Right bar
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + 1.5, y, z + 0.32))
    rb = bpy.context.active_object
    rb.scale = (0.4, 3, 0.05)
    rb.data.materials.append(mat_pad_line)
    # Middle bar
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + 0.32))
    mb = bpy.context.active_object
    mb.scale = (2.5, 0.4, 0.05)
    mb.data.materials.append(mat_pad_line)
    
    # Snow ring around pad
    bpy.ops.mesh.primitive_torus_add(major_radius=6.5, minor_radius=0.3, location=(x, y, z + 0.1))
    ring = bpy.context.active_object
    ring.data.materials.append(mat_snow)

make_pad((5, 5, 0))

# --- HELICOPTER ---
def make_heli(loc):
    x, y, z = loc
    # Fuselage
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(x, y, z + 1.5))
    fus = bpy.context.active_object
    fus.scale = (1.2, 0.8, 0.8)
    fus.data.materials.append(mat_heli_body)
    
    # Tail boom
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=4, location=(x - 2.5, y, z + 1.5), rotation=(0, math.radians(90), 0))
    tail = bpy.context.active_object
    tail.data.materials.append(mat_heli_body)
    
    # Tail rotor housing
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.3, location=(x - 4.5, y, z + 1.5), rotation=(math.radians(90), 0, 0))
    trh = bpy.context.active_object
    trh.data.materials.append(mat_heli_dark)
    
    # Tail rotor blades
    for ang in [0, 90, 180, 270]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x - 4.65, y, z + 1.5))
        blade = bpy.context.active_object
        blade.scale = (0.05, 0.7, 0.08)
        blade.rotation_euler[0] = math.radians(ang)
        blade.data.materials.append(mat_heli_dark)
    
    # Cockpit glass
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(x + 1.2, y, z + 1.7))
    glass = bpy.context.active_object
    glass.scale = (0.8, 0.7, 0.7)
    glass.data.materials.append(mat_heli_glass)
    
    # Landing skids
    for sx in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=3, location=(x, y + sx, z + 0.3), rotation=(math.radians(90), 0, 0))
        skid = bpy.context.active_object
        skid.data.materials.append(mat_heli_dark)
        # Skid struts
        for sz in [-1, 1]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.2, location=(x + sz * 0.5, y + sx, z + 0.9))
            strut = bpy.context.active_object
            strut.data.materials.append(mat_heli_dark)
    
    # Main rotor mast
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1, location=(x, y, z + 2.8))
    mast = bpy.context.active_object
    mast.data.materials.append(mat_heli_dark)
    
    # Main rotor hub
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.2, location=(x, y, z + 3.3))
    hub = bpy.context.active_object
    hub.data.materials.append(mat_heli_dark)
    
    # Main rotor blades
    for ang in [0, 60, 120, 180, 240, 300]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + 3.35))
        rblade = bpy.context.active_object
        rblade.scale = (4, 0.15, 0.05)
        rblade.rotation_euler[2] = math.radians(ang)
        rblade.data.materials.append(mat_heli_dark)
    
    # Engine cowling
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x - 0.5, y, z + 2.2))
    eng = bpy.context.active_object
    eng.scale = (1.2, 0.9, 0.6)
    eng.data.materials.append(mat_heli_dark)

make_heli((5, 5, 0))

# --- SKI RACK ---
def make_ski_rack(loc):
    x, y, z = loc
    # Frame posts
    for px in [-2, 2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2, location=(x + px, y, z + 1))
        post = bpy.context.active_object
        post.data.materials.append(mat_rack)
    
    # Top bar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=4, location=(x, y, z + 2), rotation=(0, math.radians(90), 0))
    topbar = bpy.context.active_object
    topbar.data.materials.append(mat_rack)
    
    # Middle bar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=4, location=(x, y, z + 1.2), rotation=(0, math.radians(90), 0))
    midbar = bpy.context.active_object
    midbar.data.materials.append(mat_rack)
    
    # Skis hanging
    ski_colors = [mat_ski_blue, mat_ski_red, mat_ski_yellow, mat_ski_blue, mat_ski_red]
    for i, sc in enumerate(ski_colors):
        sx = x - 1.6 + i * 0.8
        # Ski 1
        bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, y + 0.1, z + 1.5))
        ski1 = bpy.context.active_object
        ski1.scale = (0.12, 0.05, 1.8)
        ski1.data.materials.append(sc)
        # Ski 2
        bpy.ops.mesh.primitive_cube_add(size=1, location=(sx + 0.25, y - 0.1, z + 1.5))
        ski2 = bpy.context.active_object
        ski2.scale = (0.12, 0.05, 1.8)
        ski2.data.materials.append(sc)

make_ski_rack((-15, -5, 0))

# --- FUEL CACHE ---
def make_fuel_cache(loc):
    x, y, z = loc
    # Fuel tanks
    for i, (tx, ty) in enumerate([(-1.5, 0), (1.5, 0)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2.5, location=(x + tx, y, z + 1.25))
        tank = bpy.context.active_object
        tank.data.materials.append(mat_fuel_tank)
        # Tank cap
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(x + tx, y, z + 2.6))
        cap = bpy.context.active_object
        cap.data.materials.append(mat_metal)
    
    # Fuel pump
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 1.5, z + 0.8))
    pump = bpy.context.active_object
    pump.scale = (0.5, 0.4, 0.8)
    pump.data.materials.append(mat_fuel_pump)
    
    # Fuel hose
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.5, location=(x + 0.3, y + 0.8, z + 0.5), rotation=(math.radians(45), 0, 0))
    hose = bpy.context.active_object
    hose.data.materials.append(mat_heli_dark)
    
    # Small shelter roof
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + 3))
    shelter = bpy.context.active_object
    shelter.scale = (4, 2, 0.1)
    shelter.data.materials.append(mat_wood)
    # Shelter posts
    for px, py in [(-2, -1), (2, -1), (-2, 1), (2, 1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=3, location=(x + px, y + py, z + 1.5))
        sp = bpy.context.active_object
        sp.data.materials.append(mat_wood)

make_fuel_cache((15, -5, 0))

# --- TREES (sparse, snowy) ---
def make_tree(loc):
    x, y, z = loc
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=2, location=(x, y, z + 1))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_wood)
    # Foliage layers
    for i, (radius, height) in enumerate([(1.5, 1.5), (1.2, 2.5), (0.8, 3.5)]):
        bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=0, depth=1.2, location=(x, y, z + height))
        fol = bpy.context.active_object
        fol.data.materials.append(mat_snow)

# Place some trees
tree_positions = [
    (-25, -20, 0), (-20, -25, 0), (-30, -15, 0), (-22, -18, 0),
    (20, 15, 0), (25, 10, 0), (22, 20, 0), (28, 18, 0),
    (-25, 10, 0), (-20, 15, 0), (-30, 5, 0),
    (10, -20, 0), (15, -25, 0), (5, -22, 0),
    (-10, 20, 0), (-5, 25, 0), (-15, 22, 0),
]
for tp in tree_positions:
    make_tree(tp)

# --- SNOW DRIFTS ---
for _ in range(15):
    rx = random.uniform(-30, 30)
    ry = random.uniform(-25, 25)
    # Avoid pad and lodge areas
    if abs(rx - 5) < 8 and abs(ry - 5) < 8:
        continue
    if abs(rx + 15) < 8 and abs(ry + 10) < 6:
        continue
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.5, 2), location=(rx, ry, 0.2))
    drift = bpy.context.active_object
    drift.scale = (random.uniform(1, 2), random.uniform(1, 2), 0.3)
    drift.data.materials.append(mat_snow)
    bpy.ops.object.shade_smooth()

# --- LIGHTING: Fresh Blue Morning ---
# World
world = bpy.data.worlds.get('World')
if world is None:
    world = bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wlinks = world.node_tree.links
wnodes.clear()
bg = wnodes.new('ShaderNodeBackground')
out = wnodes.new('ShaderNodeOutputWorld')
# Blue morning sky
bg.inputs['Color'].default_value = (0.3, 0.5, 0.8, 1.0)
bg.inputs['Strength'].default_value = 0.8
wlinks.new(bg.outputs['Background'], out.inputs['Surface'])

# Sun (low angle, warm-ish but cool morning)
sun_data = bpy.data.lights.new('Sun', type='SUN')
sun_data.energy = 3.0
sun_data.color = (1.0, 0.9, 0.75)  # warm morning sun
sun_data.angle = math.radians(5)
sun_obj = bpy.data.objects.new('Sun', sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(60), math.radians(10), math.radians(160))  # low angle

# Fill light (cool blue from sky)
fill_data = bpy.data.lights.new('Fill', type='AREA')
fill_data.energy = 500
fill_data.color = (0.5, 0.6, 0.9)
fill_data.size = 50
fill_obj = bpy.data.objects.new('Fill', fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (0, 0, 30)
fill_obj.rotation_euler = (0, 0, 0)

# Rim light for drama
rim_data = bpy.data.lights.new('Rim', type='AREA')
rim_data.energy = 300
rim_data.color = (0.7, 0.8, 1.0)
rim_data.size = 20
rim_obj = bpy.data.objects.new('Rim', rim_data)
bpy.context.collection.objects.link(rim_obj)
rim_obj.location = (-20, -20, 15)
rim_obj.rotation_euler = (math.radians(45), math.radians(30), math.radians(45))

# --- CAMERA ---
cam_data = bpy.data.cameras.new('Camera')
cam_data.lens = 35
cam_obj = bpy.data.objects.new('Camera', cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (-25, 25, 8)
# Look toward center of scene
target = Vector((0, 0, 2))
direction = target - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
bpy.context.scene.camera = cam_obj

# --- RENDER SETTINGS ---
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
