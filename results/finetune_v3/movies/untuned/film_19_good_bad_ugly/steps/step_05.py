import bpy
import math
import random
from mathutils import Vector

# The scene looks washed out - the sky is too bright and the ground is too light.
# Let's fix the world lighting and add more contrast.

# Fix the world - make it a more dramatic dusty sky
world = bpy.data.worlds.get("World")
if world:
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    # Clear and rebuild
    for node in nodes:
        nodes.remove(node)
    
    # Create a gradient sky using a sky texture
    sky_node = nodes.new(type='ShaderNodeTexSky')
    sky_node.sky_type = 'PREETHAM'
    sky_node.sun_elevation = math.radians(35)
    sky_node.sun_rotation = math.radians(180)
    sky_node.sun_intensity = 0.5
    sky_node.altitude = 1000
    sky_node.air_density = 3.0
    sky_node.dust_density = 5.0  # Very dusty
    sky_node.ozone_density = 1.0
    
    bg_node = nodes.new(type='ShaderNodeBackground')
    bg_node.inputs[1].default_value = 0.3  # Reduce strength for darker, moodier look
    
    output_node = nodes.new(type='ShaderNodeOutputWorld')
    links.new(sky_node.outputs[0], bg_node.inputs[0])
    links.new(bg_node.outputs[0], output_node.inputs[0])

# Adjust the sun light - make it warmer and more dramatic
sun = None
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        sun = obj
        break

if sun:
    sun.data.energy = 3
    sun.data.color = (1.0, 0.85, 0.6)  # Warm, dusty light
    sun.rotation_euler = (math.radians(40), math.radians(10), 0)

# Get materials
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

# Darken the ground material
ground_mat = get_or_create_material("Ground", (0.25, 0.2, 0.15, 1.0), roughness=0.95)
dirt_mat = get_or_create_material("Dirt", (0.2, 0.17, 0.12, 1.0), roughness=0.95)
stone_mat = get_or_create_material("Stone", (0.4, 0.38, 0.35, 1.0), roughness=0.9)
cemetery_stone_mat = get_or_create_material("CemeteryStone", (0.45, 0.43, 0.4, 1.0), roughness=0.85)
wood_mat = get_or_create_material("Wood", (0.2, 0.13, 0.08, 1.0), roughness=0.8)
grass_mat = get_or_create_material("Grass", (0.2, 0.28, 0.12, 1.0), roughness=0.9)

# Update existing materials to be darker
for mat_name, new_color in [("Ground", (0.25, 0.2, 0.15, 1.0)), 
                              ("Dirt", (0.2, 0.17, 0.12, 1.0)),
                              ("Stone", (0.4, 0.38, 0.35, 1.0)),
                              ("CemeteryStone", (0.45, 0.43, 0.4, 1.0)),
                              ("Wood", (0.2, 0.13, 0.08, 1.0)),
                              ("Grass", (0.2, 0.28, 0.12, 1.0))]:
    mat = bpy.data.materials.get(mat_name)
    if mat:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = new_color

# Reposition the camera to better frame the action
scene = bpy.context.scene
cam = scene.camera
if cam:
    # Move camera closer and lower for a more dramatic angle
    cam.location = (0, -10, 2.5)
    cam.data.lens = 40
    # Point at the center where the gunmen are
    target = Vector((0, 0, 1.0))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

# Add more detail - a small mound of dirt in the center (where the coffin will be buried)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 0))
mound = bpy.context.active_object
mound.scale = (1, 1, 0.3)
mound.data.materials.append(dirt_mat)

# Add a small pile of dirt (freshly dug)
for i in range(20):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0.5, 2.0)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.1, 0.3), 
        location=(x, y, 0.1))
    dirt_pile = bpy.context.active_object
    dirt_pile.scale = (1, 1, 0.5)
    dirt_pile.data.materials.append(dirt_mat)

# Add a shovel stuck in the ground
shovel_x, shovel_y = 1.5, 1.5
# Handle
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.2, location=(shovel_x, shovel_y, 0.6))
handle = bpy.context.active_object
handle.rotation_euler = (0, math.radians(15), 0)
handle.data.materials.append(wood_mat)
# Blade
bpy.ops.mesh.primitive_cube_add(location=(shovel_x + 0.1, shovel_y, 0.05))
blade = bpy.context.active_object
blade.scale = (0.15, 0.08, 0.02)
blade.data.materials.append(get_or_create_material("Metal", (0.3, 0.3, 0.32, 1.0), roughness=0.3, metallic=0.8))

# Add more scattered bones (for the cemetery feel)
bone_mat = get_or_create_material("Bone", (0.85, 0.82, 0.75, 1.0), roughness=0.7)
for i in range(30):
    x = random.uniform(-12, 12)
    y = random.uniform(-12, 12)
    if math.sqrt(x*x + y*y) < 8:
        continue
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=random.uniform(0.1, 0.25), 
        location=(x, y, 0.02))
    bone = bpy.context.active_object
    bone.rotation_euler = (random.uniform(0, 0.5), random.uniform(0, 0.5), random.uniform(0, 2*math.pi))
    bone.data.materials.append(bone_mat)

# Add more rocks in the foreground
for i in range(40):
    x = random.uniform(-10, 10)
    y = random.uniform(-10, 5)
    if math.sqrt(x*x + y*y) < 8:
        continue
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.05, 0.2), 
        location=(x, y, 0.05))
    rock = bpy.context.active_object
    rock.scale = (random.uniform(0.7, 1.3), random.uniform(0.7, 1.3), random.uniform(0.4, 0.7))
    rock.data.materials.append(stone_mat)

# Add more grass in the foreground
for i in range(200):
    x = random.uniform(-12, 12)
    y = random.uniform(-12, 5)
    if math.sqrt(x*x + y*y) < 8:
        continue
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.025, radius2=0.002, depth=0.1, 
        location=(x, y, 0.05))
    grass = bpy.context.active_object
    grass.scale = (1, 1, random.uniform(0.5, 1.5))
    grass.data.materials.append(grass_mat)

# Add a few more headstones very close to the camera
for i in range(10):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(8, 12)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    if y > 0:  # Only in front of camera
        continue
    
    height = random.uniform(0.5, 0.9)
    width = random.uniform(0.25, 0.4)
    
    bpy.ops.mesh.primitive_cube_add(location=(x, y, height/2))
    hs = bpy.context.active_object
    hs.scale = (width/2, 0.07, height/2)
    hs.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
    hs.data.materials.append(cemetery_stone_mat)

# Add a small cairn of stones
cairn_x, cairn_y = -5, -3
for i in range(4):
    sz = 0.12 - i * 0.015
    bpy.ops.mesh.primitive_cube_add(location=(cairn_x, cairn_y, 0.04 + i * 0.1))
    cstone = bpy.context.active_object
    cstone.scale = (sz, sz * 0.8, 0.05)
    cstone.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
    cstone.data.materials.append(stone_mat)

# Add some distant hills/mountains for depth
hill_mat = get_or_create_material("Hill", (0.3, 0.25, 0.18, 1.0), roughness=0.95)
for i in range(5):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(80, 120)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(15, 30), location=(x, y, 0))
    hill = bpy.context.active_object
    hill.scale = (1, 1, random.uniform(0.3, 0.5))
    hill.data.materials.append(hill_mat)

# Adjust render settings for better mood
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.view_settings.look = 'AgX - High Contrast'
scene.view_settings.exposure = -0.3  # Slightly darker for mood

# Make sure camera is set
if scene.camera:
    cam = scene.camera
    cam.location = (0, -10, 2.5)
    cam.data.lens = 40
    target = Vector((0, 0, 1.0))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

print("Scene mood and detail enhanced")
print("Total objects:", len(bpy.data.objects))
