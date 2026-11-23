import bpy
import math
import random
from mathutils import Vector, Euler

# Clean up
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set scene properties
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = -0.3

# World settings - frosty morning light
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links

bg_node = world_nodes.get("Background")
bg_node.inputs[0].default_value = (0.7, 0.75, 0.85, 1.0)  # Pale frosty sky
bg_node.inputs[1].default_value = 0.8

# Sun light - low angle morning
sun_data = bpy.data.lights.new("MorningSun", type='SUN')
sun_data.energy = 3.5
sun_data.color = (1.0, 0.85, 0.65)  # Warm golden light
sun_data.angle = math.radians(2.0)
sun_obj = bpy.data.objects.new("MorningSun", sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(75), 0, math.radians(-30))  # Low angle

# Fill light - cool frosty
fill_data = bpy.data.lights.new("FrostFill", type='AREA')
fill_data.energy = 150
fill_data.color = (0.8, 0.85, 1.0)
fill_data.size = 20
fill_obj = bpy.data.objects.new("FrostFill", fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.location = (15, -10, 12)
fill_obj.rotation_euler = (math.radians(60), 0, math.radians(20))

# Helper functions
def add_sphere(loc, radius, color, name, roughness=0.6, emission=0.0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=16, ring_count=8)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    obj.data.materials.append(mat)
    return obj

def add_cylinder(loc, radius, depth, color, name, roughness=0.7):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, vertices=16)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    obj.data.materials.append(mat)
    return obj

def add_plane(loc, size, color, name, roughness=0.8):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    obj.data.materials.append(mat)
    return obj

def add_tree(loc, scale=1.0):
    """Create a bare orange-laden tree"""
    # Trunk
    trunk = add_cylinder((loc[0], loc[1], loc[2] + 1.5*scale), 0.15*scale, 3.0*scale, (0.25, 0.15, 0.08), "trunk", roughness=0.9)
    trunk.name = "tree_trunk"
    
    # Branches
    branch_positions = [
        (0.3, 0.2, 2.5), (-0.3, -0.1, 2.8), (0.1, 0.4, 3.0),
        (-0.2, 0.3, 3.2), (0.4, -0.2, 2.6), (-0.4, 0.1, 3.1)
    ]
    for i, bp in enumerate(branch_positions):
        branch = add_cylinder((loc[0]+bp[0]*scale, loc[1]+bp[1]*scale, loc[2]+bp[2]*scale), 
                              0.04*scale, 1.2*scale, (0.22, 0.13, 0.07), f"branch_{i}", roughness=0.9)
        # Random tilt
        branch.rotation_euler = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(0, 6.28))
    
    # Orange fruit clusters
    fruit_colors = [(0.9, 0.45, 0.05), (0.95, 0.5, 0.08), (0.85, 0.4, 0.03)]
    for i in range(12):
        fx = loc[0] + random.uniform(-0.8, 0.8)*scale
        fy = loc[1] + random.uniform(-0.8, 0.8)*scale
        fz = loc[2] + random.uniform(2.0, 3.5)*scale
        fruit = add_sphere((fx, fy, fz), random.uniform(0.06, 0.1)*scale, 
                          random.choice(fruit_colors), f"fruit_{i}", roughness=0.4)
    return trunk

def add_farmhouse(loc):
    """Create a simple farmhouse"""
    # Main body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], loc[2]+2))
    body = bpy.context.active_object
    body.name = "farmhouse_body"
    body.scale = (6, 4, 4)
    mat = bpy.data.materials.new("house_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.85, 0.8, 0.7, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
    body.data.materials.append(mat)
    
    # Roof
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], loc[2]+4.5))
    roof = bpy.context.active_object
    roof.name = "farmhouse_roof"
    roof.scale = (6.5, 4.5, 1.5)
    roof.rotation_euler = (0, 0, 0)
    mat_roof = bpy.data.materials.new("roof_mat")
    mat_roof.use_nodes = True
    bsdf_roof = mat_roof.node_tree.nodes.get("Principled BSDF")
    bsdf_roof.inputs["Base Color"].default_value = (0.3, 0.25, 0.2, 1.0)
    bsdf_roof.inputs["Roughness"].default_value = 0.9
    roof.data.materials.append(mat_roof)
    
    # Eave beam (where strings hang)
    eave = add_cylinder((loc[0], loc[1]-2.2, loc[2]+4.0), 0.08, 12, (0.3, 0.2, 0.1), "eave_beam", roughness=0.8)
    eave.rotation_euler = (0, math.radians(90), 0)
    
    # Windows
    for wx in [-2, 0, 2]:
        win = add_sphere((loc[0]+wx, loc[1]-2.05, loc[2]+2.5), 0.3, (0.4, 0.5, 0.6), f"window_{wx}", roughness=0.2)
        win.scale = (1, 0.3, 1.2)
    
    # Door
    door = add_sphere((loc[0], loc[1]-2.05, loc[2]+1.2), 0.4, (0.25, 0.15, 0.08), "door", roughness=0.8)
    door.scale = (1, 0.3, 1.5)
    
    return body

def add_bamboo_basket(loc, scale=1.0):
    """Create a bamboo basket"""
    # Base cylinder
    basket = add_cylinder((loc[0], loc[1], loc[2]+0.3*scale), 0.5*scale, 0.6*scale, 
                         (0.7, 0.55, 0.3), "bamboo_basket", roughness=0.7)
    # Make it open top by scaling
    basket.scale = (1, 1, 1)
    
    # Rim
    rim = add_cylinder((loc[0], loc[1], loc[2]+0.6*scale), 0.52*scale, 0.05*scale, 
                      (0.65, 0.5, 0.25), "basket_rim", roughness=0.6)
    return basket

def add_persimmon_string(loc, num_fruits=8):
    """Create a string of drying persimmons"""
    # String line
    string_data = bpy.data.meshes.new("persimmon_string")
    string_obj = bpy.data.objects.new("persimmon_string", string_data)
    scene.collection.objects.link(string_obj)
    
    # Create vertices for string
    verts = []
    for i in range(num_fruits + 1):
        x = loc[0] + i * 0.15
        y = loc[1]
        z = loc[2] - i * 0.12
        verts.append((x, y, z))
    
    string_data.from_pydata(verts, [], [])
    string_obj.data.update()
    
    mat_string = bpy.data.materials.new("string_mat")
    mat_string.use_nodes = True
    bsdf = mat_string.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.5, 0.4, 0.2, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    string_obj.data.materials.append(mat_string)
    
    # Add persimmons along the string
    persimmon_colors = [(0.9, 0.4, 0.05), (0.95, 0.45, 0.08), (0.85, 0.35, 0.03)]
    for i in range(num_fruits):
        px = loc[0] + i * 0.15 + 0.075
        py = loc[1]
        pz = loc[2] - i * 0.12 - 0.1
        p = add_sphere((px, py, pz), 0.08, random.choice(persimmon_colors), 
                      f"persimmon_{i}", roughness=0.3)
        # Slight squish for persimmon shape
        p.scale = (1, 1, 0.85)
    
    return string_obj

# Build the scene

# Ground - frosty yard
ground = add_plane((0, 0, 0), 40, (0.9, 0.92, 0.95), "frosty_ground", roughness=0.3)
ground.name = "frosty_ground"

# Add some frost patches
for i in range(15):
    fx = random.uniform(-10, 10)
    fy = random.uniform(-10, 10)
    frost = add_plane((fx, fy, 0.01), random.uniform(1, 3), (0.95, 0.97, 1.0), f"frost_{i}", roughness=0.1)

# Farmhouse
farmhouse = add_farmhouse((0, 5, 0))

# Persimmon strings hanging from eave
eave_y = 5 - 2.2  # Front of house
eave_z = 4.0
for i in range(6):
    sx = -3 + i * 1.2
    add_persimmon_string((sx, eave_y, eave_z), num_fruits=random.randint(6, 10))

# Trees with orange fruit
tree_positions = [
    (-8, -3, 0), (-5, -6, 0), (7, -4, 0), (10, -2, 0),
    (-10, 2, 0), (12, 3, 0), (6, -8, 0), (-6, -9, 0)
]
for i, tp in enumerate(tree_positions):
    add_tree(tp, scale=random.uniform(0.8, 1.3))

# Bamboo baskets in yard
basket_positions = [
    (-2, -2, 0), (1, -3, 0), (3, -1, 0), (-4, -4, 0), (5, -5, 0)
]
for i, bp in enumerate(basket_positions):
    add_bamboo_basket(bp, scale=random.uniform(0.8, 1.2))
    # Add some persimmons in baskets
    for j in range(5):
        px = bp[0] + random.uniform(-0.3, 0.3)
        py = bp[1] + random.uniform(-0.3, 0.3)
        pz = bp[2] + 0.4 + random.uniform(0, 0.2)
        add_sphere((px, py, pz), 0.07, (0.9, 0.4, 0.05), f"basket_persimmon_{i}_{j}", roughness=0.3)

# Camera
bpy.ops.object.camera_add(location=(0, -12, 2.5))
camera = bpy.context.active_object
camera.name = "main_camera"
camera.rotation_euler = (math.radians(80), 0, 0)
scene.camera = camera

# Set camera properties
camera.data.lens = 35
camera.data.sensor_width = 36

# Render settings
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4

# Add slight fog for frosty atmosphere
world_nodes.clear()
world_links.clear()

bg_node = world_nodes.new("Background")
bg_node.inputs[0].default_value = (0.75, 0.8, 0.9, 1.0)
bg_node.inputs[1].default_value = 0.6

fog_node = world_nodes.new("Volume Scatter")
fog_node.inputs["Color"].default_value = (0.9, 0.92, 0.95, 1.0)
fog_node.inputs["Density"].default_value = 0.015

out_node = world_nodes.new("World Output")
world_links.new(bg_node.outputs[0], out_node.inputs[0])
world_links.new(fog_node.outputs[0], out_node.inputs[1])

# Save viewport shading
bpy.context.space_data.shading.type = 'MATERIAL'

print("Persimmon yard scene created successfully!")
