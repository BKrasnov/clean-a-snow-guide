"""Farmyard kit, authored as solid primitives in Blender; dimensions are Roblox studs.

JSON records the same solids for assembly in Studio without new uploaded mesh assets.
Blender world uses (Roblox X, -Roblox Z, Roblox Y), in metres (one stud = .28 m).
"""
from pathlib import Path
import bpy
import json
import math
import random
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
ROOT = ASSET.parents[2]
STUD = .28
C = dict(snow='F3F6F5', shade='CDCDED', ice='A8DEE7', wood='CD925C',
         oak='C28E49', bark='80401B', dark='2B1A11', cream='FFFDF5',
         gold='FFCE43', sun='FAD66E', red='D6392B', blue='40A5FF',
         pine='54A577', spruce='3C8E63', metal='A0B0C4')
T = Matrix(((1,0,0),(0,0,-1),(0,1,0)))
parts = []
materials = {}
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def rotation(rx=0, ry=0, rz=0):
    return Matrix.Rotation(math.radians(rx),3,'X') @ Matrix.Rotation(math.radians(ry),3,'Y') @ Matrix.Rotation(math.radians(rz),3,'Z')

def material(key):
    if key not in materials:
        m = bpy.data.materials.new('M_Farmyard_'+key)
        rgb = [int(C[key][i:i+2],16)/255 for i in (0,2,4)]
        m.diffuse_color=tuple((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for v in rgb)+(1,)
        m.use_nodes=True
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color
        m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72
        materials[key]=m
    return materials[key]

def solid(group,name,at,size,col,rot=None,kind='Part',collide=True):
    rot=rot or Matrix.Identity(3)
    frame = (T@rot@T.transposed()).to_4x4()
    frame.translation = T@Vector(at)*STUD
    if kind=='WedgePart':
        # Wedge slopes from its bottom at -Z to its upper edge at +Z.
        verts=[(-.5,-.5,-.5),(.5,-.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(-.5,.5,.5),(.5,.5,.5)]
        faces=[(0,2,3,1),(2,4,5,3),(0,1,5,4),(0,4,2),(1,3,5)]
        mesh=bpy.data.meshes.new(name)
        mesh.from_pydata([T@Vector((v[0]*size[0],v[1]*size[1],v[2]*size[2]))*STUD for v in verts],[],faces)
        mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    elif kind=='Ball':
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.5)
        obj=bpy.context.object
        obj.name=name
        obj.scale=(size[0]*STUD,size[2]*STUD,size[1]*STUD)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj=bpy.context.object
        obj.name=name
        obj.scale=(size[0]*STUD,size[2]*STUD,size[1]*STUD)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.matrix_world=frame
    obj.data.materials.append(material(col))
    collection=bpy.data.collections.get(group)
    if not collection:
        collection=bpy.data.collections.new(group);bpy.context.scene.collection.children.link(collection)
    for existing in list(obj.users_collection): existing.objects.unlink(obj)
    collection.objects.link(obj)
    parts.append(dict(group=group,name=name,at=list(at),size=list(size),rgb=C[col],
                      rotation=[round(rot[i][j],7) for i in range(3) for j in range(3)],
                      kind=kind,collide=collide))
    return obj

def builder(group,origin,yaw=0):
    R=rotation(ry=yaw)
    def part(name,x,y,z,w,h,d,col,rot=None,kind='Part',collide=True):
        return solid(group,name,Vector(origin)+R@Vector((x,y,z)),(w,h,d),col,R@(rot or Matrix.Identity(3)),kind,collide)
    return part

def lantern(p,name,x,y,z):
    p(name+'Bracket',x,y+1,z,.55,1.8,.7,'dark',collide=False)
    p(name+'Base',x,y-1.05,z+.48,1.6,.24,1.25,'bark',collide=False)
    p(name+'Light',x,y-.38,z+.48,1.03,1.22,.82,'sun',collide=False)
    for side in (-1,1):
        p(name+'Frame',x+side*.62,y-.4,z+.96,.16,1.5,.18,'bark',collide=False)
    p(name+'Cap',x,y+.47,z+.48,1.8,.32,1.5,'dark',collide=False)
    p(name+'Snow',x,y+.69,z+.48,1.55,.18,1.25,'snow',collide=False)

def cabin(group,origin,yaw,garage=False):
    p=builder(group,origin,yaw)
    width,depth=32,27
    col='red' if garage else 'wood'
    p('Foundation',0,.4,0,33,.8,28,'bark')
    p('Floor',0,.91,0,31,.24,26,'oak')
    # Clear opening in the garage, closed scenic house with inset windows.
    p('BackWall',0,7.3,-13,32,13,.7,col)
    for x in (-15.6,15.6): p('SideWall',x,7.3,0,.8,13,27,col)
    if garage:
        for x in (-13,13): p('FrontPier',x,7.3,13,6,13,.9,col)
        p('DoorHeader',0,13,13,22,1.6,1,'wood')
        for x in (-10.25,10.25): p('DoorFrame',x,7.05,13.6,.7,12.3,.7,'cream')
        p('UpperWall',0,15.4,13,32,4.2,.8,'red')
    else:
        p('FrontWall',0,7.3,13,32,13,.8,'wood')
        p('Door',0,5.3,13.55,5.2,8.8,.45,'bark')
        p('DoorInset',0,6.5,13.83,3.8,4.3,.12,'gold',collide=False)
        p('DoorKnob',1.9,4.5,13.95,.32,.32,.32,'dark',collide=False)
        for x in (-9.5,9.5):
            p('WindowFrame',x,7.7,13.65,6.7,6.5,.55,'bark',collide=False)
            p('WindowGlow',x,7.7,14,5.7,5.5,.18,'sun',collide=False)
            p('WindowVertical',x,7.7,14.15,.32,5.7,.22,'cream',collide=False)
            p('WindowHorizontal',x,7.7,14.15,5.9,.32,.22,'cream',collide=False)
    # Individual horizontal planks, shallow relief, no coincident faces.
    for row in range(7):
        y=1.9+row*1.7
        for side in (-1,1):
            p('SidePlank',side*16.08,y,0,.16,.16,26.7,'oak',collide=False)
        p('BackPlank',0,y,-13.42,31.9,.15,.14,'oak',collide=False)
        if not garage: p('FrontPlank',0,y,13.43,31.9,.13,.13,'oak',collide=False)
    for x in (-15.7,15.7):
        for z in (-13,13): p('CornerPost',x,7.6,z,1.1,14,1.15,'cream' if garage else 'oak')
    roof_base=16.8 if garage else 14
    slope=32
    roof_rise=math.tan(math.radians(slope))*17
    for side in (-1,1):
        tilt=rotation(rz=-side*slope)
        y=roof_base+roof_rise/2
        p('RoofTimber',side*8.5,y,0,20.1,.72,30.2,'bark',tilt)
        p('SnowRoof',side*8.5,y+.62,0,20.5,1.05,30.7,'snow',tilt,collide=False)
        for end in (-1,1):
            p('SnowRoofLip',side*8.5,y+.78,end*15.1,21.1,1.55,3.5,'snow',tilt,kind='Ball',collide=False)
        # Large overlapping pillows turn a straight sheet into a soft snow cap.
        rng=random.Random((37 if garage else 71)+side)
        for i in range(5):
            p('SnowEave',side*(16.35+rng.uniform(-.25,.25)),roof_base+.53,
              -12+i*6+rng.uniform(-.6,.6),rng.uniform(3.8,4.8),rng.uniform(1.5,2.1),
              rng.uniform(7,9),'snow',rotation(rz=-side*24),kind='Ball',collide=False)
    for z in (-13,13):
        for side in (-1,1):
            p('Gable',side*8,roof_base+roof_rise/2,z,.8,roof_rise,16,col,
              rotation(ry=-side*90),kind='WedgePart')
    for i in range(4):
        p('RidgeSnow',0,roof_base+roof_rise+.7,-11.5+i*7.5,3,1.5,10,'snow',kind='Ball',collide=False)
    if garage:
        p('LoftDoor',0,20.1,13.6,7,5.5,.55,'red',collide=False)
        for x in (-3.7,3.7): p('LoftFrame',x,20.1,14,.5,6.2,.5,'cream',collide=False)
        for y in (17,23.2): p('LoftFrame',0,y,14,7.9,.5,.5,'cream',collide=False)
        for side in (-1,1): p('LoftBrace',0,20.1,14.25,.45,8.2,.4,'cream',rotation(rz=side*47),collide=False)
        p('GarageSign',0,15.2,15.05,24,3.1,.65,'bark',collide=False)
        # Shelving leaves the middle clear for an avatar and a parked vehicle.
        for side in (-1,1):
            for y in (2.1,5.4,8.7): p('Shelf',side*12.5,y,-8,4.2,.45,8,'wood')
            for z in (-11,-5): p('ShelfLeg',side*14,4.8,z,.5,9,.5,'bark')
            for i in range(3): p('Crate',side*12.5,2.9+i*3.3,-10,2.8,1.3,2.8,'gold' if i==1 else 'oak',collide=False)
    else:
        p('PorchDeck',0,.85,18.1,34,.6,11,'oak')
        p('StepLow',0,.18,25,14,.36,2.2,'wood')
        p('StepHigh',0,.48,23.4,15,.4,1.4,'oak')
        for x in (-15,15):
            p('PorchPost',x,6.5,22,1.1,11,1.1,'wood')
            p('RailSide',x,3,18,.5,.45,8,'wood')
            for z in (15.5,18,20.5): p('RailSpindle',x,2.1,z,.35,2.6,.35,'wood')
        for side in (-1,1):
            p('FrontRail',side*11,3,22,7,.5,.55,'wood')
            for i in range(4): p('RailSpindle',side*(8+i*2),2.1,22,.35,2.6,.35,'wood')
        p('PorchCanopy',0,12.2,18,35,.65,12,'bark',rotation(rx=8))
        p('PorchSnow',0,12.8,18,35.4,.85,12.5,'snow',rotation(rx=8),collide=False)
        for x,z,w,d in [(-13,23.4,9,3.2),(-5,23.65,11,2.8),(4,23.45,10,3.3),(12,23.3,10,3.4)]:
            p('PorchSnowPillow',x,12.1,z,w,1.3,d,'snow',rotation(rx=8),kind='Ball',collide=False)
        p('Chimney',9,21,-6,4,7,4,'metal')
        p('ChimneyCap',9,24.6,-6,4.7,.7,4.7,'snow',collide=False)
    lantern(p,'LeftLamp',-12.4,11.5,14.3)
    lantern(p,'RightLamp',12.4,11.5,14.3)

cabin('Garage',(-66,0,33),12,True)
cabin('House',(66,0,33),-12,False)

p=builder('LaunchArch',(0,0,-49))
for x in (-56,56):
    p('StoneFoot',x,1.2,0,4.8,2.4,4.8,'metal')
    p('Pillar',x,11,0,2.8,19,2.8,'wood')
    p('PillarInset',x,12,1.55,.65,13,.22,'oak',collide=False)
    lantern(p,'ArchLamp',x,15,2)
    p('Bolt',x,20,2,.85,.85,.5,'gold',collide=False)
    p('Brace',x+(-3 if x>0 else 3),17,0,1.4,7.8,1.6,'oak',rotation(rz=36 if x>0 else -36))
p('Header',0,21,0,117,4,3.3,'wood')
p('HeaderPlank',0,20,1.85,114,.55,.35,'oak',collide=False)
p('Sign',0,20.7,2.15,37,4,.8,'bark',collide=False)
arch_rng=random.Random(295)
for i in range(12):
    p('SnowCap',-54+i*9.8,23.05+arch_rng.uniform(0,.35),arch_rng.uniform(-.3,.3),
      arch_rng.uniform(13.5,16),arch_rng.uniform(1.8,2.6),arch_rng.uniform(5.5,6.5),
      'snow',kind='Ball',collide=False)

for index in range(6):
    x=-42.5+index*17
    p=builder(f'MapFrame{index+1:02d}',(x,0,-44))
    p('MapBack',0,7.2,0,13.8,12,.65,'bark',collide=False)
    p('MapSky',0,8,.4,11.9,8.5,.18,'ice',collide=False)
    p('MapField',0,4.8,.65,11.9,2,.2,'pine',collide=False)
    for side in (-1,1):
        p('MapPost',side*6.85,7.1,.2,.85,14,1,'wood')
        p('MapFoot',side*6.85,.45,.2,1.7,.9,2.5,'metal')
    for y in (2.5,13): p('MapCrossbar',0,y,.2,15,.85,1.3,'wood',collide=False)
    p('MapSnow',0,13.6,.2,15.5,.5,1.7,'snow',collide=False)
    p('MapSnowPillow',-2,13.75,.2,10,1.1,2.2,'snow',kind='Ball',collide=False)
    p('MapSnowPillow',4,13.65,.2,7.4,.9,2.3,'snow',kind='Ball',collide=False)
    for n in range(3):
        for side in (-1,1):
            p('MapMountain',-3.5+n*3.3+side*.8,8.7,1.05,.3,3.5,1.6,'snow' if n%2 else 'shade',rotation(ry=-side*90),kind='WedgePart',collide=False)

for group,origin,yaw in [('Rewards',(-78,0,-12),25),('Upgrades',(-77,0,-36),20),('Classes',(78,0,-10),-25)]:
    p=builder(group,origin,yaw)
    for x in (-6,6): p('Post',x,5.3,0,.8,10.6,.8,'wood')
    p('Counter',0,3.1,1,13.6,.7,5,'wood')
    p('CounterBody',0,1.5,0,12,2.6,4.3,'bark')
    for x in (-4,0,4): p('Cabinet',x,1.8,2.26,3.5,2.1,.18,'pine',collide=False)
    p('Roof',0,10.7,0,15,.65,7,'oak',rotation(rx=9))
    p('SnowRoof',0,11.25,0,15.4,.7,7.4,'snow',rotation(rx=9),collide=False)
    for i in range(3): p('StallSnowPillow',-5+i*5,11.2,2.5,7,1.5+(i%2)*.3,3.5,'snow',kind='Ball',collide=False)
    p('Sign',0,8.4,1,12.6,2.6,.7,'bark',collide=False)
    lantern(p,'StallLamp',5.5,6,2)
    if group=='Rewards':
        for i in range(3):
            p('Gift',-3.8+i*3.7,4.5+(i%2)*.5,1,2.7,2+(i%2),2.7,'red' if i%2==0 else 'blue',collide=False)
            p('Ribbon',-3.8+i*3.7,4.5+(i%2)*.5,2.4,.4,2.1+(i%2),.14,'gold',collide=False)
    elif group=='Classes':
        for x in (-3.5,3.5):
            p('MannequinBody',x,5,0,2,2.3,1.2,'blue' if x<0 else 'red',collide=False)
            p('MannequinHead',x,6.8,0,1.4,1.4,1.4,'cream',collide=False)
    else:
        for i in range(3): p('ToolBox',-3.7+i*3.5,4.2,1,2.7,1.6,2.4,'red' if i%2==0 else 'gold',collide=False)

for side in (-1,1):
    p=builder('EntryLanterns',(side*13,0,83))
    p('Base',0,.5,0,3,1,3,'oak')
    p('Post',0,3.3,0,1.7,5.6,1.7,'wood')
    p('SnowCap',0,6.4,0,2.7,.55,2.7,'snow',collide=False)
    lantern(p,'GateLamp',0,8.3,0)

ASSET.mkdir(exist_ok=True,parents=True)
(ASSET/'export').mkdir(exist_ok=True)
(ASSET/'export'/'parts.json').write_text(json.dumps({'units':'studs','origin':[14000,120.75,0],'parts':parts},indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'FarmyardLobby.blend'))
print('FARMYARD_PARTS',len(parts))
