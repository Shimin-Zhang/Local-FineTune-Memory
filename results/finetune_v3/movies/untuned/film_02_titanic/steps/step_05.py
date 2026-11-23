import bpy, math
from mathutils import Vector

# The scene is too dark - the volume scatter is blocking light. Remove it and boost lighting.
world = bpy.context.scene.world
if world and world.use_nodes:
    wn, wo = world.node_tree.nodes, world.node_tree.links
    # Remove volume scatter
    for node in list(wn):
        if node.type == 'VOLUME_SCATTER':
            # Disconnect volume
            for node2 in wn:
                if node2.type == 'OUTPUT_WORLD':
                    for link in list(wo):
                        if link.to_node == node2 and link.to_socket.name == 'Volume':
                            wo.remove(link)
            wn.remove(node)

# Boost sun light
sun = bpy.data.objects.get("SunsetSun")
if sun:
    sun.data.energy = 8.0
    sun.data.color = (1.0, 0.65, 0.35)

# Boost fill
fill = bpy.data.objects.get("WarmFill")
if fill:
    fill.data.energy = 200

# Add a stronger key light from the sunset direction
bpy.ops.object.light_add(type='SUN', location=(0, -50, 5))
key = bpy.context.active_object; key.name = "SunKey"
key.data.energy = 6.0
key.data.color = (1.0, 0.7, 0.4)
key.rotation_euler = (math.radians(75), 0, math.radians(180))

# Add ambient fill from above
bpy.ops.object.light_add(type='AREA', location=(0, 0, 40))
amb = bpy.context.active_object; amb.name = "AmbientFill"
amb.data.energy = 150
amb.data.size = 50
amb.data.color = (0.9, 0.8, 0.7)

# Increase exposure
scene = bpy.context.scene
scene.view_settings.exposure = 1.5
scene.cycles.samples = 128

# Make the ocean more reflective and visible
ocean = bpy.data.objects.get("Ocean")
if ocean:
    om = ocean.data.materials[0]
    if om and om.use_nodes:
        for node in om.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node.inputs['Roughness'].default_value = 0.02
                node.inputs['Metallic'].default_value = 0.4
                node.inputs['Base Color'].default_value = (0.05, 0.15, 0.25, 1)

# Add a sun reflection path on the water - a bright strip
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -50, -7.5))
sun_path = bpy.context.active_object; sun_path.name = "SunPath"
sun_path.scale = (3, 150, 1)
sp_mat = bpy.data.materials.new("SunPathMat"); sp_mat.use_nodes = True
spn, spl = sp_mat.node_tree.nodes, sp_mat.node_tree.links
for n in spn: spn.remove(n)
spp = spn.new('ShaderNodeEmission')
spp.inputs['Color'].default_value = (1.0, 0.7, 0.3, 1)
spp.inputs['Strength'].default_value = 2.0
spo = spn.new('ShaderNodeOutputMaterial')
spl.new(spp.outputs['Emission'], spo.inputs['Surface'])
sun_path.data.materials.append(sp_mat)

# Add more hull detail - rivets along the bow
for i in range(15):
    y = 5 + i * 1.5
    for side in [-1, 1]:
        x = side * (7 - (y/30)*2)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(x, y, 6))
        rivet = bpy.context.active_object; rivet.name = f"Rivet_{i}_{side}"
        rivet.data.materials.append(bpy.data.materials["Metal"])

# Add portholes on the hull
for i in range(8):
    y = 8 + i * 3
    for side in [-1, 1]:
        x = side * (6.5 - (y/30)*1.5)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(x, y, 5))
        port = bpy.context.active_object; port.name = f"Porthole_{i}_{side}"
        port.rotation_euler = (0, math.radians(90), 0)
        port.data.materials.append(bpy.data.materials["Metal"])

# Add the ship's funnel/stacks with proper black tops
for i in range(2):
    x = -2.5 + i * 5
    # Main stack
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=12, location=(x, 10, 26))
    stack = bpy.context.active_object; stack.name = f"Funnel_{i}"
    stack.data.materials.append(bpy.data.materials["Steel"])
    # Black top
    bpy.ops.mesh.primitive_cylinder_add(radius=1.9, depth=2, location=(x, 10, 32))
    top = bpy.context.active_object; top.name = f"FunnelTop_{i}"
    tm = bpy.data.materials.new("FunnelTop"); tm.use_nodes = True
    tn, tl = tm.node_tree.nodes, tm.node_tree.links
    for n in tn: tn.remove(n)
    tp = tn.new('ShaderNodeBsdfPrincipled')
    tp.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
    to = tn.new('ShaderNodeOutputMaterial')
    tl.new(tp.outputs['BSDF'], to.inputs['Surface'])
    top.data.materials.append(tm)

# Add a flag on the mast
mast = bpy.data.objects.get("ForwardMast")
if mast:
    flag_loc = mast.location
    bpy.ops.mesh.primitive_plane_add(size=2, location=(flag_loc.x, flag_loc.y - 1, flag_loc.z + 9))
    flag = bpy.context.active_object; flag.name = "ShipFlag"
    flag.scale = (1, 1.5, 1)
    flag.rotation_euler = (0, math.radians(10), 0)
    fm = bpy.data.materials.new("FlagMat"); fm.use_nodes = True
    fn, fl = fm.node_tree.nodes, fm.node_tree.links
    for n in fn: fn.remove(n)
    fp = fn.new('ShaderNodeBsdfPrincipled')
    fp.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1)
    fo = fn.new('ShaderNodeOutputMaterial')
    fl.new(fp.outputs['BSDF'], fo.inputs['Surface'])
    flag.data.materials.append(fm)

# Add a rope/line from mast to bow
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=15, location=(0, 28, 22))
rope = bpy.context.active_object; rope.name = "BowRope"
rope.rotation_euler = (math.radians(30), 0, 0)
rope.data.materials.append(bpy.data.materials["Metal"])

# Add deck chairs / details near the figures
for i in range(3):
    x = -3 + i * 3
    bpy.ops.mesh.primitive_cube_add(size=0.8, location=(x, 25, 8.5))
    chair = bpy.context.active_object; chair.name = f"DeckChair_{i}"
    chair.scale = (1, 1.5, 0.5)
    chair.data.materials.append(bpy.data.materials["Wood"])

# Add a binoculars hanging from a neck (Jack)
jb = Vector((0, 28, 8))
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=(jb.x, jb.y + 0.3, jb.z + 1.8))
bins = bpy.context.active_object; bins.name = "Binoculars"
bins.rotation_euler = (math.radians(30), 0, 0)
bins.data.materials.append(bpy.data.materials["Metal"])

# Add a hat on Jack
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.1, location=(jb.x, jb.y, jb.z + 2.5))
hat = bpy.context.active_object; hat.name = "JackHat"
hat.data.materials.append(bpy.data.materials["JackSuit"])

# Add a necklace on Rose
rb = Vector((1.5, 28, 8))
bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.02, location=(rb.x, rb.y + 0.3, rb.z + 1.8))
neck = bpy.context.active_object; neck.name = "RoseNecklace"
neck.rotation_euler = (math.radians(90), 0, 0)
nm = bpy.data.materials.new("Gold"); nm.use_nodes = True
nn, nl = nm.node_tree.nodes, nm.node_tree.links
for n in nn: nn.remove(n)
np = nn.new('ShaderNodeBsdfPrincipled')
np.inputs['Base Color'].default_value = (1.0, 0.8, 0.2, 1)
np.inputs['Metallic'].default_value = 1.0
np.inputs['Roughness'].default_value = 0.2
no = nn.new('ShaderNodeOutputMaterial')
nl.new(np.outputs['BSDF'], no.inputs['Surface'])
neck.data.materials.append(nm)

# Add the famous diamond
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.08, location=(rb.x, rb.y + 0.35, rb.z + 1.7))
diamond = bpy.context.active_object; diamond.name = "Diamond"
dm = bpy.data.materials.new("DiamondMat"); dm.use_nodes = True
dn, dl = dm.node_tree.nodes, dm.node_tree.links
for n in dn: dn.remove(n)
dp = dn.new('ShaderNodeBsdfPrincipled')
dp.inputs['Base Color'].default_value = (0.9, 0.95, 1.0, 1)
dp.inputs['Transmission Weight'].default_value = 1.0
dp.inputs['Roughness'].default_value = 0.0
dp.inputs['IOR'].default_value = 2.4
do = dn.new('ShaderNodeOutputMaterial')
dl.new(dp.outputs['BSDF'], do.inputs['Surface'])
diamond.data.materials.append(dm)

# Add a slight camera tilt for cinematic feel
cam = bpy.context.scene.camera
if cam:
    cam.rotation_euler = (math.radians(84), 0, math.radians(2))

# Add more seagulls
for i in range(3):
    x = -20 + i * 20
    y = -60 + i * 15
    z = 25 + i * 8
    bpy.ops.mesh.primitive_cone_add(radius1=0.4, radius2=0, depth=1.2, location=(x, y, z))
    bird = bpy.context.active_object; bird.name = f"Gull_{i}"
    bird.rotation_euler = (0, math.radians(90), math.radians(i*45))
    bird.data.materials.append(bpy.data.materials.get("Bird") or bpy.data.materials.new("Bird"))

# Add a wake / water spray at the bow
bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 38, -7))
wake = bpy.context.active_object; wake.name = "Wake"
wake.scale = (1, 2, 1)
wm = bpy.data.materials.new("WakeMat"); wm.use_nodes = True
wn2, wl = wm.node_tree.nodes, wm.node_tree.links
for n in wn2: wn2.remove(n)
wp = wn2.new('ShaderNodeBsdfPrincipled')
wp.inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1)
wp.inputs['Transmission Weight'].default_value = 0.8
wp.inputs['Roughness'].default_value = 0.3
wo2 = wn2.new('ShaderNodeOutputMaterial')
wl.new(wp.outputs['BSDF'], wo2.inputs['Surface'])
wake.data.materials.append(wm)

print("Brightened and detailed the scene")
