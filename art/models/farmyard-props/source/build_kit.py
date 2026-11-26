"""Snowy farm lobby props. Author in studs with front toward -Y; deliver in metres."""
import math
import os
from pathlib import Path
import random
import sys

import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ASSET.parent / "rustic-stalls/source"))
import build_stalls as stalls
from build_stalls import lobby as L

S = L.STUD
pi = math.pi
sin, cos = math.sin, math.cos


def timber(m, x, y, z, w, d, h, col, bevel=.09):
    if min(w,d,h)<.34:
        m.box((x,y,z),(w,d,h),col)
        return
    L.slab(m, x, y, z-h/2, w, d, h, min(bevel,w*.22,d*.22), col)


def lettering(m, words, x, y, z, w, h):
    curve = bpy.data.curves.new(words, 'FONT')
    curve.font, curve.body = font, words
    curve.align_x = curve.align_y = 'CENTER'
    curve.resolution_u, curve.extrude = 1, .017
    obj = bpy.data.objects.new(words, curve)
    bpy.context.scene.collection.objects.link(obj)
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000012)
    bmesh.ops.dissolve_limit(bm,angle_limit=.00005,verts=list(bm.verts),edges=list(bm.edges),use_dissolve_boundaries=False)
    bm.to_mesh(mesh)
    bm.free()
    pts = [v.co for v in mesh.vertices]
    bounds = [(min(p[k] for p in pts), max(p[k] for p in pts)) for k in (0,1)]
    s = min(l/(b-a) for l,(a,b) in zip((w,h),bounds))
    cx,cz = [(a+b)/2 for a,b in bounds]
    m.add([(x+(p.x-cx)*s,y-p.z*s,z+(p.y-cz)*s) for p in pts],
          [tuple(p.vertices) for p in mesh.polygons], 'cream')
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.curves.remove(curve)
    bpy.data.meshes.remove(mesh)


def fix_letter_caps(obj):
    # Fredoka has collinear points across the horizontal strokes of the T.
    # Rotate the cap diagonal to use the neighbouring triangle's off-line tip.
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3])
    for _ in range(12):
        flat=[f for f in bm.faces if len(f.verts)==3 and f.calc_area()<1e-8]
        if not flat: break
        for face in flat:
            if face.is_valid and face.calc_area()<1e-8:
                longest=max(face.edges,key=lambda e:e.calc_length())
                if longest.is_manifold:
                    bmesh.utils.edge_rotate(longest,True)
    bm.to_mesh(obj.data)
    bm.free()


def lamp(m, x, y, z, s=1):
    """Hanging carriage lantern with a pitched cap and amber glass."""
    levels = [(-.72,.44),(-.62,.62),(-.54,.49),(.35,.55),(.42,.72),(.56,.56),(.83,.19)]
    L.body(m,x,y,[(z+s*lo,s*a*2,s*a*1.48,s*.085) for lo,a in levels],
           ['dark','oak','sun','dark','bark','bark'])
    for side in (-1,1):
        for end in (-1,1):
            m.beam((x+side*s*.44,y+end*s*.32,z-s*.56),
                   (x+side*s*.50,y+end*s*.37,z+s*.39),s*.083,s*.093,'bark')
    m.tube([(x,y,z+.79*s),(x,y,z+1.07*s),(x,y+.64*s,z+1.07*s)],s*.09,'dark',8)


def roof_snow(m, profile, front, back, seed, snow=.67):
    """One folded timber roof and one continuous sculpted snow envelope."""
    rng = random.Random(seed)
    m.prism(profile+[(x,z-.38) for x,z in reversed(profile)], front, back,'Y','bark')
    # Cross sections have changing eaves and slightly scalloped ends. All rings
    # belong to one shell, including the underside that meets the roof.
    rows = 9
    rings = []
    for i in range(rows):
        t = i/(rows-1)
        ring = []
        for k,(x,z) in enumerate(profile):
            outer = k in (0,len(profile)-1)
            over = (1 if x>0 else -1)*rng.uniform(.22,.52) if outer else 0
            y = front+(back-front)*t
            if i in (0,rows-1):
                y += (-1 if i==0 else 1)*rng.uniform(.26,.57)
            ring.append((x+over,y,z+snow+rng.uniform(-.12,.12)))
        # Three points around either eave round over the snow cornice.
        ax,ay,az=ring[0]
        bx,by,bz=ring[-1]
        bottom=[(x*.987,y+.12*(1-2*t),z-snow-.14) for x,y,z in reversed(ring)]
        section=[(ax-.18,ay,az-.18)]+ring+[(bx+.18,by,bz-.18)]+bottom
        if i in (0,rows-1):
            edge=[(x,y+(.26 if i==0 else -.26),z+.24) for x,y,z in section]
            if i==0: rings.extend([section,edge])
            else: rings.extend([edge,section])
        else:
            rings.append(section)
    m.loft(rings,['snow']*(len(rings)-1))


def snowcap(m,x,y,z,w,d,seed):
    rng=random.Random(seed)
    n=2*max(3,round(w/2))
    edge=[(-w/2+w*i/n,-d/2+rng.uniform(-.14,.12)) for i in range(n+1)]
    edge += [(w/2-w*i/n,d/2+rng.uniform(-.1,.12)) for i in range(n+1)]
    undulate=[rng.uniform(-.11,.1) for p in edge]
    rings=[[(x+a*sx,y+b*sy,z+dz+v*amp) for (a,b),v in zip(edge,undulate)]
           for sx,sy,dz,amp in [(.986,.91,-.08,.85),(1,1,.16,1),(.992,.97,.39,.76),(.96,.72,.53,.55)]]
    m.loft(rings,['shade','snow','snow'])


def arch():
    m=L.new('StartGameArch')
    for sign in (-1,1):
        x=sign*23.3
        for i,(base,w,h,col) in enumerate([(0,2.7,.52,'slate'),(.50,2.45,.69,'metal'),(1.17,2.25,.53,'slate')]):
            L.slab(m,x,0,base,w,2.13-.07*i,h,.20,col)
        timber(m,x,0,7.05,1.67,1.55,10.74,'wood')
        m.beam((x-sign*.14,.08,8.3),(x-sign*3.4,.08,11.71),.69,.83,'oak')
        lamp(m,x,-1.14,9.26,1.10)
        L.disk(m,x,12.77,-.94,.31,.13,'metal',12)
    for i,col in enumerate(['bark','wood','oak']):
        timber(m,0,.02,11.37+i*.75,49.45-.16*i,1.71,.735,col,.16)
    timber(m,0,-.91,12.03,18.65,.58,2.51,'bark',.19)
    lettering(m,'START GAME',0,-1.27,12.03,16.65,1.65)
    snowcap(m,0,0,13.23,50.1,2.37,91)
    obj=L.finish(m)
    fix_letter_caps(obj)
    return obj


def map_frame(index):
    m=L.new(f'LaunchStation{index:02d}')
    for x in (-2.92,2.92):
        timber(m,x,.08,4.05,.48,.64,7.14,'wood')
        timber(m,x,.07,.32,.83,1.12,.64,'bark')
        for z in (1.32,7.07): L.disk(m,x,z,-.30,.102,.12,'metal',8)
    timber(m,0,.08,4.46,5.45,.47,5.26,'bark')
    for z in (1.23,7.40): timber(m,0,0,z,6.65,.81,.60,'oak')
    return L.finish(m,(index-3.5)*7.2,-.30)


def board(name, x):
    m=L.new(name)
    for side in (-1,1):
        timber(m,side*4.38,0,7.46,.62,.89,13.16,'wood')
        timber(m,side*4.38,0,.54,1.03,1.45,1.08,'earth')
    timber(m,0,.14,7.25,8.35,.66,12.96,'dark')
    for z in (1.00,13.82): timber(m,0,-.03,z,9.75,1.13,.62,'oak')
    snowcap(m,0,0,14.10,9.91,1.40,18)
    return L.finish(m,x,0)


def wheel():
    base=L.new('PrizeWheel')
    L.slab(base,0,0,0,9.13,4.26,.53,.38,'bark')
    L.slab(base,0,.015,.51,8.85,4.00,.26,.35,'wood')
    for side in (-1,1):
        base.beam((side*3.22,1.55,.72),(side*.40,1.40,7.63),.72,.75,'oak')
        base.beam((side*2.38,.91,.76),(side*.43,1.49,6.89),.52,.51,'earth')
    timber(base,0,1.02,7.76,1.08,.73,13.97,'wood')
    base.beam((0,1.35,7.82),(0,.515,7.82),.58,.63,'metal')
    base.tube([(0,1.07,14.43),(0,.91,14.89),(0,-.87,14.89)],.18,'bark',8)
    base.prism([(-.77,14.94),(.77,14.94),(.56,14.39),(0,13.40),(-.54,14.39)],-1.04,-.66,'Y','red')
    root=L.finish(base,43,-4.5)
    m=L.new('PrizeWheel_Dial')
    # Dial local origin is the axle. Sectors form a single closed rotor.
    n=64
    def ring(radius,y):
        return [(radius*sin(2*pi*i/n),y,radius*cos(2*pi*i/n)) for i in range(n)]
    rings=[ring(r,y) for r,y in [(5.91,.51),(6.14,.28),(6.14,-.22),(5.98,-.43),(5.54,-.45)]]
    m.loft(rings,['bark','wood','oak','gold'])
    m.faces.pop();m.colors.pop()
    cols=['gold','green','aqua','blue','violet','rose','red','orange']
    center=len(m.vertices)
    m.vertices.append((0,-.45,0))
    for i in range(n):
        m.faces.append((center,4*n+i,4*n+(i+1)%n))
        m.colors.append(cols[i//8])
    for i in range(20):
        a=2*pi*i/20
        L.disk(m,5.81*sin(a),5.81*cos(a),-.473,.146,.094,'cream',10)
    L.disk(m,0,0,-.528,.71,.20,'oak')
    L.disk(m,0,0,-.673,.56,.12,'gold')
    dial=L.finish(m)
    dial.parent=root
    dial.location=Vector((0,0,7.82))*S
    return root


def log_course(m,a,b,r,col):
    m.tube([a,b],r,col,8)


def window(m,x,y,z,w,h):
    timber(m,x,y,z,w+.48,.42,h+.48,'bark')
    timber(m,x,y-.245,z,w,.15,h,'sun')
    timber(m,x,y-.378,z,.16,.15,h+.04,'wood')
    timber(m,x,y-.423,z,w+.09,.11,.17,'wood')
    timber(m,x,y-.15,z-h/2-.25,w+.86,.79,.30,'oak')


def chair(m,x,y,z):
    for i in (-1,1):
        for j in (-1,1):
            m.box((x+i*.76,y+j*.61,z+.66),(.21,.24,1.32),'earth')
    timber(m,x,y,z+1.37,1.85,1.54,.23,'wood')
    for i in (-1,0,1):
        m.beam((x+i*.58,y+.61,z+1.48),(x+i*.58,y+.87,z+3.14),.42,.19,'oak')
    timber(m,x,y+.86,z+3.05,1.83,.27,.27,'wood')


def cottage():
    m=L.new('LogCabin')
    L.slab(m,0,0,0,17.48,14.38,.49,.22,'earth')
    for row in range(13):
        z=.83+row*.70
        span=8.91 if row%2 else 8.59
        col=['wood','oak','wood','earth','oak'][row%5]
        for y in (-6.72,6.72): log_course(m,(-span,y,z),(span,y,z),.48,col)
        span_y=7.28 if row%2==0 else 6.89
        for x in (-8.14,8.14):
            log_course(m,(x,-span_y,z+.025),(x,span_y,z+.025),.477,col)
    gable=[(-8.62,9.44),(0,16.53),(8.62,9.44)]
    for y in (-6.86,6.86):
        m.prism(gable,y-.24,y+.24,'Y','wood')
        for i in range(1,8):
            z=9.67+i*.78
            w=2*(16.52-z)*1.17
            timber(m,0,y+(-.32 if y<0 else .32),z,w,.24,.18,'oak')
    roof_snow(m,[(-9.51,9.09),(-7.8,10.76),(0,17.2),(7.8,10.76),(9.51,9.09)],-7.57,7.66,21)
    for k in range(7):
        timber(m,3.87,2.82,14.7+k*.53,2.24-(k%2)*.06,2.00,.52,'metal' if k%3 else 'slate')
    timber(m,3.87,2.82,18.12,2.63,2.38,.42,'slate')
    snowcap(m,3.87,2.82,18.31,2.78,2.54,55)
    window(m,0,-7.26,12.30,2.79,3.12)
    for x in (-5.36,5.36): window(m,x,-7.30,4.58,2.54,2.78)
    timber(m,0,-7.28,3.97,3.82,.49,6.69,'bark')
    for i in range(5):
        timber(m,(i-2)*.636,-7.56,3.96,.61,.19,6.17,'wood' if i%2 else 'oak')
    m.blob((1.13,-7.78,3.65),(.15,.16,.15),'gold')
    for j in range(8):
        timber(m,0,-7.63-j*.66,.71,18.13,.645,.55,'wood' if j%3 else 'oak')
    for s in (-1,1):
        x=s*8.05
        timber(m,x,-11.66,4.72,.71,.78,7.89,'wood')
        timber(m,x,-11.66,1.39,.93,.97,.84,'earth')
        m.beam((x,-11.53,6.61),(x,-10.29,8.19),.38,.39,'oak')
        m.beam((x,-11.64,6.83),(x-s*1.35,-11.64,8.09),.39,.38,'oak')
        for j in range(4):
            timber(m,s*(3.66+j*1.07),-11.71,1.91,.31,.32,1.80,'oak')
        timber(m,s*5.91,-11.76,2.91,4.95,.48,.35,'wood')
        timber(m,x,-9.63,2.94,.43,3.68,.35,'wood')
        lamp(m,x,-12.21,6.51,.83)
    # Awning is pitched along Y. Build in a local transverse section, then rotate.
    start=len(m.vertices)
    roof_snow(m,[(-3.02,8.36),(0,9.12),(2.47,9.46)],-9.16,9.16,36,.48)
    for i in range(start,len(m.vertices)):
        a,b,c=m.vertices[i];m.vertices[i]=(-b,a-9.81,c)
    L.slab(m,0,-13.34,0,6.81,1.51,.32,.14,'oak')
    L.slab(m,0,-12.75,.29,7.25,1.05,.37,.12,'wood')
    chair(m,-4.60,-9.21,.99)
    return L.finish(m,66,-33,0,-18)


def garage():
    m=L.new('BarnGarage')
    L.slab(m,0,0,0,18.15,16.22,.43,.19,'slate')
    # Open vehicle bay. Vertical plank skins are the walls themselves.
    for i in range(15):
        x=(i-7)*1.15
        m.box((x,7.42,4.78),(1.13,.55,8.74),'red')
        if abs(x)>5.28:
            m.box((x,-7.42,4.78),(1.13,.56,8.74),'red')
    for sign in (-1,1):
        for i in range(13):
            m.box((sign*8.47,(i-6)*1.15,4.78),(.55,1.13,8.76),'red')
        timber(m,sign*5.18,-7.72,4.81,.62,.73,8.79,'cream')
        m.beam((sign*4.93,-7.73,7.15),(sign*3.39,-7.73,8.87),.42,.48,'wood')
    prof=[(-8.68,8.92),(-5.55,14.57),(0,17.61),(5.55,14.57),(8.68,8.92)]
    for y in (-7.4,7.4): m.prism(prof,y-.31,y+.31,'Y','red')
    roof_snow(m,[(-9.36,8.68),(-6.06,14.94),(0,18.29),(6.06,14.94),(9.36,8.68)],-8.20,8.22,38,.74)
    timber(m,0,-7.69,8.95,10.67,.76,.56,'cream')
    timber(m,0,-8.04,10.09,11.76,.62,2.10,'bark')
    lettering(m,'GARAGE',0,-8.45,10.09,9.45,1.28)
    snowcap(m,0,-7.96,11.09,11.89,1.05,93)
    timber(m,0,-7.82,13.64,3.69,.37,3.68,'cream')
    timber(m,0,-8.06,13.64,3.07,.22,3.06,'red')
    for side in (-1,1):
        m.beam((-1.43,-8.23-.13*(side==1),13.64-side*1.43),(1.43,-8.23-.13*(side==1),13.64+side*1.43),.27,.12,'cream')
    lamp(m,0,-8.20,16.47,.75)
    for x in (-6.66,6.66):
        for z in (1.5,3.86,6.22):
            timber(m,x,3.16,z,2.62,6.52,.25,'oak')
            for j,col in enumerate(['orange','earth','blue']):
                timber(m,x,1.13+j*1.85,z+.69,1.80,1.52,1.11,col)
        for y in (.12,6.19):
            timber(m,x+.94,y,3.58,.27,.30,6.33,'bark')
    # Short firewood stack sits at the side of the garage.
    for row,count in enumerate((3,2,1)):
        for i in range(count):
            x=10.77+(i-(count-1)/2)*1.05
            y=-6.26+.073*i-.121*row
            z=.61+row*.91
            log_course(m,(x,y,z),(x,-2.41+i*.096+row*.139,z),.60,'bark')
            L.disk(m,x,z,y-.03,.47,.085,'oak',12)
    return L.finish(m,-56,-33,0,18)


def plow():
    m=L.new('GarageSnowplow')
    timber(m,0,0,1.65,3.83,5.87,.84,'dark')
    timber(m,0,-1.68,2.34,3.57,2.65,1.13,'gold')
    timber(m,0,1.04,2.49,3.69,2.85,1.14,'orange')
    timber(m,0,1.43,3.03,1.64,1.14,.44,'dark')
    timber(m,0,1.94,3.66,1.60,.32,1.15,'bark')
    for x in (-1.38,1.38):
        for y in (-.13,2.12):
            m.beam((x,y,2.91),(x*.86,y+.19,5.12),.19,.22,'dark')
        L.disk(m,x,2.62,-3.07,.28,.13,'cream',12)
    timber(m,0,1.10,5.23,3.52,3.30,.33,'gold')
    for s in (-1,1):
        for y in (-1.57,1.76):
            m.tube([(s*1.53,y,1.08),(s*2.11,y,1.08),(s*2.23,y,1.08)],[.96,1.04,.94],'dark',16)
            m.tube([(s*2.23,y,1.08),(s*2.29,y,1.08)],.53,'metal',12)
        m.beam((s*.91,-2.31,1.28),(s*1.69,-3.81,.76),.30,.32,'metal')
    m.prism([(-4.45,.19),(-4.29,.18),(-3.84,.73),(-3.67,1.48),(-3.68,1.89),(-3.91,1.89),(-3.98,1.16)],-2.99,2.99,'X','gold')
    m.prism([(-4.56,.12),(-4.27,.12),(-4.17,.28),(-4.49,.28)],-3.06,3.06,'X','metal')
    return L.finish(m)


def fence():
    m=L.new('LanternFence')
    for i,x in enumerate((-7.2,0,7.2)):
        h=4.03 if i==2 else 3.24
        timber(m,x,0,h/2,.82,.84,h,'wood')
        timber(m,x,0,h-.04,1.02,1.01,.27,'oak')
        if i==2:
            lamp(m,x,-.01,h+.90,1.10)
        else:
            snowcap(m,x,0,h+.075,1.17,1.16,54+i)
    for i in range(2):
        x=-3.60+7.20*i
        for z in (1.08,2.54):
            timber(m,x,.025,z,6.52,.43,.48,'oak')
        snowcap(m,x,.025,2.74,6.48,.61,12+i)
    return L.finish(m,-13,-49)


def main():
    global font
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    L.collection=bpy.data.collections.new('FarmyardProps')
    scene.collection.children.link(L.collection)
    L.plant_mesh.COLORS={**L.COLORS,'earth':'966240','grass':'96DC6A'}
    L.surface=L.plant_mesh.palette()
    L.surface[0].name='Farmyard | painted wood and snow'
    paths=sorted((Path(os.environ['LOCALAPPDATA'])/'Roblox/Versions').glob('*/content/fonts/FredokaOne-Regular.ttf'))
    font=bpy.data.fonts.load(str(paths[-1] if paths else Path('C:/Windows/Fonts/arialbd.ttf')))
    stalls.make_stalls(font)
    for name,x,y,yaw in [('Rewards',-49,-10,23),('Upgrades',-40,-3,19),('Classes',54.6,-10,-23)]:
        obj=bpy.data.objects[name]
        obj.location=Vector((x,y,0))*S
        obj.rotation_euler.z=math.radians(yaw)
    arch()
    for i in range(1,7): map_frame(i)
    board('LeaderboardLeft',-30.6)
    board('LeaderboardRight',30.6)
    wheel()
    barn=garage()
    vehicle=plow()
    vehicle.rotation_euler.z=barn.rotation_euler.z
    vehicle.location=barn.location+barn.rotation_euler.to_matrix()@Vector((0,-5.6,.445))*S
    cottage()
    entry=fence()
    far=entry.copy()
    far.name='LanternFenceRight'
    L.collection.objects.link(far)
    far.rotation_euler.z=pi
    far.location.x=-entry.location.x
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active
            sp.shading.color_type='TEXTURE'
            sp.overlay.show_overlays=False
            sp.region_3d.view_rotation=Vector((.03,-1,.50)).to_track_quat('Z','Y')
            sp.region_3d.view_location=(0,-5,1.5)
            sp.region_3d.view_distance=34
            sp.region_3d.view_perspective='ORTHO'
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'FarmyardProps.blend'),compress=True)
    dest=ASSET/'export'
    dest.mkdir(exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(dest/'FarmyardProps.glb'),export_format='GLB',export_animations=False)


if __name__=='__main__':
    main()
