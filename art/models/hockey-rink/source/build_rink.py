"""Static Clean a Snow rink. Construction coordinates are Roblox studs."""
from pathlib import Path
from math import sin, cos, pi, hypot
import sys, json
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT.parent/'starter-farmhouse/source'))
import build_farmhouse as kit
from check_surface_overlap import audit
from render_farmhouse import camera, light, render

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
group=kit.collection('HockeyRink',scene.collection)
kit.MODEL='HockeyRink'
kit.COLORS=dict(ice='#A8DEE7',wood='#CD925C',dark='#80401B',amber='#C28E49',snow='#F3F6F5',cream='#FFFDF5',red='#D6392B',blue='#40A5FF',gold='#FFCE43',wire='#2B1A11',grey='#909282',shadow='#966240')
surf=kit.palette()
def part(name): return kit.Mesh(name,group,surf)
def finish(m):
    m.vertices=[tuple(v*.28 for v in p) for p in m.vertices]
    obj=m.object()
    if m.name=='Marked ice':
        import bmesh
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
        bm.to_mesh(obj.data);bm.free()
    return obj
def perimeter(offset=0):
    pts=[]
    for j,(x,y) in enumerate([(50.4,16.8),(-50.4,16.8),(-50.4,-16.8),(50.4,-16.8)]):
        for i in range(4):
            a=(j+i/3)*pi/2
            pts.append((x+(12+offset)*cos(a),y+(12+offset)*sin(a)))
    return pts

m=part('Raised timber deck')
m.box((0,0,8),(144.8,77.6,2),'shadow')
for x in (-67,-23,23,67):
    for y in (-34,34):m.box((x,y,3.53),(3.2,3.4,7.06),'dark')
finish(m)
# One watertight ice slab. The centre stripe and circle share edges with the ice.
m=part('Marked ice')
boundary=perimeter(-.015)
verts=[];faces=[];colors=[];lookup={}
def face(poly,color):
    idx=[]
    for v in poly:
        key=tuple(round(t,6) for t in v)
        if key not in lookup:lookup[key]=len(verts);verts.append(key)
        if not idx or idx[-1]!=lookup[key]:idx.append(lookup[key])
    if idx and idx[0]==idx[-1]:idx.pop()
    if len(set(idx))>=3:faces.append(idx);colors.append(color)
def clip(poly,k,side):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[0]-k)*side>=0:out.append(a)
        if (a[0]-k)*(b[0]-k)<0:
            t=(k-a[0])/(b[0]-a[0]);out.append((k,a[1]+t*(b[1]-a[1])))
    return out
# Sample long straights as well as rounded corners for a smooth centre circle.
outline=[]
for a,b in zip(boundary,boundary[1:]+boundary[:1]):
    n=6 if abs(b[0]-a[0])>50 else 2 if abs(b[1]-a[1])>25 else 1
    outline.extend([(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n)])
rings=[[(r*x/hypot(x,y),r*y/hypot(x,y)) for x,y in outline] for r in (7.2,8.1)]+[outline]
for i in range(len(outline)):
    j=(i+1)%len(outline)
    for poly,color in [([(0,0),rings[0][i],rings[0][j]],'ice'),([rings[0][i],rings[1][i],rings[1][j],rings[0][j]],'red'),([rings[1][i],outline[i],outline[j],rings[1][j]],'ice')]:
        for piece,c in [(clip(poly,-.42,-1),color),(clip(clip(poly,-.42,1),.42,-1),'red'),(clip(poly,.42,1),color)]:
            face([(x,y,9.4) for x,y in piece],c)
    a,b=outline[i],outline[j]
    edge=[a]+[(k,a[1]+(b[1]-a[1])*(k-a[0])/(b[0]-a[0])) for k in sorted((-.42,.42),reverse=b[0]<a[0]) if (a[0]-k)*(b[0]-k)<0]+[b]
    for u,v in zip(edge,edge[1:]):
        face([(*u,9.4),(*v,9.4),(*v,9.04),(*u,9.04)],'ice')
        face([(0,0,9.04),(*v,9.04),(*u,9.04)],'ice')
m.add(verts,faces,'ice');m.colors=colors;finish(m)

m=part('Rounded boards and cream rail')
# End the sweep at either side of the front entrance.
path=perimeter();start=11
path=path[start+1:]+path[:start+1]
# index 17 is the left endpoint of the front straight.
for_path=[(3.1,-28.8)]+path+[(-3.1,-28.8)]
outer=perimeter(.98);outer=outer[start+1:]+outer[:start+1]
outer=[(3.1,-29.78)]+outer+[(-3.1,-29.78)]
rows=[]
for (x,y),(u,v) in zip(for_path,outer):
    rows.append([(x,y,9.06),(u,v,9.06),(u,v,11.5),(u,v,11.99),(x,y,11.99),(x,y,11.5)])
fs=[tuple(range(5,-1,-1))];cs=['wood']
for i in range(len(rows)-1):
    for k,c in enumerate(['wood','wood','cream','cream','cream','wood']):
        a=i*6+k;b=i*6+(k+1)%6;fs.append((a,b,b+6,a+6));cs.append(c)
fs.append(tuple(range(6*(len(rows)-1),6*len(rows))));cs.append('wood')
m.add(sum(rows,[]),fs,'wood');m.colors=cs;finish(m)

m=part('Entry stair and snow ramps')
profile=[(-52,0),(-38.84,0),(-38.84,9)]
for i in range(9):
    y=-38.84-(i+1)*13.16/9
    profile.append((y,9-i))
    if i<8:profile.append((y,8-i))
m.prism(profile,-8.3,8.3,'X','wood')
for x in (-7.85,7.85):
    for y,h in [(-51,1),(-40,9)]:m.box((x,y,h+1.25),(.71,.73,2.66),'shadow')
    m.beam((x,-51.5,3.4),(x,-39.7,11.92),.84,.98,'wood')
m.prism([(-60.8,0),(-38.84,0),(-38.84,9),(-60.8,.18)],-58,-43,'X','snow')
m.prism([(72.45,0),(94.4,0),(94.4,.18),(72.45,9)],-7,8,'Y','snow')
finish(m)

for side,c in [(-1,'red'),(1,'blue')]:
    m=part(c.title()+' goal')
    x=side*57;back=x+side*3.3;w=7.2;h=16.6;z=9.41
    for y in (-w,w):
        m.beam((x,y,z),(x,y,h),.54,.54,c)
        m.beam((x,y,h-.18),(back,y,z+.22),.30,.32,'cream')
        m.beam((x,y,z+.28),(back,y,z+.28),.36,.36,c)
    m.beam((x,-w-.29,h+.19),(x,w+.29,h+.19),.62,.62,c)
    m.beam((back,-w-.19,z+.31),(back,w+.19,z+.31),.37,.42,c)
    for y in (-5.4,-3.6,-1.8,0,1.8,3.6,5.4):
        m.beam((x,y,h-.03),(back,y,z+.38),.19,.18,'cream')
    for t in (.24,.48,.72):
        xx=x+(back-x)*t;zz=h+(z+.35-h)*t
        m.beam((xx,-w,zz),(xx,w,zz),.22,.21,'cream')
    finish(m)

m=part('Scoreboard')
m.box((0,34.3,15.1),(1.5,1.28,12.3),'dark')
m.box((0,34.2,21.25),(17.6,1.52,6.9),'shadow')
for x,c in [(-4.15,'red'),(4.15,'blue')]:
    m.box((x,33.39,21.24),(7.90,.18,5.49),c)
m.prism([(-9.05,24.55),(-8.62,25.25),(-4.2,25.97),(0,25.72),(3,26.06),(8.8,25.27),(9.06,24.60)],33.07,35.36,'Y','snow')
MARGIN=1.37
m.vertices=[(x*MARGIN,34.2+(y-34.2)*MARGIN,9+(z-9)*1.19) for x,y,z in m.vertices]
finish(m)
m=part('Team sign')
m.box((13,-34.8,12.98),(.95,1.02,8),'amber')
def disk(x,y,z,r,c):
    m.prism([(x+r*cos(2*pi*i/12),z+r*sin(2*pi*i/12)) for i in range(12)],y,y+.51,'Y',c)
for x,c in [(10.65,'red'),(15.35,'blue')]:
    disk(x,-35.18,17.75,2.31,c)
    m.prism([(x-1.28,17.06),(x+.06,17.06),(x+1.03,18.93),(x+.64,19.09),(x-.22,17.60),(x-1.28,17.60)],-35.24,-35.16,'Y','cream')
disk(13,-35.25,14.35,1.79,'grey')
m.box((13,-35.30,14.32),(2.35,.15,1.38),'cream')
for x in (12.48,13.52):m.box((x,-35.40,14.43),(.34,.11,.32),'wire')
m.box((13,-35.40,14.02),(.65,.10,.16),'grey')
m.vertices=[(13+(x-13)*1.55,-34.8+(y+34.8)*1.55,9+(z-9)*1.30) for x,y,z in m.vertices]
finish(m)

m=part('Corner festoons')
for sx in (-1,1):
    for sy in (-1,1):
        ends=[(sx*48,sy*31.8),(sx*64.2,sy*26.6)]
        for x,y in ends:m.box((x,y,13.09),(.80,.83,8.20),'shadow')
        def cord(t):
            return (ends[0][0]+t*(ends[1][0]-ends[0][0]),ends[0][1]+t*(ends[1][1]-ends[0][1]),17.09-5*t*(1-t))
        for i in range(4):m.beam(cord(i/4),cord((i+1)/4),.14,.15,'wire')
        for i in range(5):
            x,y,z=cord((i+.5)/5)
            m.add([(x,y,z-.02),(x,y,z-1.65)]+[(x+.97*cos(k*pi/2),y+.97*sin(k*pi/2),z-.75) for k in range(4)],[(j,k+2,(k+1)%4+2) for j in (0,1) for k in range(4)],'gold')
finish(m)
scene.unit_settings.system='METRIC'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.shading.type='MATERIAL'
        sp.region_3d.view_distance=65;sp.region_3d.view_location=(1,-1,2)
        sp.region_3d.view_rotation=Vector((.28,-1,.63)).to_track_quat('Z','Y')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/HockeyRink_master.blend'))
report=audit(.002,True,'HockeyRink')
assert report['triangles_checked'] <= 2000 and report['overlapping_face_pairs'] == 0, report
(ROOT/'reports/surfaces.json').write_text(json.dumps(report,indent=2)+'\n')
# Staging is transient; not included in model counts.
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.world=bpy.data.worlds.new('Sky');scene.world.color=(.76,.80,.88)
scene.view_settings.view_transform='Khronos PBR Neutral'
bpy.ops.mesh.primitive_plane_add(size=190,location=(0,0,-.013))
light(scene.collection,'Sun',(-16,-24,35),(0,0,0),14500,18,(1,.94,.87))
light(scene.collection,'Fill',(12,5,29),(0,0,0),9500,22,(.83,.92,1))
camera(scene,scene.collection,(2,-55,30),(2,-1,2),ortho=55)
render(scene,ROOT/'preview','rink',(1200,760))
