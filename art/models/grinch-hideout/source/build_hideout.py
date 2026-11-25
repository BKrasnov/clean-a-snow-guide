"""Grinch's ice hideout. Local coordinates are metres, entry faces -Y."""
from math import sin, cos, pi, sqrt, radians
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ASSET.parent/'starter-farmhouse/source'))
import build_farmhouse as farm
from build_farmhouse import Mesh, collection

MODEL = 'GrinchHideout'
FLOOR = .12
N = 20
rng = random.Random(48)
colors = dict(ice='#A8DEE7', seam='#80A0E6', snow='#F3F6F5', shade='#CDCDED',
              wood='#CD925C', dark='#80401B', metal='#A0B0C4', ink='#2B1A11',
              red='#D6392B', emerald='#54A577', aqua='#8BE0FF', gold='#FFCE43',
              cream='#FFFDF5', green='#96DC6A', pine='#3C8E63', honey='#FAD66E')


def loft(m, rings, colors):
    n=len(rings[0])
    faces=[tuple(reversed(range(n)))]
    shades=[colors[0]]
    for j,c in enumerate(colors):
        for i in range(n):
            a=j*n+i
            b=j*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
            shades.append(c)
    faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    m.add(sum(rings,[]),faces,colors[0])
    m.colors[-len(faces):]=shades+[colors[-1]]


def blob(m,x,y,z,rx,ry,h,color='snow',n=12):
    # Two silhouette rings and a shallow crown; no hidden intermediate layers.
    rings=[]
    layers=[(.94,0),(1,.31),(.63,.90)] if h>.25 else [(1,.06),(.69,.89)]
    if h<=.25: n=min(n,6)
    for scale,height in layers:
        rings.append([(x+rx*scale*(1+.05*sin(3*a+x))*cos(a),
                       y+ry*scale*(1+.05*sin(3*a+x))*sin(a),z+h*(height+.046*cos(3*a+y)))
                      for a in (2*pi*i/n for i in range(n))])
    loft(m,rings,[('shade' if color=='snow' else color),color][:len(rings)-1])


def disk(m,x,y,z,rx,rz,depth,c,n=16):
    p=[(x+rx*cos(2*pi*i/n),z+rz*sin(2*pi*i/n)) for i in range(n)]
    m.prism(p,y-depth/2,y+depth/2,'Y',c)


def spike(m,x,y,z,r,h,c):
    n=5
    verts=[(x+r*cos(2*pi*i/n),y+r*sin(2*pi*i/n),z) for i in range(n)]
    verts.append((x+.19*r,y-.07*r,z-h))
    m.add(verts,[tuple(range(n))]+[(i,(i+1)%n,n) for i in range(n)],c)


def sign(m):
    x,y,z=0,-3.55,3.78
    for s in (-1,1):
        m.beam((s*.44,y+.11,z),(s*1.72,y+.14,z-.35),.24,.20,'dark')
        for t in (.85,1.55): disk(m,s*t,y-.017,z-.10-(t-.85)*.21,.062,.062,.048,'metal',6)
    disk(m,x,y,z,.77,.76,.22,'dark',18)
    disk(m,x,y-.113,z,.68,.67,.032,'wood',18)
    disk(m,x,y-.14,z,.608,.60,.045,'cream',18)
    fy=y-.193
    outline=[(-.50,.15),(-.31,.13),(-.29,.29),(-.12,.37),(.13,.38),(.31,.29),(.35,.13),(.51,.16),(.45,-.02),(.34,-.08),(.30,-.22),(.17,-.31),(0,-.36),(-.19,-.30),(-.31,-.22),(-.34,-.09),(-.45,-.02)]
    def badge(poly,depth,c):
        m.prism([(x+a*1.16,z+b*1.16) for a,b in poly],fy-depth-.022,fy-depth,'Y',c)
    badge(outline,0,'green')
    badge([(-.30,.25),(-.23,.37),(-.08,.43),(.14,.42),(.29,.32),(.31,.24),(.19,.20),(.08,.24),(-.06,.20),(-.17,.24)],.026,'snow')
    for s in (-1,1):
        disk(m,s*.151,fy-.05,z+.045,.104,.105,.025,'cream',12)
        disk(m,s*.125,fy-.073,z+.037,.037,.048,.016,'ink',10)
        badge([(s*.27,.17),(s*.25,.099),(s*.073,.052),(s*.06,.116)],.086,'dark')
    badge([(-.21,-.081),(-.10,-.10),(.086,-.10),(.21,-.067),(.16,-.191),(.055,-.243),(-.07,-.225),(-.16,-.18)],.032,'ink')
    for s in (-1,1):
        badge([(s*.145,-.10),(s*.082,-.114),(s*.12,-.165)],.062,'cream')


def lock(m,x,y,z,s):
    shackle=[(x+s*r*cos(i*pi/8),z+s*(.155+r*sin(i*pi/8)))
             for r,indices in [(.23,range(9)),(.147,range(8,-1,-1))] for i in indices]
    m.prism(shackle,y-.030*s,y+.034*s,'Y','metal')
    m.box((x,y-.036,z),(.54*s,.18*s,.39*s),'gold' if s<.9 else 'metal')
    key=[(-.022,.0),(-.046,.025),(-.045,.061),(-.019,.083),(.020,.083),(.046,.062),
         (.047,.026),(.022,.0),(.043,-.076),(-.043,-.076)]
    front=y-.036-.09*s
    m.prism([(x+u*s,z+v*s) for u,v in key],front-.016,front+.009,'Y','ink')


def footprint(i):
    a=2*pi*i/N
    def power(v,p): return (1 if v>=0 else -1)*abs(v)**p
    x=4.34*power(sin(a),.79)*(1+.028*sin(3*a))
    y=-3.43*power(cos(a),.77)*(1+.025*cos(5*a))
    if i%N in (1,N-1): x,y=(1 if i%N==1 else -1)*1.94,-3.13
    return x,y


def shell(m):
    # One continuous wall from jamb to jamb. Recessed joints wrap both wall faces.
    verts=[]; faces=[]; shades=[]
    def vertex(co):
        verts.append(Vector(co));return len(verts)-1
    def face(indices,c):
        faces.append(indices);shades.append(c)
    strips=[]
    for side in (0,1):
        bands=[]
        for j,(base,z) in enumerate([(1.04,.026),(1.01,1.17),(.965,2.31),(.88,3.44)]):
            row=[]
            for i in range(1,N):
                x,y=footprint(i)
                r=base+.018*sin(i*1.9+j)
                level=z+(.17*sin(i*1.61+j*.82) if j else 0)
                dx=.14*sin(i*1.78+j*2.2) if j in (1,2) else 0
                if i in (1,N-1): r,level,dx=1,z,0
                if side: r-=.095
                row.append(vertex((x*r+dx+(0 if i in (1,N-1) else (.36 if j%2 else -.18)*cos(2*pi*i/N)),y*r+(0 if i in (1,N-1) else (.36 if j%2 else -.18)*sin(2*pi*i/N)),level)))
            bands.append(row)
        strips.append(bands)
    opening=(16,1)
    for s,bands in enumerate(strips):
        for j in range(3):
            for k in range(N-2):
                if (k,j)==opening: continue
                quad=[bands[j][k],bands[j][k+1],bands[j+1][k+1],bands[j+1][k]]
                if s and (k+j)%2==0:
                    face(quad,'aqua' if k%3 else 'ice');continue
                center=sum((verts[v] for v in quad),Vector())*.25
                no=Vector((center.x,center.y,0)).normalized()*(.10 if not s else -.055)
                inner=[vertex(verts[v].lerp(center,.135)+no) for v in quad]
                for a in range(4): face((quad[a],quad[(a+1)%4],inner[(a+1)%4],inner[a]),'seam' if a in (0,3) else 'ice')
                face(inner,'aqua' if (k+2*j)%4!=1 else 'ice')
    outer,inner=strips
    for j in (0,3):
        for k in range(N-2): face((outer[j][k],outer[j][k+1],inner[j][k+1],inner[j][k]),'ice')
    for k in (0,N-2):
        for j in range(3):face((outer[j][k],outer[j+1][k],inner[j+1][k],inner[j][k]),'ice')
    k,j=opening
    points=[(j,k),(j,k+1),(j+1,k+1),(j+1,k)]
    for a,b in zip(points,points[1:]+points[:1]):
        face((outer[a[0]][a[1]],outer[b[0]][b[1]],inner[b[0]][b[1]],inner[a[0]][a[1]]),'seam')
    m.add(verts,faces,'ice');m.colors[-len(faces):]=shades


def arch_top(x):
    return 1.55+1.55*sqrt(max(0,1-(x/1.60)**2))


def entrance(m):
    # Stone voussoirs make an actual opening below the crown.
    for i in range(11):
        a=pi*i/11+.005; b=pi*(i+1)/11-.005
        poly=[(r*cos(t),1.55+r*.97*sin(t)) for r,t in [(1.60,a),(1.60,b),(2.00,b),(2.00,a)]]
        m.prism(poly,-3.41+.015*sin(i*2),-2.92+.014*i,'Y','ice')
    for s in (-1,1):
        m.box((s*1.804,-3.149,.789),(.401,.506,1.548),'ice')
    # Bridge from the round opening to the roof. Keep the lower surface behind the stone trim.
    arc=[(1.90*cos(i*pi/14),1.55+1.77*sin(i*pi/14)) for i in range(15)]
    m.prism(arc+[(-1.94,3.60),(0,3.91),(1.94,3.60)],-3.115,-2.79,'Y','ice')
    sign(m)


def hinged_gate(m):
    for i in range(7):
        a=-1.55+i*(3.10/7)+.009; b=a+3.10/7-.018
        m.prism([(a,.139),(b,.139),(b,arch_top(b)-.025),(a,arch_top(a)-.046)],-3.234-.009*sin(i),-3.06,'Y','wood' if i%3 else 'dark')
    for i,(z,slope) in enumerate([(.87,-.045),(2.04,.10)]):
        m.beam((-1.48,-3.264,z-1.48*slope),(1.46,-3.264,z+1.46*slope),.225,.122,'metal')
        for x in (-1.22,0,1.19):
            disk(m,x,-3.347,z+x*slope,.072,.072,.055,'metal',6)
    lock(m,.43,-3.413,1.49,1.08)
    hinge=Vector((-1.57,-3.18,0))
    m.vertices=[Vector(v)-hinge for v in m.vertices]
    ob=m.object();ob.location=hinge
    ob.rotation_euler.z=0;ob.keyframe_insert(data_path='rotation_euler',frame=1)
    ob.rotation_euler.z=radians(-108);ob.keyframe_insert(data_path='rotation_euler',frame=36)
    return ob


def roof(m):
    rings=[]
    for radius,h,wave in [(.847,3.40,.08),(.933,3.51,.16),(.944,3.66,.19),(.83,3.94,.12),(.59,4.12,.12),(.28,4.26,.06)]:
        rings.append([(x*radius,y*radius,h+wave*sin(i*1.73)) for i,(x,y) in enumerate(footprint(k) for k in range(N))])
    loft(m,rings,['seam','shade','snow','snow','snow'])
    blob(m,-.35,-1.77,3.85,2.42,1.61,.72,'snow',13)
    for x,y,z in [(-2.84,-1.85,3.40),(2.7,-1.80,3.48),(-3.45,.54,3.52)]:
        blob(m,x,y,z,.95,.82,.26,'snow',6)
    for i in (2,4,6,7,8,9,10,11,12,13,14,16,18):
        x,y=footprint(i)
        spike(m,.77*x,.77*y,3.46,.135+.04*sin(i),.72+.21*sin(i*2),'snow')


def turret(m):
    rows=[]
    for radius,z in [(.85,.08),(1.02,.67),(.78,2.47),(.84,3.37),(.80,4.40),(.83,4.48),(.92,4.91),(1.14,4.95),(1.13,5.19),(.91,5.45),(.50,5.58)]:
        row=[]
        for i in range(11):
            a=i*2*pi/11
            r=radius*(1+.042*sin(3*a+.3))
            row.append((3.04+.112*z+r*cos(a),1.47+.026*z+r*sin(a),z+.043*cos(3*a+.4)))
        rows.append(row)
    loft(m,rows,['ice','ice','seam','ice','seam','ice','seam','shade','snow','snow'])
    for i in range(10):
        a=2*pi*i/10
        spike(m,3.60+1.10*cos(a),1.60+1.10*sin(a),5.09,.175+.048*cos(i),.71+.25*sin(i*2),'ice')
    m.beam((3.03,.65,3.72),(4.12,.76,4.04),.22,.14,'wood')
    m.vertices=[(x+.23,y+.97,z) for x,y,z in m.vertices]


def bow(m,x,y,z,s):
    for side in (-1,1):
        outer=[(0,0),(.07,.23),(.26,.42),(.43,.39),(.46,.24),(.31,.09)]
        inner=[(.09,.075),(.13,.20),(.27,.32),(.34,.29),(.35,.23),(.28,.15)]
        rings=[[(x+side*u*s,y+d*s,z+v*s) for u,v in prof] for prof,d in [(outer,-.07),(outer,.07),(inner,.07),(inner,-.07)]]
        faces=[(j*6+i,j*6+(i+1)%6,((j+1)%4)*6+(i+1)%6,((j+1)%4)*6+i) for j in range(4) for i in range(6)]
        m.add(sum(rings,[]),faces,'cream')
    m.box((x,y-.025,z+.075*s),(.18*s,.19*s,.15*s),'cream')


def present(m,x,y,z,s,c):
    m.box((x,y,z+.49*s),(.92*s,.81*s,.98*s),c)
    m.box((x,y,z+.98*s),(.99*s,.88*s,.15*s),c)
    for sign in (-1,1):
        m.box((x,y+sign*.405*s,z+.48*s),(.18*s,.025*s,.95*s),'cream')
        m.box((x,y+sign*.443*s,z+.985*s),(.195*s,.019*s,.146*s),'cream')
    m.box((x,y,z+1.062*s),(.159*s,.830*s,.024*s),'cream')
    for sign in (-1,1):
        blob(m,x+sign*.28*s,y+.034*s,z+1.041*s,.20*s,.39*s,.065*s,'snow',7)
    bow(m,x,y,z+1.067*s,s)
    if c=='aqua':
        for i in range(2):
            m.lathe(x+.28*s,y-.411*s,[(.083*s,z+(.86+i*.027)*s),(.087*s,z+(.881+i*.027)*s)],8,'gold')


def interior(group,surface):
    def part(name):return Mesh(name,group,surface)
    stage=part('Frozen dais')
    stage.prism([(-3.16,1.43),(-2.99,1.25),(2.96,1.28),(3.11,1.56),(2.63,2.75),(-2.60,2.75)],.08,.37,'Z','snow')
    stage.object()
    for idx,(x,c) in enumerate([(-2.06,'red'),(-.70,'emerald'),(.68,'aqua'),(2.05,'gold')]):
        m=part('Gift '+c)
        present(m,x,1.99+.055*cos(idx),.355,1.12,c)
        m.object()
    fence=part('Locked gift fence')
    for i,x in enumerate([-2.92,-1.46,0,1.46,2.92]):
        h=1.19+.042*cos(i)
        fence.box((x,1.105,h/2+.093),(.175,.22,h),'dark')
        blob(fence,x,1.105,h+.065,.135,.16,.071,'snow',7)
        disk(fence,x,.970,1.09,.063,.063,.064,'metal',6)
    for i in range(4):
        a=-2.92+1.46*i
        for ya,z1,z2 in [(1.065,.43,1.12),(1.185,1.12,.43)]:
            fence.beam((a+.027,ya,z1),(a+1.438,ya+.013,z2),.16,.090,'wood')
    lock(fence,0,.883,.89,.82);fence.object()
    throne=part('Empty ice throne')
    cx,cy=3.04,-.08
    throne.box((cx,cy,.66),(.98,.88,.23),'ice')
    blob(throne,cx,cy,.744,.52,.45,.094,'snow',9)
    for dx in (-.45,.45):
        for dy in (-.33,.33):
            throne.lathe(cx+dx,cy+dy,[(.168,.105),(.142,.59),(.134,.93),(.088,1.025)],6,'ice')
        blob(throne,cx+dx,cy,.982,.16,.44,.091,'snow',8)
    for dx,h in [(-.35,1.56),(0,1.90),(.31,1.675)]:
        throne.lathe(cx+dx,cy+.41,[(.23,.51+.058*dx),(.24,h-.24),(.052,h)],6,'ice')
        blob(throne,cx+dx,cy+.41,h-.08,.135,.13,.105,'snow',7)
    throne.object()
    drift=part('Snowballs near the left wall')
    for x,y,z,r in [(-3.07,.80,.125,.28),(-2.70,.83,.129,.25),(-2.87,.85,.46,.22)]:
        blob(drift,x,y,z,r,r,1.8*r,'snow',5)
    drift.object()
    for i,(x,y) in enumerate([(-2.58,.67),(0,2.67),(2.60,.64)]):
        lamp=part('Ornament lantern '+str(i+1))
        lamp.beam((x-.27,y,3.27),(x+.31,y+.031,3.38),.13,.18,'dark')
        lamp.box((x,y,3.11),(.048,.06,.42),'wood')
        lamp.lathe(x,y,[(.10,2.82),(.215,2.90),(.255,3.01),(.083,3.174)],8,'gold')
        lamp.object()
    for side in (-1,1):
        win=part('Ice lattice '+str(side))
        x,y=side*3.64,.74
        pattern=[(-.49,1.86),(-.25,1.48),(.25,1.48),(.49,1.86),(.25,2.31),(-.25,2.31)]
        win.prism(pattern,x-.065,x+.065,'X','seam')
        win.prism([(u*.78,1.90+(z-1.90)*.76) for u,z in pattern],min(x-side*.08,x-side*.105),max(x-side*.08,x-side*.105),'X','aqua')
        for a,b in [((x-side*.12,-.36,1.88),(x-side*.12,.36,1.88)),((x-side*.13,0,1.60),(x-side*.13,0,2.20))]:
            win.beam(a,b,.046,.056,'seam')
        win.object()


def scenery(group,surface):
    m=Mesh('Snow at the foundation',group,surface)
    for i in (2,3,5,7,10,12,15,17,18):
        x,y=footprint(i)
        # One faceted rock, with snow confined to the upper rings.
        xx,yy=x*1.02,y*1.02
        h=.46+.17*cos(2*i)
        rings=[[(xx+.49*r*cos(a),yy+.388*r*sin(a),z+.021*cos(2*a+i))
                for a in (2*pi*j/6 for j in range(6))]
               for r,z in [(.94,.043),(1,h*.53),(.81,h*.82),(.41,h)]]
        loft(m,rings,['ice','shade','snow'])
    # A shallow festive relief sits on the inner sill of the left-hand fissure.
    x,y=-2.99,-2.38
    m.box((x,y,1.53),(.62,.38,.54),'gold')
    m.box((x,y-.030,1.79),(.68,.41,.105),'honey')
    m.box((x,y-.216,1.56),(.105,.027,.49),'cream')
    for side in (-1,1):
        m.prism([(x,1.85),(x+side*.14,2.03),(x+side*.26,2.01),(x+side*.25,1.91),(x+side*.10,1.85)],y-.07,y+.074,'Y','cream')
    for i in (3,7,13,17):
        x,y=footprint(i)
        a=2*pi*i/N
        vx,vy=cos(a)*.51,sin(a)*.51
        m.beam((x-vx,y-vy,1.75),(x+vx,y+vy,2.12),.18,.23,'wood')
    m.object()


def guards(scene):
    # Share one packed project elf mesh between the three NPC preview placements.
    source=ASSET.parent/'elf'
    with bpy.data.libraries.load(str(source/'source/Elf_master.blend'),link=False) as (src,dst):
        dst.objects=['Elf_Body']
    elf=dst.objects[0]
    atlas=bpy.data.images['Elf_Palette']
    atlas.filepath=str(source/'textures/Elf_Palette.png')
    atlas.reload();atlas.pack()
    # Pose the local copy of the approved elf mesh. Its sleeve and mitten islands
    # have independent vertices, so their rotations leave the face and tunic intact.
    mesh=elf.data
    adjacent=[set() for _ in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices;adjacent[a].add(b);adjacent[b].add(a)
    unseen=set(range(len(adjacent)))
    while unseen:
        stack=[unseen.pop()];island=[]
        while stack:
            k=stack.pop();island.append(k)
            fresh=adjacent[k]&unseen;unseen-=fresh;stack.extend(fresh)
        pts=[mesh.vertices[k].co for k in island]
        center=sum(pts,Vector())/len(pts)
        if abs(center.x)>.19 and .54<center.z<.74 and max(v.z for v in pts)<.76:
            side=1 if center.x>0 else -1
            pivot=Vector((side*.112,0,.625))
            rot=Matrix.Rotation(radians(54*side),3,'Y') @ Matrix.Rotation(radians(-22*side),3,'Z')
            for k in island:mesh.vertices[k].co=pivot+rot@(mesh.vertices[k].co-pivot)
    group=collection('NPC preview - three guards',scene.collection)
    for i,(x,y,angle) in enumerate([(-2.32,.49,8),(-.60,.54,-7),(2.03,.48,-12)]):
        ob=elf if i==0 else elf.copy()
        ob.name='Guard %02d'%(i+1)
        group.objects.link(ob)
        ob.location=(x,y,FLOOR);ob.rotation_euler.z=radians(angle)
        ob.scale=(.88,)*3


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC'
    group=collection(MODEL,scene.collection)
    structure=collection('Ice structure',group)
    top=collection('Removable roof',group)
    inside=collection('Treasure hall',group)
    farm.COLORS=colors;farm.MODEL=MODEL
    surface=farm.palette()
    for name,grp,fn in [('Glacial walls',structure,shell),('Gate arch and sign',structure,entrance),
                        ('Snow roof',top,roof),('Leaning ice tower',structure,turret)]:
        m=Mesh(name,grp,surface);fn(m);m.object()
    floor=Mesh('Snow floor',structure,surface)
    floor.prism([(x*1.04,y*1.04) for x,y in [footprint(i) for i in range(N)]],0,FLOOR,'Z','snow')
    # Replace the flat top cap with a continuous faceted snow surface.
    floor.faces.pop(1);floor.colors.pop(1)
    start=len(floor.vertices)
    for i in range(N):
        x,y=footprint(i)
        radius=.29+.12*sin(i*2.3)
        floor.vertices.append((x*radius,y*radius,FLOOR))
    for i in range(N):
        j=(i+1)%N
        floor.faces.extend([(N+i,N+j,start+i),(N+j,start+j,start+i)])
        floor.colors.extend([('shade' if i%4==0 else 'snow'),('shade' if i%5==2 else 'snow')])
    floor.faces.append(tuple(range(start,start+N)));floor.colors.append('snow')
    floor.object()
    hinged_gate(Mesh('Entrance gate - hinged',structure,surface))
    interior(inside,surface);scenery(structure,surface);guards(scene)
    scene.frame_end=36;scene.frame_set(1)
    scene.timeline_markers.new('Locked exterior',frame=1)
    scene.timeline_markers.new('Open entrance',frame=36)
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.shading.type='MATERIAL'
                sp.region_3d.view_location=(0,0,2.0);sp.region_3d.view_distance=15.2
                sp.region_3d.view_rotation=Vector((2,-12,4)).to_track_quat('Z','Y')
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'GrinchHideout_master.blend'))


if __name__=='__main__':
    main()
