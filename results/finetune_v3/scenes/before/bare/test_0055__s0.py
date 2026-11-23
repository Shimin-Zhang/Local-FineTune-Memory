import bpy
import math
import mathutils
import random
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- MATERIALS ---
def create_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

stone_mat = create_material("Stone", (0.35, 0.35, 0.38, 1.0), roughness=0.9)
gravel_mat = create_material("Gravel", (0.5, 0.48, 0.45, 1.0), roughness=0.95)
wood_mat = create_material("Wood", (0.35, 0.2, 0.1, 1.0), roughness=0.8)
leaves_mat = create_material("Leaves", (0.1, 0.3, 0.1, 1.0), roughness=0.8)
trunk_mat = create_material("Trunk", (0.25, 0.15, 0.08, 1.0), roughness=0.9)
ground_mat = create_material("Ground", (0.2, 0.3, 0.15, 1.0), roughness=0.95)

# --- GROUND ---
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.object
ground.data.materials.append(ground_mat)
ground.name = "Ground"

# --- PILLAR ---
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=8, location=(0, 0, 4))
pillar = bpy.context.object
pillar.data.materials.append(stone_mat)
pillar.name = "Pillar"

# Pillar top cap
bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=0.5, location=(0, 0, 8.25))
cap = bpy.context.object
cap.data.materials.append(stone_mat)
cap.name = "PillarCap"

# --- WOLF MOTHER (Stone) ---
def create_wolf(name, scale=1.0, location=(0,0,0), rotation=(0,0,0)):
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8 * scale, location=(location[0], location[1], location[2]))
    body = bpy.context.object
    body.scale = (1.5, 1.0, 1.0)
    body.data.materials.append(stone_mat)
    
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5 * scale, location=(location[0] + 1.2 * scale, location[1], location[2] + 0.3 * scale))
    head = bpy.context.object
    head.scale = (1.2, 0.8, 0.8)
    head.data.materials.append(stone_mat)
    
    # Snout
    bpy.ops.mesh.primitive_cone_add(radius1=0.3 * scale, radius2=0.1 * scale, depth=0.6 * scale, location=(location[0] + 1.8 * scale, location[1], location[2] + 0.2 * scale))
    snout = bpy.context.object
    snout.rotation_euler = (0, math.radians(90), 0)
    snout.data.materials.append(stone_mat)
    
    # Ears
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.15 * scale, radius2=0, depth=0.4 * scale, location=(location[0] + 1.0 * scale, location[1] + side * 0.3 * scale, location[2] + 0.7 * scale))
        ear = bpy.context.object
        ear.rotation_euler = (0, math.radians(-20 * side), 0)
        ear.data.materials.append(stone_mat)
    
    # Legs
    for i, (dx, dy) in enumerate([(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15 * scale, depth=0.8 * scale, location=(location[0] + dx * scale, location[1] + dy * scale, location[2] - 0.4 * scale))
        leg = bpy.context.object
        leg.data.materials.append(stone_mat)
    
    # Tail
    bpy.ops.mesh.primitive_cone_add(radius1=0.2 * scale, radius2=0.05 * scale, depth=0.8 * scale, location=(location[0] - 1.2 * scale, location[1], location[2] + 0.2 * scale))
    tail = bpy.context.object
    tail.rotation_euler = (0, math.radians(120), 0)
    tail.data.materials.append(stone_mat)
    
    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(body.name) or obj == body:
            pass
    
    # Select all new objects and join
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    head.select_set(True)
    snout.select_set(True)
    for obj in bpy.context.scene.objects:
        if obj.name not in [body.name, head.name, snout.name] and obj.type == 'MESH':
            if obj.location[0] < location[0] + 2.5 * scale and obj.location[0] > location[0] - 2.5 * scale:
                if obj != ground and obj != pillar and obj != cap:
                    obj.select_set(True)
    
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    body.name = name
    body.rotation_euler = rotation
    return body

# Mother wolf on pillar
mother = create_wolf("WolfMother", scale=1.0, location=(0, 0, 8.5), rotation=(0, 0, 0))

# --- CUBS ---
cub1 = create_wolf("Cub1", scale=0.5, location=(0.6, 0.4, 8.5), rotation=(0, 0, math.radians(30)))
cub2 = create_wolf("Cub2", scale=0.5, location=(0.6, -0.4, 8.5), rotation=(0, 0, math.radians(-30)))

# --- GRAVEL PATH ---
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 10, 0.01))
path = bpy.context.object
path.scale = (1.5, 10, 1)
path.data.materials.append(gravel_mat)
path.name = "GravelPath"

# --- BENCH ---
# Seat
bpy.ops.mesh.primitive_cube_add(size=1, location=(-3, 5, 0.5))
seat = bpy.context.object
seat.scale = (1.5, 0.5, 0.1)
seat.data.materials.append(wood_mat)
seat.name = "BenchSeat"

# Back
bpy.ops.mesh.primitive_cube_add(size=1, location=(-3, 4.7, 1.0))
back = bpy.context.object
back.scale = (1.5, 0.1, 0.5)
back.data.materials.append(wood_mat)
back.name = "BenchBack"

# Legs
for x in [-3.5, -2.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.5, location=(x, 5, 0.25))
    leg = bpy.context.object
    leg.data.materials.append(wood_mat)

# --- WOODEN SIGN ---
# Post
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2, location=(3, 5, 1))
post = bpy.context.object
post.data.materials.append(wood_mat)
post.name = "SignPost"

# Board
bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 5, 1.8))
board = bpy.context.object
board.scale = (1.0, 0.1, 0.5)
board.data.materials.append(wood_mat)
board.name = "SignBoard"

# --- FOREST TREES ---
random.seed(42)
for i in range(30):
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(15, 30)
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    
    # Avoid placing trees on path or near center
    if abs(x) < 3 and y > 0:
        continue
    
    # Trunk
    height = random.uniform(4, 8)
    bpy.ops.mesh.primitive_cylinder_add(radius=random.uniform(0.2, 0.4), depth=height, location=(x, y, height/2))
    trunk = bpy.context.object
    trunk.data.materials.append(trunk_mat)
    
    # Canopy
    canopy_size = random.uniform(2, 4)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=canopy_size, location=(x, y, height + canopy_size*0.5))
    canopy = bpy.context.object
    canopy.scale = (1, 1, 1.3)
    canopy.data.materials.append(leaves_mat)

# --- MORNING LIGHT (Sun) ---
bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
sun = bpy.context.object
sun.rotation_euler = (math.radians(45), math.radians(30), math.radians(0))
sun.data.energy = 3.0
sun.data.color = (1.0, 0.9, 0.7)  # Warm morning light
sun.name = "MorningSun"

# --- WORLD BACKGROUND ---
world = bpy.data.worlds.get("World")
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.7, 0.8, 1.0, 1.0)  # Light blue morning sky
    bg.inputs[1].default_value = 0.5

# --- CAMERA ---
bpy.ops.object.camera_add(location=(8, 12, 6))
camera = bpy.context.object
camera.rotation_euler = (math.radians(75), 0, math.radians(-15))
camera.data.lens = 50
bpy.context.scene.camera = camera

# --- RENDER SETTINGS ---
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
