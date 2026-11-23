import bpy
import math
import random
from mathutils import Vector

# The camera is pointing at the sky. Need to fix camera to look at the house.
# House is around (0,0,5-10), balloons above. Camera should be lower and looking up.

cam = bpy.data.objects.get("Camera")
if cam:
    # Place camera at a good viewing angle
    cam.location = (25, 25, 5)
    # Look at house center
    target = Vector((0, 0, 8))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    # Set lens for wider view
    cam.data.lens = 35

# Add more detail: house siding lines, roof shingles suggestion, 
# balloon highlights, more town variety, a lake, mountains in background

# --- House siding (horizontal lines) ---
mat_siding = bpy.data.materials.get("Siding")
if mat_siding is None:
    mat_siding = bpy.data.materials.new("Siding")
    mat_siding.use_nodes = True
    bsdf = mat_siding.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.85, 0.8, 0.7, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6

# Add horizontal siding strips on front face
for i in range(8):
    z = 3.5 + i * 0.6
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.02, z))
    siding = bpy.context.object
    siding.name = f"Siding_{i}"
    siding.scale = (3, 0.02, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    siding.data.materials.append(mat_siding)

# --- Roof shingles (small overlapping planes) ---
mat_shingle = bpy.data.materials.get("Shingle")
if mat_shingle is None:
    mat_shingle = bpy.data.materials.new("Shingle")
    mat_shingle.use_nodes = True
    bsdf = mat_shingle.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.3, 0.12, 0.08, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8

# Add shingle rows on roof
for row in range(5):
    z = 8.5 + row * 0.4
    scale_factor = 1 - row * 0.15
    for col in range(6):
        x = -2 + col * 0.8
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, z))
        shingle = bpy.context.object
        shingle.name = f"Shingle_{row}_{col}"
        shingle.scale = (0.7 * scale_factor, 3 * scale_factor, 0.03)
        bpy.ops.object.transform_apply(scale=True)
        shingle.data.materials.append(mat_shingle)

# --- Balloon highlights (small white spheres on top of some balloons) ---
balloon_col = bpy.data.collections.get("Balloons")
if balloon_col:
    mat_highlight = bpy.data.materials.get("BalloonHighlight")
    if mat_highlight is None:
        mat_highlight = bpy.data.materials.new("BalloonHighlight")
        mat_highlight.use_nodes = True
        bsdf = mat_highlight.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.2
    
    for i, obj in enumerate(balloon_col.objects[:100]):
        if obj.name.startswith("Balloon_"):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, segments=6, ring_count=4, 
                location=(obj.location.x - 0.05, obj.location.y - 0.05, obj.location.z + obj.dimensions.z*0.3))
            hl = bpy.context.object
            hl.name = f"BalloonHL_{i}"
            hl.data.materials.append(mat_highlight)
            for col in hl.users_collection:
                col.objects.unlink(hl)
            balloon_col.objects.link(hl)

# --- Add a lake ---
lake_col = bpy.data.collections.get("Lake")
if lake_col is None:
    lake_col = bpy.data.collections.new("Lake")
    bpy.context.scene.collection.children.link(lake_col)

mat_water = bpy.data.materials.get("Water")
if mat_water is None:
    mat_water = bpy.data.materials.new("Water")
    mat_water.use_nodes = True
    bsdf = mat_water.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.2, 0.4, 0.6, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.1
    bsdf.inputs["Metallic"].default_value = 0.3

bpy.ops.mesh.primitive_plane_add(size=15, location=(-20, 15, -4.95))
lake = bpy.context.object
lake.name = "Lake"
lake.data.materials.append(mat_water)
for col in lake.users_collection:
    col.objects.unlink(lake)
lake_col.objects.link(lake)

# --- Add mountains in background ---
mountain_col = bpy.data.collections.get("Mountains")
if mountain_col is None:
    mountain_col = bpy.data.collections.new("Mountains")
    bpy.context.scene.collection.children.link(mountain_col)

mat_mountain = bpy.data.materials.get("Mountain")
if mat_mountain is None:
    mat_mountain = bpy.data.materials.new("Mountain")
    mat_mountain.use_nodes = True
    bsdf = mat_mountain.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.4, 0.35, 0.3, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9

mat_snow = bpy.data.materials.get("Snow")
if mat_snow is None:
    mat_snow = bpy.data.materials.new("Snow")
    mat_snow.use_nodes = True
    bsdf = mat_snow.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.97, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5

for i in range(8):
    x = random.uniform(-80, 80)
    y = random.uniform(-80, -40)
    h = random.uniform(10, 25)
    w = random.uniform(15, 30)
    bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=w, radius2=0, depth=h, location=(x, y, -5 + h/2))
    mtn = bpy.context.object
    mtn.name = f"Mountain_{i}"
    mtn.data.materials.append(mat_mountain)
    for col in mtn.users_collection:
        col.objects.unlink(mtn)
    mountain_col.objects.link(mtn)
    
    # Snow cap
    bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=w*0.3, radius2=0, depth=h*0.3, location=(x, y, -5 + h - h*0.15))
    snow = bpy.context.object
    snow.name = f"SnowCap_{i}"
    snow.data.materials.append(mat_snow)
    for col in snow.users_collection:
        col.objects.unlink(snow)
    mountain_col.objects.link(snow)

# --- Add more varied town buildings ---
town_col = bpy.data.collections.get("Town")
if town_col:
    mat_town_house2 = bpy.data.materials.get("TownHouse2")
    if mat_town_house2 is None:
        mat_town_house2 = bpy.data.materials.new("TownHouse2")
        mat_town_house2.use_nodes = True
        bsdf = mat_town_house2.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.6, 0.5, 0.4, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.7
    
    mat_town_roof2 = bpy.data.materials.get("TownRoof2")
    if mat_town_roof2 is None:
        mat_town_roof2 = bpy.data.materials.new("TownRoof2")
        mat_town_roof2.use_nodes = True
        bsdf = mat_town_roof2.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.2, 0.3, 0.4, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.7
    
    for i in range(15):
        x = random.uniform(-35, 35)
        y = random.uniform(-35, 35)
        if abs(x) < 8 and abs(y) < 8:
            continue
        h = random.uniform(2, 6)
        w = random.uniform(2, 5)
        d = random.uniform(2, 5)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, -5 + h/2))
        th = bpy.context.object
        th.name = f"TownHouse2_{i}"
        th.scale = (w, d, h)
        bpy.ops.object.transform_apply(scale=True)
        th.data.materials.append(mat_town_house2)
        for col in th.users_collection:
            col.objects.unlink(th)
        town_col.objects.link(th)
        
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=max(w, d)*0.9, radius2=0, depth=1.5, location=(x, y, -5 + h + 0.75))
        tr = bpy.context.object
        tr.name = f"TownRoof2_{i}"
        tr.rotation_euler[2] = math.radians(45)
        tr.data.materials.append(mat_town_roof2)
        for col in tr.users_collection:
            col.objects.unlink(tr)
        town_col.objects.link(tr)

# --- Add a church with steeple ---
mat_church = bpy.data.materials.get("Church")
if mat_church is None:
    mat_church = bpy.data.materials.new("Church")
    mat_church.use_nodes = True
    bsdf = mat_church.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.85, 0.8, 0.7, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6

bpy.ops.mesh.primitive_cube_add(size=1, location=(15, -15, -3))
church_body = bpy.context.object
church_body.name = "ChurchBody"
church_body.scale = (4, 6, 4)
bpy.ops.object.transform_apply(scale=True)
church_body.data.materials.append(mat_church)

bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=5, radius2=0, depth=3, location=(15, -15, 1))
church_roof = bpy.context.object
church_roof.name = "ChurchRoof"
church_roof.rotation_euler[2] = math.radians(45)
church_roof.data.materials.append(mat_town_roof)

# Steeple
bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=3, location=(15, -15, 3.5))
steeple = bpy.context.object
steeple.name = "Steeple"
steeple.data.materials.append(mat_church)

bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1, radius2=0, depth=2, location=(15, -15, 5.5))
steeple_top = bpy.context.object
steeple_top.name = "SteepleTop"
steeple_top.rotation_euler[2] = math.radians(45)
steeple_top.data.materials.append(mat_town_roof)

# Cross on steeple
mat_cross = bpy.data.materials.get("Cross")
if mat_cross is None:
    mat_cross = bpy.data.materials.new("Cross")
    mat_cross.use_nodes = True
    bsdf = mat_cross.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.7, 0.2, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.8
    bsdf.inputs["Roughness"].default_value = 0.3

bpy.ops.mesh.primitive_cube_add(size=1, location=(15, -15, 6.8))
cross_v = bpy.context.object
cross_v.name = "CrossV"
cross_v.scale = (0.1, 0.1, 0.5)
bpy.ops.object.transform_apply(scale=True)
cross_v.data.materials.append(mat_cross)

bpy.ops.mesh.primitive_cube_add(size=1, location=(15, -15, 6.9))
cross_h = bpy.context.object
cross_h.name = "CrossH"
cross_h.scale = (0.3, 0.1, 0.1)
bpy.ops.object.transform_apply(scale=True)
cross_h.data.materials.append(mat_cross)

# --- Add a windmill ---
mat_windmill = bpy.data.materials.get("Windmill")
if mat_windmill is None:
    mat_windmill = bpy.data.materials.new("Windmill")
    mat_windmill.use_nodes = True
    bsdf = mat_windmill.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.7, 0.65, 0.6, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7

bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=2, radius2=1, depth=8, location=(-20, -20, -1))
windmill_body = bpy.context.object
windmill_body.name = "WindmillBody"
windmill_body.data.materials.append(mat_windmill)

# Windmill blades
mat_blade = bpy.data.materials.get("Blade")
if mat_blade is None:
    mat_blade = bpy.data.materials.new("Blade")
    mat_blade.use_nodes = True
    bsdf = mat_blade.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.9, 0.85, 0.8, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6

for i in range(4):
    angle = i * math.pi / 2
    x = -20 + math.cos(angle) * 2.5
    y = -20 + math.sin(angle) * 2.5
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 3))
    blade = bpy.context.object
    blade.name = f"WindmillBlade_{i}"
    blade.scale = (0.3, 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    blade.rotation_euler = (0, 0, angle)
    blade.data.materials.append(mat_blade)

# --- Add a dock by the lake ---
mat_dock = bpy.data.materials.get("Dock")
if mat_dock is None:
    mat_dock = bpy.data.materials.new("Dock")
    mat_dock.use_nodes = True
    bsdf = mat_dock.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.5, 0.35, 0.2, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8

bpy.ops.mesh.primitive_cube_add(size=1, location=(-12, 15, -4.8))
dock = bpy.context.object
dock.name = "Dock"
dock.scale = (3, 8, 0.1)
bpy.ops.object.transform_apply(scale=True)
dock.data.materials.append(mat_dock)

# Dock posts
for i in range(4):
    for j in range(2):
        x = -13.5 + i * 1
        y = 11 + j * 8
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1, location=(x, y, -4.5))
        post = bpy.context.object
        post.name = f"DockPost_{i}_{j}"
        post.data.materials.append(mat_dock)

# --- Add a boat on the lake ---
mat_boat = bpy.data.materials.get("Boat")
if mat_boat is None:
    mat_boat = bpy.data.materials.new("Boat")
    mat_boat.use_nodes = True
    bsdf = mat_boat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.6, 0.4, 0.2, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6

bpy.ops.mesh.primitive_cube_add(size=1, location=(-18, 18, -4.7))
boat = bpy.context.object
boat.name = "Boat"
boat.scale = (1, 2.5, 0.3)
bpy.ops.object.transform_apply(scale=True)
boat.data.materials.append(mat_boat)

# --- Add a lighthouse ---
mat_lighthouse = bpy.data.materials.get("Lighthouse")
if mat_lighthouse is None:
    mat_lighthouse = bpy.data.materials.new("Lighthouse")
    mat_lighthouse.use_nodes = True
    bsdf = mat_lighthouse.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.85, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5

mat_red_stripe = bpy.data.materials.get("RedStripe")
if mat_red_stripe is None:
    mat_red_stripe = bpy.data.materials.new("RedStripe")
    mat_red_stripe.use_nodes = True
    bsdf = mat_red_stripe.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5

bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=8, location=(-35, 30, -1))
lighthouse = bpy.context.object
lighthouse.name = "Lighthouse"
lighthouse.data.materials.append(mat_lighthouse)

# Red stripes
for i in range(3):
    z = -3 + i * 2.5
    bpy.ops.mesh.primitive_cylinder_add(radius=1.52, depth=0.8, location=(-35, 30, z))
    stripe = bpy.context.object
    stripe.name = f"LighthouseStripe_{i}"
    stripe.data.materials.append(mat_red_stripe)

# Lighthouse top
bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=1, location=(-35, 30, 3.5))
lh_top = bpy.context.object
lh_top.name = "LighthouseTop"
lh_top.data.materials.append(mat_red_stripe)

bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.3, radius2=0, depth=1.5, location=(-35, 30, 4.5))
lh_roof = bpy.context.object
lh_roof.name = "LighthouseRoof"
lh_roof.data.materials.append(mat_lighthouse)

# Light
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=8, ring_count=6, location=(-35, 30, 3.8))
lh_light = bpy.context.object
lh_light.name = "LighthouseLight"
mat_light = bpy.data.materials.get("LighthouseLightMat")
if mat_light is None:
    mat_light = bpy.data.materials.new("LighthouseLightMat")
    mat_light.use_nodes = True
    bsdf = mat_light.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (1.0, 0.9, 0.5, 1.0)
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.9, 0.5, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 5.0
    bsdf.inputs["Roughness"].default_value = 0.3
lh_light.data.materials.append(mat_light)

# --- Add a point light for the lighthouse ---
lh_light_data = bpy.data.lights.new("LighthouseLight", 'POINT')
lh_light_data.energy = 50
lh_light_data.color = (1.0, 0.9, 0.5)
lh_light_obj = bpy.data.objects.new("LighthouseLightObj", lh_light_data)
bpy.context.scene.collection.objects.link(lh_light_obj)
lh_light_obj.location = (-35, 30, 3.8)

print(f"Scene refined further. Objects: {len(bpy.data.objects)}")
