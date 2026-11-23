import bpy
import math
import random
from mathutils import Vector

# The scene is looking better but the camera is too far away and the stone circle 
# with the three gunmen is not clearly visible. Let's zoom in and add more detail.

# Reposition camera closer to the action
scene = bpy.context.scene
cam = scene.camera
if cam:
    cam.location = (2, -8, 2.5)
    cam.data.lens = 60
    target = Vector((0, 0, 1.0))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

# Get materials
def get_mat(name):
    return bpy.data.materials.get(name)

stone_mat = get_mat("Stone")
cemetery_stone_mat = get_mat("CemeteryStone")
dirt_mat = get_mat("Dirt")
wood_mat = get_mat("Wood")
metal_mat = get_mat("Metal")
coat_mat = get_mat("Coat")
skin_mat = get_mat("Skin")
hat_mat = get_mat("Hat")
pants_mat = get_mat("Pants")
boot_mat = get_mat("Boot")
hair_mat = get_mat("Hair")
scarf_mat = get_mat("Scarf")
grass_mat = get_mat("Grass")
cross_mat = get_mat("Cross")
horse_mat = get_mat("Horse")
bone_mat = get_mat("Bone")

# The three gunmen need to be more visible. Let's check if they exist and enhance them.
# The gunmen were created earlier but might be small. Let's add some more prominent figures.

# Actually, let's add some more detail to make the scene feel more alive

# Add more scattered debris
for i in range(30):
    x = random.uniform(-8, 8)
    y = random.uniform(-8, 8)
    if math.sqrt(x*x + y*y) < 7:
        continue
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.03, 0.12), 
        location=(x, y, 0.03))
    debris = bpy.context.active_object
    debris.scale = (random.uniform(0.5, 1.2), random.uniform(0.5, 1.2), random.uniform(0.3, 0.6))
    if debris.data.materials:
        pass
    else:
        debris.data.materials.append(stone_mat)

# Add more grass tufts very close to the camera
for i in range(100):
    x = random.uniform(-6, 6)
    y = random.uniform(-6, 2)
    if math.sqrt(x*x + y*y) < 7:
        continue
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.015, radius2=0.001, depth=0.06, 
        location=(x, y, 0.03))
    grass = bpy.context.active_object
    grass.scale = (1, 1, random.uniform(0.5, 1.3))
    grass.data.materials.append(grass_mat)

# Add a few more small rocks in the foreground
for i in range(20):
    x = random.uniform(-5, 5)
    y = random.uniform(-5, 3)
    if math.sqrt(x*x + y*y) < 7:
        continue
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.03, 0.08), 
        location=(x, y, 0.03))
    rock = bpy.context.active_object
    rock.scale = (random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.3, 0.5))
    rock.data.materials.append(stone_mat)

# Add some more headstones very close
for i in range(8):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(7, 10)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    if y > 0:
        continue
    
    height = random.uniform(0.4, 0.7)
    width = random.uniform(0.2, 0.35)
    
    bpy.ops.mesh.primitive_cube_add(location=(x, y, height/2))
    hs = bpy.context.active_object
    hs.scale = (width/2, 0.05, height/2)
    hs.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
    hs.data.materials.append(cemetery_stone_mat)

# Add a small dirt path
for i in range(15):
    y = -7 + i * 0.5
    x = random.uniform(-0.2, 0.2)
    if y < -5:
        bpy.ops.mesh.primitive_plane_add(size=0.8, location=(x, y, 0.005))
        path = bpy.context.active_object
        path.data.materials.append(dirt_mat)

# Add some fallen leaves/debris
leaf_mat = get_mat("Grass")
for i in range(50):
    x = random.uniform(-8, 8)
    y = random.uniform(-8, 8)
    if math.sqrt(x*x + y*y) < 7:
        continue
    
    bpy.ops.mesh.primitive_plane_add(size=0.04, location=(x, y, 0.01))
    leaf = bpy.context.active_object
    leaf.rotation_euler = (math.radians(90), 0, random.uniform(0, 2*math.pi))
    leaf.data.materials.append(leaf_mat)

# Add a few more distant trees
for i in range(10):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(35, 55)
    x = dist * math.cos(angle)
    y = dist * math.sin(angle)
    
    trunk_height = random.uniform(2, 4)
    bpy.ops.mesh.primitive_cylinder_add(radius=random.uniform(0.08, 0.15), 
        depth=trunk_height, location=(x, y, trunk_height/2))
    trunk = bpy.context.active_object
    trunk.data.materials.append(wood_mat)
    
    for j in range(random.randint(2, 4)):
        branch_height = trunk_height * random.uniform(0.5, 0.85)
        branch_angle = random.uniform(0, 2 * math.pi)
        branch_len = random.uniform(0.4, 1.2)
        bx = x + branch_len * 0.5 * math.cos(branch_angle)
        by = y + branch_len * 0.5 * math.sin(branch_angle)
        bz = branch_height
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=branch_len, 
            location=(bx, by, bz))
        branch = bpy.context.active_object
        branch.rotation_euler = (
            random.uniform(-0.6, 0.6), 
            random.uniform(-0.6, 0.6), 
            0
        )
        branch.data.materials.append(wood_mat)

# Add a small cairn
cairn_x, cairn_y = -4, -2
for i in range(3):
    sz = 0.1 - i * 0.01
    bpy.ops.mesh.primitive_cube_add(location=(cairn_x, cairn_y, 0.03 + i * 0.08))
    cstone = bpy.context.active_object
    cstone.scale = (sz, sz * 0.7, 0.04)
    cstone.rotation_euler = (0, 0, random.uniform(0, 2*math.pi))
    cstone.data.materials.append(stone_mat)

# Final camera adjustment - make sure we're looking at the stone circle
if scene.camera:
    cam = scene.camera
    cam.location = (2, -8, 2.5)
    cam.data.lens = 60
    target = Vector((0, 0, 1.0))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

# Render settings
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.view_settings.look = 'AgX - High Contrast'
scene.view_settings.exposure = -0.2

print("Final refinements applied")
print("Total objects:", len(bpy.data.objects))
