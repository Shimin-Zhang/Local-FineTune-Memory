import bpy, math, random
from mathutils import Vector

# Fix camera - point it at the character and lamp post
cam = bpy.data.objects.get("MainCam")
if cam:
    cam.location = (-8, 3, 4)
    # Look at the character at (2.5, 3.5, 0)
    target = Vector((2.5, 3.5, 0))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 35  # Wider lens to capture more of the scene
    cam.data.sensor_width = 36

# Increase light energies significantly
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        if obj.name.startswith("LampLight"):
            obj.data.energy = 500
        elif obj.name.startswith("LampL"):
            obj.data.energy = 300
        elif obj.name.startswith("StoreL"):
            obj.data.energy = 150
        elif obj.name.startswith("NeonL"):
            obj.data.energy = 80

# Add a subtle fill light from above to prevent pure black
bpy.ops.object.light_add(type='SUN', location=(0, 20, 0))
sun = bpy.context.active_object; sun.name="FillSun"
sun.data.energy = 0.5
sun.data.color = (0.3, 0.4, 0.6)
sun.rotation_euler = (math.radians(60), 0, math.radians(30))

# Add rain particles (simple falling streaks)
import bmesh
rain_mesh = bpy.data.meshes.new("Rain")
rain_obj = bpy.data.objects.new("Rain", rain_mesh)
bpy.context.collection.objects.link(rain_obj)
bm = bmesh.new()
for i in range(200):
    rx = random.uniform(-15, 15)
    ry = random.uniform(0, 15)
    rz = random.uniform(-25, 25)
    # Each rain drop is a small thin cylinder
    angle = math.radians(random.uniform(-5, 5))
    v1 = bm.verts.new((rx, ry, rz))
    v2 = bm.verts.new((rx + 0.02*math.sin(angle), ry - 0.15, rz + 0.02*math.cos(angle)))
    bm.edges.new([v1, v2])
bm.to_mesh(rain_mesh)
bm.free()
mRain = bpy.data.materials.get("RainMat") or bpy.data.materials.new("RainMat")
mRain.use_nodes = True
n = mRain.node_tree.nodes; l = mRain.node_tree.links; n.clear()
b = n.new('ShaderNodeBsdfPrincipled'); o = n.new('ShaderNodeOutputMaterial')
b.inputs['Base Color'].default_value = (0.7, 0.7, 0.8, 1)
b.inputs['Metallic'].default_value = 0.5
b.inputs['Roughness'].default_value = 0.1
b.inputs['Emission Color'].default_value = (0.5, 0.5, 0.6, 1)
b.inputs['Emission Strength'].default_value = 0.3
l.new(b.outputs['BSDF'], o.inputs['Surface'])
rain_obj.data.materials.append(mRain)
# Set rain as wireframe or thin lines - actually let's use a different approach
# Delete the edge mesh and use thin cylinders
bpy.data.objects.remove(rain_obj, do_unlink=True)
bpy.data.meshes.remove(rain_mesh)

# Rain as thin cylinders
for i in range(150):
    rx = random.uniform(-15, 15)
    ry = random.uniform(0.5, 12)
    rz = random.uniform(-25, 25)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.2, location=(rx, ry, rz), vertices=4)
    rd = bpy.context.active_object; rd.name=f"Rain_{i}"
    rd.rotation_euler = (math.radians(random.uniform(-3,3)), math.radians(random.uniform(-3,3)), 0)
    rd.data.materials.append(mRain)

# Add more detail: building cornices/moldings
for bx, bz, bw, bh, bd in [(-13,-15,6,15,8),(-13,-5,6,12,8),(-13,5,6,18,8),(-13,15,6,14,8),
                             (13,-15,6,16,8),(13,-5,6,13,8),(13,5,6,20,8),(13,15,6,15,8)]:
    # Cornice at top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, bh, bz))
    cor = bpy.context.active_object; cor.name=f"Cor_{bx}_{bz}"
    cor.scale = (bw*1.1, 0.3, bd*1.1)
    cor.data.materials.append(bpy.data.materials.get("StoneDark") or cm("StoneDark",(0.15,0.14,0.12,1),0,0.9))
    # Base molding
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, 0.2, bz))
    bas = bpy.context.active_object; bas.name=f"Bas_{bx}_{bz}"
    bas.scale = (bw*1.05, 0.4, bd*1.05)
    bas.data.materials.append(bpy.data.materials.get("StoneDark") or cm("StoneDark",(0.15,0.14,0.12,1),0,0.9))

# Add a crosswalk / street markings
mWhite = cm("StreetMark",(0.6,0.6,0.6,1),0,0.5)
for i in range(6):
    mz = -15 + i * 5
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.01, mz))
    mk = bpy.context.active_object; mk.name=f"CrossMark_{i}"
    mk.scale = (8, 0.02, 0.3)
    mk.data.materials.append(mWhite)

# Add parked car silhouette (simple box shape)
mCar = cm("CarBody",(0.05,0.05,0.08,1),0.3,0.3)
mWheel = cm("Wheel",(0.02,0.02,0.02,1),0.5,0.4)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-7, 0.5, -12))
car = bpy.context.active_object; car.name="Car_Body"
car.scale = (1.8, 1.2, 4)
car.data.materials.append(mCar)
# Car roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(-7, 1.2, -12.5))
roof = bpy.context.active_object; roof.name="Car_Roof"
roof.scale = (1.5, 0.8, 2.5)
roof.data.materials.append(mCar)
# Wheels
for wz in [-13.5, -10.5]:
    for wx in [-7.8, -6.2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(wx, 0.3, wz), vertices=12)
        wh = bpy.context.active_object; wh.name=f"Wheel_{wx}_{wz}"
        wh.rotation_euler = (0, math.radians(90), 0)
        wh.data.materials.append(mWheel)

# Add a second character silhouette in the background (onlooker)
mSil = cm("Silhouette",(0.01,0.01,0.01,1),0,0.8)
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.6, location=(-8, 0.8, 5), vertices=8)
onk = bpy.context.active_object; onk.name="Onlooker_Body"
onk.data.materials.append(mSil)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-8, 1.7, 5), segments=12, ring_count=6)
bpy.context.active_object.data.materials.append(mSil)

# Add more puddle reflections - larger ones near the lamp post
for i in range(5):
    px = random.uniform(0, 5)
    pz = random.uniform(-3, 3)
    pr = random.uniform(0.5, 1.5)
    bpy.ops.mesh.primitive_circle_add(radius=pr, fill_type='NGON', location=(px, 0.015, pz), vertices=16)
    p = bpy.context.active_object; p.name=f"BigPuddle_{i}"
    p.data.materials.append(bpy.data.materials.get("Puddle") or cm("Puddle",(0.02,0.02,0.03,1),0.9,0.01))

# Add a newspaper / trash on the ground
mTrash = cm("Trash",(0.3,0.25,0.2,1),0,0.9)
for i in range(5):
    tx = random.uniform(-5, 5)
    tz = random.uniform(-15, 15)
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(tx, 0.05, tz))
    tr = bpy.context.active_object; tr.name=f"Trash_{i}"
    tr.rotation_euler = (random.uniform(0,0.3), random.uniform(0,0.3), random.uniform(0,6.28))
    tr.data.materials.append(mTrash)

# Add a bench on the sidewalk
mWood = cm("BenchWood",(0.15,0.08,0.04,1),0,0.8)
mMetal = cm("BenchMetal",(0.05,0.05,0.05,1),0.7,0.3)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-11, 0.4, 8))
bench = bpy.context.active_object; bench.name="Bench_Seat"
bench.scale = (0.8, 0.1, 2)
bench.data.materials.append(mWood)
# Bench legs
for lx in [-11.3, -10.7]:
    for lz in [7.2, 8.8]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.4, location=(lx, 0.2, lz), vertices=8)
        leg = bpy.context.active_object; leg.name=f"BenchLeg_{lx}_{lz}"
        leg.data.materials.append(mMetal)

# Add a trash can
mTrashCan = cm("TrashCan",(0.03,0.03,0.03,1),0.5,0.4)
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.8, location=(-10.5, 0.4, -3), vertices=12)
tc = bpy.context.active_object; tc.name="TrashCan"
tc.data.materials.append(mTrashCan)

# Add a street sign
mSignPost = cm("SignPost",(0.05,0.05,0.05,1),0.7,0.3)
mSignFace = cm("SignFace",(0.02,0.1,0.02,1),0,0.6)
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=2.5, location=(-9.5, 1.25, 12), vertices=8)
sp = bpy.context.active_object; sp.name="SignPost"
sp.data.materials.append(mSignPost)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-9.5, 2.2, 12))
sfg = bpy.context.active_object; sfg.name="SignFace"
sfg.scale = (0.02, 0.4, 0.6)
sfg.data.materials.append(mSignFace)

# Add a subtle fog/volume for atmosphere
# Use a large cube with volume scatter
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5, 0))
fog = bpy.context.active_object; fog.name="FogVolume"
fog.scale = (30, 10, 50)
mFog = bpy.data.materials.new("FogMat")
mFog.use_nodes = True
n = mFog.node_tree.nodes; l = mFog.node_tree.links; n.clear()
vol = n.new('ShaderNodeVolumeScatter')
out = n.new('ShaderNodeOutputMaterial')
vol.inputs['Color'].default_value = (0.1, 0.1, 0.15, 1)
vol.inputs['Density'].default_value = 0.02
l.new(vol.outputs['Volume'], out.inputs['Volume'])
fog.data.materials.append(mFog)
fog.display_type = 'WIRE'
fog.visible_shadow = False

# Boost the main lamp light to be the hero light
ml = bpy.data.objects.get("LampLight_Main")
if ml:
    ml.data.energy = 800
    ml.data.shadow_soft_size = 0.5

# Add a rim light from behind the character for dramatic effect
bpy.ops.object.light_add(type='SPOT', location=(5, 6, -3))
rim = bpy.context.active_object; rim.name="RimLight"
rim.data.energy = 200
rim.data.color = (0.5, 0.6, 1.0)
rim.data.spot_size = math.radians(60)
rim.data.shadow_soft_size = 0.3
# Point it at the character
target = Vector((2.5, 3.5, 0))
direction = target - rim.location
rot_quat = direction.to_track_quat('-Z', 'Y')
rim.rotation_euler = rot_quat.to_euler()

print("Refined: camera fixed, lights boosted, rain added, car, onlooker, bench, trash, sign, fog, rim light")
