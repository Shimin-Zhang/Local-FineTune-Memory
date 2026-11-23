import bpy
import math
import random
from mathutils import Vector

# Remove fog sphere - it's blocking the view
fog = bpy.data.objects.get('FogSphere')
if fog:
    bpy.data.objects.remove(fog, do_unlink=True)

# Remove clouds that are blocking
for i in range(8):
    cloud = bpy.data.objects.get(f'Cloud_{i}')
    if cloud:
        bpy.data.objects.remove(cloud, do_unlink=True)

# Reposition camera: lower and closer, looking up at Kong
cam_obj = bpy.data.objects.get('Camera')
if cam_obj:
    cam_obj.location = (80, 80, 350)
    target = Vector((0, 0, 500))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.data.lens = 35

# Boost lighting significantly
moon_light = bpy.data.lights.get('Moon')
if moon_light:
    moon_light.energy = 8.0

city_glow_light = bpy.data.lights.get('CityGlow')
if city_glow_light:
    city_glow_light.energy = 500

rim_light = bpy.data.lights.get('RimLight')
if rim_light:
    rim_light.energy = 1000

# Add a key light directly on Kong
key_light = bpy.data.lights.new('KongKey', type='POINT')
key_light.energy = 2000
key_light.color = (0.9, 0.85, 0.7)
key_obj = bpy.data.objects.new('KongKey', key_light)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (30, 30, 550)

# Make ESB windows brighter
mat_window_lit = bpy.data.materials.get('WindowLit')
if mat_window_lit:
    bsdf = mat_window_lit.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.9, 0.5, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 5.0

# Make Kong material slightly emissive so he's visible
mat_kong = bpy.data.materials.get('Kong')
if mat_kong:
    bsdf = mat_kong.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Emission Color'].default_value = (0.3, 0.2, 0.15, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 0.5

# Add more city glow lights at ground level
for i in range(5):
    x = random.uniform(-100, 100)
    y = random.uniform(-100, 100)
    if abs(x) < 30 and abs(y) < 30:
        continue
    glow = bpy.data.lights.new(f'CityGlow_{i}', type='POINT')
    glow.energy = 100
    glow.color = (1.0, 0.7, 0.3)
    glow_obj = bpy.data.objects.new(f'CityGlow_{i}', glow)
    bpy.context.collection.objects.link(glow_obj)
    glow_obj.location = (x, y, 10)

# Add searchlights sweeping from city
mat_searchlight = bpy.data.materials.new('SearchlightMat')
mat_searchlight.use_nodes = True
bsdf_sl = mat_searchlight.node_tree.nodes.get('Principled BSDF')
bsdf_sl.inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1.0)
bsdf_sl.inputs['Emission Color'].default_value = (0.8, 0.9, 1.0, 1.0)
bsdf_sl.inputs['Emission Strength'].default_value = 15.0

for i in range(4):
    x = random.uniform(-80, 80)
    y = random.uniform(-80, 80)
    if abs(x) < 30 and abs(y) < 30:
        continue
    # Searchlight beam (cone)
    bpy.ops.mesh.primitive_cone_add(radius1=2, radius2=15, depth=200, location=(x, y, 100), vertices=8)
    beam = bpy.context.active_object
    beam.name = f'Searchlight_{i}'
    # Point beam toward Kong
    target = Vector((0, 0, 500))
    direction = target - beam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    beam.rotation_euler = rot_quat.to_euler()
    beam.data.materials.append(mat_searchlight)
    # Make beam transparent
    beam.data.materials[0].blend_method = 'BLEND'
    beam.data.materials[0].show_transparent_back = False

# Add more biplanes at different heights
mat_biplane = bpy.data.materials.get('Biplane')
def make_biplane_simple(name, loc, rot_z):
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=10, location=loc, vertices=8)
    fus = bpy.context.active_object
    fus.name = name+'_Fus'
    fus.rotation_euler = (0, math.radians(90), rot_z)
    fus.data.materials.append(mat_biplane)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], loc[2]+2))
    wup = bpy.context.active_object
    wup.name = name+'_WUp'
    wup.scale = (14, 1, 0.3)
    wup.rotation_euler = (0, 0, rot_z)
    wup.data.materials.append(mat_biplane)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], loc[2]-1))
    wlo = bpy.context.active_object
    wlo.name = name+'_WLo'
    wlo.scale = (14, 1, 0.3)
    wlo.rotation_euler = (0, 0, rot_z)
    wlo.data.materials.append(mat_biplane)

# Second ring of biplanes
for i in range(6):
    angle = (i / 6) * 2 * math.pi + 0.5
    x = 150 * math.cos(angle)
    y = 150 * math.sin(angle)
    z = 550 + 20 * math.sin(angle * 2)
    make_biplane_simple(f'Biplane2_{i}', (x, y, z), angle + math.pi/2)

# Add airplane lights (red/green)
mat_red_light = bpy.data.materials.new('RedLight')
mat_red_light.use_nodes = True
bsdf_rl = mat_red_light.node_tree.nodes.get('Principled BSDF')
bsdf_rl.inputs['Base Color'].default_value = (1.0, 0, 0, 1.0)
bsdf_rl.inputs['Emission Color'].default_value = (1.0, 0, 0, 1.0)
bsdf_rl.inputs['Emission Strength'].default_value = 20.0

mat_green_light = bpy.data.materials.new('GreenLight')
mat_green_light.use_nodes = True
bsdf_gl = mat_green_light.node_tree.nodes.get('Principled BSDF')
bsdf_gl.inputs['Base Color'].default_value = (0, 1.0, 0, 1.0)
bsdf_gl.inputs['Emission Color'].default_value = (0, 1.0, 0, 1.0)
bsdf_gl.inputs['Emission Strength'].default_value = 20.0

for i in range(10):
    angle = (i / 10) * 2 * math.pi
    x = 120 * math.cos(angle)
    y = 120 * math.sin(angle)
    z = 520 + 15 * math.sin(angle * 3)
    # Red light on left wing
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x-7, y, z+2), segments=8, ring_count=4)
    rl = bpy.context.active_object
    rl.name = f'PlaneRed_{i}'
    rl.data.materials.append(mat_red_light)
    # Green light on right wing
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x+7, y, z+2), segments=8, ring_count=4)
    gl = bpy.context.active_object
    gl.name = f'PlaneGreen_{i}'
    gl.data.materials.append(mat_green_light)

print("Scene refined: camera fixed, fog removed, lighting boosted, searchlights, plane lights, more biplanes")
