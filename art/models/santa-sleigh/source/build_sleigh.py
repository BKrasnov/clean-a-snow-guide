"""Build the rigged Frostbound-style Santa team. Metres, +X forward, Z up."""
from pathlib import Path
from math import sin, cos, pi, radians
import json, sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT.parent/'starter-farmhouse/source'))
import build_farmhouse as kit
from check_surface_overlap import audit
from render_farmhouse import camera,light,render

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
group=kit.collection('SantaSleigh',scene.collection)
kit.MODEL='SantaSleigh'
kit.COLORS=dict(red='#D6392B',gold='#FFCE43',fur='#CD925C',mane='#C28E49',dark='#80401B',
               leather='#966240',black='#2B1A11',snow='#F3F6F5',white='#FFFDF5',
               skin='#F2C29A',pink='#CE9ED2',shade='#CDCDED',honey='#FAD66E')
surf=kit.palette()
m=kit.Mesh('SantaSleigh_Body',group,surf)
bones={};weights={};active=None
def bone(name,h,t,parent=None):
    global active
    bones[name]=(h,t,parent);active=name
    return name
def paint(fn,*args):
    start=len(m.vertices);fn(*args)
    weights.update({i:{active:1.0} for i in range(start,len(m.vertices))})
def box(x,y,z,l,w,h,c):paint(m.box,(x,y,z),(l,w,h),c)
def panel(poly,y,depth,c):paint(m.prism,poly,y-depth/2,y+depth/2,'Y',c)
def beam(a,b,w,d,c):paint(m.beam,a,b,w,d,c)
def block(x,y,z,l,w,h,c,r=.035):
    # Clipped corners and a small shoulder give larger toy blocks a readable rim.
    def ring(dx,dy,cut,z0):
        return [(x+a,y+b,z0) for a,b in [(dx-cut,dy),(-dx+cut,dy),(-dx,dy-cut),(-dx,-dy+cut),(-dx+cut,-dy),(dx-cut,-dy),(dx,-dy+cut),(dx,dy-cut)]]
    a=ring(l/2,w/2,r,z-h/2);b=ring(l/2,w/2,r,z+h/2-r*.48);crown=ring(l/2-r*.42,w/2-r*.42,r*.8,z+h/2)
    faces=[tuple(range(7,-1,-1)),tuple(range(16,24))]+[(k+j*8,(k+1)%8+j*8,(k+1)%8+(j+1)*8,k+(j+1)*8) for j in range(2) for k in range(8)]
    paint(m.add,a+b+crown,faces,c)
def rod(a,b,w,c):beam(a,b,w,w*.91,c)

bone('Root',(0,0,0),(0,0,.45))
sled=bone('Sleigh',(-1.65,0,.23),(-1.65,0,.53),'Root')
# Solid side panels with gold trim following the stepped silhouette.
runner=[(-3.14,.26),(-3.10,.09),(-2.95,.0),(-.69,.0),(-.49,.09),(-.31,.29),(-.23,.52),(-.24,.74),(-.34,.85),(-.52,.85),(-.61,.77),(-.61,.65),(-.53,.65),(-.50,.73),(-.41,.73),(-.39,.62),(-.45,.43),(-.61,.24),(-.76,.16),(-2.91,.16),(-2.96,.27)]
rim=[(-3.04,1.69),(-2.42,1.69),(-2.42,1.51),(-2.15,1.51),(-2.15,1.34),(-1.82,1.34),(-1.82,1.17),(-1.31,1.17),(-1.31,1.01),(-.59,1.01)]
for s in (-1,1):
    y=s*.69
    panel(runner,y,.155,'gold')
    for x in (-2.62,-1.04):box(x,y,.335,.18,.13,.38,'mane')
    panel(rim+[(-.59,.58),(-.79,.52),(-2.84,.52),(-3.04,.69)],y,.14,'red')
    panel([(x+.012,z+.032) for x,z in rim]+[(x-.065,z-.058) for x,z in reversed(rim)],y+s*.015,.157,'gold')
box(-1.81,0,.58,2.43,1.32,.155,'red')
box(-2.96,0,1.09,.14,1.29,1.0,'red')
box(-.63,0,.785,.15,1.28,.315,'red')
block(-1.97,0,.95,.83,1.04,.28,'leather')
box(-2.32,0,1.24,.16,.96,.48,'dark')
# Sack with octagonal belly, gathered neck and individual folds.
def sack():
    rows=[]
    for rx,ry,z in [(.31,.40,1.13),(.43,.49,1.35),(.42,.47,1.64),(.27,.32,1.89),(.17,.22,1.99),(.29,.33,2.15),(.30,.34,2.23)]:
        rows.extend([(-2.65+rx*cos(i*pi/4),ry*sin(i*pi/4),z+(.034*cos(i*3) if z>2.2 else 0)) for i in range(8)])
    fs=[tuple(range(7,-1,-1)),tuple(range(48,56))]+[(j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k) for j in range(6) for k in range(8)]
    paint(m.add,rows,fs,'leather')
sack()
block(-2.65,0,1.978,.44,.54,.093,'gold',.06)
for s in (-1,1):rod((-2.66+s*.05,-.255,1.97),(-2.66+s*.11,-.36,1.79),.061,'gold')

pel=bone('Santa_Hips',(-1.92,0,1.09),(-1.92,0,1.26),sled)
box(-1.92,0,1.15,.54,.68,.22,'red')
body=bone('Santa_Spine',(-1.92,0,1.24),(-1.94,0,1.81),pel)
block(-1.91,0,1.556,.63,.77,.71,'red',.065)
block(-1.90,0,1.268,.66,.81,.105,'white',.025)
box(-1.90,0,1.424,.668,.797,.12,'black')
box(-1.55,0,1.428,.052,.205,.158,'gold')
box(-1.516,0,1.43,.021,.112,.078,'black')
head=bone('Santa_Head',(-1.94,0,1.85),(-1.94,0,2.47),body)
block(-1.94,0,2.18,.684,.79,.69,'skin',.05)
for s in (-1,1):
    box(-1.94,s*.411,2.15,.185,.09,.205,'skin')
    box(-2.06,s*.382,2.16,.34,.102,.42,'snow')
    box(-1.84,s*.38,2.014,.16,.09,.18,'snow')
    box(-1.593,s*.168,2.24,.028,.091,.128,'black')
    box(-1.571,s*.15,2.274,.022,.034,.041,'white')
    box(-1.582,s*.17,2.36,.044,.144,.051,'white')
block(-1.552,0,2.149,.12,.157,.111,'skin',.018)
# Beard outline and inset smiling mouth face forward on X.
def mask(poly,x,depth,col):paint(m.prism,poly,x-depth/2,x+depth/2,'X',col)
mask([(-.38,2.14),(-.30,2.14),(-.30,2.055),(.30,2.055),(.30,2.14),(.38,2.14),(.38,1.92),(.28,1.92),(.28,1.81),(.15,1.81),(.15,1.70),(-.13,1.70),(-.13,1.79),(-.27,1.82),(-.27,1.90),(-.38,1.90)],-1.615,.173,'snow')
mask([(-.154,2.051),(.154,2.051),(.126,1.96),(.073,1.93),(-.067,1.93),(-.126,1.96)],-1.514,.041,'black')
box(-1.487,0,1.955,.028,.145,.03,'pink')
for s in (-1,1):
    block(-1.517,s*.145,2.078,.11,.278,.083,'white',.014)
block(-1.97,0,2.51,.787,.884,.164,'snow',.041)
block(-2.00,0,2.66,.68,.78,.20,'red',.06)
block(-2.07,.011,2.80,.55,.58,.12,'red',.04)
panel([(-2.03,2.84),(-2.31,2.85),(-2.50,2.70),(-2.59,2.52),(-2.44,2.47),(-2.35,2.62),(-2.19,2.70)],-.28,.30,'red')
block(-2.53,-.28,2.469,.216,.233,.20,'white',.035)
hands={}
for s,tag in [(-1,'R'),(1,'L')]:
    shoulder=(-1.91,s*.394,1.77);elbow=(-1.76,s*.52,1.55);wrist=(-1.48,s*.50,1.55)
    upper=bone('Santa_UpperArm_'+tag,shoulder,elbow,body)
    beam(shoulder,elbow,.275,.285,'red')
    lower=bone('Santa_Forearm_'+tag,elbow,wrist,upper)
    beam(elbow,wrist,.254,.259,'red')
    box(-1.51,s*.50,1.555,.10,.284,.279,'white')
    hand=bone('Santa_Hand_'+tag,wrist,(-1.29,s*.5,1.55),lower)
    block(-1.372,s*.50,1.55,.217,.242,.232,'skin',.025)
    hands[s]=hand
    hip=(-1.89,s*.215,1.13);knee=(-1.51,s*.221,1.075);ankle=(-1.49,s*.224,.79)
    thigh=bone('Santa_Thigh_'+tag,hip,knee,pel);beam(hip,knee,.258,.293,'red')
    shin=bone('Santa_Shin_'+tag,knee,ankle,thigh);beam(knee,ankle,.23,.253,'red')
    box(-1.486,s*.224,.859,.258,.272,.086,'white')
    foot=bone('Santa_Boot_'+tag,ankle,(-1.26,s*.224,.74),shin)
    block(-1.394,s*.224,.735,.39,.29,.174,'black',.022)

def ribbon(a,b,sag,from_bone,to_bone,w):
    # Consecutive sections share vertices; end weights follow hand and chest.
    start=len(m.vertices);vv=[];ff=[]
    for i in range(7):
        t=i/6;p=Vector(a).lerp(Vector(b),t);p.z-=sag*4*t*(1-t)
        vv.extend([tuple(p+Vector((0,dy,dz))) for dy,dz in [(-w*.27,-w*.5),(w*.27,-w*.5),(w*.27,w*.5),(-w*.27,w*.5)]])
    for i in range(6):
        for j in range(4):ff.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
    m.add(vv,[(3,2,1,0),tuple(range(24,28))]+ff,'dark')
    for i in range(28):
        t=(i//4)/6;weights[start+i]={n:v for n,v in [(from_bone,1-t),(to_bone,t)] if v>0}

for s,prefix in [(-1,'Deer_R'),(1,'Deer_L')]:
    y=s*.78;x=1.44
    def dn(n):return prefix+'_'+n
    torso=bone(dn('Body'),(x-.36,y,.85),(x+.43,y,1.10),'Root')
    block(x,y,1.04,1.56,.66,.73,'fur',.065)
    box(x+.42,y,1.04,.153,.692,.738,'red')
    box(x+.33,y,.998,1.03,.705,.134,'red')
    box(x+.862,y,1.007,.074,.185,.172,'gold')
    box(x+.904,y,1.01,.026,.095,.080,'red')
    for side in (-1,1):box(x+.13,y+side*.372,1.002,.138,.066,.173,'gold')
    box(x+.79,y,.877,.105,.468,.116,'white')
    box(x+.775,y,.802,.09,.341,.073,'white')
    tail=bone(dn('Tail'),(x-.75,y,1.17),(x-.95,y,1.34),torso)
    beam((x-.72,y,1.21),(x-.94,y,1.36),.15,.17,'fur')
    neck=bone(dn('Neck'),(x+.51,y,1.12),(x+.59,y,1.57),torso)
    block(x+.53,y,1.37,.414,.49,.60,'fur',.034)
    box(x+.754,y,1.38,.09,.524,.51,'white')
    box(x+.798,y,1.17,.067,.378,.22,'white')
    hd=bone(dn('Head'),(x+.58,y,1.61),(x+.88,y,1.77),neck)
    head_start=len(m.vertices)
    block(x+.61,y,1.79,.598,.584,.512,'fur',.039)
    block(x+.916,y,1.704,.34,.51,.254,'white',.028)
    block(x+1.067,y,1.785,.143,.272,.122,'black',.021)
    box(x+1.093,y,1.667,.029,.19,.077,'dark')
    box(x+1.111,y,1.642,.025,.125,.033,'pink')
    for side in (-1,1):
        box(x+.902,y+side*.181,1.899,.030,.086,.094,'black')
        box(x+.932,y+side*.17,1.922,.019,.028,.028,'white')
        box(x+.74,y+side*.247,1.685,.12,.095,.09,'white')

        beam((x+.54,y+side*.25,1.89),(x+.44,y+side*.441,2.008),.138,.155,'fur')
        box(x+.548,y+side*.36,1.973,.047,.103,.055,'skin')
        # The forked antlers have one continuous stepped silhouette each.
        poly=[(-.061,0),(.061,0),(.061,.14),(.18,.14),(.18,.35),(.074,.35),(.074,.249),(-.01,.249),(-.01,.35),(-.13,.35),(-.13,.50),(-.238,.50),(-.238,.276),(-.113,.276),(-.113,.165),(-.061,.165)]
        mask([(y+side*(.195-u*1.12+v*.22),2.03+v*1.09) for u,v in poly],x+.52,.146,'mane')
    for i in range(head_start,len(m.vertices)):
        vx,vy,vz=m.vertices[i];m.vertices[i]=(vx,y+(vy-y)*1.16,vz)
    for dx,k in [(-.54,'Hind'),(.53,'Fore')]:
        for side,tag in [(-1,'R'),(1,'L')]:
            yy=y+side*.213
            hip=(x+dx,yy,.824);knee=(x+dx-.035,yy,.435);ank=(x+dx+.007,yy,.15)
            up=bone(dn(k+'Upper_'+tag),hip,knee,torso);beam(hip,knee,.205,.208,'fur')
            low=bone(dn(k+'Lower_'+tag),knee,ank,up);beam(knee,ank,.171,.178,'mane')
            hoof=bone(dn(k+'Hoof_'+tag),ank,(ank[0]+.123,yy,.08),low)
            box(ank[0]+.035,yy,.091,.254,.205,.182,'black')
    ribbon((-1.34,s*.54,1.55),(x+.13,y+s*.385,1.01),.22,hands[s],torso,.065)
    ribbon((-.625,s*.665,.745),(x+.24,y+s*.34,.95),.085,sled,torso,.060)

ob=m.object()
arm=bpy.data.armatures.new('SantaSleigh');rig=bpy.data.objects.new('SantaSleigh_Rig',arm)
group.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for name,(h,t,parent) in bones.items():
    b=arm.edit_bones.new(name);b.head=h;b.tail=t
    if parent:b.parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
for name in bones:
    if name=='Root':continue
    g=ob.vertex_groups.new(name=name)
    for i,w in weights.items():
        if name in w:g.add([i],w[name],'REPLACE')
assert len(weights)==len(ob.data.vertices)
ob.parent=rig;mod=ob.modifiers.new('Character skin','ARMATURE');mod.object=rig
arm.display_type='STICK';rig.show_in_front=False
scene.unit_settings.system='METRIC'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
        sp.region_3d.view_location=(-.22,0,1.31);sp.region_3d.view_distance=9.1
        sp.region_3d.view_rotation=Vector((.62,-1,.32)).to_track_quat('Z','Y')
rig.select_set(False);ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/SantaSleigh_master.blend'))
rep=audit(.002,True,'SantaSleigh');print('RESULT',rep,flush=True);assert rep['triangles_checked']<=4000 and rep['overlapping_face_pairs']==0
(ROOT/'reports/surfaces.json').write_text(json.dumps(rep,indent=2)+'\n')
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.view_settings.view_transform='Khronos PBR Neutral'
scene.world=bpy.data.worlds.new('Soft sky');scene.world.color=(.53,.61,.77)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.014))
floor=bpy.data.materials.new('Blue studio');floor.diffuse_color=(.37,.51,.69,1)
bpy.context.object.data.materials.append(floor)
light(scene.collection,'Key',(1,-4,8),(0,0,1),680,6,(1,.93,.82))
light(scene.collection,'Fill',(-4,2,5),(0,0,1),420,6,(.80,.90,1))
camera(scene,scene.collection,(7.4,-10.3,4.15),(-.22,0,1.33),ortho=7.05)
render(scene,ROOT/'preview','team',(1200,760))
# Exercise the unmodified saved skeleton on a diagnostic pose.
for name,angles in {'Santa_Head':(0,12,0),'Santa_Forearm_R':(18,0,0),'Santa_Hand_L':(-8,0,0),
                     'Deer_R_ForeUpper_R':(0,0,27),'Deer_R_ForeLower_R':(0,0,-42),
                     'Deer_L_Head':(0,-15,0),'Deer_L_HindUpper_L':(0,0,-19),
                     'Deer_R_Neck':(0,0,-9)}.items():
    p=rig.pose.bones[name];p.rotation_mode='XYZ';p.rotation_euler=[radians(a) for a in angles]
bpy.context.view_layer.update()
posed=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
motion=max((a.co-b.co).length for a,b in zip(ob.data.vertices,posed.vertices))
assert motion>.10
render(scene,ROOT/'preview','rig-test',(1200,760))
print('RIG',len(bones),motion)
