import bpy
import math
import random
from mathutils import Vector

# Fix camera to see the scene properly
cam_obj = bpy.data.objects.get('Camera')
if cam_obj:
    cam_obj.location = (200, 200, 500)
    target = Vector((0, 0, 400))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.data.lens = 35

# Remove atmosphere box if it exists (caused issues)
atm_box = bpy.data.objects.get('AtmosphereBox')
if atm_box:
    bpy.data.objects.remove(atm_box, do_unlink=True)

# Boost lighting - make everything much brighter
for light_name in ['Moon', 'CityGlow', 'RimLight', 'KongKey', 'Backlight']:
    light = bpy.data.lights.get(light_name)
    if light:
        light.energy *= 3

# Make all materials more visible with emission
def boost_material(mat_name, color, strength):
    mat = bpy.data.materials.get(mat_name)
    if mat:
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs['Emission Color'].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs['Emission Strength'].default_value = strength

boost_material('Building', (0.4, 0.4, 0.5), 2.0)
boost_material('Kong', (0.5, 0.4, 0.3), 2.0)
boost_material('Biplane', (1.0, 0.3, 0.3), 2.0)
boost_material('City', (0.3, 0.3, 0.4), 1.0)
boost_material('WindowLit', (1.0, 0.9, 0.5), 10.0)
boost_material('CityMat2', (0.3, 0.3, 0.4), 1.0)

# Add crown lights to ESB
mat_crown_light = bpy.data.materials.get('CrownLight')
if not mat_crown_light:
    mat_crown_light = bpy.data.materials.new('CrownLight')
    mat_crown_light.use_nodes = True
    bsdf_cl = mat_crown_light.node_tree.nodes.get('Principled BSDF')
    bsdf_cl.inputs['Base Color'].default_value = (1.0, 0.9, 0.5, 1.0)
    bsdf_cl.inputs['Emission Color'].default_value = (1.0, 0.9, 0.5, 1.0)
    bsdf_cl.inputs['Emission Strength'].default_value = 20.0

for i in range(8):
    angle = (i / 8) * 2 * math.pi
    x = 5 * math.cos(angle)
    y = 5 * math.sin(angle)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, y, 415), segments=8, ring_count=4)
    crown_light = bpy.context.active_object
    crown_light.name = f'CrownLight_{i}'
    crown_light.data.materials.append(mat_crown_light)

# Antenna light
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 478), segments=8, ring_count=4)
antenna_light = bpy.context.active_object
antenna_light.name = 'AntennaLight'
antenna_light.data.materials.append(mat_crown_light)

# Add moon glow
mat_moon_glow = bpy.data.materials.get('MoonGlow')
if not mat_moon_glow:
    mat_moon_glow = bpy.data.materials.new('MoonGlow')
    mat_moon_glow.use_nodes = True
    bsdf_mg = mat_moon_glow.node_tree.nodes.get('Principled BSDF')
    bsdf_mg.inputs['Base Color'].default_value = (0.8, 0.85, 1.0, 1.0)
    bsdf_mg.inputs['Emission Color'].default_value = (0.8, 0.85, 1.0, 1.0)
    bsdf_mg.inputs['Emission Strength'].default_value = 15.0

bpy.ops.mesh.primitive_uv_sphere_add(radius=25, location=(-200, -300, 600), segments=16, ring_count=8)
moon_glow = bpy.context.active_object
moon_glow.name = 'MoonGlow'
moon_glow.data.materials.append(mat_moon_glow)

# Add more stars
mat_star = bpy.data.materials.get('StarMat')
if not mat_star:
    mat_star = bpy.data.materials.new('StarMat')
    mat_star.use_nodes = True
    bsdf_st = mat_star.node_tree.nodes.get('Principled BSDF')
    bsdf_st.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_st.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_st.inputs['Emission Strength'].default_value = 30.0

random.seed(202)
for i in range(100):
    x = random.uniform(-500, 500)
    y = random.uniform(-500, 500)
    z = random.uniform(400, 900)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x, y, z), segments=8, ring_count=4)
    star = bpy.context.active_object
    star.name = f'Star4_{i}'
    star.data.materials.append(mat_star)

# Add airplane contrails
mat_contrail = bpy.data.materials.get('ContrailMat')
if not mat_contrail:
    mat_contrail = bpy.data.materials.new('ContrailMat')
    mat_contrail.use_nodes = True
    bsdf_ct = mat_contrail.node_tree.nodes.get('Principled BSDF')
    bsdf_ct.inputs['Base Color'].default_value = (0.6, 0.6, 0.7, 1.0)
    bsdf_ct.inputs['Emission Color'].default_value = (0.6, 0.6, 0.7, 1.0)
    bsdf_ct.inputs['Emission Strength'].default_value = 8.0

for i in range(10):
    angle = (i / 10) * 2 * math.pi
    x = 120 * math.cos(angle)
    y = 120 * math.sin(angle)
    z = 520 + 15 * math.sin(angle * 3)
    for j in range(4):
        tx = x - 6 * (j+1) * math.cos(angle + math.pi/2)
        ty = y - 6 * (j+1) * math.sin(angle + math.pi/2)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=3, location=(tx, ty, z), vertices=6)
        contrail = bpy.context.active_object
        contrail.name = f'Contrail_{i}_{j}'
        contrail.rotation_euler = (0, math.radians(90), angle + math.pi/2)
        contrail.data.materials.append(mat_contrail)

# Add more city buildings with lit windows
mat_city3 = bpy.data.materials.new('CityMat3')
mat_city3.use_nodes = True
bsdf_c3 = mat_city3.node_tree.nodes.get('Principled BSDF')
bsdf_c3.inputs['Base Color'].default_value = (0.2, 0.2, 0.3, 1.0)
bsdf_c3.inputs['Emission Color'].default_value = (0.2, 0.2, 0.3, 1.0)
bsdf_c3.inputs['Emission Strength'].default_value = 1.0

random.seed(303)
for i in range(20):
    x = random.uniform(-200, 200)
    y = random.uniform(-200, 200)
    if abs(x) < 35 and abs(y) < 35:
        continue
    h = random.uniform(10, 50)
    w = random.uniform(3, 10)
    d = random.uniform(3, 10)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h/2))
    bldg = bpy.context.active_object
    bldg.name = f'City3_{i}'
    bldg.scale = (w, d, h)
    bldg.data.materials.append(mat_city3)
    # Add lit windows
    for k in range(int(h/5)):
        wx = x + random.uniform(-w/2+1, w/2-1)
        wy = y + random.uniform(-d/2+1, d/2-1)
        wz = 2 + k * 5
        bpy.ops.mesh.primitive_cube_add(size=1, location=(wx, wy, wz))
        win = bpy.context.active_object
        win.name = f'City3Win_{i}_{k}'
        win.scale = (0.4, 0.4, 0.4)
        win.data.materials.append(bpy.data.materials.get('WindowLit'))

# Add searchlight beams (cones pointing up)
mat_searchlight = bpy.data.materials.get('SearchlightMat')
if not mat_searchlight:
    mat_searchlight = bpy.data.materials.new('SearchlightMat')
    mat_searchlight.use_nodes = True
    bsdf_sl = mat_searchlight.node_tree.nodes.get('Principled BSDF')
    bsdf_sl.inputs['Base Color'].default_value = (0.7, 0.8, 1.0, 1.0)
    bsdf_sl.inputs['Emission Color'].default_value = (0.7, 0.8, 1.0, 1.0)
    bsdf_sl.inputs['Emission Strength'].default_value = 10.0

for i in range(6):
    x = random.uniform(-100, 100)
    y = random.uniform(-100, 100)
    if abs(x) < 30 and abs(y) < 30:
        continue
    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=10, depth=150, location=(x, y, 75), vertices=8)
    beam = bpy.context.active_object
    beam.name = f'SearchBeam_{i}'
    # Point toward Kong
    target = Vector((0, 0, 500))
    direction = target - beam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    beam.rotation_euler = rot_quat.to_euler()
    beam.data.materials.append(mat_searchlight)

print("Scene refined: camera fixed, materials boosted, crown lights, moon glow, stars, contrails, city, searchlights")
