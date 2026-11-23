import bpy, math, random
from mathutils import Vector

# Delete all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
for l in list(bpy.data.lights): bpy.data.lights.remove(l)
for c in list(bpy.data.cameras): bpy.data.cameras.remove(c)

# ============ MATERIALS ============
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
m_scr_face = mat("ScrFace",(.9,.7,.5,1),.7)
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
m_win = mat("Win",(.5,.9,1,1),.1,0,.3)
m_cloud = mat("Cloud",(1,1,1,1),.9,0,.2)
m_trunk = mat("Trunk",(.4,.25,.1,1),.8)
m_tree = mat("Tree",(.1,.5,.1,1),.7)
m_fence = mat("Fence",(.5,.3,.15,1),.8)
m_rock = mat("Rock",(.5,.5,.5,1),.9)
m_sky = mat("Sky",(.4,.7,1,1),0,0,.8)
m_tin_dark = mat("TinDark",(.4,.4,.45,1),.3,.9)
m_lion_belly = mat("LionBelly",(.9,.6,.2,1),.7)
m_dorothy_skin = mat("DorothySkin",(.95,.8,.7,1),.6)
m_scarecrow_buckle = mat("Buckle",(.3,.3,.3,1),.3,.8)

# ============ WORLD ============
w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = w
w.use_nodes = True
for n in list(w.node_tree.nodes): w.node_tree.nodes.remove(n)
bg = w.node_tree.nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (.45,.7,1,1)
bg.inputs['Strength'].default_value = 1.0
out = w.node_tree.nodes.new('ShaderNodeOutputWorld')
w.node_tree.links.new(bg.outputs[0], out.inputs[0])

# ============ GROUND ============
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,0))
g = bpy.context.active_object; g.name="Ground"; g.data.materials.append(m_grass)

# ============ YELLOW BRICK ROAD ============
# Continuous road surface
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,.02))
road_base = bpy.context.active_object
road_base.scale = (2.2, 50, .02)
road_base.data.materials.append(m_brick2)

# Individual bricks on top
for i in range(67):
    y = -50 + i*1.5 + .75
    offs = [-1.5,-.5,.5,1.5] if i%2==0 else [-1,0,1]
    for j,ox in enumerate(offs):
        if abs(ox)>2: continue
        bpy.ops.mesh.primitive_cube_add(size=1, location=(ox,y,.06))
        b = bpy.context.active_object
        b.scale = (.48,.73,.04)
        b.data.materials.append(m_brick if (i+j)%3 else m_brick2)

# Road edges (stone curbs)
for sx in [-2.3, 2.3]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(sx,0,.08))
    e = bpy.context.active_object; e.scale = (.3,50,.08); e.data.materials.append(m_rock)

# ============ POPPY FIELD ============
random.seed(42)
for i in range(250):
    s = random.choice([-1,1])
    x = s*random.uniform(2.8,15); y = random.uniform(-45,45)
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

# ============ EMERALD CITY ============
cy = 55
# Main tower
bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=12, location=(0,cy,6))
bpy.context.active_object.data.materials.append(m_city)
bpy.ops.mesh.primitive_cone_add(radius1=3.2, radius2=0, depth=4, location=(0,cy,14))
bpy.context.active_object.data.materials.append(m_city)
# Tower windows
for a in range(0,360,45):
    r = math.radians(a)
    bpy.ops.mesh.primitive_cube_add(size=.8, location=(3.1*math.cos(r), cy+3.1*math.sin(r), 8))
    bpy.context.active_object.data.materials.append(m_win)
# Side buildings
for bx in [-8,8,-15,15,-5,5]:
    bh = random.uniform(4,8); bw = random.uniform(2,4)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, cy+random.uniform(-3,3), bh/2))
    bl = bpy.context.active_object; bl.scale = (bw/2,bw/2,bh/2); bl.data.materials.append(m_city)
    # Windows
    for wy in range(1, int(bh)-1, 2):
        bpy.ops.mesh.primitive_cube_add(size=.5, location=(bx+bw/2+.1, cy, wy))
        bpy.context.active_object.data.materials.append(m_win)
# Gate arch
bpy.ops.mesh.primitive_torus_add(major_radius=4, minor_radius=.5, location=(0,cy-10,4))
bpy.context.active_object.data.materials.append(m_city)
for gx in [-4,4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=.8, depth=8, location=(gx,cy-10,4))
    bpy.context.active_object.data.materials.append(m_city)
# Gate top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,cy-10,8.5))
gt = bpy.context.active_object; gt.scale=(4.5,.5,.5); gt.data.materials.append(m_city)

# ============ CLOUDS ============
for i in range(15):
    cx = random.uniform(-60,60); cyy = random.uniform(-40,60); cz = random.uniform(25,45)
    for j in range(3):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(2,4), location=(cx+random.uniform(-3,3), cyy+random.uniform(-2,2), cz+random.uniform(-1,1)))
        cp = bpy.context.active_object; cp.scale=(1,.6,.5); cp.data.materials.append(m_cloud)

# ============ TREES ============
for i in range(18):
    s = random.choice([-1,1]); tx = s*random.uniform(18,35); ty = random.uniform(-45,45)
    th = random.uniform(3,6)
    bpy.ops.mesh.primitive_cylinder_add(radius=.3, depth=th, location=(tx,ty,th/2))
    bpy.context.active_object.data.materials.append(m_trunk)
    for k in range(4):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(1.5,2.5), location=(tx+random.uniform(-1,1), ty+random.uniform(-1,1), th+random.uniform(0,2)))
        bpy.context.active_object.data.materials.append(m_tree)

# ============ HILLS ============
for i in range(6):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(10,20), location=(random.uniform(-80,80), random.uniform(60,90), -5))
    h = bpy.context.active_object; h.scale=(1,1,.4); h.data.materials.append(m_grass)

# ============ ROCKS ============
for i in range(25):
    s = random.choice([-1,1])
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(.2,.6), location=(s*random.uniform(3,20), random.uniform(-40,40), .2))
    r = bpy.context.active_object; r.scale = (random.uniform(.8,1.2),random.uniform(.8,1.2),random.uniform(.5,.8)); r.data.materials.append(m_rock)

# ============ FENCE ============
for i in range(10):
    fy = -40 + i*8
    for fx in [-3.2, 3.2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.05, depth=1, location=(fx,fy,.5))
        bpy.context.active_object.data.materials.append(m_fence)
    # Horizontal rails
    bpy.ops.mesh.primitive_cylinder_add(radius=.03, depth=6.4, location=(0,fy,.7))
    rail = bpy.context.active_object; rail.rotation_euler=(0,math.radians(90),0); rail.data.materials.append(m_fence)
    bpy.ops.mesh.primitive_cylinder_add(radius=.03, depth=6.4, location=(0,fy,.4))
    rail2 = bpy.context.active_object; rail2.rotation_euler=(0,math.radians(90),0); rail2.data.materials.append(m_fence)

# ============ DOROTHY ============
def build_dorothy(x,y,z,s=1.2):
    # Legs
    for lx in [-.15,.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.08*s, depth=.5*s, location=(x+lx*s,y,z+.25*s))
        bpy.context.active_object.data.materials.append(m_dress)
        # Ruby slippers
        bpy.ops.mesh.primitive_cube_add(size=.15*s, location=(x+lx*s,y+.05*s,z+.03*s))
        sh = bpy.context.active_object; sh.scale=(1,1.3,.5); sh.data.materials.append(m_shoe)
    # Dress (cone)
    bpy.ops.mesh.primitive_cone_add(radius1=.35*s, radius2=.2*s, depth=.6*s, location=(x,y,z+.8*s))
    bpy.context.active_object.data.materials.append(m_dress)
    # Torso
    bpy.ops.mesh.primitive_cylinder_add(radius=.18*s, depth=.3*s, location=(x,y,z+1.25*s))
    bpy.context.active_object.data.materials.append(m_dress)
    # Arms
    for ax in [-.25,.25]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.05*s, depth=.4*s, location=(x+ax*s,y,z+1.1*s))
        a = bpy.context.active_object; a.rotation_euler=(0,math.radians(20 if ax>0 else -20),0); a.data.materials.append(m_dress)
        # Hands
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.04*s, location=(x+ax*s+ax*.1*s,y,z+.9*s))
        bpy.context.active_object.data.materials.append(m_dorothy_skin)
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.18*s, location=(x,y,z+1.55*s))
    bpy.context.active_object.data.materials.append(m_hair)
    # Face (slightly lighter)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.16*s, location=(x,y+.02*s,z+1.55*s))
    f = bpy.context.active_object; f.scale=(.9,.7,.9); f.data.materials.append(m_dorothy_skin)
    # Pigtails
    for px in [-.2,.2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.06*s, depth=.3*s, location=(x+px*s,y-.1*s,z+1.5*s))
        p = bpy.context.active_object; p.rotation_euler=(math.radians(-15),0,0); p.data.materials.append(m_hair)
        # Pigtail tips
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.05*s, location=(x+px*s,y-.25*s,z+1.35*s))
        bpy.context.active_object.data.materials.append(m_hair)
    # Red bow
    bpy.ops.mesh.primitive_cube_add(size=.1*s, location=(x,y-.15*s,z+1.7*s))
    bw = bpy.context.active_object; bw.scale=(1.5,.5,.8); bw.data.materials.append(m_bow)
    # Bow center
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.03*s, location=(x,y-.15*s,z+1.7*s))
    bpy.context.active_object.data.materials.append(m_bow)
    # Eyes
    for ex in [-.06,.06]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.02*s, location=(x+ex*s,y+.16*s,z+1.58*s))
        bpy.context.active_object.data.materials.append(m_nose)
    # Mouth
    bpy.ops.mesh.primitive_cube_add(size=.05*s, location=(x,y+.16*s,z+1.5*s))
    mo = bpy.context.active_object; mo.scale=(1,.3,.3); mo.data.materials.append(m_bow)
    # Apron
    bpy.ops.mesh.primitive_plane_add(size=.25*s, location=(x,y+.19*s,z+1.1*s))
    ap = bpy.context.active_object; ap.rotation_euler=(math.radians(90),0,0); ap.scale=(1,1,1)
    mat_apron = mat("Apron",(1,1,1,1),.6)
    ap.data.materials.append(mat_apron)

build_dorothy(-1.2,-15,.1)

# ============ SCARECROW ============
def build_scarecrow(x,y,z,s=1.3):
    # Pole
    bpy.ops.mesh.primitive_cylinder_add(radius=.05*s, depth=1.8*s, location=(x,y,z+.9*s))
    bpy.context.active_object.data.materials.append(m_scr_hat)
    # Cross arm pole
    bpy.ops.mesh.primitive_cylinder_add(radius=.04*s, depth=.8*s, location=(x,y,z+1.3*s))
    ap = bpy.context.active_object; ap.rotation_euler=(0,math.radians(90),0); ap.data.materials.append(m_scr_hat)
    # Body (patchwork)
    bpy.ops.mesh.primitive_cube_add(size=.5*s, location=(x,y,z+.8*s))
    bd = bpy.context.active_object; bd.scale=(1,.7,1.2); bd.data.materials.append(m_scr_body)
    # Patch on body
    bpy.ops.mesh.primitive_cube_add(size=.15*s, location=(x+.1*s,y+.2*s,z+.8*s))
    pt = bpy.context.active_object; pt.scale=(1,.3,1); pt.data.materials.append(m_scr_hat)
    # Belt
    bpy.ops.mesh.primitive_cylinder_add(radius=.22*s, depth=.05*s, location=(x,y,z+.95*s))
    blt = bpy.context.active_object; blt.rotation_euler=(math.radians(90),0,0); blt.data.materials.append(m_scarecrow_buckle)
    # Buckle
    bpy.ops.mesh.primitive_cube_add(size=.08*s, location=(x,y+.22*s,z+.95*s))
    bk = bpy.context.active_object; bk.scale=(1,.3,1); bk.data.materials.append(m_scarecrow_buckle)
    # Arms (stuffed)
    for ax in [-.4,.4]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.08*s, depth=.4*s, location=(x+ax*s,y,z+1.2*s))
        a = bpy.context.active_object; a.rotation_euler=(0,math.radians(30 if ax>0 else -30),0); a.data.materials.append(m_scr_body)
        # Hands (mittens)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.06*s, location=(x+ax*s+ax*.2*s,y,z+1.0*s))
        bpy.context.active_object.data.materials.append(m_scr_hat)
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.22*s, location=(x,y,z+1.55*s))
    hd = bpy.context.active_object; hd.data.materials.append(m_scr_face)
    # Hat brim
    bpy.ops.mesh.primitive_cylinder_add(radius=.35*s, depth=.05*s, location=(x,y,z+1.7*s))
    bpy.context.active_object.data.materials.append(m_scr_hat)
    # Hat top
    bpy.ops.mesh.primitive_cone_add(radius1=.2*s, radius2=.15*s, depth=.3*s, location=(x,y,z+1.85*s))
    bpy.context.active_object.data.materials.append(m_scr_hat)
    # Eyes
    for ex in [-.08,.08]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.03*s, location=(x+ex*s,y+.18*s,z+1.58*s))
        bpy.context.active_object.data.materials.append(m_scr_hat)
    # Nose (carrot)
    bpy.ops.mesh.primitive_cone_add(radius1=.04*s, radius2=0, depth=.1*s, location=(x,y+.22*s,z+1.55*s))
    ns = bpy.context.active_object; ns.rotation_euler=(math.radians(-90),0,0); ns.data.materials.append(m_bow)
    # Stitched mouth
    bpy.ops.mesh.primitive_cube_add(size=.1*s, location=(x,y+.2*s,z+1.48*s))
    mo = bpy.context.active_object; mo.scale=(1,.2,.2); mo.data.materials.append(m_scr_hat)

build_scarecrow(.5,-12,.1)

# ============ TIN MAN ============
def build_tinman(x,y,z,s=1.2):
    # Legs
    for lx in [-.15,.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.1*s, depth=.6*s, location=(x+lx*s,y,z+.3*s))
        bpy.context.active_object.data.materials.append(m_tin)
        # Knee joint
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.1*s, location=(x+lx*s,y,z+.3*s))
        bpy.context.active_object.data.materials.append(m_tin_dark)
        # Feet
        bpy.ops.mesh.primitive_cube_add(size=.2*s, location=(x+lx*s,y+.05*s,z+.05*s))
        f = bpy.context.active_object; f.scale=(1,1.5,.4); f.data.materials.append(m_tin)
    # Body (torso)
    bpy.ops.mesh.primitive_cylinder_add(radius=.25*s, depth=.6*s, location=(x,y,z+.9*s))
    bpy.context.active_object.data.materials.append(m_tin)
    # Chest plate
    bpy.ops.mesh.primitive_cube_add(size=.3*s, location=(x,y+.2*s,z+.95*s))
    cp = bpy.context.active_object; cp.scale=(.8,.3,.8); cp.data.materials.append(m_tin_dark)
    # Keyhole
    bpy.ops.mesh.primitive_cylinder_add(radius=.05*s, depth=.02*s, location=(x,y+.35*s,z+1*s))
    kh = bpy.context.active_object; kh.rotation_euler=(math.radians(90),0,0); kh.data.materials.append(m_tin_dark)
    # Shoulder joints
    for ax in [-.28,.28]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.1*s, location=(x+ax*s,y,z+1.15*s))
        bpy.context.active_object.data.materials.append(m_tin_dark)
    # Arms
    for ax in [-.3,.3]:
        bpy.ops.mesh.primitive_cylinder_add(radius=.07*s, depth=.5*s, location=(x+ax*s,y,z+.85*s))
        a = bpy.context.active_object; a.rotation_euler=(0,math.radians(15 if ax>0 else -15),0); a.data.materials.append(m_tin)
        # Elbow
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.07*s, location=(x+ax*s,y,z+.85*s))
        bpy.context.active_object.data.materials.append(m_tin_dark)
        # Hand
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.06*s, location=(x+ax*s+ax*.15*s,y,z+.6*s))
        bpy.context.active_object.data.materials.append(m_tin)
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.2*s, location=(x,y,z+1.4*s))
    hd = bpy.context.active_object; hd.scale=(1,1,1.1); hd.data.materials.append(m_tin)
    # Funnel hat
    bpy.ops.mesh.primitive_cone_add(radius1=.25*s, radius2=.05*s, depth=.35*s, location=(x,y,z+1.65*s))
    bpy.context.active_object.data.materials.append(m_tin_hat)
    # Eyes
    for ex in [-.08,.08]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.04*s, location=(x+ex*s,y+.18*s,z+1.42*s))
        bpy.context.active_object.data.materials.append(m_tin_dark)
    # Oil can in right hand
    bpy.ops.mesh.primitive_cylinder_add(radius=.08*s, depth=.15*s, location=(x+.4*s,y+.1*s,z+.6*s))
    bpy.context.active_object.data.materials.append(m_tin)
    # Oil can spout
    bpy.ops.mesh.primitive_cylinder_add(radius=.02*s, depth=.1*s, location=(x+.4*s,y+.2*s,z+.65*s))
    sp = bpy.context.active_object; sp.rotation_euler=(math.radians(45),0,0); sp.data.materials.append(m_tin)

build_tinman(1.8,-10,.1)

# ============ LION ============
def build_lion(x,y,z,s=1.0):
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.4*s, location=(x,y,z+.4*s))
    bd = bpy.context.active_object; bd.scale=(1,1.3,.8); bd.data.materials.append(m_lion)
    # Belly (lighter)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.35*s, location=(x,y+.1*s,z+.35*s))
    bl = bpy.context.active_object; bl.scale=(.8,1,.7); bl.data.materials.append(m_lion_belly)
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.25*s, location=(x,y+.5*s,z+.65*s))
    bpy.context.active_object.data.materials.append(m_lion)
    # Mane (multiple spheres)
    for a in range(0,360,25):
        r = math.radians(a)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.12*s, location=(x+.25*s*math.cos(r), y+.5*s+.25*s*math.sin(r), z+.65*s+.1*s*math.sin(a)))
        bpy.context.active_object.data.materials.append(m_manee)
    # Nose
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.06*s, location=(x,y+.75*s,z+.6*s))
    bpy.context.active_object.data.materials.append(m_nose)
    # Eyes
    for ex in [-.1,.1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.04*s, location=(x+ex*s,y+.7*s,z+.7*s))
        bpy.context.active_object.data.materials.append(m_nose)
    # Ears
    for ex in [-.15,.15]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.08*s, location=(x+ex*s,y+.45*s,z+.85*s))
        bpy.context.active_object.data.materials.append(m_manee)
    # Legs
    for lx in [-.25,.25]:
        for ly in [-.3,.3]:
            bpy.ops.mesh.primitive_cylinder_add(radius=.08*s, depth=.4*s, location=(x+lx*s,y+ly*s,z+.2*s))
            bpy.context.active_object.data.materials.append(m_lion)
            # Paw
            bpy.ops.mesh.primitive_uv_sphere_add(radius=.1*s, location=(x+lx*s,y+ly*s+.05*s,z+.05*s))
            pw = bpy.context.active_object; pw.scale=(1,1.2,.5); pw.data.materials.append(m_lion)
    # Tail
    bpy.ops.mesh.primitive_cylinder_add(radius=.04*s, depth=.5*s, location=(x,y-.5*s,z+.4*s))
    t = bpy.context.active_object; t.rotation_euler=(math.radians(-30),0,0); t.data.materials.append(m_lion)
    # Tail tuft
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.08*s, location=(x,y-.7*s,z+.25*s))
    bpy.context.active_object.data.materials.append(m_manee)
    # Collar
    bpy.ops.mesh.primitive_torus_add(major_radius=.25*s, minor_radius=.03*s, location=(x,y+.4*s,z+.55*s))
    cl = bpy.context.active_object; cl.rotation_euler=(math.radians(90),0,0); cl.data.materials.append(m_bow)

build_lion(-.5,-7,.1)

# =