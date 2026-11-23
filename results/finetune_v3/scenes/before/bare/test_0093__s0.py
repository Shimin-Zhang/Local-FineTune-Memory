import bpy
import math
import random

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
def mat(name, color, roughness=0.7, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metal
    return m

mat_wood      = mat("Wood",      (0.45, 0.30, 0.15))
mat_roof      = mat("Roof",      (0.35, 0.20, 0.10))
mat_floor     = mat("Floor",     (0.55, 0.40, 0.25))
mat_ground    = mat("Ground",    (0.55, 0.45, 0.20))
mat_door      = mat("Door",      (0.20, 0.10, 0.05))
mat_window    = mat("Window",    (0.70, 0.80, 0.90), roughness=0.1)
mat_pump      = mat("Pump",      (0.15, 0.15, 0.15), metal=0.8)
mat_pole      = mat("Pole",      (0.80, 0.80, 0.80), metal=0.6)
mat_flag      = mat("Flag",      (0.80, 0.10, 0.10))
mat_outhouse  = mat("Outhouse",  (0.30, 0.25, 0.20))
mat_bell      = mat("Bell",      (0.85, 0.70, 0.30), metal=0.9)
mat_sun       = mat("Sun",       (1.0, 0.95, 0.85), roughness=0.0)

# --- Ground ---
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(mat_ground)

# --- Schoolhouse ---
def box(name, sx, sy, sz, loc, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (sx/2, sy/2, sz/2)
    o.data.materials.append(material)
    return o

# Main room
room = box("Schoolhouse", 8, 6, 4, (0, 0, 2), mat_wood)

# Roof (triangular prism)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=5.5, radius2=0, depth=7, location=(0, 0, 4))
roof = bpy.context.object
roof.name = "Roof"
roof.rotation_euler = (0, math.radians(90), math.radians(45))
roof.scale = (1, 0.75, 1)
roof.data.materials.append(mat_roof)

# Door
door = box("Door", 1.2, 0.1, 2.2, (0, 3.05, 1.1), mat_door)

# Windows
for wx in (-2.5, 2.5):
    w = box(f"Window_{wx}", 1.0, 0.1, 1.0, (wx, 3.05, 2.5), mat_window)

# --- Bell on roof ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0, 0, 5.5))
bell = bpy.context.object
bell.name = "Bell"
bell.scale = (1, 1, 1.2)
bell.data.materials.append(mat_bell)

# Bell clapper
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=(0, 0, 5.2))
clapper = bpy.context.object
clapper.name = "BellClapper"
clapper.data.materials.append(mat_bell)

# --- Yard: Pump ---
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.2, location=(5, 5, 0.6))
pump_base = bpy.context.object
pump_base.name = "PumpBase"
pump_base.data.materials.append(mat_pump)

bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.8, location=(5, 5, 1.6))
pump_pole = bpy.context.object
pump_pole.name = "PumpPole"
pump_pole.data.materials.append(mat_pump)

bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.1, location=(5, 5, 2.05))
pump_top = bpy.context.object
pump_top.name = "PumpTop"
pump_top.data.materials.append(mat_pump)

# Handle
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.6, location=(5.3, 5, 2.1))
handle = bpy.context.object
handle.name = "PumpHandle"
handle.rotation_euler = (0, math.radians(45), 0)
handle.data.materials.append(mat_pump)

# --- Flagpole ---
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=6, location=(-5, 5, 3))
pole = bpy.context.object
pole.name = "Flagpole"
pole.data.materials.append(mat_pole)

# Flag
bpy.ops.mesh.primitive_plane_add(size=1, location=(-4.6, 5, 5.5))
flag = bpy.context.object
flag.name = "Flag"
flag.scale = (1.2, 0.8, 1)
flag.rotation_euler = (math.radians(90), 0, 0)
flag.data.materials.append(mat_flag)

# --- Two Outhouses ---
def outhouse(name, loc):
    o = box(name, 1.5, 1.5, 2.5, loc, mat_outhouse)
    # Small roof
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.3, radius2=0, depth=1, location=(loc[0], loc[1], loc[2]+1.5))
    r = bpy.context.object
    r.name = name + "_Roof"
    r.rotation_euler = (0, math.radians(90), math.radians(45))
    r.scale = (1, 1, 1)
    r.data.materials.append(mat_roof)
    return o

outhouse("Outhouse1", (-3, -5, 1.25))
outhouse("Outhouse2", (3, -5, 1.25))

# --- Lighting: Bright Autumn Day ---
# Sun
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.object
sun.name = "Sun"
sun.data.energy = 5.0
sun.data.color = (1.0, 0.95, 0.85)
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# World background (warm autumn sky)
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.85, 0.75, 0.55, 1.0)
bg.inputs["Strength"].default_value = 1.0

# Camera
bpy.ops.object.camera_add(location=(12, 12, 8), rotation=(math.radians(55), 0, math.radians(-45)))
cam = bpy.context.object
cam.name = "Camera"
bpy.context.scene.camera = cam
