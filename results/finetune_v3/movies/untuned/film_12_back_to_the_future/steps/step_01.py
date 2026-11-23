import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set up render settings
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

# --- MATERIALS ---
def create_material(name, color, roughness=0.5, metallic=0.0, emission=0.0, emission_color=(1,1,1,1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission > 0:
        bsdf.inputs['Emission Strength'].default_value = emission
        bsdf.inputs['Emission Color'].default_value = emission_color
    return mat

# Materials
mat_concrete = create_material("Concrete", (0.35, 0.35, 0.33, 1), 0.8, 0.0)
mat_stone = create_material("Stone", (0.4, 0.38, 0.35, 1), 0.9, 0.0)
mat_metal = create_material("Metal", (0.6, 0.6, 0.65, 1), 0.3, 0.9)
mat_copper = create_material("Copper", (0.8, 0.4, 0.2, 1), 0.4, 0.8)
mat_glass = create_material("Glass", (0.8, 0.9, 1.0, 1), 0.1, 0.0, 0.0)
mat_road = create_material("Road", (0.15, 0.15, 0.15, 1), 0.9, 0.0)
mat_sand = create_material("Sand", (0.7, 0.65, 0.5, 1), 1.0, 0.0)
mat_fire = create_material("Fire", (1.0, 0.3, 0.0, 1), 0.5, 0.0, 5.0, (1.0, 0.3, 0.0, 1))
mat_lightning = create_material("Lightning", (0.7, 0.8, 1.0, 1), 0.1, 0.0, 15.0, (0.7, 0.8, 1.0, 1))
mat_dealorian_body = create_material("DeLorean Body", (0.7, 0.72, 0.75, 1), 0.2, 0.9)
mat_dealorian_glass = create_material("DeLorean Glass", (0.1, 0.15, 0.2, 1), 0.1, 0.0)
mat_tire = create_material("Tire", (0.05, 0.05, 0.05, 1), 0.9, 0.0)
mat_sky = create_material("Sky", (0.05, 0.05, 0.1, 1), 0.5, 0.0)
mat_cloud = create_material("Cloud", (0.3, 0.3, 0.35, 1), 1.0, 0.0, 0.5, (0.2, 0.2, 0.25, 1))
mat_grass = create_material("Grass", (0.2, 0.4, 0.1, 1), 0.9, 0.0)
mat_building1 = create_material("Building1", (0.5, 0.45, 0.4, 1), 0.8, 0.0)
mat_building2 = create_material("Building2", (0.4, 0.4, 0.45, 1), 0.8, 0.0)
mat_building3 = create_material("Building3", (0.45, 0.42, 0.38, 1), 0.8, 0.0)
mat_window = create_material("Window", (0.1, 0.1, 0.15, 1), 0.3, 0.0)
mat_window_lit = create_material("Window Lit", (1.0, 0.8, 0.4, 1), 0.3, 0.0, 2.0, (1.0, 0.8, 0.4, 1))
mat_cable = create_material("Cable", (0.1, 0.1, 0.1, 1), 0.5, 0.8)
mat_wood = create_material("Wood", (0.5, 0.3, 0.15, 1), 0.8, 0.0)
mat_spark = create_material("Spark", (1.0, 0.5, 0.1, 1), 0.1, 0.0, 10.0, (1.0, 0.5, 0.1, 1))
mat_smoke = create_material("Smoke", (0.3, 0.3, 0.3, 1), 1.0, 0.0, 0.1, (0.3, 0.3, 0.3, 1))
mat_pole = create_material("Pole", (0.2, 0.2, 0.2, 1), 0.6, 0.5)
mat_sign = create_material("Sign", (0.8, 0.1, 0.1, 1), 0.5, 0.0)
mat_floodlight = create_material("Floodlight", (1.0, 0.9, 0.7, 1), 0.1, 0.0, 8.0, (1.0, 0.9, 0.7, 1))
mat_bolt_glow = create_material("Bolt Glow", (0.5, 0.6, 1.0, 1), 0.1, 0.0, 20.0, (0.5, 0.6, 1.0, 1))

# --- GROUND / STREET ---
# Main street (flat plane)
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
street = bpy.context.object
street.name = "Street"
street.data.materials.append(mat_road)

# Sidewalks
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -25, 0.1))
sw1 = bpy.context.object
sw1.scale = (50, 5, 0.2)
sw1.name = "Sidewalk Left"
sw1.data.materials.append(mat_concrete)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 25, 0.1))
sw2 = bpy.context.object
sw2.scale = (50, 5, 0.2)
sw2.name = "Sidewalk Right"
sw2.data.materials.append(mat_concrete)

# Crosswalk stripes
for i in range(-4, 5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(i*3, 0, 0.05))
    stripe = bpy.context.object
    stripe.scale = (1.5, 8, 0.02)
    stripe.name = f"Crosswalk {i}"
    mat_white = create_material(f"White{i}", (0.9, 0.9, 0.9, 1), 0.7, 0.0)
    stripe.data.materials.append(mat_white)

# --- CLOCK TOWER ---
# Base platform
bpy.ops.mesh.primitive_cylinder_add(radius=8, depth=2, location=(0, 0, 1))
tower_base = bpy.context.object
tower_base.name = "Tower Base"
tower_base.data.materials.append(mat_stone)

# Main tower shaft
bpy.ops.mesh.primitive_cylinder_add(radius=5, depth=30, location=(0, 0, 17))
tower_shaft = bpy.context.object
tower_shaft.name = "Tower Shaft"
tower_shaft.data.materials.append(mat_stone)

# Decorative bands on tower
for h in [5, 10, 15, 20, 25]:
    bpy.ops.mesh.primitive_cylinder_add(radius=5.2, depth=0.5, location=(0, 0, h))
    band = bpy.context.object
    band.name = f"Band {h}"
    band.data.materials.append(mat_concrete)

# Clock face (front)
bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=0.3, location=(0, 5.1, 22), rotation=(math.pi/2, 0, 0))
clock_face = bpy.context.object
clock_face.name = "Clock Face"
mat_clock = create_material("Clock Face", (0.9, 0.9, 0.85, 1), 0.3, 0.0)
clock_face.data.materials.append(mat_clock)

# Clock hands
# Hour hand
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5.2, 22.5))
hour_hand = bpy.context.object
hour_hand.scale = (0.15, 0.05, 1.2)
hour_hand.rotation_euler = (0, 0, math.radians(30))
hour_hand.name = "Hour Hand"
mat_black = create_material("Black", (0.05, 0.05, 0.05, 1), 0.5, 0.0)
hour_hand.data.materials.append(mat_black)

# Minute hand
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5.2, 22.5))
min_hand = bpy.context.object
min_hand.scale = (0.1, 0.05, 1.8)
min_hand.rotation_euler = (0, 0, math.radians(60))
min_hand.name = "Minute Hand"
min_hand.data.materials.append(mat_black)

# Clock center
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, location=(0, 5.2, 22), rotation=(math.pi/2, 0, 0))
clock_center = bpy.context.object
clock_center.name = "Clock Center"
clock_center.data.materials.append(mat_black)

# Clock face back (top of tower)
bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=0.3, location=(0, 0, 32.5), rotation=(0, 0, 0))
clock_top = bpy.context.object
clock_top.name = "Clock Top"
clock_top.data.materials.append(mat_clock)

# Tower cap / roof
bpy.ops.mesh.primitive_cone_add(radius1=5.5, radius2=0, depth=5, location=(0, 0, 35))
tower_roof = bpy.context.object
tower_roof.name = "Tower Roof"
mat_roof = create_material("Roof", (0.2, 0.2, 0.25, 1), 0.6, 0.5)
tower_roof.data.materials.append(mat_roof)

# Spire on top
bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0, depth=3, location=(0, 0, 38.5))
spire = bpy.context.object
spire.name = "Spire"
spire.data.materials.append(mat_metal)

# Lightning rod at very top
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2, location=(0, 0, 40.5))
lightning_rod = bpy.context.object
lightning_rod.name = "Lightning Rod"
lightning_rod.data.materials.append(mat_copper)

# Arched windows on tower
for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
    for h in [8, 14, 20]:
        x = 5.1 * math.cos(angle)
        y = 5.1 * math.sin(angle)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h))
        win = bpy.context.object
        win.scale = (0.8, 0.15, 1.5)
        win.rotation_euler = (0, 0, angle)
        win.name = f"Window {angle:.1f} {h}"
        win.data.materials.append(mat_window)

# Door at base
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5.1, 1.5))
door = bpy.context.object
door.scale = (1.5, 0.1, 2.5)
door.name = "Tower Door"
mat_door = create_material("Door", (0.3, 0.15, 0.05, 1), 0.7, 0.0)
door.data.materials.append(mat_door)

# --- LIGHTNING BOLT ---
# Create a jagged lightning bolt from sky to tower top
import bmesh

def create_lightning_bolt(start, end, segments=15, spread=3.0, name="Lightning"):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    points = []
    for i in range(segments + 1):
        t = i / segments
        base = start.lerp(end, t)
        # Add randomness perpendicular to the line
        if 0 < i < segments:
            offset = Vector((
                random.uniform(-spread, spread) * (1 - t*0.5),
                random.uniform(-spread, spread) * (1 - t*0.5),
                random.uniform(-spread*0.3, spread*0.3)
            ))
            base += offset
        points.append(base)
    
    # Create a tube along the points
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i+1]
        direction = (p2 - p1).normalized()
        # Create cross-section
        up = Vector((0, 0, 1))
        if abs(direction.dot(up)) > 0.9:
            up = Vector((1, 0, 0))
        side = direction.cross(up).normalized()
        up2 = direction.cross(side).normalized()
        
        r1 = 0.3
        r2 = 0.2
        v1 = bm.verts.new(p1 + side * r1)
        v2 = bm.verts.new(p1 - side * r1)
        v3 = bm.verts.new(p1 + up2 * r1)
        v4 = bm.verts.new(p1 - up2 * r1)
        
        v5 = bm.verts.new(p2 + side * r2)
        v6 = bm.verts.new(p2 - side * r2)
        v7 = bm.verts.new(p2 + up2 * r2)
        v8 = bm.verts.new(p2 - up2 * r2)
        
        bm.faces.new([v1, v2, v6, v5])
        bm.faces.new([v2, v4, v8, v6])
        bm.faces.new([v4, v3, v7, v8])
        bm.faces.new([v3, v1, v5, v7])
    
    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat_lightning)
    return obj

# Main lightning bolt
bolt_start = Vector((5, -10, 60))
bolt_end = Vector((0, 0, 40))
lightning = create_lightning_bolt(bolt_start, bolt_end, segments=20, spread=4.0, name="Lightning Bolt")

# Branch bolts
for _ in range(3):
    branch_start = Vector((random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(35, 45)))
    branch_end = Vector((random.uniform(-8, 8), random.uniform(-8, 8), random.uniform(20, 30)))
    create_lightning_bolt(branch_start, branch_end, segments=8, spread=2.0, name="Lightning Branch")

# Glow sphere at impact point
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 40), segments=16, ring_count=8)
impact_glow = bpy.context.object
impact_glow.name = "Impact Glow"
impact_glow.data.materials.append(mat_bolt_glow)

# --- CABLE STRUNG ACROSS STREET ---
# Cable from tower to a pole on the other side
# Pole on left side of street
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=12, location=(-20, 0, 6))
pole = bpy.context.object
pole.name = "Cable Pole"
pole.data.materials.append(mat_pole)

# Cross arm on pole
bpy.ops.mesh.primitive_cube_add(size=1, location=(-20, 0, 11))
cross_arm = bpy.context.object
cross_arm.scale = (0.1, 3, 0.1)
cross_arm.name = "Cross Arm"
cross_arm.data.materials.append(mat_wood)

# Cable from tower top to pole
# Use a curve for the cable
curve_data = bpy.data.curves.new("CableCurve", 'CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.08
curve_data.bevel_resolution = 4

spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(2)  # 3 points total

# Tower attachment point
spline.bezier_points[0].co = Vector((0, 0, 38))
spline.bezier_points[0].handle_left = Vector((0, 0, 40))
spline.bezier_points[0].handle_right = Vector((-5, 0, 37))

# Midpoint (sag)
spline.bezier_points[1].co = Vector((-10, 0, 25))
spline.bezier_points[1].handle_left = Vector((-5, 0, 32))
spline.bezier_points[1].handle_right = Vector((-15, 0, 22))

# Pole attachment
spline.bezier_points[2].co = Vector((-20, 0, 11))
spline.bezier_points[2].handle_left = Vector((-15, 0, 18))
spline.bezier_points[2].handle_right = Vector((-20, 0, 10))

cable_obj = bpy.data.objects.new("Cable", curve_data)
bpy.context.collection.objects.link(cable_obj)
cable_obj.data.materials.append(mat_cable)

# Second cable (parallel, slightly different sag)
curve_data2 = bpy.data.curves.new("CableCurve2", 'CURVE')
curve_data2.dimensions = '3D'
curve_data2.bevel_depth = 0.06
curve_data2.bevel_resolution = 4

spline2 = curve_data2.splines.new('BEZIER')
spline2.bezier_points.add(2)

spline2.bezier_points[0].co = Vector((0.5, 0.5, 37))
spline2.bezier_points[0].handle_left = Vector((0.5, 0.5, 39))
spline2.bezier_points[0].handle_right = Vector((-4.5, 0.5, 36))

spline2.bezier_points[1].co = Vector((-10, 0.5, 24))
spline2.bezier_points[1].handle_left = Vector((-5, 0.5, 31))
spline2.bezier_points[1].handle_right = Vector((-15, 0.5, 21))

spline2.bezier_points[2].co = Vector((-20, 0.5, 10.5))
spline2.bezier_points[2].handle_left = Vector((-15, 0.5, 17))
spline2.bezier_points[2].handle_right = Vector((-20, 0.5, 9.5))

cable_obj2 = bpy.data.objects.new("Cable2", curve_data2)
bpy.context.collection.objects.link(cable_obj2)
cable_obj2.data.materials.append(mat_cable)

# --- DELOREAN ---
# Position: racing towards the tower, on the right side of street
dealorian_loc = Vector((15, 15, 0.5))

# Body (main chassis)
bpy.ops.mesh.primitive_cube_add(size=1, location=dealorian_loc)
body = bpy.context.object
body.name = "DeLorean Body"
body.scale = (2.5, 4.5, 0.8)
body.data.materials.append(mat_dealorian_body)

# Hood (front)
bpy.ops.mesh.primitive_cube_add(size=1, location=(dealorian_loc.x + 1.5, dealorian_loc.y, dealorian_loc.z + 0.2))
hood = bpy.context.object
hood.name = "DeLorean Hood"
hood.scale = (1.5, 4.3, 0.4)
hood.data.materials.append(mat_dealorian_body)

# Trunk (back)
bpy.ops.mesh.primitive_cube_add(size=1, location=(dealorian_loc.x - 1.5, dealorian_loc.y, dealorian_loc.z + 0.2))
trunk = bpy.context.object
trunk.name = "DeLorean Trunk"
trunk.scale = (1.5, 4.3, 0.4)
trunk.data.materials.append(mat_dealorian_body)

# Cabin / roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(dealorian_loc.x - 0.5, dealorian_loc.y, dealorian_loc.z + 1.0))
cabin = bpy.context.object
cabin.name = "DeLorean Cabin"
cabin.scale = (1.5, 4.0, 0.5)
cabin.data.materials.append(mat_dealorian_body)

# Windshield (angled)
bpy.ops.mesh.primitive_cube_add(size=1, location=(dealorian_loc.x + 0.8, dealorian_loc.y, dealorian_loc.z + 0.9))
windshield = bpy.context.object
windshield.name = "DeLorean Windshield"
windshield.scale = (0.3, 3.8, 0.6)
windshield.rotation_euler = (0, math.radians(-15), 0)
windshield.data.materials.append(mat_dealorian_glass)

# Rear window
bpy.ops.mesh.primitive_cube_add(size=1, location=(dealorian_loc.x - 1.5, dealorian_loc.y, dealorian_loc.z + 0.9))
rear_window = bpy.context.object
rear_window.name = "DeLorean Rear Window"
rear_window.scale = (0.2, 3.8, 0.5)
rear_window.rotation_euler = (0, math.radians(15), 0)
rear_window.data.materials.append(mat_dealorian_glass)

# Side windows
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(dealorian_loc.x - 0.5, dealorian_loc.y + side * 2.0, dealorian_loc.z + 0.8))
    side_win = bpy.context.object
    side_win.name = f"DeLorean Side Window {side}"
    side_win.scale = (1.2, 0.1, 0.5)
    side_win.data.materials.append(mat_dealorian_glass)

# Gullwing doors (open, angled up)
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(dealorian_loc.x, dealorian_loc.y + side * 2.3, dealorian_loc.z + 1.5))
    door_obj = bpy.context.object
    door_obj.name = f"DeLorean Door {side}"
    door_obj.scale = (1.8, 0.1, 1.2)
    door_obj.rotation_euler = (0, 0, math.radians(side * 60))
    door_obj.data.materials.append(mat_dealorian_body)

# Wheels
wheel_positions = [
    (dealorian_loc.x + 1.5, dealorian_loc.y + 2.0, dealorian_loc.z - 0.3),
    (dealorian_loc.x + 1.5, dealorian_loc.y - 2.0, dealorian_loc.z - 0.3),
    (dealorian_loc.x - 1.5, dealorian_loc.y + 2.0, dealorian_loc.z - 0.3),
    (dealorian_loc.x - 1.5, dealorian_loc.y - 2.0, dealorian_loc.z - 0.3),
]
for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.3, location=pos, rotation=(0, math.pi/2, 0))
    wheel = bpy.context.object
    wheel.name = f"DeLorean Wheel {i}"
    wheel.data.materials.append(mat_tire)
    # Hub
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.35, location=pos, rotation=(0, math.pi/2, 0))
    hub = bpy.context.object
    hub.name = f"DeLorean Hub {i}"
    hub.data.materials.append(mat_metal)

# Headlights
for side in [-1, 1]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(dealorian_loc.x + 2.5, dealorian_loc.y + side * 1.5, dealorian_loc.z + 0.3))
    hl = bpy.context.object
    hl.name = f"DeLorean Headlight {side}"
    mat_headlight = create_material(f"Headlight{side}", (1.0, 1.0, 0.8, 1), 0.1, 0.0, 5.0, (1.0, 1.0, 0.8, 1))
    hl.data.materials.append(mat_headlight)

# Taillights
for side in [-1, 1]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(dealorian_loc.x - 2.5, dealorian_loc.y + side * 1.5, dealorian_loc.z + 0.3))
    tl = bpy.context.object
    tl.name = f"DeLorean Taillight {side}"
    mat_taillight = create_material(f"Taillight{side}", (1.0, 0.1, 0.1, 1), 0.1, 0.0, 3.0, (1.0, 0.1, 0.1, 1))
    tl.data.materials.append(mat_taillight)

# --- FIRE TRAILS BEHIND DELOREAN ---
# Create fire trail particles / mesh strips behind the car
trail_start_x = dealorian_loc.x - 3
trail_end_x = dealorian_loc.x - 25
trail_y = dealorian_loc.y
trail_z = dealorian_loc.z - 0.2

# Main fire trail (elongated)
bpy.ops.mesh.primitive_cube_add(size=1, location=((trail_start_x + trail_end_x)/2, trail_y, trail_z))
fire_trail = bpy.context.object
fire_trail.name = "Fire Trail"
fire_trail.scale = ((trail_start_x - trail_end_x)/2, 1.5, 0.3)
fire_trail.data.materials.append(mat_fire)

# Secondary fire trail (wider, lower)
bpy.ops.mesh.primitive_cube_add(size=1, location=((trail_start_x + trail_end_x)/2, trail_y, trail_z - 0.1))
fire_trail2 = bpy.context.object
fire_trail2.name = "Fire Trail 2"
fire_trail2.scale = ((trail_start_x - trail_end_x)/2 * 0.8, 2.0, 0.2)
fire_trail2.data.materials.append(mat_fire)

# Spark particles along the trail
for i in range(30):
    t = i / 29
    x = trail_start_x + (trail_end_x - trail_start_x) * t
    y = trail_y + random.uniform(-1.5, 1.5)
    z = trail_z + random.uniform(-0.2, 0.5)
    size = random.uniform(0.05, 0.15) * (1 - t * 0.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=(x, y, z))
    spark = bpy.context.object
    spark.name = f"Spark {i}"
    spark.data.materials.append(mat_spark)

# Smoke puffs
for i in range(15):
    t = i / 14
    x = trail_start_x + (trail_end_x - trail_start_x) * t * 0.7
    y = trail_y + random.uniform(-1, 1)
    z = trail_z + random.uniform(0.5, 2.0)
    size = random.uniform(0.3, 0.8) * (1 + t)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=(x, y, z))
    smoke = bpy.context.object
    smoke.name = f"Smoke {i}"
    smoke.data.materials.append(mat_smoke)

# --- BUILDINGS ALONG THE STREET ---
# Left side buildings
building_specs_left = [
    (-15, -30, 8, 10, 15, mat_building1),
    (-25, -30, 10, 12, 20, mat_building2),
    (-35, -30, 8, 10, 12, mat_building3),
    (-45, -30, 12, 14, 18, mat_building1),
]
for x, y, w, d, h, mat in building_specs_left:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h/2))
    bldg = bpy.context.object
    bldg.name = f"Building L {x}"
    bldg.scale = (w/2, d/2, h/2)
    bldg.data.materials.append(mat)
    # Windows
    for wy in range(2, int(h), 3):
        for wx in range(-int(w/2)+2, int(w/2)-1, 3):
            if random.random() > 0.3:
                bpy.ops.mesh.primitive_cube_add(size=1, location=(x + wx, y + d/2 + 0.1, wy))
                win = bpy.context.object
                win.name = f"Win L {x} {wx} {wy}"
                win.scale = (1, 0.1, 1.2)
                win_mat = mat_window_lit if random.random() > 0.5 else mat_window
                win.data.materials.append(win_mat)

# Right side buildings
building_specs_right = [
    (15, 30, 8, 10, 14, mat_building2),
    (25, 30, 10, 12, 18, mat_building3),
    (35, 30, 8, 10, 12, mat_building1),
    (45, 30, 12, 14, 22, mat_building2),
]
for x, y, w, d, h, mat in building_specs_right:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h/2))
    bldg = bpy.context.object
    bldg.name = f"Building R {x}"
    bldg.scale = (w/2, d/2, h/2)
    bldg.data.materials.append(mat)
    # Windows
    for wy in range(2, int(h), 3):
        for wx in range(-int(w/2)+2, int(w/2)-1, 3):
            if random.random() > 0.3:
                bpy.ops.mesh.primitive_cube_add(size=1, location=(x + wx, y - d/2 - 0.1, wy))
                win = bpy.context.object
                win.name = f"Win R {x} {wx} {wy}"
                win.scale = (1, 0.1, 1.2)
                win_mat = mat_window_lit if random.random() > 0.5 else mat_window
                win.data.materials.append(win_mat)

# --- STREET LIGHTS ---
for lx in [-10, 0, 10, 20]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=8, location=(lx, -22, 4))
    light_pole = bpy.context.object
    light_pole.name = f"Street Light Pole {lx}"
    light_pole.data.materials.append(mat_pole)
    # Lamp
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(lx, -22, 8.2))
    lamp = bpy.context.object
    lamp.name = f"Street Light Lamp {lx}"
    mat_street_light = create_material(f"StreetLight{lx}", (1.0, 0.9, 0.6, 1), 0.1, 0.0, 3.0, (1.0, 0.9, 0.6, 1))
    lamp.data.materials.append(mat_street_light)

# --- CLOUDS / SKY ---
# Dark storm clouds
for i in range(20):
    x = random.uniform(-50, 50)
    y = random.uniform(-50, 50)
    z = random.uniform(50, 70)
    size = random.uniform(5, 12)
    bpy.ops.mesh.primitive_uv_sphere_add