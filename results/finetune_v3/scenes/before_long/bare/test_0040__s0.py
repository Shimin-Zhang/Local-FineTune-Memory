import bpy
import math
import random
from mathutils import Vector, noise

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set units
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# Create materials
def make_mat(name, color, rough=0.8, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat

# Autumn palette
mat_autumn_rock   = make_mat("AutumnRock",  (0.45, 0.25, 0.12, 1), rough=0.95)
mat_autumn_stone  = make_mat("AutumnStone", (0.55, 0.45, 0.35, 1), rough=0.90)
mat_autumn_wall   = make_mat("AutumnWall",  (0.40, 0.30, 0.20, 1), rough=0.95)
mat_autumn_wood   = make_mat("AutumnWood",  (0.35, 0.18, 0.08, 1), rough=0.85)
mat_autumn_roof   = make_mat("AutumnRoof",  (0.20, 0.10, 0.05, 1), rough=0.80)
mat_autumn_leaves = make_mat("AutumnLeaves",(0.85, 0.45, 0.10, 1), rough=0.70)
mat_autumn_leaves2= make_mat("AutumnLeaves2",(0.90, 0.55, 0.15, 1), rough=0.70)
mat_autumn_leaves3= make_mat("AutumnLeaves3",(0.75, 0.30, 0.08, 1), rough=0.70)
mat_autumn_fire   = make_mat("AutumnFire",  (1.0, 0.5, 0.1, 1), rough=0.5)
mat_autumn_fire.emission_color = (1.0, 0.4, 0.05, 1)
mat_autumn_fire.emission_strength = 3.0
mat_autumn_temple = make_mat("AutumnTemple",(0.60, 0.50, 0.35, 1), rough=0.85)
mat_autumn_ground = make_mat("AutumnGround",(0.50, 0.35, 0.15, 1), rough=0.95)

# ---- RIDGE LINE ----
# Define ridge as a series of points forming a mountainous contour
random.seed(42)
ridge_points = []
num_pts = 40
for i in range(num_pts):
    t = i / (num_pts - 1)
    angle = t * 2 * math.pi
    # Mountainous radius with noise
    r = 80 + 30 * math.sin(angle * 2) + 20 * math.cos(angle * 3) + 10 * noise.noise(Vector((t*5, 0, 0)))
    x = r * math.cos(angle)
    z = r * math.sin(angle)
    y = 20 + 15 * math.sin(angle * 1.5) + 10 * math.cos(angle * 2.5)
    ridge_points.append(Vector((x, y, z)))

# ---- GROUND / TERRAIN ----
# Create a large plane with displacement for terrain
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Terrain"
ground.data.materials.append(mat_autumn_ground)

# Subdivide and add displacement
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=50)
bpy.ops.object.mode_set(mode='OBJECT')

# Add displacement modifier
disp = ground.modifiers.new("Displace", 'DISPLACE')
texture = bpy.data.textures.new("TerrainNoise", type='CLOUDS')
texture.noise_scale = 50
texture.noise_depth = 4
disp.texture = texture
disp.strength = 30
disp.mid_level = 0.5

# ---- MOUNTAIN RIDGE (rocky formation) ----
# Create ridge as a thick mesh along the ridge points
# Build a ridge mesh: for each point, create a cross-section
ridge_mesh_verts = []
ridge_mesh_faces = []

ridge_width = 15
ridge_height = 25

for i, pt in enumerate(ridge_points):
    # Direction along ridge
    if i < len(ridge_points) - 1:
        direction = (ridge_points[i+1] - pt).normalized()
    else:
        direction = (pt - ridge_points[i-1]).normalized()
    # Perpendicular in XZ plane
    perp = Vector((-direction.z, 0, direction.x)).normalized()
    
    # Cross-section: a rough triangular/oval shape
    # Left side
    left = pt + perp * ridge_width + Vector((0, ridge_height * 0.3, 0))
    # Top
    top = pt + Vector((0, ridge_height, 0))
    # Right side
    right = pt - perp * ridge_width + Vector((0, ridge_height * 0.3, 0))
    # Base left
    base_left = pt + perp * ridge_width
    # Base right
    base_right = pt - perp * ridge_width
    # Base center
    base_center = pt
    
    idx = len(ridge_mesh_verts)
    ridge_mesh_verts.extend([
        base_left, base_center, base_right,
        left, top, right
    ])
    # Faces: bottom triangle
    ridge_mesh_faces.append((idx, idx+1, idx+2))
    # Left face
    ridge_mesh_faces.append((idx, idx+3, idx+1))
    # Top-left
    ridge_mesh_faces.append((idx+3, idx+4, idx+1))
    # Top-right
    ridge_mesh_faces.append((idx+4, idx+5, idx+2))
    # Right face
    ridge_mesh_faces.append((idx+5, idx+2, idx+1))

# Connect consecutive cross-sections
for i in range(len(ridge_points) - 1):
    a = i * 6
    b = (i + 1) * 6
    # Connect corresponding vertices
    for j in range(6):
        if j < 5:
            ridge_mesh_faces.append((a+j, b+j, b+(j+1), a+(j+1)))

# Create ridge mesh
ridge_data = bpy.data.meshes.new("RidgeMesh")
ridge_data.from_pydata(ridge_mesh_verts, [], ridge_mesh_faces)
ridge_data.update()
ridge_obj = bpy.data.objects.new("MountainRidge", ridge_data)
bpy.context.collection.objects.link(ridge_obj)
ridge_obj.data.materials.append(mat_autumn_rock)

# Smooth shading
for poly in ridge_obj.data.polygons:
    poly.use_smooth = True

# ---- STONE WALL ALONG RIDGE ----
# Wall follows the ridge line, elevated on the ridge
wall_height = 8
wall_thickness = 2
wall_segments = []

for i in range(len(ridge_points) - 1):
    p1 = ridge_points[i]
    p2 = ridge_points[i+1]
    mid = (p1 + p2) / 2
    direction = (p2 - p1).normalized()
    perp = Vector((-direction.z, 0, direction.x)).normalized()
    
    # Wall sits on top of ridge, offset to the outer side
    wall_base = mid + Vector((0, ridge_height * 0.8, 0))
    
    # Create wall segment as a box
    seg_len = (p2 - p1).length
    bpy.ops.mesh.primitive_cube_add(size=1, location=wall_base)
    wall_seg = bpy.context.active_object
    wall_seg.scale = (wall_thickness/2, wall_height/2, seg_len/2)
    # Rotate to align with direction
    rot_angle = math.atan2(direction.x, direction.z)
    wall_seg.rotation_euler = (0, 0, rot_angle)
    wall_seg.data.materials.append(mat_autumn_wall)
    wall_segments.append(wall_seg)

# Add battlements (crenellations) on top of wall
for i in range(len(ridge_points) - 1):
    p1 = ridge_points[i]
    p2 = ridge_points[i+1]
    mid = (p1 + p2) / 2
    direction = (p2 - p1).normalized()
    perp = Vector((-direction.z, 0, direction.x)).normalized()
    
    wall_top = mid + Vector((0, ridge_height * 0.8 + wall_height, 0))
    
    # Add merlons (raised parts)
    for j in range(3):
        offset = (j - 1) * 2
        merlon_pos = wall_top + perp * offset
        bpy.ops.mesh.primitive_cube_add(size=1, location=merlon_pos)
        merlon = bpy.context.active_object
        merlon.scale = (wall_thickness/2, 1.5, 0.8)
        rot_angle = math.atan2(direction.x, direction.z)
        merlon.rotation_euler = (0, 0, rot_angle)
        merlon.data.materials.append(mat_autumn_wall)

# ---- SOUTH GATE PAVILION ----
# Find the southernmost point on the ridge
south_idx = max(range(len(ridge_points)), key=lambda i: ridge_points[i].z)
south_pt = ridge_points[south_idx]
gate_base = south_pt + Vector((0, ridge_height * 0.8, 0))

# Gate tower - larger structure
bpy.ops.mesh.primitive_cube_add(size=1, location=gate_base + Vector((0, 6, 0)))
gate_tower = bpy.context.active_object
gate_tower.name = "SouthGateTower"
gate_tower.scale = (8, 12, 8)
gate_tower.data.materials.append(mat_autumn_stone)

# Gate arch opening (use a smaller dark cube to suggest the opening)
bpy.ops.mesh.primitive_cube_add(size=1, location=gate_base + Vector((0, 4, 0)))
gate_arch = bpy.context.active_object
gate_arch.name = "GateArch"
gate_arch.scale = (4, 5, 2)
mat_dark = make_mat("DarkGate", (0.1, 0.08, 0.05, 1), rough=0.9)
gate_arch.data.materials.append(mat_dark)

# Gate pavilion roof (pagoda style)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=10, radius2=2, depth=6, location=gate_base + Vector((0, 14, 0)))
gate_roof = bpy.context.active_object
gate_roof.name = "GateRoof"
gate_roof.rotation_euler = (0, 0, math.pi/4)
gate_roof.data.materials.append(mat_autumn_roof)

# Upper pavilion level
bpy.ops.mesh.primitive_cube_add(size=1, location=gate_base + Vector((0, 17, 0)))
gate_upper = bpy.context.active_object
gate_upper.name = "GateUpper"
gate_upper.scale = (5, 4, 5)
gate_upper.data.materials.append(mat_autumn_wood)

# Upper roof
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=7, radius2=1.5, depth=4, location=gate_base + Vector((0, 21, 0)))
gate_roof2 = bpy.context.active_object
gate_roof2.name = "GateRoof2"
gate_roof2.rotation_euler = (0, 0, math.pi/4)
gate_roof2.data.materials.append(mat_autumn_roof)

# ---- SIGNAL FIRE STATION ----
# Place on the eastern side of the ridge
east_idx = max(range(len(ridge_points)), key=lambda i: ridge_points[i].x)
east_pt = ridge_points[east_idx]
signal_base = east_pt + Vector((0, ridge_height * 0.8 + wall_height, 0))

# Signal tower
bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=10, location=signal_base + Vector((0, 5, 0)))
signal_tower = bpy.context.active_object
signal_tower.name = "SignalTower"
signal_tower.data.materials.append(mat_autumn_stone)

# Signal fire platform
bpy.ops.mesh.primitive_cylinder_add(radius=4, depth=1, location=signal_base + Vector((0, 10.5, 0)))
signal_platform = bpy.context.active_object
signal_platform.name = "SignalPlatform"
signal_platform.data.materials.append(mat_autumn_wood)

# Fire pit
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=0.5, location=signal_base + Vector((0, 11, 0)))
fire_pit = bpy.context.active_object
fire_pit.name = "FirePit"
fire_pit.data.materials.append(mat_dark)

# Fire (emissive)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=signal_base + Vector((0, 12, 0)))
fire = bpy.context.active_object
fire.name = "SignalFire"
fire.data.materials.append(mat_autumn_fire)

# Small roof over signal station
bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=5, radius2=1, depth=3, location=signal_base + Vector((0, 13, 0)))
signal_roof = bpy.context.active_object
signal_roof.name = "SignalRoof"
signal_roof.data.materials.append(mat_autumn_roof)

# ---- SMALL TEMPLE ----
# Place on the western side of the ridge
west_idx = min(range(len(ridge_points)), key=lambda i: ridge_points[i].x)
west_pt = ridge_points[west_idx]
temple_base = west_pt + Vector((0, ridge_height * 0.8 + wall_height, 0))

# Temple base platform
bpy.ops.mesh.primitive_cube_add(size=1, location=temple_base + Vector((0, 1, 0)))
temple_platform = bpy.context.active_object
temple_platform.name = "TemplePlatform"
temple_platform.scale = (10, 2, 10)
temple_platform.data.materials.append(mat_autumn_temple)

# Temple main structure
bpy.ops.mesh.primitive_cube_add(size=1, location=temple_base + Vector((0, 4, 0)))
temple_main = bpy.context.active_object
temple_main.name = "TempleMain"
temple_main.scale = (7, 5, 7)
temple_main.data.materials.append(mat_autumn_wood)

# Temple roof (traditional Asian style - curved)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=10, radius2=2, depth=5, location=temple_base + Vector((0, 9, 0)))
temple_roof = bpy.context.active_object
temple_roof.name = "TempleRoof"
temple_roof.rotation_euler = (0, 0, math.pi/4)
temple_roof.data.materials.append(mat_autumn_roof)

# Temple upper tier
bpy.ops.mesh.primitive_cube_add(size=1, location=temple_base + Vector((0, 11, 0)))
temple_upper = bpy.context.active_object
temple_upper.name = "TempleUpper"
temple_upper.scale = (5, 3, 5)
temple_upper.data.materials.append(mat_autumn_wood)

# Temple upper roof
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=7, radius2=1.5, depth=3, location=temple_base + Vector((0, 14, 0)))
temple_roof2 = bpy.context.active_object
temple_roof2.name = "TempleRoof2"
temple_roof2.rotation_euler = (0, 0, math.pi/4)
temple_roof2.data.materials.append(mat_autumn_roof)

# Temple finial
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.5, radius2=0.1, depth=2, location=temple_base + Vector((0, 16, 0)))
temple_finial = bpy.context.active_object
temple_finial.name = "TempleFinial"
temple_finial.data.materials.append(mat_autumn_stone)

# ---- AUTUMN TREES ----
# Scatter autumn-colored trees around the fortress
def create_autumn_tree(location, scale=1.0):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3*scale, depth=3*scale, location=location + Vector((0, 1.5*scale, 0)))
    trunk = bpy.context.active_object
    trunk.name = "TreeTrunk"
    trunk.data.materials.append(mat_autumn_wood)
    
    # Foliage - multiple spheres for autumn canopy
    foliage_mats = [mat_autumn_leaves, mat_autumn_leaves2, mat_autumn_leaves3]
    for i in range(5):
        offset = Vector((
            random.uniform(-1.5, 1.5) * scale,
            random.uniform(2, 4) * scale,
            random.uniform(-1.5, 1.5) * scale
        ))
        r = random.uniform(1.0, 2.0) * scale
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=location + offset)
        foliage = bpy.context.active_object
        foliage.name = "TreeFoliage"
        foliage.data.materials.append(random.choice(foliage_mats))
        for poly in foliage.data.polygons:
            poly.use_smooth = True

# Place trees around the ridge
for i in range(30):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(100, 180)
    x = dist * math.cos(angle)
    z = dist * math.sin(angle)
    # Estimate ground height
    y = 5 + 10 * math.sin(angle * 1.5) + 5 * math.cos(angle * 2.5)
    tree_loc = Vector((x, y, z))
    create_autumn_tree(tree_loc, scale=random.uniform(0.8, 1.5))

# Some trees on the ridge itself (smaller)
for i in range(10):
    pt = random.choice(ridge_points)
    tree_loc = pt + Vector((random.uniform(-5, 5), ridge_height * 0.5, random.uniform(-5, 5)))
    create_autumn_tree(tree_loc, scale=random.uniform(0.5, 0.8))

# ---- LIGHTING ----
# Sun light (warm autumn sun)
bpy.ops.object.light_add(type='SUN', location=(50, 80, 50))
sun = bpy.context.active_object
sun.name = "AutumnSun"
sun.data.energy = 3.0
sun.data.color = (1.0, 0.85, 0.6)
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Ambient light
bpy.ops.object.light_add(type='AREA', location=(0, 100, 0))
ambient = bpy.context.active_object
ambient.name = "AmbientLight"
ambient.data.energy = 50
ambient.data.color = (1.0, 0.9, 0.8)
ambient.data.size = 200

# ---- CAMERA ----
bpy.ops.object.camera_add(location=(150, 60, 150))
camera = bpy.context.active_object
camera.name = "MainCamera"
scene.camera = camera

# Point camera at the fortress center
target = Vector((0, 20, 0))
direction = target - camera.location
rot_quat = direction.to_track_quat('Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# ---- WORLD BACKGROUND (autumn sky) ----
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.85, 0.75, 0.6, 1)  # Warm autumn sky
bg.inputs[1].default_value = 1.0

# Render settings
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

print("Mountain fortress scene created successfully!")
print(f"Objects in scene: {len(bpy.data.objects)}")
