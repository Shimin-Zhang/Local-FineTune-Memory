import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.object.select_all(action='DESELECT')

# Remove default objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

# --- MATERIALS ---
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

# Materials
water_mat = create_material("Water", (0.05, 0.15, 0.35), roughness=0.1, metallic=0.1)
wood_mat = create_material("Wood", (0.35, 0.2, 0.1), roughness=0.8)
metal_mat = create_material("Metal", (0.4, 0.4, 0.45), roughness=0.3, metallic=0.8)
plane_body_mat = create_material("PlaneBody", (0.8, 0.8, 0.85), roughness=0.2, metallic=0.3)
plane_wing_mat = create_material("PlaneWing", (0.9, 0.9, 0.95), roughness=0.2, metallic=0.2)
mountain_mat = create_material("Mountain", (0.15, 0.2, 0.35), roughness=0.9)
snow_mat = create_material("Snow", (0.9, 0.95, 1.0), roughness=0.6)
ramp_mat = create_material("Ramp", (0.5, 0.5, 0.5), roughness=0.5, metallic=0.3)
gas_pump_mat = create_material("GasPump", (0.7, 0.7, 0.7), roughness=0.3, metallic=0.5)
gas_pump_red = create_material("GasPumpRed", (0.8, 0.1, 0.1), roughness=0.3, metallic=0.3)
concrete_mat = create_material("Concrete", (0.6, 0.6, 0.6), roughness=0.8)
green_mat = create_material("Green", (0.1, 0.4, 0.1), roughness=0.7)

# --- WATER ---
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
water = bpy.context.active_object
water.name = "Water"
water.data.materials.append(water_mat)

# --- FLOATING DOCK ---
def create_dock():
    # Main dock platform
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, 0.3))
    dock_platform = bpy.context.active_object
    dock_platform.name = "DockPlatform"
    dock_platform.scale = (8, 12, 0.3)
    dock_platform.data.materials.append(wood_mat)

    # Dock pilings
    for x in [-3, 0, 3]:
        for y in [8, 15, 22]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=2, location=(x, y, -0.5))
            piling = bpy.context.active_object
            piling.name = f"Piling_{x}_{y}"
            piling.data.materials.append(wood_mat)

    # Dock edge railings
    for x in [-3.5, 3.5]:
        for y in range(8, 23, 2):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1, location=(x, y, 0.8))
            rail = bpy.context.active_object
            rail.name = f"Rail_{x}_{y}"
            rail.data.materials.append(metal_mat)

    # Horizontal rails
    for x in [-3.5, 3.5]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=15, location=(x, 15, 1.2), rotation=(math.pi/2, 0, 0))
        h_rail = bpy.context.active_object
        h_rail.name = f"HRail_{x}"
        h_rail.data.materials.append(metal_mat)

create_dock()

# --- BOATHOUSE ---
def create_boathouse():
    # Base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-15, 15, 1))
    base = bpy.context.active_object
    base.name = "BoathouseBase"
    base.scale = (6, 8, 1)
    base.data.materials.append(wood_mat)

    # Walls
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-15, 15, 2.5))
    walls = bpy.context.active_object
    walls.name = "BoathouseWalls"
    walls.scale = (5.5, 7.5, 1.5)
    walls.data.materials.append(wood_mat)

    # Roof
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=6, radius2=0, depth=3, location=(-15, 15, 4.5))
    roof = bpy.context.active_object
    roof.name = "BoathouseRoof"
    roof.scale = (1.1, 1.4, 1)
    roof.rotation_euler = (0, 0, math.pi/4)
    roof.data.materials.append(create_material("RoofWood", (0.25, 0.15, 0.08), roughness=0.7))

    # Door opening (dark inset)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-15, 11.5, 1.5))
    door = bpy.context.active_object
    door.name = "BoathouseDoor"
    door.scale = (1.5, 0.1, 1.2)
    door.data.materials.append(create_material("DarkWood", (0.1, 0.05, 0.02), roughness=0.9))

    # Windows
    for x in [-18, -12]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 11.5, 2.5))
        window = bpy.context.active_object
        window.name = f"BoathouseWindow_{x}"
        window.scale = (0.8, 0.1, 0.8)
        window.data.materials.append(create_material("Window", (0.3, 0.5, 0.7), roughness=0.1, metallic=0.5))

create_boathouse()

# --- PLANE ON CRADLE ---
def create_plane_cradle():
    # Cradle base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 15, 0.5))
    cradle_base = bpy.context.active_object
    cradle_base.name = "CradleBase"
    cradle_base.scale = (4, 6, 0.5)
    cradle_base.data.materials.append(metal_mat)

    # Cradle arms
    for x in [13, 17]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 15, 1.5))
        arm = bpy.context.active_object
        arm.name = f"CradleArm_{x}"
        arm.scale = (0.3, 5, 1)
        arm.data.materials.append(metal_mat)

    # Cradle cross beams
    for y in [12, 15, 18]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(15, y, 2))
        beam = bpy.context.active_object
        beam.name = f"CradleBeam_{y}"
        beam.scale = (4, 0.3, 0.3)
        beam.data.materials.append(metal_mat)

    # --- PLANE ---
    # Fuselage
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=6, location=(15, 15, 3), rotation=(0, math.pi/2, 0))
    fuselage = bpy.context.active_object
    fuselage.name = "PlaneFuselage"
    fuselage.scale = (1, 1, 1.2)
    fuselage.data.materials.append(plane_body_mat)

    # Nose
    bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0, depth=1.5, location=(12, 15, 3), rotation=(0, -math.pi/2, 0))
    nose = bpy.context.active_object
    nose.name = "PlaneNose"
    nose.scale = (1, 1, 1.2)
    nose.data.materials.append(plane_body_mat)

    # Tail
    bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0.2, depth=2, location=(18.5, 15, 3), rotation=(0, math.pi/2, 0))
    tail = bpy.context.active_object
    tail.name = "PlaneTail"
    tail.scale = (1, 1, 1.2)
    tail.data.materials.append(plane_body_mat)

    # Vertical stabilizer
    bpy.ops.mesh.primitive_cube_add(size=1, location=(19, 15, 4.5))
    vstab = bpy.context.active_object
    vstab.name = "PlaneVStab"
    vstab.scale = (1.5, 0.15, 1.5)
    vstab.rotation_euler = (0, -0.3, 0)
    vstab.data.materials.append(plane_body_mat)

    # Wings
    for z in [3.5]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 15, z))
        wing = bpy.context.active_object
        wing.name = f"PlaneWing_{z}"
        wing.scale = (3, 1.5, 0.1)
        wing.data.materials.append(plane_wing_mat)

    # Landing gear (floats for seaplane)
    for x in [13, 17]:
        for y in [13.5, 16.5]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=3, location=(x, y, 2), rotation=(0, math.pi/2, 0))
            float_ = bpy.context.active_object
            float_.name = f"PlaneFloat_{x}_{y}"
            float_.scale = (1, 1, 1.5)
            float_.data.materials.append(create_material("Float", (0.6, 0.6, 0.65), roughness=0.4, metallic=0.2))

    # Propeller
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.5, location=(11.2, 15, 3), rotation=(0, math.pi/2, 0))
    prop_hub = bpy.context.active_object
    prop_hub.name = "PropHub"
    prop_hub.data.materials.append(metal_mat)

    for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(11, 15, 3))
        blade = bpy.context.active_object
        blade.name = f"PropBlade_{angle}"
        blade.scale = (0.3, 0.05, 1.5)
        blade.rotation_euler = (angle, 0, 0)
        blade.location = (11, 15 + 0.75*math.cos(angle), 3 + 0.75*math.sin(angle))
        blade.data.materials.append(metal_mat)

create_plane_cradle()

# --- RAMP ---
def create_ramp():
    # Main ramp
    bpy.ops.mesh.primitive_cube_add(size=1, location=(5, 25, 1))
    ramp = bpy.context.active_object
    ramp.name = "Ramp"
    ramp.scale = (4, 10, 0.3)
    ramp.rotation_euler = (0.3, 0, 0)
    ramp.data.materials.append(ramp_mat)

    # Ramp supports
    for x in [3, 7]:
        for y in [20, 25, 30]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=3, location=(x, y, -0.5))
            support = bpy.context.active_object
            support.name = f"RampSupport_{x}_{y}"
            support.data.materials.append(metal_mat)

    # Ramp edge rails
    for x in [3, 7]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=10, location=(x, 25, 2), rotation=(0.3, 0, 0))
        rail = bpy.context.active_object
        rail.name = f"RampRail_{x}"
        rail.data.materials.append(metal_mat)

create_ramp()

# --- GAS PUMP ---
def create_gas_pump():
    # Base
    bpy.ops.mesh.primitive_cube_add(size=1, location=(8, 10, 0.5))
    pump_base = bpy.context.active_object
    pump_base.name = "GasPumpBase"
    pump_base.scale = (1.5, 1.5, 0.5)
    pump_base.data.materials.append(gas_pump_mat)

    # Body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(8, 10, 1.5))
    pump_body = bpy.context.active_object
    pump_body.name = "GasPumpBody"
    pump_body.scale = (1, 1, 1)
    pump_body.data.materials.append(gas_pump_red)

    # Display panel
    bpy.ops.mesh.primitive_cube_add(size=1, location=(8, 9.5, 1.8))
    display = bpy.context.active_object
    display.name = "GasPumpDisplay"
    display.scale = (0.6, 0.1, 0.4)
    display.data.materials.append(create_material("Display", (0.1, 0.3, 0.1), roughness=0.2, metallic=0.5))

    # Hose
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2, location=(9, 10, 1.5), rotation=(0, math.pi/4, 0))
    hose = bpy.context.active_object
    hose.name = "GasPumpHose"
    hose.data.materials.append(create_material("Hose", (0.1, 0.1, 0.1), roughness=0.8))

    # Nozzle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.5, location=(10, 10, 0.8), rotation=(0, math.pi/2, 0))
    nozzle = bpy.context.active_object
    nozzle.name = "GasPumpNozzle"
    nozzle.data.materials.append(metal_mat)

    # Canopy
    bpy.ops.mesh.primitive_cube_add(size=1, location=(8, 10, 2.5))
    canopy = bpy.context.active_object
    canopy.name = "GasPumpCanopy"
    canopy.scale = (2, 2, 0.2)
    canopy.data.materials.append(gas_pump_mat)

    # Canopy supports
    for x in [7, 9]:
        for y in [9, 11]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.5, location=(x, y, 1.75))
            support = bpy.context.active_object
            support.name = f"CanopySupport_{x}_{y}"
            support.data.materials.append(metal_mat)

create_gas_pump()

# --- COLD BLUE MOUNTAINS ---
def create_mountains():
    random.seed(42)
    mountain_positions = [
        (-40, -60, 20), (-20, -70, 25), (0, -65, 30),
        (20, -70, 25), (40, -60, 20), (-50, -50, 15),
        (50, -50, 15), (-30, -55, 18), (30, -55, 18),
        (-10, -75, 28), (10, -75, 28)
    ]

    for i, (x, y, height) in enumerate(mountain_positions):
        # Main mountain body
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=height*0.8, radius2=0, depth=height*2, location=(x, y, height))
        mountain = bpy.context.active_object
        mountain.name = f"Mountain_{i}"
        mountain.scale = (1, 1, 1)
        mountain.rotation_euler = (0, 0, random.uniform(0, math.pi*2))
        mountain.data.materials.append(mountain_mat)

        # Snow cap
        if height > 15:
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=height*0.3, radius2=0, depth=height*0.5, location=(x, y, height*1.8))
            snow_cap = bpy.context.active_object
            snow_cap.name = f"SnowCap_{i}"
            snow_cap.rotation_euler = (0, 0, random.uniform(0, math.pi*2))
            snow_cap.data.materials.append(snow_mat)

    # Distant mountain range
    for i in range(15):
        x = random.uniform(-60, 60)
        y = random.uniform(-90, -80)
        height = random.uniform(10, 20)
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=height*0.7, radius2=0, depth=height*1.5, location=(x, y, height*0.75))
        distant_mountain = bpy.context.active_object
        distant_mountain.name = f"DistantMountain_{i}"
        distant_mountain.rotation_euler = (0, 0, random.uniform(0, math.pi*2))
        # Use a bluer, more distant material
        dist_mat = create_material(f"DistantMountain_{i}", (0.1, 0.15, 0.3), roughness=0.9)
        distant_mountain.data.materials.append(dist_mat)

create_mountains()

# --- ADDITIONAL DETAILS ---

# Trees near boathouse
def create_trees():
    tree_positions = [
        (-20, 8), (-22, 12), (-18, 20), (-25, 18),
        (-10, 8), (-8, 12), (-12, 22), (-5, 20)
    ]

    for i, (x, y) in enumerate(tree_positions):
        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=2, location=(x, y, 1))
        trunk = bpy.context.active_object
        trunk.name = f"TreeTrunk_{i}"
        trunk.data.materials.append(create_material("Trunk", (0.2, 0.1, 0.05), roughness=0.9))

        # Foliage
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.5, radius2=0, depth=3, location=(x, y, 3))
        foliage = bpy.context.active_object
        foliage.name = f"TreeFoliage_{i}"
        foliage.data.materials.append(green_mat)

create_trees()

# Buoy markers in water
def create_buoys():
    buoy_positions = [
        (10, 30), (15, 35), (20, 28), (-5, 30), (-10, 35)
    ]

    for i, (x, y) in enumerate(buoy_positions):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x, y, 0.3))
        buoy = bpy.context.active_object
        buoy.name = f"Buoy_{i}"
        buoy.scale = (1, 1, 1.5)
        buoy.data.materials.append(create_material(f"Buoy_{i}", (0.9, 0.2, 0.1), roughness=0.3, metallic=0.2))

create_buoys()

# --- CAMERA AND LIGHTING ---

# Camera
bpy.ops.object.camera_add(location=(0, 40, 15), rotation=(math.pi/3, 0, 0))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Sun light
bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3
sun.data.color = (0.9, 0.95, 1.0)
sun.rotation_euler = (math.pi/4, 0, math.pi/6)

# Ambient fill
bpy.ops.object.light_add(type='AREA', location=(0, 0, 30))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 500
fill.data.size = 50
fill.data.color = (0.5, 0.6, 0.8)

# World background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.1, 0.15, 0.3, 1.0)
    bg_node.inputs[1].default_value = 1.0

# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Seaplane base scene built successfully!")
