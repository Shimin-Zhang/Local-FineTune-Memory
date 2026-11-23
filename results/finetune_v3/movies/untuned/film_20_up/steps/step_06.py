import bpy
import math
import random
from mathutils import Vector

# Fix the error: mat_town_roof was not defined. Let's get or create it.
mat_town_roof = bpy.data.materials.get("TownRoof")
if mat_town_roof is None:
    mat_town_roof = bpy.data.materials.new("TownRoof")
    mat_town_roof.use_nodes = True
    bsdf = mat_town_roof.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.4, 0.2, 0.15, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7

# Check if church roof was created before error - if not, create it
if bpy.data.objects.get("ChurchRoof") is None:
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=5, radius2=0, depth=3, location=(15, -15, 1))
    church_roof = bpy.context.object
    church_roof.name = "ChurchRoof"
    church_roof.rotation_euler[2] = math.radians(45)
    church_roof.data.materials.append(mat_town_roof)

# Check if steeple was created
if bpy.data.objects.get("Steeple") is None:
    mat_church = bpy.data.materials.get("Church")
    if mat_church is None:
        mat_church = bpy.data.materials.new("Church")
        mat_church.use_nodes = True
        bsdf = mat_church.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.85, 0.8, 0.7, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.6
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=3, location=(15, -15, 3.5))
    steeple = bpy.context.object
    steeple.name = "Steeple"
    steeple.data.materials.append(mat_church)
    
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1, radius2=0, depth=2, location=(15, -15, 5.5))
    steeple_top = bpy.context.object
    steeple_top.name = "SteepleTop"
    steeple_top.rotation_euler[2] = math.radians(45)
    steeple_top.data.materials.append(mat_town_roof)
    
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

# Continue with windmill, dock, boat, lighthouse
# Windmill
mat_windmill = bpy.data.materials.get("Windmill")
if mat_windmill is None:
    mat_windmill = bpy.data.materials.new("Windmill")
    mat_windmill.use_nodes = True
    bsdf = mat_windmill.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.7, 0.65, 0.6, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7

if bpy.data.objects.get("WindmillBody") is None:
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=2, radius2=1, depth=8, location=(-20, -20, -1))
    windmill_body = bpy.context.object
    windmill_body.name = "WindmillBody"
    windmill_body.data.materials.append(mat_windmill)
    
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

# Dock
mat_dock = bpy.data.materials.get("Dock")
if mat_dock is None:
    mat_dock = bpy.data.materials.new("Dock")
    mat_dock.use_nodes = True
    bsdf = mat_dock.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.5, 0.35, 0.2, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8

if bpy.data.objects.get("Dock") is None:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-12, 15, -4.8))
    dock = bpy.context.object
    dock.name = "Dock"
    dock.scale = (3, 8, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    dock.data.materials.append(mat_dock)
    
    for i in range(4):
        for j in range(2):
            x = -13.5 + i * 1
            y = 11 + j * 8
            bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1, location=(x, y, -4.5))
            post = bpy.context.object
            post.name = f"DockPost_{i}_{j}"
            post.data.materials.append(mat_dock)

# Boat
mat_boat = bpy.data.materials.get("Boat")
if mat_boat is None:
    mat_boat = bpy.data.materials.new("Boat")
    mat_boat.use_nodes = True
    bsdf = mat_boat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.6, 0.4, 0.2, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6

if bpy.data.objects.get("Boat") is None:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-18, 18, -4.7))
    boat = bpy.context.object
    boat.name = "Boat"
    boat.scale = (1, 2.5, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    boat.data.materials.append(mat_boat)

# Lighthouse
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

if bpy.data.objects.get("Lighthouse") is None:
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=8, location=(-35, 30, -1))
    lighthouse = bpy.context.object
    lighthouse.name = "Lighthouse"
    lighthouse.data.materials.append(mat_lighthouse)
    
    for i in range(3):
        z = -3 + i * 2.5
        bpy.ops.mesh.primitive_cylinder_add(radius=1.52, depth=0.8, location=(-35, 30, z))
        stripe = bpy.context.object
        stripe.name = f"LighthouseStripe_{i}"
        stripe.data.materials.append(mat_red_stripe)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=1, location=(-35, 30, 3.5))
    lh_top = bpy.context.object
    lh_top.name = "LighthouseTop"
    lh_top.data.materials.append(mat_red_stripe)
    
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.3, radius2=0, depth=1.5, location=(-35, 30, 4.5))
    lh_roof = bpy.context.object
    lh_roof.name = "LighthouseRoof"
    lh_roof.data.materials.append(mat_lighthouse)
    
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
    
    if bpy.data.objects.get("LighthouseLightObj") is None:
        lh_light_data = bpy.data.lights.new("LighthouseLight", 'POINT')
        lh_light_data.energy = 50
        lh_light_data.color = (1.0, 0.9, 0.5)
        lh_light_obj = bpy.data.objects.new("LighthouseLightObj", lh_light_data)
        bpy.context.scene.collection.objects.link(lh_light_obj)
        lh_light_obj.location = (-35, 30, 3.8)

# Add more balloons to fill out the cloud (the scene looks like it could use more)
balloon_col = bpy.data.collections.get("Balloons")
if balloon_col:
    balloon_colors = [
        (1.0, 0.2, 0.2), (1.0, 0.6, 0.1), (1.0, 0.9, 0.2),
        (0.2, 0.8, 0.2), (0.2, 0.4, 0.9), (0.5, 0.2, 0.8),
        (0.9, 0.3, 0.6), (0.1, 0.8, 0.8), (0.8, 0.5, 0.1),
        (0.3, 0.7, 0.5), (0.7, 0.3, 0.3), (0.4, 0.4, 0.9),
    ]
    random.seed(123)
    for i in range(300):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0.5, 9)
        x = math.cos(angle) * radius + random.uniform(-1, 1)
        y = math.sin(angle) * radius + random.uniform(-1, 1)
        z = random.uniform(11, 23)
        r = random.uniform(0.25, 0.4)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=8, ring_count=6, location=(x, y, z))
        balloon = bpy.context.object
        balloon.name = f"Balloon_{1000+i}"
        color = random.choice(balloon_colors)
        mat = bpy.data.materials.get(f"BalloonMat_{1000+i}")
        if mat is None:
            mat = bpy.data.materials.new(f"BalloonMat_{1000+i}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.3
        balloon.data.materials.append(mat)
        for col in balloon.users_collection:
            col.objects.unlink(balloon)
        balloon_col.objects.link(balloon)

# Add a few more ropes
chimney_top_pos = Vector((1.5, -1.5, 10.5))
rope_col = bpy.data.collections.get("Ropes")
if rope_col:
    mat_rope = bpy.data.materials.get("Rope")
    if mat_rope is None:
        mat_rope = bpy.data.materials.new("Rope")
        mat_rope.use_nodes = True
        bsdf = mat_rope.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.4, 0.3, 0.2, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
    
    for i in range(100):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(1, 7)
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        z = random.uniform(12, 20)
        start = chimney_top_pos
        end = Vector((x, y, z))
        mid = (start + end) / 2
        mid.z -= random.uniform(0.5, 2)
        
        curve_data = bpy.data.curves.new(f"RopeCurve_{1000+i}", 'CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.02
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(2)
        spline.bezier_points[0].co = start
        spline.bezier_points[0].handle_left_type = 'AUTO'
        spline.bezier_points[0].handle_right_type = 'AUTO'
        spline.bezier_points[1].co = mid
        spline.bezier_points[1].handle_left_type = 'AUTO'
        spline.bezier_points[1].handle_right_type = 'AUTO'
        spline.bezier_points[2].co = end
        spline.bezier_points[2].handle_left_type = 'AUTO'
        spline.bezier_points[2].handle_right_type = 'AUTO'
        
        rope_obj = bpy.data.objects.new(f"Rope_{1000+i}", curve_data)
        rope_obj.data.materials.append(mat_rope)
        rope_col.objects.link(rope_obj)

# Add a small garden fence around the house
mat_fence = bpy.data.materials.get("Fence")
if mat_fence is None:
    mat_fence = bpy.data.materials.new("Fence")
    mat_fence.use_nodes = True
    bsdf = mat_fence.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.75, 0.7, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7

# Fence around house (front, left, right)
for i in range(8):
    x = -3 + i * 0.9
    for y in [6, -6]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 3.3))
        post = bpy.context.object
        post.name = f"HouseFencePost_{i}_{y}"
        post.scale = (0.08, 0.08, 0.4)
        bpy.ops.object.transform_apply(scale=True)
        post.data.materials.append(mat_fence)

# Fence rails
for y in [6, -6]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, 3.4))
    rail = bpy.context.object
    rail.name = f"HouseFenceRail_{y}"
    rail.scale = (3.5, 0.05, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    rail.data.materials.append(mat_fence)

# Side fences
for x in [-3, 3]:
    for i in range(8):
        y = -5 + i * 1.4
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 3.3))
        post = bpy.context.object
        post.name = f"HouseFenceSidePost_{x}_{i}"
        post.scale = (0.08, 0.08, 0.4)
        bpy.ops.object.transform_apply(scale=True)
        post.data.materials.append(mat_fence)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 3.4))
    rail = bpy.context.object
    rail.name = f"HouseFenceSideRail_{x}"
    rail.scale = (0.05, 5, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    rail.data.materials.append(mat_fence)

print(f"Scene complete. Objects: {len(bpy.data.objects)}")
