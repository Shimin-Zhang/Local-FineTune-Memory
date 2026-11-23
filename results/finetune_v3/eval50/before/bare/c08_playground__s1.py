import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up materials
def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    return mat

mat_ground = create_material("Ground", (0.4, 0.6, 0.2, 1.0))
mat_slide = create_material("Slide", (0.9, 0.5, 0.1, 1.0))
mat_swing_frame = create_material("SwingFrame", (0.2, 0.2, 0.2, 1.0))
mat_swing_seat = create_material("SwingSeat", (0.1, 0.3, 0.8, 1.0))
mat_sandbox = create_material("Sandbox", (0.9, 0.8, 0.5, 1.0))
mat_seesaw = create_material("Seesaw", (0.8, 0.1, 0.1, 1.0))
mat_pole = create_material("Pole", (0.3, 0.3, 0.3, 1.0))

# Ground
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.data.materials.append(mat_ground)

# --- Slide ---
# Slide base (steps)
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 0, 0.25 + i * 0.25))
    step = bpy.context.active_object
    step.scale = (0.3, 0.5, 0.25)
    step.data.materials.append(mat_slide)

# Slide surface (angled)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.5, 0, 1.0))
slide_surface = bpy.context.active_object
slide_surface.scale = (2.5, 0.5, 0.1)
slide_surface.rotation_euler = (0, math.radians(-15), 0)
slide_surface.data.materials.append(mat_slide)

# Slide supports
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.5, location=(3, 0, 0.75))
support1 = bpy.context.active_object
support1.data.materials.append(mat_pole)

bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.5, location=(0.5, 0, 0.75))
support2 = bpy.context.active_object
support2.data.materials.append(mat_pole)

# --- Swing Set ---
# Frame posts
for x in [-2, 2]:
    for y in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.5, location=(x, y, 1.25))
        post = bpy.context.active_object
        post.data.materials.append(mat_swing_frame)

# Top bar
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=4, location=(0, 0, 2.5))
top_bar = bpy.context.active_object
top_bar.rotation_euler = (math.radians(90), 0, 0)
top_bar.data.materials.append(mat_swing_frame)

# Swing chains and seats
for x in [-1, 1]:
    # Chain
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.5, location=(x, 0, 1.75))
    chain = bpy.context.active_object
    chain.data.materials.append(mat_swing_frame)
    
    # Seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 1.0))
    seat = bpy.context.active_object
    seat.scale = (0.3, 0.5, 0.05)
    seat.data.materials.append(mat_swing_seat)

# --- Sandbox ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(-4, 3, 0.2))
sandbox = bpy.context.active_object
sandbox.scale = (2, 2, 0.4)
sandbox.data.materials.append(mat_sandbox)

# Sandbox border
bpy.ops.mesh.primitive_cube_add(size=1, location=(-4, 3, 0.45))
border = bpy.context.active_object
border.scale = (2.1, 2.1, 0.1)
border.data.materials.append(mat_swing_frame)

# --- Seesaw ---
# Fulcrum
bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0, depth=0.5, location=(4, -3, 0.25))
fulcrum = bpy.context.active_object
fulcrum.data.materials.append(mat_pole)

# Seesaw board
bpy.ops.mesh.primitive_cube_add(size=1, location=(4, -3, 0.55))
seesaw_board = bpy.context.active_object
seesaw_board.scale = (2, 0.4, 0.08)
seesaw_board.rotation_euler = (0, math.radians(5), 0)
seesaw_board.data.materials.append(mat_seesaw)

# Set viewport to view the playground
bpy.ops.object.select_all(action='DESELECT')
bpy.context.scene.camera = bpy.data.objects.get("Camera")
if bpy.context.scene.camera:
    bpy.context.scene.camera.location = (0, -15, 8)
    bpy.context.scene.camera.rotation_euler = (math.radians(70), 0, 0)
