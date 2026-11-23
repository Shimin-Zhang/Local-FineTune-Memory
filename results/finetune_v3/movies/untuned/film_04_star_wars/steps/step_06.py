import bpy
import math
import mathutils
import random
import bmesh
from mathutils import Vector

# Fix the bmesh import issue and continue refining the scene
# The suns are now visible! Good progress. Let's refine further.

# Reposition Luke to be more visible - he's cut off on the left
luke_parts = ["LukeTorso", "LukeHead", "LukeHair", "LukeLeg_-1", "LukeLeg_1", "LukeArm_-1", "LukeArm_1", "LukeBelt"]
for name in luke_parts:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.x = -1.5
        obj.location.y = 8
        obj.scale = (1.2, 1.2, 1.2)

# Adjust camera to better frame the scene
cam = bpy.data.objects.get("Camera")
if cam:
    cam.location = (-1, 11, 1.5)
    cam.rotation_euler = (math.radians(86), 0, math.radians(175))
    cam.data.lens = 35

# Add the foreground rocks that failed to create due to bmesh not being defined
rock_mat = bpy.data.materials.get("RockMat")
if rock_mat:
    for i in range(10):
        rock_data = bpy.data.meshes.new(f"NewFGRock_{i}")
        rock_obj = bpy.data.objects.new(f"NewFGRock_{i}", rock_data)
        bpy.context.scene.collection.objects.link(rock_obj)
        
        bm_rock = bmesh.new()
        bmesh.ops.create_icosphere(bm_rock, subdivisions=2, radius=0.15)
        for v in bm_rock.verts:
            v.co += Vector((random.uniform(-0.04, 0.04), random.uniform(-0.04, 0.04), random.uniform(-0.04, 0.04)))
        bm_rock.to_mesh(rock_data)
        bm_rock.free()
        
        rock_obj.location = (random.uniform(-4, 4), random.uniform(6, 12), 0.03)
        rock_obj.scale = (random.uniform(0.5, 2), random.uniform(0.5, 2), random.uniform(0.3, 0.8))
        rock_obj.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))
        rock_obj.data.materials.append(rock_mat)

# Add the mesas that failed
mesa_mat = bpy.data.materials.get("MesaMat")
if not mesa_mat:
    mesa_mat = bpy.data.materials.new("MesaMat")
    mesa_mat.use_nodes = True
    mesa_nodes = mesa_mat.node_tree.nodes
    mesa_links = mesa_mat.node_tree.links
    for node in mesa_nodes:
        mesa_nodes.remove(node)
    bsdf_mesa = mesa_nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_mesa.inputs['Base Color'].default_value = (0.45, 0.25, 0.12, 1)
    bsdf_mesa.inputs['Roughness'].default_value = 0.95
    mesa_links.new(bsdf_mesa.outputs['BSDF'], mesa_nodes.new('ShaderNodeOutputMaterial').inputs['Surface'])

# Mesa 1
mesa_data = bpy.data.meshes.new("Mesa")
mesa_obj = bpy.data.objects.new("Mesa", mesa_data)
bpy.context.scene.collection.objects.link(mesa_obj)
bm_mesa = bmesh.new()
bmesh.ops.create_cone(bm_mesa, cap_ends=True, cap_tris=False, segments=8, radius1=8, radius2=5, depth=6)
bm_mesa.to_mesh(mesa_data)
bm_mesa.free()
mesa_obj.location = (-30, -50, 3)
mesa_obj.data.materials.append(mesa_mat)

# Mesa 2
mesa2_data = bpy.data.meshes.new("Mesa2")
mesa2_obj = bpy.data.objects.new("Mesa2", mesa2_data)
bpy.context.scene.collection.objects.link(mesa2_obj)
bm_mesa2 = bmesh.new()
bmesh.ops.create_cone(bm_mesa2, cap_ends=True, cap_tris=False, segments=6, radius1=6, radius2=4, depth=4)
bm_mesa2.to_mesh(mesa2_data)
bm_mesa2.free()
mesa2_obj.location = (35, -55, 2)
mesa2_obj.data.materials.append(mesa_mat)

# Add sand ripple displacement to ground
ground_obj = bpy.data.objects.get("Ground")
if ground_obj:
    # Check if modifier already exists
    if "SandRipples" not in [m.name for m in ground_obj.modifiers]:
        displace2 = ground_obj.modifiers.new("SandRipples", 'DISPLACE')
        displace2.strength = 0.15
        displace2.mid_level = 0.5
        ripple_tex = bpy.data.textures.new("SandRippleTex", type='MARBLE')
        ripple_tex.noise_scale = 0.5
        ripple_tex.turbulence = 5
        ripple_tex.noise_depth = 3
        displace2.texture = ripple_tex

# Make the suns slightly less intense so they don't blow out
sun1_obj = bpy.data.objects.get("Sun1")
sun2_obj = bpy.data.objects.get("Sun2")

if sun1_obj:
    sun1_mat = bpy.data.materials.get("Sun1Mat")
    if sun1_mat and sun1_mat.use_nodes:
        for node in sun1_mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node.inputs['Emission Strength'].default_value = 30.0

if sun2_obj:
    sun2_mat = bpy.data.materials.get("Sun2Mat")
    if sun2_mat and sun2_mat.use_nodes:
        for node in sun2_mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node.inputs['Emission Strength'].default_value = 25.0

# Add some distant birds (simple V shapes) for life
bird_mat = bpy.data.materials.new("BirdMat")
bird_mat.use_nodes = True
bird_nodes = bird_mat.node_tree.nodes
bird_links = bird_mat.node_tree.links
for node in bird_nodes:
    bird_nodes.remove(node)
bsdf_bird = bird_nodes.new('ShaderNodeBsdfPrincipled')
bsdf_bird.inputs['Base Color'].default_value = (0.1, 0.08, 0.05, 1)
bird_links.new(bsdf_bird.outputs['BSDF'], bird_nodes.new('ShaderNodeOutputMaterial').inputs['Surface'])

for i in range(5):
    bird_data = bpy.data.curves.new(f"Bird_{i}", type='CURVE')
    bird_data.dimensions = '3D'
    bird_data.bevel_depth = 0.02
    bird_data.bevel_resolution = 1
    
    spline = bird_data.splines.new('POLY')
    spline.points.add(2)
    
    bx = random.uniform(-10, 10)
    by = -40 - random.uniform(0, 10)
    bz = 8 + random.uniform(0, 5)
    
    wing_span = 0.3 + random.uniform(0, 0.2)
    spline.points[0].co = (bx - wing_span, by, bz, 1)
    spline.points[1].co = (bx, by, bz + 0.1, 1)
    spline.points[2].co = (bx + wing_span, by, bz, 1)
    
    bird_obj = bpy.data.objects.new(f"Bird_{i}", bird_data)
    bpy.context.scene.collection.objects.link(bird_obj)
    bird_obj.data.materials.append(bird_mat)

# Add a subtle warm rim light from the sunset direction
rim_light_data = bpy.data.lights.new("RimLight", type='SUN')
rim_light_data.energy = 2.0
rim_light_data.color = (1.0, 0.4, 0.1)
rim_light_data.angle = math.radians(10)
rim_light = bpy.data.objects.new("RimLight", rim_light_data)
bpy.context.scene.collection.objects.link(rim_light)
rim_light.rotation_euler = (math.radians(80), 0, math.radians(180))

# Final render settings
scene = bpy.context.scene
scene.view_settings.exposure = -0.2
scene.cycles.samples = 256

print("Scene refined with birds, mesas, rocks, and better lighting!")
