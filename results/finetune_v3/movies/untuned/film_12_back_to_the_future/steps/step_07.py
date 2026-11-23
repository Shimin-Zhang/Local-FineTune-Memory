import bpy, math
from mathutils import Vector

# Camera is too far and looking wrong direction. Reposition to a proper cinematic angle
cam = bpy.data.objects.get("Camera")
if cam:
    # Place camera at a distance looking at the tower and DeLorean
    cam.location = (35, -35, 12)
    # Look towards the tower (at origin) and DeLorean
    target = Vector((5, 5, 10))
    direction = target - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = 35
    cam.data.sensor_width = 36

# Boost ambient lights significantly so the scene is visible
amb = bpy.data.objects.get("AmbientFill")
if amb:
    amb.data.energy = 5000
    amb.data.size = 100

amb2 = bpy.data.objects.get("AmbientFill2")
if amb2:
    amb2.data.energy = 3000

# Boost floodlights
for obj in bpy.data.objects:
    if obj.name.startswith("FloodLight"):
        obj.data.energy = 1000

# Boost lightning lights
for lname in ["LightningLight", "LightningLight2", "CloudLight"]:
    l = bpy.data.objects.get(lname)
    if l:
        l.data.energy = 8000

# Boost fire light
fl = bpy.data.objects.get("FireLight")
if fl:
    fl.data.energy = 1500

# Boost headlight
hl = bpy.data.objects.get("Headlight")
if hl:
    hl.data.energy = 500

# Make the world background slightly brighter so it's not pure black
world = bpy.context.scene.world
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.05, 0.05, 0.1, 1)
        bg.inputs[1].default_value = 1.0

# Add a strong key light from the lightning direction to illuminate the tower
bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
key = bpy.context.object; key.name = "LightningKey"
key.data.energy = 10
key.data.color = (0.5, 0.6, 1.0)
key.rotation_euler = (math.radians(30), 0, math.radians(45))

# Add a warm key light from the fire direction
bpy.ops.object.light_add(type='SUN', location=(20, 20, 5))
warm_key = bpy.context.object; warm_key.name = "FireKey"
warm_key.data.energy = 5
warm_key.data.color = (1.0, 0.5, 0.2)
warm_key.rotation_euler = (math.radians(60), 0, math.radians(-135))
