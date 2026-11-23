import bpy, math, random

# Remove remaining fence rails crossing the road
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.dimensions.x > 5 and obj.dimensions.y < 1 and obj.dimensions.z < 1:
        if abs(obj.location.z) < 1.5 and abs(obj.location.x) < 4:
            bpy.data.objects.remove(obj, do_unlink=True)

# Add a distant rainbow arc
m_rainbow = bpy.data.materials.new("Rainbow")
m_rainbow.use_nodes = True
m_rainbow.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1,0.5,0,1)
m_rainbow.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0.3

bpy.ops.mesh.primitive_torus_add(major_radius=30, minor_radius=0.5, location=(0, 80, 10), major_segments=64, minor_segments=8)
rb = bpy.context.active_object
rb.rotation_euler = (0, math.radians(90), 0)
rb.scale = (1, 1, 0.4)
rb.data.materials.append(m_rainbow)

# Add a second rainbow band
m_rainbow2 = bpy.data.materials.new("Rainbow2")
m_rainbow2.use_nodes = True
m_rainbow2.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,0.5,1,1)
m_rainbow2.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0.3

bpy.ops.mesh.primitive_torus_add(major_radius=28, minor_radius=0.5, location=(0, 80, 10), major_segments=64, minor_segments=8)
rb2 = bpy.context.active_object
rb2.rotation_euler = (0, math.radians(90), 0)
rb2.scale = (1, 1, 0.4)
rb2.data.materials.append(m_rainbow2)

# Add a third rainbow band
m_rainbow3 = bpy.data.materials.new("Rainbow3")
m_rainbow3.use_nodes = True
m_rainbow3.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0,1,0,1)
m_rainbow3.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0.3

bpy.ops.mesh.primitive_torus_add(major_radius=26, minor_radius=0.5, location=(0, 80, 10), major_segments=64, minor_segments=8)
rb3 = bpy.context.active_object
rb3.rotation_euler = (0, math.radians(90), 0)
rb3.scale = (1, 1, 0.4)
rb3.data.materials.append(m_rainbow3)

# Add more detailed Emerald City: flag on top
m_flag = bpy.data.materials.new("Flag")
m_flag.use_nodes = True
m_flag.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1,0,0,1)
m_flag.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .5

bpy.ops.mesh.primitive_cylinder_add(radius=.03, depth=3, location=(0,55,17))
fp = bpy.context.active_object; fp.data.materials.append(bpy.data.materials.get("Trunk"))
bpy.ops.mesh.primitive_plane_add(size=.8, location=(.4,55,17.5))
flg = bpy.context.active_object; flg.rotation_euler=(0,math.radians(90),0); flg.data.materials.append(m_flag)

# Add a second smaller tower to the city
m_city = bpy.data.materials.get("City")
if m_city:
    bpy.ops.mesh.primitive_cylinder_add(radius=2, depth=8, location=(-10,58,4))
    bpy.context.active_object.data.materials.append(m_city)
    bpy.ops.mesh.primitive_cone_add(radius1=2.2, radius2=0, depth=3, location=(-10,58,10))
    bpy.context.active_object.data.materials.append(m_city)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=2, depth=8, location=(10,58,4))
    bpy.context.active_object.data.materials.append(m_city)
    bpy.ops.mesh.primitive_cone_add(radius1=2.2, radius2=0, depth=3, location=(10,58,10))
    bpy.context.active_object.data.materials.append(m_city)

# Add a walking stick for the Scarecrow
m_wood = bpy.data.materials.get("Fence")
if m_wood:
    bpy.ops.mesh.primitive_cylinder_add(radius=.03, depth=1.5, location=(.8,-12,.75))
    ws = bpy.context.active_object; ws.rotation_euler=(0,math.radians(10),0); ws.data.materials.append(m_wood)

# Add a small bird on the fence
m_bird = bpy.data.materials.new("Bird")
m_bird.use_nodes = True
m_bird.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.2,.2,.3,1)

bpy.ops.mesh.primitive_uv_sphere_add(radius=.08, location=(-3.2,-16,1.1))
bd = bpy.context.active_object; bd.scale=(1,1.2,.8); bd.data.materials.append(m_bird)
bpy.ops.mesh.primitive_cone_add(radius1=.04, radius2=0, depth=.08, location=(-3.2,-15.9,1.1))
beak = bpy.context.active_object; beak.rotation_euler=(math.radians(-90),0,0); beak.data.materials.append(m_bird)

# Add subtle ground detail: small grass tufts
m_grass_tuft = bpy.data.materials.get("Grass")
if m_grass_tuft:
    random.seed(123)
    for i in range(50):
        s = random.choice([-1,1])
        x = s*random.uniform(3,25); y = random.uniform(-45,45)
        for j in range(3):
            bpy.ops.mesh.primitive_cone_add(radius1=.03, radius2=0, depth=.15, location=(x+random.uniform(-.1,.1), y+random.uniform(-.1,.1), .07))
            gt = bpy.context.active_object
            gt.rotation_euler = (random.uniform(-.3,.3), random.uniform(-.3,.3), random.uniform(0,6.28))
            gt.data.materials.append(m_grass_tuft)

# Slightly adjust camera for better framing
cam = bpy.data.objects.get("Cam")
if cam:
    cam.location = (0, -26, 4)
    cam.rotation_euler = (math.radians(84), 0, 0)
    cam.data.lens = 40
