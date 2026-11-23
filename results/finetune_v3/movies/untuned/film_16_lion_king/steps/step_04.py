import bpy
import math
import random
from mathutils import Vector

# Fix the camera to see the animals and rock better
cam = bpy.data.objects.get('Camera')
if cam:
    cam.location = (0, -100, 30)
    cam.rotation_euler = (math.radians(80), 0, 0)
    cam.data.lens = 28

# Add more animals that are currently missing or need to be visible
# Add more elephants
for i in range(2):
    x = -15 + i * 10
    z = 18
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(x, z, 2))
    body = bpy.context.active_object
    body.name = f'ElephantB{i}_body'
    body.scale = (1.5, 1, 1)
    body.data.materials.append(bpy.data.materials.get('Elephant'))
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(x + 2, z, 2.5))
    head = bpy.context.active_object
    head.name = f'ElephantB{i}_head'
    head.data.materials.append(bpy.data.materials.get('Elephant'))
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.5, location=(x + 2.5, z, 1.5))
    trunk = bpy.context.active_object
    trunk.name = f'ElephantB{i}_trunk'
    trunk.rotation_euler = (math.radians(30), 0, 0)
    trunk.data.materials.append(bpy.data.materials.get('Elephant'))
    # Ears
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x + 1.5, z + side*0.8, 2.5))
        ear = bpy.context.active_object
        ear.name = f'ElephantB{i}_ear{side}'
        ear.scale = (0.5, 0.8, 1)
        ear.rotation_euler = (0, math.radians(20*side), 0)
        ear.data.materials.append(bpy.data.materials.get('Elephant'))
    # Legs
    for j, (lx, lz) in enumerate([(-1, -0.8), (-1, 0.8), (1, -0.8), (1, 0.8)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.5, location=(x + lx, z + lz, 0.75))
        leg = bpy.context.active_object
        leg.name = f'ElephantB{i}_leg{j}'
        leg.data.materials.append(bpy.data.materials.get('Elephant'))

# Add more giraffes
for i in range(2):
    x = 15 + i * 5
    z = 15
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, z, 3))
    body = bpy.context.active_object
    body.name = f'GiraffeB{i}_body'
    body.scale = (1.5, 1, 1)
    body.data.materials.append(bpy.data.materials.get('Giraffe'))
    # Neck
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=3, location=(x + 1.5, z, 4.5))
    neck = bpy.context.active_object
    neck.name = f'GiraffeB{i}_neck'
    neck.rotation_euler = (0, math.radians(-20), 0)
    neck.data.materials.append(bpy.data.materials.get('Giraffe'))
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x + 2, z, 6))
    head = bpy.context.active_object
    head.name = f'GiraffeB{i}_head'
    head.data.materials.append(bpy.data.materials.get('Giraffe'))
    # Ossicones
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=(x + 2 + side*0.1, z, 6.3))
        oss = bpy.context.active_object
        oss.name = f'GiraffeB{i}_oss{side}'
        oss.data.materials.append(bpy.data.materials.get('GiraffeSpot'))
    # Legs
    for j, (lx, lz) in enumerate([(-1, -0.5), (-1, 0.5), (1, -0.5), (1, 0.5)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2.5, location=(x + lx, z + lz, 1.25))
        leg = bpy.context.active_object
        leg.name = f'GiraffeB{i}_leg{j}'
        leg.data.materials.append(bpy.data.materials.get('Giraffe'))

# Add more zebras
for i in range(3):
    x = -10 + i * 6
    z = 22
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(x, z, 1.2))
    body = bpy.context.active_object
    body.name = f'ZebraB{i}_body'
    body.scale = (1.5, 1, 0.8)
    body.data.materials.append(bpy.data.materials.get('Zebra'))
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x + 1.2, z, 1.5))
    head = bpy.context.active_object
    head.name = f'ZebraB{i}_head'
    head.data.materials.append(bpy.data.materials.get('Zebra'))
    # Legs
    for j, (lx, lz) in enumerate([(-0.5, -0.3), (-0.5, 0.3), (0.5, -0.3), (0.5, 0.3)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1, location=(x + lx, z + lz, 0.5))
        leg = bpy.context.active_object
        leg.name = f'ZebraB{i}_leg{j}'
        leg.data.materials.append(bpy.data.materials.get('Zebra'))

# Add more wildebeests
for i in range(3):
    x = -5 + i * 5
    z = 28
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(x, z, 1))
    body = bpy.context.active_object
    body.name = f'WildebeestB{i}_body'
    body.scale = (1.5, 1, 0.8)
    body.data.materials.append(bpy.data.materials.get('Wildebeest'))
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(x + 1, z, 1.2))
    head = bpy.context.active_object
    head.name = f'WildebeestB{i}_head'
    head.data.materials.append(bpy.data.materials.get('Wildebeest'))
    # Horns
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.4, location=(x + 1, z + side*0.15, 1.4))
        horn = bpy.context.active_object
        horn.name = f'WildebeestB{i}_horn{side}'
        horn.rotation_euler = (0, math.radians(45*side), 0)
        horn.data.materials.append(bpy.data.materials.get('Buffalo'))
    # Legs
    for j, (lx, lz) in enumerate([(-0.4, -0.2), (-0.4, 0.2), (0.4, -0.2), (0.4, 0.2)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.8, location=(x + lx, z + lz, 0.4))
        leg = bpy.context.active_object
        leg.name = f'WildebeestB{i}_leg{j}'
        leg.data.materials.append(bpy.data.materials.get('Wildebeest'))

# Add more buffaloes
for i in range(2):
    x = 8 + i * 5
    z = 25
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, z, 1.2))
    body = bpy.context.active_object
    body.name = f'BuffaloB{i}_body'
    body.scale = (1.5, 1, 1)
    body.data.materials.append(bpy.data.materials.get('Buffalo'))
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x + 1.5, z, 1.5))
    head = bpy.context.active_object
    head.name = f'BuffaloB{i}_head'
    head.data.materials.append(bpy.data.materials.get('Buffalo'))
    # Horns
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.5, location=(x + 1.5, z + side*0.3, 1.8))
        horn = bpy.context.active_object
        horn.name = f'BuffaloB{i}_horn{side}'
        horn.rotation_euler = (0, math.radians(60*side), 0)
        horn.data.materials.append(bpy.data.materials.get('Buffalo'))
    # Legs
    for j, (lx, lz) in enumerate([(-0.8, -0.5), (-0.8, 0.5), (0.8, -0.5), (0.8, 0.5)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1, location=(x + lx, z + lz, 0.5))
        leg = bpy.context.active_object
        leg.name = f'BuffaloB{i}_leg{j}'
        leg.data.materials.append(bpy.data.materials.get('Buffalo'))

# Add more acacia trees
for i in range(4):
    angle = i * math.pi / 2 + 1
    x = math.cos(angle) * 40
    z = math.sin(angle) * 40
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=4, location=(x, z, 2))
    trunk = bpy.context.active_object
    trunk.name = f'AcaciaB{i}_trunk'
    trunk.data.materials.append(bpy.data.materials.get('Trunk'))
    # Canopy
    bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=0.5, location=(x, z, 4.5))
    canopy = bpy.context.active_object
    canopy.name = f'AcaciaB{i}_canopy'
    canopy.data.materials.append(bpy.data.materials.get('Tree'))

# Add more birds
for i in range(10):
    x = random.uniform(-60, 60)
    y = random.uniform(-30, 30)
    z = random.uniform(35, 70)
    bpy.ops.mesh.primitive_cone_add(radius1=0.3, depth=0.5, location=(x, y, z))
    bird = bpy.context.active_object
    bird.name = f'BirdB{i}'
    bird.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))
    bird.data.materials.append(bpy.data.materials.get('Bird'))
    # Wings
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_plane_add(size=0.4, location=(x, y + side*0.3, z))
        wing = bpy.context.active_object
        wing.name = f'BirdB{i}_wing{side}'
        wing.rotation_euler = (0, math.radians(30*side), 0)
        wing.data.materials.append(bpy.data.materials.get('Bird'))

# Add more ground rocks
for i in range(15):
    x = random.uniform(-50, 50)
    z = random.uniform(-50, 50)
    if abs(x) > 25 or abs(z) > 25:
        bpy.ops.mesh.primitive_ico_sphere_add(radius=1, subdivisions=1, location=(x, z, 0))
        rock = bpy.context.active_object
        rock.name = f'GroundRock{i}'
        rock.scale = (random.uniform(0.5, 2), random.uniform(0.5, 2), random.uniform(0.3, 1))
        rock.data.materials.append(bpy.data.materials.get('Rock'))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        mod = rock.modifiers.new('Displace', 'DISPLACE')
        tex = bpy.data.textures.new(f'GroundRock{i}_tex', type='CLOUDS')
        tex.noise_scale = 0.5
        mod.texture = tex
        mod.strength = 0.3
        bpy.ops.object.modifier_apply(modifier='Displace')
        bpy.ops.object.shade_smooth()

# Add more grass tufts
for i in range(40):
    x = random.uniform(-50, 50)
    z = random.uniform(-50, 50)
    if abs(x) > 25 or abs(z) > 25:
        bpy.ops.mesh.primitive_cone_add(radius1=0.1, depth=0.5, location=(x, z, 0.25))
        grass = bpy.context.active_object
        grass.name = f'GrassB{i}'
        grass.data.materials.append(bpy.data.materials.get('Grass'))

# Add a few more lions in the crowd (other pride members)
for i in range(2):
    x = -3 + i * 6
    z = 10
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, z, 1.5))
    body = bpy.context.active_object
    body.name = f'LionC{i}_body'
    body.scale = (1.5, 1, 0.8)
    body.data.materials.append(bpy.data.materials.get('Lion'))
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(x + 1.5, z, 2))
    head = bpy.context.active_object
    head.name = f'LionC{i}_head'
    head.data.materials.append(bpy.data.materials.get('Lion'))
    # Mane
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(x + 1.5, z, 2))
    mane = bpy.context.active_object
    mane.name = f'LionC{i}_mane'
    mane.scale = (1.2, 1.2, 1.2)
    mane.data.materials.append(bpy.data.materials.get('LionMane'))
    # Legs
    for j, (lx, lz) in enumerate([(-0.8, -0.5), (-0.8, 0.5), (0.8, -0.5), (0.8, 0.5)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1, location=(x + lx, z + lz, 0.75))
        leg = bpy.context.active_object
        leg.name = f'LionC{i}_leg{j}'
        leg.data.materials.append(bpy.data.materials.get('Lion'))
    # Tail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.5, location=(x - 1.5, z, 1.5))
    tail = bpy.context.active_object
    tail.name = f'LionC{i}_tail'
    tail.rotation_euler = (0, math.radians(45), 0)
    tail.data.materials.append(bpy.data.materials.get('Lion'))

print("Added more detail!")
print(f"Total objects: {len(bpy.data.objects)}")
