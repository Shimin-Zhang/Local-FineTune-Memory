import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- World / Sky (first light) ---
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

bg = nodes.new('ShaderNodeBackground')
bg.inputs[0].default_value = (0.05, 0.08, 0.15, 1.0)
bg.inputs[1].default_value = 0.3

sky = nodes.new('ShaderNodeTexSky')
sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(3)   # first light
sky.sun_rotation = math.radians(180)
sky.sun_intensity = 2.0
sky.altitude = 100
sky.air_density = 2.0
sky.dust_density = 1.5

out = nodes.new('ShaderNodeOutputWorld')
links.new(sky.outputs['Color'], bg.inputs[0])
links.new(bg.outputs['Background'], out.inputs['Surface'])

# --- Sun light ---
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_data.color = (1.0, 0.85, 0.6)
sun_data.angle = math.radians(2)
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(85), 0, math.radians(180))

# --- Materials ---
def make_mat(name, color, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    return m

marble = make_mat("Marble", (0.85, 0.82, 0.75), rough=0.4)
bronze = make_mat("Bronze", (0.45, 0.3, 0.15), rough=0.3, metal=0.9)
stone  = make_mat("Stone", (0.5, 0.45, 0.4), rough=0.8)
grass  = make_mat("Grass", (0.15, 0.3, 0.1), rough=0.9)
dirt   = make_mat("Dirt", (0.35, 0.25, 0.15), rough=0.9)
water  = make_mat("Water", (0.05, 0.15, 0.3), rough=0.1)

# --- Sea ---
bpy.ops.mesh.primitive_plane_add(size=500, location=(0, -150, -5))
sea = bpy.context.active_object
sea.name = "Sea"
sea.data.materials.append(water)

# --- Cape (rocky ground) ---
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 20, 0))
cape = bpy.context.active_object
cape.name = "Cape"
cape.data.materials.append(grass)

# Displace for rocky look
mod = cape.modifiers.new("Disp", 'DISPLACE')
tex = bpy.data.textures.new("RockTex", type='CLOUDS')
tex.noise_scale = 8.0
mod.texture = tex
mod.strength = 2.0
bpy.ops.object.modifier_apply(modifier="Disp")

# Flatten the top area for the temple
for v in cape.data.vertices:
    if v.co.y > 10 and v.co.y < 60 and abs(v.co.x) < 30:
        v.co.z = max(v.co.z, 0.5)

# --- Stepped base (stereobate) ---
base_steps = 3
base_w, base_d = 20, 14
for i in range(base_steps):
    w = base_w - i * 1.0
    d = base_d - i * 1.0
    h = 0.4
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 30, 0.2 + i * h))
    step = bpy.context.active_object
    step.name = f"BaseStep_{i}"
    step.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    step.data.materials.append(marble)

# --- Fluted Doric Columns ---
def create_fluted_column(name, loc, height=6.0, radius=0.5):
    """Create a fluted Doric column."""
    # Shaft with flutes (use cylinder with high segments and displace)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=height, location=loc)
    col = bpy.context.active_object
    col.name = name
    # Add flutes via simple deformation: scale alternating verts
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(col.data)
    for v in bm.verts:
        angle = math.atan2(v.co.y, v.co.x)
        flute = 1.0 + 0.06 * math.sin(12 * angle)  # 12 flutes
        v.co.x *= flute
        v.co.y *= flute
    bm.to_mesh(col.data)
    bm.free()
    col.data.materials.append(marble)

    # Capital (echinus + abacus)
    cap_h = 0.5
    cap_loc = (loc[0], loc[1], loc[2] + height/2 + cap_h/2)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius*1.3, depth=cap_h*0.4, location=cap_loc)
    echinus = bpy.context.active_object
    echinus.name = name + "_Echinus"
    echinus.data.materials.append(marble)

    abacus_loc = (loc[0], loc[1], loc[2] + height/2 + cap_h*0.7)
    bpy.ops.mesh.primitive_cube_add(size=1, location=abacus_loc)
    abacus = bpy.context.active_object
    abacus.name = name + "_Abacus"
    abacus.scale = (radius*2.2, radius*2.2, cap_h*0.3)
    bpy.ops.object.transform_apply(scale=True)
    abacus.data.materials.append(marble)

    # Base (torus-like plinth)
    plinth_loc = (loc[0], loc[1], loc[2] - height/2 + 0.15)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius*1.15, depth=0.3, location=plinth_loc)
    plinth = bpy.context.active_object
    plinth.name = name + "_Plinth"
    plinth.data.materials.append(marble)

    return col

# Row of columns along the front
num_cols = 8
spacing = 2.5
col_height = 6.0
col_radius = 0.5
base_top_z = 0.2 + base_steps * 0.4  # top of base

for i in range(num_cols):
    x = -((num_cols - 1) / 2) * spacing + i * spacing
    loc = (x, 30, base_top_z + col_height / 2)
    create_fluted_column(f"Col_{i}", loc, height=col_height, radius=col_radius)

# --- Entablature (simplified architrave + frieze + cornice) ---
ent_w = num_cols * spacing + 2
ent_d = base_d + 2
ent_z = base_top_z + col_height + 0.5

# Architrave
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 30, ent_z))
arch = bpy.context.active_object
arch.name = "Architrave"
arch.scale = (ent_w, ent_d, 0.5)
bpy.ops.object.transform_apply(scale=True)
arch.data.materials.append(marble)

# Frieze (triglyphs simplified)
frieze_z = ent_z + 0.5
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 30, frieze_z))
frieze = bpy.context.active_object
frieze.name = "Frieze"
frieze.scale = (ent_w, ent_d, 0.6)
bpy.ops.object.transform_apply(scale=True)
frieze.data.materials.append(marble)

# Cornice
cornice_z = frieze_z + 0.6
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 30, cornice_z))
cornice = bpy.context.active_object
cornice.name = "Cornice"
cornice.scale = (ent_w + 1, ent_d + 1, 0.4)
bpy.ops.object.transform_apply(scale=True)
cornice.data.materials.append(marble)

# --- Bronze Brazier ---
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.8, depth=0.3, location=(0, 30, base_top_z + 0.15))
brazier_base = bpy.context.active_object
brazier_base.name = "Brazier_Base"
brazier_base.data.materials.append(bronze)

bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.6, depth=0.8, location=(0, 30, base_top_z + 0.7))
brazier_body = bpy.context.active_object
brazier_body.name = "Brazier_Body"
brazier_body.data.materials.append(bronze)

bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.5, location=(0, 30, base_top_z + 1.3))
brazier_bowl = bpy.context.active_object
brazier_bowl.name = "Brazier_Bowl"
brazier_bowl.scale = (1, 1, 0.5)
bpy.ops.object.transform_apply(scale=True)
brazier_bowl.data.materials.append(bronze)

# --- Goat Path from shore to temple ---
# Create a winding path using a series of small cubes/planes
path_points = []
start = (0, 5, 0)   # shore
end = (0, 25, base_top_z)  # near temple base

num_path_segments = 20
for i in range(num_path_segments):
    t = i / (num_path_segments - 1)
    x = math.sin(t * math.pi * 2) * 3 * (1 - t)  # gentle curve
    y = start[1] + (end[1] - start[1]) * t
    z = 0.1 + t * (base_top_z - 0.1)
    path_points.append((x, y, z))

for i, (px, py, pz) in enumerate(path_points):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(px, py, pz))
    seg = bpy.context.active_object
    seg.name = f"Path_{i}"
    seg.scale = (1.5, 0.8, 0.1)
    # Slight random rotation for natural look
    seg.rotation_euler = (0, 0, random.uniform(-0.1, 0.1))
    bpy.ops.object.transform_apply(scale=True)
    seg.data.materials.append(dirt)

# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (25, -10, 8)
# Point camera at temple
target = Vector((0, 30, 5))
direction = target - cam_obj.location
rot_quat = direction.to_track_quat('Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam_obj

# --- Render settings ---
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'

print("Doric temple scene built successfully.")
