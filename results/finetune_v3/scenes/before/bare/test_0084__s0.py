import bpy
import math
import mathutils

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Helper: create a cube
def create_cube(name, size, location, color=(1,1,1,1), rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.8
    obj.data.materials.append(mat)
    return obj

# Helper: create a cylinder
def create_cylinder(name, radius, depth, location, color=(1,1,1,1), rotation=(0,0,0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, rotation=rotation, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.8
    obj.data.materials.append(mat)
    return obj

# Helper: create a plane
def create_plane(name, size, location, color=(1,1,1,1), rotation=(0,0,0)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.9
    obj.data.materials.append(mat)
    return obj

# Ground
ground = create_plane("Ground", 100, (0, 0, 0), color=(0.3, 0.5, 0.2, 1))
ground.scale = (1, 1, 1)

# Shooting line (long line on the ground)
shooting_line = create_plane("ShootingLine", 1, (0, -20, 0.01), color=(1, 1, 1, 1))
shooting_line.scale = (20, 0.2, 1)

# Straw targets at three distances (y = -30, -40, -50)
target_distances = [-30, -40, -50]
for i, dist in enumerate(target_distances):
    # Target stand (two vertical posts)
    for side in [-1, 1]:
        post = create_cylinder(f"TargetStandPost_{i}_{side}", 0.1, 1.8, (side * 0.8, dist, 0.9), color=(0.5, 0.3, 0.1, 1))
    # Crossbar
    crossbar = create_cylinder(f"TargetCrossbar_{i}", 0.08, 1.6, (0, dist, 1.6), color=(0.5, 0.3, 0.1, 1), rotation=(0, math.radians(90), 0))
    # Straw target (cylinder facing shooter)
    target = create_cylinder(f"StrawTarget_{i}", 0.5, 0.3, (0, dist, 1.2), color=(0.85, 0.75, 0.4, 1), rotation=(math.radians(90), 0, 0))
    # Target face (colored rings - simplified as a flat cylinder)
    face = create_cylinder(f"TargetFace_{i}", 0.5, 0.05, (0, dist + 0.16, 1.2), color=(0.9, 0.85, 0.6, 1), rotation=(math.radians(90), 0, 0))

# Scorekeeper's table
table_top = create_cube("ScorekeeperTableTop", 1, (10, -10, 0.75), color=(0.6, 0.4, 0.2, 1))
table_top.scale = (1.5, 1, 0.1)
for leg_pos in [(-0.6, -0.4), (0.6, -0.4), (-0.6, 0.4), (0.6, 0.4)]:
    leg = create_cylinder(f"TableLeg_{leg_pos[0]}_{leg_pos[1]}", 0.05, 0.75, (10 + leg_pos[0], -10 + leg_pos[1], 0.375), color=(0.4, 0.25, 0.1, 1))

# Chair for scorekeeper
chair_seat = create_cube("ChairSeat", 0.5, (10, -9, 0.45), color=(0.3, 0.3, 0.3, 1))
chair_seat.scale = (1, 1, 0.1)
chair_back = create_cube("ChairBack", 0.5, (10, -9.2, 0.7), color=(0.3, 0.3, 0.3, 1))
chair_back.scale = (1, 0.1, 1)
for leg_pos in [(-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)]:
    leg = create_cylinder(f"ChairLeg_{leg_pos[0]}_{leg_pos[1]}", 0.03, 0.45, (10 + leg_pos[0], -9 + leg_pos[1], 0.225), color=(0.2, 0.2, 0.2, 1))

# Arrow rack (near shooting line)
rack_base = create_cube("ArrowRackBase", 1, (-8, -15, 0.5), color=(0.5, 0.3, 0.1, 1))
rack_base.scale = (0.3, 1, 1)
# Arrow slots (small cylinders representing arrows)
for i in range(6):
    arrow = create_cylinder(f"Arrow_{i}", 0.02, 0.8, (-8, -15.5 + i * 0.15, 0.9), color=(0.7, 0.5, 0.2, 1))
    # Arrow head
    head = create_cylinder(f"ArrowHead_{i}", 0.04, 0.1, (-8, -15.5 + i * 0.15, 1.35), color=(0.2, 0.2, 0.2, 1))

# Striped pavilion
pavilion_center = (0, -5, 0)
# Four posts
for px in [-3, 3]:
    for py in [-2, 2]:
        post = create_cylinder(f"PavilionPost_{px}_{py}", 0.15, 3, (pavilion_center[0] + px, pavilion_center[1] + py, 1.5), color=(0.5, 0.3, 0.1, 1))

# Pavilion roof (pyramid-like, striped)
# Create a cone for the roof
bpy.ops.mesh.primitive_cone_add(radius1=5, radius2=0, depth=2, location=(pavilion_center[0], pavilion_center[1], 4), vertices=4)
roof = bpy.context.active_object
roof.name = "PavilionRoof"
roof.rotation_euler = (0, 0, math.radians(45))
# Create striped material for roof
roof_mat = bpy.data.materials.new("PavilionRoofMat")
roof_mat.use_nodes = True
nodes = roof_mat.node_tree.nodes
links = roof_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
# Create a stripe pattern using a wave texture
wave = nodes.new("ShaderNodeTexWave")
wave.inputs["Scale"].default_value = 10
wave.inputs["Distortion"].default_value = 0
wave.inputs["Detail"].default_value = 0
wave.inputs["Detail Scale"].default_value = 1
wave.bands_direction = 'X'
# Color ramp for stripes (red and white)
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.8, 0.1, 0.1, 1)  # Red
ramp.color_ramp.elements[1].color = (1, 1, 1, 1)  # White
links.new(wave.outputs["Color"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.7
roof.data.materials.append(roof_mat)

# Pavilion floor
pavilion_floor = create_plane("PavilionFloor", 8, (pavilion_center[0], pavilion_center[1], 0.02), color=(0.7, 0.6, 0.4, 1))
pavilion_floor.scale = (1, 0.8, 1)

# Add a bench inside the pavilion
bench = create_cube("PavilionBench", 1, (pavilion_center[0], pavilion_center[1], 0.45), color=(0.5, 0.3, 0.1, 1))
bench.scale = (2, 0.4, 0.1)
for leg_pos in [(-0.8, -0.15), (0.8, -0.15), (-0.8, 0.15), (0.8, 0.15)]:
    leg = create_cylinder(f"BenchLeg_{leg_pos[0]}_{leg_pos[1]}", 0.05, 0.45, (pavilion_center[0] + leg_pos[0], pavilion_center[1] + leg_pos[1], 0.225), color=(0.4, 0.25, 0.1, 1))

print("Archery range created successfully!")
