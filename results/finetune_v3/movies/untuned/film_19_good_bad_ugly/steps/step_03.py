import bpy
import math
import random
from mathutils import Vector

# The scene has 383 objects. The sky node error stopped execution.
# Let's fix the sky, set up lighting, camera, and add more detail.

# Fix the world/sky - use a simple background color for dusty sky
world = bpy.data.worlds.get("World")
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Clear existing nodes
for node in nodes:
    nodes.remove(node)

# Create a simple dusty sky background
bg_node = nodes.new(type='ShaderNodeBackground')
bg_node.inputs[0].default_value = (0.65, 0.55, 0.4, 1.0)  # Dusty tan/orange sky
bg_node.inputs[1].default_value = 1.0

output_node = nodes.new(type='ShaderNodeOutputWorld')
links.new(bg_node.outputs[0], output_node.inputs[0])

# Add sun light
sun_exists = any(obj.type == 'LIGHT' for obj in bpy.data.objects)
if not sun_exists:
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
    sun = bpy.context.active_object
    sun.data.energy = 5
    sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(30), math.radians(20), 0)

# Add/fix camera
cam_exists = any(obj.type == 'CAMERA' for obj in bpy.data.objects)
if not cam_exists:
    bpy.ops.object.camera_add(location=(0, -18, 4))
    camera = bpy.context.active_object
    camera.data.lens = 45
    # Point at the center of the stone circle
    direction = Vector((0, 0, 1)) - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.camera = camera
else:
    # Use existing camera
    cams = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
    if cams:
        bpy.context.scene.camera = cams[0]

# Now let's add much more detail to the scene

# Get or create materials
def get_or_create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
    return mat

# Materials
stone_mat = get_or_create_material("Stone", (0.5, 0.48, 0.45, 1.0), roughness=0.9)
cemetery_stone_mat = get_or_create_material("CemeteryStone", (0.6, 0.58, 0.55, 1.0), roughness=0.85)
ground_mat = get_or_create_material("Ground", (0.4, 0.35, 0.25, 1.0), roughness=0.95)
dirt_mat = get_or_create_material("Dirt", (0.35, 0.3, 0.2, 1.0), roughness=0.95)
wood_mat = get_or_create_material("Wood", (0.3, 0.2, 0.1, 1.0), roughness=0.8)
metal_mat = get_or_create_material("Metal", (0.4, 0.4, 0.42, 1.0), roughness=0.3, metallic=0.8)
hat_mat = get_or_create_material("Hat", (0.2, 0.15, 0.1, 1.0), roughness=0.7)
coat_mat = get_or_create_material("Coat", (0.3, 0.25, 0.2, 1.0), roughness=0.7)
skin_mat = get_or_create_material("Skin", (0.8, 0.6, 0.5, 1.0), roughness=0.6)
pants_mat = get_or_create_material("Pants", (0.25, 0.2, 0.15, 1.0), roughness=0.7)
boot_mat = get_or_create_material("Boot", (0.15, 0.1, 0.08, 1.0), roughness=0.6)
hair_mat = get_or_create_material("Hair", (0.1, 0.08, 0.05, 1.0), roughness=0.8)
scarf_mat = get_or_create_material("Scarf", (0.5, 0.4, 0.3, 1.0), roughness=0.8)
grass_mat = get_or_create_material("Grass", (0.3, 0.4, 0.2, 1.0), roughness=0.9)
cross_mat = get_or_create_material("Cross", (0.5, 0.48, 0.45, 1.0), roughness=0.85)
horse_mat = get_or_create_material("Horse", (0.4, 0.3, 0.2, 1.0), roughness=0.7)

# Add more detailed headstones with varying shapes
for i in range(60):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(12, 45)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    if dist < 11:
        continue
    
    # Random shape: rectangular, rounded top, or cross-shaped
    shape_type = random.choice(['rect', 'rounded', 'cross'])
    
    if shape_type == 'rect':
        height = random.uniform(0.6, 1.2)
        width = random.uniform(0.3, 0.5)
        bpy.ops.mesh.primitive_cube_add(location=(x, y, height/2))
        hs = bpy.context.active_object
        hs.scale = (width/2, 0.1, height/2)
        hs.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
        hs.data.materials.append(cemetery_stone_mat)
        
    elif shape_type == 'rounded':
        height = random.uniform(0.5, 1.0)
        width = random.uniform(0.3, 0.5)
        # Base
        bpy.ops.mesh.primitive_cube_add(location=(x, y, height/2 - 0.1))
        base = bpy.context.active_object
        base.scale = (width/2, 0.1, (height - 0.2)/2)
        base.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
        base.data.materials.append(cemetery_stone_mat)
        # Rounded top
        bpy.ops.mesh.primitive_uv_sphere_add(radius=width/2, location=(x, y, height - 0.1))
        top = bpy.context.active_object
        top.scale = (1, 0.4, 0.5)
        top.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
        top.data.materials.append(cemetery_stone_mat)
        
    elif shape_type == 'cross':
        height = random.uniform(0.8, 1.5)
        # Vertical
        bpy.ops.mesh.primitive_cube_add(location=(x, y, height/2))
        vbar = bpy.context.active_object
        vbar.scale = (0.04, 0.04, height/2)
        vbar.data.materials.append(cross_mat)
        # Horizontal
        bpy.ops.mesh.primitive_cube_add(location=(x, y, height * 0.65))
        hbar = bpy.context.active_object
        hbar.scale = (0.15, 0.04, 0.04)
        hbar.data.materials.append(cross_mat)

# Add more scattered rocks
for i in range(50):
    x = random.uniform(-30, 30)
    y = random.uniform(-30, 30)
    if math.sqrt(x*x + y*y) < 10:
        continue
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.08, 0.35), 
        location=(x, y, 0.08))
    rock = bpy.context.active_object
    rock.scale = (random.uniform(0.7, 1.5), random.uniform(0.7, 1.5), random.uniform(0.4, 0.9))
    rock.data.materials.append(stone_mat)

# Add more grass tufts
for i in range(200):
    x = random.uniform(-35, 35)
    y = random.uniform(-35, 35)
    if math.sqrt(x*x + y*y) < 10:
        continue
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.04, radius2=0.005, depth=0.15, 
        location=(x, y, 0.075))
    grass = bpy.context.active_object
    grass.scale = (1, 1, random.uniform(0.6, 1.8))
    grass.data.materials.append(grass_mat)

# Add a dirt path leading to the stone circle from multiple directions
for i in range(30):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(9, 20)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    bpy.ops.mesh.primitive_plane_add(size=1.5, location=(x, y, 0.01))
    path_piece = bpy.context.active_object
    path_piece.scale = (1, 1, 1)
    path_piece.rotation_euler = (0, 0, angle)
    path_piece.data.materials.append(dirt_mat)

# Add more distant dead trees
for i in range(20):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(45, 70)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    # Trunk
    trunk_height = random.uniform(2, 4)
    bpy.ops.mesh.primitive_cylinder_add(radius=random.uniform(0.1, 0.2), 
        depth=trunk_height, location=(x, y, trunk_height/2))
    trunk = bpy.context.active_object
    trunk.data.materials.append(wood_mat)
    
    # Branches
    num_branches = random.randint(2, 5)
    for j in range(num_branches):
        branch_height = trunk_height * random.uniform(0.5, 0.9)
        branch_angle = random.uniform(0, 2 * math.pi)
        branch_len = random.uniform(0.5, 1.5)
        bx = x + branch_len * 0.5 * math.cos(branch_angle)
        by = y + branch_len * 0.5 * math.sin(branch_angle)
        bz = branch_height
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=branch_len, 
            location=(bx, by, bz))
        branch = bpy.context.active_object
        branch.rotation_euler = (
            random.uniform(-0.6, 0.6), 
            random.uniform(-0.6, 0.6), 
            0
        )
        branch.data.materials.append(wood_mat)

# Add a wagon with coffin (the funeral wagon from the movie)
wagon_x, wagon_y = 30, -25
# Wagon bed
bpy.ops.mesh.primitive_cube_add(location=(wagon_x, wagon_y, 0.7))
wagon_bed = bpy.context.active_object
wagon_bed.scale = (1.5, 1.0, 0.25)
wagon_bed.data.materials.append(wood_mat)

# Wagon sides
for sx in [-1.5, 1.5]:
    bpy.ops.mesh.primitive_cube_add(location=(wagon_x + sx, wagon_y, 1.0))
    side = bpy.context.active_object
    side.scale = (0.05, 1.0, 0.3)
    side.data.materials.append(wood_mat)

for sy in [-1.0, 1.0]:
    bpy.ops.mesh.primitive_cube_add(location=(wagon_x, wagon_y + sy, 1.0))
    side = bpy.context.active_object
    side.scale = (1.5, 0.05, 0.3)
    side.data.materials.append(wood_mat)

# Wagon wheels
for wx, wy in [(wagon_x - 1.3, wagon_y - 0.9), (wagon_x - 1.3, wagon_y + 0.9),
               (wagon_x + 1.3, wagon_y - 0.9), (wagon_x + 1.3, wagon_y + 0.9)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.06, 
        location=(wx, wy, 0.45))
    wheel = bpy.context.active_object
    wheel.rotation_euler = (math.radians(90), 0, 0)
    wheel.data.materials.append(wood_mat)
    # Spokes
    for spoke_angle in range(0, 360, 45):
        sa = math.radians(spoke_angle)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.8, 
            location=(wx, wy, 0.45))
        spoke = bpy.context.active_object
        spoke.rotation_euler = (math.radians(90), sa, 0)
        spoke.data.materials.append(wood_mat)

# Coffin on the wagon
bpy.ops.mesh.primitive_cube_add(location=(wagon_x, wagon_y, 1.1))
coffin = bpy.context.active_object
coffin.scale = (0.8, 0.3, 0.12)
coffin.data.materials.append(wood_mat)

# Add a second wagon
wagon2_x, wagon2_y = -28, 22
bpy.ops.mesh.primitive_cube_add(location=(wagon2_x, wagon2_y, 0.7))
wagon_bed2 = bpy.context.active_object
wagon_bed2.scale = (1.2, 0.8, 0.2)
wagon_bed2.data.materials.append(wood_mat)

for wx, wy in [(wagon2_x - 1.0, wagon2_y - 0.7), (wagon2_x - 1.0, wagon2_y + 0.7),
               (wagon2_x + 1.0, wagon2_y - 0.7), (wagon2_x + 1.0, wagon2_y + 0.7)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.05, 
        location=(wx, wy, 0.4))
    wheel = bpy.context.active_object
    wheel.rotation_euler = (math.radians(90), 0, 0)
    wheel.data.materials.append(wood_mat)

# Add more horses
for hx, hy in [(18, 12), (-15, -18), (22, -15)]:
    # Body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.0, location=(hx, hy, 0.7))
    hbody = bpy.context.active_object
    hbody.rotation_euler = (0, math.radians(90), 0)
    hbody.data.materials.append(horse_mat)
    
    # Head
    bpy.ops.mesh.primitive_cube_add(location=(hx + 0.6, hy, 1.0))
    hhead = bpy.context.active_object
    hhead.scale = (0.18, 0.12, 0.18)
    hhead.data.materials.append(horse_mat)
    
    # Neck
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.4, location=(hx + 0.4, hy, 0.9))
    hneck = bpy.context.active_object
    hneck.rotation_euler = (0, math.radians(30), 0)
    hneck.data.materials.append(horse_mat)
    
    # Legs
    for lx, ly in [(hx - 0.25, hy - 0.15), (hx - 0.25, hy + 0.15),
                   (hx + 0.25, hy - 0.15), (hx + 0.25, hy + 0.15)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.5, location=(lx, ly, 0.25))
        hleg = bpy.context.active_object
        hleg.data.materials.append(horse_mat)
    
    # Tail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.5, location=(hx - 0.5, hy, 0.8))
    htail = bpy.context.active_object
    htail.rotation_euler = (0, math.radians(20), 0)
    htail.data.materials.append(horse_mat)

# Add some fence posts in the distance
for i in range(10):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(35, 50)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.2, location=(x, y, 0.6))
    post = bpy.context.active_object
    post.data.materials.append(wood_mat)

# Add a broken fence section
fence_x, fence_y = 20, 30
for i in range(5):
    px = fence_x + i * 1.5
    py = fence_y + random.uniform(-0.2, 0.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=random.uniform(0.8, 1.2), 
        location=(px, py, 0.5))
    post = bpy.context.active_object
    post.rotation_euler = (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 0)
    post.data.materials.append(wood_mat)
    
    # Horizontal rails
    if i < 4:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.5, 
            location=(px + 0.75, py, 0.8))
        rail = bpy.context.active_object
        rail.rotation_euler = (0, math.radians(90), 0)
        rail.data.materials.append(wood_mat)

# Add some fallen headstones
for i in range(10):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(12, 30)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    if dist < 11:
        continue
    
    height = random.uniform(0.4, 0.7)
    width = random.uniform(0.25, 0.4)
    
    bpy.ops.mesh.primitive_cube_add(location=(x, y, 0.05))
    fallen = bpy.context.active_object
    fallen.scale = (width/2, 0.08, height/2)
    fallen.rotation_euler = (math.radians(85), 0, random.uniform(0, 2*math.pi))
    fallen.data.materials.append(cemetery_stone_mat)

# Set up render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.5

# Make sure camera is set and pointing at the action
if scene.camera:
    cam = scene.camera
    # Point at the center of the stone circle where the gunmen are
    target = Vector((0, 0, 1))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
else:
    bpy.ops.object.camera_add(location=(0, -18, 4))
    camera = bpy.context.active_object
    camera.data.lens = 45
    direction = Vector((0, 0, 1)) - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    scene.camera = camera

print("Scene refined with extensive details")
print("Total objects:", len(bpy.data.objects))
