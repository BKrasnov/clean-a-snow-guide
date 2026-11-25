"""Build six separate snow containers. Coordinates are local, Z up, front -Y."""
from math import cos, sin, pi, radians
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parents[1] / "starter-farmhouse/source"))
import build_farmhouse as farm


def ring(rx, ry, z, n=12, power=1, ripple=0, phase=0):
    def curve(v):
        return abs(v) ** power * (1 if v >= 0 else -1)
    pts = []
    for i in range(n):
        a = 2 * pi * (i + 0.5) / n
        r = 1 + ripple * sin(3*a + phase)
        pts.append((rx * curve(cos(a))*r, ry * curve(sin(a))*r, z))
    return pts


def loft(m, rings, colors):
    """Sealed shell through matching rings; cap ends belong to the same solid."""
    n = len(rings[0])
    vs = sum(rings, [])
    fs = [tuple(reversed(range(n)))]
    cols = [colors[0]]
    for j, color in enumerate(colors):
        for i in range(n):
            a, b = j*n+i, j*n+(i+1)%n
            fs.append((a,b,b+n,a+n))
            cols.append(color)
    fs.append(tuple(range(len(vs)-n,len(vs))))
    m.add(vs,fs,cols[0])
    m.colors[-len(fs):] = cols + [colors[-1]]


def tube(m, path, radii, color, sides=7):
    pts = [Vector(p) for p in path]
    rings = []
    for i, p in enumerate(pts):
        tangent = (pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        ref = Vector((0,1,0)) if abs(tangent.y)<.88 else Vector((1,0,0))
        u = tangent.cross(ref).normalized()
        v = tangent.cross(u).normalized()
        rings.append([tuple(p+radii[i]*(cos(2*pi*k/sides)*u+sin(2*pi*k/sides)*v)) for k in range(sides)])
    loft(m,rings,[color]*(len(path)-1))


def bucket(m):
    rings=[ring(r,r,z,12) for r,z in [(.63,0),(.69,.035),(.69,.12),(.665,.15),(.91,1.17),(.96,1.19),(.96,1.32),(.87,1.34),(.84,1.20),(.60,.08)]]
    loft(m,rings,['metal']*9)
    tube(m,[(-.94,0,1.22),(-.90,0,1.58),(-.76,0,1.99),(-.42,0,2.34),(.42,0,2.34),(.76,0,1.99),(.90,0,1.58),(.94,0,1.22)],[.042]*8,'metal',6)
    tube(m,[(-.41,0,2.34),(-.37,0,2.34),(.37,0,2.34),(.41,0,2.34)],[.09,.12,.12,.09],'wood',8)
    for s in (-1,1):
        tube(m,[(s*.88,0,1.22),(s*.98,0,1.22),(s*1.01,0,1.22)],[.10,.10,.07],'metal',8)


def chipbag(m):
    rings=[]
    for width,depth,z in [(.82,.14,0),(.80,.24,.10),(.67,.32,.27),(.69,.33,.40),(.77,.40,1.05),(.72,.34,1.45),(.72,.33,1.54),(.73,.32,1.66),(.78,.29,1.84),(.74,.265,1.84),(.65,.22,1.26),(.59,.20,.33),(.66,.12,.09)]:
        pts=ring(width,depth,z,12,.45)
        folded=[]
        for i,(x,y,_) in enumerate(pts):
            crown=.062*cos(i*pi) if z>1.80 else 0
            pleat=.055*sin(2.4*i+3.7*z) if .2<z<1.80 else 0
            folded.append((x,y+pleat,z+crown))
        # Fold the rear crimp directly into each ring, following the foil.
        a,b=folded[2],folded[3]
        seam=[]
        for t,offset in [(.35,0),(.43,.038),(.57,.034),(.65,0)]:
            seam.append(tuple(a[k]*(1-t)+b[k]*t+(offset if k==1 else 0) for k in range(3)))
        rings.append(folded[:3]+seam+folded[3:])
    colors=['red','red','trim','red','red','red','trim','red','metal','metal','metal','metal']
    first=len(m.colors)
    loft(m,rings,colors)
    for row in (2,6):
        for i in range(10):
            m.colors[first+1+row*16+i]='red'
    for x,z,ang in [(-.18,.90,-25),(.17,.78,-48)]:
        pts=[(x+.23*cos(a)*cos(radians(ang))-.13*sin(a)*sin(radians(ang)),z+.23*cos(a)*sin(radians(ang))+.13*sin(a)*cos(radians(ang))) for a in [2*pi*i/12 for i in range(12)]]
        m.prism(pts,-.409-(.018 if x>0 else 0),(-.29 if x>0 else -.32),'Y','gold')


    # Broader family-size packet, including the foil lining and front artwork.
    m.vertices = [(1.25*x, y, z) for x, y, z in m.vertices]


def sack(m):
    rr=[]
    for x,y,z,phase in [(.76,.61,0,0),(.92,.75,.13,.6),(.95,.74,.43,1),(.77,.65,.85,2),(.56,.50,1.28,.4),(.58,.51,1.41,.6),(.72,.61,1.51,.3),(.73,.60,1.68,.6),(.62,.51,1.72,.6),(.51,.43,1.31,.7),(.71,.54,.46,1),(.65,.49,.10,.4)]:
        rr.append(ring(x,y,z,12,.84,.075,phase))
    loft(m,rr,['wood']*(len(rr)-1))
    centers=ring(.598,.531,1.35,12,.84,.075,.53)
    rope=[]
    for x,y,z in centers:
        normal=Vector((x,y,0)).normalized()
        for k in range(6):
            a=2*pi*k/6
            rope.append((x+.069*cos(a)*normal.x,y+.069*cos(a)*normal.y,z+.067*sin(a)))
    faces=[(i*6+k,i*6+(k+1)%6,((i+1)%12)*6+(k+1)%6,((i+1)%12)*6+k)
           for i in range(12) for k in range(6)]
    m.add(rope,faces,'dark')
    for s in (-1,1):
        tube(m,[(0,-.50,1.38),(s*.07,-.58,1.32),(s*.12,-.64,1.16),(s*.17,-.71,.96)],[.073,.071,.045,.038],'dark',6)


def carrier(m):
    # Both die-cut handles grow out of the same wall as the bag. The inner
    # skin turns back around each opening to give the film a readable edge.
    n = 16
    levels = [(0,.63,.33),(.12,.79,.42),(.56,.85,.46),(.89,.74,.39),
              (1,.72,.37),(2,.70,.34),(3,.66,.28),
              (3,.62,.25),(2,.66,.31),(1,.68,.34),(.86,.67,.34),(.52,.76,.37),(.08,.57,.26)]
    rings = []
    for row,(level,w,d) in enumerate(levels):
        coords=[]
        for i in range(n):
            a=2*pi*i/n
            side=abs(cos(a))
            lift=max(0,(side-.57)/.43)
            if level in (1,2,3):
                z={1:.98+.26*lift,2:1.01+.66*lift,3:1.08+.84*lift}[level]
            else:
                z=level
            def curve(v): return abs(v)**.77 * (1 if v>=0 else -1)
            fold=1+.065*sin(3*a+level)*sin(pi*min(level,1))
            x=w*curve(cos(a))*fold
            y=d*curve(sin(a))*fold
            if row in (6,7):
                x-=.04*cos(a)*lift
            coords.append((x,y,z))
        rings.append(coords)
    vs=sum(rings,[])
    faces=[tuple(reversed(range(n))),tuple(range(len(vs)-n,len(vs)))]
    for j in range(len(levels)-1):
        for i in range(n):
            if j in (4,8) and i in (15,0,7,8):
                continue
            a,b=j*n+i,j*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
    for i in (15,0,7,8):
        k=(i+1)%n
        for a,b in [(4,9),(5,8)]:
            faces.append((a*n+i,a*n+k,b*n+k,b*n+i))
    for i in (15,1,7,9):
        faces.append(tuple(j*n+i for j in (4,5,8,9)))
    m.add(vs,faces,'glass')


def bin_(m):
    specs=[(.50,.46,.10),(.55,.52,.18),(.66,.62,1.68),(.72,.67,1.72),(.72,.67,1.86),(.64,.59,1.88),(.59,.56,1.58),(.46,.41,.21)]
    loft(m,[ring(x,y,z,12,.24) for x,y,z in specs],['metal']*(len(specs)-1))
    for s in (-1,1):
        tube(m,[(s*.45,.38,.239),(s*.58,.38,.239),(s*.64,.38,.239)],[.235,.235,.192],'outline',12)
        tube(m,[(s*.605,.38,.239),(s*.66,.38,.239)],[.094,.085],'metal',8)
    m.box((0,-.34,.061),(.66,.17,.122),'metal')
    tube(m,[(-.43,.64,1.868),(.43,.64,1.868)],[.074,.074],'metal',6)
    lid_start=len(m.vertices)
    loft(m,[ring(x,y,z,8,.21) for x,y,z in [(.73,.68,0),(.75,.70,.06),(.72,.67,.14)]],['metal']*2)
    for x in (-.38,.38):
        m.box((x,0,.145),(.085,1.05,.061),'metal')
    tip_lid(m,lid_start,.68,.63,1.89,42)
    m.box((0,.655,1.64),(.70,.16,.09),'metal')


def tip_lid(m,start,depth,pivot_y,pivot_z,angle):
    rot=Matrix.Rotation(radians(-angle),3,'X')
    for i in range(start,len(m.vertices)):
        x,y,z=m.vertices[i]
        m.vertices[i]=tuple(rot@Vector((x,y-depth,z))+Vector((0,pivot_y,pivot_z)))


def pizza(m):
    specs=[(.90,.86,0),(.95,.90,.035),(.95,.90,.255),(.91,.86,.27),(.89,.84,.08)]
    loft(m,[ring(x,y,z,12,.16) for x,y,z in specs],['wood']*4)
    start=len(m.vertices)
    loft(m,[ring(x,y,z,12,.16) for x,y,z in [(.93,.88,0),(.95,.90,.028),(.95,.90,.09),(.92,.87,.11)]],['wood']*3)
    m.box((0,-.87,.045),(.33,.13,.072),'wood')
    points=[(-.36,.19),(-.29,.28),(-.08,.34),(.16,.34),(.35,.28),(.39,.19),(.035,-.38),(-.045,-.38)]
    loft(m,[[(x,y,z) for x,y in points] for z in (.086,.143)],['red'])
    for px,py in [(-.16,.16),(.14,.15),(.01,-.09)]:
        loft(m,[[(x+px,y+py,h) for x,y,h in ring(.067,.067,z,8)] for z in (.125,.164)],['dark'])
    tip_lid(m,start,.88,.85,.26,67)


def bevel_rect(x, y, cut):
    return [(-x+cut,-y),(x-cut,-y),(x,-y+cut),(x,y-cut),
            (x-cut,y),(-x+cut,y),(-x,y-cut),(-x,-y+cut)]


def dustpan(m):
    # Rolled perimeter of the tray goes from the outer sole over the rim
    # to the inside floor. The front edge doubles as a shallow sweep ramp.
    outline=[(-.98,-.77),(-.74,-.79),(.74,-.79),(.98,-.77),
             (1,-.72),(.93,-.23),(.82,.44),(.77,.63),(.68,.71),
             (.45,.72),(-.45,.72),(-.68,.71),(-.77,.63),(-.82,.44),
             (-.93,-.23),(-1,-.72)]
    sections=[]
    for scale,zoffset,kind in [(.973,0,'base'),(1,.025,'base'),(1,-.018,'rim'),
                                (.984,0,'rim'),(.938,-.009,'rim'),(.915,-.047,'rim'),
                                (.89,.082,'floor'),(.81,.070,'floor')]:
        row=[]
        for x,y in outline:
            rise=max(0,min(1,(y+.78)/1.42))
            z=zoffset
            if kind=='rim':
                z+=.078+.77*rise
            elif kind=='floor':
                z-=.046*(1-rise)**3
            row.append((x*scale,y*scale,z))
        sections.append(row)
    loft(m,sections,['glass']*7)
    # Continuous bevels around the handgrip and its octagonal hanging hole.
    outer=bevel_rect(.22,.52,.074)
    hole=bevel_rect(.094,.094,.048)
    rows=[]
    for profile,scale,depth,center in [(outer,.92,-.10,1.26),(outer,1,-.072,1.26),
                                       (outer,1,.060,1.26),(outer,.92,.087,1.26),
                                       (hole,1.15,.087,1.55),(hole,1,.061,1.55),
                                       (hole,1,-.074,1.55),(hole,1.15,-.10,1.55)]:
        rows.append([(x*scale,.66+depth+(center+v*scale-.8)*.075,center+v*scale) for x,v in profile])
    faces=[(j*8+i,j*8+(i+1)%8,((j+1)%8)*8+(i+1)%8,((j+1)%8)*8+i)
           for j in range(8) for i in range(8)]
    m.add(sum(rows,[]),faces,'glass')


def suitcase_half(m,x,y,height,inside,upside_down=False):
    # The leather corner patches share the topology of the shell.
    rings=[]
    for s,z in [(.966,0),(1,.035),(1,height*.40),(1,height-.035),
                (.983,height),(.924,height-.010),(.897,inside)]:
        row=[]
        for px,py in bevel_rect(x,y,.095):
            row.append((px*s,py*s,z))
        rings.append(row)
    first=len(m.colors)
    loft(m,rings,['wood','wood','wood','wood','wood','trim'])
    for row in (0,1) if not upside_down else (0,1,2):
        for corner in (1,3,5,7):
            m.colors[first+1+row*8+corner]='dark'


def suitcase(m):
    suitcase_half(m,1.08,.72,.46,.075)
    for x in (-.64,.64):
        m.box((x,-.737,.34),(.205,.083,.197),'gold')
        m.box((x,-.783,.35),(.120,.027,.127),'lamp')
        tube(m,[(x-.10,.71,.416),(x+.10,.71,.416)],[.061,.061],'gold',8)
    grip=[(-.37,-.755,.32),(-.37,-.815,.295),(-.32,-.84,.18),
          (.32,-.84,.18),(.37,-.815,.295),(.37,-.755,.32)]
    tube(m,grip,[.046]*6,'dark',6)
    start=len(m.vertices)
    suitcase_half(m,1.075,.714,.195,.052,True)
    pocket=[(-.66,-.38),(.66,-.38),(.68,.27),(0,.19),(-.68,.27)]
    loft(m,[[(x,y,z) for x,y in pocket] for z in (.035,.102)],['trim'])
    for px in (-.53,-.32,-.11,.11,.32,.53):
        m.box((px,-.324,.106),(.101,.014,.023),'wood')
    rot=Matrix.Rotation(radians(83),3,'X')
    for i in range(start,len(m.vertices)):
        x,y,z=m.vertices[i]
        m.vertices[i]=tuple(rot@Vector((x,y+.714,z))+Vector((0,.734,.44)))


MODELS=[('MetalPail',bucket,.28),('ChipPacket',chipbag,.28),('BurlapSack',sack,.36),
        ('PlasticCarrier',carrier,.30),('WheelieBin',bin_,.43),('PizzaBox',pizza,.32),
        ('Dustpan',dustpan,.24),('Suitcase',suitcase,.37)]
if __name__=='__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    group=farm.collection('SnowStorage',scene.collection)
    farm.MODEL='SnowStorage'
    farm.COLORS.update({'gold':'#FFCE43','outline':'#2B1A11'})
    surf=farm.palette()
    for i,(name,build,size) in enumerate(MODELS):
        m=farm.Mesh(name+'_Body',group,surf)
        build(m)
        m.vertices=[tuple(size*v for v in co) for co in m.vertices]
        obj=m.object()
        obj.location=((i%4-1.5)*1.2,(i//4-.5)*1.40,0)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active
                sp.shading.type='MATERIAL'
                sp.region_3d.view_location=(0,0,.35)
                sp.region_3d.view_rotation=Vector((2,-10,6)).to_track_quat('Z','Y')
                sp.region_3d.view_distance=5.7
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'SnowStorage.blend'))
