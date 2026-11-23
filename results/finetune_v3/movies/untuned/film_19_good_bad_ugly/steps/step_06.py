import bpy
import math
import random
from mathutils import Vector

# Fix the world - the PREETHAM sky node doesn't have dust_density.
# Let's use a simpler approach: a gradient background for a dusty sky.

world = bpy.data.worlds.get("World")
if world:
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    # Clear all nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create a simple dusty sky with a gradient
    # Use a color ramp with a sky texture
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.inputs['Rotation'].default_value = (0, math.radians(-90), 0)
    
    # Use a gradient based on the Z coordinate (elevation)
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    
    # Color ramp for dusty sky: dark at horizon, lighter at top
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = (0.4, 0.35, 0.25, 1.0)  # Dusty horizon
    color_ramp.color_ramp.elements[1].position = 1.0
    color_ramp.color_ramp.elements[1].color = (0.55, 0.45, 0.3, 1.0)  # Dusty sky
    
    # Add a middle stop for more dust
    elem_mid = color_ramp.color_ramp.elements.new(0.5)
    elem_mid.color = (0.48, 0.4, 0.28, 1.0)
    
    bg_node = nodes.new(type='ShaderNodeBackground')
    bg_node.inputs[1].default_value = 0.5
    
    output_node = nodes.new(type='ShaderNodeOutputWorld')
    
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], sep_xyz.inputs['Vector'])
    links.new(sep_xyz.outputs['Z'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bg_node.inputs['Color'])
    links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

# Fix the sun light
sun = None
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        sun = obj
        break

if sun:
    sun.data.energy = 4
    sun.data.color = (1.0, 0.8, 0.5)  # Warm, dusty light
    sun.data.angle = math.radians(3)
    sun.rotation_euler = (math.radians(45), math.radians(15), 0)

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

# Update materials to be darker and moodier
material_updates = {
    "Ground": (0.2, 0.17, 0.12, 1.0),
    "Dirt": (0.18, 0.15, 0.1, 1.0),
    "Stone": (0.35, 0.33, 0.3, 1.0),
    "CemeteryStone": (0.4, 0.38, 0.35, 1.0),
    "Wood": (0.18, 0.12, 0.07, 1.0),
    "Grass": (0.18, 0.25, 0.1, 1.0),
    "Coat": (0.25, 0.2, 0.15, 1.0),
    "Pants": (0.2, 0.17, 0.12, 1.0),
    "Hat": (0.15, 0.12, 0.08, 1.0),
}

for mat_name, new_color in material_updates.items():
    mat = bpy.data.materials.get(mat_name)
    if mat:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = new_color

# Reposition camera for a better view of the standoff
scene = bpy.context.scene
cam = scene.camera
if cam:
    # Camera at a slight angle, looking at the three gunmen
    cam.location = (3, -12, 3)
    cam.data.lens = 50
    # Point at the center of the stone circle
    target = Vector((0, 0, 1.0))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

# Add more detail to the scene

# Add a small dirt mound in the center (the burial spot)
dirt_mat = get_or_create_material("Dirt", (0.18, 0.15, 0.1, 1.0), roughness=0.95)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, 0))
mound = bpy.context.active_object
mound.scale = (1, 1, 0.25)
mound.data.materials.append(dirt_mat)

# Add a shovel
wood_mat = get_or_create_material("Wood", (0.18, 0.12, 0.07, 1.0), roughness=0.8)
metal_mat = get_or_create_material("Metal", (0.3, 0.3, 0.32, 1.0), roughness=0.3, metallic=0.8)

shovel_x, shovel_y = 2.0, 1.5
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=1.1, location=(shovel_x, shovel_y, 0.55))
handle = bpy.context.active_object
handle.rotation_euler = (0, math.radians(20), 0)
handle.data.materials.append(wood_mat)

bpy.ops.mesh.primitive_cube_add(location=(shovel_x + 0.12, shovel_y, 0.04))
blade = bpy.context.active_object
blade.scale = (0.14, 0.07, 0.015)
blade.data.materials.append(metal_mat)

# Add scattered bones
bone_mat = get_or_create_material("Bone", (0.8, 0.78, 0.7, 1.0), roughness=0.7)
for i in range(40):
    x = random.uniform(-15, 15)
    y = random.uniform(-15, 15)
    if math.sqrt(x*x + y*y) < 8:
        continue
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=random.uniform(0.08, 0.2), 
        location=(x, y, 0.015))
    bone = bpy.context.active_object
    bone.rotation_euler = (random.uniform(0, 0.4), random.uniform(0, 0.4), random.uniform(0, 2*math.pi))
    bone.data.materials.append(bone_mat)

# Add more rocks
stone_mat = get_or_create_material("Stone", (0.35, 0.33, 0.3, 1.0), roughness=0.9)
for i in range(50):
    x = random.uniform(-15, 15)
    y = random.uniform(-15, 15)
    if math.sqrt(x*x + y*y) < 8:
        continue
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.04, 0.18), 
        location=(x, y, 0.04))
    rock = bpy.context.active_object
    rock.scale = (random.uniform(0.6, 1.3), random.uniform(0.6, 1.3), random.uniform(0.3, 0.6))
    rock.data.materials.append(stone_mat)

# Add more grass
grass_mat = get_or_create_material("Grass", (0.18, 0.25, 0.1, 1.0), roughness=0.9)
for i in range(300):
    x = random.uniform(-20, 20)
    y = random.uniform(-20, 20)
    if math.sqrt(x*x + y*y) < 8:
        continue
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.02, radius2=0.002, depth=0.08, 
        location=(x, y, 0.04))
    grass = bpy.context.active_object
    grass.scale = (1, 1, random.uniform(0.5, 1.5))
    grass.data.materials.append(grass_mat)

# Add more headstones
cemetery_stone_mat = get_or_create_material("CemeteryStone", (0.4, 0.38, 0.35, 1.0), roughness=0.85)
cross_mat = get_or_create_material("Cross", (0.4, 0.38, 0.35, 1.0), roughness=0.85)

for i in range(50):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(10, 35)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    if dist < 10:
        continue
    
    shape_type = random.choice(['rect', 'rounded', 'cross'])
    
    if shape_type == 'rect':
        height = random.uniform(0.4, 0.9)
        width = random.uniform(0.22, 0.38)
        bpy.ops.mesh.primitive_cube_add(location=(x, y, height/2))
        hs = bpy.context.active_object
        hs.scale = (width/2, 0.06, height/2)
        hs.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
        hs.data.materials.append(cemetery_stone_mat)
        
    elif shape_type == 'rounded':
        height = random.uniform(0.4, 0.8)
        width = random.uniform(0.22, 0.35)
        bpy.ops.mesh.primitive_cube_add(location=(x, y, height/2 - 0.06))
        base = bpy.context.active_object
        base.scale = (width/2, 0.06, (height - 0.12)/2)
        base.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
        base.data.materials.append(cemetery_stone_mat)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=width/2, location=(x, y, height - 0.06))
        top = bpy.context.active_object
        top.scale = (1, 0.3, 0.4)
        top.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
        top.data.materials.append(cemetery_stone_mat)
        
    elif shape_type == 'cross':
        height = random.uniform(0.6, 1.1)
        bpy.ops.mesh.primitive_cube_add(location=(x, y, height/2))
        vbar = bpy.context.active_object
        vbar.scale = (0.03, 0.03, height/2)
        vbar.data.materials.append(cross_mat)
        bpy.ops.mesh.primitive_cube_add(location=(x, y, height * 0.6))
        hbar = bpy.context.active_object
        hbar.scale = (0.1, 0.03, 0.03)
        hbar.data.materials.append(cross_mat)

# Add distant hills
hill_mat = get_or_create_material("Hill", (0.25, 0.22, 0.15, 1.0), roughness=0.95)
for i in range(6):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(80, 130)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(12, 25), location=(x, y, 0))
    hill = bpy.context.active_object
    hill.scale = (1, 1, random.uniform(0.25, 0.4))
    hill.data.materials.append(hill_mat)

# Add a few more horses
horse_mat = get_or_create_material("Horse", (0.35, 0.25, 0.15, 1.0), roughness=0.7)
for hx, hy in [(10, 6), (-8, 12), (15, -10), (-15, -8)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.85, location=(hx, hy, 0.6))
    hbody = bpy.context.active_object
    hbody.rotation_euler = (0, math.radians(90), 0)
    hbody.data.materials.append(horse_mat)
    
    bpy.ops.mesh.primitive_cube_add(location=(hx + 0.5, hy, 0.9))
    hhead = bpy.context.active_object
    hhead.scale = (0.15, 0.1, 0.15)
    hhead.data.materials.append(horse_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.3, location=(hx + 0.32, hy, 0.8))
    hneck = bpy.context.active_object
    hneck.rotation_euler = (0, math.radians(35), 0)
    hneck.data.materials.append(horse_mat)
    
    for lx, ly in [(hx - 0.2, hy - 0.12), (hx - 0.2, hy + 0.12),
                   (hx + 0.2, hy - 0.12), (hx + 0.2, hy + 0.12)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.4, location=(lx, ly, 0.2))
        hleg = bpy.context.active_object
        hleg.data.materials.append(horse_mat)

# Add a wagon
wagon_x, wagon_y = 22, -18
bpy.ops.mesh.primitive_cube_add(location=(wagon_x, wagon_y, 0.65))
wagon_bed = bpy.context.active_object
wagon_bed.scale = (1.4, 0.9, 0.22)
wagon_bed.data.materials.append(wood_mat)

for wx, wy in [(wagon_x - 1.2, wagon_y - 0.8), (wagon_x - 1.2, wagon_y + 0.8),
               (wagon_x + 1.2, wagon_y - 0.8), (wagon_x + 1.2, wagon_y + 0.8)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.05, 
        location=(wx, wy, 0.42))
    wheel = bpy.context.active_object
    wheel.rotation_euler = (math.radians(90), 0, 0)
    wheel.data.materials.append(wood_mat)

bpy.ops.mesh.primitive_cube_add(location=(wagon_x, wagon_y, 1.0))
coffin = bpy.context.active_object
coffin.scale = (0.75, 0.28, 0.11)
coffin.data.materials.append(wood_mat)

# Final render settings
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.view_settings.look = 'AgX - High Contrast'
scene.view_settings.exposure = -0.2

# Ensure camera is set
if scene.camera:
    cam = scene.camera
    cam.location = (3, -12, 3)
    cam.data.lens = 50
    target = Vector((0, 0, 1.0))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

print("Scene finalized with mood and detail")
print("Total objects:", len(bpy.data.objects))
