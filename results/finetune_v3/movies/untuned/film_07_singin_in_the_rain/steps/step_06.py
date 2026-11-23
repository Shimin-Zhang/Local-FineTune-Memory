import bpy, math, random
from mathutils import Vector

def cm(name, col, met=0, rgh=0.5, em=0, ecol=(0,0,0,1)):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes; l = m.node_tree.links; n.clear()
    b = n.new('ShaderNodeBsdfPrincipled'); o = n.new('ShaderNodeOutputMaterial')
    o.location=(300,0); b.location=(0,0)
    b.inputs['Base Color'].default_value = col
    b.inputs['Metallic'].default_value = met
    b.inputs['Roughness'].default_value = rgh
    if em > 0:
        b.inputs['Emission Color'].default_value = ecol
        b.inputs['Emission Strength'].default_value = em
    l.new(b.outputs['BSDF'], o.inputs['Surface'])
    return m

# The camera is still looking at a building wall. The issue is the camera position
# is too close to the buildings. Let's place it in the middle of the street, elevated.

cam = bpy.data.objects.get("MainCam")
if cam:
    # Place camera in the street, looking down the street at the character
    cam.location = (0, 2, 4)
    # Character is at (2.5, 3.5, 0) - but let's look slightly past him
    target = Vector((3, 4, 1))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 24  # Wide angle to capture the whole street scene
    cam.data.sensor_width = 36
    cam.data.clip_start = 0.1
    cam.data.clip_end = 500

# The scene is still too dark and brownish. The problem is likely:
# 1. Too many warm lights overpowering
# 2. Not enough overall illumination
# Let's reduce warm lights and add more balanced lighting

for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        if obj.name.startswith("LampLight"):
            obj.data.energy = 1500
        elif obj.name.startswith("LampL"):
            obj.data.energy = 500
        elif obj.name.startswith("StoreL"):
            obj.data.energy = 300
        elif obj.name.startswith("StoreInt"):
            obj.data.energy = 150
        elif obj.name.startswith("NeonL"):
            obj.data.energy = 200
        elif obj.name == "FillSun":
            obj.data.energy = 3.0
        elif obj.name == "RimLight":
            obj.data.energy = 500
        elif obj.name.startswith("Bounce"):
            obj.data.energy = 150
        elif obj.name == "SkyFill":
            obj.data.energy = 800
        elif obj.name == "BlueRim":
            obj.data.energy = 400

# Add a large white/neutral area light from above to provide base illumination
if not bpy.data.objects.get("TopFill"):
    bpy.ops.object.light_add(type='AREA', location=(0, 10, 0))
    tf = bpy.context.active_object; tf.name="TopFill"
    tf.data.energy = 1000
    tf.data.color = (0.8, 0.85, 1.0)
    tf.data.size = 25
    tf.rotation_euler = (0, 0, 0)

# Make the road material lighter so it's not pure black
mA = bpy.data.materials.get("WetAsphalt")
if mA and mA.use_nodes:
    bsdf = mA.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1)
        bsdf.inputs['Metallic'].default_value = 0.4
        bsdf.inputs['Roughness'].default_value = 0.1

# Make buildings slightly lighter so they're visible
for bname in ["Brick1", "Brick2", "Brick3"]:
    mb = bpy.data.materials.get(bname)
    if mb and mb.use_nodes:
        bsdf = mb.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Roughness'].default_value = 0.7

# Boost window emission more
mWL = bpy.data.materials.get("WinLit")
if mWL and mWL.use_nodes:
    bsdf = mWL.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Emission Strength'].default_value = 4.0

# Boost storefront glass
mSG = bpy.data.materials.get("StoreGlass")
if mSG and mSG.use_nodes:
    bsdf = mSG.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Emission Strength'].default_value = 3.0

# Boost lamp glass
mLG = bpy.data.materials.get("LampGlass")
if mLG and mLG.use_nodes:
    bsdf = mLG.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Emission Strength'].default_value = 6.0

# Set render settings for better exposure
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.view_settings.exposure = 1.5
bpy.context.scene.cycles.max_bounces = 8
bpy.context.scene.cycles.glossy_bounces = 4
bpy.context.scene.cycles.caustics_reflective = False
bpy.context.scene.cycles.caustics_refractive = False

# Add a subtle vignette by adding a large dark plane far away
# Actually, let's just make sure the world background is a dark blue
w = bpy.context.scene.world
if w and w.use_nodes:
    bg = w.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.01, 0.015, 0.03, 1)
        bg.inputs[1].default_value = 1.0

# Add a few more details: fire escape stairs on buildings
mMetal = cm("FireEscape",(0.03,0.03,0.03,1),0.8,0.3)
for bx, bz, bw, bh, bd in [(-13,-15,6,15,8),(-13,5,6,18,8),(13,-15,6,16,8),(13,5,6,20,8)]:
    fe_name = f"FireEsc_{bx}_{bz}"
    if not bpy.data.objects.get(fe_name):
        # Simple vertical ladder
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=bh*0.8, location=(bx + bw/2 + 0.1, bh*0.4, bz - bd/2 - 0.1), vertices=6)
        fe = bpy.context.active_object; fe.name = fe_name
        fe.data.materials.append(mMetal)
        # Horizontal rungs
        for i in range(6):
            ry = bh * 0.15 + i * (bh * 0.8 / 6)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.5, location=(bx + bw/2 + 0.1, ry, bz - bd/2 - 0.1), vertices=6)
            rung = bpy.context.active_object; rung.name=f"Rung_{bx}_{bz}_{i}"
            rung.rotation_euler = (0, 0, math.radians(90))
            rung.data.materials.append(mMetal)

# Add a simple "OPEN" neon sign with box geometry
mNeonOpen = cm("NeonOpen",(1,0.8,0.2,1),0,0.1,5.0,(1,0.7,0.2,1))
if not bpy.data.objects.get("NeonSignBox"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-11, 3.5, -10))
    nsb = bpy.context.active_object; nsb.name="NeonSignBox"
    nsb.scale = (0.05, 0.5, 1.2)
    nsb.data.materials.append(mNeonOpen)

# Add a "BAR" neon sign
mNeonBar = cm("NeonBar",(0.2,1,0.3,1),0,0.1,5.0,(0.1,1,0.2,1))
if not bpy.data.objects.get("NeonBarSign"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(11, 3.5, 5))
    nbs = bpy.context.active_object; nbs.name="NeonBarSign"
    nbs.scale = (0.05, 0.4, 1.0)
    nbs.data.materials.append(mNeonBar)

print("Fixed: camera in street looking at character, lighting balanced, top fill added, materials tuned, fire escapes and neon signs added, exposure improved")
