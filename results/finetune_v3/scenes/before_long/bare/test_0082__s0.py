import bpy
import math
import random
from mathutils import Vector, Euler

# --- Clean Scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in bpy.data.collections:
    if block.name != "Collection":
        bpy.data.collections.remove(block)

# --- Materials ---
def create_material(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    if emission:
        bsdf.inputs['Emission Color'].default_value = emission
        bsdf.inputs['Emission Strength'].default_value = emission_strength
        
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        bsdf.inputs['Alpha'].default_value = alpha
        
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Colors
mat_wall = create_material("Wall", (0.85, 0.75, 0.6), 0.9)
mat_floor = create_material("Floor", (0.4, 0.3, 0.2), 0.8)
mat_wood = create_material("Wood", (0.35, 0.2, 0.1), 0.7)
mat_wood_dark = create_material("WoodDark", (0.2, 0.1, 0.05), 0.8)
mat_brass = create_material("Brass", (0.85, 0.65, 0.15), 0.2, metallic=1.0)
mat_sack_burlap = create_material("Burlap", (0.6, 0.5, 0.35), 0.9)
mat_glass = create_material("Glass", (0.8, 0.9, 0.9), 0.1, alpha=0.3)
mat_chillie = create_material("Chillie", (0.8, 0.05, 0.02), 0.4)
mat_sun = create_material("Sun", (1, 0.9, 0.7), emission=(1, 0.9, 0.7), emission_strength=5.0)

# Spice Colors
spice_colors = [
    (0.9, 0.2, 0.0),  # Red
    (0.9, 0.8, 0.0),  # Yellow
    (0.5, 0.0, 0.0),  # Dark Red
    (0.9, 0.5, 0.0),  # Orange
    (0.3, 0.1, 0.0),  # Brown
    (0.8, 0.1, 0.3),  # Pinkish
    (0.1, 0.4, 0.1),  # Green
    (0.9, 0.9, 0.8),  # White
]

# --- Room ---
# Floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Floor"
floor.data.materials.append(mat_floor)

# Walls
# Back wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 5, 5), rotation=(math.radians(90), 0, 0))
bpy.context.object.name = "BackWall"
bpy.context.object.data.materials.append(mat_wall)

# Left wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(-5, 0, 5), rotation=(0, math.radians(90), 0))
bpy.context.object.name = "LeftWall"
bpy.context.object.data.materials.append(mat_wall)

# Right wall (with window opening simulated by light shaft)
bpy.ops.mesh.primitive_plane_add(size=10, location=(5, 0, 5), rotation=(0, math.radians(90), 0))
bpy.context.object.name = "RightWall"
bpy.context.object.data.materials.append(mat_wall)

# Ceiling
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 10), rotation=(math.radians(180), 0, 0))
bpy.context.object.name = "Ceiling"
bpy.context.object.data.materials.append(mat_wall)

# --- Counter/Shelves ---
# Main counter
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 2, 0.5))
counter = bpy.context.object
counter.name = "Counter"
counter.scale = (4, 1, 0.5)
counter.data.materials.append(mat_wood)

# Back shelf unit
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.5, 2))
shelf_unit = bpy.context.object
shelf_unit.name = "ShelfUnit"
shelf_unit.scale = (4, 0.5, 3)
shelf_unit.data.materials.append(mat_wood_dark)

# Shelf boards
for i in range(4):
    z = 1 + i * 0.8
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.5, z))
    shelf = bpy.context.object
    shelf.name = f"Shelf_{i}"
    shelf.scale = (4, 0.4, 0.05)
    shelf.data.materials.append(mat_wood)

# --- Jars on Shelves ---
def add_jar(x, y, z, scale=1.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15 * scale, depth=0.3 * scale, location=(x, y, z))
    jar = bpy.context.object
    jar.name = "Jar"
    jar.data.materials.append(mat_glass)
    # Spice inside
    spice_idx = random.randint(0, len(spice_colors) - 1)
    mat_spice = create_material(f"Spice_{spice_idx}_{random.randint(0,1000)}", spice_colors[spice_idx], 0.9)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.13 * scale, depth=0.2 * scale, location=(x, y, z - 0.05 * scale))
    spice = bpy.context.object
    spice.name = "Spice"
    spice.data.materials.append(mat_spice)

for i in range(4):
    z = 1.05 + i * 0.8
    for j in range(8):
        x = -1.8 + j * 0.5
        if random.random() > 0.2:
            add_jar(x, 4.5, z, scale=random.uniform(0.8, 1.2))

# --- Sacks on Floor ---
def add_sack(x, y, z, scale=1.0, spice_color=None):
    if not spice_color:
        spice_color = random.choice(spice_colors)
    mat_spice = create_material(f"SackSpice_{random.randint(0,1000)}", spice_color, 0.9)
    
    # Sack body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4 * scale, location=(x, y, z))
    sack = bpy.context.object
    sack.name = "Sack"
    sack.scale = (1, 1, 1.2)
    sack.data.materials.append(mat_sack_burlap)
    
    # Top opening
    bpy.ops.mesh.primitive_torus_add(major_radius=0.3 * scale, minor_radius=0.05 * scale, location=(x, y, z + 0.45 * scale))
    rim = bpy.context.object
    rim.name = "SackRim"
    rim.data.materials.append(mat_sack_burlap)
    
    # Spice pile
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35 * scale, location=(x, y, z + 0.4 * scale))
    spice_pile = bpy.context.object
    spice_pile.name = "SpicePile"
    spice_pile.scale = (1, 1, 0.5)
    spice_pile.data.materials.append(mat_spice)

# Place sacks
sack_positions = [
    (-3, 3, 0.5, 1.2),
    (-2, 3.5, 0.4, 0.9),
    (2.5, 3, 0.5, 1.1),
    (3.5, 3.5, 0.4, 0.8),
    (-1, 1, 0.4, 0.7),
    (1.5, 1.5, 0.4, 0.8),
]
for pos in sack_positions:
    add_sack(*pos)

# --- Brass Scales ---
def add_scales(x, y, z):
    # Base
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.05, location=(x, y, z))
    base = bpy.context.object
    base.name = "ScaleBase"
    base.data.materials.append(mat_brass)
    
    # Pillar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.5, location=(x, y, z + 0.25))
    pillar = bpy.context.object
    pillar.name = "ScalePillar"
    pillar.data.materials.append(mat_brass)
    
    # Beam
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + 0.5))
    beam = bpy.context.object
    beam.name = "ScaleBeam"
    beam.scale = (0.5, 0.02, 0.02)
    beam.data.materials.append(mat_brass)
    
    # Pans
    for side in [-1, 1]:
        px = x + side * 0.5
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.02, location=(px, y, z + 0.3))
        pan = bpy.context.object
        pan.name = f"ScalePan_{side}"
        pan.data.materials.append(mat_brass)
        # Strings
        for angle in [0, 120, 240]:
            rad = math.radians(angle)
            sx = px + 0.1 * math.cos(rad)
            sy = y + 0.1 * math.sin(rad)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.2, location=((x+px)/2, y, z + 0.4))
            string = bpy.context.object
            string.name = "String"
            string.data.materials.append(mat_brass)
            # Rotate string to connect
            start = Vector((sx, sy, z + 0.3))
            end = Vector((x, y, z + 0.5))
            mid = (start + end) / 2
            string.location = mid
            string.rotation_euler = end.to_track_quat('Z', 'Y').to_euler()
            string.scale = (1, 1, (end - start).length / 2)

add_scales(0, 2.5, 1.0)

# --- Grinding Mill ---
def add_mill(x, y, z):
    # Base
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.1, location=(x, y, z))
    base = bpy.context.object
    base.name = "MillBase"
    base.data.materials.append(mat_wood_dark)
    
    # Lower stone
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, location=(x, y, z + 0.125))
    lower = bpy.context.object
    lower.name = "MillLower"
    lower.data.materials.append(mat_wood)
    
    # Upper stone
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, location=(x, y, z + 0.3))
    upper = bpy.context.object
    upper.name = "MillUpper"
    upper.data.materials.append(mat_wood)
    
    # Handle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.4, location=(x + 0.2, y, z + 0.3), rotation=(0, math.radians(90), 0))
    handle = bpy.context.object
    handle.name = "MillHandle"
    handle.data.materials.append(mat_wood_dark)
    
    # Spoon on top
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(x, y, z + 0.4))
    spoon = bpy.context.object
    spoon.name = "MillSpoon"
    spoon.scale = (1, 1, 0.5)
    spoon.data.materials.append(mat_brass)

add_mill(-2, 2.5, 1.0)

# --- Strings of Chillies ---
def add_chillie_string(x, y, z_start, z_end, count=15):
    for i in range(count):
        t = i / (count - 1)
        z = z_start + t * (z_end - z_start)
        # Slight curve
        offset_x = math.sin(t * math.pi) * 0.1
        offset_y = math.cos(t * math.pi) * 0.05
        
        # Chillie
        bpy.ops.mesh.primitive_cone_add(radius1=0.02, radius2=0.005, depth=0.08, location=(x + offset_x, y + offset_y, z))
        chillie = bpy.context.object
        chillie.name = "Chillie"
        chillie.rotation_euler = (math.radians(180), 0, 0)
        chillie.data.materials.append(mat_chillie)
        
        # Stem
        bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.02, location=(x + offset_x, y + offset_y, z + 0.04))
        stem = bpy.context.object
        stem.name = "ChillieStem"
        stem.data.materials.append(create_material("Stem", (0.1, 0.3, 0.1), 0.5))

# Hang chillies from ceiling
chillie_positions = [
    (-1, -1, 4, 3),
    (0, -2, 4, 2.8),
    (1, -1, 4, 3.2),
    (-2, -3, 4, 2.9),
    (2, -2, 4, 3.1),
]
for pos in chillie_positions:
    add_chillie_string(*pos)

# --- Lighting: Afternoon Sun Shaft ---
# Sun light
bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
sun_light = bpy.context.object
sun_light.name = "AfternoonSun"
sun_light.data.energy = 10
sun_light.data.color = (1, 0.9, 0.7)
sun_light.rotation_euler = (math.radians(45), math.radians(30), math.radians(15))
sun_light.data.shadow_soft_size = 0.5

# World background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.1, 0.1, 0.15)
    bg_node.inputs[1].default_value = 0.5

# Volumetric light shaft
bpy.ops.object.light_add(type='SPOT', location=(4, -3, 6))
spot_light = bpy.context.object
spot_light.name = "SunShaft"
spot_light.data.energy = 50
spot_light.data.color = (1, 0.85, 0.6)
spot_light.data.spot_size = math.radians(45)
spot_light.data.spot_blend = 0.5
spot_light.rotation_euler = (math.radians(60), math.radians(20), math.radians(10))
spot_light.data.shadow_soft_size = 1.0

# Add a volumetric cube for the light shaft effect
bpy.ops.mesh.primitive_cube_add(size=1, location=(2, -1, 3))
vol_cube = bpy.context.object
vol_cube.name = "LightShaftVolume"
vol_cube.scale = (3, 3, 4)
vol_cube.rotation_euler = (math.radians(30), math.radians(15), math.radians(10))

mat_vol = bpy.data.materials.new("VolumetricLight")
mat_vol.use_nodes = True
nodes = mat_vol.node_tree.nodes
links = mat_vol.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
output.location = (300, 0)

vol = nodes.new('ShaderNodeVolumePrincipled')
vol.location = (0, 0)
vol.inputs['Color'].default_value = (1, 0.9, 0.7)
vol.inputs['Density'].default_value = 0.02
vol.inputs['Anisotropy'].default_value = 0.3

links.new(vol.outputs['Volume'], output.inputs['Volume'])

vol_cube.data.materials.append(mat_vol)
vol_cube.display_type = 'WIRE'
vol_cube.visible_shadow = False

# --- Camera ---
bpy.ops.object.camera_add(location=(-3, -4, 2))
camera = bpy.context.object
camera.name = "MainCamera"
bpy.context.scene.camera = camera

# Point camera at center of shop
direction = Vector((0, 2, 1.5)) - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Set camera properties
camera.data.lens = 35
camera.data.dof.use_dof = True
camera.data.dof.focus_distance = direction.length
camera.data.dof.aperture_fstop = 2.8

# --- Render Settings ---
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.volume_bounces = 2
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# Set up the scene for the sun shaft to be visible
scene.cycles.volume_step_rate = 0.5
scene.cycles.volume_max_steps = 512
