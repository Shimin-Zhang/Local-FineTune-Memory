import bpy
import math
import mathutils
import random
import bmesh
from mathutils import Vector

# The scene is looking good! Let me add final refinements:
# 1. Make Luke face the sunset (away from camera) - he's currently facing camera
# 2. Add more detail to the dome
# 3. Improve the sky gradient
# 4. Add a subtle lens flare

# Rotate Luke to face the sunset (toward negative Y)
luke_parts = ["LukeTorso", "LukeHead", "LukeHair", "LukeLeg_-1", "LukeLeg_1", "LukeArm_-1", "LukeArm_1", "LukeBelt"]
for name in luke_parts:
    obj = bpy.data.objects.get(name)
    if obj:
        # Rotate to face away from camera (toward -Y)
        obj.rotation_euler = (0, 0, math.radians(180))

# Add more structural details to the dome
dome_mat = bpy.data.materials.get("DomeMaterial")
if dome_mat:
    # Add a vent on top of dome
    vent_data = bpy.data.meshes.new("Vent")
    vent_obj = bpy.data.objects.new("Vent", vent_data)
    bpy.context.scene.collection.objects.link(vent_obj)
    
    bm_vent = bmesh.new()
    bmesh.ops.create_cone(bm_vent, cap_ends=True, cap_tris=False, segments=8, radius1=0.5, radius2=0.3, depth=0.8)
    bm_vent.to_mesh(vent_data)
    bm_vent.free()
    
    vent_obj.location = (3, -15, 5.5)
    vent_obj.data.materials.append(dome_mat)
    
    # Add a small pipe coming out of the vent
    pipe_data = bpy.data.curves.new("VentPipe", type='CURVE')
    pipe_data.dimensions = '3D'
    pipe_data.bevel_depth = 0.04
    pipe_data.bevel_resolution = 2
    
    spline = pipe_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    spline.bezier_points[0].co = (0, 0, 0)
    spline.bezier_points[1].co = (0.3, 0, 0.5)
    for bp in spline.bezier_points:
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    
    pipe_obj = bpy.data.objects.new("VentPipe", pipe_data)
    bpy.context.scene.collection.objects.link(pipe_obj)
    pipe_obj.location = (3, -15, 5.5)
    pipe_obj.data.materials.append(dome_mat)

# Add a ladder to the dome
ladder_data = bpy.data.curves.new("Ladder", type='CURVE')
ladder_data.dimensions = '3D'
ladder_data.bevel_depth = 0.03
ladder_data.bevel_resolution = 2

spline_ladder = ladder_data.splines.new('POLY')
spline_ladder.points.add(10)
for i in range(11):
    t = i / 10
    x = 3 + 4.8 * math.cos(math.pi/4) * math.cos(t * math.pi/2)
    y = -15 + 4.8 * math.sin(math.pi/4) * math.cos(t * math.pi/2)
    z = t * 4
    spline_ladder.points[i].co = (x, y, z, 1)

ladder_obj = bpy.data.objects.new("Ladder", ladder_data)
bpy.context.scene.collection.objects.link(ladder_obj)
ladder_obj.data.materials.append(dome_mat)

# Add rungs to the ladder
for i in range(5):
    t = (i + 0.5) / 5
    x = 3 + 4.8 * math.cos(math.pi/4) * math.cos(t * math.pi/2)
    y = -15 + 4.8 * math.sin(math.pi/4) * math.cos(t * math.pi/2)
    z = t * 4
    
    rung_data = bpy.data.curves.new(f"LadderRung_{i}", type='CURVE')
    rung_data.dimensions = '3D'
    rung_data.bevel_depth = 0.02
    rung_data.bevel_resolution = 1
    
    spline_rung = rung_data.splines.new('POLY')
    spline_rung.points.add(1)
    spline_rung.points[0].co = (x - 0.15, y, z, 1)
    spline_rung.points[1].co = (x + 0.15, y, z, 1)
    
    rung_obj = bpy.data.objects.new(f"LadderRung_{i}", rung_data)
    bpy.context.scene.collection.objects.link(rung_obj)
    rung_obj.data.materials.append(dome_mat)

# Add a small flag on the antenna
flag_data = bpy.data.meshes.new("Flag")
flag_obj = bpy.data.objects.new("Flag", flag_data)
bpy.context.scene.collection.objects.link(flag_obj)

bm_flag = bmesh.new()
bmesh.ops.create_grid(bm_flag, x_segments=5, y_segments=3, size=1)
for v in bm_flag.verts:
    v.co.x *= 0.4
    v.co.y *= 0.25
    v.co.z = 0
bm_flag.to_mesh(flag_data)
bm_flag.free()

flag_obj.location = (3.1, -15, 8.5)
flag_obj.rotation_euler = (0, 0, math.radians(90))

flag_mat = bpy.data.materials.new("FlagMat")
flag_mat.use_nodes = True
flag_nodes = flag_mat.node_tree.nodes
flag_links = flag_mat.node_tree.links
for node in flag_nodes:
    flag_nodes.remove(node)
bsdf_flag = flag_nodes.new('ShaderNodeBsdfPrincipled')
bsdf_flag.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1)
bsdf_flag.inputs['Roughness'].default_value = 0.9
flag_links.new(bsdf_flag.outputs['BSDF'], flag_nodes.new('ShaderNodeOutputMaterial').inputs['Surface'])
flag_obj.data.materials.append(flag_mat)

# Add some sand dust particles in the air (small spheres)
dust_mat = bpy.data.materials.new("DustMat")
dust_mat.use_nodes = True
dust_mat.blend_method = 'BLEND'
dust_nodes = dust_mat.node_tree.nodes
dust_links = dust_mat.node_tree.links
for node in dust_nodes:
    dust_nodes.remove(node)
bsdf_dust = dust_nodes.new('ShaderNodeBsdfPrincipled')
bsdf_dust.inputs['Base Color'].default_value = (0.8, 0.6, 0.4, 1)
bsdf_dust.inputs['Alpha'].default_value = 0.3
dust_links.new(bsdf_dust.outputs['BSDF'], dust_nodes.new('ShaderNodeOutputMaterial').inputs['Surface'])

for i in range(20):
    dust_data = bpy.data.meshes.new(f"Dust_{i}")
    dust_obj = bpy.data.objects.new(f