import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- MATERIALS ---
def get_or_create_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_snow = get_or_create_material("Snow", (0.95, 0.97, 1.0), 0.3)
mat_tower = get_or_create_material("Tower_Metal", (0.3, 0.3, 0.35), 0.4, 0.8)
mat_orange = get_or_create_material("Orange_Tent", (1.0, 0.4, 0.0), 0.6)
mat_flag = get_or_create_material("Flag_Red", (0.8, 0.05, 0.05), 0.8)
mat_ice = get_or_create_material("Ice", (0.7, 0.85, 0.95), 0.1, 0.0)
mat_dark = get_or_create_material("Dark_Metal", (0.1, 0.1, 0.1), 0.5, 0.6)
mat_wood = get_or_create_material("Wood", (0.4, 0.25, 0.1), 0.8)

# --- LIGHTING (Cold Sun) ---
# World
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.6, 0.7, 0.9, 1.0)  # Cold blue sky
    bg.inputs[1].default_value = 1.0

# Sun
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3.0
sun_data.color = (0.9, 0.95, 1.0)  # Slightly cool white
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(60), math.radians(10), math.radians(120))  # Low angle for long shadows

# --- GROUND (Snow/Ice) ---
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.active_object
ground.data.materials.append(mat_snow)
# Add some noise to ground
subsurf = ground.modifiers.new("Subsurf", 'SUBSURF')
subsurf.subdivision_type = 'SIMPLE'
subsurf.levels = 4
subsurf.render_levels = 4
tex = bpy.data.textures.new("SnowNoise", 'CLOUDS')
tex.noise_scale = 2.0
disp = ground.modifiers.new("Disp", 'DISPLACE')
disp.texture = tex
disp.strength = 0.5
disp.mid_level = 0.5

# --- DRILLING TOWER ---
def create_tower(location, height=15, width=2):
    # Base
    bpy.ops.mesh.primitive_cube_add(location=(location[0], location[1], 0.5))
    base = bpy.context.active_object
    base.scale = (width, width, 0.5)
    base.data.materials.append(mat_dark)
    
    # Legs (4)
    leg_height = height
    for i in range(4):
        angle = i * math.pi / 2 + math.pi / 4
        lx = location[0] + width * math.cos(angle)
        ly = location[1] + width * math.sin(angle)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=leg_height, location=(lx, ly, leg_height/2))
        leg = bpy.context.active_object
        leg.data.materials.append(mat_tower)
        
    # Cross beams
    for h in range(2, int(height), 3):
        for i in range(4):
            angle1 = i * math.pi / 2 + math.pi / 4
            angle2 = (i + 1) % 4 * math.pi / 2 + math.pi / 4
            x1 = location[0] + width * math.cos(angle1)
            y1 = location[1] + width * math.sin(angle1)
            x2 = location[0] + width * math.cos(angle2)
            y2 = location[1] + width * math.sin(angle2)
            
            # Beam
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            rot_z = math.atan2(y2-y1, x2-x1)
            bpy.ops.mesh.primitive_cube_add(location=(mid_x, mid_y, h))
            beam = bpy.context.active_object
            beam.scale = (length/2, 0.1, 0.1)
            beam.rotation_euler = (0, 0, rot_z)
            beam.data.materials.append(mat_tower)
            
    # Top platform
    bpy.ops.mesh.primitive_cube_add(location=(location[0], location[1], height))
    platform = bpy.context.active_object
    platform.scale = (width + 0.5, width + 0.5, 0.2)
    platform.data.materials.append(mat_tower)
    
    # Drill head
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(location[0], location[1], height - 1))
    drill = bpy.context.active_object
    drill.data.materials.append(mat_dark)
    
    # Drill bit (going into ice)
    bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.0, depth=3, location=(location[0], location[1], -1.5))
    bit = bpy.context.active_object
    bit.rotation_euler = (math.radians(180), 0, 0)
    bit.data.materials.append(mat_dark)

create_tower((0, 0, 0))

# --- TRENCH LAB ---
def create_trench_lab(location):
    # Excavated area (slightly lower)
    bpy.ops.mesh.primitive_cube_add(location=(location[0], location[1], -0.5))
    trench = bpy.context.active_object
    trench.scale = (8, 4, 0.5)
    trench.data.materials.append(mat_ice)
    
    # Lab structure inside trench
    bpy.ops.mesh.primitive_cube_add(location=(location[0], location[1], 0.2))
    lab = bpy.context.active_object
    lab.scale = (6, 3, 1)
    lab.data.materials.append(mat_orange)
    
    # Windows (dark panels)
    for i in range(3):
        x = location[0] - 2 + i * 2
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, location[1] + 3.01, 0.5))
        window = bpy.context.active_object
        window.rotation_euler = (math.radians(90), 0, 0)
        window.scale = (0.8, 0.8, 1)
        window.data.materials.append(mat_dark)
        
    # Stairs down to trench
    for i in range(5):
        bpy.ops.mesh.primitive_cube_add(location=(location[0] + 8, location[1], 0.1 - i * 0.1))
        step = bpy.context.active_object
        step.scale = (0.5, 2, 0.05)
        step.data.materials.append(mat_dark)

create_trench_lab((15, 0, 0))

# --- ORANGE TENTS ---
def create_tent(location, size=2):
    # Cone shape
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=size, radius2=0, depth=size*1.2, location=(location[0], location[1], size*0.6))
    tent = bpy.context.active_object
    tent.data.materials.append(mat_orange)
    
    # Entrance flap (slightly darker)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(location[0] + size*0.8, location[1], size*0.4))
    flap = bpy.context.active_object
    flap.rotation_euler = (math.radians(90), 0, math.radians(90))
    flap.scale = (0.8, 0.8, 1)
    flap.data.materials.append(mat_dark)

# Cluster of tents
tent_positions = [
    (-10, 10, 2.5),
    (-12, 8, 2.0),
    (-8, 12, 2.2),
    (-15, 12, 1.8),
    (-11, 14, 2.3),
]
for pos in tent_positions:
    create_tent(pos)

# --- SLEDGES ---
def create_sledge(location, rotation=0):
    # Platform
    bpy.ops.mesh.primitive_cube_add(location=(location[0], location[1], 0.3))
    platform = bpy.context.active_object
    platform.scale = (1.5, 0.8, 0.1)
    platform.data.materials.append(mat_wood)
    
    # Runners
    for i in range(2):
        x = location[0] - 0.6 + i * 1.2
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=3, location=(x, location[1], 0.1))
        runner = bpy.context.active_object
        runner.rotation_euler = (0, math.radians(90), 0)
        runner.data.materials.append(mat_dark)
        
    # Cargo (crates)
    for i in range(3):
        cx = location[0] - 0.8 + i * 0.8
        bpy.ops.mesh.primitive_cube_add(location=(cx, location[1], 0.6))
        crate = bpy.context.active_object
        crate.scale = (0.3, 0.3, 0.3)
        crate.data.materials.append(mat_wood)
        
    # Rotate whole sledge
    for obj in bpy.context.selected_objects:
        pass  # We'll handle rotation differently

# Create sledges
sledge_positions = [
    (5, 5, 0.5),
    (7, 3, 1.0),
    (10, 8, 0.3),
    (-5, -5, 0.8),
]
for pos in sledge_positions:
    create_sledge(pos)

# --- FLAG MARKED ROUTE ---
def create_flag_route(start, end, num_flags=10):
    for i in range(num_flags):
        t = i / (num_flags - 1)
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        
        # Pole
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2, location=(x, y, 1))
        pole = bpy.context.active_object
        pole.data.materials.append(mat_dark)
        
        # Flag
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x + 0.3, y, 1.8))
        flag = bpy.context.active_object
        flag.rotation_euler = (0, math.radians(90), 0)
        flag.scale = (0.4, 0.3, 1)
        flag.data.materials.append(mat_flag)
        
        # Add slight wave to flag
        sub = flag.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = 2
        sub.render_levels = 2
        tex = bpy.data.textures.new(f"Wave_{i}", 'MARBLE')
        disp = flag.modifiers.new("Disp", 'DISPLACE')
        disp.texture = tex
        disp.strength = 0.1
        disp.direction = 'Z'

# Route from base camp to trench lab
create_flag_route((-10, 10), (15, 0), 12)

# --- ICE CORES (sample tubes) ---
def create_ice_core(location):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.5, location=(location[0], location[1], 0.75))
    core = bpy.context.active_object
    core.data.materials.append(mat_ice)
    
    # Label
    bpy.ops.mesh.primitive_plane_add(size=0.1, location=(location[0] + 0.16, location[1], 1.0))
    label = bpy.context.active_object
    label.rotation_euler = (0, math.radians(90), 0)
    label.data.materials.append(mat_flag)

# Scattered ice cores
core_positions = [
    (2, 2), (3, 1), (1, 3), (4, 4), (2, 5),
    (16, 2), (17, 1), (18, 3), (15, 2),
]
for pos in core_positions:
    create_ice_core(pos)

# --- CAMERA ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (-25, 25, 15)
cam_obj.rotation_euler = (math.radians(70), 0, math.radians(-45))
bpy.context.scene.camera = cam_obj

# --- RENDER SETTINGS ---
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
