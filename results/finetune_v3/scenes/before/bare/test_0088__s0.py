import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.object.select_all(action='DESELECT')

# ===================== MATERIALS =====================
def new_mat(name, color, metallic=0.0, roughness=0.8):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m

mat_marble   = new_mat("Marble",   (0.92, 0.90, 0.85, 1), roughness=0.55)
mat_bronze   = new_mat("Bronze",   (0.45, 0.28, 0.10, 1), metallic=1.0, roughness=0.35)
mat_stone    = new_mat("Stone",    (0.55, 0.52, 0.48, 1), roughness=0.9)
mat_grass    = new_mat("Grass",    (0.25, 0.45, 0.15, 1), roughness=0.95)
mat_rock     = new_mat("Rock",     (0.40, 0.38, 0.35, 1), roughness=0.95)
mat_sea      = new_mat("Sea",      (0.05, 0.25, 0.45, 1), roughness=0.15)
mat_dirt     = new_mat("Dirt",     (0.45, 0.35, 0.22, 1), roughness=0.95)
mat_flame    = new_mat("Flame",    (1.0, 0.6, 0.1, 1), roughness=0.4)
mat_flame.emission_color = (1.0, 0.5, 0.05, 1)
mat_flame.emission_strength = 8.0

# ===================== HELPERS =====================
def add_box(name, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj

def add_cyl(name, loc, radius, depth, mat, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

# ===================== SEA =====================
bpy.ops.mesh.primitive_plane_add(size=500, location=(0, -120, -2))
sea = bpy.context.active_object
sea.name = "Sea"
sea.data.materials.append(mat_sea)

# ===================== CAPE / GROUND =====================
# Main cape platform (stepped base under temple)
cape_loc = (0, 0, 0)

# Large cape ground
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 10, 0))
cape = bpy.context.active_object
cape.name = "Cape"
cape.scale = (1, 1.4, 1)
bpy.ops.object.transform_apply(scale=True)
cape.data.materials.append(mat_grass)

# Rocky cliff face on sea side (front, -Y)
for i in range(8):
    x = -15 + i * 4.5
    h = 4 + random.uniform(-1, 2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -18 + random.uniform(-1,1), -h/2 + 1))
    rock = bpy.context.active_object
    rock.scale = (3.5, 4, h)
    bpy.ops.object.transform_apply(scale=True)
    rock.rotation_euler[1] = random.uniform(-0.15, 0.15)
    rock.data.materials.append(mat_rock)

# ===================== STEPPED BASE (CREPIDOMA) =====================
# 3 steps, each 0.5m tall, shrinking inward
step_sizes = [(24, 16, 0.5), (22, 14, 0.5), (20, 12, 0.5)]
base_z = 0
for i, (sx, sy, sz) in enumerate(step_sizes):
    z = base_z + sz/2
    add_box(f"Step_{i}", (0, 0, z), (sx, sy, sz), mat_marble)
    base_z += sz

# Stylobate (top of steps)
stylobate_z = base_z + 0.25
add_box("Stylobate", (0, 0, stylobate_z), (19, 11, 0.5), mat_marble)

# ===================== DORIC COLUMNS (FLUTED) =====================
col_radius = 0.6
col_height = 5.0
num_cols_front = 6
num_cols_side = 8
col_spacing = 2.8

def make_fluted_column(name, loc, height, radius, mat):
    # Base (torus-like)
    bpy.ops.mesh.primitive_torus_add(location=(loc[0], loc[1], loc[2] + 0.15),
                                      major_radius=radius*1.15, minor_radius=0.12,
                                      major_segments=32, minor_segments=8)
    base = bpy.context.active_object
    base.name = name + "_base"
    base.data.materials.append(mat)

    # Fluted shaft: use cylinder with many verts and displace for fluting
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
                                        location=(loc[0], loc[1], loc[2] + 0.3 + height/2),
                                        vertices=24)
    shaft = bpy.context.active_object
    shaft.name = name + "_shaft"
    # Add fluting via simple deform or just keep as smooth cylinder for simplicity
    # Add subtle fluting: scale alternate verts
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(shaft.data)
    for v in bm.verts:
        angle = math.atan2(v.co.y, v.co.x)
        # 20 flutes
        flute = math.cos(angle * 20) * 0.03
        v.co.x += v.co.x * flute
        v.co.y += v.co.y * flute
    bm.to_mesh(shaft.data)
    bm.free()
    shaft.data.materials.append(mat)

    # Echinus + Abacus (capital)
    cap_z = loc[2] + 0.3 + height
    bpy.ops.mesh.primitive_cone_add(radius1=radius*1.3, radius2=radius*1.1,
                                     depth=0.3, location=(loc[0], loc[1], cap_z + 0.15),
                                     vertices=24)
    echinus = bpy.context.active_object
    echinus.name = name + "_echinus"
    echinus.data.materials.append(mat)

    add_box(name + "_abacus", (loc[0], loc[1], cap_z + 0.35),
            (radius*2.4, radius*2.4, 0.15), mat_marble)
    return shaft

# Front row (facing -Y, toward sea)
front_y = -5.0
for i in range(num_cols_front):
    x = -(num_cols_front - 1) * col_spacing / 2 + i * col_spacing
    make_fluted_column(f"Col_F{i}", (x, front_y, stylobate_z), col_height, col_radius, mat_marble)

# Back row
back_y = 5.0
for i in range(num_cols_front):
    x = -(num_cols_front - 1) * col_spacing / 2 + i * col_spacing
    make_fluted_column(f"Col_B{i}", (x, back_y, stylobate_z), col_height, col_radius, mat_marble)

# Side columns (left and right, excluding corners already placed)
side_x_left = -(num_cols_front - 1) * col_spacing / 2
side_x_right = (num_cols_front - 1) * col_spacing / 2
for i in range(1, num_cols_side - 1):
    y = -(num_cols_side - 1) * col_spacing / 2 + i * col_spacing
    make_fluted_column(f"Col_L{i}", (side_x_left, y, stylobate_z), col_height, col_radius, mat_marble)
    make_fluted_column(f"Col_R{i}", (side_x_right, y, stylobate_z), col_height, col_radius, mat_marble)

# ===================== ENTABLATURE (Architrave, Frieze, Cornice) =====================
ent_z = stylobate_z + 0.3 + col_height + 0.4

# Architrave
add_box("Architrave", (0, 0, ent_z), (19, 11, 0.6), mat_marble)

# Frieze with triglyphs
frieze_z = ent_z + 0.6 + 0.3
add_box("Frieze", (0, 0, frieze_z), (19, 11, 0.6), mat_marble)

# Triglyphs on front and back
trig_w = 0.5
trig_d = 0.4
for i in range(num_cols_front):
    x = -(num_cols_front - 1) * col_spacing / 2 + i * col_spacing
    add_box(f"Trig_F{i}", (x, front_y - 0.2, frieze_z), (trig_w, trig_d, 0.6), mat_marble)
    add_box(f"Trig_B{i}", (x, back_y + 0.2, frieze_z), (trig_w, trig_d, 0.6), mat_marble)

# Cornice
cornice_z = frieze_z + 0.6 + 0.2
add_box("Cornice", (0, 0, cornice_z), (20, 12, 0.4), mat_marble)

# ===================== PEDIMENTS (front and back triangles) =====================
def make_pediment(name, loc, width, height, depth, mat):
    # Create triangular prism
    mesh = bpy.data.meshes.new(name)
    verts = [
        (-width/2, -depth/2, 0),
        ( width/2, -depth/2, 0),
        (0, -depth/2, height),
        (-width/2,  depth/2, 0),
        ( width/2,  depth/2, 0),
        (0,  depth/2, height),
    ]
    faces = [
        (0, 1, 2),      # front
        (4, 3, 5),      # back
        (0, 3, 4, 1),   # bottom
        (0, 2, 5, 3),   # left
        (1, 4, 5, 2),   # right
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.data.materials.append(mat)
    return obj

ped_h = 2.5
make_pediment("Pediment_F", (0, front_y - 0.5, cornice_z + 0.4), 19, ped_h, 1.0, mat_marble)
make_pediment("Pediment_B", (0, back_y + 0.5, cornice_z + 0.4), 19, ped_h, 1.0, mat_marble)

# ===================== INTERIOR (cella walls - simple) =====================
# Back wall
add_box("Cella_Back", (0, 3.5, stylobate_z + col_height/2), (16, 0.5, col_height), mat_marble)
# Side walls
add_box("Cella_Left",  (-8, 0, stylobate_z + col_height/2), (0.5, 7, col_height), mat_marble)
add_box("Cella_Right", ( 8, 0, stylobate_z + col_height/2), (0.5, 7, col_height), mat_marble)

# ===================== BRONZE BRAZIER =====================
brazier_loc = (0, -2, stylobate_z)

# Base pedestal
add_box("Brazier_Pedestal", (brazier_loc[0], brazier_loc[1], brazier_loc[2] + 0.3),
        (1.2, 1.2, 0.6), mat_stone)

# Bowl
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(brazier_loc[0], brazier_loc[1], brazier_loc[2] + 1.0),
                                     segments=24, ring_count=12)
bowl = bpy.context.active_object
bowl.name = "Brazier_Bowl"
bowl.scale = (1, 1, 0.5)
bpy.ops.object.transform_apply(scale=True)
bowl.data.materials.append(mat_bronze)

# Flame
bpy.ops.mesh.primitive_cone_add(radius=0.3, depth=0.8,
                                 location=(brazier_loc[0], brazier_loc[1], brazier_loc[2] + 1.5),
                                 vertices=12)
flame = bpy.context.active_object
flame.name = "Brazier_Flame"
flame.scale = (1, 1, 1)
flame.data.materials.append(mat_flame)

# Point light for flame
light_data = bpy.data.lights.new("FlameLight", type='POINT')
light_data.energy = 50
light_data.color = (1.0, 0.5, 0.1)
light_data.shadow_soft_size = 0.3
light_obj = bpy.data.objects.new("FlameLight", light_data)
light_obj.location = (brazier_loc[0], brazier_loc[1], brazier_loc[2] + 1.5)
bpy.context.collection.objects.link(light_obj)

# ===================== GOAT PATH FROM SHORE =====================
# Winding path from sea (-Y) to temple steps
import mathutils
path_points = []
num_path_pts = 30
for i in range(num_path_pts):
    t = i / (num_path_pts - 1)
    # Start at shore (y=-25, z=0), end at temple steps (y=-8, z=0.5)
    y = -25 + t * 17
    x = math.sin(t * 3.5) * 2.5 * (1 - t * 0.5)  # winding, narrows toward temple
    z = 0.0 + t * 0.5  # slight rise
    path_points.append(Vector((x, y, z)))

# Create path as a series of small stone slabs
for i in range(len(path_points) - 1):
    p1 = path_points[i]
    p2 = path_points[i + 1]
    mid = (p1 + p2) / 2
    direction = (p2 - p1)
    length = direction.length
    angle = math.atan2(direction.y, direction.x)

    # Stone slab
    bpy.ops.mesh.primitive_cube_add(size=1, location=(mid.x, mid.y, mid.z + 0.05))
    slab = bpy.context.active_object
    slab.scale = (0.8, length/2 + 0.1, 0.1)
    slab.rotation_euler[2] = angle
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    slab.data.materials.append(mat_dirt)

    # Small rocks on sides
    if i % 3 == 0:
        for side in [-1, 1]:
            offset = Vector((-direction.y, direction.x, 0)).normalized() * 0.6 * side
            rock_loc = mid + offset
            bpy.ops.mesh.primitive_ico_sphere_add(radius=0.15, location=(rock_loc.x, rock_loc.y, rock_loc.z + 0.05),
                                                  subdivisions=1)
            r = bpy.context.active_object
            r.scale = (1, 1, 0.6)
            bpy.ops.object.transform_apply(scale=True)
            r.data.materials.append(mat_rock)

# ===================== LIGHTING - FIRST LIGHT (SUNRISE) =====================
# Remove default light if any
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Sun - low angle, warm golden
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_data.color = (1.0, 0.75, 0.4)
sun_data.angle = math.radians(5)
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects