import bpy
import math
import random
from mathutils import Vector

# The camera is too close and looking at the ground. Fix to a dramatic wide shot.
cam_obj = bpy.data.objects.get('Camera')
if cam_obj:
    # Position camera far away and high, looking down at the scene
    cam_obj.location = (250, 250, 600)
    # Look at Kong on top of ESB
    target = Vector((0, 0, 480))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.data.lens = 24  # Wide angle to capture the whole scene

# Boost all lights further for visibility
for light_name in ['Moon', 'CityGlow', 'RimLight', 'KongKey']:
    light = bpy.data.lights.get(light_name)
    if light:
        light.energy *= 2

# Make building material lighter so it's visible
mat_building = bpy.data.materials.get('Building')
if mat_building:
    bsdf = mat_building.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.35, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.1, 0.1, 0.15, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 1.0

# Make Kong more visible
mat_kong = bpy.data.materials.get('Kong')
if mat_kong:
    bsdf = mat_kong.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.4, 0.3, 0.2, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.4, 0.3, 0.2, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 1.0

# Make biplanes more visible
mat_biplane = bpy.data.materials.get('Biplane')
if mat_biplane:
    bsdf = mat_biplane.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.9, 0.2, 0.2, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.9, 0.2, 0.2, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 1.0

# Add a strong backlight to silhouette Kong
backlight = bpy.data.lights.new('Backlight', type='SUN')
backlight.energy = 10.0
backlight.color = (0.5, 0.6, 1.0)
backlight_obj = bpy.data.objects.new('Backlight', backlight)
bpy.context.collection.objects.link(backlight_obj)
backlight_obj.rotation_euler = (math.radians(60), math.radians(30), math.radians(225))

# Add volumetric fog effect using a large transparent cube around the city
mat_atmosphere = bpy.data.materials.new('Atmosphere')
mat_atmosphere.use_nodes = True
bsdf_atm = mat_atmosphere.node_tree.nodes.get('Principled BSDF')
bsdf_atm.inputs['Base Color'].default_value = (0.05, 0.08, 0.15, 1.0)
bsdf_atm.inputs['Roughness'].default_value = 1.0
bsdf_atm.inputs['Transmission'].default_value = 0.8
mat_atmosphere.blend_method = 'BLEND'
mat_atmosphere.show_transparent_back = False

# Large atmosphere box
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 150))
atm_box = bpy.context.active_object
atm_box.name = 'AtmosphereBox'
atm_box.scale = (300, 300, 200)
atm_box.data.materials.append(mat_atmosphere)

# Add more detailed ESB crown lights
mat_crown_light = bpy.data.materials.new('CrownLight')
mat_crown_light.use_nodes = True
bsdf_cl = mat_crown_light.node_tree.nodes.get('Principled BSDF')
bsdf_cl.inputs['Base Color'].default_value = (1.0, 0.9, 0.5, 1.0)
bsdf_cl.inputs['Emission Color'].default_value = (1.0, 0.9, 0.5, 1.0)
bsdf_cl.inputs['Emission Strength'].default_value = 20.0

# Lights around the crown of ESB
for i in range(8):
    angle = (i / 8) * 2 * math.pi
    x = 5 * math.cos(angle)
    y = 5 * math.sin(angle)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, y, 415), segments=8, ring_count=4)
    crown_light = bpy.context.active_object
    crown_light.name = f'CrownLight_{i}'
    crown_light.data.materials.append(mat_crown_light)

# Add antenna light at top of spire
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 478), segments=8, ring_count=4)
antenna_light = bpy.context.active_object
antenna_light.name = 'AntennaLight'
antenna_light.data.materials.append(mat_crown_light)

# Add more stars
mat_star = bpy.data.materials.get('StarMat')
if not mat_star:
    mat_star = bpy.data.materials.new('StarMat')
    mat_star.use_nodes = True
    bsdf_st = mat_star.node_tree.nodes.get('Principled BSDF')
    bsdf_st.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_st.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_st.inputs['Emission Strength'].default_value = 30.0

random.seed(101)
for i in range(150):
    x = random.uniform(-600, 600)
    y = random.uniform(-600, 600)
    z = random.uniform(400, 1000)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(x, y, z), segments=8, ring_count=4)
    star = bpy.context.active_object
    star.name = f'Star3_{i}'
    star.data.materials.append(mat_star)

# Add moon glow (larger emissive sphere)
mat_moon_glow = bpy.data.materials.new('MoonGlow')
mat_moon_glow.use_nodes = True
bsdf_mg = mat_moon_glow.node_tree.nodes.get('Principled BSDF')
bsdf_mg.inputs['Base Color'].default_value = (0.8, 0.85, 1.0, 1.0)
bsdf_mg.inputs['Emission Color'].default_value = (0.8, 0.85, 1.0, 1.0)
bsdf_mg.inputs['Emission Strength'].default_value = 10.0
mat_moon_glow.blend_method = 'BLEND'
mat_moon_glow.show_transparent_back = False

bpy.ops.mesh.primitive_uv_sphere_add(radius=30, location=(-200, -300, 600), segments=16, ring_count=8)
moon_glow = bpy.context.active_object
moon_glow.name = 'MoonGlow'
moon_glow.data.materials.append(mat_moon_glow)

# Add airplane contrails (thin emissive lines)
mat_contrail = bpy.data.materials.new('ContrailMat')
mat_contrail.use_nodes = True
bsdf_ct = mat_contrail.node_tree.nodes.get('Principled BSDF')
bsdf_ct.inputs['Base Color'].default_value = (0.5, 0.5, 0.6, 1.0)
bsdf_ct.inputs['Emission Color'].default_value = (0.5, 0.5, 0.6, 1.0)
bsdf_ct.inputs['Emission Strength'].default_value = 5.0
mat_contrail.blend_method = 'BLEND'
mat_contrail.show_transparent_back = False

for i in range(10):
    angle = (i / 10) * 2 * math.pi
    x = 120 * math.cos(angle)
    y = 120 * math.sin(angle)
    z = 520 + 15 * math.sin(angle * 3)
    # Contrail behind plane
    for j in range(5):
        tx = x - 8 * (j+1) * math.cos(angle + math.pi/2)
        ty = y - 8 * (j+1) * math.sin(angle + math.pi/2)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=4, location=(tx, ty, z), vertices=6)
        contrail = bpy.context.active_object
        contrail.name = f'Contrail_{i}_{j}'
        contrail.rotation_euler = (0, math.radians(90), angle + math.pi/2)
        contrail.data.materials.append(mat_contrail)

print("Scene refined: camera fixed to wide shot, lighting boosted, atmosphere, crown lights, moon glow, contrails, more stars")
