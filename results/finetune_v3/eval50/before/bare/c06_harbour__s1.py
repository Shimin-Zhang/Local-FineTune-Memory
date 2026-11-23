import bpy
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Helper functions
def add_box(name, location, size=(1,1,1), color=(0.5,0.5,0.5,1.0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    mat = bpy.data.materials.new(name=name+"_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)
    return obj

def add_cylinder(name, location, radius=0.5, depth=1, color=(0.5,0.5,0.5,1.0), segments=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, vertices=segments)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name+"_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)
    return obj

def add_sphere(name, location, radius=0.5, color=(0.5,0.5,0.5,1.0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=16, ring_count=8)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name+"_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)
    return obj

# Water
water = add_box("Water", (0, 0, -0.5), size=(20, 20, 0.5), color=(0.1, 0.3, 0.6, 1.0))

# Ground / Shore
ground = add_box("Shore", (-8, 0, 0), size=(12, 16, 0.3), color=(0.6, 0.5, 0.3, 1.0))

# Pier
pier_deck = add_box("Pier", (0, 0, 0.15), size=(8, 2, 0.3), color=(0.4, 0.3, 0.2, 1.0))
# Pier pilings
for x in [-3, -1, 1, 3]:
    for y in [-0.8, 0.8]:
        add_cylinder(f"Piling_{x}_{y}", (x, y, -0.3), radius=0.15, depth=1.2, color=(0.3, 0.2, 0.1, 1.0))

# Boat 1
boat1_hull = add_box("Boat1_Hull", (2, 3, 0.1), size=(2.5, 1, 0.4), color=(0.7, 0.1, 0.1, 1.0))
boat1_deck = add_box("Boat1_Deck", (2, 3, 0.35), size=(2.3, 0.8, 0.05), color=(0.8, 0.6, 0.4, 1.0))
boat1_cabin = add_box("Boat1_Cabin", (1.5, 3, 0.6), size=(0.8, 0.6, 0.5), color=(0.9, 0.9, 0.9, 1.0))
boat1_mast = add_cylinder("Boat1_Mast", (2.5, 3, 1.0), radius=0.05, depth=1.5, color=(0.4, 0.3, 0.2, 1.0))

# Boat 2
boat2_hull = add_box("Boat2_Hull", (-2, 4, 0.1), size=(2, 0.8, 0.35), color=(0.1, 0.4, 0.7, 1.0))
boat2_deck = add_box("Boat2_Deck", (-2, 4, 0.3), size=(1.8, 0.6, 0.05), color=(0.8, 0.6, 0.4, 1.0))
boat2_mast = add_cylinder("Boat2_Mast", (-2, 4, 0.8), radius=0.04, depth=1.2, color=(0.4, 0.3, 0.2, 1.0))

# Lighthouse
lh_base = add_cylinder("Lighthouse_Base", (-7, -4, 2), radius=1.2, depth=4, color=(0.9, 0.9, 0.8, 1.0))
lh_mid = add_cylinder("Lighthouse_Mid", (-7, -4, 4.5), radius=0.9, depth=1.5, color=(0.9, 0.1, 0.1, 1.0))
lh_top = add_cylinder("Lighthouse_Top", (-7, -4, 5.75), radius=0.7, depth=1, color=(0.9, 0.9, 0.8, 1.0))
lh_lamp = add_cylinder("Lighthouse_Lamp", (-7, -4, 6.5), radius=0.5, depth=0.5, color=(1.0, 1.0, 0.3, 1.0))
lh_roof = add_cylinder("Lighthouse_Roof", (-7, -4, 7.0), radius=0.6, depth=0.5, color=(0.2, 0.2, 0.2, 1.0))

# Crates
crate_positions = [
    (3.5, -1.5, 0.35, 0.5, (0.6, 0.4, 0.2, 1.0)),
    (4.0, -1.0, 0.35, 0.5, (0.5, 0.35, 0.15, 1.0)),
    (3.5, -1.5, 0.85, 0.5, (0.55, 0.4, 0.2, 1.0)),
    (4.5, -1.5, 0.35, 0.4, (0.45, 0.3, 0.1, 1.0)),
    (5.0, -1.0, 0.3, 0.4, (0.6, 0.45, 0.25, 1.0)),
    (3.8, -0.5, 0.35, 0.5, (0.5, 0.35, 0.15, 1.0)),
]
for i, (x, y, z, s, c) in enumerate(crate_positions):
    add_box(f"Crate_{i}", (x, y, z), size=(s, s, s), color=c)

# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.active_object
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), math.radians(20), 0)

# Camera
bpy.ops.object.camera_add(location=(10, 10, 8), rotation=(math.radians(50), 0, math.radians(135)))
cam = bpy.context.active_object
bpy.context.scene.camera = cam
