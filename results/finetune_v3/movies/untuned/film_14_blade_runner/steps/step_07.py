import bpy
import math
import random
from mathutils import Vector

# Fix camera to look down the street properly
camera = bpy.data.objects.get("Camera")
if camera:
    camera.location = (0, 1.5, 15)
    camera.rotation_euler = (math.radians(85), 0, 0)
    camera.data.lens = 50

# Add more neon signs at street level
mat_neon_pink = bpy.data.materials.get("Neon_Pink")
mat_neon_cyan = bpy.data.materials.get("Neon_Cyan")
mat_neon_yellow = bpy.data.materials.get("Neon_Yellow")
mat_neon_green = bpy.data.materials.get("Neon_Green")
mat_neon_purple = bpy.data.materials.get("Neon_Purple")
mat_neon_red = bpy.data.materials.get("Neon_Red")

def create_neon_sign_simple(x, y, z, width, height, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
    sign = bpy.context.active_object
    sign.scale = (width/2, height/2, 1)
    sign.rotation_euler = (math.pi/2, 0, 0)
    sign.data.materials.append(mat)
    return sign

# More street level neon
create_neon_sign_simple(-8, 2, 8, 3, 1, mat_neon_pink)
create_neon_sign_simple(8, 2, 8, 3, 1, mat_neon_cyan)
create_neon_sign_simple(-8, 3, 12, 4, 1.2, mat_neon_yellow)
create_neon_sign_simple(8, 3, 12, 4, 1.2, mat_neon_green)
create_neon_sign_simple(-8, 4, 16, 5, 1.5, mat_neon_purple)
create_neon_sign_simple(8, 4, 16, 5, 1.5, mat_neon_red)

# Add more people
mat_umbrella = bpy.data.materials.get("Umbrella")
mat_umbrella2 = bpy.data.materials.get("Umbrella2")
mat_umbrella3 = bpy.data.materials.get("Umbrella3")
mat_person = bpy.data.materials.get("Person")
mat_person2 = bpy.data.materials.get("Person2")
mat_metal = bpy.data.materials.get("Metal")

def create_person_simple(x, z, umbrella_mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.5, location=(x, 0.75, z))
    body = bpy.context.active_object
    body.data.materials.append(random.choice([mat_person, mat_person2]))
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x, 1.7, z))
    head = bpy.context.active_object
    head.data.materials.append(mat_person)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0.1, depth=0.5, location=(x, 2.2, z))
    umbrella = bpy.context.active_object
    umbrella.data.materials.append(umbrella_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1, location=(x, 1.7, z))
    handle = bpy.context.active_object
    handle.data.materials.append(mat_metal)

for i in range(15):
    x = random.uniform(-15, 15)
    z = random.uniform(3, 20)
    if abs(x) < 3:
        x += 4 * (1 if x > 0 else -1)
    create_person_simple(x, z, random.choice([mat_umbrella, mat_umbrella2, mat_umbrella3]))

# Add more neon lights
neon_light_data = [
    (-8, 2, 8, (1, 0.1, 0.3)),
    (8, 2, 8, (0.1, 0.8, 1)),
    (-8, 3, 12, (1, 0.9, 0.1)),
    (8, 3, 12, (0.1, 1, 0.3)),
    (-8, 4, 16, (0.6, 0.1, 1)),
    (8, 4, 16, (1, 0.1, 0.1)),
]

for x, y, z, color in neon_light_data:
    bpy.ops.object.light_add(type='POINT', location=(x, y, z))
    light = bpy.context.active_object
    light.data.energy = 15
    light.data.color = color
    light.data.shadow_soft_size = 0.3

print("Added more detail!")
