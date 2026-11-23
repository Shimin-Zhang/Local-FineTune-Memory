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
def create_material(name, color, metallic=0.0, roughness=0.8, specular=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Specular IOR Level'].default_value = specular
    return mat

# Materials
mat_black_stone = create_material("BlackStone", (0.05, 0.05, 0.05, 1.0), metallic=0.1, roughness=0.9)
mat_corrugated = create_material("CorrugatedIron", (0.3, 0.35, 0.4, 1.0), metallic=0.7, roughness=0.4)
mat_ash = create_material("Ash", (0.6, 0.6, 0.6, 1.0), metallic=0.0, roughness=1.0)
mat_crater = create_material("CraterRock", (0.15, 0.1, 0.08, 1.0), metallic=0.0, roughness=1.0)
mat_lava = create_material("Lava", (1.0, 0.3, 0.05, 1.0), metallic=0.0, roughness=0.3)
mat_pole = create_material("PoleWood", (0.3, 0.2, 0.1, 1.0), metallic=0.0, roughness=0.9)
mat_rail = create_material("RailMetal", (0.2, 0.2, 0.2, 1.0), metallic=0.8, roughness=0.3)
mat_steam = create_material("Steam", (0.9, 0.9, 0.9, 0.3), metallic=0.0, roughness=1.0)
mat_steam.blend_method = 'BLEND'
mat_steam.shadow_method = 'NONE'

# Function to create a mesh from vertices and faces
def create_mesh_object(name, verts, faces, material=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj

# Create volcano terrain
def create_volcano_terrain():
    # Create a large plane and displace it
    bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
    terrain = bpy.context.active_object
    terrain.name = "VolcanoTerrain"
    
    # Subdivide for displacement
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=60)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Apply displacement via script
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(terrain.data)
    
    for v in bm.verts:
        x, y, z = v.co
        # Volcano shape - cone with crater
        dist = math.sqrt(x*x + y*y)
        # Base slope
        height = max(0, 10 - dist * 0.4)
        # Crater depression
        if dist < 5:
            crater_depth = 3 * (1 - dist/5)
            height -= crater_depth
        # Add noise for roughness
        n = noise.noise(Vector((x*0.1, y*0.1, 0))) * 0.5
        height += n
        v.co.z = height
    
    bm.to_mesh(terrain.data)
    bm.free()
    
    terrain.data.materials.append(mat_crater)
    return terrain

terrain = create_volcano_terrain()

# Create lava pool in crater
bpy.ops.mesh.primitive_cylinder_add(radius=3.5, depth=0.1, location=(0, 0, 0.5))
lava = bpy.context.active_object
lava.name = "LavaPool"
lava.data.materials.append(mat_lava)

# Create ash layer
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0.05))
ash = bpy.context.active_object
ash.name = "AshLayer"
ash.data.materials.append(mat_ash)

# Subdivide ash for slight irregularity
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')

import bmesh
bm = bmesh.new()
bm.from_mesh(ash.data)
for v in bm.verts:
    x, y, z = v.co
    n = noise.noise(Vector((x*0.2, y*0.2, 0))) * 0.1
    v.co.z = 0.05 + n
bm.to_mesh(ash.data)
bm.free()

# Create the hut
def create_hut():
    hut_parts = []
    
    # Hut position on the rim
    hut_x, hut_y = 8, 8
    hut_z = 8 - math.sqrt(hut_x*hut_x + hut_y*hut_y) * 0.4  # approximate terrain height
    
    # Hut base - black stone walls
    # Front wall
    wall_width = 4
    wall_height = 2.5
    wall_depth = 0.3
    
    # Create stone blocks for walls
    def create_stone_wall(name, loc, size, material):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        wall = bpy.context.active_object
        wall.name = name
        wall.scale = (size[0], size[1], size[2])
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        wall.data.materials.append(material)
        return wall
    
    # Front wall
    front_wall = create_stone_wall("HutFrontWall", (hut_x, hut_y - wall_width/2, hut_z + wall_height/2), (wall_width, wall_depth, wall_height), mat_black_stone)
    # Back wall
    back_wall = create_stone_wall("HutBackWall", (hut_x, hut_y + wall_width/2, hut_z + wall_height/2), (wall_width, wall_depth, wall_height), mat_black_stone)
    # Left wall
    left_wall = create_stone_wall("HutLeftWall", (hut_x - wall_width/2, hut_y, hut_z + wall_height/2), (wall_depth, wall_width, wall_height), mat_black_stone)
    # Right wall
    right_wall = create_stone_wall("HutRightWall", (hut_x + wall_width/2, hut_y, hut_z + wall_height/2), (wall_depth, wall_width, wall_height), mat_black_stone)
    
    # Corrugated iron roof
    # Create a sloped roof
    roof_width = wall_width + 0.5
    roof_length = wall_width + 0.5
    roof_height = 1.0
    
    # Roof vertices (sloped from back to front)
    roof_verts = [
        (-roof_width/2, -roof_length/2, hut_z + wall_height),  # front left
        (roof_width/2, -roof_length/2, hut_z + wall_height),   # front right
        (roof_width/2, roof_length/2, hut_z + wall_height + roof_height),  # back right
        (-roof_width/2, roof_length/2, hut_z + wall_height + roof_height), # back left
    ]
    roof_faces = [(0, 1, 2, 3)]
    
    roof = create_mesh_object("HutRoof", roof_verts, roof_faces, mat_corrugated)
    
    # Add corrugation effect by subdividing and displacing
    bpy.context.view_layer.objects.active = roof
    bpy.ops.object.select_all(action='DESELECT')
    roof.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=10)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bm = bmesh.new()
    bm.from_mesh(roof.data)
    for v in bm.verts:
        # Corrugation based on x position
        corrugation = math.sin(v.co.x * 10) * 0.05
        v.co.z += corrugation
    bm.to_mesh(roof.data)
    bm.free()
    
    # Door opening
    door_width = 1
    door_height = 1.8
    door_loc = (hut_x, hut_y - wall_width/2 - 0.01, hut_z + door_height/2)
    
    # Create door frame
    door_frame = create_stone_wall("DoorFrame", door_loc, (door_width, 0.1, door_height), mat_black_stone)
    
    # Window
    window_width = 0.8
    window_height = 0.8
    window_loc = (hut_x + 1, hut_y - wall_width/2 - 0.01, hut_z + 1.5)
    window = create_stone_wall("Window", window_loc, (window_width, 0.1, window_height), mat_black_stone)
    
    return hut_parts

create_hut()

# Create marker pole
def create_marker_pole():
    pole_x, pole_y = 10, 6
    pole_z = 8 - math.sqrt(pole_x*pole_x + pole_y*pole_y) * 0.4
    
    # Pole
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2, location=(pole_x, pole_y, pole_z + 1))
    pole = bpy.context.active_object
    pole.name = "MarkerPole"
    pole.data.materials.append(mat_pole)
    
    # Sign on top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(pole_x, pole_y, pole_z + 2.2))
    sign = bpy.context.active_object
    sign.name = "MarkerSign"
    sign.scale = (0.8, 0.05, 0.4)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    sign.data.materials.append(mat_pole)
    
    return pole, sign

create_marker_pole()

# Create railed path
def create_railed_path():
    # Path from front to hut
    path_start = (0, 15, 0)
    path_end = (8, 8, 0)
    
    # Create path surface
    path_points = []
    num_segments = 10
    for i in range(num_segments + 1):
        t = i / num_segments
        x = path_start[0] + (path_end[0] - path_start[0]) * t
        y = path_start[1] + (path_end[1] - path_start[1]) * t
        z = 8 - math.sqrt(x*x + y*y) * 0.4
        path_points.append((x, y, z))
    
    # Create path mesh
    path_width = 1.5
    path_verts = []
    path_faces = []
    
    for i, point in enumerate(path_points):
        # Calculate direction
        if i < len(path_points) - 1:
            dx = path_points[i+1][0] - point[0]
            dy = path_points[i+1][1] - point[1]
        else:
            dx = point[0] - path_points[i-1][0]
            dy = point[1] - path_points[i-1][1]
        
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            nx = -dy / length
            ny = dx / length
        else:
            nx, ny = 1, 0
        
        # Left and right vertices
        left_v = (point[0] + nx * path_width/2, point[1] + ny * path_width/2, point[2] + 0.05)
        right_v = (point[0] - nx * path_width/2, point[1] - ny * path_width/2, point[2] + 0.05)
        
        path_verts.append(left_v)
        path_verts.append(right_v)
    
    # Create faces
    for i in range(len(path_points) - 1):
        v1 = i * 2
        v2 = i * 2 + 1
        v3 = (i+1) * 2 + 1
        v4 = (i+1) * 2
        path_faces.append((v1, v2, v3, v4))
    
    path = create_mesh_object("Path", path_verts, path_faces, mat_ash)
    
    # Create rails
    def create_rail(offset):
        rail_verts = []
        rail_height = 0.8
        rail_radius = 0.03
        
        for point in path_points:
            if offset > 0:
                # Calculate perpendicular
                idx = path_points.index(point)
                if idx < len(path_points) - 1:
                    dx = path_points[idx+1][0] - point[0]
                    dy = path_points[idx+1][1] - point[1]
                else:
                    dx = point[0] - path_points[idx-1][0]
                    dy = point[1] - path_points[idx-1][1]
                
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    nx = -dy / length
                    ny = dx / length
                else:
                    nx, ny = 1, 0
                
                rail_x = point[0] + nx * offset
                rail_y = point[1] + ny * offset
            else:
                rail_x = point[0]
                rail_y = point[1]
            
            # Create small cylinder segment
            pass
        
        # Simplified: create a single curved rail
        # Use a curve
        curve_data = bpy.data.curves.new(name="RailCurve", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('POLY')
        spline.points.add(len(path_points) - 1)
        
        for i, point in enumerate(path_points):
            if offset != 0:
                idx = i
                if idx < len(path_points) - 1:
                    dx = path_points[idx+1][0] - point[0]
                    dy = path_points[idx+1][1] - point[1]
                else:
                    dx = point[0] - path_points[idx-1][0]
                    dy = point[1] - path_points[idx-1][1]
                
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    nx = -dy / length
                    ny = dx / length
                else:
                    nx, ny = 1, 0
                
                rail_x = point[0] + nx * offset
                rail_y = point[1] + ny * offset
            else:
                rail_x = point[0]
                rail_y = point[1]
            
            spline.points[i].co = (rail_x, rail_y, point[2] + rail_height, 1)
        
        curve_data.bevel_depth = 0.03
        curve_data.bevel_resolution = 2
        
        rail_obj = bpy.data.objects.new(f"Rail_{offset}", curve_data)
        bpy.context.collection.objects.link(rail_obj)
        rail_obj.data.materials.append(mat_rail)
        
        return rail_obj
    
    # Left rail
    create_rail(0.8)
    # Right rail
    create_rail(-0.8)
    
    # Posts
    for i in range(0, len(path_points), 2):
        point = path_points[i]
        # Left post
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.8, location=(point[0] + 0.8, point[1], point[2] + 0.4))
        post = bpy.context.active_object
        post.name = f"Post_L_{i}"
        post.data.materials.append(mat_rail)
        
        # Right post
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.8, location=(point[0] - 0.8, point[1], point[2] + 0.4))
        post = bpy.context.active_object
        post.name = f"Post_R_{i}"
        post.data.materials.append(mat_rail)
    
    return path

create_railed_path()

# Create steam particles
def create_steam():
    # Create several steam puffs
    random.seed(42)
    for i in range(15):
        x = random.uniform(-2, 2)
        y = random.uniform(-2, 2)
        z = random.uniform(1, 5)
        size = random.uniform(0.3, 0.8)
        
        bpy