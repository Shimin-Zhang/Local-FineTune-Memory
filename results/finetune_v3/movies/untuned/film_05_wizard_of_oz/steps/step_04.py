import bpy, math, random

# Add lights
sd = bpy.data.lights.new("Sun",'SUN'); sd.energy=3; sd.color=(1,.95,.8)
so = bpy.data.objects.new("Sun",sd); bpy.context.collection.objects.link(so)
so.rotation_euler = (math.radians(45),math.radians(20),0)

fd = bpy.data.lights.new("Fill",'AREA'); fd.energy=100; fd.color=(.8,.9,1)
fo = bpy.data.objects.new("Fill",fd); bpy.context.collection.objects.link(fo)
fo.location = (-20,-20,15); fo.rotation_euler = (math.radians(45),0,0)

rd = bpy.data.lights.new("Rim",'AREA'); rd.energy=50; rd.color=(1,1,.9)
ro = bpy.data.objects.new("Rim",rd); bpy.context.collection.objects.link(ro)
ro.location = (0,-25,10); ro.rotation_euler = (math.radians(60),0,0)

# Camera
cd = bpy.data.cameras.new("Cam"); cd.lens=50
co = bpy.data.objects.new("Cam",cd); bpy.context.collection.objects.link(co)
co.location = (0,-22,3); co.rotation_euler = (math.radians(82),0,0)
bpy.context.scene.camera = co

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
