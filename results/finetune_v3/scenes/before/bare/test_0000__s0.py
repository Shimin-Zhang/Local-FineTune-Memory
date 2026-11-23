import bpy
import math
import random
import mathutils

# Set up random seed for reproducibility
random.seed(42)

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create materials
def create_material(name, base_color, metallic=0.0, roughness=0.8):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

# Rusty material
rust_mat = create_material("Rust", (0.45, 0.18, 0.08), 0.3, 0.9)
# Dry seabed material
seabed_mat = create_material("DrySeabed", (0.35, 0.28, 0.18), 0.0, 0.95)
# Wood material
wood_mat = create_material("OldWood", (0.25, 0.15, 0.08), 0.0, 0.9)
# Plant material
plant_mat = create_material("ScrubPlant", (0.2, 0.35, 0.1), 0.0, 0.8)
# Metal material for ladder
metal_mat = create_material("WornMetal", (0.3, 0.3, 0.3), 0.8, 0.7)

# Create the dry seabed (cracked dry seabed)
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
seabed = bpy.context.active_object
seabed.name = "DrySeabed"
seabed.data.materials.append(seabed_mat)

# Add some displacement for cracked appearance
subsurf = seabed.modifiers.new("Subsurf", 'SUBSURF')
subsurf.levels = 3
subsurf.render_levels = 3

# Add crack lines by creating thin boxes
for i in range(15):
    x = random.uniform(-20, 20)
    y = random.uniform(-20, 20)
    length = random.uniform(2, 8)
    angle = random.uniform(0, math.pi)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.01))
    crack = bpy.context.active_object
    crack.name = f"Crack_{i}"
    crack.scale = (length, 0.05, 0.02)
    crack.rotation_euler = (0, 0, angle)
    crack.data.materials.append(seabed_mat)

# Create the fishing ship (listing on its keel)
# Main hull
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2))
hull = bpy.context.active_object
hull.name = "ShipHull"
hull.scale = (8, 3, 2)
hull.rotation_euler = (0, math.radians(15), 0)  # Listing angle
hull.data.materials.append(rust_mat)

# Add deck
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 3.5))
deck = bpy.context.active_object
deck.name = "ShipDeck"
deck.scale = (7.5, 2.8, 0.3)
deck.rotation_euler = (0, math.radians(15), 0)
deck.data.materials.append(wood_mat)

# Add cabin
bpy.ops.mesh.primitive_cube_add(size=1, location=(-3, 0, 4.5))
cabin = bpy.context.active_object
cabin.name = "ShipCabin"
cabin.scale = (3, 2, 1.5)
cabin.rotation_euler = (0, math.radians(15), 0)
cabin.data.materials.append(rust_mat)

# Add mast
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=6, location=(2, 0, 6))
mast = bpy.context.active_object
mast.name = "ShipMast"
mast.rotation_euler = (0, math.radians(15), 0)
mast.data.materials.append(wood_mat)

# Add dangling ladder
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=3, location=(5, 0, 2))
ladder_rail1 = bpy.context.active_object
ladder_rail1.name = "LadderRail1"
ladder_rail1.rotation_euler = (math.radians(30), 0, 0)
ladder_rail1.data.materials.append(metal_mat)

bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=3, location=(5.3, 0, 2))
ladder_rail2 = bpy.context.active_object
ladder_rail2.name = "LadderRail2"
ladder_rail2.rotation_euler = (math.radians(30), 0, 0)
ladder_rail2.data.materials.append(metal_mat)

# Add ladder rungs
for i in range(5):
    z = 0.5 + i * 0.6
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.3, location=(5.15, 0, z))
    rung = bpy.context.active_object
    rung.name = f"LadderRung_{i}"
    rung.rotation_euler = (0, math.radians(90), math.radians(30))
    rung.data.materials.append(metal_mat)

# Create wrecked sheds
for i in range(3):
    x = random.uniform(-10, 10)
    y = random.uniform(-10, 10)
    rotation = random.uniform(0, math.pi)
    
    # Shed body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 1))
    shed = bpy.context.active_object
    shed.name = f"WreckedShed_{i}"
    shed.scale = (3, 2, 1.5)
    shed.rotation_euler = (0, 0, rotation)
    shed.data.materials.append(wood_mat)
    
    # Shed roof (damaged)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 2.5))
    roof = bpy.context.active_object
    roof.name = f"WreckedRoof_{i}"
    roof.scale = (3.2, 2.2, 1)
    roof.rotation_euler = (math.radians(random.uniform(-10, 10)), math.radians(random.uniform(-10, 10)), rotation)
    roof.data.materials.append(wood_mat)

# Add scrubby plants
for i in range(10):
    x = random.uniform(-15, 15)
    y = random.uniform(-15, 15)
    
    # Plant stem
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.5, location=(x, y, 0.25))
    stem = bpy.context.active_object
    stem.name = f"PlantStem_{i}"
    stem.data.materials.append(plant_mat)
    
    # Plant leaves (simple spheres)
    for j in range(3):
        leaf_x = x + random.uniform(-0.2, 0.2)
        leaf_y = y + random.uniform(-0.2, 0.2)
        leaf_z = 0.4 + random.uniform(0, 0.2)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(leaf_x, leaf_y, leaf_z))
        leaf = bpy.context.active_object
        leaf.name = f"PlantLeaf_{i}_{j}"
        leaf.scale = (1, 1, 0.5)
        leaf.data.materials.append(plant_mat)

# Add some rocks for detail
for i in range(5):
    x = random.uniform(-12, 12)
    y = random.uniform(-12, 12)
    size = random.uniform(0.2, 0.5)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=size, location=(x, y, size/2))
    rock = bpy.context.active_object
    rock.name = f"Rock_{i}"
    rock.scale = (1, random.uniform(0.8, 1.2), random.uniform(0.5, 0.8))
    rock.data.materials.append(seabed_mat)

# Set up camera
bpy.ops.object.camera_add(location=(15, 15, 10))
camera = bpy.context.active_object
camera.name = "MainCamera"
camera.rotation_euler = (math.radians(60), 0, math.radians(-45))
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.active_object
sun.name = "Sunlight"
sun.rotation_euler = (math.radians(45), math.radians(30), 0)
sun.data.energy = 5
sun.data.color = (1, 0.9, 0.8)  # Warm light for dusty atmosphere

# Add ambient light
bpy.ops.object.light_add(type='AREA', location=(0, 0, 15))
ambient = bpy.context.active_object
ambient.name = "AmbientLight"
ambient.rotation_euler = (0, 0, 0)
ambient.data.energy = 10
ambient.data.size = 30
ambient.data.color = (0.8, 0.75, 0.7)  # Warm ambient

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.7, 0.6, 0.5, 1.0)  # Dusty sky color
