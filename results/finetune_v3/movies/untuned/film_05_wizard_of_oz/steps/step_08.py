import bpy, math, random

# Remove the flagpole that appears as a tall vertical line
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.dimensions.z > 15 and obj.dimensions.x < 1 and obj.dimensions.y < 1:
        bpy.data.objects.remove(obj, do_unlink=True)

# Remove fence rails still crossing road
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.dimensions.x > 3 and obj.dimensions.y < 1 and obj.dimensions.z < 1:
        if abs(obj.location.z) < 2 and abs(obj.location.x) < 5:
            bpy.data.objects.remove(obj, do_unlink=True)

# Remove rainbow toruses (they look odd)
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.dimensions.x > 15 and obj.dimensions.y > 15 and obj.dimensions.z < 5:
        if obj.location.y > 50:
            bpy.data.objects.remove(obj, do_unlink=True)

# Add a proper sun glow
m_sun_glow = bpy.data.materials.new("SunGlow"); m_sun_glow.use_nodes=True
m_sun_glow.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(1,.95,.7,1)
m_sun_glow.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=2

bpy.ops.mesh.primitive_uv_sphere_add(radius=3, location=(30,60,40))
sg = bpy.context.active_object; sg.data.materials.append(m_sun_glow)

# Add a few more poppies in foreground for depth
m_poppy = bpy.data.materials.get("Poppy")
m_stem = bpy.data.materials.get("Stem")
if m_poppy and m_stem:
    random.seed(200)
    for i in range(40):
        s = random.choice([-1,1])
        x = s*random.uniform(3,10); y = random.uniform(-25,-5)
        h = random.uniform(.5,1)
        bpy.ops.mesh.primitive_cylinder_add(radius=.03, depth=h, location=(x,y,h/2))
        bpy.context.active_object.data.materials.append(m_stem)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.1, location=(x,y,h+.07))
        hd = bpy.context.active_object; hd.scale=(1,1,.6); hd.data.materials.append(m_poppy)

# Add a small dog (Toto) near Dorothy
m_toto = bpy.data.materials.new("Toto"); m_toto.use_nodes=True
m_toto.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.3,.2,.1,1)
m_toto.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7

bpy.ops.mesh.primitive_uv_sphere_add(radius=.12, location=(-1.5,-14,.12))
tb = bpy.context.active_object; tb.scale=(1,1.3,.8); tb.data.materials.append(m_toto)
bpy.ops.mesh.primitive_uv_sphere_add(radius=.08, location=(-1.5,-13.8,.2))
th = bpy.context.active_object; th.data.materials.append(m_toto)
for lx in [-.06,.06]:
    bpy.ops.mesh.primitive_cylinder_add(radius=.03, depth=.15, location=(-1.5+lx,-14,.07))
    bpy.context.active_object.data.materials.append(m_toto)
bpy.ops.mesh.primitive_cylinder_add(radius=.02, depth=.15, location=(-1.5,-14.2,.15))
tt = bpy.context.active_object; tt.rotation_euler=(math.radians(-30),0,0); tt.data.materials.append(m_toto)

# Add a small shadow plane under each character for grounding
m_shadow = bpy.data.materials.new("Shadow"); m_shadow.use_nodes=True
m_shadow.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0,0,0,1)
m_shadow.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=1
m_shadow.blend_method = 'BLEND'
m_shadow.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = .3

for cx, cy in [(-1.2,-15),(.5,-12),(1.8,-10),(-.5,-7)]:
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx,cy,.01))
    sh = bpy.context.active_object; sh.scale=(.5,.5,1); sh.data.materials.append(m_shadow)

# Final camera tweak
cam = bpy.data.objects.get("Cam")
if cam:
    cam.location = (0, -30, 5)
    cam.rotation_euler = (math.radians(85), 0, 0)
    cam.data.lens = 35
