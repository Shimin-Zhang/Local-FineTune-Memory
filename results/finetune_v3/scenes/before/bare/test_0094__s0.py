import bpy
import math
import mathutils
from mathutils import Vector

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Scene Setup ---
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# --- World / Environment ---
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

bg_node = nodes.new('ShaderNodeBackground')
bg_node.inputs['Color'].default_value = (0.02, 0.08, 0.15, 1.0)  # Deep blue water
bg_node.inputs['Strength'].default_value = 0.5
out_node = nodes.new('ShaderNodeOutputWorld')
links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])

# Add a sun for the light rays
sun_node = nodes.new('ShaderNodeLightPath')
links.new(sun_node.outputs['Is Camera Ray'], bg_node.inputs['Strength'])

# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# Position camera looking down the slope
cam.location = (5, -15, 12)
cam.rotation_euler = (math.radians(70), 0, math.radians(15))

# --- Sandy Slope ---
# Create a plane and deform it into a slope
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
slope = bpy.context.active_object
slope.name = "SandySlope"

# Add subdivision for deformation
mod = slope.modifiers.new("Subsurf", 'SUBSURF')
mod.levels = 4
mod.render_levels = 4

# Apply a wave/slope deform
bpy.ops.object.transform_apply(location=False, rotation=False, scale=False)
# Manually displace vertices to create a slope
me = slope.data
for v in me.vertices:
    # Create a gentle slope: higher at +X, lower at -X
    z = v.co.x * 0.15 + math.sin(v.co.x * 0.5) * 0.5 + math.cos(v.co.y * 0.3) * 0.3
    v.co.z = z

# Smooth shading
bpy.ops.object.shade_smooth()

# Sandy material
sand_mat = bpy.data.materials.new("Sand")
sand_mat.use_nodes = True
nodes_s = sand_mat.node_tree.nodes
links_s = sand_mat.node_tree.links
nodes_s.clear()

bsdf_s = nodes_s.new('ShaderNodeBsdfPrincipled')
bsdf_s.inputs['Base Color'].default_value = (0.7, 0.6, 0.4, 1.0)
bsdf_s.inputs['Roughness'].default_value = 0.9
bsdf_s.inputs['Subsurface Weight'].default_value = 0.1
out_s = nodes_s.new('ShaderNodeOutputMaterial')
links_s.new(bsdf_s.outputs['BSDF'], out_s.inputs['Surface'])

slope.data.materials.append(sand_mat)

# --- Thick Cable ---
# Create a curve for the cable path along the slope
cable_curve_data = bpy.data.curves.new("CableCurve", 'CURVE')
cable_curve_data.dimensions = '3D'
cable_curve_data.bevel_depth = 0.3
cable_curve_data.bevel_resolution = 8
cable_curve_data.fill_mode = 'FULL'

# Define cable path: from upper slope down toward the ROV
spline = cable_curve_data.splines.new('BEZIER')
spline.bezier_points.add(4)

# Points along the slope
points = [
    (15, -5, 4.5),   # Start: high on slope
    (8, -3, 2.5),    # 
    (2, -1, 1.0),    # 
    (-5, 1, -0.5),   # 
    (-12, 3, -2.0),  # End: near ROV
]

for i, pt in enumerate(points):
    bp = spline.bezier_points[i]
    bp.co = pt
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'

cable = bpy.data.objects.new("ThickCable", cable_curve_data)
scene.collection.objects.link(cable)

# Cable material: dark rubber
cable_mat = bpy.data.materials.new("CableRubber")
cable_mat.use_nodes = True
nodes_c = cable_mat.node_tree.nodes
links_c = cable_mat.node_tree.links
nodes_c.clear()

bsdf_c = nodes_c.new('ShaderNodeBsdfPrincipled')
bsdf_c.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
bsdf_c.inputs['Roughness'].default_value = 0.7
out_c = nodes_c.new('ShaderNodeOutputMaterial')
links_c.new(bsdf_c.outputs['BSDF'], out_c.inputs['Surface'])

cable.data.materials.append(cable_mat)

# --- ROV (Remotely Operated Vehicle) ---
# Simple box-based ROV
rov_parts = []

# Main body
bpy.ops.mesh.primitive_cube_add(size=1, location=(-10, 2, -1.5))
rov_body = bpy.context.active_object
rov_body.scale = (2, 1.5, 1)
rov_body.name = "ROV_Body"
rov_parts.append(rov_body)

# Frame struts
for x_off in [-0.8, 0.8]:
    for y_off in [-0.6, 0.6]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.2, location=(-10 + x_off, 2 + y_off, -1.5))
        strut = bpy.context.active_object
        strut.rotation_euler = (0, 0, 0)
        strut.name = f"ROV_Strut_{x_off}_{y_off}"
        rov_parts.append(strut)

# Thrusters (small cylinders on sides)
for x_off in [-1.2, 1.2]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(-10 + x_off, 2, -1.5))
    thruster = bpy.context.active_object
    thruster.rotation_euler = (0, math.radians(90), 0)
    thruster.name = f"ROV_Thruster_{x_off}"
    rov_parts.append(thruster)

# Camera housing on front
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(-11.5, 2, -1.2))
cam_housing = bpy.context.active_object
cam_housing.name = "ROV_CameraHousing"
rov_parts.append(cam_housing)

# Combine ROV parts
bpy.ops.object.select_all(action='DESELECT')
for part in rov_parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = rov_body
bpy.ops.object.join()
rov = bpy.context.active_object
rov.name = "ROV"
bpy.ops.object.shade_smooth()

# ROV material: metallic
rov_mat = bpy.data.materials.new("ROV_Metal")
rov_mat.use_nodes = True
nodes_r = rov_mat.node_tree.nodes
links_r = rov_mat.node_tree.links
nodes_r.clear()

bsdf_r = nodes_r.new('ShaderNodeBsdfPrincipled')
bsdf_r.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)
bsdf_r.inputs['Metallic'].default_value = 0.8
bsdf_r.inputs['Roughness'].default_value = 0.3
out_r = nodes_r.new('ShaderNodeOutputMaterial')
links_r.new(bsdf_r.outputs['BSDF'], out_r.inputs['Surface'])

rov.data.materials.append(rov_mat)

# --- ROV Lamp (Spot Light) ---
lamp_data = bpy.data.lights.new("ROV_Lamp", 'SPOT')
lamp_data.energy = 500
lamp_data.color = (1.0, 0.95, 0.8)
lamp_data.spot_size = math.radians(60)
lamp_data.spot_blend = 0.3
lamp_data.shadow_soft_size = 0.5

lamp = bpy.data.objects.new("ROV_Lamp", lamp_data)
scene.collection.objects.link(lamp)
lamp.location = (-11.5, 2, -1.0)
lamp.rotation_euler = (math.radians(-90), 0, math.radians(180))  # Pointing forward/down

# --- Fish Caught in Lamp Beam ---
# Create a few simple fish shapes
def create_fish(location, scale=1.0, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0, depth=0.6, location=location)
    fish = bpy.context.active_object
    fish.scale = (scale, scale * 0.5, scale)
    fish.rotation_euler = rotation
    fish.name = "Fish"
    
    # Add tail
    bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0, depth=0.3, location=(location[0] + 0.35 * scale, location[1], location[2]))
    tail = bpy.context.active_object
    tail.scale = (scale, scale * 0.8, scale)
    tail.rotation_euler = (0, math.radians(90), 0)
    
    # Join
    bpy.ops.object.select_all(action='DESELECT')
    fish.select_set(True)
    tail.select_set(True)
    bpy.context.view_layer.objects.active = fish
    bpy.ops.object.join()
    bpy.ops.object.shade_smooth()
    return fish

# Fish positions near the lamp beam
fish_positions = [
    (-13, 1.5, -0.8),
    (-12.5, 2.5, -1.0),
    (-13.5, 2.0, -0.5),
    (-12.8, 1.8, -1.2),
]

for i, pos in enumerate(fish_positions):
    rot = (math.radians(180), math.radians(10 * i), math.radians(20 * i))
    fish = create_fish(pos, scale=0.8 + 0.1 * i, rotation=rot)
    fish.name = f"Fish_{i}"
    
    # Fish material
    fish_mat = bpy.data.materials.new(f"FishMat_{i}")
    fish_mat.use_nodes = True
    nodes_f = fish_mat.node_tree.nodes
    links_f = fish_mat.node_tree.links
    nodes_f.clear()
    
    bsdf_f = nodes_f.new('ShaderNodeBsdfPrincipled')
    # Vary fish colors slightly
    colors = [(0.6, 0.4, 0.2, 1.0), (0.5, 0.5, 0.3, 1.0), (0.7, 0.5, 0.3, 1.0), (0.4, 0.5, 0.4, 1.0)]
    bsdf_f.inputs['Base Color'].default_value = colors[i % len(colors)]
    bsdf_f.inputs['Roughness'].default_value = 0.4
    bsdf_f.inputs['Subsurface Weight'].default_value = 0.2
    out_f = nodes_f.new('ShaderNodeOutputMaterial')
    links_f.new(bsdf_f.outputs['BSDF'], out_f.inputs['Surface'])
    
    fish.data.materials.append(fish_mat)

# --- Light Rays (Volumetric) ---
# Add a volumetric cube to simulate water and light rays
bpy.ops.mesh.primitive_cube_add(size=60, location=(0, 0, 0))
water_vol = bpy.context.active_object
water_vol.name = "WaterVolume"
water_vol.display_type = 'WIRE'

# Volumetric material
vol_mat = bpy.data.materials.new("WaterVolume")
vol_mat.use_nodes = True
nodes_v = vol_mat.node_tree.nodes
links_v = vol_mat.node_tree.links
nodes_v.clear()

vol_principled = nodes_v.new('ShaderNodeVolumePrincipled')
vol_principled.inputs['Color'].default_value = (0.1, 0.3, 0.5, 1.0)
vol_principled.inputs['Density'].default_value = 0.02
vol_principled.inputs['Anisotropy'].default_value = 0.3
out_v = nodes_v.new('ShaderNodeOutputMaterial')
links_v.new(vol_principled.outputs['Volume'], out_v.inputs['Volume'])

water_vol.data.materials.append(vol_mat)

# Add a strong directional light from above to create rays
sun_light_data = bpy.data.lights.new("Sun", 'SUN')
sun_light_data.energy = 5
sun_light_data.angle = math.radians(10)
sun_light_data.color = (0.8, 0.9, 1.0)

sun_light = bpy.data.objects.new("Sun", sun_light_data)
scene.collection.objects.link(sun_light)
sun_light.rotation_euler = (math.radians(30), math.radians(10), math.radians(0))

# --- Ship Above (Simple silhouette) ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(20, -10, 25))
ship = bpy.context.active_object
ship.scale = (8, 3, 2)
ship.name = "Ship"

# Add a simple mast
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=5, location=(20, -10, 28))
mast = bpy.context.active_object
mast.name = "Ship_Mast"

# Ship material
ship_mat = bpy.data.materials.new("Ship_Metal")
ship_mat.use_nodes = True
nodes_sh = ship_mat.node_tree.nodes
links_sh = ship_mat.node_tree.links
nodes_sh.clear()

bsdf_sh = nodes_sh.new('ShaderNodeBsdfPrincipled')
bsdf_sh.inputs['Base Color'].default_value = (0.2, 0.2, 0.25, 1.0)
bsdf_sh.inputs['Metallic'].default_value = 0.5
bsdf_sh.inputs['Roughness'].default_value = 0.6
out_sh = nodes_sh.new('ShaderNodeOutputMaterial')
links_sh.new(bsdf_sh.outputs['BSDF'], out_sh.inputs['Surface'])

ship.data.materials.append(ship_mat)
mast.data.materials.append(ship_mat)

# --- Final Adjustments ---
# Set render film to transparent off (we want the water background)
scene.render.film_transparent = False

# Enable volumetric rendering
scene.cycles.volume_bounces = 2
scene.cycles.volume_step_rate = 1.0
scene.cycles.volume_max_steps = 256

# Print summary
print("Scene created: Sandy slope, thick cable, ROV with lamp, fish in beam, light rays, ship above.")
