import bpy
import math
import random
from mathutils import Vector

# The scene looks good but needs more detail and refinement
# Let's add:
# 1. Better road markings (lane lines, crosswalks)
# 2. More detailed cars with headlights
# 3. More people in the crowd with varied poses
# 4. Building details: doors, fire escapes, rooftop structures
# 5. More atmospheric effects
# 6. Better camera angle
# 7. Add a few more street details

# Add road markings - lane lines
for i in range(20):
    y = -60 + i * 6
    # Center line
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, y, 0.01))
    line = bpy.context.active_object
    line.name = f"LaneLine_{i}"
    line.scale = (0.15, 2, 0.01)
    mat_line = bpy.data.materials.new(f"LaneLine_{i}_mat")
    mat_line.use_nodes = True
    bsdf = mat_line.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.3, 1.0)
    line.data.materials.append(mat_line)

# Crosswalks
for cx in [-2, 2]:
    for i in range(8):
        y = -10 + i * 0.8
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(cx, y, 0.01))
        cw = bpy.context.active_object
        cw.name = f"Crosswalk_{cx}_{i}"
        cw.scale = (0.3, 0.4, 0.01)
        mat_cw = bpy.data.materials.new(f"Crosswalk_{cx}_{i}_mat")
        mat_cw.use_nodes = True
        bsdf = mat_cw.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1.0)
        cw.data.materials.append(mat_cw)

# Add headlights to cars
for i in range(6):
    # Find car objects
    car = bpy.data.objects.get(f"Car_{i}")
    if car:
        x, y, z = car.location
        # Headlights (front)
        for side in [-1, 1]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x + side * 0.7, y - 2, z))
            hl = bpy.context.active_object
            hl.name = f"Car_{i}_Headlight_{side}"
            mat_hl = bpy.data.materials.new(f"Car_{i}_Headlight_{side}_mat")
            mat_hl.use_nodes = True
            bsdf = mat_hl.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 0.8, 1.0)
            bsdf.inputs['Emission Color'].default_value = (1.0, 1.0, 0.8, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 10.0
            hl.data.materials.append(mat_hl)
            
            # Headlight glow (point light)
            light_data = bpy.data.lights.new(f"Car_{i}_HL_Light_{side}", type='POINT')
            light_data.energy = 20
            light_data.color = (1.0, 1.0, 0.8)
            light_data.shadow_soft_size = 0.3
            light_obj = bpy.data.objects.new(f"Car_{i}_HL_Light_{side}", light_data)
            light_obj.location = (x + side * 0.7, y - 2.2, z)
            bpy.context.collection.objects.link(light_obj)
        
        # Taillights (back)
        for side in [-1, 1]:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x + side * 0.7, y + 2, z))
            tl = bpy.context.active_object
            tl.name = f"Car_{i}_Taillight_{side}"
            mat_tl = bpy.data.materials.new(f"Car_{i}_Taillight_{side}_mat")
            mat_tl.use_nodes = True
            bsdf = mat_tl.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)
            bsdf.inputs['Emission Color'].default_value = (1.0, 0.0, 0.0, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 5.0
            tl.data.materials.append(mat_tl)

# Add more people with varied appearances
for i in range(40):
    x = random.uniform(-7, 7)
    y = random.uniform(-55, 55)
    if abs(x) < 2.5:
        continue
    
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(x, y, 0.7))
    person = bpy.context.active_object
    person.name = f"Person2_{i}"
    person.scale = (0.7, 0.7, 1.1)
    # Varied clothing colors
    cloth_colors = [
        (0.5, 0.2, 0.2, 1.0), (0.2, 0.3, 0.5, 1.0), (0.3, 0.5, 0.3, 1.0),
        (0.6, 0.5, 0.2, 1.0), (0.4, 0.2, 0.5, 1.0), (0.2, 0.4, 0.4, 1.0),
        (0.5, 0.3, 0.4, 1.0), (0.3, 0.3, 0.3, 1.0),
    ]
    color = random.choice(cloth_colors)
    mat_person = bpy.data.materials.new(f"Person2_{i}_mat")
    mat_person.use_nodes = True
    bsdf = mat_person.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    person.data.materials.append(mat_person)
    
    # Head
    skin_colors = [(0.8, 0.6, 0.5, 1.0), (0.9, 0.7, 0.6, 1.0), (0.6, 0.4, 0.3, 1.0), (0.5, 0.3, 0.2, 1.0), (0.7, 0.5, 0.4, 1.0)]
    skin = random.choice(skin_colors)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(x, y, 1.15))
    phead = bpy.context.active_object
    phead.name = f"Person2_{i}_Head"
    mat_phead = bpy.data.materials.new(f"Person2_{i}_Head_mat")
    mat_phead.use_nodes = True
    bsdf = mat_phead.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = skin
    phead.data.materials.append(mat_phead)

# Add building doors
for i in range(8):
    y_pos = -60 + i * 16
    for side in [-1, 1]:
        x = side * 12
        # Door
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x - side * 1, y_pos, 1.2))
        door = bpy.context.active_object
        door.name = f"Door_{side}_{i}"
        door.scale = (0.8, 0.1, 1.2)
        mat_door = bpy.data.materials.new(f"Door_{side}_{i}_mat")
        mat_door.use_nodes = True
        bsdf = mat_door.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.15, 0.1, 0.05, 1.0)
        door.data.materials.append(mat_door)
        
        # Door frame
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x - side * 1, y_pos, 2.5))
        frame = bpy.context.active_object
        frame.name = f"DoorFrame_{side}_{i}"
        frame.scale = (1.0, 0.05, 0.1)
        mat_frame = bpy.data.materials.new(f"DoorFrame_{side}_{i}_mat")
        mat_frame.use_nodes = True
        bsdf = mat_frame.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.3, 0.25, 0.2, 1.0)
        frame.data.materials.append(mat_frame)

# Add fire escapes to some buildings
for i in range(4):
    y_pos = -50 + i * 25
    for side in [-1, 1]:
        x = side * 12
        # Fire escape platform
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x - side * 0.5, y_pos, 8))
        platform = bpy.context.active_object
        platform.name = f"FireEscape_{side}_{i}"
        platform.scale = (0.5, 2, 0.1)
        mat_fe = bpy.data.materials.new(f"FireEscape_{side}_{i}_mat")
        mat_fe.use_nodes = True
        bsdf = mat_fe.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
        platform.data.materials.append(mat_fe)
        
        # Railing
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x - side * 0.7, y_pos, 8.5))
        rail = bpy.context.active_object
        rail.name = f"FireEscapeRail_{side}_{i}"
        rail.scale = (0.05, 2, 0.5)
        mat_rail = bpy.data.materials.new(f"FireEscapeRail_{side}_{i}_mat")
        mat_rail.use_nodes = True
        bsdf = mat_rail.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
        rail.data.materials.append(mat_rail)

# Add rooftop structures (water towers, AC units)
for i in range(6):
    y_pos = -55 + i * 20
    for side in [-1, 1]:
        x = side * (14 + random.uniform(0, 3))
        # Water tower
        if random.random() > 0.5:
            bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3, location=(x, y_pos, 25))
            tower = bpy.context.active_object
            tower.name = f"WaterTower_{side}_{i}"
            mat_tower = bpy.data.materials.new(f"WaterTower_{side}_{i}_mat")
            mat_tower.use_nodes = True
            bsdf = mat_tower.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.1, 1.0)
            tower.data.materials.append(mat_tower)
            
            # Tower top
            bpy.ops.mesh.primitive_cone_add(radius1=1.5, radius2=0, depth=1, location=(x, y_pos, 27))
            top = bpy.context.active_object
            top.name = f"WaterTowerTop_{side}_{i}"
            mat_top = bpy.data.materials.new(f"WaterTowerTop_{side}_{i}_mat")
            mat_top.use_nodes = True
            bsdf = mat_top.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs['Base Color'].default_value = (0.3, 0.15, 0.08, 1.0)
            top.data.materials.append(mat_top)
        else:
            # AC unit
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y_pos, 22))
            ac = bpy.context.active_object
            ac.name = f"ACUnit_{side}_{i}"
            ac.scale = (1, 1, 1)
            mat_ac = bpy.data.materials.new(f"ACUnit_{side}_{i}_mat")
            mat_ac.use_nodes = True
            bsdf = mat_ac.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.6, 1.0)
            ac.data.materials.append(mat_ac)

# Add more street details: manhole covers
for i in range(5):
    x = random.uniform(-4, 4)
    y = random.uniform(-40, 40)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.05, location=(x, y, 0.02))
    mh = bpy.context.active_object
    mh.name = f"Manhole_{i}"
    mat_mh = bpy.data.materials.new(f"Manhole_{i}_mat")
    mat_mh.use_nodes = True
    bsdf = mat_mh.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1.0)
    mh.data.materials.append(mat_mh)

# Add a few more cars parked on the side
for i in range(4):
    side = random.choice([-1, 1])
    x = side * 5.5
    y = -30 + i * 20
    z = 0.5
    car_colors = [
        (0.5, 0.0, 0.0, 1.0), (0.0, 0.0, 0.5, 1.0),
        (0.8, 0.8, 0.0, 1.0), (0.2, 0.2, 0.2, 1.0),
    ]
    color = random.choice(car_colors)
    
    # Car body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    car = bpy.context.active_object
    car.name = f"ParkedCar_{i}"
    car.scale = (1.8, 4, 1.2)
    mat_car = bpy.data.materials.new(f"ParkedCar_{i}_mat")
    mat_car.use_nodes = True
    bsdf = mat_car.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.3
    car.data.materials.append(mat_car)
    
    # Car cabin
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 0.5, z + 0.8))
    cabin = bpy.context.active_object
    cabin.name = f"ParkedCar_{i}_Cabin"
    cabin.scale = (1.5, 2.5, 0.8)
    mat_cabin = bpy.data.materials.new(f"ParkedCar_{i}_Cabin_mat")
    mat_cabin.use_nodes = True
    bsdf = mat_cabin.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.15, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.2
    cabin.data.materials.append(mat_cabin)
    
    # Wheels
    for wx in [-1.2, 1.2]:
        for wy in [-1.5, 1.5]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.3, location=(x + wx, y + wy, 0.4), rotation=(0, math.radians(90), 0))
            wheel = bpy.context.active_object
            wheel.name = f"ParkedCar_{i}_Wheel_{wx}_{wy}"
            mat_wheel = bpy.data.materials.new(f"ParkedCar_{i}_Wheel_{wx}_{wy}_mat")
            mat_wheel.use_nodes = True
            bsdf = mat_wheel.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
            wheel.data.materials.append(mat_wheel)

# Add a billboard on one of the buildings
bpy.ops.mesh.primitive_cube_add(size=1, location=(-12, -20, 15))
billboard = bpy.context.active_object
billboard.name = "Billboard"
billboard.scale = (0.1, 4, 2.5)
mat_bb = bpy.data.materials.new("Billboard_mat")
mat_bb.use_nodes = True
bsdf = mat_bb.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
bsdf.inputs['Emission Color'].default_value = (0.5, 0.3, 0.8, 1.0)
bsdf.inputs['Emission Strength'].default_value = 2.0
billboard.data.materials.append(mat_bb)

# Add a neon sign
bpy.ops.mesh.primitive_cube_add(size=1, location=(12, -10, 10))
neon = bpy.context.active_object
neon.name = "NeonSign"
neon.scale = (0.1, 2, 1)
mat_neon = bpy.data.materials.new("NeonSign_mat")
mat_neon.use_nodes = True
bsdf = mat_neon.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (1.0, 0.2, 0.5, 1.0)
bsdf.inputs['Emission Color'].default_value = (1.0, 0.2, 0.5, 1.0)
bsdf.inputs['Emission Strength'].default_value = 5.0
neon.data.materials.append(mat_neon)

# Add point light for neon sign
light_data = bpy.data.lights.new("NeonLight", type='POINT')
light_data.energy = 30
light_data.color = (1.0, 0.2, 0.5)
light_data.shadow_soft_size = 0.5
light_obj = bpy.data.objects.new("NeonLight", light_data)
light_obj.location = (12, -10, 10)
bpy.context.collection.objects.link(light_obj)

# Add some debris/rubble on the street (from Stay Puft's footprints)
for i in range(15):
    x = random.uniform(-3, 3)
    y = random.uniform(-20, 20)
    size = random.uniform(0.1, 0.3)
    bpy.ops.mesh.primitive_cube_add(size=size, location=(x, y, size/2))
    debris = bpy.context.active_object
    debris.name = f"Debris_{i}"
    debris.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))
    mat_debris = bpy.data.materials.new(f"Debris_{i}_mat")
    mat_debris.use_nodes = True
    bsdf = mat_debris.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.3, 0.25, 0.2, 1.0)
    debris.data.materials.append(mat_debris)

# Add a few more street lamps for better coverage
for i in range(5):
    y = -20 + i * 10
    for side in [-1, 1]:
        x = side * 9
        # Pole
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=5, location=(x, y, 2.5))
        pole = bpy.context.active_object
        pole.name = f"Lamp2_Pole_{side}_{i}"
        mat_pole = bpy.data.materials.new(f"Lamp2_Pole_{side}_{i}_mat")
        mat_pole.use_nodes = True
        bsdf = mat_pole.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
        pole.data.materials.append(mat_pole)
        
        # Lamp head
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x, y, 5.2))
        lamp = bpy.context.active_object
        lamp.name = f"Lamp2_Head_{side}_{i}"
        mat_lamp = bpy.data.materials.new(f"Lamp2_Head_{side}_{i}_mat")
        mat_lamp.use_nodes = True
        bsdf = mat_lamp.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (1.0, 0.9, 0.6, 1.0)
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.85, 0.5, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 5.0
        lamp.data.materials.append(mat_lamp)
        
        # Point light
        light_data = bpy.data.lights.new(f"Lamp2_Light_{side}_{i}", type='POINT')
        light_data.energy = 50
        light_data.color = (1.0, 0.85, 0.5)
        light_data.shadow_soft_size = 0.5
        light_obj = bpy.data.objects.new(f"Lamp2_Light_{side}_{i}", light_data)
        light_obj.location = (x, y, 5.0)
        bpy.context.collection.objects.link(light_obj)

# Adjust camera for better view
camera = bpy.data.objects.get("MainCamera")
if camera:
    camera.location = (0, -25, 4)
    camera.rotation_euler = (math.radians(88), 0, 0)

# Add a subtle ambient light
ambient_data = bpy.data.lights.new("AmbientLight", type='POINT')
ambient_data.energy = 10
ambient_data.color = (0.5, 0.5, 0.7)
ambient_data.shadow_soft_size = 10
ambient_obj = bpy.data.objects.new("AmbientLight", ambient_data)
ambient_obj.location = (0, 0, 20)
bpy.context.collection.objects.link(ambient_obj)

# Add some fog effect using volume
# Create a cube to hold the fog
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 5))
fog_box = bpy.context.active_object
fog_box.name = "FogVolume"
fog_box.scale = (30, 80, 15)
mat_fog = bpy.data.materials.new("FogVolume_mat")
mat_fog.use_nodes = True
nodes = mat_fog.node_tree.nodes
links = mat_fog.node_tree.links
nodes.clear()
vol_principled = nodes.new('ShaderNodeVolumePrincipled')
vol_principled.inputs['Color'].default_value = (0.3, 0.3, 0.4, 1.0)
vol_principled.inputs['Density'].default_value = 0.02
vol_principled.inputs['Anisotropy'].default_value = 0.5
vol_out = nodes.new('ShaderNodeOutputMaterial')
links.new(vol_principled.outputs['Volume'], vol_out.inputs['Volume'])
fog_box.data.materials.append(mat_fog)
fog_box.display_type = 'WIRE'

print("Additional details added successfully!")
