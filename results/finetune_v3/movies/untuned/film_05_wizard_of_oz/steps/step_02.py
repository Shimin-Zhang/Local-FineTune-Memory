import bpy, math, random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
for l in list(bpy.data.lights): bpy.data.lights.remove(l)
for c in list(bpy.data.cameras): bpy.data.cameras.remove(c)

# Materials
def mat(name, col, rough=0.5, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit > 0: b.inputs['Emission Strength'].default_value = emit
    return m

m_brick = mat("Brick",(1,.85,.1,1),.4)
m_brick2 = mat("Brick2",(.85,.7,.05,1),.5)
m_grass = mat("Grass",(.2,.6,.1,1),.8)
m_dress = mat("Dress",(.1,.3,.8,1),.6)
m_bow = mat("Bow",(.8,0,0,1),.5)
m_hair = mat("Hair",(.6,.3,.1,1),.7)
m_shoe = mat("Shoe",(1,0,0,1),.2,.3)
m_scr_body = mat("ScrBody",(.9,.8,.5,1),.9)
m_scr_hat = mat("ScrHat",(.6,.4,.2,1),.8)
m_tin = mat("Tin",(.7,.7,.75,1),.2,.9)
m_tin_hat = mat("TinHat",(.6,.6,.65,1),.2,.9)
m_lion = mat("Lion",(.8,.5,.1,1),.7)
m_manee = mat("Mane",(.6,.35,.05,1),.8)
m_nose = mat("Nose",(.3,.2,.1,1),.5)
m_poppy = mat("Poppy",(1,0,0,1),.4)
m_stem = mat("Stem",(.2,.5,.1,1),.7)
m_leaf = mat("Leaf",(.1,.4,.05,1),.7)
m_road_edge = mat("RoadEdge",(.7,.6,.2,1),.6)
m_city = mat("City",(0,.9,.4,1),.3,.3)
m_win = mat("Win",(.5,.9,1,1),.1,.0,.3)
m_cloud = mat("Cloud",(1,1,1,1),.9,0,.2)
m_trunk = mat("Trunk",(.4,.25,.1,1),.8)
m_tree = mat("Tree",(.1,.5,.1,1),.7)
m_fence = mat("Fence",(.5,.3,.15,1),.8)
m_rock = mat("Rock",(.5,.5,.5,1),.9)

# World
w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = w
w.use_nodes = True
for n in list(w.node_tree.nodes): w.node_tree.nodes.remove(n)
bg = w.node_tree.nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (.45,.7,1,1)
bg.inputs['Strength'].default_value = 1.0
out = w.node_tree.nodes.new('ShaderNodeOutputWorld')
w.node_tree.links.new(bg.outputs[0], out.inputs[0])

# Ground
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,0))
g = bpy.context.active_object; g.name="Ground"; g.data.materials.append(m_grass)

# Yellow Brick Road
for i in range(67):
    y = -50 + i*1.5 + .75
    offs = [-1.5,-.5,.5,1.5] if i%2==0 else [-1,0,1]
    for j,ox in enumerate(offs):
        if abs(ox)>2: continue
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox,y,.05))
        b = bpy.context.active_object
        b.scale = (.5,.75,.05)
        b.data.materials.append(m_brick if (i+j)%3 else m_brick2)

# Road edges
for sx in [-2.2,2.2]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx,0,.05))
    e = bpy.context.active_object; e.scale = (.3,50,.05); e.data.materials.append(m_road_edge)

# Poppy field
random.seed(42)
for i in range(200):
    s = random.choice([-1,1])
    x = s*random.uniform(2.5,15); y = random.uniform(-40,40)
    h = random.uniform(.5,1.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=.03, depth=h, location=(x,y,h/2))
    bpy.context.active_object.data.materials.append(m_stem)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.12, location=(x,y,h+.08))
    hd = bpy.context.active_object; hd.scale=(1,1,.6); hd.data.materials.append(m_poppy)
    for _ in range(2):
        a = random.uniform(0,6.28)
        bpy.ops.mesh.primitive_plane_add(size=.3, location=(x+.15*math.cos(a), y+.15*math.sin(a), h*random.uniform(.3,.7)))
        lf = bpy.context.active_object
        lf.rotation_euler = (random.uniform(-.5,.5),random.uniform(-.5,.5),random.uniform(0,6.28))
        lf.scale = (1,.6,1); lf.data.materials.append(m_leaf)

# Emerald City
cy = 55
bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=12, location=(0,cy,6))
bpy.context.active_object.data.materials.append(m_city)
bpy.ops.mesh.primitive_cone_add(radius1=3.2, radius2=0, depth=4, location=(0,cy,14))
bpy.context.active_object.data.materials.append(m_city)
for a in range(0,360,45):
    r = math.radians(a)
    bpy.ops.mesh.primitive_cube_add(size=.8, location=(3.1*math.cos(r), cy+3.1*math.sin(r), 8))
    bpy.context.active_object.data.materials.append(m_win)
for bx in [-8,8,-15,15,-5,5]:
    bh = random.uniform(4,8); bw = random.uniform(2,4)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, cy+random.uniform(-3,3), bh/2))
    bl = bpy.context.active_object; bl.scale = (bw/2,bw/2,bh/2); bl.data.materials.append(m_city)
# Gate
bpy.ops.mesh.primitive_torus_add(major_radius=4, minor_radius=.5, location=(0,cy-10,4))
bpy.context.active_object.data.materials.append(m_city)
for gx in [-4,4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=.8, depth=8, location=(gx,cy-10,4))
    bpy.context.active_object.data.materials.append(m_city)

# Clouds
for i in range(12):
    cx = random.uniform(-60,60); cyy = random.uniform(-40,60); cz = random.uniform(25,45)
    for j in range(3):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(2,4), location=(cx+random.uniform(-3,3), cyy+random.uniform(-2,2), cz+random.uniform(-1,1)))
        cp = bpy.context.active_object; cp.scale=(1,.6,.5); cp.data.materials.append(m_cloud)

# Trees
for i in range(15):
    s = random.choice([-1,1]); tx = s*random.uniform(18,35); ty = random.uniform(-45,45)
    th = random.uniform(3,6)
    bpy.ops.mesh.primitive_cylinder_add(radius=.3, depth=th, location=(tx,ty,th/2))
    bpy.context.active_object.data.materials.append(m_trunk)
    for k in range(3):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(1.5,2.5), location=(tx+random.uniform(-1,1), ty+random.uniform(-1,1), th+random.uniform(0,2)))
        bpy.context.active_object.data.materials.append(m_tree)

# Hills
for i in range(6):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(10,20), location=(random.uniform(-80,80), random.uniform(60,90), -5))
    h = bpy.context.active_object; h.scale=(1,1,.4); h.data.materials.append(m_grass)

# Rocks
for i in range(20):
    s = random.choice([-1,1])
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(.2,.6), location=(s*random.uniform(3,20), random.uniform(-40,40), .2))
    r = bpy.context.active_object; r.scale = (random.uniform(.8,1.2),random.uniform(.8,1.2),random.uniform(.5,.8)); r.data.materials.append(m_rock)

# Fence posts
for i in range(10):
    fy = -40 + i*8
    for fx in [-3.2, 3.2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.05, depth=1, location=(fx,fy,.5))
        bpy.context.active_object.data.materials.append(m_fence)

# ============ CHARACTERS ============
# Dorothy at (-1.2, -15)
def dorothy(x,y,z,s=1.2):
    for lx in [-.15,.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.08*s, depth=.5*s, location=(x+lx*s,y,z+.25*s))
        bpy.context.active_object.data.materials.append(m_dress)
        bpy.ops.mesh.primitive_cube_add(size=.15*s, location=(x+lx*s,y+.05*s,z+.03*s))
        sh = bpy.context.active_object; sh.scale=(1,1.3,.5); sh.data.materials.append(m_shoe)
    bpy.ops.mesh.primitive_cone_add(radius1=.35*s, radius2=.2*s, depth=.6*s, location=(x,y,z+.8*s))
    bpy.context.active_object.data.materials.append(m_dress)
    bpy.ops.mesh.primitive_cylinder_add(radius=.18*s, depth=.3*s, location=(x,y,z+1.25*s))
    bpy.context.active_object.data.materials.append(m_dress)
    for ax in [-.25,.25]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.05*s, depth=.4*s, location=(x+ax*s,y,z+1.1*s))
        a = bpy.context.active_object; a.rotation_euler=(0,math.radians(20 if ax>0 else -20),0); a.data.materials.append(m_dress)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.18*s, location=(x,y,z+1.55*s))
    bpy.context.active_object.data.materials.append(m_hair)
    for px in [-.2,.2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.06*s, depth=.3*s, location=(x+px*s,y-.1*s,z+1.5*s))
        p = bpy.context.active_object; p.rotation_euler=(math.radians(-15),0,0); p.data.materials.append(m_hair)
    bpy.ops.mesh.primitive_cube_add(size=.1*s, location=(x,y-.15*s,z+1.7*s))
    bw = bpy.context.active_object; bw.scale=(1.5,.5,.8); bw.data.materials.append(m_bow)
dorothy(-1.2,-15,.1)

# Scarecrow at (0.5, -12)
def scarecrow(x,y,z,s=1.3):
    bpy.ops.mesh.primitive_cylinder_add(radius=.05*s, depth=1.8*s, location=(x,y,z+.9*s))
    bpy.context.active_object.data.materials.append(m_scr_hat)
    bpy.ops.mesh.primitive_cylinder_add(radius=.04*s, depth=.8*s, location=(x,y,z+1.3*s))
    ap = bpy.context.active_object; ap.rotation_euler=(0,math.radians(90),0); ap.data.materials.append(m_scr_hat)
    bpy.ops.mesh.primitive_cube_add(size=.5*s, location=(x,y,z+.8*s))
    bd = bpy.context.active_object; bd.scale=(1,.7,1.2); bd.data.materials.append(m_scr_body)
    for ax in [-.4,.4]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.08*s, depth=.4*s, location=(x+ax*s,y,z+1.2*s))
        a = bpy.context.active_object; a.rotation_euler=(0,math.radians(30 if ax>0 else -30),0); a.data.materials.append(m_scr_body)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.22*s, location=(x,y,z+1.55*s))
    bpy.context.active_object.data.materials.append(m_scr_body)
    bpy.ops.mesh.primitive_cylinder_add(radius=.35*s, depth=.05*s, location=(x,y,z+1.7*s))
    bpy.context.active_object.data.materials.append(m_scr_hat)
    bpy.ops.mesh.primitive_cone_add(radius1=.2*s, radius2=.15*s, depth=.3*s, location=(x,y,z+1.85*s))
    bpy.context.active_object.data.materials.append(m_scr_hat)
    for ex in [-.08,.08]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.03*s, location=(x+ex*s,y+.18*s,z+1.58*s))
        bpy.context.active_object.data.materials.append(m_scr_hat)
scarecrow(.5,-12,.1)

# Tin Man at (1.8, -10)
def tinman(x,y,z,s=1.2):
    for lx in [-.15,.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.1*s, depth=.6*s, location=(x+lx*s,y,z+.3*s))
        bpy.context.active_object.data.materials.append(m_tin)
        bpy.ops.mesh.primitive_cube_add(size=.2*s, location=(x+lx*s,y+.05*s,z+.05*s))
        f = bpy.context.active_object; f.scale=(1,1.5,.4); f.data.materials.append(m_tin)
    bpy.ops.mesh.primitive_cylinder_add(radius=.25*s, depth=.6*s, location=(x,y,z+.9*s))
    bpy.context.active_object.data.materials.append(m_tin)
    bpy.ops.mesh.primitive_cylinder_add(radius=.05*s, depth=.02*s, location=(x,y+.24*s,z+1*s))
    kh = bpy.context.active_object; kh.rotation_euler=(math.radians(90),0,0); kh.data.materials.append(m_tin_hat)
    for ax in [-.3,.3]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.07*s, depth=.5*s, location=(x+ax*s,y,z+.85*s))
        a = bpy.context.active_object; a.rotation_euler=(0,math.radians(15 if ax>0 else -15),0); a.data.materials.append(m_tin)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.2*s, location=(x,y,z+1.4*s))
    hd = bpy.context.active_object; hd.scale=(1,1,1.1); hd.data.materials.append(m_tin)
    bpy.ops.mesh.primitive_cone_add(radius1=.25*s, radius2=.05*s, depth=.35*s, location=(x,y,z+1.65*s))
    bpy.context.active_object.data.materials.append(m_tin_hat)
    for ex in [-.08,.08]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.04*s, location=(x+ex*s,y+.18*s,z+1.42*s))
        bpy.context.active_object.data.materials.append(m_tin_hat)
    bpy.ops.mesh.primitive_cylinder_add(radius=.08*s, depth=.15*s, location=(x+.4*s,y+.1*s,z+.6*s))
    bpy.context.active_object.data.materials.append(m_tin)
tinman(1.8,-10,.1)

# Lion at (-0.5, -7)
def lion(x,y,z,s=1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.4*s, location=(x,y,z+.4*s))
    bd = bpy.context.active_object; bd.scale=(1,1.3,.8); bd.data.materials.append(m_lion)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.25*s, location=(x,y+.5*s,z+.65*s))
    bpy.context.active_object.data.materials.append(m_lion)
    for a in range(0,360,30):
        r = math.radians(a)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.12*s, location=(x+.25*s*math.cos(r), y+.5*s+.25*s*math.sin(r), z+.65*s+.1*s*math.sin(a)))
        bpy.context.active_object.data.materials.append(m_manee)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.06*s, location=(x,y+.75*s,z+.6*s))
    bpy.context.active_object.data.materials.append(m_nose)
    for ex in [-.1,.1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.04*s, location=(x+ex*s,y+.7*s,z+.7*s))
        bpy.context.active_object.data.materials.append(m_nose)
    for lx in [-.25,.25]:
        for ly in [-.3,.3]:
            bpy.ops.mesh.primitive_cylinder_add(radius=.08*s, depth=.4*s, location=(x+lx*s,y+ly*s,z+.2*s))
            bpy.context.active_object.data.materials.append(m_lion)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=.1*s, location=(x+lx*s,y+ly*s+.05*s,z+.05*s))
            pw = bpy.context.active_object; pw.scale=(1,1.2,.5); pw.data.materials.append(m_lion)
    bpy.ops.mesh.primitive_cylinder_add(radius=.04*s, depth=.5*s, location=(x,y-.5*s,z+.4*s))
    t = bpy.context.active_object; t.rotation_euler=(math.radians(-30),0,0); t.data.materials.append(m_lion)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.08*s, location=(x,y-.7*s,z+.25*s))
    bpy.context.active_object.data.materials.append(m_manee)
lion(-.5,-7,.1)

# Lighting
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
co.location = (0,-25,3); co.rotation_euler = (math.radians(80),0,0)
bpy.context.scene.camera = co

# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
