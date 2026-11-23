import bpy
import math
import random
from mathutils import Vector

# Fix the light color that failed - lights use 3-tuple for color
# The fire light was created but color failed. Let's fix it and continue.

# Find the fire light and fix its color
fire_light = bpy.data.objects.get("Fire_Light")
if fire_light:
    fire_light.data.color = (1.0, 0.4, 0.1)  # 3-tuple for light color

# Add the remaining lights that didn't get created
# Ambient sun
sun = bpy.data.objects.get("Ambient_Sun")
if not sun:
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.object
    sun.name = "Ambient_Sun"
    sun.data.energy = 0.5
    sun.data.color = (0.3, 0.3, 0.4)  # 3-tuple

# Rim light
rim_light = bpy.data.objects.get("Rim_Light")
if not rim_light:
    bpy.ops.object.light_add(type='POINT', location=(4.5 + 2, 0, 0.2 + 2))
    rim_light = bpy.context.object
    rim_light.name = "Rim_Light"
    rim_light.data.energy = 100
    rim_light.data.color = (1.0, 0.3, 0.0)  # 3-tuple

# --- CAMERA ---
camera = bpy.data.objects.get("Main_Camera")
if not camera:
    bpy.ops.object.camera_add(location=(-5, 3, 2.5))
    camera = bpy.context.object
    camera.name = "Main_Camera"
    target = Vector((1.5, 0, 1.5))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

bpy.context.scene.camera = camera

# --- WORLD BACKGROUND ---
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)
    bg_node.inputs[1].default_value = 1.0

# --- RENDER SETTINGS ---
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
try:
    scene.view_settings.look = 'AgX - Punchy'
except:
    scene.view_settings.look = 'None'

# --- ADD MORE DETAIL ---

# Add more stone blocks on the bridge for texture
bridge_length = 12.0
bridge_width = 2.0
bridge_thickness = 0.4
bridge_y = 0.0

# Random stone cracks and details on bridge
for i in range(20):
    x = random.uniform(-bridge_length/2 + 0.5, bridge_length/2 - 0.5)
    y = random.uniform(-bridge_width/2 + 0.2, bridge_width/2 - 0.2)
    z = bridge_thickness/2 + 0.01
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    crack = bpy.context.object
    crack.name = f"Bridge_Detail_{i}"
    crack.scale = (random.uniform(0.05, 0.15), random.uniform(0.05, 0.15), 0.02)
    crack.data.materials.append(bpy.data.materials.get("StoneDark"))
    bpy.ops.object.transform_apply(scale=True)

# Add more railing details - vertical posts
for i in range(14):
    x = -bridge_length/2 + 0.3 + i * (bridge_length/14)
    # Left side
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.8, location=(x, -bridge_width/2 + 0.05, bridge_thickness/2 + 0.4))
    post = bpy.context.object
    post.name = f"RailPost_L_{i}"
    post.data.materials.append(bpy.data.materials.get("PillarStone"))
    
    # Right side
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.8, location=(x, bridge_width/2 - 0.05, bridge_thickness/2 + 0.4))
    post = bpy.context.object
    post.name = f"RailPost_R_{i}"
    post.data.materials.append(bpy.data.materials.get("PillarStone"))

# Add arches under the bridge
for i in range(3):
    x = -bridge_length/2 + 2 + i * 4
    bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.2, location=(x, 0, -1))
    arch = bpy.context.object
    arch.name = f"Bridge_Arch_{i}"
    arch.rotation_euler = (0, math.radians(90), 0)
    arch.data.materials.append(bpy.data.materials.get("StoneDark"))

# Add more fire particles around Balrog
balrog_x = 4.5
balrog_y = 0
balrog_z = bridge_thickness/2

mat_fire = bpy.data.materials.get("Fire")
mat_fire_inner = bpy.data.materials.get("FireInner")

for i in range(10):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0.5, 2.0)
    x = balrog_x - 1.0 + dist * math.cos(angle)
    y = balrog_y + dist * math.sin(angle)
    z = balrog_z + random.uniform(0.1, 1.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.1, 0.25), location=(x, y, z))
    fire = bpy.context.object
    fire.name = f"FireExtra_{i}"
    fire.data.materials.append(mat_fire if random.random() > 0.5 else mat_fire_inner)

# Add more smoke
mat_smoke = bpy.data.materials.get("Smoke")
for i in range(12):
    x = balrog_x - 0.5 + random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    z = balrog_z + 3.0 + i * 0.4 + random.uniform(-0.2, 0.2)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2 + i * 0.03, location=(x, y, z))
    smoke = bpy.context.object
    smoke.name = f"SmokeExtra_{i}"
    smoke.data.materials.append(mat_smoke)

# Add Gandalf's glowing eyes (small emissive spheres)
mat_eye_glow = bpy.data.materials.get("Glow")
gandalf_x = -1.5
gandalf_y = 0
gandalf_z = bridge_thickness/2

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(gandalf_x + 0.05, gandalf_y - 0.05, gandalf_z + 2.18))
eye_g = bpy.context.object
eye_g.name = "Gandalf_Eye_L"
eye_g.data.materials.append(mat_eye_glow)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(gandalf_x + 0.05, gandalf_y + 0.05, gandalf_z + 2.18))
eye_g = bpy.context.object
eye_g.name = "Gandalf_Eye_R"
eye_g.data.materials.append(mat_eye_glow)

# Add a subtle glow under the Balrog's feet
mat_glow = bpy.data.materials.get("Glow")
bpy.ops.mesh.primitive_plane_add(size=1, location=(balrog_x, balrog_y, balrog_z + 0.05))
glow_plane = bpy.context.object
glow_plane.name = "Balrog_FootGlow"
glow_plane.scale = (2.0, 1.5, 1)
glow_plane.data.materials.append(mat_glow)
bpy.ops.object.transform_apply(scale=True)

# Add more chasm details - rock formations
mat_stone_dark = bpy.data.materials.get("StoneDark")
for i in range(8):
    x = random.uniform(-4, 4)
    y = random.uniform(-8, 8)
    z = random.uniform(-8, -3)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.5, 1.5), location=(x, y, z))
    rock = bpy.context.object
    rock.name = f"Chasm_Rock_{i}"
    rock.scale = (random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), random.uniform(0.5, 1.5))
    rock.data.materials.append(mat_stone_dark)
    bpy.ops.object.transform_apply(scale=True)

# Add torches on the bridge for additional lighting
mat_torch_wood = bpy.data.materials.get("WoodDark")
mat_torch_fire = bpy.data.materials.get("Fire")

torch_positions = [(-4, -1.2), (-2, 1.2), (0, -1.2), (2, 1.2)]
for idx, (tx, ty) in enumerate(torch_positions):
    # Torch pole
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=1.2, location=(tx, ty, bridge_thickness/2 + 0.6))
    pole = bpy.context.object
    pole.name = f"Torch_Pole_{idx}"
    pole.data.materials.append(mat_torch_wood)
    
    # Torch fire
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(tx, ty, bridge_thickness/2 + 1.25))
    tf = bpy.context.object
    tf.name = f"Torch_Fire_{idx}"
    tf.data.materials.append(mat_torch_fire)
    
    # Point light for torch
    bpy.ops.object.light_add(type='POINT', location=(tx, ty, bridge_thickness/2 + 1.3))
    tl = bpy.context.object
    tl.name = f"Torch_Light_{idx}"
    tl.data.energy = 50
    tl.data.color = (1.0, 0.5, 0.1)
    tl.data.shadow_soft_size = 0.2

# Add a slight fog/volume for atmosphere
world = bpy.context.scene.world
if world and world.use_nodes:
    # Add volume scatter
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    bg_node = nodes.get("Background")
    if bg_node:
        # Create volume scatter
        vol_scatter = nodes.new('ShaderNodeVolumeScatter')
        vol_scatter.inputs['Color'].default_value = (0.1, 0.08, 0.06, 1.0)
        vol_scatter.inputs['Density'].default_value = 0.02
        vol_scatter.inputs['Anisotropy'].default_value = 0.3
        
        # Connect to world output
        world_output = nodes.get("World Output")
        if world_output:
            links.new(vol_scatter.outputs['Volume'], world_output.inputs['Volume'])

print("Scene refined with additional details: torches, rocks, more fire/smoke, bridge details, arches")
