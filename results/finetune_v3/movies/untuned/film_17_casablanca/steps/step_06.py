import bpy
import math
import random
from mathutils import Vector

scene = bpy.context.scene

# Remove all lights
for obj in list(scene.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Dark night world
world = scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()
bg = nodes.new('ShaderNodeBackground')
bg.inputs[0].default_value = (0.003, 0.005, 0.015, 1.0)
bg.inputs[1].default_value = 1.0
out = nodes.new('ShaderNodeOutputWorld')
links.new(bg.outputs[0], out.inputs[0])

# Very dark materials
def mm(name, c, r=0.5, m=0.0, e=0.0, ec=None):
    if ec is None: ec = c
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    n = mat.node_tree.nodes; l = mat.node_tree.links
    n.clear()
    b = n.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*c, 1.0)
    b.inputs['Roughness'].default_value = r
    b.inputs['Metallic'].default_value = m
    if e > 0:
        b.inputs['Emission Color'].default_value = (*ec, 1.0)
        b.inputs['Emission Strength'].default_value = e
    o = n.new('ShaderNodeOutputMaterial')
    l.new(b.outputs[0], o.inputs[0])
    return mat

ma = mm("AspD", (0.02, 0.02, 0.025), 0.9)
mc = mm("ConD", (0.06, 0.06, 0.055), 0.8)
mm_ = mm("MetD", (0.12, 0.12, 0.14), 0.4, 0.7)
mdm = mm("DMetD", (0.04, 0.04, 0.05), 0.5, 0.6)
mg = mm("GlsD", (0.2, 0.25, 0.35), 0.1)
mcd = mm("CDarkD", (0.025, 0.025, 0.03), 0.6)
mcl = mm("CLightD", (0.08, 0.07, 0.05), 0.6)
mh = mm("HatD", (0.03, 0.025, 0.015), 0.5)
msk = mm("SkinD", (0.2, 0.14, 0.1), 0.4)
mcb = mm("CarBD", (0.01, 0.01, 0.012), 0.3, 0.5)
mcg = mm("CarGD", (0.06, 0.08, 0.1), 0.1)
mhw = mm("HWallD", (0.05, 0.05, 0.06), 0.6, 0.3)
mhd = mm("HDoorD", (0.06, 0.06, 0.07), 0.5, 0.4)
mt = mm("TireD", (0.01, 0.01, 0.01), 0.9)
mp = mm("PropD", (0.04, 0.04, 0.04), 0.4, 0.5)
mf = mm("FusD", (0.08, 0.08, 0.1), 0.3, 0.5)
mw = mm("WingD", (0.07, 0.07, 0.08), 0.3, 0.5)
me = mm("EngD", (0.05, 0.05, 0.05), 0.4, 0.7)
mwo = mm("WoodD", (0.06, 0.04, 0.02), 0.7)
mlw = mm("LWarmD", (1.0, 0.7, 0.3), 0.4, 0, 25.0, (1.0, 0.7, 0.3))
mlc = mm("LColdD", (0.4, 0.5, 0.8), 0.4, 0, 12.0, (0.4, 0.5, 0.8))
mtl = mm("TLightD", (1.0, 0.08, 0.05), 0.4, 0, 12.0, (1.0, 0.08, 0.05))

for obj in scene.objects:
    if obj.type != 'MESH': continue
    n = obj.name
    if n.startswith("Ground"): obj.data.materials.clear(); obj.data.materials.append(ma)
    elif n.startswith("Marking") or n.startswith("CenterLine") or n.startswith("TaxiMark"): obj.data.materials.clear(); obj.data.materials.append(mc)
    elif n.startswith("HangarBody") or n.startswith("HangarRoof") or n.startswith("ControlTower"): obj.data.materials.clear(); obj.data.materials.append(mhw)
    elif n.startswith("HangarDoor") or n.startswith("DoorFrame"): obj.data.materials.clear(); obj.data.materials.append(mhd)
    elif n.startswith("HangarWin") or n.startswith("TowerWin") or n.startswith("CockpitWin") or n.startswith("PaxWin") or n.startswith("CarWin") or n.startswith("Windshield") or n.startswith("RearWindow"): obj.data.materials.clear(); obj.data.materials.append(mg)
    elif n.startswith("Fuselage") or n.startswith("Nose") or n.startswith("Tail") or n.startswith("VStab") or n.startswith("HStab"): obj.data.materials.clear(); obj.data.materials.append(mf)
    elif n.startswith("Wing"): obj.data.materials.clear(); obj.data.materials.append(mw)
    elif n.startswith("Engine"): obj.data.materials.clear(); obj.data.materials.append(me)
    elif n.startswith("PropHub") or n.startswith("Blade"): obj.data.materials.clear(); obj.data.materials.append(mp)
    elif n.startswith("Gear") or n.startswith("Wheel") or n.startswith("TailWheel") or n.startswith("CarWheel"): obj.data.materials.clear(); obj.data.materials.append(mt)
    elif n.startswith("Hubcap"): obj.data.materials.clear(); obj.data.materials.append(mm_)
    elif n.startswith("Headlight"): obj.data.materials.clear(); obj.data.materials.append(mlw)
    elif n.startswith("Taillight"): obj.data.materials.clear(); obj.data.materials.append(mtl)
    elif n.startswith("Rick"):
        if "Head" in n: obj.data.materials.clear(); obj.data.materials.append(msk)
        elif "Hat" in n: obj.data.materials.clear(); obj.data.materials.append(mh)
        else: obj.data.materials.clear(); obj.data.materials.append(mcd)
    elif n.startswith("Ilsa"):
        if "Head" in n: obj.data.materials.clear(); obj.data.materials.append(msk)
        elif "Hat" in n: obj.data.materials.clear(); obj.data.materials.append(mh)
        else: obj.data.materials.clear(); obj.data.materials.append(mcl)
    elif n.startswith("CarBody") or n.startswith("CarRoof") or n.startswith("Hood") or n.startswith("Trunk"): obj.data.materials.clear(); obj.data.materials.append(mcb)
    elif n.startswith("LightPole") or n.startswith("SignPole") or n.startswith("Ladder") or n.startswith("SmallLampPole"): obj.data.materials.clear(); obj.data.materials.append(mdm)
    elif n.startswith("LightFixture") or n.startswith("SmallLampGlobe"): obj.data.materials.clear(); obj.data.materials.append(mlw)
    elif n.startswith("Crate") or n.startswith("ExtraCrate") or n.startswith("Bench") or n.startswith("Trunk") or n.startswith("Suitcase"): obj.data.materials.clear(); obj.data.materials.append(mwo)
    elif n.startswith("Drum") or n.startswith("Barrel") or n.startswith("TrashCan"): obj.data.materials.clear(); obj.data.materials.append(mdm)
    elif n.startswith("EdgeLight") or n.startswith("RunwayEdge"): obj.data.materials.clear(); obj.data.materials.append(mlc)
    elif n.startswith("SignBoard"): obj.data.materials.clear(); obj.data.materials.append(mc)
    elif n.startswith("Tree"): obj.data.materials.clear(); obj.data.materials.append(mm(f"T{n}", (0.005, 0.01, 0.005), 0.9))
    elif n.startswith("CityLight"): obj.data.materials.clear(); obj.data.materials.append(mm(f"C{n}", (0.8, 0.5, 0.2), 0.5, 0, 10.0, (0.8, 0.5, 0.2)))

# Lights - strong but controlled
for i, p in enumerate([(-10, 5, 6), (10, 5, 6), (-10, -5, 6), (10, -5, 6)]):
    ld = bpy.data.lights.new(f"F{i}", type='POINT'); ld.energy = 12000; ld.color = (1.0, 0.75, 0.35); ld.shadow_soft_size = 0.8
    lo = bpy.data.objects.new(f"FO{i}", ld); scene.collection.objects.link(lo); lo.location = p

hl = bpy.data.lights.new("HL", type='POINT'); hl.energy = 8000; hl.color = (0.5, 0.6, 1.0); hl.shadow_soft_size = 2.0
hlo = bpy.data.objects.new("HLO", hl); scene.collection.objects.link(hlo); hlo.location = (15, 14, 4)

for s in [-1, 1]:
    cl = bpy.data.lights.new(f"CH{s}", type='SPOT'); cl.energy = 2000; cl.color = (1.0, 0.8, 0.4); cl.spot_size = math.radians(35); cl.shadow_soft_size = 0.2
    clo = bpy.data.objects.new(f"CHO{s}", cl); scene.collection.objects.link(clo); clo.location = (-7.8, -2+s*0.6, 0.5); clo.rotation_euler = (0, math.radians(-90), 0)

ml = bpy.data.lights.new("Moon", type='SUN'); ml.energy = 0.3; ml.color = (0.3, 0.4, 0.7); ml.shadow_soft_size = 3.0
mlo = bpy.data.objects.new("MO", ml); scene.collection.objects.link(mlo); mlo.rotation_euler = (math.radians(55), math.radians(10), 0)

kl = bpy.data.lights.new("KC", type='AREA'); kl.energy = 800; kl.color = (1.0, 0.75, 0.4); kl.size = 