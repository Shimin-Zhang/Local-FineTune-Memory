import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Helpers ---
def add_cylinder(name, radius, depth, location, rotation=(0,0,0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_box(name, size, location, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.scale = size
    obj.name = name
    bpy.ops.object.transform_apply(scale=True)
    return obj

def add_sphere(name, radius, location, segments=16, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=segments, rings=rings)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_rope(start, end, radius=0.08, segments=20):
    """Create a rope as a curve between two points."""
    curve_data = bpy.data.curves.new(name="rope", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 3
    spline = curve_data.splines.new('POLY')
    spline.points.add(segments)  # segments+1 points
    for i in range(segments + 1):
        t = i / segments
        # Slight sag
        p = start.lerp(end, t)
        sag = -0.3 * math.sin(math.pi * t)
        p.y += sag
        spline.points[i].co = (p.x, p.y, p.z, 1.0)
    obj = bpy.data.objects.new("rope", curve_data)
    bpy.context.collection.objects.link(obj)
    return obj

def add_ladder_spiral(trunk_location, trunk_radius, bottom_z, top_z, turns=3, rungs=20, radius_offset=0.15):
    """Add a spiral ladder wrapping around a trunk."""
    ladder_objects = []
    total_rungs = rungs * turns
    for i in range(total_rungs):
        t = i / total_rungs
        angle = t * turns * 2 * math.pi
        z = bottom_z + t * (top_z - bottom_z)
        r = trunk_radius + radius_offset
        x = trunk_location.x + r * math.cos(angle)
        y = trunk_location.y + r * math.sin(angle)
        # Rung
        rung = add_box("rung", (0.06, 0.4, 0.06), (x, y, z), rotation=(0, 0, angle))
        ladder_objects.append(rung)
    # Vertical ropes (sides)
    for side in [0, math.pi]:
        points = []
        for i in range(30):
            t = i / 29
            angle = t * turns * 2 * math.pi + side
            z = bottom_z + t * (top_z - bottom_z)
            r = trunk_radius + radius_offset
            x = trunk_location.x + r * math.cos(angle)
            y = trunk_location.y + r * math.sin(angle)
            points.append(Vector((x, y, z)))
        # Create rope along spiral
        curve_data = bpy.data.curves.new(name="ladder_rope", type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.03
        curve_data.bevel_resolution = 2
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(points) - 1)
        for i, p in enumerate(points):
            spline.points[i].co = (p.x, p.y, p.z, 1.0)
        obj = bpy.data.objects.new("ladder_rope", curve_data)
        bpy.context.collection.objects.link(obj)
        ladder_objects.append(obj)
    return ladder_objects

def add_platform(center, size=(2.0, 2.0, 0.15), rotation=(0,0,0)):
    """Add a wooden platform with planks."""
    platform = add_box("platform", size, center, rotation=rotation)
    # Add plank lines (visual detail)
    for i in range(5):
        offset = (i - 2) * 0.35
        plank = add_box("plank", (0.3, size[1] * 0.9, 0.02), (center.x + offset, center.y, center.z + size[2]/2 + 0.01), rotation=rotation)
    return platform

def add_tree_trunk(location, height, base_radius, top_radius):
    """Add a tapered tree trunk."""
    bpy.ops.mesh.primitive_cone_add(radius1=base_radius, radius2=top_radius, depth=height, vertices=24, location=(location[0], location[1], location[2] + height/2))
    trunk = bpy.context.active_object
    trunk.name = "trunk"
    return trunk

def add_tree_canopy(location, radius, height):
    """Add a canopy of spheres."""
    canopy_objs = []
    for i in range(15):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius * 0.7)
        x = location[0] + dist * math.cos(angle)
        y = location[1] + dist * math.sin(angle)
        z = location[2] + random.uniform(0, height)
        r = random.uniform(radius * 0.3, radius * 0.5)
        sphere = add_sphere("canopy", r, (x, y, z))
        canopy_objs.append(sphere)
    return canopy_objs

# --- Define Tree Positions ---
# Four trees in a rough square
tree_positions = [
    Vector((0, 0, 0)),
    Vector((15, 0, 0)),
    Vector((15, 15, 0)),
    Vector((0, 15, 0)),
]

# Platform heights (where bridges connect)
platform_heights = [12, 14, 13, 15]  # Varying heights

# --- Build Trees ---
for i, pos in enumerate(tree_positions):
    height = random.uniform(25, 35)
    base_r = random.uniform(1.2, 1.8)
    top_r = base_r * 0.4
    trunk = add_tree_trunk(pos, height, base_r, top_r)
    
    # Add some branches
    for b in range(4):
        branch_angle = random.uniform(0, 2 * math.pi)
        branch_z = random.uniform(height * 0.5, height * 0.9)
        branch_len = random.uniform(3, 6)
        bx = pos.x + branch_len * math.cos(branch_angle) * 0.5
        by = pos.y + branch_len * math.sin(branch_angle) * 0.5
        bz = branch_z + branch_len * 0.3
        branch = add_cylinder("branch", 0.15, branch_len, (bx, by, bz), rotation=(0, math.radians(30), branch_angle))
    
    # Canopy
    canopy = add_tree_canopy(Vector((pos.x, pos.y, height)), radius=random.uniform(4, 6), height=random.uniform(3, 5))

# --- Build Platforms ---
platforms = []
for i, (pos, h) in enumerate(zip(tree_positions, platform_heights)):
    # Platform at the base of the tree trunk area
    plat_center = Vector((pos.x, pos.y, h))
    plat = add_platform(plat_center, size=(2.5, 2.5, 0.2))
    platforms.append(plat_center)

# --- Build Rope Bridges between adjacent trees ---
bridge_pairs = [(0,1), (1,2), (2,3), (3,0)]
for i, j in bridge_pairs:
    p1 = platforms[i]
    p2 = platforms[j]
    # Main bridge deck (series of planks)
    segments = 15
    for s in range(segments):
        t = s / segments
        mid = p1.lerp(p2, t)
        # Sag
        sag = -0.8 * math.sin(math.pi * t)
        mid.y += sag
        angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
        plank = add_box("bridge_plank", (0.3, 1.5, 0.08), mid, rotation=(0, 0, angle))
    
    # Side ropes
    for side in [-0.7, 0.7]:
        start = Vector((p1.x, p1.y + side, p1.z + 0.5))
        end = Vector((p2.x, p2.y + side, p2.z + 0.5))
        rope = add_rope(start, end, radius=0.05, segments=25)
    
    # Handrail ropes
    for side in [-0.7, 0.7]:
        start = Vector((p1.x, p1.y + side, p1.z + 1.0))
        end = Vector((p2.x, p2.y + side, p2.z + 1.0))
        rope = add_rope(start, end, radius=0.04, segments=25)
    
    # Vertical ropes for handrails
    for s in range(0, segments, 2):
        t = s / segments
        mid = p1.lerp(p2, t)
        sag = -0.8 * math.sin(math.pi * t)
        mid.y += sag
        for side in [-0.7, 0.7]:
            vert_rope = add_cylinder("handrail", 0.03, 1.0, (mid.x, mid.y + side, mid.z + 0.5), rotation=(0,0,0))

# --- Add Spiral Ladders on each tree ---
for i, pos in enumerate(tree_positions):
    bottom_z = 2
    top_z = platform_heights[i]
    trunk_radius = 1.5
    add_ladder_spiral(pos, trunk_radius, bottom_z, top_z, turns=2, rungs=15, radius_offset=0.2)

# --- Add Mist at the Top ---
# Create mist using translucent spheres
mist_height = 28
for i in range(40):
    x = random.uniform(-5, 20)
    y = random.uniform(-5, 20)
    z = random.uniform(mist_height, mist_height + 8)
    r = random.uniform(2, 5)
    mist = add_sphere("mist", r, (x, y, z), segments=12, rings=6)
    # Make mist material translucent
    mat = bpy.data.materials.new(name="mist_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.85, 0.9, 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Transmission Weight"].default_value = 0.8
    bsdf.inputs["IOR"].default_value = 1.0
    mist.data.materials.append(mat)

# --- Add Ground ---
bpy.ops.mesh.primitive_plane_add(size=50, location=(7.5, 7.5, 0))
ground = bpy.context.active_object
ground.name = "ground"
ground_mat = bpy.data.materials.new(name="ground_mat")
ground_mat.use_nodes = True
bsdf = ground_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.15, 0.25, 0.1, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9
ground.data.materials.append(ground_mat)

# --- Add Lighting ---
# Sun
bpy.ops.object.light_add(type='SUN', location=(10, 10, 30))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Ambient fill
bpy.ops.object.light_add(type='POINT', location=(7.5, 7.5, 15))
fill = bpy.context.active_object
fill.data.energy = 500
fill.data.color = (0.8, 0.9, 1.0)

# --- Camera ---
bpy.ops.object.camera_add(location=(-5, -5, 10))
cam = bpy.context.active_object
cam.data.lens = 35
# Look at center
direction = Vector((7.5, 7.5, 12)) - cam.location
rot_quat = direction.to_track_quat('Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam

# --- World Background ---
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.4, 0.5, 0.6, 1.0)
bg.inputs["Strength"].default_value = 0.5

print("Canopy walkway built successfully!")
