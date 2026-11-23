import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove default objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create materials
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

# Materials
sofa_mat = create_material("Sofa", (0.4, 0.2, 0.1, 1.0), roughness=0.8)
cushion_mat = create_material("Cushion", (0.5, 0.3, 0.15, 1.0), roughness=0.9)
table_mat = create_material("Wood", (0.3, 0.15, 0.05, 1.0), roughness=0.6)
metal_mat = create_material("Metal", (0.7, 0.7, 0.7, 1.0), roughness=0.3, metallic=1.0)
lamp_shade_mat = create_material("LampShade", (0.9, 0.85, 0.7, 1.0), roughness=0.7)
rug_mat = create_material("Rug", (0.6, 0.4, 0.3, 1.0), roughness=1.0)
floor_mat = create_material("Floor", (0.5, 0.4, 0.3, 1.0), roughness=0.8)
wall_mat = create_material("Wall", (0.8, 0.75, 0.7, 1.0), roughness=0.9)

# Create floor
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.data.materials.append(floor_mat)

# Create walls
# Back wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, -5, 2.5), rotation=(math.radians(90), 0, 0))
back_wall = bpy.context.active_object
back_wall.name = "BackWall"
back_wall.data.materials.append(wall_mat)

# Left wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(-5, 0, 2.5), rotation=(math.radians(90), 0, math.radians(90)))
left_wall = bpy.context.active_object
left_wall.name = "LeftWall"
left_wall.data.materials.append(wall_mat)

# Right wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(5, 0, 2.5), rotation=(math.radians(90), 0, math.radians(-90)))
right_wall = bpy.context.active_object
right_wall.name = "RightWall"
right_wall.data.materials.append(wall_mat)

# Create sofa
# Sofa base
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -3, 0.3))
sofa_base = bpy.context.active_object
sofa_base.name = "SofaBase"
sofa_base.scale = (2, 1, 0.3)
sofa_base.data.materials.append(sofa_mat)

# Sofa back
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -3.4, 0.6))
sofa_back = bpy.context.active_object
sofa_back.name = "SofaBack"
sofa_back.scale = (2, 0.2, 0.6)
sofa_back.data.materials.append(sofa_mat)

# Sofa armrests
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.8, -3, 0.4))
arm_left = bpy.context.active_object
arm_left.name = "ArmLeft"
arm_left.scale = (0.2, 1, 0.4)
arm_left.data.materials.append(sofa_mat)

bpy.ops.mesh.primitive_cube_add(size=1, location=(1.8, -3, 0.4))
arm_right = bpy.context.active_object
arm_right.name = "ArmRight"
arm_right.scale = (0.2, 1, 0.4)
arm_right.data.materials.append(sofa_mat)

# Sofa cushions
for i, x in enumerate([-0.7, 0, 0.7]):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -3, 0.55))
    cushion = bpy.context.active_object
    cushion.name = f"Cushion{i}"
    cushion.scale = (0.6, 0.8, 0.15)
    cushion.data.materials.append(cushion_mat)

# Create coffee table
# Table top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.5, 0.4))
table_top = bpy.context.active_object
table_top.name = "TableTop"
table_top.scale = (1, 0.6, 0.05)
table_top.data.materials.append(table_mat)

# Table legs
for x, y in [(-0.9, -1.1), (0.9, -1.1), (-0.9, -1.9), (0.9, -1.9)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.4, location=(x, y, 0.2))
    leg = bpy.context.active_object
    leg.name = f"TableLeg_{x}_{y}"
    leg.data.materials.append(table_mat)

# Create floor lamp
# Lamp base
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.05, location=(3, -3, 0.025))
lamp_base = bpy.context.active_object
lamp_base.name = "LampBase"
lamp_base.data.materials.append(metal_mat)

# Lamp pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.5, location=(3, -3, 0.8))
lamp_pole = bpy.context.active_object
lamp_pole.name = "LampPole"
lamp_pole.data.materials.append(metal_mat)

# Lamp shade
bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0.15, depth=0.3, location=(3, -3, 1.6))
lamp_shade = bpy.context.active_object
lamp_shade.name = "LampShade"
lamp_shade.data.materials.append(lamp_shade_mat)

# Add a point light for the lamp
bpy.ops.object.light_add(type='POINT', location=(3, -3, 1.5))
lamp_light = bpy.context.active_object
lamp_light.name = "LampLight"
lamp_light.data.energy = 50
lamp_light.data.color = (1.0, 0.9, 0.7)

# Create rug
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -1.5, 0.01))
rug = bpy.context.active_object
rug.name = "Rug"
rug.scale = (2.5, 1.5, 1)
rug.data.materials.append(rug_mat)

# Add a sun light for ambient lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
sun_light = bpy.context.active_object
sun_light.name = "SunLight"
sun_light.data.energy = 3
sun_light.rotation_euler = (math.radians(45), math.radians(30), 0)

# Set up camera
bpy.ops.object.camera_add(location=(4, 4, 2), rotation=(math.radians(60), 0, math.radians(45)))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Living room created successfully!")
