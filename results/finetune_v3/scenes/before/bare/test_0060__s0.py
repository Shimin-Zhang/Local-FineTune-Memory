import bpy
import math
import mathutils
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create materials
def create_material(name, color, metallic=0.0, roughness=0.5, transmission=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["Alpha"].default_value = alpha
    if transmission > 0:
        mat.blend_method = 'BLEND'
        mat.use_backface_culling = False
    return mat

glass_mat = create_material("Glass", (0.8, 0.9, 1.0, 1.0), metallic=0.0, roughness=0.1, transmission=0.95, alpha=0.3)
wood_mat = create_material("Wood", (0.55, 0.35, 0.15, 1.0), metallic=0.0, roughness=0.8)
metal_mat = create_material("Metal", (0.4, 0.4, 0.45, 1.0), metallic=0.8, roughness=0.3)
concrete_mat = create_material("Concrete", (0.6, 0.6, 0.6, 1.0), metallic=0.0, roughness=0.9)
leaf_mat = create_material("Leaf", (0.1, 0.4, 0.1, 1.0), metallic=0.0, roughness=0.7)
trunk_mat = create_material("Trunk", (0.35, 0.2, 0.1, 1.0), metallic=0.0, roughness=0.9)
building_mat = create_material("Building", (0.5, 0.5, 0.55, 1.0), metallic=0.0, roughness=0.8)
road_mat = create_material("Road", (0.2, 0.2, 0.2, 1.0), metallic=0.0, roughness=0.95)
door_mat = create_material("AirlockDoor", (0.3, 0.3, 0.35, 1.0), metallic=0.9, roughness=0.2)

# Create city block context - surrounding buildings
def create_building(x, z, width, depth, height, name="Building"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, height/2, z))
    obj = bpy.context.active_object
    obj.scale = (width/2, height/2, depth/2)
    obj.name = name
    obj.data.materials.append(building_mat)
    return obj

# Surrounding city buildings
create_building(-15, -15, 10, 10, 20, "Building_NW")
create_building(15, -15, 10, 10, 25, "Building_NE")
create_building(-15, 15, 10, 10, 18, "Building_SW")
create_building(15, 15, 10, 10, 22, "Building_SE")
create_building(0, -20, 12, 8, 15, "Building_North")
create_building(0, 20, 12, 8, 17, "Building_South")
create_building(-20, 0, 8, 12, 20, "Building_West")
create_building(20, 0, 8, 12, 23, "Building_East")

# Roads
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
road = bpy.context.active_object
road.scale = (25, 0.01, 25)
road.name = "Road"
road.data.materials.append(road_mat)

# Ground inside greenhouse
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.01, 0))
ground = bpy.context.active_object
ground.scale = (12, 0.01, 12)
ground.name = "GreenhouseGround"
ground.data.materials.append(concrete_mat)

# Glass dome
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=10, location=(0, 5, 0))
dome = bpy.context.active_object
dome.name = "GlassDome"
dome.data.materials.append(glass_mat)
# Cut bottom half
import bmesh
bm = bmesh.new()
bm.from_mesh(dome.data)
for v in bm.verts:
    if v.co.y < 0:
        v.co.y = 0
bm.to_mesh(dome.data)
bm.free()

# Dome frame - metal rings
for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4]:
    bpy.ops.mesh.primitive_torus_add(major_radius=10, minor_radius=0.1, major_segments=32, minor_segments=8, location=(0, 5, 0))
    ring = bpy.context.active_object
    ring.rotation_euler = (0, angle, 0)
    ring.name = f"DomeFrame_{angle:.2f}"
    ring.data.materials.append(metal_mat)

# Base ring
bpy.ops.mesh.primitive_torus_add(major_radius=10, minor_radius=0.2, major_segments=48, minor_segments=8, location=(0, 0.1, 0))
base_ring = bpy.context.active_object
base_ring.name = "BaseRing"
base_ring.data.materials.append(metal_mat)

# Wooden walkway
def create_walkway(x1, z1, x2, z2, width=1.5):
    dx = x2 - x1
    dz = z2 - z1
    length = math.sqrt(dx*dx + dz*dz)
    angle = math.atan2(dz, dx)
    cx = (x1 + x2) / 2
    cz = (z1 + z2) / 2
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, 0.1, cz))
    walk = bpy.context.active_object
    walk.scale = (length/2, 0.05, width/2)
    walk.rotation_euler = (0, 0, angle)
    walk.name = "Walkway"
    walk.data.materials.append(wood_mat)
    return walk

# Main walkways
create_walkway(0, -8, 0, 8)
create_walkway(-8, 0, 8, 0)
create_walkway(0, 0, 6, 6)
create_walkway(0, 0, -6, -6)

# Tropical trees
def create_tropical_tree(x, z, scale=1.0):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15*scale, depth=3*scale, location=(x, 1.5*scale, z))
    trunk = bpy.context.active_object
    trunk.name = "TreeTrunk"
    trunk.data.materials.append(trunk_mat)
    
    # Palm leaves - multiple flat planes
    for i in range(6):
        angle = i * math.pi / 3
        leaf_x = x + 0.8*scale * math.cos(angle)
        leaf_z = z + 0.8*scale * math.sin(angle)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(leaf_x, 3*scale, leaf_z))
        leaf = bpy.context.active_object
        leaf.scale = (1.2*scale, 0.01, 0.4*scale)
        leaf.rotation_euler = (math.radians(-30), 0, angle)
        leaf.name = "PalmLeaf"
        leaf.data.materials.append(leaf_mat)
    
    # Bushy tropical tree variant
    if scale > 0.8:
        for j in range(3):
            bx = x + 0.5*scale * math.cos(j*2.1)
            bz = z + 0.5*scale * math.sin(j*2.1)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.6*scale, location=(bx, 3.5*scale, bz))
            bush = bpy.context.active_object
            bush.name = "TropicalBush"
            bush.data.materials.append(leaf_mat)

create_tropical_tree(-4, -4, 1.0)
create_tropical_tree(4, -4, 0.9)
create_tropical_tree(-4, 4, 1.1)
create_tropical_tree(4, 4, 0.8)
create_tropical_tree(0, -6, 0.7)
create_tropical_tree(0, 6, 0.7)
create_tropical_tree(-6, 0, 0.9)
create_tropical_tree(6, 0, 0.9)

# Research hut
def create_research_hut(x, z):
    # Base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 1, z))
    hut = bpy.context.active_object
    hut.scale = (2, 1, 2)
    hut.name = "ResearchHut"
    hut.data.materials.append(wood_mat)
    
    # Roof
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=3, radius2=0, depth=1.5, location=(x, 2.75, z))
    roof = bpy.context.active_object
    roof.rotation_euler = (0, 0, math.pi/4)
    roof.name = "HutRoof"
    roof.data.materials.append(metal_mat)
    
    # Windows
    for wx in [-1.2, 1.2]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x + wx, 1.2, z + 2.01))
        win = bpy.context.active_object
        win.scale = (0.4, 0.3, 0.05)
        win.name = "HutWindow"
        win.data.materials.append(glass_mat)
    
    # Door
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.7, z + 2.01))
    door = bpy.context.active_object
    door.scale = (0.5, 0.7, 0.05)
    door.name = "HutDoor"
    door.data.materials.append(wood_mat)

create_research_hut(-6, 6)

# Airlock door
def create_airlock(x, z, rot_z=0):
    # Frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 1.2, z))
    frame = bpy.context.active_object
    frame.scale = (1.2, 1.2, 0.3)
    frame.name = "AirlockFrame"
    frame.data.materials.append(metal_mat)
    
    # Door
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 1.0, z + 0.16))
    door = bpy.context.active_object
    door.scale = (0.9, 0.9, 0.1)
    door.name = "AirlockDoor"
    door.data.materials.append(door_mat)
    
    # Handle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=(x + 0.5, 1.0, z + 0.25))
    handle = bpy.context.active_object
    handle.rotation_euler = (0, math.pi/2, 0)
    handle.name = "DoorHandle"
    handle.data.materials.append(metal_mat)
    
    # Light indicator
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(x, 1.8, z + 0.16))
    light = bpy.context.active_object
    light.name = "AirlockLight"
    mat_light = bpy.data.materials.new("AirlockLightMat")
    mat_light.use_nodes = True
    bsdf = mat_light.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.0, 1.0, 0.0, 1.0)
    bsdf.inputs["Emission Color"].default_value = (0.0, 1.0, 0.0, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 2.0
    light.data.materials.append(mat_light)

create_airlock(0, 10, 0)  # South entrance
create_airlock(0, -10, math.pi)  # North entrance

# Add some potted plants
for px, pz in [(-2, -2), (2, 2), (-2, 2), (2, -2)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(px, 0.25, pz))
    pot = bpy.context.active_object
    pot.name = "PlantPot"
    pot.data.materials.append(concrete_mat)
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.4, location=(px, 0.7, pz))
    plant = bpy.context.active_object
    plant.name = "PottedPlant"
    plant.data.materials.append(leaf_mat)

# Set up lighting
bpy.ops.object.light_add(type='SUN', location=(10, 20, 10))
sun = bpy.context.active_object
sun.rotation_euler = (math.radians(45), math.radians(30), 0)
sun.data.energy = 3.0

bpy.ops.object.light_add(type='POINT', location=(0, 8, 0))
point_light = bpy.context.active_object
point_light.data.energy = 100
point_light.data.color = (1.0, 0.95, 0.8)

# Camera
bpy.ops.object.camera_add(location=(25, 15, 20))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(55), 0, math.radians(135))
bpy.context.scene.camera = camera

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Glass dome greenhouse city block scene created successfully!")
