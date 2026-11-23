import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Materials ---
def make_material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

mat_house_body = make_material("HouseBody", (0.9, 0.85, 0.75), roughness=0.6)
mat_roof = make_material("Roof", (0.35, 0.15, 0.1), roughness=0.7)
mat_chimney = make_material("Chimney", (0.5, 0.45, 0.4), roughness=0.8)
mat_door = make_material("Door", (0.2, 0.4, 0.2), roughness=0.5)
mat_window = make_material("Window", (0.7, 0.85, 0.95), metallic=0.3, roughness=0.2)
mat_porch = make_material("Porch", (0.8, 0.75, 0.65), roughness=0.6)
mat_ground = make_material("Ground", (0.3, 0.5, 0.25), roughness=0.9)
mat_town_house = make_material("TownHouse", (0.7, 0.65, 0.6), roughness=0.7)
mat_town_roof = make_material("TownRoof", (0.4, 0.2, 0.15), roughness=0.7)
mat_tree_trunk = make_material("TreeTrunk", (0.35, 0.2, 0.1), roughness=0.9)
mat_tree_leaves = make_material("TreeLeaves", (0.2, 0.5, 0.15), roughness=0.8)
mat_cloud = make_material("Cloud", (1.0, 1.0, 1.0), roughness=0.9)
mat_rope = make_material("Rope", (0.4, 0.3, 0.2), roughness=0.9)

# --- House ---
# Main body
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 5))
house_body = bpy.context.object
house_body.name = "HouseBody"
house_body.scale = (3, 4, 2.5)
bpy.ops.object.transform_apply(scale=True)
house_body.data.materials.append(mat_house_body)

# Roof (pyramid-ish using cone with 4 verts)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=4.5, radius2=0, depth=2.5, location=(0, 0, 8.25))
roof = bpy.context.object
roof.name = "Roof"
roof.rotation_euler[2] = math.radians(45)
roof.data.materials.append(mat_roof)

# Chimney
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, -1.5, 9.5))
chimney = bpy.context.object
chimney.name = "Chimney"
chimney.scale = (0.5, 0.5, 1.5)
bpy.ops.object.transform_apply(scale=True)
chimney.data.materials.append(mat_chimney)

# Chimney top
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, -1.5, 10.4))
chimney_top = bpy.context.object
chimney_top.name = "ChimneyTop"
chimney_top.scale = (0.6, 0.6, 0.3)
bpy.ops.object.transform_apply(scale=True)
chimney_top.data.materials.append(mat_chimney)

# Door
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.01, 4.5))
door = bpy.context.object
door.name = "Door"
door.scale = (0.8, 0.1, 1.2)
bpy.ops.object.transform_apply(scale=True)
door.data.materials.append(mat_door)

# Windows
window_positions = [
    (-1.5, 4.01, 5.5), (1.5, 4.01, 5.5),
    (-3.01, 0, 5.5), (3.01, 0, 5.5),
    (0, -4.01, 5.5),
]
for i, pos in enumerate(window_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    win = bpy.context.object
    win.name = f"Window_{i}"
    win.scale = (0.6, 0.1, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    win.data.materials.append(mat_window)

# Porch
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.8, 3.2))
porch = bpy.context.object
porch.name = "Porch"
porch.scale = (2, 1, 0.15)
bpy.ops.object.transform_apply(scale=True)
porch.data.materials.append(mat_porch)

# Porch pillars
for px in [-1.5, 1.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=2.5, location=(px, 4.8, 4.5))
    pillar = bpy.context.object
    pillar.name = f"Pillar_{px}"
    pillar.data.materials.append(mat_porch)

# --- Balloons ---
balloon_colors = [
    (1.0, 0.2, 0.2), (1.0, 0.6, 0.1), (1.0, 0.9, 0.2),
    (0.2, 0.8, 0.2), (0.2, 0.4, 0.9), (0.5, 0.2, 0.8),
    (0.9, 0.3, 0.6), (0.1, 0.8, 0.8), (0.8, 0.5, 0.1),
    (0.3, 0.7, 0.5), (0.7, 0.3, 0.3), (0.4, 0.4, 0.9),
]

balloon_positions = []
random.seed(42)
for i in range(3000):
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(0.5, 8)
    x = math.cos(angle) * radius + random.uniform(-1, 1)
    y = math.sin(angle) * radius + random.uniform(-1, 1)
    z = random.uniform(11, 22)
    balloon_positions.append((x, y, z))

# Use a single mesh with many balloon instances for performance
balloon_verts = []
balloon_faces = []
balloon_mats = []

# Create balloon geometry (UV sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, segments=16, ring_count=12, location=(0, 0, 0))
balloon_proto = bpy.context.object
balloon_proto.name = "BalloonProto"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Get balloon mesh data
balloon_mesh = balloon_proto.data
bpy.data.objects.remove(balloon_proto, do_unlink=True)

# Create instanced balloons
balloon_collection = bpy.data.collections.new("Balloons")
bpy.context.scene.collection.children.link(balloon_collection)

for i, pos in enumerate(balloon_positions):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.25, 0.4), segments=12, ring_count=8, location=pos)
    balloon = bpy.context.object
    balloon.name = f"Balloon_{i}"
    color = random.choice(balloon_colors)
    mat = make_material(f"BalloonMat_{i}", color, roughness=0.3)
    balloon.data.materials.append(mat)
    # Move to balloon collection
    for col in balloon.users_collection:
        col.objects.unlink(balloon)
    balloon_collection.objects.link(balloon)

# --- Ropes from chimney to balloons ---
chimney_top_pos = Vector((1.5, -1.5, 10.5))
rope_collection = bpy.data.collections.new("Ropes")
bpy.context.scene.collection.children.link(rope_collection)

for i, pos in enumerate(balloon_positions):
    if i % 3 == 0:  # Not every balloon gets a visible rope (performance)
        start = chimney_top_pos
        end = Vector(pos)
        mid = (start + end) / 2
        mid.z -= random.uniform(0.5, 2)  # Slight sag
        
        # Create curve for rope
        curve_data = bpy.data.curves.new(f"RopeCurve_{i}", 'CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.02
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(2)
        spline.bezier_points[0].co = start
        spline.bezier_points[0].handle_left_type = 'AUTO'
        spline.bezier_points[0].handle_right_type = 'AUTO'
        spline.bezier_points[1].co = mid
        spline.bezier_points[1].handle_left_type = 'AUTO'
        spline.bezier_points[1].handle_right_type = 'AUTO'
        spline.bezier_points[2].co = end
        spline.bezier_points[2].handle_left_type = 'AUTO'
        spline.bezier_points[2].handle_right_type = 'AUTO'
        
        rope_obj = bpy.data.objects.new(f"Rope_{i}", curve_data)
        rope_obj.data.materials.append(mat_rope)
        rope_collection.objects.link(rope_obj)

# --- Town below ---
town_collection = bpy.data.collections.new("Town")
bpy.context.scene.collection.children.link(town_collection)

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -5))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(mat_ground)
for col in ground.users_collection:
    col.objects.unlink(ground)
town_collection.objects.link(ground)

# Town houses
town_house_positions = []
for i in range(50):
    x = random.uniform(-30, 30)
    y = random.uniform(-30, 30)
    if abs(x) < 5 and abs(y) < 5:
        continue  # Skip area under the flying house
    town_house_positions.append((x, y))

for i, (x, y) in enumerate(town_house_positions):
    h = random.uniform(2, 5)
    w = random.uniform(2, 4)
    d = random.uniform(2, 4)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, -5 + h/2))
    th = bpy.context.object
    th.name = f"TownHouse_{i}"
    th.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    th.data.materials.append(mat_town_house)
    for col in th.users_collection:
        col.objects.unlink(th)
    town_collection.objects.link(th)
    
    # Town roof
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=max(w, d)*0.8, radius2=0, depth=1.5, location=(x, y, -5 + h + 0.75))
    tr = bpy.context.object
    tr.name = f"TownRoof_{i}"
    tr.rotation_euler[2] = math.radians(45)
    tr.data.materials.append(mat_town_roof)
    for col in tr.users_collection:
        col.objects.unlink(tr)
    town_collection.objects.link(tr)

# --- Trees ---
tree_collection = bpy.data.collections.new("Trees")
bpy.context.scene.collection.children.link(tree_collection)

for i in range(30):
    x = random.uniform(-40, 40)
    y = random.uniform(-40, 40)
    if abs(x) < 5 and abs(y) < 5:
        continue
    trunk_h = random.uniform(1.5, 3)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=trunk_h, location=(x, y, -5 + trunk_h/2))
    trunk = bpy.context.object
    trunk.name = f"TreeTrunk_{i}"
    trunk.data.materials.append(mat_tree_trunk)
    for col in trunk.users_collection:
        col.objects.unlink(trunk)
    tree_collection.objects.link(trunk)
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(1, 2), location=(x, y, -5 + trunk_h + 1))
    leaves = bpy.context.object
    leaves.name = f"TreeLeaves_{i}"
    leaves.data.materials.append(mat_tree_leaves)
    for col in leaves.users_collection:
        col.objects.unlink(leaves)
    tree_collection.objects.link(leaves)

# --- Clouds ---
cloud_collection = bpy.data.collections.new("Clouds")
bpy.context.scene.collection.children.link(cloud_collection)

for i in range(15):
    x = random.uniform(-50, 50)
    y = random.uniform(-50, 50)
    z = random.uniform(5, 25)
    for j in range(random.randint(3, 6)):
        ox = random.uniform(-2, 2)
        oy = random.uniform(-2, 2)
        oz = random.uniform(-0.5, 0.5)
        r = random.uniform(1, 2.5)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=16, ring_count=12, location=(x+ox, y+oy, z+oz))
        cloud = bpy.context.object
        cloud.name = f"Cloud_{i}_{j}"
        cloud.data.materials.append(mat_cloud)
        for col in cloud.users_collection:
            col.objects.unlink(cloud)
        cloud_collection.objects.link(cloud)

# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location = (15, 15, 12)
cam.rotation_euler = (math.radians(60), 0, math.radians(-45))
bpy.context.scene.camera = cam

# --- Lighting ---
# Sun
sun_data = bpy.data.lights.new("Sun", 'SUN')
sun_data.energy = 3
sun_data.color = (1.0, 0.95, 0.85)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(30))

# World
world = bpy.context.scene.world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs["Color"].default_value = (0.4, 0.6, 0.9, 1.0)
bg_node.inputs["Strength"].default_value = 1.0

# --- Render settings ---
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Scene built successfully!")
print(f"Total objects: {len(bpy.data.objects)}")
