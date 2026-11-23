import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Materials
def make_mat(name, color, roughness=0.5, metallic=0.0, specular=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Specular IOR Level"].default_value = specular
    return mat

mat_copper = make_mat("Copper", (0.72, 0.35, 0.15), 0.25, 1.0, 0.8)
mat_dark_copper = make_mat("DarkCopper", (0.45, 0.20, 0.08), 0.35, 1.0, 0.6)
mat_charcoal = make_mat("Charcoal", (0.05, 0.05, 0.05), 0.9, 0.0, 0.2)
mat_wood = make_mat("Wood", (0.35, 0.20, 0.10), 0.7, 0.0, 0.3)
mat_stone = make_mat("Stone", (0.4, 0.38, 0.35), 0.8, 0.0, 0.2)
mat_floor = make_mat("Floor", (0.3, 0.28, 0.25), 0.9, 0.0, 0.1)
mat_lamp_metal = make_mat("LampMetal", (0.5, 0.3, 0.1), 0.4, 1.0, 0.7)
mat_glass = make_mat("LampGlass", (1.0, 0.8, 0.4), 0.1, 0.0, 1.0)
mat_glass.blend_method = 'BLEND'
mat_glass.shadow_method = 'NONE'

# Floor
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
floor = bpy.context.active_object
floor.data.materials.append(mat_floor)
floor.name = "Floor"

# Walls (simple back and left)
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, -4, 4))
back_wall = bpy.context.active_object
back_wall.rotation_euler = (math.radians(90), 0, 0)
back_wall.data.materials.append(mat_stone)
back_wall.name = "BackWall"

bpy.ops.mesh.primitive_plane_add(size=8, location=(-4, 0, 4))
left_wall = bpy.context.active_object
left_wall.rotation_euler = (0, math.radians(90), 0)
left_wall.data.materials.append(mat_stone)
left_wall.name = "LeftWall"

# Low anvil (stone base + copper top)
# Base
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, 0.5, 0.25))
anvil_base = bpy.context.active_object
anvil_base.scale = (0.8, 0.6, 0.25)
anvil_base.data.materials.append(mat_stone)
anvil_base.name = "AnvilBase"

# Anvil top (elongated)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, 0.5, 0.55))
anvil_top = bpy.context.active_object
anvil_top.scale = (0.7, 0.5, 0.1)
anvil_top.data.materials.append(mat_dark_copper)
anvil_top.name = "AnvilTop"

# Hammer on anvil
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.4, location=(1.3, 0.3, 0.68), rotation=(0, math.radians(90), 0))
hammer_handle = bpy.context.active_object
hammer_handle.data.materials.append(mat_wood)
hammer_handle.name = "HammerHandle"

bpy.ops.mesh.primitive_cube_add(size=1, location=(1.1, 0.3, 0.68))
hammer_head = bpy.context.active_object
hammer_head.scale = (0.15, 0.08, 0.06)
hammer_head.data.materials.append(mat_dark_copper)
hammer_head.name = "HammerHead"

# Hammered trays (several flat cylinders with slight variation)
tray_positions = [(-1.5, -1.0, 0.05), (-1.0, -1.5, 0.05), (-2.0, -0.5, 0.05), (-0.5, -0.8, 0.05)]
for i, pos in enumerate(tray_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3 + random.uniform(-0.05, 0.05), depth=0.02, location=pos)
    tray = bpy.context.active_object
    tray.data.materials.append(mat_copper)
    tray.name = f"Tray_{i}"
    # Slight tilt for realism
    tray.rotation_euler = (random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(0, math.pi*2))

# Charcoal pot (cylindrical pot with charcoal inside)
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.5, location=(-2.5, 1.5, 0.25))
charcoal_pot = bpy.context.active_object
charcoal_pot.data.materials.append(mat_stone)
charcoal_pot.name = "CharcoalPot"

# Charcoal inside (small dark spheres)
for i in range(8):
    angle = random.uniform(0, math.pi * 2)
    r = random.uniform(0, 0.2)
    x = -2.5 + r * math.cos(angle)
    y = 1.5 + r * math.sin(angle)
    z = 0.45 + random.uniform(0, 0.05)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(x, y, z))
    coal = bpy.context.active_object
    coal.data.materials.append(mat_charcoal)
    coal.name = f"Coal_{i}"

# Stacked bowls (3-4 bowls stacked)
stack_center = (2.5, -1.5, 0)
for i in range(4):
    z = stack_center[2] + i * 0.12
    radius = 0.25 - i * 0.02
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=0.1, location=(stack_center[0], stack_center[1], z))
    bowl = bpy.context.active_object
    bowl.data.materials.append(mat_copper)
    bowl.name = f"Bowl_{i}"
    # Hollow out top slightly by scaling top face (simplified: just add a darker inner disc)
    bpy.ops.mesh.primitive_cylinder_add(radius=radius * 0.8, depth=0.02, location=(stack_center[0], stack_center[1], z + 0.04))
    inner = bpy.context.active_object
    inner.data.materials.append(mat_dark_copper)
    inner.name = f"BowlInner_{i}"

# Hanging lamp (chain + lamp body + glass + light)
lamp_x, lamp_y, lamp_z = (0, 0, 3.5)
# Chain (small cylinders)
for i in range(5):
    z = lamp_z + 0.1 + i * 0.15
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.15, location=(lamp_x, lamp_y, z))
    link = bpy.context.active_object
    link.data.materials.append(mat_lamp_metal)
    link.name = f"ChainLink_{i}"

# Lamp body (cone/cylinder)
bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0.25, depth=0.3, location=(lamp_x, lamp_y, lamp_z - 0.1))
lamp_body = bpy.context.active_object
lamp_body.data.materials.append(mat_lamp_metal)
lamp_body.name = "LampBody"

# Glass shade
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(lamp_x, lamp_y, lamp_z - 0.05))
glass = bpy.context.active_object
glass.scale = (1, 1, 1.3)
glass.data.materials.append(mat_glass)
glass.name = "LampGlass"

# Point light inside lamp
light_data = bpy.data.lights.new("LampLight", type='POINT')
light_data.energy = 100
light_data.color = (1.0, 0.8, 0.5)
light_data.shadow_soft_size = 0.1
light_obj = bpy.data.objects.new("LampLight", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (lamp_x, lamp_y, lamp_z - 0.05)

# Sun light for ambient
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 2
sun_data.color = (1.0, 0.95, 0.9)
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(45), math.radians(20), 0)

# Camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0, 3, 1.5)
cam_obj.rotation_euler = (math.radians(75), 0, 0)
bpy.context.scene.camera = cam_obj

# World background
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.1, 0.08, 0.06, 1.0)
    bg_node.inputs[1].default_value = 1.0
