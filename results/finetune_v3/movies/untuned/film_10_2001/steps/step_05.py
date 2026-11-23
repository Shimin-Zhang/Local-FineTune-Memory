import bpy
import math
import random
from mathutils import Vector

# The scene looks good! Now let's refine and add more detail:
# 1. The monolith is floating - it needs to be grounded
# 2. Add more dramatic lighting
# 3. Add some atmospheric haze
# 4. Improve the ground to be more savanna-like
# 5. Add more rocks and vegetation

scene = bpy.context.scene

# Fix monolith - make sure it's grounded (it should already be at z=4 center with height 8, so base at 0)
# The monolith looks like it's floating because the ground is displaced. Let's lower it slightly or raise ground
monolith = bpy.data.objects.get("Monolith")
if monolith:
    # The monolith base should be at ground level. Since ground has displacement, 
    # let's make sure the monolith sits properly
    monolith.location.z = 0.1  # Slightly above to avoid z-fighting with displaced ground

# Add atmospheric haze for depth
world = scene.world
nodes = world.node_tree.nodes
links = world.node_tree.links

# Find the background node and add volume scatter for haze
bg_node = None
for node in nodes:
    if node.type == 'BACKGROUND':
        bg_node = node
        break

# Add a volume scatter for atmospheric haze
vol_scatter = nodes.new('ShaderNodeVolumeScatter')
vol_scatter.inputs['Color'].default_value = (0.8, 0.6, 0.4, 1)
vol_scatter.inputs['Density'].default_value = 0.005
vol_scatter.inputs['Anisotropy'].default_value = 0.3

out_node = None
for node in nodes:
    if node.type == 'OUTPUT_WORLD':
        out_node = node
        break

if out_node:
    links.new(vol_scatter.outputs['Volume'], out_node.inputs['Volume'])

# Add a second sun for rim lighting from the side
rim_data = bpy.data.lights.new("RimSun", type='SUN')
rim_data.energy = 1.5
rim_data.color = (1.0, 0.5, 0.2)
rim_data.angle = math.radians(5)
rim_obj = bpy.data.objects.new("RimSun", rim_data)
scene.collection.objects.link(rim_obj)
rim_obj.rotation_euler = (math.radians(80), math.radians(10), math.radians(90))

# Add more distant rocks for depth
def create_rock(location, scale, rotation_z=0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=location)
    rock = bpy.context.active_object
    rock.name = f"Rock_{random.randint(1000,9999)}"
    
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(rock.data)
    for vert in bm.verts:
        vert.co.x += random.uniform(-0.15, 0.15)
        vert.co.y += random.uniform(-0.15, 0.15)
        vert.co.z += random.uniform(-0.1, 0.1)
    bm.to_mesh(rock.data)
    bm.free()
    
    rock.scale = (scale[0], scale[1], scale[2])
    rock.rotation_euler = (0, 0, rotation_z)
    bpy.ops.object.transform_apply(scale=True)
    
    mod = rock.modifiers.new("Subdiv", 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 2
    mod.render_levels = 3
    
    tex = bpy.data.textures.new(f"RockTex_{rock.name}", type='CLOUDS')
    tex.noise_scale = 0.5
    tex.noise_depth = 3
    
    disp_mod = rock.modifiers.new("Displace", 'DISPLACE')
    disp_mod.texture = tex
    disp_mod.strength = 0.1
    
    mat = bpy.data.materials.new(f"RockMat_{rock.name}")
    mat.use_nodes = True
    nodes_m = mat.node_tree.nodes
    links_m = mat.node_tree.links
    
    for node in nodes_m:
        nodes_m.remove(node)
    
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.95
    bsdf.inputs['Specular IOR Level'].default_value = 0.05
    
    noise = nodes_m.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 10.0
    
    color_ramp_m = nodes_m.new('ShaderNodeValToRGB')
    color_ramp_m.color_ramp.elements[0].position = 0.3
    color_ramp_m.color_ramp.elements[0].color = (0.25, 0.18, 0.12, 1)
    color_ramp_m.color_ramp.elements[1].position = 0.7
    color_ramp_m.color_ramp.elements[1].color = (0.4, 0.3, 0.2, 1)
    
    links_m.new(noise.outputs['Fac'], color_ramp_m.inputs['Fac'])
    links_m.new(color_ramp_m.outputs['Color'], bsdf.inputs['Base Color'])
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    rock.data.materials.append(mat)
    return rock

# Add distant rocks
for i in range(20):
    angle = random.uniform(0, 2*math.pi)
    dist = random.uniform(15, 30)
    x = math.cos(angle) * dist
    y = math.sin(angle) * dist
    scale = random.uniform(0.5, 1.5)
    create_rock((x, y, scale*0.3), (scale, scale*0.8, scale*0.6), random.uniform(0, 2*math.pi))

# Add some acacia-like trees in the distance for savanna feel
def create_acacia_tree(location, scale=1.0):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.1*scale, depth=3*scale, location=(location[0], location[1], 1.5*scale))
    trunk = bpy.context.active_object
    trunk.name = f"Tree_Trunk_{random.randint(100,999)}"
    trunk.rotation_euler = (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 0)
    
    # Canopy - flat umbrella shape
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=2*scale, radius2=0.5*scale, depth=0.8*scale, location=(location[0], location[1], 3.2*scale))
    canopy = bpy.context.active_object
    canopy.name = f"Tree_Canopy_{trunk.name}"
    
    # Materials
    trunk_mat = bpy.data.materials.new(f"TrunkMat_{trunk.name}")
    trunk_mat.use_nodes = True
    nodes_m = trunk_mat.node_tree.nodes
    links_m = trunk_mat.node_tree.links
    for node in nodes_m:
        nodes_m.remove(node)
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.2, 0.12, 0.06, 1)
    bsdf.inputs['Roughness'].default_value = 0.9
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    trunk.data.materials.append(trunk_mat)
    
    canopy_mat = bpy.data.materials.new(f"CanopyMat_{trunk.name}")
    canopy_mat.use_nodes = True
    nodes_m = canopy_mat.node_tree.nodes
    links_m = canopy_mat.node_tree.links
    for node in nodes_m:
        nodes_m.remove(node)
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.3, 0.35, 0.1, 1)
    bsdf.inputs['Roughness'].default_value = 0.8
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    canopy.data.materials.append(canopy_mat)
    
    return [trunk, canopy]

# Place a few trees in the distance
tree_positions = [
    ((-20, -15, 0), 1.2),
    ((25, -10, 0), 1.0),
    ((-15, 20, 0), 1.1),
    ((20, 18, 0), 0.9),
    ((-25, 5, 0), 1.3),
    ((18, -20, 0), 1.0),
]

for pos, scl in tree_positions:
    create_acacia_tree(pos, scl)

# Add more grass tufts
def create_grass_tuft(location):
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.05, radius2=0.0, depth=0.3, location=location)
    grass = bpy.context.active_object
    grass.name = f"Grass_{random.randint(100,999)}"
    grass.rotation_euler = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), 0)
    
    mat = bpy.data.materials.new(f"GrassMat_{grass.name}")
    mat.use_nodes = True
    nodes_m = mat.node_tree.nodes
    links_m = mat.node_tree.links
    for node in nodes_m:
        nodes_m.remove(node)
    output = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.5, 0.4, 0.15, 1)
    bsdf.inputs['Roughness'].default_value = 0.9
    links_m.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    grass.data.materials.append(mat)
    return grass

for i in range(30):
    angle = random.uniform(0, 2*math.pi)
    dist = random.uniform(5, 20)
    x = math.cos(angle) * dist
    y = math.sin(angle) * dist
    if abs(x) > 3 and abs(y) > 3:
        create_grass_tuft((x, y, 0.15))

# Adjust camera for better composition - slightly lower and wider
camera = bpy.data.objects.get("MainCamera")
if camera:
    camera.location = (7, 10, 1.2)
    target = Vector((0, 0, 3.5))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    camera.data.lens = 45

print("Scene refined with more detail!")
print(f"Objects in scene: {len(bpy.data.objects)}")
