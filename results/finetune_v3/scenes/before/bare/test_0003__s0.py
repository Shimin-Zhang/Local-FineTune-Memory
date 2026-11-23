import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- MATERIALS ---
def new_mat(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_snow    = new_mat("Snow",    (0.95, 0.97, 1.00), 0.7)
mat_wood    = new_mat("Wood",    (0.45, 0.28, 0.15), 0.9)
mat_roof    = new_mat("Roof",    (0.15, 0.15, 0.18), 0.6)
mat_glass   = new_mat("Glass",   (0.7, 0.85, 0.95),  0.1)
mat_heli    = new_mat("Heli",    (0.2, 0.25, 0.35),  0.3, 0.6)
mat_rotor   = new_mat("Rotor",   (0.1, 0.1, 0.1),    0.4)
mat_pad     = new_mat("Pad",     (0.85, 0.88, 0.92), 0.5)
mat_rack    = new_mat("Rack",    (0.6, 0.6, 0.65),   0.4, 0.7)
mat_ski     = new_mat("Ski",     (0.9, 0.3, 0.2),    0.5)
mat_fuel    = new_mat("Fuel",    (0.85, 0.6, 0.1),   0.6)
mat_barrel  = new_mat("Barrel",  (0.7, 0.7, 0.75),   0.4, 0.5)
mat_sky     = new_mat("Sky",     (0.55, 0.75, 0.95), 0.0)

# --- SNOW GROUND ---
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "SnowGround"
ground.data.materials.append(mat_snow)

# Add subtle displacement for snow texture
mod = ground.modifiers.new("SnowDisp", 'DISPLACE')
tex = bpy.data.textures.new("SnowTex", type='CLOUDS')
tex.noise_scale = 2.0
mod.texture = tex
mod.strength = 0.3

# --- LODGE ---
def build_lodge(loc):
    # Main body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], 1.5))
    body = bpy.context.object
    body.name = "LodgeBody"
    body.scale = (8, 5, 3)
    body.data.materials.append(mat_wood)

    # Roof
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], 3.3))
    roof = bpy.context.object
    roof.name = "LodgeRoof"
    roof.scale = (8.5, 5.5, 0.4)
    roof.data.materials.append(mat_roof)

    # Gable triangle (approx with a wedge)
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius=5.5, depth=1.5, location=(loc[0], loc[1], 3.8))
    gable = bpy.context.object
    gable.name = "LodgeGable"
    gable.rotation_euler = (0, math.radians(90), math.radians(90))
    gable.scale = (1, 1, 0.3)
    gable.data.materials.append(mat_roof)

    # Windows (front)
    for i in range(3):
        wx = loc[0] - 2.5 + i * 2.5
        bpy.ops.mesh.primitive_cube_add(size=1, location=(wx, loc[1] + 2.55, 1.5))
        win = bpy.context.object
        win.name = f"LodgeWindow_{i}"
        win.scale = (1.2, 0.1, 1.0)
        win.data.materials.append(mat_glass)

    # Door
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1] + 2.55, 1.0))
    door = bpy.context.object
    door.name = "LodgeDoor"
    door.scale = (1.0, 0.1, 1.8)
    door.data.materials.append(mat_wood)

    # Chimney
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0] + 3, loc[1] - 1, 4.5))
    chim = bpy.context.object
    chim.name = "LodgeChimney"
    chim.scale = (0.8, 0.8, 2.5)
    chim.data.materials.append(mat_roof)

    # Snow on roof
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], 3.6))
    snowroof = bpy.context.object
    snowroof.name = "LodgeRoofSnow"
    snowroof.scale = (8.5, 5.5, 0.15)
    snowroof.data.materials.append(mat_snow)

build_lodge((-15, -5, 0))

# --- HELICOPTER PAD ---
pad_loc = (15, 10, 0)
bpy.ops.mesh.primitive_cylinder_add(radius=8, depth=0.2, location=(pad_loc[0], pad_loc[1], 0.1))
pad = bpy.context.object
pad.name = "HeliPad"
pad.data.materials.append(mat_pad)

# H mark
bpy.ops.mesh.primitive_cube_add(size=1, location=(pad_loc[0], pad_loc[1], 0.22))
h1 = bpy.context.object
h1.name = "HMark1"
h1.scale = (0.3, 4, 0.05)
h1.data.materials.append(mat_snow)

bpy.ops.mesh.primitive_cube_add(size=1, location=(pad_loc[0] - 1.5, pad_loc[1], 0.22))
h2 = bpy.context.object
h2.name = "HMark2"
h2.scale = (0.3, 0.3, 0.05)
h2.data.materials.append(mat_snow)

bpy.ops.mesh.primitive_cube_add(size=1, location=(pad_loc[0] + 1.5, pad_loc[1], 0.22))
h3 = bpy.context.object
h3.name = "HMark3"
h3.scale = (0.3, 0.3, 0.05)
h3.data.materials.append(mat_snow)

# --- HELICOPTER ---
def build_heli(loc):
    # Fuselage
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(loc[0], loc[1], 1.5))
    fus = bpy.context.object
    fus.name = "HeliFuselage"
    fus.scale = (1.0, 2.0, 1.0)
    fus.data.materials.append(mat_heli)

    # Tail boom
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1] - 3.0, 1.5))
    tail = bpy.context.object
    tail.name = "HeliTail"
    tail.scale = (0.4, 2.5, 0.4)
    tail.data.materials.append(mat_heli)

    # Tail rotor
    bpy.ops.mesh.primitive_torus_add(major_radius=0.8, minor_radius=0.05, location=(loc[0] + 0.4, loc[1] - 4.5, 1.5))
    t_rotor = bpy.context.object
    t_rotor.name = "HeliTailRotor"
    t_rotor.rotation_euler = (0, math.radians(90), 0)
    t_rotor.data.materials.append(mat_rotor)

    # Main rotor mast
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.8, location=(loc[0], loc[1], 2.8))
    mast = bpy.context.object
    mast.name = "HeliMast"
    mast.data.materials.append(mat_rotor)

    # Main rotor blades
    for angle in [0, 90]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], 3.2))
        blade = bpy.context.object
        blade.name = f"HeliBlade_{angle}"
        blade.scale = (4.0, 0.15, 0.05)
        blade.rotation_euler = (0, 0, math.radians(angle))
        blade.data.materials.append(mat_rotor)

    # Skids
    for sx in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0] + sx, loc[1], 0.3))
        skid = bpy.context.object
        skid.name = f"HeliSkid_{sx}"
        skid.scale = (0.08, 2.5, 0.08)
        skid.data.materials.append(mat_rotor)

    # Skid struts
    for sx in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0] + sx, loc[1], 0.8))
        strut = bpy.context.object
        strut.name = f"HeliStrut_{sx}"
        strut.scale = (0.06, 0.06, 1.0)
        strut.data.materials.append(mat_rotor)

    # Cross struts
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1] + 1.0, 0.3))
    cs1 = bpy.context.object
    cs1.name = "HeliCross1"
    cs1.scale = (1.6, 0.06, 0.06)
    cs1.data.materials.append(mat_rotor)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1] - 1.0, 0.3))
    cs2 = bpy.context.object
    cs2.name = "HeliCross2"
    cs2.scale = (1.6, 0.06, 0.06)
    cs2.data.materials.append(mat_rotor)

build_heli((15, 10, 0))

# --- SKI RACK ---
rack_loc = (-8, 12, 0)
# Rack frame
for i in range(4):
    rx = rack_loc[0] - 1.5 + i * 1.0
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2.0, location=(rx, rack_loc[1], 1.0))
    post = bpy.context.object
    post.name = f"SkiRackPost_{i}"
    post.data.materials.append(mat_rack)

# Horizontal bars
for z in [0.5, 1.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=3.5, location=(rack_loc[0], rack_loc[1], z))
    bar = bpy.context.object
    bar.name = f"SkiRackBar_{z}"
    bar.rotation_euler = (0, math.radians(90), 0)
    bar.data.materials.append(mat_rack)

# Skis on rack
for i in range(5):
    sx = rack_loc[0] - 1.2 + i * 0.6
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx, rack_loc[1], 1.0))
    ski = bpy.context.object
    ski.name = f"Ski_{i}"
    ski.scale = (0.08, 0.15, 2.0)
    ski.rotation_euler = (0, math.radians(5), 0)
    ski.data.materials.append(mat_ski)

# --- FUEL CACHE ---
fuel_loc = (5, -15, 0)
# Container
bpy.ops.mesh.primitive_cube_add(size=1, location=(fuel_loc[0], fuel_loc[1], 1.0))
container = bpy.context.object
container.name = "FuelContainer"
container.scale = (2.5, 2.0, 2.0)
container.data.materials.append(mat_fuel)

# Barrels
for i in range(3):
    bx = fuel_loc[0] + 2.0
    by = fuel_loc[1] - 1.0 + i * 1.0
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.2, location=(bx, by, 0.6))
    barrel = bpy.context.object
    barrel.name = f"FuelBarrel_{i}"
    barrel.data.materials.append(mat_barrel)

# Snow drifts around fuel cache
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(fuel_loc[0] - 2, fuel_loc[1] + 1.5, 0.3))
drift1 = bpy.context.object
drift1.name = "FuelDrift1"
drift1.scale = (1.5, 1.0, 0.4)
drift1.data.materials.append(mat_snow)

# --- SNOW DRIFTS / MOUNTAIN SILHOUETTES ---
# Distant mountains
for i in range(6):
    mx = -60 + i * 25
    my = -80 - random.uniform(0, 20)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius=15 + random.uniform(0, 8), depth=30 + random.uniform(0, 15), location=(mx, my, 15))
    mtn = bpy.context.object
    mtn.name = f"Mountain_{i}"
    mtn.data.materials.append(mat_snow)
    mtn.rotation_euler = (0, 0, random.uniform(0, 360))

# Snow drifts on ground
for i in range(12):
    dx = random.uniform(-30, 30)
    dy = random.uniform(-20, 20)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(1, 3), location=(dx, dy, 0.2))
    drift = bpy.context.object
    drift.name = f"SnowDrift_{i}"
    drift.scale = (random.uniform(1, 2), random.uniform(0.8, 1.5), random.uniform(0.2, 0.5))
    drift.data.materials.append(mat_snow)

# --- TREES (simple cones) ---
for i in range(15):
    tx = random.uniform(-35, 35)
    ty = random.uniform(-30, 30)
    # Skip if too close to lodge or pad
    if abs(tx - (-15)) < 10 and abs(ty - (-5)) < 10:
        continue
    if abs(tx - 15) < 10 and abs(ty - 10) < 10:
        continue

    bpy.ops.mesh.primitive_cone_add(vertices=8, radius=1.5, depth=5, location=(tx, ty, 2.5))
    tree = bpy.context.object
    tree.name = f"Tree_{i}"
    tree.data.materials.append(mat_wood)

    # Snow cap on tree
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius=1.2, depth=1.5, location=(tx, ty, 5.0))
    cap = bpy.context.object
    cap.name = f"TreeCap_{i}"
    cap.data.materials.append(mat_snow)

# --- SKY / WORLD ---
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.55, 0.75, 0.95, 1.0)  # Blue morning
    bg.inputs["Strength"].default_value = 1.2

# --- LIGHTING: Fresh blue morning ---
# Sun (low angle, cool blue)
bpy.ops.object.light_add(type='SUN', location=(50, -30, 20))
sun = bpy.context.object
sun.name = "MorningSun"
sun.data.energy = 3.0
sun.data.color = (0.85, 0.92, 1.0)  # Cool blue-white
sun.rotation_euler