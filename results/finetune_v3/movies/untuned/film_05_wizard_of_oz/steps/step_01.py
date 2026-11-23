import bpy
import math
import random
from mathutils import Vector

# Clean the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.data.meshes.remove_all()
bpy.data.materials.remove_all()
bpy.data.lights.remove_all()
bpy.data.cameras.remove_all()

# ============ MATERIALS ============
def create_material(name, color, roughness=0.5, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission > 0:
        bsdf.inputs['Emission Color'].default_value = color
        bsdf.inputs['Emission Strength'].default_value = emission
    return mat

# Core materials
mat_yellow_brick = create_material("YellowBrick", (1.0, 0.85, 0.1, 1.0), roughness=0.4)
mat_yellow_brick_dark = create_material("YellowBrickDark", (0.85, 0.7, 0.05, 1.0), roughness=0.5)
mat_green_emerald = create_material("EmeraldGreen", (0.0, 0.8, 0.3, 1.0), roughness=0.3, metallic=0.2)
mat_green_dark = create_material("EmeraldDark", (0.0, 0.5, 0.15, 1.0), roughness=0.4)
mat_sky = create_material("Sky", (0.4, 0.7, 1.0, 1.0), roughness=0.0, emission=0.5)
mat_grass = create_material("Grass", (0.2, 0.6, 0.1, 1.0), roughness=0.8)
mat_dorothy_dress = create_material("DorothyDress", (0.1, 0.3, 0.8, 1.0), roughness=0.6)
mat_dorothy_bow = create_material("DorothyBow", (0.8, 0.0, 0.0, 1.0), roughness=0.5)
mat_dorothy_hair = create_material("DorothyHair", (0.6, 0.3, 0.1, 1.0), roughness=0.7)
mat_dorothy_shoes = create_material("RubySlippers", (1.0, 0.0, 0.0, 1.0), roughness=0.2, metallic=0.3)
mat_scarecrow_body = create_material("ScarecrowBody", (0.9, 0.8, 0.5, 1.0), roughness=0.9)
mat_scarecrow_hat = create_material("ScarecrowHat", (0.6, 0.4, 0.2, 1.0), roughness=0.8)
mat_scarecrow_face = create_material("ScarecrowFace", (0.9, 0.7, 0.5, 1.0), roughness=0.7)
mat_tinman_body = create_material("TinManBody", (0.7, 0.7, 0.75, 1.0), roughness=0.2, metallic=0.9)
mat_tinman_hat = create_material("TinManHat", (0.6, 0.6, 0.65, 1.0), roughness=0.2, metallic=0.9)
mat_lion_body = create_material("LionBody", (0.8, 0.5, 0.1, 1.0), roughness=0.7)
mat_lion_manee = create_material("LionMane", (0.6, 0.35, 0.05, 1.0), roughness=0.8)
mat_lion_nose = create_material("LionNose", (0.3, 0.2, 0.1, 1.0), roughness=0.5)
mat_poppy_red = create_material("PoppyRed", (1.0, 0.0, 0.0, 1.0), roughness=0.4)
mat_poppy_stem = create_material("PoppyStem", (0.2, 0.5, 0.1, 1.0), roughness=0.7)
mat_poppy_leaf = create_material("PoppyLeaf", (0.1, 0.4, 0.05, 1.0), roughness=0.7)
mat_road_edge = create_material("RoadEdge", (0.7, 0.6, 0.2, 1.0), roughness=0.6)
mat_building_emerald = create_material("EmeraldBuilding", (0.0, 0.9, 0.4, 1.0), roughness=0.3, metallic=0.3)
mat_building_window = create_material("Window", (0.5, 0.9, 1.0, 1.0), roughness=0.1, emission=0.3)
mat_cloud = create_material("Cloud", (1.0, 1.0, 1.0, 1.0), roughness=0.9, emission=0.2)
mat_tree_trunk = create_material("TreeTrunk", (0.4, 0.25, 0.1, 1.0), roughness=0.8)
mat_tree_leaves = create_material("TreeLeaves", (0.1, 0.5, 0.1, 1.0), roughness=0.7)
mat_sky_gradient = create_material("SkyGradient", (0.3, 0.6, 1.0, 1.0), roughness=0.0, emission=0.8)

# ============ WORLD / SKY ============
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
wn = world.node_tree.nodes
wl = world.node_tree.links
for n in wn:
    wn.remove(n)
bg = wn.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.45, 0.7, 1.0, 1.0)
bg.inputs['Strength'].default_value = 1.0
out = wn.new('ShaderNodeOutputWorld')
wl.new(bg.outputs['Background'], out.inputs['Surface'])

# ============ GROUND ============
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(mat_grass)

# Subdivide ground for slight undulation
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')

# ============ YELLOW BRICK ROAD ============
# Road goes from y=-50 (near) to y=50 (far toward Emerald City)
road_length = 100
road_width = 4
brick_length = 1.5
brick_width = 1.0
num_bricks = int(road_length / brick_length)

road_bricks = []
for i in range(num_bricks):
    y = -road_length/2 + i * brick_length + brick_length/2
    # Alternate brick pattern
    if i % 2 == 0:
        offsets = [-1.5, -0.5, 0.5, 1.5]
    else:
        offsets = [-1.0, 0.0, 1.0]
    
    for j, ox in enumerate(offsets):
        # Skip if outside road width
        if abs(ox) > road_width/2:
            continue
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox, y, 0.05))
        brick = bpy.context.active_object
        brick.scale = (brick_width/2, brick_length/2, 0.05)
        brick.data.materials.append(mat_yellow_brick if (i+j) % 3 != 0 else mat_yellow_brick_dark)
        road_bricks.append(brick)

# Road edges
bpy.ops.mesh.primitive_cube_add(size=1, location=(-road_width/2 - 0.2, 0, 0.05))
edge_l = bpy.context.active_object
edge_l.scale = (0.3, road_length/2, 0.05)
edge_l.data.materials.append(mat_road_edge)

bpy.ops.mesh.primitive_cube_add(size=1, location=(road_width/2 + 0.2, 0, 0.05))
edge_r = bpy.context.active_object
edge_r.scale = (0.3, road_length/2, 0.05)
edge_r.data.materials.append(mat_road_edge)

# ============ POPPY FIELD ============
random.seed(42)
poppy_count = 300
for i in range(poppy_count):
    # Place poppies on both sides of the road
    side = random.choice([-1, 1])
    x = side * random.uniform(road_width/2 + 1, 15)
    y = random.uniform(-40, 40)
    
    # Stem
    stem_height = random.uniform(0.5, 1.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=stem_height, location=(x, y, stem_height/2))
    stem = bpy.context.active_object
    stem.data.materials.append(mat_poppy_stem)
    
    # Flower head
    head_z = stem_height + 0.08
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(x, y, head_z), segments=12, ring_count=8)
    head = bpy.context.active_object
    head.scale = (1, 1, 0.6)
    head.data.materials.append(mat_poppy_red)
    
    # Leaves
    for leaf_i in range(2):
        leaf_angle = random.uniform(0, 2*math.pi)
        leaf_x = x + 0.15 * math.cos(leaf_angle)
        leaf_y = y + 0.15 * math.sin(leaf_angle)
        leaf_z = stem_height * random.uniform(0.3, 0.7)
        bpy.ops.mesh.primitive_plane_add(size=0.3, location=(leaf_x, leaf_y, leaf_z))
        leaf = bpy.context.active_object
        leaf.rotation_euler = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(0, 2*math.pi))
        leaf.scale = (1, 0.6, 1)
        leaf.data.materials.append(mat_poppy_leaf)

# ============ EMERALD CITY (in the distance) ============
city_center_y = 55
city_x = 0

# Main castle tower
bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=12, location=(city_x, city_center_y, 6))
tower = bpy.context.active_object
tower.data.materials.append(mat_building_emerald)

# Tower top (cone)
bpy.ops.mesh.primitive_cone_add(radius1=3.2, radius2=0, depth=4, location=(city_x, city_center_y, 14))
tower_top = bpy.context.active_object
tower_top.data.materials.append(mat_building_emerald)

# Tower windows
for angle in range(0, 360, 45):
    rad = math.radians(angle)
    wx = city_x + 3.1 * math.cos(rad)
    wy = city_center_y + 3.1 * math.sin(rad)
    bpy.ops.mesh.primitive_cube_add(size=0.8, location=(wx, wy, 8))
    win = bpy.context.active_object
    win.scale = (0.4, 0.4, 0.8)
    win.data.materials.append(mat_building_window)

# Side buildings
for bx in [-8, 8, -15, 15, -5, 5]:
    bh = random.uniform(4, 8)
    bw = random.uniform(2, 4)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(city_x + bx, city_center_y + random.uniform(-3, 3), bh/2))
    bld = bpy.context.active_object
    bld.scale = (bw/2, bw/2, bh/2)
    bld.data.materials.append(mat_building_emerald)
    
    # Windows on building
    for wy in range(1, int(bh)-1, 2):
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(city_x + bx + bw/2 + 0.1, city_center_y, wy))
        w = bpy.context.active_object
        w.scale = (0.1, 0.3, 0.3)
        w.data.materials.append(mat_building_window)

# City gate (arch)
bpy.ops.mesh.primitive_torus_add(major_radius=4, minor_radius=0.5, location=(city_x, city_center_y - 10, 4))
gate = bpy.context.active_object
gate.data.materials.append(mat_building_emerald)

# Gate pillars
for gx in [-4, 4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=8, location=(city_x + gx, city_center_y - 10, 4))
    pillar = bpy.context.active_object
    pillar.data.materials.append(mat_building_emerald)

# ============ CLOUDS ============
for i in range(15):
    cx = random.uniform(-60, 60)
    cy = random.uniform(-40, 60)
    cz = random.uniform(25, 45)
    for j in range(3):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(2, 4), location=(cx + random.uniform(-3, 3), cy + random.uniform(-2, 2), cz + random.uniform(-1, 1)))
        cloud_part = bpy.context.active_object
        cloud_part.scale = (1, 0.6, 0.5)
        cloud_part.data.materials.append(mat_cloud)

# ============ TREES (scattered) ============
for i in range(20):
    side = random.choice([-1, 1])
    tx = side * random.uniform(18, 35)
    ty = random.uniform(-45, 45)
    
    # Trunk
    trunk_h = random.uniform(3, 6)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=trunk_h, location=(tx, ty, trunk_h/2))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_tree_trunk)
    
    # Canopy (multiple spheres)
    for k in range(4):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(1.5, 2.5), location=(tx + random.uniform(-1, 1), ty + random.uniform(-1, 1), trunk_h + random.uniform(0, 2)))
        canopy = bpy.context.active_object
        canopy.data.materials.append(mat_tree_leaves)

# ============ DOROTHY ============
def build_dorothy(x, y, z, scale=1.0):
    parts = []
    
    # Legs
    for lx in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08*scale, depth=0.5*scale, location=(x + lx*scale, y, z + 0.25*scale))
        leg = bpy.context.active_object
        leg.data.materials.append(mat_dorothy_dress)
        parts.append(leg)
    
    # Ruby slippers
    for lx in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cube_add(size=0.15*scale, location=(x + lx*scale, y + 0.05*scale, z + 0.03*scale))
        shoe = bpy.context.active_object
        shoe.scale = (1, 1.3, 0.5)
        shoe.data.materials.append(mat_dorothy_shoes)
        parts.append(shoe)
    
    # Dress (cone/cylinder)
    bpy.ops.mesh.primitive_cone_add(radius1=0.35*scale, radius2=0.2*scale, depth=0.6*scale, location=(x, y, z + 0.8*scale))
    dress = bpy.context.active_object
    dress.data.materials.append(mat_dorothy_dress)
    parts.append(dress)
    
    # Torso
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18*scale, depth=0.3*scale, location=(x, y, z + 1.25*scale))
    torso = bpy.context.active_object
    torso.data.materials.append(mat_dorothy_dress)
    parts.append(torso)
    
    # Arms
    for ax in [-0.25, 0.25]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05*scale, depth=0.4*scale, location=(x + ax*scale, y, z + 1.1*scale))
        arm = bpy.context.active_object
        arm.rotation_euler = (0, math.radians(20 if ax > 0 else -20), 0)
        arm.data.materials.append(mat_dorothy_dress)
        parts.append(arm)
    
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18*scale, location=(x, y, z + 1.55*scale))
    head = bpy.context.active_object
    head.data.materials.append(mat_dorothy_hair)
    parts.append(head)
    
    # Hair (pigtails)
    for px in [-0.2, 0.2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06*scale, depth=0.3*scale, location=(x + px*scale, y - 0.1*scale, z + 1.5*scale))
        pigtail = bpy.context.active_object
        pigtail.rotation_euler = (math.radians(-15), 0, 0)
        pigtail.data.materials.append(mat_dorothy_hair)
        parts.append(pigtail)
    
    # Red bow on head
    bpy.ops.mesh.primitive_cube_add(size=0.1*scale, location=(x, y - 0.15*scale, z + 1.7*scale))
    bow = bpy.context.active_object
    bow.scale = (1.5, 0.5, 0.8)
    bow.data.materials.append(mat_dorothy_bow)
    parts.append(bow)
    
    return parts

dorothy_parts = build_dorothy(-1.2, -15, 0.1, scale=1.2)

# ============ SCARECROW ============
def build_scarecrow(x, y, z, scale=1.0):
    parts = []
    
    # Pole (body support)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05*scale, depth=1.8*scale, location=(x, y, z + 0.9*scale))
    pole = bpy.context.active_object
    pole.data.materials.append(mat_scarecrow_hat)
    parts.append(pole)
    
    # Cross arm pole
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04*scale, depth=0.8*scale, location=(x, y, z + 1.3*scale))
    arm_pole = bpy.context.active_object
    arm_pole.rotation_euler = (0, math.radians(90), 0)
    arm_pole.data.materials.append(mat_scarecrow_hat)
    parts.append(arm_pole)
    
    # Body (patchwork)
    bpy.ops.mesh.primitive_cube_add(size=0.5*scale, location=(x, y, z + 0.8*scale))
    body = bpy.context.active_object
    body.scale = (1, 0.7, 1.2)
    body.data.materials.append(mat_scarecrow_body)
    parts.append(body)
    
    # Arms (stuffed)
    for ax in [-0.4, 0.4]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08*scale, depth=0.4*scale, location=(x + ax*scale, y, z + 1.2*scale))
        arm = bpy.context.active_object
        arm.rotation_euler = (0, math.radians(30 if ax > 0 else -30), 0)
        arm.data.materials.append(mat_scarecrow_body)
        parts.append(arm)
    
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22*scale, location=(x, y, z + 1.55*scale))
    head = bpy.context.active_object
    head.data.materials.append(mat_scarecrow_face)
    parts.append(head)
    
    # Hat (wide brim)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35*scale, depth=0.05*scale, location=(x, y, z + 1.7*scale))
    hat_brim = bpy.context.active_object
    hat_brim.data.materials.append(mat_scarecrow_hat)
    parts.append(hat_brim)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.2*scale, radius2=0.15*scale, depth=0.3*scale, location=(x, y, z + 1.85*scale))
    hat_top = bpy.context.active_object
    hat_top.data.materials.append(mat_scarecrow_hat)
    parts.append(hat_top)
    
    # Button eyes
    for ex in [-0.08, 0.08]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03*scale, location=(x + ex*scale, y + 0.18*scale, z + 1.58*scale))
        eye = bpy.context.active_object
        eye.data.materials.append(mat_scarecrow_hat)
        parts.append(eye)
    
    # Patch on body
    bpy.ops.mesh.primitive_cube_add(size=0.15*scale, location=(x + 0.1*scale, y + 0.2*scale, z + 0.8*scale))
    patch = bpy.context.active_object
    patch.scale = (1, 0.3, 1)
    patch.data.materials.append(mat_scarecrow_hat)
    parts.append(patch)
    
    return parts

scarecrow_parts = build_scarecrow(0.5, -12, 0.1, scale=1.3)

# ============ TIN MAN ============
def build_tinman(x, y, z, scale=1.0):
    parts = []
    
    # Legs
    for lx in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1*scale, depth=0.6*scale, location=(x + lx*scale, y, z + 0.3*scale))
        leg = bpy.context.active_object
        leg.data.materials.append(mat_tinman_body)
        parts.append(leg)
    
    # Feet
    for lx in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cube_add(size=0.2*scale, location=(x + lx*scale, y + 0.05*scale, z + 0.05*scale))
        foot = bpy.context.active_object
        foot.scale = (1, 1.5, 0.4)
        foot.data.materials.append(mat_tinman_body)
        parts.append(foot)
    
    # Body (torso)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25*scale, depth=0.6*scale, location=(x, y, z + 0.9*scale))
    torso = bpy.context.active_object
    torso.data.materials.append(mat_tinman_body)
    parts.append(torso)
    
    # Keyhole on chest
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05*scale, depth=0.02*scale, location=(x, y + 0.24*scale, z + 1.0*scale))
    keyhole = bpy.context.active_object
    keyhole.rotation_euler = (math.radians(90), 0, 0)
    keyhole.data.materials.append(mat_tinman_hat)
    parts.append(keyhole)
    
    # Arms
    for ax in [-0.3, 0.3]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07*scale, depth=0.5*scale, location=(x + ax*scale, y, z + 0.85*scale))
        arm = bpy.context.active_object
        arm.rotation_euler = (0, math.radians(15 if ax > 0 else -15), 0)
        arm.data.materials.append(mat_tinman_body)
        parts.append(arm)
    
    # Head (rounded)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2*scale, location=(x, y, z + 1.4*scale))
    head = bpy.context.active_object
    head.scale = (1, 1, 1.1)
    head.data.materials.append(mat_tinman_body)
    parts.append(head)
    
    # Funnel hat
    bpy.ops.mesh.primitive_cone_add(radius1=0.25*scale, radius2=0.05*scale, depth=0.35*scale, location=(x, y, z + 1.65*scale))
    hat = bpy.context.active_object
    hat.data.materials.append(mat_tinman_hat)
    parts.append(hat)
    
    # Eyes
    for ex in [-0.08, 0.08]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04*scale, location=(x + ex*scale, y + 0.18*scale, z + 1.42*scale))
        eye = bpy.context.active_object
        eye.data.materials.append(mat_tinman_hat)
        parts.append(eye)
    
    # Oil can in hand
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08*scale, depth=0.15*scale, location=(x + 0.4*scale, y + 0.1*scale, z + 0.6*scale))
    oil_can = bpy.context.active_object
    oil_can.data.materials.append(mat_tinman_body)
    parts.append(oil_can)
    
    # Oil can spout
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02*scale, depth=0.1*scale, location=(x + 0.4*scale, y + 0.1*scale + 0.1*scale, z + 0.65*scale))
    spout = bpy.context.active_object
    spout.rotation_euler = (math.radians(45), 0, 0)
    spout.data.materials.append(mat_tinman_body)
    parts.append(spout)
    
    return parts

tinman_parts = build_tinman(1.8, -10, 0.1, scale=1.2)

# ============ LION ============
def build_lion(x, y, z, scale=1.0):
    parts = []
    
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4*scale, location=(x, y, z + 0.4*scale))
    body = bpy.context.active_object
    body.scale = (1, 1.3, 0.8)
    body.data.materials.append(mat_lion_body)
    parts.append(body)
    
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25*scale, location=(x, y + 0.5*scale, z + 0.65*scale))
    head = bpy.context.active_object
    head.data.materials.append(mat_lion_body)
    parts.append(head)
    
    # Mane (multiple spheres around head)
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        mx = x + 0.25*scale * math.cos(rad)
        my = y + 0.5*scale + 0.25*scale * math.sin(rad)
        mz = z + 0.65*scale + 0.1*scale * math.sin(rad * 2)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12*scale, location=(mx, my, mz))
        mane_part = bpy.context.active_object
        mane_part.data.materials.append(mat_lion_manee)
        parts.append(mane_part)
    
    # Nose
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06*scale, location=(x, y + 0.75*scale, z + 0.6*scale))
    nose = bpy.context.active_object
    nose.data.materials.append(mat_lion_nose)
    parts.append(nose)
    
    # Eyes
    for ex in [-0.1, 0.1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04*scale, location=(x + ex*scale, y + 0.7*scale, z + 0.7*scale))
        eye = bpy.context.active_object
        eye.data.materials.append(mat_lion_nose)
        parts.append(eye)
    
    # Legs
    for lx in [-0.25, 0.25]:
        for ly in [-0.3, 0.3]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08*scale, depth=0.4*scale, location=(x + lx*scale, y + ly*scale, z + 0.2*scale))
            leg = bpy.context.active_object
            leg.data.materials.append(mat_lion_body)
            parts.append(leg)
    
    # Paws
    for lx in [-0.25, 0.25]:
        for ly in [-0.3, 0.3]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1*scale, location=(x + lx*scale, y + ly*scale + 0.05*scale, z + 0.05*scale))
            paw = bpy.context.active_object
            paw.scale = (1, 1.2, 0.5)
            paw.data.materials.append(mat_lion_body)
            parts.append(paw)
    
    # Tail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04*scale, depth=0.5*scale, location=(x, y - 0.5*scale, z + 0.4*scale))
    tail = bpy.context.active_object
    tail.rotation_euler = (math.radians(-30), 0, 0)
    tail.data.materials.append(mat_lion_body)
    parts.append(tail)
    
    # Tail tuft
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08*scale, location=(x, y - 0.7*scale, z + 0.25*scale))
    tuft = bpy.context.active_object
    tuft.data.materials.append(mat_lion_manee)
    parts.append(tuft)
    
    return parts

lion_parts = build_lion(-0.5, -7, 0.1, scale=1.0)

# ============ LIGHTING ============
# Sun
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun_data.energy = 3.0
sun_data.color = (1.0, 0.95, 0.8)
sun_obj = bpy.data.objects.new(name="Sun", object_data=sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(45), math.radians(20), 0)

# Fill light
fill_data = bpy.data.lights.new(name="Fill", type='AREA')
fill_data.energy = 100
fill_data.color = (0.8, 0.9, 1.0)
fill_obj = bpy.data.objects.new(name="Fill", object_data=fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (-20, -20, 15)
fill_obj.rotation_euler = (math.radians(45), 0, 0)

# Rim light for characters
rim_data = bpy.data.lights.new(name="Rim", type='AREA')
rim_data.energy = 50
rim_data.color = (1.0, 1.0, 0.9)
rim_obj = bpy.data.objects.new(name="Rim", object_data=rim_data)
bpy.context.collection.objects.link(rim_obj)
rim_obj.location = (0, -25, 10)
rim_obj.rotation_euler = (math.radians(60), 0, 0)

# ============ CAMERA ============
cam_data = bpy.data.cameras.new(name="MainCamera")
cam_data.lens = 50
cam_obj = bpy.data.objects.new(name="MainCamera", object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0, -25, 3)
cam_obj.rotation_euler = (math.radians(80), 0, 0)
bpy.context.scene.camera = cam_obj

# ============ ADDITIONAL DETAILS ============

# Distant hills
for i in range(8):
    hx = random.uniform(-80, 80)
    hy = random.uniform(60, 90)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(10, 20), location=(hx, hy, -5))
    hill = bpy.context.active_object
    hill.scale = (1, 1, 0.4)
    hill.data.materials.append(mat_grass)

# Scattered rocks
for i in range(30):
    side = random.choice([-1, 1])
    rx = side * random.uniform(road_width/2 + 2, 20)
    ry = random.uniform(-40, 40)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.2, 0.6), location=(rx, ry, 0.2))
    rock = bpy.context.active_object
    rock.scale = (random.uniform(0.8, 1.2), random.uniform(0.8, 1.2), random.uniform(0.5, 0.8))
    mat_rock = create_material("Rock", (0.5, 0.5, 0.5, 1.0), roughness=0.9)
    rock.data.materials.append(mat_rock)

# Fence posts along road (periodic)
for i in range(10):
    fy = -40 + i * 8
    for fx in [-road_width/2 - 1, road_width/2 + 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.0, location=(fx, fy, 0.5))
        post = bpy.context.active_object
        mat_fence = create_material("FenceWood", (0.5, 0.3