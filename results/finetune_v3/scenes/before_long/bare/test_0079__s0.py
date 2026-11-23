import bpy
import math
import random

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create collections
for name in ["Structure", "Conveyors", "Crusher", "Furnace", "IngotStacks", "HazardLights"]:
    if name in bpy.data.collections:
        bpy.data.collections[name].clear()
    else:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)

def get_col(name):
    return bpy.data.collections[name]

def link_to(obj, col_name):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    get_col(col_name).objects.link(obj)

def set_mat(obj, color, metallic=0.8, roughness=0.3, emission=None, emit_strength=0.0):
    mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    obj.data.materials.append(mat)
    return mat

# =====================
# ROOM STRUCTURE
# =====================
# Floor
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
set_mat(floor, (0.2, 0.2, 0.22), metallic=0.5, roughness=0.6)
link_to(floor, "Structure")

# Walls
wall_h = 6
wall_thick = 0.3
walls_data = [
    ("Wall_N", (0, -10, wall_h/2), (20, wall_thick, wall_h)),
    ("Wall_S", (0, 10, wall_h/2), (20, wall_thick, wall_h)),
    ("Wall_W", (-10, 0, wall_h/2), (wall_thick, 20, wall_h)),
    ("Wall_E", (10, 0, wall_h/2), (wall_thick, 20, wall_h)),
]
for name, loc, dims in walls_data:
    bpy.ops.mesh.primitive_cube_add(location=loc)
    w = bpy.context.active_object
    w.name = name
    w.scale = (dims[0]/2, dims[1]/2, dims[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    set_mat(w, (0.35, 0.35, 0.38), metallic=0.3, roughness=0.7)
    link_to(w, "Structure")

# Ceiling
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, wall_h))
ceil = bpy.context.active_object
ceil.name = "Ceiling"
ceil.rotation_euler = (math.pi, 0, 0)
set_mat(ceil, (0.3, 0.3, 0.33), metallic=0.3, roughness=0.7)
link_to(ceil, "Structure")

# Pillars
pillar_positions = [(-7, -7), (-7, 7), (7, -7), (7, 7)]
for i, (px, py) in enumerate(pillar_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=wall_h, location=(px, py, wall_h/2))
    p = bpy.context.active_object
    p.name = f"Pillar_{i}"
    set_mat(p, (0.4, 0.4, 0.42), metallic=0.6, roughness=0.4)
    link_to(p, "Structure")

# =====================
# CONVEYOR BELTS
# =====================
def make_conveyor(name, start, end, width=1.2, height=0.8, belt_color=(0.15, 0.15, 0.15)):
    """Create a conveyor belt from start to end."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    mid = ((start[0]+end[0])/2, (start[1]+end[1])/2, (start[2]+end[2])/2)
    rot_z = math.atan2(dy, dx)

    # Frame (base)
    bpy.ops.mesh.primitive_cube_add(location=mid)
    frame = bpy.context.active_object
    frame.name = f"{name}_Frame"
    frame.scale = (length/2, width/2, 0.3)
    frame.rotation_euler = (0, 0, rot_z)
    bpy.ops.object.transform_apply(scale=True)
    set_mat(frame, (0.5, 0.5, 0.52), metallic=0.7, roughness=0.3)
    link_to(frame, "Conveyors")

    # Belt surface
    bpy.ops.mesh.primitive_cube_add(location=(mid[0], mid[1], mid[2] + 0.32))
    belt = bpy.context.active_object
    belt.name = f"{name}_Belt"
    belt.scale = (length/2 - 0.1, width/2 - 0.05, 0.05)
    belt.rotation_euler = (0, 0, rot_z)
    bpy.ops.object.transform_apply(scale=True)
    set_mat(belt, belt_color, metallic=0.2, roughness=0.8)
    link_to(belt, "Conveyors")

    # Side rails
    for side in [-1, 1]:
        offset_y = side * (width/2 - 0.02)
        # Calculate perpendicular offset
        perp_x = -math.sin(rot_z) * offset_y
        perp_y = math.cos(rot_z) * offset_y
        rail_loc = (mid[0] + perp_x, mid[1] + perp_y, mid[2] + 0.35)
        bpy.ops.mesh.primitive_cube_add(location=rail_loc)
        rail = bpy.context.active_object
        rail.name = f"{name}_Rail_{side}"
        rail.scale = (length/2 - 0.05, 0.05, 0.15)
        rail.rotation_euler = (0, 0, rot_z)
        bpy.ops.object.transform_apply(scale=True)
        set_mat(rail, (0.6, 0.6, 0.62), metallic=0.8, roughness=0.2)
        link_to(rail, "Conveyors")

    # Rollers (visual)
    num_rollers = max(2, int(length / 0.5))
    for i in range(num_rollers):
        t = (i + 0.5) / num_rollers
        rx = start[0] + dx * t
        ry = start[1] + dy * t
        rz = start[2] + dz * t
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=width - 0.1, location=(rx, ry, rz + 0.15))
        roller = bpy.context.active_object
        roller.name = f"{name}_Roller_{i}"
        # Rotate cylinder to align with conveyor direction
        roller.rotation_euler = (math.pi/2, 0, rot_z)
        set_mat(roller, (0.55, 0.55, 0.58), metallic=0.9, roughness=0.15)
        link_to(roller, "Conveyors")

    return frame

# Main conveyor: from left to center
make_conveyor("Conv_Main", (-9, 0, 0.8), (0, 0, 0.8), width=1.5)

# Branch conveyor: from center to furnace area
make_conveyor("Conv_Furnace", (0, 0, 0.8), (4, 3, 0.8), width=1.2)

# Output conveyor: from furnace to ingot stacks
make_conveyor("Conv_Output", (4, 3, 0.8), (8, 6, 0.8), width=1.2)

# =====================
# CRUSHER
# =====================
crusher_loc = (-5, -4, 0)

# Base platform
bpy.ops.mesh.primitive_cube_add(location=(crusher_loc[0], crusher_loc[1], 0.3))
c_base = bpy.context.active_object
c_base.name = "Crusher_Base"
c_base.scale = (2.5, 2.5, 0.3)
bpy.ops.object.transform_apply(scale=True)
set_mat(c_base, (0.45, 0.45, 0.48), metallic=0.6, roughness=0.4)
link_to(c_base, "Crusher")

# Main body
bpy.ops.mesh.primitive_cube_add(location=(crusher_loc[0], crusher_loc[1], 1.8))
c_body = bpy.context.active_object
c_body.name = "Crusher_Body"
c_body.scale = (2, 2, 1.2)
bpy.ops.object.transform_apply(scale=True)
set_mat(c_body, (0.5, 0.48, 0.45), metallic=0.7, roughness=0.3)
link_to(c_body, "Crusher")

# Hopper (top funnel)
bpy.ops.mesh.primitive_cone_add(radius1=2.2, radius2=0.8, depth=1.5, location=(crusher_loc[0], crusher_loc[1], 3.5))
hopper = bpy.context.active_object
hopper.name = "Crusher_Hopper"
set_mat(hopper, (0.55, 0.52, 0.48), metallic=0.7, roughness=0.3)
link_to(hopper, "Crusher")

# Crusher jaws (two angled plates)
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(location=(crusher_loc[0] + side * 0.6, crusher_loc[1], 1.5))
    jaw = bpy.context.active_object
    jaw.name = f"Crusher_Jaw_{side}"
    jaw.scale = (0.15, 1.5, 1.0)
    jaw.rotation_euler = (0, side * 0.3, 0)
    bpy.ops.object.transform_apply(scale=True)
    set_mat(jaw, (0.3, 0.3, 0.32), metallic=0.9, roughness=0.2)
    link_to(jaw, "Crusher")

# Output chute
bpy.ops.mesh.primitive_cube_add(location=(crusher_loc[0] + 2.5, crusher_loc[1], 0.8))
chute = bpy.context.active_object
chute.name = "Crusher_Chute"
chute.scale = (1.0, 1.0, 0.3)
chute.rotation_euler = (0, 0.3, 0)
bpy.ops.object.transform_apply(scale=True)
set_mat(chute, (0.5, 0.5, 0.52), metallic=0.6, roughness=0.4)
link_to(chute, "Crusher")

# =====================
# MOLTEN FURNACE
# =====================
furnace_loc = (4, 3, 0)

# Base
bpy.ops.mesh.primitive_cylinder_add(radius=2.5, depth=0.5, location=(furnace_loc[0], furnace_loc[1], 0.25))
f_base = bpy.context.active_object
f_base.name = "Furnace_Base"
set_mat(f_base, (0.4, 0.38, 0.35), metallic=0.5, roughness=0.5)
link_to(f_base, "Furnace")

# Main vessel
bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=3.0, location=(furnace_loc[0], furnace_loc[1], 2.0))
f_vessel = bpy.context.active_object
f_vessel.name = "Furnace_Vessel"
set_mat(f_vessel, (0.35, 0.3, 0.28), metallic=0.6, roughness=0.4)
link_to(f_vessel, "Furnace")

# Molten interior (emissive)
bpy.ops.mesh.primitive_cylinder_add(radius=1.7, depth=2.5, location=(furnace_loc[0], furnace_loc[1], 1.8))
molten = bpy.context.active_object
molten.name = "Furnace_Molten"
set_mat(molten, (1.0, 0.3, 0.05), metallic=0.0, roughness=0.2, emission=(1.0, 0.25, 0.02), emit_strength=5.0)
link_to(molten, "Furnace")

# Top opening ring
bpy.ops.mesh.primitive_torus_add(major_radius=2.0, minor_radius=0.15, location=(furnace_loc[0], furnace_loc[1], 3.5))
f_ring = bpy.context.active_object
f_ring.name = "Furnace_Ring"
set_mat(f_ring, (0.5, 0.45, 0.4), metallic=0.8, roughness=0.2)
link_to(f_ring, "Furnace")

# Support legs
for i in range(4):
    angle = i * math.pi / 2
    lx = furnace_loc[0] + math.cos(angle) * 2.2
    ly = furnace_loc[1] + math.sin(angle) * 2.2
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.8, location=(lx, ly, 0.4))
    leg = bpy.context.active_object
    leg.name = f"Furnace_Leg_{i}"
    set_mat(leg, (0.45, 0.42, 0.38), metallic=0.7, roughness=0.3)
    link_to(leg, "Furnace")

# Glow light inside furnace
bpy.ops.light.add(type='POINT', location=(furnace_loc[0], furnace_loc[1], 2.0))
furnace_light = bpy.context.active_object
furnace_light.name = "Furnace_Light"
furnace_light.data.color = (1.0, 0.4, 0.1)
furnace_light.data.energy = 200
furnace_light.data.shadow_soft_size = 1.0
link_to(furnace_light, "Furnace")

# =====================
# INGOT STACKS
# =====================
def make_ingot_stack(name, location, rows=3, cols=3, layers=4, ingot_size=(0.6, 0.3, 0.15)):
    """Create a stack of ingots."""
    stack_objects = []
    for layer in range(layers):
        for r in range(rows):
            for c in range(cols):
                # Slight random offset for realism
                ox = random.uniform(-0.02, 0.02)
                oy = random.uniform(-0.02, 0.02)
                x = location[0] + (c - cols/2 + 0.5) * (ingot_size[0] + 0.05) + ox
                y = location[1] + (r - rows/2 + 0.5) * (ingot_size[1] + 0.05) + oy
                z = location[2] + layer * (ingot_size[2] + 0.02)
                
                bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
                ingot = bpy.context.active_object
                ingot.name = f"{name}_L{layer}_R{r}_C{c}"
                ingot.scale = (ingot_size[0]/2, ingot_size[1]/2, ingot_size[2]/2)
                bpy.ops.object.transform_apply(scale=True)
                
                # Slight color variation
                base_r = 0.75 + random.uniform(-0.05, 0.05)
                base_g = 0.65 + random.uniform(-0.05, 0.05)
                base_b = 0.3 + random.uniform(-0.03, 0.03)
                set_mat(ingot, (base_r, base_g, base_b), metallic=0.95, roughness=0.15)
                link_to(ingot, "IngotStacks")
                stack_objects.append(ingot)
    return stack_objects

# Stack 1: near output conveyor end
make_ingot_stack("IngotStack1", (8.5, 6.5, 0.05), rows=3, cols=4, layers=5)

# Stack 2: another pile
make_ingot_stack("IngotStack2", (9.0, 4.5, 0.05), rows=2, cols=3, layers=4)

# Stack 3: smaller pile
make_ingot_stack("IngotStack3", (7.5, 8.0, 0.05), rows=3, cols=3, layers=3)

# =====================
# HAZARD LIGHTS (rotating)
# =====================
def make_hazard_light(name, location, height=4.0):
    """Create a rotating hazard light on a pole."""
    # Pole
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=height, location=(location[0], location[1], height/2))
    pole = bpy.context.active_object
    pole.name = f"{name}_Pole"
    set_mat(pole, (0.3, 0.3, 0.32), metallic=0.8, roughness=0.3)
    link_to(pole, "HazardLights")

    # Light housing (base)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, location=(location[0], location[1], height))
    housing = bpy.context.active_object
    housing.name = f"{name}_Housing"
    set_mat(housing, (0.2, 0.2, 0.22), metallic=0.6, roughness=0.4)
    link_to(housing, "HazardLights")

    # Rotating lamp (emissive orange)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.3, location=(location[0], location[1], height + 0.2))
    lamp = bpy.context.active_object
    lamp.name = f"{name}_Lamp"
    set_mat(lamp, (1.0, 0.5, 0.0), metallic=0.0, roughness=0.2, emission=(1.0, 0.45, 0.0), emit_strength=8.0)
    link_to(lamp, "HazardLights")

    # Point light for the glow
    bpy.ops.light.add(type='POINT', location=(location[0], location[1], height + 0.2))
    light = bpy.context.active_object
    light.name = f"{name}_Light"
    light.data.color = (1.0, 0.5, 0.0)
    light.data.energy = 50
    light.data.shadow_soft_size = 0.3
    link_to(light, "HazardLights")

    # Create an empty to animate rotation
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(location[0], location[1], height + 0.2))
    empty = bpy.context.active_object
    empty.name = f"{name}_Rotator"
    link_to(empty, "HazardLights")

    # Parent lamp and light to empty
    lamp.parent = empty
    light.parent = empty
    lamp.matrix_parent_inverse = empty.matrix_world.inverted()
    light.matrix_parent_inverse = empty.matrix_world.inverted()

    # Animate rotation
    empty.rotation_euler = (0, 0, 0)
    empty.keyframe_insert(data_path="rotation_euler", frame=1)
    empty.rotation_euler = (0, 0, math.radians(360))
    empty.keyframe_insert(data_path="rotation_euler", frame=60)

    # Make animation loop
    for fc in empty.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
        fc.modifiers.new(type='CYCLES')

    return empty

# Place hazard lights around the room
hazard_positions = [
    (-8, -8),
    (8, -8),
    (-8, 8),
    (8, 8),
    (-5, 4),
    (5, -4),
]

for i, (hx, hy) in enumerate(hazard_positions):
    make_hazard_light(f"Hazard_{i}", (hx, hy), height=4.5)

# =====================
# ADDITIONAL DETAILS
# =====================

# Pipes along walls
for i, (x1, y1, x2, y2) in enumerate([
    (-9.5, -9.5, 9.5, -9.5),  # North wall pipe
    (-9.5, 9.5, 9.5, 9.5),    # South wall pipe
    (-9.5, -9.5, -9.5, 9.5),  # West wall pipe
]):
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    mid = ((x1+x2)/2, (y1+y2)/2, 4.5)
    rot_z = math.atan2(dy, dx)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=length, location=mid)
    pipe = bpy.context.active_object
    pipe.name = f"Pipe_{i}"
    pipe.rotation_euler = (math.pi/2, 0, rot_z)
    set_mat(pipe, (0.6, 0.55, 0.5), metallic=0.85, roughness=0.15)
    link_to(pipe, "Structure")

# Warning stripes on floor (simple planes)
for i, (sx, sy, sw, sh) in enumerate([
    (-6, -2, 2, 0.3),
    (-6, 2, 2, 0.3),
    (2, -2, 2, 0.3),
    (2, 2, 2, 0.3),
]):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(sx, sy, 0.01))
    stripe = bpy.context.active_object
    stripe.name = f"WarningStripe_{i}"
    stripe.scale = (sw/2, sh/2, 1)
    bpy.ops.object.transform_apply(scale=True)
    # Yellow-black striped material (simplified: just yellow)
    set_mat(stripe, (0.9, 0.8, 0.1), metallic=0.1, roughness=0.8)
    link_to(stripe, "Structure")

# Control panel
bpy.ops.mesh.primitive_cube_add(location=(-8, 0, 1.5))
panel = bpy.context.active_object
panel.name = "ControlPanel"
panel.scale = (0.3, 1.5, 1.0)
bpy.ops.object.transform_apply(scale=True)
set_mat(panel, (0.25, 0.25, 0.28), metallic=0.5, roughness=0.4)
link_to(panel, "Structure")

# Screen on panel
bpy.ops.mesh.primitive_plane_add(size=1, location=(-7.85, 0, 1.6))
screen = bpy.context.active_object
screen.name = "PanelScreen"
screen.rotation_euler = (0, math.pi/2, 0)
screen.scale = (0.8, 0.5, 1)
bpy.ops.object.transform_apply(scale=True)
set_mat(screen, (0.0, 0.3, 0.5), metallic=0.0, roughness=0.3, emission=(0.0, 0.25, 0.4), emit_strength=2.0)
link_to(screen, "Structure")

# =====================
# LIGHTING
# =====================
# Main overhead lights
for i, (lx, ly) in enumerate([(-5, -5), (5, -5), (-5, 5), (5, 5)]):
    bpy.ops.light.add(type='AREA', location=(lx, ly, 5.5))
    area_light = bpy.context.active_object
    area_light.name = f"CeilingLight_{i}"
    area_light.data.energy = 150
    area_light.data.size = 2.0
    area_light.data.color = (0.9, 0.9, 1.0)
    area_light.rotation_euler = (0, 0, 0)
    link_to(area_light, "Structure")

# Ambient fill
bpy.ops.light.add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object
sun.name = "AmbientSun"
sun.data.energy = 0.5
sun.data.angle = math.radians(10)
link_to(sun, "Structure")

# =====================
# CAMERA
# =====================
bpy.ops.object.camera_add(location=(-8, -8, 4), rotation=(math.radians(60), 0, math.radians(45)))
camera = bpy.context.active_object
camera.name = "MainCamera"
bpy.context.scene.camera = camera
camera.data.lens = 35

# Set up viewport
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

# World settings
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.05, 0.05, 0.08)
bg.inputs[1].default_value = 1.0

print("Machine hall scene created successfully!")
