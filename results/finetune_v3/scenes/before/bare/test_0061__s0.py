import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
def mat(name, color=(0.5, 0.5, 0.5, 1.0), metallic=0.0, roughness=0.5, emission=0.0, emit_color=(1,1,1,1)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = emit_color
        bsdf.inputs["Emission Strength"].default_value = emission
    return m

mat_cinema_wall = mat("CinemaWall", (0.15, 0.12, 0.18, 1.0), 0.0, 0.7)
mat_cinema_roof = mat("CinemaRoof", (0.08, 0.06, 0.10, 1.0), 0.0, 0.6)
mat_marquee_frame = mat("MarqueeFrame", (0.9, 0.85, 0.6, 1.0), 0.8, 0.3)
mat_marquee_holo = mat("MarqueeHolo", (0.2, 0.9, 1.0, 1.0), 0.0, 0.1, emission=2.5, emit_color=(0.2, 0.9, 1.0, 1.0))
mat_marquee_holo2 = mat("MarqueeHolo2", (1.0, 0.3, 0.9, 1.0), 0.0, 0.1, emission=2.5, emit_color=(1.0, 0.3, 0.9, 1.0))
mat_booth = mat("TicketBooth", (0.3, 0.15, 0.4, 1.0), 0.0, 0.4)
mat_booth_glass = mat("BoothGlass", (0.7, 0.85, 1.0, 0.3), 0.0, 0.1)
mat_poster_bg = mat("PosterBG", (0.9, 0.85, 0.7, 1.0), 0.0, 0.8)
mat_poster_art1 = mat("PosterArt1", (0.9, 0.2, 0.1, 1.0), 0.0, 0.6)
mat_poster_art2 = mat("PosterArt2", (0.1, 0.5, 0.9, 1.0), 0.0, 0.6)
mat_poster_art3 = mat("PosterArt3", (0.1, 0.8, 0.3, 1.0), 0.0, 0.6)
mat_ground = mat("Ground", (0.1, 0.1, 0.12, 1.0), 0.0, 0.8)
mat_person = mat("Person", (0.4, 0.3, 0.35, 1.0), 0.0, 0.7)
mat_person_head = mat("PersonHead", (0.7, 0.5, 0.4, 1.0), 0.0, 0.6)
mat_drone_body = mat("DroneBody", (0.2, 0.2, 0.25, 1.0), 0.7, 0.3)
mat_drone_popcorn = mat("DronePopcorn", (0.95, 0.85, 0.5, 1.0), 0.0, 0.5, emission=0.5, emit_color=(1.0, 0.9, 0.5, 1.0))
mat_drone_light = mat("DroneLight", (0.0, 1.0, 0.5, 1.0), 0.0, 0.1, emission=3.0, emit_color=(0.0, 1.0, 0.5, 1.0))
mat_red_carpet = mat("RedCarpet", (0.6, 0.05, 0.05, 1.0), 0.0, 0.7)
mat_step = mat("Step", (0.2, 0.18, 0.22, 1.0), 0.0, 0.6)

# --- Ground ---
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat_ground)

# --- Cinema Building ---
# Main structure
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, 5))
bpy.context.active_object.scale = (12, 6, 5)
bpy.context.active_object.data.materials.append(mat_cinema_wall)
bpy.context.active_object.name = "CinemaBuilding"

# Roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, 10.3))
bpy.context.active_object.scale = (12.5, 6.5, 0.5)
bpy.context.active_object.data.materials.append(mat_cinema_roof)
bpy.context.active_object.name = "CinemaRoof"

# Entrance steps
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 8.5 - i*0.5, 0.25 + i*0.0))
    bpy.context.active_object.scale = (8, 0.5, 0.5)
    bpy.context.active_object.location.z = 0.25 + i * 0.15
    bpy.context.active_object.data.materials.append(mat_step)
    bpy.context.active_object.name = f"Step_{i}"

# Red carpet
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4, 0.1))
bpy.context.active_object.scale = (4, 12, 0.1)
bpy.context.active_object.data.materials.append(mat_red_carpet)
bpy.context.active_object.name = "RedCarpet"

# --- Holographic Marquee ---
# Frame
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 8, 8))
bpy.context.active_object.scale = (10, 0.5, 3)
bpy.context.active_object.data.materials.append(mat_marquee_frame)
bpy.context.active_object.name = "MarqueeFrame"

# Holo panels (floating text-like blocks)
random.seed(42)
for i in range(8):
    x = -4.5 + i * 1.3
    y = 7.5
    z = 7.5 + random.uniform(-0.5, 0.5)
    h = random.uniform(0.5, 1.5)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    bpy.context.active_object.scale = (0.8, 0.1, h)
    mat_choice = mat_marquee_holo if i % 2 == 0 else mat_marquee_holo2
    bpy.context.active_object.data.materials.append(mat_choice)
    bpy.context.active_object.name = f"HoloPanel_{i}"
    # Slight rotation for holo effect
    bpy.context.active_object.rotation_euler[1] = random.uniform(-0.1, 0.1)

# Holo ring accent
bpy.ops.mesh.primitive_torus_add(location=(0, 7.5, 9.5), major_radius=5, minor_radius=0.15)
bpy.context.active_object.data.materials.append(mat_marquee_holo)
bpy.context.active_object.name = "HoloRing"
bpy.context.active_object.rotation_euler[0] = math.pi / 2

# --- Ticket Booth ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, 7, 2))
bpy.context.active_object.scale = (2.5, 1.5, 2)
bpy.context.active_object.data.materials.append(mat_booth)
bpy.context.active_object.name = "TicketBooth"

# Booth window (glass)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, 5.5, 2.2))
bpy.context.active_object.scale = (1.5, 0.1, 1.0)
bpy.context.active_object.data.materials.append(mat_booth_glass)
bpy.context.active_object.name = "BoothWindow"

# Booth roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, 7, 4.2))
bpy.context.active_object.scale = (3, 2, 0.3)
bpy.context.active_object.data.materials.append(mat_marquee_frame)
bpy.context.active_object.name = "BoothRoof"

# Booth sign
bpy.ops.mesh.primitive_cube_add(size=1, location=(-8, 5.4, 3.5))
bpy.context.active_object.scale = (1.8, 0.1, 0.6)
bpy.context.active_object.data.materials.append(mat_marquee_holo2)
bpy.context.active_object.name = "BoothSign"

# --- Posters ---
poster_positions = [(-5, 8.2, 2), (-3, 8.2, 2), (3, 8.2, 2), (5, 8.2, 2)]
poster_mats = [mat_poster_art1, mat_poster_art2, mat_poster_art3, mat_poster_art1]
for i, (px, py, pz) in enumerate(poster_positions):
    # Poster frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, pz))
    bpy.context.active_object.scale = (1.5, 0.1, 2.0)
    bpy.context.active_object.data.materials.append(mat_marquee_frame)
    bpy.context.active_object.name = f"PosterFrame_{i}"
    # Poster art
    bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py - 0.05, pz))
    bpy.context.active_object.scale = (1.3, 0.1, 1.8)
    bpy.context.active_object.data.materials.append(poster_mats[i])
    bpy.context.active_object.name = f"PosterArt_{i}"

# --- Evening Queue (people) ---
random.seed(123)
queue_length = 25
start_y = 5
for i in range(queue_length):
    y = start_y - i * 1.2
    x = random.uniform(-2, 2)
    z_base = 0.5

    # Body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.2, location=(x, y, z_base + 0.6))
    bpy.context.active_object.data.materials.append(mat_person)
    bpy.context.active_object.name = f"PersonBody_{i}"

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(x, y, z_base + 1.4))
    bpy.context.active_object.data.materials.append(mat_person_head)
    bpy.context.active_object.name = f"PersonHead_{i}"

# --- Popcorn Vending Drones ---
drone_positions = [
    (3, 6, 4), (-3, 8, 5), (5, 4, 3.5), (-5, 10, 4.5), (0, 3, 5), (4, 9, 3.8), (-2, 5, 4.2)
]
for i, (dx, dy, dz) in enumerate(drone_positions):
    # Drone body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(dx, dy, dz))
    bpy.context.active_object.scale = (0.6, 0.6, 0.3)
    bpy.context.active_object.data.materials.append(mat_drone_body)
    bpy.context.active_object.name = f"DroneBody_{i}"

    # Popcorn container (glowing)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.4, location=(dx, dy, dz - 0.35))
    bpy.context.active_object.data.materials.append(mat_drone_popcorn)
    bpy.context.active_object.name = f"DronePopcorn_{i}"

    # Drone light
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(dx, dy, dz + 0.25))
    bpy.context.active_object.data.materials.append(mat_drone_light)
    bpy.context.active_object.name = f"DroneLight_{i}"

    # Rotor arms
    for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
        arm_x = dx + 0.5 * math.cos(angle)
        arm_y = dy + 0.5 * math.sin(angle)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.5, location=(arm_x, arm_y, dz))
        bpy.context.active_object.rotation_euler = (0, math.pi/2, angle)
        bpy.context.active_object.data.materials.append(mat_drone_body)
        bpy.context.active_object.name = f"DroneArm_{i}_{int(angle*2)}"

# --- Lighting (evening atmosphere) ---
# Sun (low, warm evening light)
sun_data = bpy.data.lights.new("EveningSun", type='SUN')
sun_data.energy = 1.5
sun_data.color = (1.0, 0.6, 0.3)
sun_obj = bpy.data.objects.new("EveningSun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(60), 0, math.radians(135))

# Marquee point lights
for lx in [-3, 0, 3]:
    light_data = bpy.data.lights.new(f"MarqueeLight_{lx}", type='POINT')
    light_data.energy = 50
    light_data.color = (0.3, 0.8, 1.0)
    light_obj = bpy.data.objects.new(f"MarqueeLight_{lx}", light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (lx, 7, 8)

# Booth light
light_data = bpy.data.lights.new("BoothLight", type='POINT')
light_data.energy = 30
light_data.color = (1.0, 0.5, 0.9)
light_obj = bpy.data.objects.new("BoothLight", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (-8, 6, 4)

# Ambient fill
light_data = bpy.data.lights.new("AmbientFill", type='POINT')
light_data.energy = 10
light_data.color = (0.5, 0.4, 0.8)
light_obj = bpy.data.objects.new("AmbientFill", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (0, 0, 15)

# --- World (dark evening sky) ---
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.02, 0.02, 0.05, 1.0)
bg.inputs[1].default_value = 1.0

# --- Camera ---
cam_data = bpy.data.cameras.new("CinemaCam")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("CinemaCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0, -15, 5)
cam_obj.rotation_euler = (math.radians(85), 0, 0)
bpy.context.scene.camera = cam_obj

# --- Render settings ---
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
