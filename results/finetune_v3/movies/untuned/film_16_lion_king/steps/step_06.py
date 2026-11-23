import bpy
import math
import random
from mathutils import Vector

# Reposition camera to a wide shot that includes the gathered animals below the rock
cam = bpy.data.objects.get('Camera')
if cam:
    cam.location = (0, -70, 12)
    cam.rotation_euler = (math.radians(87), 0, 0)
    cam.data.lens = 24

# Warm up the sun to match sunrise
sun = bpy.data.objects.get('Sun')
if sun:
    sun.data.energy = 8
    sun.data.color = (1.0, 0.55, 0.25)
    sun.rotation_euler = (math.radians(80), 0, math.radians(-30))

# Add a subtle warm fill light from the front to soften shadows
fill_data = bpy.data.lights.new('Fill', type='AREA')
fill_data.energy = 200
fill_data.color = (1.0, 0.7, 0.5)
fill_data.size = 50
fill = bpy.data.objects.new('Fill', fill_data)
bpy.context.scene.collection.objects.link(fill)
fill.location = (0, -40, 20)
fill.rotation_euler = (math.radians(70), 0, 0)

# Add a cool rim light from behind the rock for depth
rim_data = bpy.data.lights.new('Rim', type='AREA')
rim_data.energy = 150
rim_data.color = (0.6, 0.7, 1.0)
rim_data.size = 30
rim = bpy.data.objects.new('Rim', rim_data)
bpy.context.scene.collection.objects.link(rim)
rim.location = (0, 40, 30)
rim.rotation_euler = (math.radians(110), 0, 0)

# Add a few more animals to fill out the crowd below the rock
# Add gazelles
gazelle_mat = bpy.data.materials.new('Gazelle')
gazelle_mat.use_nodes = True
bsdf = gazelle_mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.6, 0.45, 0.25, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

for i in range(3):
    x = 12 + i * 4
    z = 18
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x, z, 0.9))
    body = bpy.context.active_object
    body.name = f'Gazelle{i}_body'
    body.scale = (1.4, 1, 0.7)
    body.data.materials.append(gazelle_mat)
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x + 0.7, z, 1.1))
    head = bpy.context.active_object
    head.name = f'Gazelle{i}_head'
    head.data.materials.append(gazelle_mat)
    # Legs
    for j, (lx, lz) in enumerate([(-0.25, -0.15), (-0.25, 0.15), (0.25, -0.15), (0.25, 0.15)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.6, location=(x + lx, z + lz, 0.3))
        leg = bpy.context.active_object
        leg.name = f'Gazelle{i}_leg{j}'
        leg.data.materials.append(gazelle_mat)

# Add a few more monkeys on the rock
for i in range(3):
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(2, 5)
    x = math.cos(angle) * radius
    z = math.sin(angle) * radius
    height = 18 - radius * 1.5
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x, z, height + 0.5))
    body = bpy.context.active_object
    body.name = f'RockMonkey{i}_body'
    body.scale = (1, 0.8, 1.2)
    body.data.materials.append(bpy.data.materials.get('Monkey'))
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x, z, height + 1))
    head = bpy.context.active_object
    head.name = f'RockMonkey{i}_head'
    head.data.materials.append(bpy.data.materials.get('Monkey'))

# Add a few more acacia trees in the distance
for i in range(5):
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(50, 80)
    x = math.cos(angle) * radius
    z = math.sin(angle) * radius
    scale = random.uniform(0.5, 1)
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2*scale, depth=3*scale, location=(x, z, 1.5*scale))
    trunk = bpy.context.active_object
    trunk.name = f'DistantTree{i}_trunk'
    trunk.data.materials.append(bpy.data.materials.get('Trunk'))
    # Canopy
    bpy.ops.mesh.primitive_cylinder_add(radius=2*scale, depth=0.4*scale, location=(x, z, 3.5*scale))
    canopy = bpy.context.active_object
    canopy.name = f'DistantTree{i}_canopy'
    canopy.data.materials.append(bpy.data.materials.get('Tree'))

# Add a few more birds in the sky
for i in range(10):
    x = random.uniform(-80, 80)
    y = random.uniform(-40, 40)
    z = random.uniform(40, 80)
    bpy.ops.mesh.primitive_cone_add(radius1=0.2, depth=0.4, location=(x, y, z))
    bird = bpy.context.active_object
    bird.name = f'SkyBird{i}'
    bird.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))
    bird.data.materials.append(bpy.data.materials.get('Bird'))
    # Wings
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_plane_add(size=0.3, location=(x, y + side*0.2, z))
        wing = bpy.context.active_object
        wing.name = f'SkyBird{i}_wing{side}'
        wing.rotation_euler = (0, math.radians(30*side), 0)
        wing.data.materials.append(bpy.data.materials.get('Bird'))

# Add some more grass tufts
for i in range(30):
    x = random.uniform(-50, 50)
    z = random.uniform(-50, 50)
    if abs(x) > 22 or abs(z) > 22:
        bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.4, location=(x, z, 0.2))
        grass = bpy.context.active_object
        grass.name = f'GrassC{i}'
        grass.data.materials.append(bpy.data.materials.get('Grass'))

# Add a few more small rocks
for i in range(15):
    x = random.uniform(-40, 40)
    z = random.uniform(-40, 40)
    if abs(x) > 22 or abs(z) > 22:
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.3, subdivisions=1, location=(x, z, 0.15))
        rock = bpy.context.active_object
        rock.name = f'RockC{i}'
        rock.scale = (random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), random.uniform(0.3, 0.8))
        rock.data.materials.append(bpy.data.materials.get('Rock'))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()

print("Added more detail!")
print(f"Total objects: {len(bpy.data.objects)}")
