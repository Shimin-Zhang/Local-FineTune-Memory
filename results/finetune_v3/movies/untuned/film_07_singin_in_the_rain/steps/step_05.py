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

# The camera is way too close and looking at the ground. 
# The scene is too dark and the camera is inside/near a building.
# Let's completely reset the camera to a good vantage point.

cam = bpy.data.objects.get("MainCam")
if cam:
    # Position camera on the opposite side of the street, elevated, looking at the character
    cam.location = (-8, 5, 6)
    # Look at the character who is at approximately (2.5, 3.5, 0)
    target = Vector((2.5, 3.5, 1))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 35
    cam.data.sensor_width = 36
    cam.data.clip_start = 0.1
    cam.data.clip_end = 200

# The scene is very dark. Let's boost all lights significantly.
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        if obj.name.startswith("LampLight"):
            obj.data.energy = 2000
        elif obj.name.startswith("LampL"):
            obj.data.energy = 800
        elif obj.name.startswith("StoreL"):
            obj.data.energy = 500
        elif obj.name.startswith("NeonL"):
            obj.data.energy = 300
        elif obj.name == "FillSun":
            obj.data.energy = 2.0
        elif obj.name == "RimLight":
            obj.data.energy = 800
        elif obj.name.startswith("Bounce"):
            obj.data.energy = 200

# The brown tint is likely from the warm lights. Let's add a cool fill to balance.
# Also make sure the world background isn't too dark
w = bpy.context.scene.world
if w and w.use_nodes:
    bg = w.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.01, 0.01, 0.03, 1)
        bg.inputs[1].default_value = 1.0

# Add a large area light from above to simulate moonlight/sky glow
if not bpy.data.objects.get("SkyFill"):
    bpy.ops.object.light_add(type='AREA', location=(0, 15, 0))
    sky = bpy.context.active_object; sky.name="SkyFill"
    sky.data.energy = 500
    sky.data.color = (0.3, 0.4, 0.6)
    sky.data.size = 30
    sky.rotation_euler = (0, 0, 0)

# Make the wet asphalt more reflective by adjusting its material
mA = bpy.data.materials.get("WetAsphalt")
if mA and mA.use_nodes:
    bsdf = mA.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Metallic'].default_value = 0.5
        bsdf.inputs['Roughness'].default_value = 0.05
        bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1)

# Make the wet reflection plane more visible
mWet = bpy.data.materials.get("WetReflect")
if mWet and mWet.use_nodes:
    bsdf = mWet.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Metallic'].default_value = 0.8
        bsdf.inputs['Roughness'].default_value = 0.02
        bsdf.inputs['Base Color'].default_value = (0.03, 0.03, 0.04, 1)

# Add more window lights to make buildings glow
mWL = bpy.data.materials.get("WinLit")
if mWL and mWL.use_nodes:
    bsdf = mWL.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Emission Strength'].default_value = 3.0

# Boost storefront glass emission
mSG = bpy.data.materials.get("StoreGlass")
if mSG and mSG.use_nodes:
    bsdf = mSG.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Emission Strength'].default_value = 2.5

# Boost lamp glass
mLG = bpy.data.materials.get("LampGlass")
if mLG and mLG.use_nodes:
    bsdf = mLG.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Emission Strength'].default_value = 5.0

# Add a few more point lights inside storefronts to create glow
for zz in [-15, -5, 5, 15]:
    for xx in [-11, 11]:
        lname = f"StoreInt_{xx}_{zz}"
        if not bpy.data.objects.get(lname):
            bpy.ops.object.light_add(type='POINT', location=(xx, 1.5, zz))
            il = bpy.context.active_object; il.name = lname
            il.data.energy = 200
            il.data.color = (1.0, 0.85, 0.5)
            il.data.shadow_soft_size = 0.5

# Add a subtle blue rim light from the side for cinematic look
if not bpy.data.objects.get("BlueRim"):
    bpy.ops.object.light_add(type='SPOT', location=(-10, 4, -5))
    br = bpy.context.active_object; br.name="BlueRim"
    br.data.energy = 300
    br.data.color = (0.2, 0.4, 1.0)
    br.data.spot_size = math.radians(80)
    br.data.shadow_soft_size = 0.5
    target = Vector((2.5, 3.5, 1))
    direction = target - br.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    br.rotation_euler = rot_quat.to_euler()

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.view_settings.exposure = 1.0
bpy.context.scene.cycles.max_bounces = 8
bpy.context.scene.cycles.glossy_bounces = 4

# Add a few more puddles with high reflectivity
mPu = cm("Puddle",(0.02,0.02,0.03,1),0.9,0.01)
random.seed(42)
for i in range(10):
    px = random.uniform(-8, 8)
    pz = random.uniform(-20, 20)
    pr = random.uniform(0.3, 1.0)
    p = bpy.data.objects.get(f"Puddle2_{i}")
    if not p:
        bpy.ops.mesh.primitive_circle_add(radius=pr, fill_type='NGON', location=(px, 0.02, pz), vertices=16)
        p = bpy.context.active_object; p.name=f"Puddle2_{i}"
        p.data.materials.append(mPu)

# Add a simple "rain" effect using small emissive particles scattered in the air
# Use a particle-like approach with small emissive spheres
mRainDrop = cm("RainDrop",(0.5,0.5,0.6,1),0,0.1,0.5,(0.4,0.4,0.5,1))
random.seed(123)
for i in range(80):
    rx = random.uniform(-12, 12)
    ry = random.uniform(0.5, 8)
    rz = random.uniform(-20, 20)
    rd = bpy.data.objects.get(f"Drop_{i}")
    if not rd:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.01, location=(rx, ry, rz), segments=6, ring_count=4)
        rd = bpy.context.active_object; rd.name=f"Drop_{i}"
        rd.data.materials.append(mRainDrop)

print("Fixed: camera repositioned to good vantage point, lights massively boosted, sky fill added, materials tuned, more puddles and rain drops added, render settings improved")
