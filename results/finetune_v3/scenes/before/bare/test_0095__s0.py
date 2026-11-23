import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Set units
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

# Camera
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (0, 25, 8)
cam.rotation_euler = Euler((math.radians(85), 0, 0))
scene.camera = cam
cam_data.lens = 35

# World
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.02, 0.08, 0.18, 1.0)
bg.inputs[1].default_value = 0.5

# Sun
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 2.0
sun_data.angle = math.radians(10)
sun = bpy.data.objects.new("Sun", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = Euler((math.radians(45), math.radians(10), math.radians(30)))

# Water surface (large plane with wave displacement)
water_mesh = bpy.data.meshes.new("Water")
water_obj = bpy.data.objects.new("Water", water_mesh)
scene.collection.objects.link(water_obj)
bpy.context.view_layer.objects.active = water_obj
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, size=200)
water_obj = bpy.context.active_object
water_obj.name = "Water"
water_obj.location = (0, 0, 0)
# Displace modifier for waves
tex = bpy.data.textures.new("WaterTex", 'CLOUDS')
tex.noise_scale = 5.0
disp = water_obj.modifiers.new("Displace", 'DISPLACE')
disp.texture = tex
disp.strength = 0.5
disp.mid_level = 0.5
# Material for water
water_mat = bpy.data.materials.new("WaterMat")
water_mat.use_nodes = True
nodes = water_mat.node_tree.nodes
links = water_mat.node_tree.links
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.0, 0.15, 0.35, 1.0)
bsdf.inputs["Roughness"].default_value = 0.1
bsdf.inputs["Transmission Weight"].default_value = 0.7
bsdf.inputs["IOR"].default_value = 1.33
water_obj.data.materials.append(water_mat)

# Boat hull (simple box)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5, 2))
hull = bpy.context.active_object
hull.name = "BoatHull"
hull.scale = (4, 8, 1.5)
hull_mat = bpy.data.materials.new("HullMat")
hull_mat.use_nodes = True
hull_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1.0)
hull.data.materials.append(hull_mat)

# Steel cage
cage_center = Vector((0, 0, -4))
cage_size = (2, 3, 2)  # x, y, z half-dimensions
bar_radius = 0.05
bar_count_x = 6
bar_count_y = 8
bar_count_z = 5

def make_bar(start, end, radius=0.05):
    length = (end - start).length
    if length < 1e-6:
        return
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(start + end) / 2)
    bar = bpy.context.active_object
    bar.name = "CageBar"
    bar.rotation_euler = (end - start).to_track_quat('Z', 'Y').to_euler()
    steel_mat = bpy.data.materials.get("SteelMat") or bpy.data.materials.new("SteelMat")
    if not steel_mat.use_nodes:
        steel_mat.use_nodes = True
    steel_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
    steel_mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
    steel_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.3
    bar.data.materials.append(steel_mat)
    return bar

# Vertical bars (along z)
for i in range(bar_count_x):
    for j in range(bar_count_y):
        x = -cage_size[0] + i * (2 * cage_size[0] / (bar_count_x - 1))
        y = -cage_size[1] + j * (2 * cage_size[1] / (bar_count_y - 1))
        start = cage_center + Vector((x, y, -cage_size[2]))
        end = cage_center + Vector((x, y, cage_size[2]))
        make_bar(start, end)

# Horizontal bars along x (at each z level and y position)
for k in range(bar_count_z):
    for j in range(bar_count_y):
        z = -cage_size[2] + k * (2 * cage_size[2] / (bar_count_z - 1))
        y = -cage_size[1] + j * (2 * cage_size[1] / (bar_count_y - 1))
        start = cage_center + Vector((-cage_size[0], y, z))
        end = cage_center + Vector((cage_size[0], y, z))
        make_bar(start, end)

# Horizontal bars along y (at each z level and x position)
for k in range(bar_count_z):
    for i in range(bar_count_x):
        z = -cage_size[2] + k * (2 * cage_size[2] / (bar_count_z - 1))
        x = -cage_size[0] + i * (2 * cage_size[0] / (bar_count_x - 1))
        start = cage_center + Vector((x, -cage_size[1], z))
        end = cage_center + Vector((x, cage_size[1], z))
        make_bar(start, end)

# Cables from hull to cage
cable_start = Vector((0, -5, 0.5))  # bottom of hull
cable_end = cage_center + Vector((0, 0, cage_size[2]))
for offset_x in [-0.5, 0.5]:
    s = cable_start + Vector((offset_x, 0, 0))
    e = cage_end + Vector((offset_x, 0, 0))
    make_bar(s, e, radius=0.03)

# Great white shark function
def make_shark(location, rotation, scale=1.0):
    # Body - elongated sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=location)
    body = bpy.context.active_object
    body.name = "SharkBody"
    body.scale = (scale * 0.3, scale * 1.2, scale * 0.25)
    # Apply scale
    bpy.ops.object.transform_apply(scale=True)
    # Shark material
    shark_mat = bpy.data.materials.new("SharkMat")
    shark_mat.use_nodes = True
    shark_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.4, 0.45, 0.5, 1.0)
    shark_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.4
    body.data.materials.append(shark_mat)

    # Dorsal fin
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.3, radius2=0, depth=0.8, location=location + Vector((0, 0, scale * 0.35)))
    fin = bpy.context.active_object
    fin.name = "DorsalFin"
    fin.scale = (scale * 0.4, scale * 0.8, scale * 0.6)
    fin.rotation_euler = Euler((math.radians(10), 0, 0))
    bpy.ops.object.transform_apply(scale=True)
    fin.data.materials.append(shark_mat)

    # Tail fin
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.25, radius2=0, depth=0.6, location=location + Vector((0, -scale * 1.1, 0)))
    tail = bpy.context.active_object
    tail.name = "TailFin"
    tail.scale = (scale * 0.5, scale * 0.3, scale * 0.5)
    tail.rotation_euler = Euler((0, math.radians(90), 0))
    bpy.ops.object.transform_apply(scale=True)
    tail.data.materials.append(shark_mat)

    # Pectoral fins
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.2, radius2=0, depth=0.5, location=location + Vector((side * scale * 0.35, scale * 0.3, -scale * 0.1)))
        pfin = bpy.context.active_object
        pfin.name = "PectoralFin"
        pfin.scale = (scale * 0.3, scale * 0.4, scale * 0.2)
        pfin.rotation_euler = Euler((math.radians(-30), 0, math.radians(45 * side)))
        bpy.ops.object.transform_apply(scale=True)
        pfin.data.materials.append(shark_mat)

    # Rotate entire shark
    body.rotation_euler = rotation
    for obj in [fin, tail, pfin]:
        obj.rotation_euler = rotation

    # Parent all to body
    for obj in [fin, tail, pfin]:
        obj.parent = body
        obj.matrix_parent_inverse = body.matrix_world.inverted()

    return body

# Two sharks passing by
shark1 = make_shark(
    location=Vector((-3, 3, -3)),
    rotation=Euler((0, math.radians(15), math.radians(30))),
    scale=1.5
)
shark2 = make_shark(
    location=Vector((4, -2, -5)),
    rotation=Euler((math.radians(-10), math.radians(20), math.radians(-60))),
    scale=1.2
)

# Bait lines (thin cylinders drifting)
bait_mat = bpy.data.materials.new("BaitMat")
bait_mat.use_nodes = True
bait_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.8, 0.7, 1.0)
bait_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5

for i in range(5):
    x = random.uniform(-2, 2)
    y = random.uniform(-1, 1)
    z_start = random.uniform(-2, -1)
    z_end = random.uniform(-6, -5)
    start = Vector((x, y, z_start))
    end = Vector((x + random.uniform(-0.3, 0.3), y + random.uniform(-0.3, 0.3), z_end))
    length = (end - start).length
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=length, location=(start + end) / 2)
    line = bpy.context.active_object
    line.name = f"BaitLine{i}"
    line.rotation_euler = (end - start).to_track_quat('Z', 'Y').to_euler()
    line.data.materials.append(bait_mat)
    # Bait at end
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=end)
    bait = bpy.context.active_object
    bait.name = f"Bait{i}"
    bait.data.materials.append(bait_mat)

# Final render settings
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# Set camera to look at cage
direction = cage_center - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

print("Scene created: steel cage hanging from boat hull, two great white sharks, bait lines in blue water.")
