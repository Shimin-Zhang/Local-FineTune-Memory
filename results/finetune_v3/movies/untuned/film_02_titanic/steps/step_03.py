import bpy, math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# World - sunset sky
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
nodes, links = world.node_tree.nodes, world.node_tree.links
for n in nodes: nodes.remove(n)

tex = nodes.new('ShaderNodeTexCoord')
mapn = nodes.new('ShaderNodeMapping')
mapn.inputs['Rotation'].default_value = (0, math.radians(90), 0)
grad = nodes.new('ShaderNodeTexGradient')
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.9, 0.4, 0.15, 1)
ramp.color_ramp.elements[1].position = 0.6
ramp.color_ramp.elements[1].color = (0.15, 0.1, 0.3, 1)
e = ramp.color_ramp.elements.new(0.25); e.color = (1.0, 0.55, 0.2, 1)
bg = nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 1.0
out = nodes.new('ShaderNodeOutputWorld')
links.new(tex.outputs['Generated'], mapn.inputs['Vector'])
links.new(mapn.outputs['Vector'], grad.inputs['Vector'])
links.new(grad.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], out.inputs['Surface'])

# Camera
bpy.ops.object.camera_add(location=(0, -22, 14), rotation=(math.radians(83), 0, 0))
cam = bpy.context.active_object; cam.data.lens = 32
bpy.context.scene.camera = cam

# Lights
bpy.ops.object.light_add(type='SUN', location=(0, -50, 3))
sun = bpy.context.active_object; sun.data.energy = 4.0; sun.data.color = (1, 0.6, 0.3)
sun.rotation_euler = (math.radians(80), 0, math.radians(180))
bpy.ops.object.light_add(type='AREA', location=(0, -15, 10))
fill = bpy.context.active_object; fill.data.energy = 80; fill.data.size = 25; fill.data.color = (1, 0.7, 0.4)

# Ocean
bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 0, -8))
ocean = bpy.context.active_object; ocean.name = "Ocean"
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=100); bpy.ops.object.mode_set(mode='OBJECT')
om = bpy.data.materials.new("Water"); om.use_nodes = True
on, ol = om.node_tree.nodes, om.node_tree.links
for n in on: on.remove(n)
noise = on.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 3.0; noise.inputs['Detail'].default_value = 8.0
bump = on.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.4
p = on.new('ShaderNodeBsdfPrincipled')
p.inputs['Base Color'].default_value = (0.02, 0.08, 0.15, 1)
p.inputs['Roughness'].default_value = 0.05; p.inputs['Transmission Weight'].default_value = 0.5
o = on.new('ShaderNodeOutputMaterial')
ol.new(noise.outputs['Fac'], bump.inputs['Height'])
ol.new(bump.outputs['Normal'], p.inputs['Normal'])
ol.new(p.outputs['BSDF'], o.inputs['Surface'])
ocean.data.materials.append(om)

# Hull
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 10, 5))
hull = bpy.context.active_object; hull.name = "Hull"; hull.scale = (10, 25, 8)
bpy.ops.object.mode_set(mode='EDIT')
import bmesh
bm = bmesh.from_edit_mesh(bpy.context.object.data)
for v in bm.verts:
    if v.co.y > 0:
        f = v.co.y / 12.5
        v.co.x *= (1 - f * 0.7); v.co.z *= (1 - f * 0.3); v.co.z += f * 3
bmesh.update_edit_mesh(bpy.context.object.data)
bpy.ops.object.mode_set(mode='OBJECT')
hm = bpy.data.materials.new("Steel"); hm.use_nodes = True
hn, hl = hm.node_tree.nodes, hm.node_tree.links
for n in hn: hn.remove(n)
hp = hn.new('ShaderNodeBsdfPrincipled')
hp.inputs['Base Color'].default_value = (0.15, 0.12, 0.1, 1)
hp.inputs['Metallic'].default_value = 0.7; hp.inputs['Roughness'].default_value = 0.5
ho = hn.new('ShaderNodeOutputMaterial')
hl.new(hp.outputs['BSDF'], ho.inputs['Surface'])
hull.data.materials.append(hm)

# Deck
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 10, 12))
deck = bpy.context.active_object; deck.name = "Deck"; deck.scale = (9, 22, 1)
bpy.ops.object.mode_set(mode='EDIT')
bmd = bmesh.from_edit_mesh(bpy.context.object.data)
for v in bmd.verts:
    if v.co.y > 0: v.co.x *= (1 - (v.co.y / 11) * 0.7)
bmesh.update_edit_mesh(bpy.context.object.data)
bpy.ops.object.mode_set(mode='OBJECT')
dm = bpy.data.materials.new("Wood"); dm.use_nodes = True
dn, dl = dm.node_tree.nodes, dm.node_tree.links
for n in dn: dn.remove(n)
wave = dn.new('ShaderNodeTexWave'); wave.inputs['Scale'].default_value = 2.0
rampd = dn.new('ShaderNodeValToRGB')
rampd.color_ramp.elements[0].color = (0.25, 0.12, 0.05, 1)
rampd.color_ramp.elements[1].color = (0.35, 0.18, 0.08, 1)
dp = dn.new('ShaderNodeBsdfPrincipled'); dp.inputs['Roughness'].default_value = 0.8
do = dn.new('ShaderNodeOutputMaterial')
dl.new(wave.outputs['Fac'], rampd.inputs['Fac'])
dl.new(rampd.outputs['Color'], dp.inputs['Base Color'])
dl.new(dp.outputs['BSDF'], do.inputs['Surface'])
deck.data.materials.append(dm)

# Railings
mm = bpy.data.materials.new("Metal"); mm.use_nodes = True
mn, ml = mm.node_tree.nodes, mm.node_tree.links
for n in mn: mn.remove(n)
mp = mn.new('ShaderNodeBsdfPrincipled')
mp.inputs['Base Color'].default_value = (0.3, 0.3, 0.35, 1)
mp.inputs['Metallic'].default_value = 0.9; mp.inputs['Roughness'].default_value = 0.2
mo = mn.new('ShaderNodeOutputMaterial')
ml.new(mp.outputs['BSDF'], mo.inputs['Surface'])

for side in [-1, 1]:
    for h, r in [(14.5, 0.15), (13.5, 0.1), (12.5, 0.08)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=20, location=(side*7, 10, h))
        bpy.context.active_object.data.materials.append(mm)
    for i in range(10):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.5, location=(side*7, i*2.2, 13.5))
        bpy.context.active_object.data.materials.append(mm)

# Jack
jb = Vector((0, 30, 12))
jm = bpy.data.materials.new("JackSuit"); jm.use_nodes = True
jn, jl = jm.node_tree.nodes, jm.node_tree.links
for n in jn: jn.remove(n)
jp = jn.new('ShaderNodeBsdfPrincipled'); jp.inputs['Base Color'].default_value = (0.08, 0.08, 0.12, 1)
jo = jn.new('ShaderNodeOutputMaterial'); jl.new(jp.outputs['BSDF'], jo.inputs['Surface'])
js = bpy.data.materials.new("JackSkin"); js.use_nodes = True
jsn, jsl = js.node_tree.nodes, js.node_tree.links
for n in jsn: jsn.remove(n)
jsp = jsn.new('ShaderNodeBsdfPrincipled'); jsp.inputs['Base Color'].default_value = (0.8, 0.6, 0.5, 1)
jso = jsn.new('ShaderNodeOutputMaterial'); jsl.new(jsp.outputs['BSDF'], jso.inputs['Surface'])

bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.6, location=(jb.x, jb.y, jb.z+1))
bpy.context.active_object.data.materials.append(jm)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(jb.x, jb.y, jb.z+2.2))
bpy.context.active_object.data.materials.append(js)
for side, rot in [(-1, 50), (1, -50)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1.3, location=(jb.x+side*1, jb.y, jb.z+1.6))
    o = bpy.context.active_object; o.rotation_euler = (0, math.radians(rot), 0); o.data.materials.append(jm)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(jb.x+side*1.8, jb.y, jb.z+2))
    bpy.context.active_object.data.materials.append(js)
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.3, location=(jb.x+side*0.2, jb.y, jb.z+0.4))
    bpy.context.active_object.data.materials.append(jm)

# Rose
rb = Vector((1.5, 30, 12))
rm = bpy.data.materials.new("RoseDress"); rm.use_nodes = True
rn, rl = rm.node_tree.nodes, rm.node_tree.links
for n in rn: rn.remove(n)
rp = rn.new('ShaderNodeBsdfPrincipled'); rp.inputs['Base Color'].default_value = (0.95, 0.9, 0.85, 1)
ro = rn.new('ShaderNodeOutputMaterial'); rl.new(rp.outputs['BSDF'], ro.inputs['Surface'])
rs = bpy.data.materials.new("RoseSkin"); rs.use_nodes = True
rsn, rsl = rs.node_tree.nodes, rs.node_tree.links
for n in rsn: rsn.remove(n)
rsp = rsn.new('ShaderNodeBsdfPrincipled'); rsp.inputs['Base Color'].default_value = (0.9, 0.7, 0.6, 1)
rso = rsn.new('ShaderNodeOutputMaterial'); rsl.new(rsp.outputs['BSDF'], rso.inputs['Surface'])

bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=1.5, location=(rb.x, rb.y, rb.z+0.95))
bpy.context.active_object.data.materials.append(rm)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(rb.x, rb.y, rb.z+2))
bpy.context.active_object.data.materials.append(rs)
for side, rot in [(-1, 50), (1, -50)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.2, location=(rb.x+side*0.85, rb.y, rb.z+1.5))
    o = bpy.context.active_object; o.rotation_euler = (0, math.radians(rot), 0); o.data.materials.append(rm)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(rb.x+side*1.55, rb.y, rb.z+1.85))
    bpy.context.active_object.data.materials.append(rs)
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1.2, location=(rb.x+side*0.15, rb.y, rb.z+0.35))
    bpy.context.active_object.data.materials.append(rm)

# Bridge + stacks
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, 22))
bpy.context.active_object.scale = (8, 6, 4); bpy.context.active_object.data.materials.append(hm)
for i in range(2):
    x = -2.5 + i*5
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=14, location=(x, 15, 32))
    bpy.context.active_object.data.materials.append(hm)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.9, depth=2.5, location=(x, 15, 39))
    bpy.context.active_object.data.materials.append(hm)

# Render settings
scene = bpy.context.scene
scene.render.resolution_x = 1920; scene.render.resolution_y = 1080
scene.cycles.samples = 64; scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.3
print("Scene built")
