import bpy, math
from mathutils import Vector

# Delete the floating bridge/stacks and reposition everything properly
# Remove old bridge and smokestacks
for name in ["Bridge", "Smokestack_0", "SmokestackTop_0", "Smokestack_1", "SmokestackTop_1"]:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

# Reposition hull so the deck is at a sensible height and the bow points toward camera
hull = bpy.data.objects.get("Hull")
if hull:
    hull.location = (0, 10, 0)

deck = bpy.data.objects.get("Deck")
if deck:
    deck.location = (0, 10, 8)

# Move the two figures to the very tip of the bow (front edge of deck)
# Deck front is at y = 10 + 22 = 32, but hull tapers; place them at y ~ 28
for prefix, xoff in [("Jack", 0), ("Rose", 1.5)]:
    pass

# Find Jack and Rose parts and shift them to bow tip
jack_parts = [o for o in bpy.data.objects if o.name.startswith("Jack_")]
rose_parts = [o for o in bpy.data.objects if o.name.startswith("Rose_")]

# Current Jack base was (0,30,12), Rose (1.5,30,12). Move them forward to y=28 and down to deck level 8
for o in jack_parts:
    o.location.y = 28
    o.location.z = 8 + (o.location.z - 12)
for o in rose_parts:
    o.location.y = 28
    o.location.z = 8 + (o.location.z - 12)

# Add a proper bow tip - pointed prow
bpy.ops.mesh.primitive_cone_add(radius1=8, radius2=0, depth=12, location=(0, 34, 4), rotation=(0, math.radians(90), 0))
prow = bpy.context.active_object; prow.name = "Prow"
prow.data.materials.append(bpy.data.materials["Steel"])

# Add anchor on the bow
bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.15, location=(0, 30, 6))
anchor = bpy.context.active_object; anchor.name = "Anchor"
anchor.data.materials.append(bpy.data.materials["Metal"])

# Add the ship's name plate / figurehead area
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 31, 10))
figurehead = bpy.context.active_object; figurehead.name = "Figurehead"
figurehead.scale = (0.5, 1, 1.5)
figurehead.data.materials.append(bpy.data.materials["Wood"])

# Add more deck planking detail - thin strips
for i in range(8):
    y = 5 + i * 3.5
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, y, 8.05))
    strip = bpy.context.active_object; strip.name = f"DeckStrip_{i}"
    strip.scale = (8, 0.3, 0.05)
    strip.data.materials.append(bpy.data.materials["Wood"])

# Add lifeboat davits on the sides
for side in [-1, 1]:
    for i in range(3):
        y = 8 + i * 6
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=3, location=(side*8, y, 11))
        davit = bpy.context.active_object; davit.name = f"Davit_{side}_{i}"
        davit.rotation_euler = (math.radians(30), 0, 0)
        davit.data.materials.append(bpy.data.materials["Metal"])

# Add a forward mast
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=20, location=(0, 25, 18))
mast = bpy.context.active_object; mast.name = "ForwardMast"
mast.data.materials.append(bpy.data.materials["Metal"])

# Add rigging lines from mast
for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
    rad = math.radians(angle)
    ex = math.sin(rad) * 8
    ey = 25 + math.cos(rad) * 8
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=12, location=(ex/2, (25+ey)/2, 25))
    rig = bpy.context.active_object; rig.name = f"Rigging_{angle}"
    rig.rotation_euler = (math.radians(25), 0, rad)
    rig.data.materials.append(bpy.data.materials["Metal"])

# Add a small upper deck / bridge behind
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 12, 16))
bridge2 = bpy.context.active_object; bridge2.name = "UpperBridge"
bridge2.scale = (6, 4, 3)
bridge2.data.materials.append(bpy.data.materials["Steel"])

# Add windows to upper bridge
for i in range(4):
    x = -1.5 + i * 1
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(x, 14.5, 16))
    win = bpy.context.active_object; win.name = f"Win_{i}"
    win.scale = (1, 0.1, 1)
    gm = bpy.data.materials.get("Glass") or bpy.data.materials.new("Glass")
    gm.use_nodes = True
    gn, gl = gm.node_tree.nodes, gm.node_tree.links
    for n in gn: gn.remove(n)
    gp = gn.new('ShaderNodeBsdfPrincipled')
    gp.inputs['Base Color'].default_value = (0.7, 0.85, 1.0, 1)
    gp.inputs['Transmission Weight'].default_value = 0.9
    go = gn.new('ShaderNodeOutputMaterial')
    gl.new(gp.outputs['BSDF'], go.inputs['Surface'])
    win.data.materials.append(gm)

# Add smokestacks behind the bridge
for i in range(2):
    x = -2 + i * 4
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=10, location=(x, 8, 24))
    stack = bpy.context.active_object; stack.name = f"Stack_{i}"
    stack.data.materials.append(bpy.data.materials["Steel"])
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=2, location=(x, 8, 29))
    top = bpy.context.active_object; top.name = f"StackTop_{i}"
    top.data.materials.append(bpy.data.materials["Steel"])

# Add a sun glow sphere for the sunset sun
bpy.ops.mesh.primitive_uv_sphere_add(radius=8, location=(0, -200, 15))
sunball = bpy.context.active_object; sunball.name = "SunGlow"
sm = bpy.data.materials.new("SunMat"); sm.use_nodes = True
sn, sl = sm.node_tree.nodes, sm.node_tree.links
for n in sn: sn.remove(n)
sp = sn.new('ShaderNodeEmission')
sp.inputs['Color'].default_value = (1.0, 0.6, 0.2, 1)
sp.inputs['Strength'].default_value = 5.0
so = sn.new('ShaderNodeOutputMaterial')
sl.new(sp.outputs['Emission'], so.inputs['Surface'])
sunball.data.materials.append(sm)

# Improve camera to frame the bow with the two figures
cam = bpy.data.objects.get("MainCamera") or bpy.context.scene.camera
if cam:
    cam.location = (0, -18, 10)
    cam.rotation_euler = (math.radians(85), 0, 0)
    cam.data.lens = 40

# Add a slight motion - wind-blown hair effect for Rose (already have strands)
# Add a few more hair strands
rose_base = Vector((1.5, 28, 8))
rh = bpy.data.materials.get("RoseHair")
if rh:
    for i in range(3):
        angle = math.radians(i * 40 - 40)
        loc = (rose_base.x + math.sin(angle)*0.35, rose_base.y - 0.4, rose_base.z + 1.8)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.8, location=loc)
        s = bpy.context.active_object; s.name = f"RoseWind_{i}"
        s.rotation_euler = (math.radians(20), 0, angle)
        s.data.materials.append(rh)

# Add Jack's hair
jh = bpy.data.materials.get("JackHair")
if jh:
    jb = Vector((0, 28, 8))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(jb.x, jb.y-0.15, jb.z+2.35))
    h = bpy.context.active_object; h.name = "JackHairMesh"
    h.scale = (1, 0.9, 0.7)
    h.data.materials.append(jh)

# Add Rose's hair mesh
if rh:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(rose_base.x, rose_base.y-0.2, rose_base.z+2.1))
    h = bpy.context.active_object; h.name = "RoseHairMesh"
    h.scale = (1, 1.1, 1.2)
    h.data.materials.append(rh)

# Add a subtle fog / atmospheric haze via world volume
world = bpy.context.scene.world
if world and world.use_nodes:
    wn = world.node_tree.nodes
    wo = world.node_tree.links
    # Add volume scatter
    vol = wn.new('ShaderNodeVolumeScatter')
    vol.inputs['Color'].default_value = (1.0, 0.7, 0.4, 1)
    vol.inputs['Density'].default_value = 0.005
    vol.inputs['Anisotropy'].default_value = 0.5
    # Connect to world output volume
    for node in wn:
        if node.type == 'OUTPUT_WORLD':
            wo.new(vol.outputs['Volume'], node.inputs['Volume'])

# Add a few seagulls in the distance
for i in range(5):
    x = -30 + i * 15
    y = -80 + i * 10
    z = 30 + i * 5
    bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0, depth=1.5, location=(x, y, z))
    bird = bpy.context.active_object; bird.name = f"Seagull_{i}"
    bird.rotation_euler = (0, math.radians(90), math.radians(i*30))
    bm = bpy.data.materials.new("Bird"); bm.use_nodes = True
    bn, bl = bm.node_tree.nodes, bm.node_tree.links
    for n in bn: bn.remove(n)
    bp = bn.new('ShaderNodeBsdfPrincipled'); bp.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1)
    bo = bn.new('ShaderNodeOutputMaterial')
    bl.new(bp.outputs['BSDF'], bo.inputs['Surface'])
    bird.data.materials.append(bm)

print("Refined scene with bow, figures, details")
