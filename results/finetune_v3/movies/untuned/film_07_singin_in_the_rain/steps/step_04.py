import bpy, math, random
from mathutils import Vector

# Define cm again since variables don't persist
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

# Fix camera - it's looking at the wrong place. Let's reposition it properly.
cam = bpy.data.objects.get("MainCam")
if cam:
    cam.location = (-6, 2, 3)
    target = Vector((2.5, 3.5, 1))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 28
    cam.data.sensor_width = 36

# The scene is very dark and brownish. The fog volume is likely causing the brown tint.
# Remove the fog volume or reduce its density
fog = bpy.data.objects.get("FogVolume")
if fog:
    bpy.data.objects.remove(fog, do_unlink=True)

# Remove the rain cylinders - too many and they're blocking light
for obj in list(bpy.data.objects):
    if obj.name.startswith("Rain_"):
        bpy.data.objects.remove(obj, do_unlink=True)

# Boost all lights significantly
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        if obj.name.startswith("LampLight"):
            obj.data.energy = 1000
        elif obj.name.startswith("LampL"):
            obj.data.energy = 500
        elif obj.name.startswith("StoreL"):
            obj.data.energy = 300
        elif obj.name.startswith("NeonL"):
            obj.data.energy = 150
        elif obj.name == "FillSun":
            obj.data.energy = 1.0
        elif obj.name == "RimLight":
            obj.data.energy = 500

# Add building cornices that failed before
mSD = cm("StoneDark",(0.15,0.14,0.12,1),0,0.9)
for bx, bz, bw, bh, bd in [(-13,-15,6,15,8),(-13,-5,6,12,8),(-13,5,6,18,8),(-13,15,6,14,8),
                             (13,-15,6,16,8),(13,-5,6,13,8),(13,5,6,20,8),(13,15,6,15,8)]:
    # Check if cornice already exists
    cname = f"Cor_{bx}_{bz}"
    if not bpy.data.objects.get(cname):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, bh, bz))
        cor = bpy.context.active_object; cor.name = cname
        cor.scale = (bw*1.1, 0.3, bd*1.1)
        cor.data.materials.append(mSD)
    bname = f"Bas_{bx}_{bz}"
    if not bpy.data.objects.get(bname):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, 0.2, bz))
        bas = bpy.context.active_object; bas.name = bname
        bas.scale = (bw*1.05, 0.4, bd*1.05)
        bas.data.materials.append(mSD)

# Add crosswalk markings
mWhite = cm("StreetMark",(0.6,0.6,0.6,1),0,0.5)
for i in range(6):
    mz = -15 + i * 5
    mname = f"CrossMark_{i}"
    if not bpy.data.objects.get(mname):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.01, mz))
        mk = bpy.context.active_object; mk.name = mname
        mk.scale = (8, 0.02, 0.3)
        mk.data.materials.append(mWhite)

# Add a parked car
mCar = cm("CarBody",(0.05,0.05,0.08,1),0.3,0.3)
mWheel = cm("Wheel",(0.02,0.02,0.02,1),0.5,0.4)
if not bpy.data.objects.get("Car_Body"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-7, 0.5, -12))
    car = bpy.context.active_object; car.name="Car_Body"
    car.scale = (1.8, 1.2, 4)
    car.data.materials.append(mCar)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-7, 1.2, -12.5))
    roof = bpy.context.active_object; roof.name="Car_Roof"
    roof.scale = (1.5, 0.8, 2.5)
    roof.data.materials.append(mCar)
    for wz in [-13.5, -10.5]:
        for wx in [-7.8, -6.2]:
            wname = f"Wheel_{wx}_{wz}"
            if not bpy.data.objects.get(wname):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(wx, 0.3, wz), vertices=12)
                wh = bpy.context.active_object; wh.name = wname
                wh.rotation_euler = (0, math.radians(90), 0)
                wh.data.materials.append(mWheel)

# Add onlooker silhouette
mSil = cm("Silhouette",(0.01,0.01,0.01,1),0,0.8)
if not bpy.data.objects.get("Onlooker_Body"):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.6, location=(-8, 0.8, 5), vertices=8)
    onk = bpy.context.active_object; onk.name="Onlooker_Body"
    onk.data.materials.append(mSil)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-8, 1.7, 5), segments=12, ring_count=6)
    bpy.context.active_object.data.materials.append(mSil)

# Add bench
mWood = cm("BenchWood",(0.15,0.08,0.04,1),0,0.8)
mMetal = cm("BenchMetal",(0.05,0.05,0.05,1),0.7,0.3)
if not bpy.data.objects.get("Bench_Seat"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-11, 0.4, 8))
    bench = bpy.context.active_object; bench.name="Bench_Seat"
    bench.scale = (0.8, 0.1, 2)
    bench.data.materials.append(mWood)
    for lx in [-11.3, -10.7]:
        for lz in [7.2, 8.8]:
            lname = f"BenchLeg_{lx}_{lz}"
            if not bpy.data.objects.get(lname):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.4, location=(lx, 0.2, lz), vertices=8)
                leg = bpy.context.active_object; leg.name = lname
                leg.data.materials.append(mMetal)

# Add trash can
mTrashCan = cm("TrashCan",(0.03,0.03,0.03,1),0.5,0.4)
if not bpy.data.objects.get("TrashCan"):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.8, location=(-10.5, 0.4, -3), vertices=12)
    tc = bpy.context.active_object; tc.name="TrashCan"
    tc.data.materials.append(mTrashCan)

# Add street sign
mSignPost = cm("SignPost",(0.05,0.05,0.05,1),0.7,0.3)
mSignFace = cm("SignFace",(0.02,0.1,0.02,1),0,0.6)
if not bpy.data.objects.get("SignPost"):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=2.5, location=(-9.5, 1.25, 12), vertices=8)
    sp = bpy.context.active_object; sp.name="SignPost"
    sp.data.materials.append(mSignPost)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-9.5, 2.2, 12))
    sfg = bpy.context.active_object; sfg.name="SignFace"
    sfg.scale = (0.02, 0.4, 0.6)
    sfg.data.materials.append(mSignFace)

# Add subtle rain as thin lines using a single mesh
import bmesh
rain_mesh = bpy.data.meshes.new("RainLines")
rain_obj = bpy.data.objects.new("RainLines", rain_mesh)
bpy.context.collection.objects.link(rain_obj)
bm = bmesh.new()
for i in range(300):
    rx = random.uniform(-15, 15)
    ry = random.uniform(0.5, 10)
    rz = random.uniform(-25, 25)
    v1 = bm.verts.new((rx, ry, rz))
    v2 = bm.verts.new((rx + 0.01, ry - 0.12, rz + 0.01))
    bm.edges.new([v1, v2])
bm.to_mesh(rain_mesh)
bm.free()
mRain = cm("RainMat",(0.6,0.6,0.7,1),0.3,0.1,0.2,(0.4,0.4,0.5,1))
rain_obj.data.materials.append(mRain)
rain_obj.display_type = 'WIRE'

# Add more puddles near the action
mPu = cm("Puddle",(0.02,0.02,0.03,1),0.9,0.01)
for i in range(6):
    px = random.uniform(-2, 6)
    pz = random.uniform(-5, 5)
    pr = random.uniform(0.4, 1.2)
    p = bpy.data.objects.get(f"BigPuddle_{i}")
    if not p:
        bpy.ops.mesh.primitive_circle_add(radius=pr, fill_type='NGON', location=(px, 0.015, pz), vertices=16)
        p = bpy.context.active_object; p.name=f"BigPuddle_{i}"
        p.data.materials.append(mPu)

# Add a neon "OPEN" sign on a storefront
mNeonOpen = cm("NeonOpen",(1,0.8,0.2,1),0,0.1,4.0,(1,0.7,0.2,1))
if not bpy.data.objects.get("NeonOpen"):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.02, location=(-11, 3.2, -5), major_segments=16, minor_segments=6)
    no = bpy.context.active_object; no.name="NeonOpen"
    no.rotation_euler = (0, math.radians(90), 0)
    no.data.materials.append(mNeonOpen)

# Add a subtle warm bounce light from the storefronts
bpy.ops.object.light_add(type='AREA', location=(-11, 1, 0))
bounce1 = bpy.context.active_object; bounce1.name="BounceL"
bounce1.data.energy = 100
bounce1.data.color = (1.0, 0.8, 0.5)
bounce1.data.size = 4
bounce1.rotation_euler = (math.radians(90), 0, math.radians(90))

bpy.ops.object.light_add(type='AREA', location=(11, 1, 0))
bounce2 = bpy.context.active_object; bounce2.name="BounceR"
bounce2.data.energy = 100
bounce2.data.color = (1.0, 0.8, 0.5)
bounce2.data.size = 4
bounce2.rotation_euler = (math.radians(90), 0, math.radians(-90))

# Set render settings for better look
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.view_settings.exposure = 0.5

print("Fixed: camera repositioned, fog removed, rain reduced, lights boosted, cornices added, car/onlooker/bench/trash/sign added, render settings improved")
