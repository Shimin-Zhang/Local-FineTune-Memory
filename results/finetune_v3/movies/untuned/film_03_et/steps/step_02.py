import bpy
import math
import random
from mathutils import Vector

# Fix: Clear everything and rebuild with correct material creation
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Helper: create material with 4-component colors
def create_material(name, color_rgb, roughness=0.5, metallic=0.0, emission=0.0, emission_color_rgb=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    # Ensure 4-component RGBA
    bsdf.inputs['Base Color'].default_value = (color_rgb[0], color_rgb[1], color_rgb[2], 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission > 0:
        ec = emission_color_rgb if emission_color_rgb else color_rgb
        bsdf.inputs['Emission Color'].default_value = (ec[0], ec[1], ec[2], 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs[0], output.inputs[0])
    return mat

# World setup
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
wnt = world.node_tree
for node in wnt.nodes:
    wnt.nodes.remove(node)

# Night sky gradient using a gradient texture
bg = wnt.nodes.new('ShaderNodeBackground')
bg.inputs[0].default_value = (0.01, 0.03, 0.08, 1.0)
bg.inputs[1].default_value = 1.0
out = wnt.nodes.new('ShaderNodeOutputWorld')
wnt.links.new(bg.outputs[0], out.inputs[0])

# Camera
scene = bpy.context.scene
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 45
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (0, -12, 1.5)
cam.rotation_euler = (math.radians(85), 0, 0)
scene.camera = cam

# Lighting
# Moon key light
sun_data = bpy.data.lights.new("MoonLight", type='SUN')
sun_data.energy = 1.0
sun_data.color = (0.75, 0.8, 1.0)
sun_data.angle = math.radians(5)
sun = bpy.data.objects.new("MoonLight", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(-50), 0, math.radians(20))

# Fill
fill_data = bpy.data.lights.new("FillLight", type='SUN')
fill_data.energy = 0.15
fill_data.color = (0.4, 0.45, 0.6)
fill = bpy.data.objects.new("FillLight", fill_data)
scene.collection.objects.link(fill)
fill.rotation_euler = (math.radians(-30), 0, math.radians(-40))

# Rim
rim_data = bpy.data.lights.new("RimLight", type='SUN')
rim_data.energy = 0.4
rim_data.color = (0.6, 0.65, 0.9)
rim = bpy.data.objects.new("RimLight", rim_data)
scene.collection.objects.link(rim)
rim.rotation_euler = (math.radians(50), 0, 0)

# Materials
mat_moon = create_material("MoonMat", (0.92, 0.92, 0.88), roughness=0.8, emission=3.0, emission_color_rgb=(0.92, 0.92, 0.88))
mat_crater = create_material("CraterMat", (0.7, 0.7, 0.65), roughness=0.9)
mat_bike_frame = create_material("BikeFrame", (0.85, 0.12, 0.12), roughness=0.25, metallic=0.8)
mat_bike_tire = create_material("BikeTire", (0.04, 0.04, 0.04), roughness=0.9)
mat_bike_handle = create_material("BikeHandle", (0.15, 0.15, 0.15), roughness=0.3, metallic=0.9)
mat_bike_seat = create_material("BikeSeat", (0.08, 0.08, 0.08), roughness=0.8)
mat_bike_chain = create_material("BikeChain", (0.25, 0.25, 0.25), roughness=0.2, metallic=0.95)
mat_bike_rim = create_material("WheelRim", (0.65, 0.65, 0.65), roughness=0.2, metallic=0.9)
mat_bike_spoke = create_material("Spoke", (0.55, 0.55, 0.55), roughness=0.3, metallic=0.8)
mat_bike_fork = create_material("BikeFork", (0.85, 0.12, 0.12), roughness=0.25, metallic=0.8)
mat_bike_seatpost = create_material("SeatPost", (0.15, 0.15, 0.15), roughness=0.3, metallic=0.8)
mat_bike_crank = create_material("Crank", (0.25, 0.25, 0.25), roughness=0.3, metallic=0.8)
mat_bike_pedal = create_material("Pedal", (0.15, 0.15, 0.15), roughness=0.4, metallic=0.7)
mat_basket = create_material("Basket", (0.35, 0.28, 0.18), roughness=0.9)
mat_basket_wire = create_material("BasketWire", (0.45, 0.38, 0.28), roughness=0.5, metallic=0.3)
mat_et_body = create_material("ETBody", (0.28, 0.48, 0.58), roughness=0.55)
mat_et_head = create_material("ETHead", (0.32, 0.52, 0.62), roughness=0.5)
mat_et_eye = create_material("ETEye", (0.08, 0.12, 0.18), roughness=0.25)
mat_et_nose = create_material("ETNose", (0.28, 0.48, 0.58), roughness=0.55)
mat_et_hand = create_material("ETHand", (0.28, 0.48, 0.58), roughness=0.55)
mat_et_foot = create_material("ETFoot", (0.28, 0.48, 0.58), roughness=0.55)
mat_tree = create_material("Tree", (0.04, 0.12, 0.04), roughness=0.9)
mat_trunk = create_material("Trunk", (0.12, 0.08, 0.04), roughness=0.9)
mat_ground = create_material("Ground", (0.04, 0.08, 0.04), roughness=0.9)
mat_star = create_material("Star", (1.0, 1.0, 1.0), roughness=0.5, emission=8.0, emission_color_rgb=(1.0, 1.0, 1.0))

# Create the Moon
bpy.ops.mesh.primitive_uv_sphere_add(radius=4.5, location=(0, 12, 7), segments=64, ring_count=32)
moon = bpy.context.active_object
moon.name = "Moon"
moon.data.materials.append(mat_moon)

# Moon craters
random.seed(42)
for i in range(20):
    angle = random.uniform(0, 2*math.pi)
    elev = random.uniform(-0.4, 0.4)
    r = 0.2 + random.uniform(0, 0.4)
    x = 4.5 * math.cos(angle) * math.cos(elev)
    y = 12 + 4.5 * math.sin(angle) * math.cos(elev)
    z = 7 + 4.5 * math.sin(elev)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=16, ring_count=8)
    crater = bpy.context.active_object
    crater.name = f"Crater_{i}"
    crater.data.materials.append(mat_crater)
    crater.scale = (1, 1, 0.25)

# Stars
for i in range(300):
    x = random.uniform(-40, 40)
    y = random.uniform(15, 50)
    z = random.uniform(-15, 30)
    size = random.uniform(0.015, 0.06)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=(x, y, z), segments=8, ring_count=4)
    star = bpy.context.active_object
    star.name = f"Star_{i}"
    star.data.materials.append(mat_star)

# Helper: cylinder between two points
def create_cyl(p1, p2, radius, material, name="Cyl"):
    p1 = Vector(p1)
    p2 = Vector(p2)
    direction = p2 - p1
    length = direction.length
    if length < 0.001:
        return None
    direction.normalize()
    mid = (p1 + p2) / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=mid, vertices=16)
    cyl = bpy.context.active_object
    cyl.name = name
    rot = direction.to_track_quat('Z', 'Y')
    cyl.rotation_euler = rot.to_euler()
    if material:
        cyl.data.materials.append(material)
    return cyl

# Bicycle
bike_center = Vector((0, -3, 0.5))
wr = 0.32  # wheel radius
ww = 0.025  # wheel width

rear_wc = bike_center + Vector((-0.38, 0, 0))
front_wc = bike_center + Vector((0.38, 0, 0))

# Rear wheel
bpy.ops.mesh.primitive_torus_add(major_radius=wr, minor_radius=ww/2, major_segments=32, minor_segments=8, location=rear_wc)
rw = bpy.context.active_object
rw.name = "RearWheel"
rw.data.materials.append(mat_bike_tire)
rw.rotation_euler = (0, math.radians(90), 0)

bpy.ops.mesh.primitive_torus_add(major_radius=wr-ww/2, minor_radius=0.008, major_segments=32, minor_segments=8, location=rear_wc)
rr = bpy.context.active_object
rr.name = "RearRim"
rr.data.materials.append(mat_bike_rim)
rr.rotation_euler = (0, math.radians(90), 0)

for i in range(12):
    a = i * math.pi / 6
    end = rear_wc + Vector((wr * math.cos(a), wr * math.sin(a), 0))
    create_cyl(rear_wc, end, 0.004, mat_bike_spoke, f"RSpoke_{i}")

# Front wheel
bpy.ops.mesh.primitive_torus_add(major_radius=wr, minor_radius=ww/2, major_segments=32, minor_segments=8, location=front_wc)
fw = bpy.context.active_object
fw.name = "FrontWheel"
fw.data.materials.append(mat_bike_tire)
fw.rotation_euler = (0, math.radians(90), 0)

bpy.ops.mesh.primitive_torus_add(major_radius=wr-ww/2, minor_radius=0.008, major_segments=32, minor_segments=8, location=front_wc)
fr = bpy.context.active_object
fr.name = "FrontRim"
fr.data.materials.append(mat_bike_rim)
fr.rotation_euler = (0, math.radians(90), 0)

for i in range(12):
    a = i * math.pi / 6
    end = front_wc + Vector((wr * math.cos(a), wr * math.sin(a), 0))
    create_cyl(front_wc, end, 0.004, mat_bike_spoke, f"FSpoke_{i}")

# Frame
bb = bike_center + Vector((0, 0, 0.12))
seat_top = bike_center + Vector((-0.08, 0, 0.58))
ht_bot = bike_center + Vector((0.32, 0, 0.48))
ht_top = bike_center + Vector((0.32, 0, 0.62))

create_cyl(bb, seat_top, 0.013, mat_bike_frame, "SeatTube")
create_cyl(bb, ht_bot, 0.013, mat_bike_frame, "DownTube")
create_cyl(seat_top, ht_top, 0.013, mat_bike_frame, "TopTube")
create_cyl(seat_top, rear_wc, 0.009, mat_bike_frame, "SeatStay")
create_cyl(bb, rear_wc, 0.009, mat_bike_frame, "ChainStay")
create_cyl(ht_bot, front_wc, 0.01, mat_bike_fork, "ForkL")
create_cyl(ht_top, front_wc, 0.01, mat_bike_fork, "ForkR")

stem_top = bike_center + Vector((0.32, 0, 0.68))
create_cyl(ht_top, stem_top, 0.009, mat_bike_handle, "Stem")

hb_l = stem_top + Vector((0, -0.13, 0))
hb_r = stem_top + Vector((0, 0.13, 0))
create_cyl(hb_l, hb_r, 0.009, mat_bike_handle, "Handlebar")

# Seat
bpy.ops.mesh.primitive_cube_add(size=1, location=seat_top + Vector((0, 0, 0.02)))
seat = bpy.context.active_object
seat.name = "Seat"
seat.scale = (0.11, 0.07, 0.018)
seat.data.materials.append(mat_bike_seat)

create_cyl(seat_top - Vector((0,0,0.02)), seat_top + Vector((0,0,0.04)), 0.007, mat_bike_seatpost, "SeatPost")

# Cranks and pedals
cl = 0.11
pl = bb + Vector((cl * math.cos(math.pi/4), cl * math.sin(math.pi/4), 0))
pr = bb + Vector((cl * math.cos(-math.pi/4), cl * math.sin(-math.pi/4), 0))
create_cyl(bb, pl, 0.007, mat_bike_crank, "CrankL")
create_cyl(bb, pr, 0.007, mat_bike_crank, "CrankR")

bpy.ops.mesh.primitive_cube_add(size=1, location=pl)
ped_l = bpy.context.active_object
ped_l.name = "PedalL"
ped_l.scale = (0.045, 0.07, 0.008)
ped_l.data.materials.append(mat_bike_pedal)

bpy.ops.mesh.primitive_cube_add(size=1, location=pr)
ped_r = bpy.context.active_object
ped_r.name = "PedalR"
ped_r.scale = (0.045, 0.07, 0.008)
ped_r.data.materials.append(mat_bike_pedal)

# Chainring
bpy.ops.mesh.primitive_torus_add(major_radius=0.07, minor_radius=0.006, major_segments=24, minor_segments=6, location=bb + Vector((0, 0.018, 0)))
cr = bpy.context.active_object
cr.name = "Chainring"
cr.data.materials.append(mat_bike_chain)
cr.rotation_euler = (math.radians(90), 0, 0)

# Chain
cp = [bb + Vector((0.07, 0.018, 0)), rear_wc + Vector((0.07, 0, 0)), rear_wc + Vector((0.07, 0, -0.04)), bb + Vector((0.07, 0.018, -0.04))]
for i in range(len(cp)):
    create_cyl(cp[i], cp[(i+1)%len(cp)], 0.0025, mat_bike_chain, f"Chain_{i}")

# Basket
bc = bike_center + Vector((0.32, 0, 0.52))
bpy.ops.mesh.primitive_cube_add(size=1, location=bc)
basket = bpy.context.active_object
basket.name = "Basket"
basket.scale = (0.14, 0.11, 0.09)
basket.data.materials.append(mat_basket)

# Basket wires
for i in range(5):
    xo = -0.055 + i * 0.0275
    create_cyl(bc + Vector((xo, -0.055, -0.045)), bc + Vector((xo, -0.055, 0.045)), 0.0025, mat_basket_wire, f"BWV_{i}")
    create_cyl(bc + Vector((xo, 0.055, -0.045)), bc + Vector((xo, 0.055, 0.045)), 0.0025, mat_basket_wire, f"BWV2_{i}")
for i in range(4):
    yo = -0.035 + i * 0.0233
    create_cyl(bc + Vector((-0.07, yo, -0.045)), bc + Vector((0.07, yo, -0.045)), 0.0025, mat_basket_wire, f"BWH_{i}")
    create_cyl(bc + Vector((-0.07, yo, 0.045)), bc + Vector((0.07, yo, 0.045)), 0.0025, mat_basket_wire, f"BWH2_{i}")

# E.T.
etc = bc + Vector((0, 0, 0.04))

# Body
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=etc, segments=32, ring_count=16)
etb = bpy.context.active_object
etb.name = "ET_Body"
etb.scale = (1, 0.8, 1.2)
etb.data.materials.append(mat_et_body)

# Head
hc = etc + Vector((0, 0, 0.075))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.048, location=hc, segments=32, ring_count=16)
eth = bpy.context.active_object
eth.name = "ET_Head"
eth.scale = (1, 0.9, 1.1)
eth.data.materials.append(mat_et_head)

# Eyes
el = hc + Vector((-0.018, 0.038, 0.008))
er = hc + Vector((0.018, 0.038, 0.008))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011, location=el, segments=16, ring_count=8)
eel = bpy.context.active_object
eel.name = "ET_EyeL"
eel.data.materials.append(mat_et_eye)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.011, location=er, segments=16, ring_count=8)
eer = bpy.context.active_object
eer.name = "ET_EyeR"
eer.data.materials.append(mat_et_eye)

# Nose
nc = hc + Vector((0, 0.048, -0.008))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, location=nc, segments=16, ring_count=8)
etn = bpy.context.active_object
etn.name = "ET_Nose"
etn.scale = (1, 1.4, 0.7)
etn.data.materials.append(mat_et_nose)

# Hands
hl = etc + Vector((-0.045, 0.025, -0.018))
hr = etc + Vector((0.045, 0.025, -0.018))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, location=hl, segments=16, ring_count=8)
ehl = bpy.context.active_object
ehl.name = "ET_HandL"
ehl.scale = (0.8, 1.2, 1.5)
ehl.data.materials.append(mat_et_hand)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, location=hr, segments=16, ring_count=8)
ehr = bpy.context.active_object
ehr.name = "ET_HandR"
ehr.scale = (0.8, 1.2, 1.5)
ehr.data.materials.append(mat_et_hand)

# Feet
fl = etc + Vector((-0.028, 0.018, -0.075))
fr2 = etc + Vector((0.028, 0.018, -0.075))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, location=fl, segments=16, ring_count=8)
efl = bpy.context.active_object
efl.name = "ET_FootL"
efl.scale = (0.8, 1.2, 1.0)
efl.data.materials.append(mat_et_foot)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, location=fr2, segments=16, ring_count=8)
efr = bpy.context.active_object
efr.name = "ET_FootR"
efr.scale = (0.8, 1.2, 1.0)
efr.data.materials.append(mat_et_foot)

# Neck
create_cyl(etc + Vector((0,0,0.025)), hc - Vector((0,0,0.025)), 0.014, mat_et_body, "ET_Neck")

# Forest
random.seed(123)
for i in range(40):
    x = random.uniform(-20, 20)
    z = random.uniform(-10, -4)
    h = random.uniform(2.5, 6)
    tr = random.uniform(0.08, 0.18)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=tr, depth=h, location=(x, 0, z + h/2), vertices=8)
    trunk = bpy.context.active_object
    trunk.name = f"Trunk_{i}"
    trunk.data.materials.append(mat_trunk)
    
    ch = h * 0.65
    cr = random.uniform(0.4, 0.9)
    bpy.ops.mesh.primitive_cone_add(radius1=cr, radius2=0, depth=ch, location=(x, 0, z + h + ch/2), vertices=8)
    canopy = bpy.context.active_object
    canopy.name = f"Canopy_{i}"
    canopy.data.materials.append(mat_tree)

# Ground
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.5))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(mat_ground)

# Grass
for i in range(60):
    x = random.uniform(-12, 12)
    z = random.uniform(-6, -1)
    bpy.ops.mesh.primitive_cone_add(radius1=0.04, radius2=0, depth=0.12, location=(x, 0, z + 0.06), vertices=6)
    g = bpy.context.active_object
    g.name = f"Grass_{i}"
    g.data.materials.append(mat_tree)
    g.rotation_euler = (random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), 0)

# Tilt bike for flying pose
bike_objs = [obj for obj in bpy.data.objects if any(obj.name.startswith(p) for p in ("Rear","Front","Seat","Down","Top","Chain","Fork","Stem","Handlebar","SeatPost","Crank","Pedal","Chainring","Basket","ET_","BW"))]
for obj in bike_objs:
    obj.rotation_euler = (math.radians(-8), math.radians(4), math.radians(-3))
    obj.location += Vector((0, -1, 1.2))

# E.T. glow
glow_data = bpy.data.lights.new("ETGlow", type='POINT')
glow_data.energy = 8
glow_data.color = (0.4, 0.65, 1.0)
glow_data.shadow_soft_size = 0.4
glow = bpy.data.objects.new("ETGlow", glow_data)
scene.collection.objects.link(glow)
glow.location = etc + Vector((0, 0, 0.08))

# Moon glow
mg_data = bpy.data.lights.new("MoonGlow", type='POINT')
mg_data.energy = 80
mg_data.color = (0.75, 0.8, 1.0)
mg_data.shadow_soft_size = 2.5
mg = bpy.data.objects.new("MoonGlow", mg_data)
scene.collection.objects.link(mg)
mg.location = (0, 12, 7)

# Render settings
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.view_settings.exposure = 0.6
scene.view_settings.look = 'Medium High Contrast'

print("Scene rebuilt successfully with all details!")
