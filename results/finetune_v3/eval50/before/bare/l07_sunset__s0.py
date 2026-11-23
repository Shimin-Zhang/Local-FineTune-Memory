import bpy
import math
import mathutils
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Create a hill (flattened sphere / displaced plane) ---
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
hill = bpy.context.active_object
hill.name = "Hill"

# Subdivide for displacement
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')

# Add a simple hill shape using vertex displacement
import bmesh
me = hill.data
bm = bmesh.new()
bm.from_mesh(me)
for v in bm.verts:
    # Create a gentle hill using a radial falloff
    r = math.sqrt(v.co.x**2 + v.co.y**2)
    v.co.z += 3.0 * math.exp(-r**2 / 100.0)
bm.to_mesh(me)
bm.free()

# --- Create the sun (low orange sphere) ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location=(0, -30, 1.5))
sun = bpy.context.active_object
sun.name = "Sun"

# Sun material - bright orange
sun_mat = bpy.data.materials.new("SunMat")
sun_mat.use_nodes = True
bsdf = sun_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 0.3, 0.0, 1.0)
bsdf.inputs["Emission Color"].default_value = (1.0, 0.3, 0.0, 1.0)
bsdf.inputs["Emission Strength"].default_value = 5.0
sun.data.materials.append(sun_mat)

# --- Create trees (simple cylinder trunk + icosphere canopy) ---
def make_tree(x, y, z, scale=1.0):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15*scale, depth=1.5*scale, location=(x, y, z + 0.75*scale))
    trunk = bpy.context.active_object
    trunk.name = f"Trunk_{x}_{y}"
    
    trunk_mat = bpy.data.materials.new(f"TrunkMat_{x}_{y}")
    trunk_mat.use_nodes = True
    tbsdf = trunk_mat.node_tree.nodes["Principled BSDF"]
    tbsdf.inputs["Base Color"].default_value = (0.2, 0.1, 0.05, 1.0)
    trunk.data.materials.append(trunk_mat)
    
    # Canopy
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.8*scale, location=(x, y, z + 1.8*scale))
    canopy = bpy.context.active_object
    canopy.name = f"Canopy_{x}_{y}"
    
    canopy_mat = bpy.data.materials.new(f"CanopyMat_{x}_{y}")
    canopy_mat.use_nodes = True
    cbsdf = canopy_mat.node_tree.nodes["Principled BSDF"]
    cbsdf.inputs["Base Color"].default_value = (0.05, 0.2, 0.05, 1.0)
    canopy.data.materials.append(canopy_mat)

# Place a few trees on the hill
tree_positions = [
    (-3, 2, 2.2, 1.0),
    (2, -1, 2.5, 1.2),
    (4, 3, 1.8, 0.9),
    (-1, 5, 1.5, 1.1),
    (1, 4, 1.9, 0.8),
]

for x, y, z, s in tree_positions:
    make_tree(x, y, z, s)

# --- World / Sky ---
world = bpy.data.worlds.get("World")
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.6, 0.3, 0.1, 1.0)  # Orange-ish sunset sky
    bg.inputs["Strength"].default_value = 1.0

# --- Sun light (directional, low angle for long shadows) ---
bpy.ops.object.light_add(type='SUN', location=(0, -30, 2))
sun_light = bpy.context.active_object
sun_light.name = "SunLight"
sun_light.data.energy = 3.0
sun_light.data.color = (1.0, 0.5, 0.2, 1.0)
# Point the sun light from a low angle (long shadows)
sun_light.rotation_euler = (math.radians(75), 0, math.radians(0))

# --- Camera ---
bpy.ops.object.camera_add(location=(0, 15, 4))
cam = bpy.context.active_object
cam.name = "Camera"
# Aim camera toward the sun/hill
direction = Vector((0, -30, 1.5)) - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam

# --- Render settings ---
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.render.filepath = "//sunset_scene.png"

print("Sunset scene created successfully!")
