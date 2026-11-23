import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Helper function to create a cylinder segment
def create_cylinder(name, radius_top, radius_bottom, depth, z_center, color):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius_bottom, depth=depth, location=(0, 0, z_center))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale[0] = radius_top / radius_bottom
    obj.scale[1] = radius_top / radius_bottom
    bpy.ops.object.transform_apply(scale=True)
    
    # Set material
    mat = bpy.data.materials.new(name=name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.5
    obj.data.materials.append(mat)
    return obj

# Lighthouse parameters
tower_height = 10
base_radius = 2
top_radius = 1.2
num_bands = 5
band_height = tower_height / num_bands

# Create the lighthouse tower with alternating red and white bands
z_offset = 0
for i in range(num_bands):
    # Calculate radii for this band (linear taper)
    t_bottom = i / num_bands
    t_top = (i + 1) / num_bands
    r_bottom = base_radius - (base_radius - top_radius) * t_bottom
    r_top = base_radius - (base_radius - top_radius) * t_top
    
    # Alternate colors: white, red, white, red, white
    color = (1, 1, 1, 1) if i % 2 == 0 else (0.8, 0.1, 0.1, 1)
    
    band = create_cylinder(
        name=f"band_{i}",
        radius_top=r_top,
        radius_bottom=r_bottom,
        depth=band_height,
        z_center=z_offset + band_height / 2,
        color=color
    )
    z_offset += band_height

# Add a base platform
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=base_radius + 0.5, depth=0.5, location=(0, 0, -0.25))
base = bpy.context.active_object
base.name = "base_platform"
mat = bpy.data.materials.new(name="base_mat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1)
bsdf.inputs["Roughness"].default_value = 0.8
base.data.materials.append(mat)

# Add the lantern room (glass section)
lantern_z = tower_height + 0.5
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=top_radius + 0.2, depth=1, location=(0, 0, lantern_z))
lantern = bpy.context.active_object
lantern.name = "lantern_room"
mat = bpy.data.materials.new(name="lantern_mat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.8, 0.9, 1, 1)
bsdf.inputs["Roughness"].default_value = 0.1
bsdf.inputs["Transmission Weight"].default_value = 0.9
lantern.data.materials.append(mat)

# Add the roof (cone)
roof_z = lantern_z + 0.5 + 0.5
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=top_radius + 0.3, radius2=0, depth=1, location=(0, 0, roof_z))
roof = bpy.context.active_object
roof.name = "roof"
mat = bpy.data.materials.new(name="roof_mat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
bsdf.inputs["Roughness"].default_value = 0.4
roof.data.materials.append(mat)

# Add a light source inside the lantern
bpy.ops.object.light_add(type='POINT', location=(0, 0, lantern_z))
light = bpy.context.active_object
light.name = "lighthouse_light"
light.data.energy = 500
light.data.color = (1, 0.9, 0.5)

# Add a sun light for scene illumination
bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
sun = bpy.context.active_object
sun.name = "sun_light"
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add a ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, -0.5))
ground = bpy.context.active_object
ground.name = "ground"
mat = bpy.data.materials.new(name="ground_mat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.2, 0.4, 0.2, 1)
bsdf.inputs["Roughness"].default_value = 0.9
ground.data.materials.append(mat)

print("Lighthouse built successfully!")
