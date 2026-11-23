import bpy
import math
import random
from mathutils import Vector, Euler

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set units
bpy.context.scene.unit_settings.system = 'METRIC'

# Set fog
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Fog via volume scatter
bg_node = nodes.get("Background")
if bg_node is None:
    bg_node = nodes.new("ShaderNodeBackground")
    bg_node.inputs[0].default_value = (0.6, 0.65, 0.7, 1.0)
    bg_node.inputs[1].default_value = 0.8

vol_node = nodes.new("ShaderNodeVolumeScatter")
vol_node.inputs['Color'].default_value = (0.7, 0.75, 0.8, 1.0)
vol_node.inputs['Density'].default_value = 0.015
vol_node.inputs['Anisotropy'].default_value = 0.3

out_node = nodes.get("World Output")
if out_node is None:
    out_node = nodes.new("ShaderNodeOutputWorld")

link = links.new(vol_node.outputs[0], out_node.inputs['Volume'])
link2 = links.new(bg_node.outputs[0], out_node.inputs['Surface'])

# Helper functions
def create_box(name, size, location, rotation=(0,0,0), material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    if material:
        obj.data.materials.append(material)
    return obj

def create_cylinder(name, radius, depth, location, rotation=(0,0,0), material=None, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, rotation=rotation, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def create_sphere(name, radius, location, material=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=32, ring_count=16)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

# Materials
def make_mat(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

mat_hull = make_mat("Hull", (0.15, 0.15, 0.18, 1.0), metallic=0.7, roughness=0.3)
mat_deck = make_mat("Deck", (0.25, 0.22, 0.2, 1.0), metallic=0.3, roughness=0.6)
mat_turret = make_mat("Turret", (0.12, 0.12, 0.15, 1.0), metallic=0.8, roughness=0.25)
mat_gun = make_mat("Gun", (0.1, 0.1, 0.12, 1.0), metallic=0.9, roughness=0.2)
mat_quay = make_mat("Quay", (0.4, 0.38, 0.35, 1.0), metallic=0.0, roughness=0.8)
mat_water = make_mat("Water", (0.05, 0.08, 0.12, 1.0), metallic=0.3, roughness=0.1)
mat_coal = make_mat("Coal", (0.05, 0.05, 0.05, 1.0), metallic=0.0, roughness=0.9)
mat_barge_hull = make_mat("BargeHull", (0.2, 0.18, 0.15, 1.0), metallic=0.4, roughness=0.5)
mat_crane = make_mat("Crane", (0.7, 0.5, 0.2, 1.0), metallic=0.6, roughness=0.4)
mat_flag = make_mat("Flag", (0.8, 0.1, 0.1, 1.0), metallic=0.0, roughness=0.7)
mat_gangway = make_mat("Gangway", (0.3, 0.28, 0.25, 1.0), metallic=0.3, roughness=0.5)
mat_rigging = make_mat("Rigging", (0.1, 0.1, 0.1, 1.0), metallic=0.8, roughness=0.3)
mat_smokestack = make_mat("Smokestack", (0.1, 0.1, 0.1, 1.0), metallic=0.5, roughness=0.4)
mat_porthole = make_mat("Porthole", (0.6, 0.7, 0.8, 1.0), metallic=0.9, roughness=0.1)

# === WATER ===
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -1))
water = bpy.context.active_object
water.name = "Water"
water.data.materials.append(mat_water)

# === QUAY (Navy Yard) ===
quay = create_box("Quay", (8, 120, 2), (4, 0, 0.5), material=mat_quay)
# Quay edge
quay_edge = create_box("QuayEdge", (1, 120, 1.5), (0.5, 0, 0.2), material=mat_quay)

# === IRONCLAD WARSHIP ===
# Main hull
hull = create_box("Hull", (10, 60, 5), (-15, 0, 2), material=mat_hull)
# Bow (pointed)
bpy.ops.mesh.primitive_cone_add(radius1=5, radius2=0, depth=12, location=(-20, 0, 2), rotation=(0, math.radians(90), 0), vertices=16)
bow = bpy.context.active_object
bow.name = "Bow"
bow.scale = (1, 1, 1)
bow.data.materials.append(mat_hull)
# Stern
stern = create_box("Stern", (4, 15, 5), (-22, 0, 2), material=mat_hull)

# Deck
deck = create_box("Deck", (10, 58, 0.5), (-15, 0, 4.5), material=mat_deck)

# Superstructure
superstructure = create_box("Superstructure", (8, 20, 3), (-15, 0, 6), material=mat_hull)
# Bridge
bridge = create_box("Bridge", (7, 8, 2.5), (-15, 0, 8.5), material=mat_hull)
# Bridge windows
for i in range(-2, 3):
    win = create_box(f"BridgeWin{i}", (0.2, 1.5, 1), (-15, i*1.8, 8.5), material=mat_porthole)

# Smokestacks
for i, x in enumerate([-12, -18]):
    stack = create_cylinder(f"Smokestack{i}", 1.2, 8, (x, 0, 10), material=mat_smokestack)
    # Stack top ring
    ring = create_cylinder(f"StackRing{i}", 1.4, 0.5, (x, 0, 14), material=mat_hull)

# Gun Turrets (Ironclad style - 2 main turrets, 1 forward, 1 aft)
# Forward turret
turret_fwd = create_cylinder("TurretFwd", 3, 2.5, (-8, 0, 5.5), material=mat_turret)
# Forward turret dome
dome_fwd = create_sphere("DomeFwd", 2.5, (-8, 0, 7), material=mat_turret)
# Forward guns
for i, angle in enumerate([math.radians(30), math.radians(-30)]):
    gun = create_cylinder(f"GunFwd{i}", 0.3, 6, (-8 + math.sin(angle)*3, math.cos(angle)*3, 6.5), rotation=(0, angle, 0), material=mat_gun)

# Aft turret
turret_aft = create_cylinder("TurretAft", 3, 2.5, (-20, 0, 5.5), material=mat_turret)
dome_aft = create_sphere("DomeAft", 2.5, (-20, 0, 7), material=mat_turret)
# Aft guns
for i, angle in enumerate([math.radians(150), math.radians(-150)]):
    gun = create_cylinder(f"GunAft{i}", 0.3, 6, (-20 + math.sin(angle)*3, math.cos(angle)*3, 6.5), rotation=(0, angle, 0), material=mat_gun)

# Secondary guns along sides
for side in [-1, 1]:
    for x in [-10, -14, -18]:
        gun = create_cylinder(f"SecGun_{side}_{x}", 0.2, 3, (x, side*5, 5), rotation=(math.radians(90), 0, 0), material=mat_gun)

# Portholes along hull
for i in range(8):
    for side in [-1, 1]:
        p = create_cylinder(f"Porthole_{i}_{side}", 0.3, 0.1, (-8 - i*4, side*5, 2.5), rotation=(math.radians(90), 0, 0), material=mat_porthole)

# Mast (single mast for ironclad)
mast = create_cylinder("Mast", 0.3, 15, (-15, 0, 14), material=mat_rigging)
# Crow's nest
crows = create_box("CrowsNest", (2, 2, 0.5), (-15, 0, 18), material=mat_rigging)
# Rigging lines
for i in range(4):
    angle = i * math.pi / 2
    rig = create_cylinder(f"Rigging{i}", 0.05, 12, (-15 + math.sin(angle)*5, math.cos(angle)*5, 12), rotation=(math.radians(45), 0, angle), material=mat_rigging)

# Flag at stern
flagpole = create_cylinder("Flagpole", 0.1, 4, (-24, 0, 7), material=mat_rigging)
flag = create_box("Flag", (2, 0.1, 1.5), (-24, 0, 8.5), material=mat_flag)

# === GANGWAY ===
# Gangway from quay to ship
gangway = create_box("Gangway", (1.5, 8, 0.3), (-10, 5, 3.5), rotation=(math.radians(15), 0, 0), material=mat_gangway)
# Gangway supports
support1 = create_cylinder("GangwaySupport1", 0.15, 3, (-10, 5, 2), material=mat_gangway)
support2 = create_cylinder("GangwaySupport2", 0.15, 3, (-10, 5, 2), material=mat_gangway)
# Handrails
for i in range(3):
    rail = create_cylinder(f"GangwayRail{i}", 0.05, 1, (-10, 4.5 + i*0.5, 4.5), rotation=(math.radians(15), 0, 0), material=mat_gangway)

# === COAL BARGES ===
for i, y in enumerate([15, -15]):
    # Barge hull
    barge = create_box(f"BargeHull{i}", (6, 20, 2), (-15, y, 0.5), material=mat_barge_hull)
    # Coal pile
    coal = create_box(f"Coal{i}", (5, 18, 1.5), (-15, y, 2), material=mat_coal)
    # Barge deck
    bdeck = create_box(f"BargeDeck{i}", (6, 20, 0.2), (-15, y, 1.5), material=mat_barge_hull)
    # Mooring lines
    for x in [-10, -20]:
        line = create_cylinder(f"Mooring_{i}_{x}", 0.05, 5, (x, y*0.5, 1), rotation=(0, math.radians(45), 0), material=mat_rigging)

# === CRANE ===
# Crane base
crane_base = create_box("CraneBase", (3, 3, 1), (2, 20, 1.5), material=mat_crane)
# Crane tower
crane_tower = create_cylinder("CraneTower", 0.8, 12, (2, 20, 7), material=mat_crane)
# Crane arm (jib)
crane_arm = create_box("CraneArm", (0.5, 10, 0.5), (2, 25, 13), rotation=(math.radians(10), 0, 0), material=mat_crane)
# Crane counterweight
counterweight = create_box("Counterweight", (1.5, 2, 1), (2, 19, 13), material=mat_crane)
# Crane cables
cable = create_cylinder("CraneCable", 0.03, 8, (2, 28, 9), rotation=(math.radians(5), 0, 0), material=mat_rigging)
# Crane hook
hook = create_sphere("CraneHook", 0.3, (2, 28, 5), material=mat_crane)
# Crane operator cabin
cabin = create_box("CraneCabin", (1.5, 1.5, 1.5), (2, 20, 12), material=mat_crane)

# === ADDITIONAL DETAILS ===
# Bollards on quay
for i in range(5):
    bollard = create_cylinder(f"Bollard{i}", 0.2, 0.8, (0.5, -30 + i*15, 1.5), material=mat_rigging)

# Mooring lines from ship to quay
for i, y in enumerate([-20, 0, 20]):
    mooring = create_cylinder(f"ShipMooring{i}", 0.05, 8, (-15, y*0.5, 2), rotation=(0, math.radians(30), 0), material=mat_rigging)

# Small boat alongside
boat = create_box("Boat", (2, 5, 0.8), (-5, 10, 0.5), material=mat_barge_hull)
boat_deck = create_box("BoatDeck", (2, 5, 0.1), (-5, 10, 0.9), material=mat_deck)

# Set camera
bpy.ops.object.camera_add(location=(20, 30, 15), rotation=(math.radians(70), 0, math.radians(-30)))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20), rotation=(math.radians(45), 0, math.radians(30)))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 1.5
sun.data.color = (1.0, 0.95, 0.9)

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Ironclad warship scene created successfully!")
