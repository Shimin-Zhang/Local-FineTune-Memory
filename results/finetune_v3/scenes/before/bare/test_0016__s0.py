import bpy
import math
import mathutils
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
    for b in block:
        if b.users == 0:
            block.remove(b)

# --- Materials ---
def mat(name, color, metallic=0.0, roughness=0.5, emission=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    return m

mat_stone = mat("Stone", (0.75, 0.72, 0.65), 0.0, 0.8)
mat_dome = mat("Dome", (0.55, 0.5, 0.45), 0.1, 0.6)
mat_gold = mat("Gold", (0.85, 0.65, 0.2), 1.0, 0.3)
mat_clock_face = mat("ClockFace", (0.9, 0.88, 0.8), 0.0, 0.4)
mat_clock_hand = mat("ClockHand", (0.1, 0.1, 0.1), 0.0, 0.5)
mat_bulb = mat("Bulb", (1.0, 0.9, 0.6), 0.0, 0.3, emission=(1.0, 0.8, 0.4), emit_strength=3.0)
mat_wire = mat("Wire", (0.2, 0.2, 0.2), 0.0, 0.6)
mat_ground = mat("Ground", (0.3, 0.28, 0.25), 0.0, 0.9)
mat_night_sky = mat("NightSky", (0.02, 0.03, 0.08), 0.0, 1.0, emission=(0.02, 0.03, 0.08), emit_strength=1.0)
mat_nave_wall = mat("NaveWall", (0.7, 0.68, 0.62), 0.0, 0.85)
mat_window = mat("Window", (0.15, 0.1, 0.05), 0.0, 0.3, emission=(0.8, 0.6, 0.2), emit_strength=1.5)
mat_door = mat("Door", (0.35, 0.2, 0.1), 0.0, 0.7)
mat_bell = mat("Bell", (0.6, 0.5, 0.3), 0.8, 0.4)
mat_rib = mat("Rib", (0.5, 0.45, 0.4), 0.2, 0.5)

# --- Ground ---
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(mat_ground)

# --- Helper: create a box mesh ---
def add_box(name, size, location, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    if material:
        obj.data.materials.append(material)
    return obj

# --- Main Nave (rectangular body) ---
nave = add_box("Nave", (20, 10, 12), (0, 0, 6), mat_nave_wall)

# --- Transept (cross shape) ---
transept = add_box("Transept", (10, 20, 12), (0, 0, 6), mat_nave_wall)

# --- Dome Drum (cylinder under dome) ---
bpy.ops.mesh.primitive_cylinder_add(radius=6, depth=6, location=(0, 0, 15), vertices=32)
drum = bpy.context.object
drum.name = "DomeDrum"
drum.data.materials.append(mat_stone)

# --- Huge Ribbed Dome ---
# Create dome using UV sphere (top half)
bpy.ops.mesh.primitive_uv_sphere_add(radius=8, location=(0, 0, 18), segments=48, ring_count=24)
dome = bpy.context.object
dome.name = "Dome"
# Cut bottom half
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
# Use bmesh to delete bottom vertices
import bmesh
bm = bmesh.new()
bm.from_mesh(dome.data)
for v in bm.verts:
    v.select = v.co.z < 0
bmesh.update_loop_triangles(bm)
bm.to_mesh(dome.data)
bm.free()
dome.data.materials.append(mat_dome)

# --- Ribs on the dome ---
num_ribs = 16
for i in range(num_rib):
    angle = i * (2 * math.pi / num_ribs)
    # Create a thin elongated box along the dome surface
    rib_length = 10
    rib_width = 0.3
    rib_height = 0.5
    # Position rib at the dome surface
    r = 8.1
    # Start at drum top, go up and inward
    start = Vector((r * math.cos(angle), r * math.sin(angle), 18))
    end = Vector((0, 0, 26))
    mid = (start + end) / 2
    length = (end - start).length
    # Create a thin box oriented along the rib
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    rib = bpy.context.object
    rib.name = f"Rib_{i}"
    rib.scale = (rib_width/2, rib_height/2, length/2)
    # Orient rib along the direction from start to end
    direction = (end - start).normalized()
    rot = direction.to_track_quat('Z', 'Y').to_euler()
    rib.rotation_euler = rot
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    rib.data.materials.append(mat_rib)

# --- Lantern on top of dome ---
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3, location=(0, 0, 27), vertices=16)
lantern = bpy.context.object
lantern.name = "Lantern"
lantern.data.materials.append(mat_stone)

# Lantern top (small dome)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 28.5), segments=16, ring_count=8)
lantern_top = bpy.context.object
lantern_top.name = "LanternTop"
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
bm = bmesh.new()
bm.from_mesh(lantern_top.data)
for v in bm.verts:
    v.select = v.co.z < 0
bmesh.update_loop_triangles(bm)
bm.to_mesh(lantern_top.data)
bm.free()
lantern_top.data.materials.append(mat_gold)

# Cross on top
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2, location=(0, 0, 30.5), vertices=8)
cross_v = bpy.context.object
cross_v.name = "CrossVertical"
cross_v.data.materials.append(mat_gold)
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.2, location=(0, 0, 30.5), vertices=8)
cross_h = bpy.context.object
cross_h.name = "CrossHorizontal"
cross_h.rotation_euler = (0, math.radians(90), 0)
bpy.ops.object.transform_apply(rotation=True)
cross_h.data.materials.append(mat_gold)

# --- Bell Towers (two, flanking the front) ---
def create_bell_tower(name, x, y):
    # Base
    base = add_box(f"{name}_Base", (6, 6, 20), (x, y, 10), mat_stone)
    # Upper section
    upper = add_box(f"{name}_Upper", (5, 5, 8), (x, y, 24), mat_stone)
    # Belfry (open section with bells)
    belfry = add_box(f"{name}_Belfry", (4.5, 4.5, 4), (x, y, 30), mat_stone)
    # Bell
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, y, 30), segments=16, ring_count=8)
    bell = bpy.context.object
    bell.name = f"{name}_Bell"
    bell.scale = (1, 1, 1.3)
    bpy.ops.object.transform_apply(scale=True)
    bell.data.materials.append(mat_bell)
    # Clock face on front
    clock_y = y - 3.1  # front face
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.2, location=(x, clock_y, 24), vertices=32)
    clock = bpy.context.object
    clock.name = f"{name}_Clock"
    clock.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    clock.data.materials.append(mat_clock_face)
    # Clock hands
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, clock_y - 0.15, 24.5))
    hand_v = bpy.context.object
    hand_v.name = f"{name}_HandV"
    hand_v.scale = (0.08, 0.05, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    hand_v.data.materials.append(mat_clock_hand)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + 0.3, clock_y - 0.15, 24))
    hand_h = bpy.context.object
    hand_h.name = f"{name}_HandH"
    hand_h.scale = (0.6, 0.05, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    hand_h.data.materials.append(mat_clock_hand)
    # Clock face on side (right)
    clock_x = x + 3.1
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.2, location=(clock_x, y, 24), vertices=32)
    clock2 = bpy.context.object
    clock2.name = f"{name}_Clock2"
    clock2.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    clock2.data.materials.append(mat_clock_face)
    # Roof (pyramid)
    bpy.ops.mesh.primitive_cone_add(radius=3.5, depth=4, location=(x, y, 34), vertices=4)
    roof = bpy.context.object
    roof.name = f"{name}_Roof"
    roof.rotation_euler = (0, 0, math.radians(45))
    bpy.ops.object.transform_apply(rotation=True)
    roof.data.materials.append(mat_dome)
    return base

create_bell_tower("TowerL", -12, -8)
create_bell_tower("TowerR", 12, -8)

# --- Front Facade / Portico ---
facade = add_box("Facade", (14, 2, 14), (0, -7, 7), mat_stone)
# Columns
for i in range(-2, 3):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=12, location=(i*3, -7.5, 6), vertices=12)
    col = bpy.context.object
    col.name = f"Column_{i}"
    col.data.materials.append(mat_stone)

# --- Entrance Door ---
door = add_box("Door", (4, 0.5, 6), (0, -7.2, 3), mat_door)

# --- Windows on nave ---
for x in [-6, -3, 3, 6]:
    for y in [-4, 4]:
        w = add_box(f"Window_{x}_{y}", (1.5, 0.3, 3), (x, y, 8), mat_window)

# --- Festival Lights Across the Square ---
# Create strings of lights between points
def create_light_string(start, end, num_bulbs, sag=2.0):
    # Create wire as a curve
    curve_data = bpy.data.curves.new(f"Wire_{start}_{end}", 'CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(2)  # 3 points: start, middle (sagged), end
    mid = (Vector(start) + Vector(end)) / 2
    mid.z -= sag
    spline.bezier_points[0].co = Vector(start)
    spline.bezier_points[1].co = Vector(mid)
    spline.bezier_points[2].co = Vector(end)
    for bp in spline.bezier_points:
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    wire_obj = bpy.data.objects.new(f"Wire_{start[0]}_{start[1]}", curve_data)
    bpy.context.collection.objects.link(wire_obj)
    wire_obj.data.materials.append(mat_wire)
    wire_obj.data.bevel_depth = 0.03

    # Create bulbs along the curve
    for i in range(num_bulbs):
        t = i / (num_bulbs - 1) if num_bulbs > 1 else 0.5
        # Quadratic bezier interpolation
        p0 = Vector(start)
        p1 = Vector(mid)
        p2 = Vector(end)
        pos = (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2
        # Slight random offset for variety
        pos += Vector((random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=pos, segments=8, ring_count=4)
        bulb = bpy.context.object
        bulb.name = f"Bulb_{start[0]}_{i}"
        bulb.data.materials.append(mat_bulb)
        # Add a point light for each bulb (limit number for performance)
        if i % 2 == 0:  # Every other bulb gets a light
            light_data = bpy.data.lights.new(f"BulbLight_{start[0]}_{i}", 'POINT')
            light_data.energy = 5
            light_data.color = (1.0, 0.8, 0.4)
            light_data.shadow_soft_size = 0.2
            light_obj = bpy.data.objects.new(f"BulbLight_{start[0]}_{i}", light_data)
            light_obj.location = pos
            bpy.context.collection.objects.link(light_obj)

# Define points for light strings across the square
# Square is roughly in front of the church (negative Y direction)
# Towers are at (-12, -8) and (12, -8)
# Square extends from y=-15 to y=-35, x from -15 to 15

# String 1: Between the two towers
create_light_string((-12, -8, 25), (12, -8, 25), 20, sag=3.0)

# String 2: From left tower to left side of square
create_light_string((-12, -8, 25), (-15, -30, 15), 15, sag=4.0)

# String 3: From right tower to right side of square
create_light_string((12, -8, 25), (15, -30, 15), 15, sag=4.0)

# String 4: Across the square (left to right, middle)
create_light_string((-15, -20, 15), (15, -20, 15), 20, sag=3.0)

# String 5: Across the square (left to right, further)
create_light_string((-15, -30, 15), (15, -30, 1