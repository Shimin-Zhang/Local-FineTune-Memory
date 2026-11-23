import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create collections
scene = bpy.context.scene
for col_name in ["Asteroid", "DrillRig", "OreHopper", "CargoPod", "CrewDome", "Lights"]:
    if col_name not in scene.collection.children:
        col = bpy.data.collections.new(col_name)
        scene.collection.children.link(col)

def get_col(name):
    return bpy.data.collections[name]

def add_to_col(obj, col_name):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    get_col(col_name).objects.link(obj)

# Helper: create mesh object
def create_obj(name, mesh_data, col_name):
    mesh = mesh_data
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    add_to_col(obj, col_name)
    return obj

# ==================== ASTEROID ====================
# Irregular rock shape
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=5.0, location=(0, 0, 0))
asteroid = bpy.context.active_object
asteroid.name = "Asteroid"
add_to_col(asteroid, "Asteroid")

# Deform with noise for rocky look
import bmesh
bm = bmesh.new()
bm.from_mesh(asteroid.data)
for v in bm.verts:
    # Add noise displacement
    n = random.uniform(-0.8, 0.8)
    v.co += v.co.normalized() * n
bm.to_mesh(asteroid.data)
bm.free()

# Smooth shading
bpy.ops.object.shade_smooth()

# Material for asteroid
mat_ast = bpy.data.materials.new("AsteroidMat")
mat_ast.use_nodes = True
nodes = mat_ast.node_tree.nodes
links = mat_ast.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.25, 0.22, 0.18, 1)
bsdf.inputs['Roughness'].default_value = 0.9
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
asteroid.data.materials.append(mat_ast)

# ==================== DRILL RIG ====================
# Main platform bolted to asteroid surface
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 5.2))
platform = bpy.context.active_object
platform.name = "DrillPlatform"
platform.scale = (3, 3, 0.3)
add_to_col(platform, "DrillRig")

# Platform material
mat_metal = bpy.data.materials.new("MetalMat")
mat_metal.use_nodes = True
nodes = mat_metal.node_tree.nodes
links = mat_metal.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.35, 1)
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.4
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
platform.data.materials.append(mat_metal)

# Support struts (4 legs)
for i, (x, y) in enumerate([(-2.5, -2.5), (2.5, -2.5), (-2.5, 2.5), (2.5, 2.5)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.0, location=(x, y, 4.0))
    strut = bpy.context.active_object
    strut.name = f"Strut_{i}"
    add_to_col(strut, "DrillRig")
    strut.data.materials.append(mat_metal)

# Drill tower
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 6.5))
tower = bpy.context.active_object
tower.name = "DrillTower"
tower.scale = (1.5, 1.5, 1.5)
add_to_col(tower, "DrillRig")
tower.data.materials.append(mat_metal)

# Drill bit (cone pointing down into asteroid)
bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0.1, depth=3.0, location=(0, 0, 3.5))
drill = bpy.context.active_object
drill.name = "DrillBit"
drill.rotation_euler = (math.pi, 0, 0)  # Point downward
add_to_col(drill, "DrillRig")
mat_drill = bpy.data.materials.new("DrillMat")
mat_drill.use_nodes = True
nodes = mat_drill.node_tree.nodes
links = mat_drill.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.55, 1)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.3
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
drill.data.materials.append(mat_drill)

# Hydraulic arms
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2.5, location=(side * 1.8, 0, 5.5))
    arm = bpy.context.active_object
    arm.name = f"HydraulicArm_{'L' if side < 0 else 'R'}"
    arm.rotation_euler = (0, math.radians(30 * side), 0)
    add_to_col(arm, "DrillRig")
    arm.data.materials.append(mat_metal)

# ==================== ORE HOPPER ====================
# Hopper body (inverted pyramid/frustum)
bpy.ops.mesh.primitive_cone_add(radius1=2.0, radius2=0.5, depth=2.0, location=(4, 0, 5.5))
hopper = bpy.context.active_object
hopper.name = "OreHopper"
hopper.rotation_euler = (math.pi, 0, 0)  # Invert so wide part is on top
add_to_col(hopper, "OreHopper")
mat_hopper = bpy.data.materials.new("HopperMat")
mat_hopper.use_nodes = True
nodes = mat_hopper.node_tree.nodes
links = mat_hopper.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.4, 0.35, 0.25, 1)
bsdf.inputs['Metallic'].default_value = 0.5
bsdf.inputs['Roughness'].default_value = 0.6
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
hopper.data.materials.append(mat_hopper)

# Hopper legs
for i, (x, y) in enumerate([(-1.5, -1.5), (1.5, -1.5), (-1.5, 1.5), (1.5, 1.5)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.5, location=(4 + x, y, 4.5))
    leg = bpy.context.active_object
    leg.name = f"HopperLeg_{i}"
    add_to_col(leg, "OreHopper")
    leg.data.materials.append(mat_metal)

# Conveyor from drill to hopper
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=4.0, location=(2, 0, 5.8))
conveyor = bpy.context.active_object
conveyor.name = "Conveyor"
conveyor.rotation_euler = (0, math.radians(90), 0)
add_to_col(conveyor, "OreHopper")
conveyor.data.materials.append(mat_metal)

# Ore particles (small spheres in hopper)
mat_ore = bpy.data.materials.new("OreMat")
mat_ore.use_nodes = True
nodes = mat_ore.node_tree.nodes
links = mat_ore.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.6, 0.4, 0.2, 1)
bsdf.inputs['Roughness'].default_value = 0.7
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

for i in range(20):
    x = 4 + random.uniform(-1.2, 1.2)
    y = random.uniform(-1.2, 1.2)
    z = 5.0 + random.uniform(0, 1.0)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.1, 0.25), location=(x, y, z))
    ore = bpy.context.active_object
    ore.name = f"Ore_{i}"
    add_to_col(ore, "OreHopper")
    ore.data.materials.append(mat_ore)

# ==================== CARGO POD ====================
# Tethered cargo pod floating nearby
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1.5, location=(8, 3, 2))
pod = bpy.context.active_object
pod.name = "CargoPod"
pod.scale = (1.2, 1.0, 0.8)
add_to_col(pod, "CargoPod")
mat_pod = bpy.data.materials.new("PodMat")
mat_pod.use_nodes = True
nodes = mat_pod.node_tree.nodes
links = mat_pod.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.75, 1)
bsdf.inputs['Metallic'].default_value = 0.6
bsdf.inputs['Roughness'].default_value = 0.3
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
pod.data.materials.append(mat_pod)

# Pod windows
for i in range(4):
    angle = i * math.pi / 2
    wx = 8 + math.cos(angle) * 1.4
    wy = 3 + math.sin(angle) * 1.0
    wz = 2
    bpy.ops.mesh.primitive_circle_add(vertices=16, radius=0.25, location=(wx, wy, wz))
    win = bpy.context.active_object
    win.name = f"PodWindow_{i}"
    win.rotation_euler = (0, angle + math.pi/2, 0)
    add_to_col(win, "CargoPod")
    mat_win = bpy.data.materials.new("WindowMat")
    mat_win.use_nodes = True
    nodes = mat_win.node_tree.nodes
    links = mat_win.node_tree.links
    nodes.clear()
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.1, 0.15, 0.2, 1)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.1
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    win.data.materials.append(mat_win)

# Tether cable (curve from asteroid to pod)
curve_data = bpy.data.curves.new("TetherCurve", 'CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.05
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(2)
spline.bezier_points[0].co = (5, 1, 4)
spline.bezier_points[0].handle_left = (5, 1, 4)
spline.bezier_points[0].handle_right = (6, 2, 3.5)
spline.bezier_points[1].co = (6.5, 2.5, 3.0)
spline.bezier_points[1].handle_left = (6, 2, 3.5)
spline.bezier_points[1].handle_right = (7.5, 2.8, 2.5)
spline.bezier_points[2].co = (8, 3, 2)
spline.bezier_points[2].handle_left = (7.5, 2.8, 2.5)
spline.bezier_points[2].handle_right = (8, 3, 2)
tether = bpy.data.objects.new("Tether", curve_data)
bpy.context.scene.collection.objects.link(tether)
add_to_col(tether, "CargoPod")
mat_tether = bpy.data.materials.new("TetherMat")
mat_tether.use_nodes = True
nodes = mat_tether.node_tree.nodes
links = mat_tether.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.2, 1)
bsdf.inputs['Roughness'].default_value = 0.5
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
tether.data.materials.append(mat_tether)

# ==================== CREW DOME ====================
# Cramped crew dome attached to asteroid
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1.8, location=(-6, -2, 3))
dome = bpy.context.active_object
dome.name = "CrewDome"
dome.scale = (1.0, 1.0, 0.9)
add_to_col(dome, "CrewDome")
mat_dome = bpy.data.materials.new("DomeMat")
mat_dome.use_nodes = True
nodes = mat_dome.node_tree.nodes
links = mat_dome.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.85, 1)
bsdf.inputs['Metallic'].default_value = 0.4
bsdf.inputs['Roughness'].default_value = 0.3
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
dome.data.materials.append(mat_dome)

# Dome windows (large front window)
bpy.ops.mesh.primitive_circle_add(vertices=24, radius=0.8, location=(-7.5, -2, 3))
dome_win = bpy.context.active_object
dome_win.name = "DomeWindow"
dome_win.rotation_euler = (0, math.radians(-90), 0)
add_to_col(dome_win, "CrewDome")
mat_dome_win = bpy.data.materials.new("DomeWindowMat")
mat_dome_win.use_nodes = True
nodes = mat_dome_win.node_tree.nodes
links = mat_dome_win.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.1, 0.15, 0.25, 1)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.05
out = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
dome_win.data.materials.append(mat_dome_win)

# Connecting tube from dome to asteroid
bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=3.0, location=(-4.5, -1.5, 3.5))
tube = bpy.context.active_object
tube.name = "DomeTube"
tube.rotation_euler = (0, math.radians(45), 0)
add_to_col(tube, "CrewDome")
tube.data.materials.append(mat_metal)

# Interior furniture (cramped)
# Small table
bpy.ops.mesh.primitive_cube_add(size=1, location=(-6.5, -2, 2.2))
table = bpy.context.active_object
table.name = "CrewTable"
table.scale = (0.5, 0.3, 0.05)
add_to_col(table, "CrewDome")
table.data.materials.append(mat_metal)

# Chair
bpy.ops.mesh.primitive_cube_add(size=1, location=(-5.5, -2, 2.0))
chair = bpy.context.active_object
chair.name = "CrewChair"
chair.scale = (0.3, 0.3, 0.5)
add_to_col(chair, "CrewDome")
chair.data.materials.append(mat_metal)

# ==================== LIGHTS ====================
# Interior light in crew dome (warm)
bpy.ops.object.light_add(type='POINT', location=(-6, -2, 3.5))
dome_light = bpy.context.active_object
dome_light.name = "DomeInteriorLight"
dome_light.data.energy = 50
dome_light.data.color = (1.0, 0.85, 0.6)
add_to_col(dome_light, "Lights")

# Drill area light (cool blue)
bpy.ops.object.light_add(type='POINT', location=(0, 0, 7.5))
drill_light = bpy.context.active_object
drill_light.name = "DrillLight"
drill_light.data.energy = 100
drill_light.data.color = (0.6, 0.8, 1.0)
add_to_col(drill_light, "Lights")

# Hopper area light
bpy.ops.object.light_add(type='POINT', location=(4, 0, 6.5))
hopper_light = bpy.context.active_object
hopper_light.name = "HopperLight"
hopper_light.data.energy = 60
hopper_light.data.color = (1.0, 0.9, 0.7)
add_to_col(hopper_light, "Lights")

# Pod light
bpy.ops.object.light_add(type='POINT', location=(8, 3, 3))
pod_light = bpy.context.active_object
pod_light.name = "PodLight"
pod_light.data.energy = 40
pod_light.data.color = (0.8, 0.9, 1.0)
add_to_col(pod_light, "Lights")

# Sun light for overall scene
bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 2.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)
add_to_col(sun, "Lights")

# World background (space)
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs['Color'].default_value = (0.02, 0.02, 0.05, 1)
    bg.inputs['Strength'].default_value = 1.0

# Set viewport shading
bpy.context.view_layer.shading.type = 'MATERIAL'

print("Asteroid mine scene created successfully!")
