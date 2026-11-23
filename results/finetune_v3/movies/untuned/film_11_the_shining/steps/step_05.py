import bpy
import math
import random
from mathutils import Vector

# Fix the look enum
scene = bpy.context.scene
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0.5
scene.view_settings.gamma = 1.0

# Fix camera - position it to see the maze in front and hotel behind
cam = bpy.data.objects.get("Camera")
if cam is None:
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object

# Place camera at a good vantage point: slightly elevated, in front of the maze
# Maze is centered around z=0, hotel is at z=-55
# Camera should be at positive z looking toward negative z
cam.location = (15, 20, 35)

# Look at a point between the maze and hotel
target = Vector((0, 5, -20))
direction = target - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()

bpy.context.scene.camera = cam

# Make sure camera is in the scene collection
if cam.name not in [o.name for o in bpy.context.collection.objects]:
    bpy.context.collection.objects.link(cam)

# --- ADD MORE HEDGE MAZE DETAIL: rounded tops on hedges ---
# Find hedge objects and add slight irregularity
for obj in bpy.context.collection.objects:
    if obj.type == 'MESH' and obj.scale.y > 2 and obj.scale.y < 4:
        # This is likely a hedge
        pass  # Already have snow caps

# --- ADD FENCE/PATH MARKERS ---
# Small snow-covered rocks along the path
mat_rock = bpy.data.materials.new("rock_mat")
mat_rock.use_nodes = True
mat_rock.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.4, 0.4, 0.42, 1.0)
mat_rock.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95

random.seed(77)
for i in range(15):
    z = -5 - i * 3
    x = random.choice([-3.5, 3.5]) + random.uniform(-0.5, 0.5)
    r = random.uniform(0.3, 0.7)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, r*0.3, z))
    rock = bpy.context.active_object
    rock.scale = (1, 0.5, 1)
    rock.data.materials.append(mat_rock)
    # Snow cap on rock
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r*0.9, location=(x, r*0.5, z))
    rock_snow = bpy.context.active_object
    rock_snow.scale = (1, 0.3, 1)
    rock_snow.data.materials.append(bpy.data.materials.get("snow"))

# --- ADD HOTEL ENTRANCE PORCH ---
hotel_x = 0
hotel_z = -55
hotel_depth = 20
front_z = hotel_z + hotel_depth/2 + 0.1

# Porch roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x, 5, front_z + 3))
porch_roof = bpy.context.active_object
porch_roof.scale = (8, 0.5, 4)
porch_roof.data.materials.append(bpy.data.materials.get("hotel_roof"))

# Porch columns
for px in [-3, 3]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=5, location=(hotel_x + px, 2.5, front_z + 2))
    col = bpy.context.active_object
    col.data.materials.append(bpy.data.materials.get("hotel_wall"))

# Porch step
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x, 0.3, front_z + 1))
step = bpy.context.active_object
step.scale = (6, 0.6, 2)
step.data.materials.append(bpy.data.materials.get("snow"))

# --- ADD CHIMNEY on hotel ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x + 12, hotel_height + 3, hotel_z - 5))
chimney = bpy.context.active_object
chimney.scale = (2, 6, 2)
chimney.data.materials.append(bpy.data.materials.get("hotel_wall"))

# Chimney top
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x + 12, hotel_height + 6.5, hotel_z - 5))
chimney_top = bpy.context.active_object
chimney_top.scale = (2.5, 1, 2.5)
chimney_top.data.materials.append(bpy.data.materials.get("hotel_roof"))

# Snow on chimney
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x + 12, hotel_height + 7.2, hotel_z - 5))
chimney_snow = bpy.context.active_object
chimney_snow.scale = (2.6, 0.4, 2.6)
chimney_snow.data.materials.append(bpy.data.materials.get("snow"))

# --- ADD MORE LIT WINDOWS with slight variation ---
mat_window_warm = bpy.data.materials.new("window_warm2")
mat_window_warm.use_nodes = True
bsdf_w = mat_window_warm.node_tree.nodes["Principled BSDF"]
bsdf_w.inputs["Emission Color"].default_value = (1.0, 0.6, 0.2, 1.0)
bsdf_w.inputs["Emission Strength"].default_value = 2.5
bsdf_w.inputs["Base Color"].default_value = (1.0, 0.6, 0.2, 1.0)

# Add a few extra lit windows on the back and sides
for i in range(8):
    x = random.uniform(-15, 15)
    y = random.uniform(3, 20)
    z = hotel_z - hotel_depth/2 - 0.1  # back face
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
    win = bpy.context.active_object
    win.scale = (1.5, 2.0, 1)
    win.rotation_euler = (math.radians(-90), 0, 0)
    if random.random() < 0.5:
        win.data.materials.append(mat_window_warm)
    else:
        win.data.materials.append(bpy.data.materials.get("window_dark"))

# --- ADD SNOW ON HOTEL ROOF ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x, hotel_height + 2.2, hotel_z))
roof_snow = bpy.context.active_object
roof_snow.scale = (hotel_width/2 + 2, 0.5, hotel_depth/2 + 2)
roof_snow.data.materials.append(bpy.data.materials.get("snow"))

# Tower roof snow
bpy.ops.mesh.primitive_cube_add(size=1, location=(hotel_x, hotel_height + 15 + 2.2, hotel_z))
tower_roof_snow = bpy.context.active_object
tower_roof_snow.scale = (7, 0.5, 6)
tower_roof_snow.data.materials.append(bpy.data.materials.get("snow"))

# --- ADD A FEW MORE TREES closer to the maze ---
mat_snow_tree = bpy.data.materials.get("snow_tree_mat")
mat_trunk = bpy.data.materials.get("trunk_mat")

def add_tree(x, z, scale=1.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3*scale, depth=3*scale, location=(x, 1.5*scale, z))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_trunk)
    for i in range(4):
        h = 2.5 + i * 1.5
        r = (2.5 - i * 0.5) * scale
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=2.0*scale, location=(x, h*scale, z))
        cone = bpy.context.active_object
        cone.data.materials.append(mat_snow_tree)

# Trees flanking the path
add_tree(-8, -5, 1.2)
add_tree(8, -8, 1.0)
add_tree(-10, -15, 1.4)
add_tree(10, -12, 1.1)
add_tree(-12, -25, 1.3)
add_tree(12, -20, 1.0)

# --- ADD FOG / ATMOSPHERE ---
# Use a large transparent volume box for subtle fog
mat_fog = bpy.data.materials.new("fog_mat")
mat_fog.use_nodes = True
nodes = mat_fog.node_tree.nodes
links = mat_fog.node_tree.links
nodes.clear()

vol = nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Color"].default_value = (0.6, 0.7, 0.9, 1.0)
vol.inputs["Density"].default_value = 0.003
vol.inputs["Anisotropy"].default_value = 0.3

out = nodes.new("ShaderNodeOutputMaterial")
links.new(vol.outputs["Volume"], out.inputs["Volume"])

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 20, -20))
fog_box = bpy.context.active_object
fog_box.scale = (80, 40, 60)
fog_box.data.materials.append(mat_fog)
fog_box.display_type = 'WIRE'
fog_box.hide_render = False

# --- RENDER SETTINGS ---
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0.3
scene.view_settings.gamma = 1.0

# Set frame for snow particles
scene.frame_set(100)

print("Scene fully refined! Camera fixed, porch, chimney, rocks, fog, more trees and windows added.")
