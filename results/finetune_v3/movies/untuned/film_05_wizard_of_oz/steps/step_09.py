import bpy, math, random

# Remove the sun glow sphere (too bright/large)
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.dimensions.x > 5 and obj.location.z > 30:
        bpy.data.objects.remove(obj, do_unlink=True)

# Remove remaining fence rails
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.dimensions.x > 3 and obj.dimensions.y < 1.5 and obj.dimensions.z < 1.5:
        if abs(obj.location.z) < 2 and abs(obj.location.x) < 6:
            bpy.data.objects.remove(obj, do_unlink=True)

# Remove shadow planes (they look like dark spots)
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.dimensions.x < 1.5 and obj.dimensions.y < 1.5 and obj.dimensions.z < 0.1:
        if obj.location.z < 0.05:
            bpy.data.objects.remove(obj, do_unlink=True)

# Add a subtle warm light to enhance the golden hour feel
wl = bpy.data.lights.new("WarmFill",'AREA'); wl.energy=50; wl.color=(1,.8,.5)
wo = bpy.data.objects.new("WarmFill",wl); bpy.context.collection.objects.link(wo)
wo.location = (15,-15,8); wo.rotation_euler = (math.radians(50),math.radians(20),0)

# Add a few more trees in the mid-ground
m_trunk = bpy.data.materials.get("Trunk")
m_tree = bpy.data.materials.get("Tree")
if m_trunk and m_tree:
    random.seed(300)
    for i in range(6):
        s = random.choice([-1,1]); tx = s*random.uniform(12,22); ty = random.uniform(-35,-10)
        th = random.uniform(2.5,5)
        bpy.ops.mesh.primitive_cylinder_add(radius=.25, depth=th, location=(tx,ty,th/2))
        bpy.context.active_object.data.materials.append(m_trunk)
        for k in range(3):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(1,2), location=(tx+random.uniform(-.8,.8), ty+random.uniform(-.8,.8), th+random.uniform(0,1.5)))
            bpy.context.active_object.data.materials.append(m_tree)

# Add a small bush near the well
m_bush = bpy.data.materials.get("Tree")
if m_bush:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.6, location=(6,-19,.4))
    bs = bpy.context.active_object; bs.scale=(1,1,.7); bs.data.materials.append(m_bush)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.5, location=(5.5,-19.5,.35))
    bs2 = bpy.context.active_object; bs2.scale=(1,1,.7); bs2.data.materials.append(m_bush)

# Final camera
cam = bpy.data.objects.get("Cam")
if cam:
    cam.location = (0, -32, 5.5)
    cam.rotation_euler = (math.radians(86), 0, 0)
    cam.data.lens = 32
