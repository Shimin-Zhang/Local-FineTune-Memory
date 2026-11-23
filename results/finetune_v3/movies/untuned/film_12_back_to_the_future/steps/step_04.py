import bpy, math, random, bmesh
from mathutils import Vector

# Clean
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

def cm(n,c,r=0.5,mt=0.0,e=0.0,ec=(1,1,1,1)):
    m=bpy.data.materials.new(n);m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=c
    b.inputs['Roughness'].default_value=r
    b.inputs['Metallic'].default_value=mt
    if e>0:
        b.inputs['Emission Strength'].default_value=e
        b.inputs['Emission Color'].default_value=ec
    return m

m_road=cm("Road",(0.12,0.12,0.12,1),0.9)
m_conc=cm("Conc",(0.35,0.35,0.33,1),0.8)
m_stone=cm("Stone",(0.4,0.38,0.35,1),0.9)
m_metal=cm("Metal",(0.6,0.6,0.65,1),0.3,0.9)
m_copper=cm("Copper",(0.8,0.4,0.2,1),0.4,0.8)
m_glass=cm("Glass",(0.1,0.15,0.2,1),0.1)
m_fire=cm("Fire",(1,0.3,0,1),0.5,0,5,(1,0.3,0,1))
m_bolt=cm("Bolt",(0.7,0.8,1,1),0.1,0,15,(0.7,0.8,1,1))
m_deal=cm("Deal",(0.7,0.72,0.75,1),0.2,0.9)
m_tire=cm("Tire",(0.05,0.05,0.05,1),0.9)
m_white=cm("White",(0.9,0.9,0.9,1),0.7)
m_black=cm("Black",(0.05,0.05,0.05,1),0.5)
m_clock=cm("Clock",(0.9,0.9,0.85,1),0.3)
m_roof=cm("Roof",(0.2,0.2,0.25,1),0.6,0.5)
m_win=cm("Win",(0.1,0.1,0.15,1),0.3)
m_winlit=cm("WinLit",(1,0.8,0.4,1),0.3,0,2,(1,0.8,0.4,1))
m_cable=cm("Cable",(0.1,0.1,0.1,1),0.5,0.8)
m_wood=cm("Wood",(0.5,0.3,0.15,1),0.8)
m_spark=cm("Spark",(1,0.5,0.1,1),0.1,0,10,(1,0.5,0.1,1))
m_smoke=cm("Smoke",(0.3,0.3,0.3,1),1,0,0.1,(0.3,0.3,0.3,1))
m_pole=cm("Pole",(0.2,0.2,0.2,1),0.6,0.5)
m_b1=cm("B1",(0.5,0.45,0.4,1),0.8)
m_b2=cm("B2",(0.4,0.4,0.45,1),0.8)
m_b3=cm("B3",(0.45,0.42,0.38,1),0.8)
m_door=cm("Door",(0.3,0.15,0.05,1),0.7)
m_glow=cm("Glow",(0.5,0.6,1,1),0.1,0,20,(0.5,0.6,1,1))
m_cloud=cm("Cloud",(0.2,0.2,0.25,1),1,0,0.3,(0.2,0.2,0.25,1))
m_head=cm("Head",(1,1,0.8,1),0.1,0,5,(1,1,0.8,1))
m_tail=cm("Tail",(1,0.1,0.1,1),0.1,0,3,(1,0.1,0.1,1))

# Ground
bpy.ops.mesh.primitive_plane_add(size=120,location=(0,0,0))
st=bpy.context.object;st.name="Street";st.data.materials.append(m_road)
for y in[-25,25]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,y,0.1))
    s=bpy.context.object;s.name=f"SW{y}";s.scale=(55,5,0.2);s.data.materials.append(m_conc)
for i in range(-4,5):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(i*3,0,0.05))
    c=bpy.context.object;c.scale=(1.5,8,0.02);c.data.materials.append(m_white)

# Tower
bpy.ops.mesh.primitive_cylinder_add(radius=8,depth=2,location=(0,0,1))
t=bpy.context.object;t.name="TBase";t.data.materials.append(m_stone)
bpy.ops.mesh.primitive_cylinder_add(radius=5,depth=30,location=(0,0,17))
t=bpy.context.object;t.name="TShaft";t.data.materials.append(m_stone)
for h in[5,10,15,20,25]:
    bpy.ops.mesh.primitive_cylinder_add(radius=5.2,depth=0.5,location=(0,0,h))
    b=bpy.context.object;b.name=f"Band{h}";b.data.materials.append(m_conc)
bpy.ops.mesh.primitive_cylinder_add(radius=3,depth=0.3,location=(0,5.1,22),rotation=(math.pi/2,0,0))
cf=bpy.context.object;cf.name="ClockFace";cf.data.materials.append(m_clock)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,5.2,22.5))
hh=bpy.context.object;hh.name="HourHand";hh.scale=(0.15,0.05,1.2);hh.rotation_euler=(0,0,math.radians(30));hh.data.materials.append(m_black)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,5.2,22.5))
mh=bpy.context.object;mh.name="MinHand";mh.scale=(0.1,0.05,1.8);mh.rotation_euler=(0,0,math.radians(60));mh.data.materials.append(m_black)
bpy.ops.mesh.primitive_cylinder_add(radius=0.2,depth=0.1,location=(0,5.2,22),rotation=(math.pi/2,0,0))
cc=bpy.context.object;cc.name="ClockC";cc.data.materials.append(m_black)
bpy.ops.mesh.primitive_cylinder_add(radius=3,depth=0.3,location=(0,0,32.5))
ct=bpy.context.object;ct.name="ClockTop";ct.data.materials.append(m_clock)
bpy.ops.mesh.primitive_cone_add(radius1=5.5,radius2=0,depth=5,location=(0,0,35))
r=bpy.context.object;r.name="TRoof";r.data.materials.append(m_roof)
bpy.ops.mesh.primitive_cone_add(radius1=0.5,radius2=0,depth=3,location=(0,0,38.5))
sp=bpy.context.object;sp.name="Spire";sp.data.materials.append(m_metal)
bpy.ops.mesh.primitive_cylinder_add(radius=0.05,depth=2,location=(0,0,40.5))
lr=bpy.context.object;lr.name="LRod";lr.data.materials.append(m_copper)
for ang in[0,math.pi/2,math.pi,3*math.pi/2]:
    for h in[8,14,20]:
        x=5.1*math.cos(ang);y=5.1*math.sin(ang)
        bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,h))
        w=bpy.context.object;w.scale=(0.8,0.15,1.5);w.rotation_euler=(0,0,ang);w.data.materials.append(m_win)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,5.1,1.5))
d=bpy.context.object;d.name="TDoor";d.scale=(1.5,0.1,2.5);d.data.materials.append(m_door)

# Lightning
def bolt(s,e,segs=15,spread=3,name="Bolt"):
    mesh=bpy.data.meshes.new(name);obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj);bm=bmesh.new();pts=[]
    for i in range(segs+1):
        t=i/segs;p=s.lerp(e,t)
        if 0<i<segs:
            p+=Vector((random.uniform(-spread,spread)*(1-t*0.5),random.uniform(-spread,spread)*(1-t*0.5),random.uniform(-spread*0.3,spread*0.3)))
        pts.append(p)
    for i in range(len(pts)-1):
        p1,p2=pts[i],pts[i+1];d=(p2-p1).normalized()
        up=Vector((0,0,1))
        if abs(d.dot(up))>0.9:up=Vector((1,0,0))
        side=d.cross(up).normalized();up2=d.cross(side).normalized()
        r1,r2=0.3,0.2
        v1=bm.verts.new(p1+side*r1);v2=bm.verts.new(p1-side*r1)
        v3=bm.verts.new(p1+up2*r1);v4=bm.verts.new(p1-up2*r1)
        v5=bm.verts.new(p2+side*r2);v6=bm.verts.new(p2-side*r2)
        v7=bm.verts.new(p2+up2*r2);v8=bm.verts.new(p2-up2*r2)
        bm.faces.new([v1,v2,v6,v5]);bm.faces.new([v2,v4,v8,v6])
        bm.faces.new([v4,v3,v7,v8]);bm.faces.new([v3,v1,v5,v7])
    bm.to_mesh(mesh);bm.free();obj.data.materials.append(m_bolt);return obj

bolt(Vector((5,-10,60)),Vector((0,0,40)),20,4,"MainBolt")
for _ in range(3):
    bolt(Vector((random.uniform(-2,2),random.uniform(-2,2),random.uniform(35,45))),Vector((random.uniform(-8,8),random.uniform(-8,8),random.uniform(20,30))),8,2,f"Br{random.randint(1,99)}")
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5,location=(0,0,40),segments=16,ring_count=8)
ig=bpy.context.object;ig.name="ImpactGlow";ig.data.materials.append(m_glow)

# Cable
bpy.ops.mesh.primitive_cylinder_add(radius=0.15,depth=12,location=(-20,0,6))
p=bpy.context.object;p.name="CPole";p.data.materials.append(m_pole)
bpy.ops.mesh.primitive_cube_add(size=1,location=(-20,0,11))
ca=bpy.context.object;ca.name="CrossArm";ca.scale=(0.1,3,0.1);ca.data.materials.append(m_wood)
cd=bpy.data.curves.new("CableC",'CURVE');cd.dimensions='3D';cd.bevel_depth=0.08;cd.bevel_resolution=4
sp=cd.splines.new('BEZIER');sp.bezier_points.add(2)
sp.bezier_points[0].co=Vector((0,0,38));sp.bezier_points[0].handle_left=Vector((0,0,40));sp.bezier_points[0].handle_right=Vector((-5,0,37))
sp.bezier_points[1].co=Vector((-10,0,25));sp.bezier_points[1].handle_left=Vector((-5,0,32));sp.bezier_points[1].handle_right=Vector((-15,0,22))
sp.bezier_points[2].co=Vector((-20,0,11));sp.bezier_points[2].handle_left=Vector((-15,0,18));sp.bezier_points[2].handle_right=Vector((-20,0,10))
co=bpy.data.objects.new("Cable",cd);bpy.context.collection.objects.link(co);co.data.materials.append(m_cable)
cd2=bpy.data.curves.new("CableC2",'CURVE');cd2.dimensions='3D';cd2.bevel_depth=0.06;cd2.bevel_resolution=4
sp2=cd2.splines.new('BEZIER');sp2.bezier_points.add(2)
sp2.bezier_points[0].co=Vector((0.5,0.5,37));sp2.bezier_points[0].handle_left=Vector((0.5,0.5,39));sp2.bezier_points[0].handle_right=Vector((-4.5,0.5,36))
sp2.bezier_points[1].co=Vector((-10,0.5,24));sp2.bezier_points[1].handle_left=Vector((-5,0.5,31));sp2.bezier_points[1].handle_right=Vector((-15,0.5,21))
sp2.bezier_points[2].co=Vector((-20,0.5,10.5));sp2.bezier_points[2].handle_left=Vector((-15,0.5,17));sp2.bezier_points[2].handle_right=Vector((-20,0.5,9.5))
co2=bpy.data.objects.new("Cable2",cd2);bpy.context.collection.objects.link(co2);co2.data.materials.append(m_cable)

# DeLorean
dl=Vector((15,15,0.5))
bpy.ops.mesh.primitive_cube_add(size=1,location=dl)
b=bpy.context.object;b.name="DBody";b.scale=(2.5,4.5,0.8);b.data.materials.append(m_deal)
bpy.ops.mesh.primitive_cube_add(size=1,location=(dl.x+1.5,dl.y,dl.z+0.2))
h=bpy.context.object;h.name="DHood";h.scale=(1.5,4.3,0.4);h.data.materials.append(m_deal)
bpy.ops.mesh.primitive_cube_add(size=1,location=(dl.x-1.5,dl.y,dl.z+0.2))
tk=bpy.context.object;tk.name="DTrunk";tk.scale=(1.5,4.3,0.4);tk.data.materials.append(m_deal)
bpy.ops.mesh.primitive_cube_add(size=1,location=(dl.x-0.5,dl.y,dl.z+1.0))
cb=bpy.context.object;cb.name="DCabin";cb.scale=(1.5,4.0,0.5);cb.data.materials.append(m_deal)
bpy.ops.mesh.primitive_cube_add(size=1,location=(dl.x+0.8,dl.y,dl.z+0.9))
ws=bpy.context.object;ws.name="DWindshield";ws.scale=(0.3,3.8,0.6);ws.rotation_euler=(0,math.radians(-15),0);ws.data.materials.append(m_glass)
bpy.ops.mesh.primitive_cube_add(size=1,location=(dl.x-1.5,dl.y,dl.z+0.9))
rw=bpy.context.object;rw.name="DRearWin";rw.scale=(0.2,3.8,0.5);rw.rotation_euler=(0,math.radians(15),0);rw.data.materials.append(m_glass)
for side in[-1,1]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(dl.x-0.5,dl.y+side*2.0,dl.z+0.8))
    sw=bpy.context.object;sw.name=f"DSWin{side}";sw.scale=(1.2,0.1,0.5);sw.data.materials.append(m_glass)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(dl.x,dl.y+side*2.3,dl.z+1.5))
    dr=bpy.context.object;dr.name=f"DDoor{side}";dr.scale=(1.8,0.1,1.2);dr.rotation_euler=(0,0,math.radians(side*60));dr.data.materials.append(m_deal)
wpos=[(dl.x+1.5,dl.y+2.0,dl.z-0.3),(dl.x+1.5,dl.y-2.0,dl.z-0.3),(dl.x-1.5,dl.y+2.0,dl.z-0.3),(dl.x-1.5,dl.y-2.0,dl.z-0.3)]
for i,pos in enumerate(wpos):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4,depth=0.3,location=pos,rotation=(0,math.pi/2,0))
    wh=bpy.context.object;wh.name=f"DWheel{i}";wh.data.materials.append(m_tire)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2,depth=0.35,location=pos,rotation=(0,math.pi/2,0))
    hb=bpy.context.object;hb.name=f"DHub{i}";hb.data.materials.append(m_metal)
for side in[-1,1]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15,location=(dl.x+2.5,dl.y+side*1.5,dl.z+0.3))
    hl=bpy.context.object;hl.name=f"DHead{side}";hl.data.materials.append(m_head)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12,location=(dl.x-2.5,dl.y+side*1.5,dl.z+0.3))
    tl=bpy.context.object;tl.name=f"DTail{side}";tl.data.materials.append(m_tail)

# Fire trail
tsx=dl.x-3;tex=dl.x-25;ty=dl.y;tz=dl.z-0.2
bpy.ops.mesh.primitive_cube_add(size=1,location=((tsx+tex)/2,ty,tz))
ft=bpy.context.object;ft.name="FireTrail";ft.scale=((tsx-tex)/2,1.5,0.3);ft.data.materials.append(m_fire)
bpy.ops.mesh.primitive_cube_add(size=1,location=((tsx+tex)/2,ty,tz-0.1))
ft2=bpy.context.object;ft2.name="FireTrail2";ft2.scale=((tsx-tex)/2*0.8,2.0,0.2);ft2.data.materials.append(m_fire)
for i in range(30):
    t=i/29;x=tsx+(tex-tsx)*t;y=ty+random.uniform(-1.5,1.5);z=tz+random.uniform(-0.2,0.5)
    sz=random.uniform(0.05,0.15)*(1-t*0.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=sz,location=(x,y,z))
    sp=bpy.context.object;sp.name=f"Spark{i}";sp.data.materials.append(m_spark)
for i in range(15):
    t=i/14;x=tsx+(tex-tsx)*t*0.7;y=ty+random.uniform(-1,1);z=tz+random.uniform(0.5,2.0)
    sz=random.uniform(0.3,0.8)*(1+t)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=sz,location=(x,y,z))
    sm=bpy.context.object;sm.name=f"Smoke{i}";sm.data.materials.append(m_smoke)

# Buildings
bl=[(-15,-30,8,10,15,m_b1),(-25,-30,10,12,20,m_b2),(-35,-30,8,10,12,m_b3),(-45,-30,12,14,18,m_b1)]
for x,y,w,d,h,mat in bl:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,h/2))
    blg=bpy.context.object;blg.name=f"BldgL{x}";blg.scale=(w/2,d/2,h/2);blg.data.materials.append(mat)
    for wy in range(2,int(h),3):
        for wx in range(-int(w/2)+2,int(w/2)-1,3):
            if random.random()>0.3:
                bpy.ops.mesh.primitive_cube_add(size=1,location=(x+wx,y+d/2+0.1,wy))
                wn=bpy.context.object;wn.name=f"WinL{x}{wx}{wy}";wn.scale=(1,0.1,1.2)
                wn.data.materials.append(m_winlit if random.random()>0.5 else m_win)
br=[(15,30,8,10,14,m_b2),(25,30,10,12,18,m_b3),(35,30,8,10,12,m_b1),(45,30,12,14,22,m_b2)]
for x,y,w,d,h,mat in br:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,h/2))
    blg=bpy.context.object;blg.name=f"BldgR{x}";blg.scale=(w/2,d/2,h/2);blg.data.materials.append(mat)
    for wy in range(2,int(h),3):
        for wx in range(-int(w/2)+2,int(w/2)-1,3):
            if random.random()>0.3:
                bpy.ops.mesh.primitive_cube_add(size=1,location=(x+wx,y-d/2-0.1,wy))
                wn=bpy.context.object;wn.name=f"WinR{x}{wx}{wy}";wn.scale=(1,0.1,1.2)
                wn.data.materials.append(m_winlit if random.random()>0.5 else m_win)

# Street lights
for lx in[-10,0,10,20]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08,depth=8,location=(lx,-22,4))
    lp=bpy.context.object;lp.name=f"SLP{lx}";lp.data.materials.append(m_pole)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3,location=(lx,-22,8.2))
    lm=bpy.context.object;lm.name=f"SLL{lx}"
    ml=cm(f"SL{lx}",(1,0.9,0.6,1),0.1,0,3,(1,0.9,0.6,1))
    lm.data.materials.append(ml)

# Clouds
for i in range(20):
    x=random.uniform(-50,50);y=random.uniform(-50,50);z=random.uniform(50,70)
    sz=random.uniform(5,12)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=sz,location=(x,y,z))
    cl=bpy.context.object;cl.name=f"Cloud{i}";cl.data.materials.append(m_cloud)

# Camera
bpy.ops.object.camera_add(location=(30,35,15),rotation=(math.radians(75),0,math.radians(-40)))
cam=bpy.context.object;cam.name="Camera"
scene.camera=cam

# Lights
bpy.ops.object.light_add(type='SUN',location=(0,0,50))
sun=bpy.context.object;sun.name="Sun";sun.data.energy=2;sun.rotation_euler=(math.radians(45),0,math.radians(30))

bpy.ops.object.light_add(type='POINT',location=(0,0,40))
pl=bpy.context.object;pl.name="LightningLight";pl.data.energy=500;pl.data.color=(0.7,0.8,1.0)

bpy.ops.object.light_add(type='POINT',location=(dl.x-5,dl.y,2))
fl=bpy.context.object;fl.name="FireLight";fl.data.energy=100;fl.data.color=(1,0.3,0)

bpy.ops.object.light_add(type='POINT',location=(dl.x+2,dl.y,2))
hl=bpy.context.object;hl.name="Headlight";hl.data.energy=50;hl.data.color=(1,1,0.8)
