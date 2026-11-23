import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def mat(name, color, metallic=0.0, rough=0.5, alpha=1.0, emission=0.0, emit_col=(0,0,0,1)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if alpha < 1.0:
        m.blend_method = 'BLEND'
        m.show_transparent_back = False
        bsdf.inputs["Alpha"].default_value = alpha
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = emit_col
        bsdf.inputs["Emission Strength"].default_value = emission
    return m

mat_wood = mat("Wood", (0.25, 0.12, 0.05, 1), rough=0.6)
mat_darkwood = mat("DarkWood", (0.12, 0.06, 0.03, 1), rough=0.5)
mat_brass = mat("Brass", (0.85, 0.65, 0.2, 1), metallic=0.9, rough=0.3)
mat_glass = mat("Glass", (0.9, 0.95, 1.0, 1), alpha=0.15, rough=0.05)
mat_metal = mat("Metal", (0.7, 0.7, 0.72, 1), metallic=1.0, rough=0.25)
mat_silver = mat("Silver", (0.85, 0.85, 0.88, 1), metallic=1.0, rough=0.15)
mat_dial = mat("Dial", (0.95, 0.95, 0.9, 1), rough=0.4)
mat_black = mat("Black", (0.02, 0.02, 0.02, 1), rough=0.4)
mat_red = mat("Red", (0.7, 0.05, 0.05, 1), rough=0.4)
mat_bench = mat("Bench", (0.3, 0.18, 0.08, 1), rough=0.55)
mat_floor = mat("Floor", (0.18, 0.1, 0.05, 1), rough=0.7)
mat_wall = mat("Wall", (0.6, 0.55, 0.45, 1), rough=0.8)
mat_tray = mat("Tray", (0.1, 0.1, 0.12, 1), metallic=0.5, rough=0.3)
mat_screw = mat("Screw", (0.6, 0.6, 0.65, 1), metallic=1.0, rough=0.2)
mat_lamp_arm = mat("LampArm", (0.15, 0.15, 0.15, 1), metallic=0.8, rough=0.3)
mat_lamp_head = mat("LampHead", (0.1, 0.1, 0.1, 1), metallic=0.7, rough=0.3)
mat_lens = mat("Lens", (0.7, 0.8, 0.9, 1), alpha=0.3, rough=0.05)
mat_clock_face = mat("ClockFace", (0.95, 0.93, 0.85, 1), rough=0.3)
mat_clock_hand = mat("ClockHand", (0.05, 0.05, 0.05, 1), metallic=0.5, rough=0.3)
mat_glow = mat("Glow", (1.0, 0.9, 0.6, 1), emission=5.0, emit_col=(1.0, 0.9, 0.6, 1))

# Floor
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
bpy.context.object.data.materials.append(mat_floor)

# Walls
for loc, rot in [((0, -6, 3), (0, 0, 0)), ((-6, 0, 3), (0, math.pi/2, 0)), ((6, 0, 3), (0, -math.pi/2, 0))]:
    bpy.ops.mesh.primitive_plane_add(size=12, location=loc, rotation=rot)
    bpy.context.object.data.materials.append(mat_wall)

# Ceiling
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 6), rotation=(math.pi, 0, 0))
bpy.context.object.data.materials.append(mat_wall)

# --- Glass display cases (3) ---
def glass_case(x, y, watches=3):
    # Base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.3))
    bpy.context.object.scale = (0.8, 0.5, 0.3)
    bpy.context.object.data.materials.append(mat_darkwood)
    # Glass box
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.9))
    bpy.context.object.scale = (0.75, 0.45, 0.55)
    bpy.context.object.data.materials.append(mat_glass)
    # Shelves inside
    for h in [0.5, 0.8, 1.1]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h))
        bpy.context.object.scale = (0.7, 0.4, 0.02)
        bpy.context.object.data.materials.append(mat_brass)
    # Pocket watches
    for i in range(watches):
        wx = x - 0.25 + i * 0.25
        wy = y
        # Case
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.02, location=(wx, wy, 0.52))
        bpy.context.object.rotation_euler = (math.pi/2, 0, 0)
        bpy.context.object.data.materials.append(mat_brass)
        # Dial
        bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.005, location=(wx, wy - 0.011, 0.52))
        bpy.context.object.rotation_euler = (math.pi/2, 0, 0)
        bpy.context.object.data.materials.append(mat_dial)
        # Crown
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.02, location=(wx, wy, 0.61))
        bpy.context.object.data.materials.append(mat_brass)
        # Chain (simple curve)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.06, minor_radius=0.005, location=(wx, wy + 0.08, 0.52))
        bpy.context.object.rotation_euler = (0, math.pi/2, 0)
        bpy.context.object.data.materials.append(mat_brass)

glass_case(-3.5, -4, 3)
glass_case(-2.0, -4, 3)
glass_case(-0.5, -4, 3)

# --- Workbench with magnifying lamp ---
# Bench top
bpy.ops.mesh.primitive_cube_add(size=1, location=(2, -3, 0.9))
bpy.context.object.scale = (2.0, 1.2, 0.08)
bpy.context.object.data.materials.append(mat_bench)
# Legs
for lx, ly in [(1.1, -3.6), (2.9, -3.6), (1.1, -2.4), (2.9, -2.4)]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly, 0.45))
    bpy.context.object.scale = (0.08, 0.08, 0.9)
    bpy.context.object.data.materials.append(mat_darkwood)

# Magnifying lamp
# Base on bench
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.04, location=(2, -3, 0.96))
bpy.context.object.data.materials.append(mat_lamp_arm)
# Vertical arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.6, location=(2, -3, 1.28))
bpy.context.object.data.materials.append(mat_lamp_arm)
# Horizontal arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.5, location=(2.25, -3, 1.58), rotation=(0, math.pi/2, 0))
bpy.context.object.data.materials.append(mat_lamp_arm)
# Lamp head (cylinder pointing down)
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.15, location=(2.5, -3, 1.5))
bpy.context.object.data.materials.append(mat_lamp_head)
# Lens
bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.02, location=(2.5, -3, 1.42))
bpy.context.object.data.materials.append(mat_lens)
# Light source
bpy.ops.object.light_add(type='POINT', location=(2.5, -3, 1.45))
bpy.context.object.data.energy = 15
bpy.context.object.data.color = (1.0, 0.9, 0.7)
bpy.context.object.data.shadow_soft_size = 0.05

# --- Tray of tiny screws on bench ---
# Tray
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, -2.7, 0.96))
bpy.context.object.scale = (0.4, 0.3, 0.03)
bpy.context.object.data.materials.append(mat_tray)
# Screws (small cylinders)
random.seed(42)
for _ in range(30):
    sx = 1.5 + random.uniform(-0.15, 0.15)
    sy = -2.7 + random.uniform(-0.1, 0.1)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.025, location=(sx, sy, 0.985))
    bpy.context.object.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), 0)
    bpy.context.object.data.materials.append(mat_screw)

# --- Tall clock case in corner ---
cx, cy = -4.5, -4.5
# Body
bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, 1.8))
bpy.context.object.scale = (0.5, 0.5, 1.8)
bpy.context.object.data.materials.append(mat_darkwood)
# Top cap
bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, 3.3))
bpy.context.object.scale = (0.55, 0.55, 0.1)
bpy.context.object.data.materials.append(mat_brass)
# Clock face (front)
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.02, location=(cx, cy + 0.26, 2.5), rotation=(math.pi/2, 0, 0))
bpy.context.object.data.materials.append(mat_clock_face)
# Hour markers
for i in range(12):
    angle = i * math.pi / 6
    mx = cx + 0.16 * math.sin(angle)
    my = cy + 0.26
    mz = 2.5 + 0.16 * math.cos(angle)
    bpy.ops.mesh.primitive_cube_add(size=0.015, location=(mx, my, mz))
    bpy.context.object.rotation_euler = (0, 0, -angle)
    bpy.context.object.data.materials.append(mat_black)
# Hands
bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy + 0.27, 2.55))
bpy.context.object.scale = (0.01, 0.005, 0.12)
bpy.context.object.rotation_euler = (0, 0, math.pi/3)
bpy.context.object.data.materials.append(mat_clock_hand)
bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy + 0.27, 2.5))
bpy.context.object.scale = (0.008, 0.005, 0.16)
bpy.context.object.rotation_euler = (0, 0, -math.pi/6)
bpy.context.object.data.materials.append(mat_clock_hand)
# Pendulum window
bpy.ops.mesh.primitive_plane_add(size=0.2, location=(cx, cy + 0.26, 1.5), rotation=(math.pi/2, 0, 0))
bpy.context.object.data.materials.append(mat_glass)
# Pendulum
bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.5, location=(cx, cy + 0.24, 1.5))
bpy.context.object.data.materials.append(mat_brass)
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.02, location=(cx, cy + 0.24, 1.2))
bpy.context.object.data.materials.append(mat_brass)

# --- Additional pocket watches on bench ---
for i in range(2):
    px = 2.2 + i * 0.2
    py = -3.3
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.015, location=(px, py, 0.95))
    bpy.context.object.rotation_euler = (math.pi/2, 0, 0)
    bpy.context.object.data.materials.append(mat_silver)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.003, location=(px, py - 0.008, 0.95))
    bpy.context.object.rotation_euler = (math.pi/2, 0, 0)
    bpy.context.object.data.materials.append(mat_dial)

# --- Small tools on bench ---
# Screwdriver
bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.15, location=(1.8, -2.5, 0.955), rotation=(0, math.pi/2, 0))
bpy.context.object.data.materials.append(mat_metal)
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.05, location=(1.72, -2.5, 0.955), rotation=(0, math.pi/2, 0))
bpy.context.object.data.materials.append(mat_black)

# --- Ambient light ---
bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
bpy.context.object.data.energy = 2
bpy.context.object.rotation_euler = (math.pi/4, 0, math.pi/4)

# Camera
bpy.ops.object.camera_add(location=(0, 2, 2.5), rotation=(math.pi/3, 0, 0))
bpy.context.scene.camera = bpy.context.object
bpy.context.object.data.lens = 35
