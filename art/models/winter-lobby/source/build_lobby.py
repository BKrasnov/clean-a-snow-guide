"""Model the selected winter plaza in studs and export metric geometry."""
from pathlib import Path
from math import sin, cos, pi, tau, radians, ceil
import json
import sys
import random
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
ROOT = ASSET.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ASSET.parent / 'garden-plants/source'))
import plant_mesh
from plant_mesh import Plant

STUD = .28
V = Vector
COLORS = dict(snow='F3F6F5', shade='CDCDED', slate='B3C2D4', ice='A8DEE7',
              aqua='8BE0FF', sky='80A0E6', pine='54A577', spruce='3C8E63',
              mint='77C98D', wood='CD925C', oak='C28E49', bark='80401B',
              dark='2B1A11', cream='FFFDF5', metal='A0B0C4', gold='FFCE43',
              sun='FAD66E', orange='F8AA3C', red='D6392B', rose='FF5192',
              violet='BE63FF', blue='40A5FF', green='5BB830', skin='F2C29A')


def octagon(w,d,c):
    a,b=w/2,d/2
    return [(-a+c,-b),(a-c,-b),(a,-b+c),(a,b-c),(a-c,b),(-a+c,b),(-a,b-c),(-a,-b+c)]


def body(m,x,y,levels,colors):
    m.loft([[(x+i,y+j,z) for i,j in octagon(w,d,c)] for z,w,d,c in levels], colors)


def slab(m,x,y,z,w,d,h,c,col):
    bevel=min(.09,h*.2,c*.4)
    body(m,x,y,[(z,w-2*bevel,d-2*bevel,c),(z+bevel,w,d,c),
                (z+h-bevel,w,d,c),(z+h,w-2*bevel,d-2*bevel,c)],[col]*3)


def new(name):
    return Plant(name,collection,surface)


def finish(m,x=0,y=0,z=0,yaw=0):
    m.vertices=[V(p)*STUD for p in m.vertices]
    obj=m.object()
    obj.location=V((x,y,z))*STUD
    obj.rotation_euler.z=radians(yaw)
    return obj


def light_faces(obj,material,predicate):
    obj.data.materials.append(material)
    for face in obj.data.polygons:
        if predicate(face):
            face.material_index=1


def glow(name,hex_code,strength):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    rgb=[int(hex_code[k:k+2],16)/255 for k in (0,2,4)]
    color=[((v+.055)/1.055)**2.4 if v>.04045 else v/12.92 for v in rgb]+[1]
    mat.diffuse_color=color
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=color
    bsdf.inputs['Emission Color'].default_value=color
    bsdf.inputs['Emission Strength'].default_value=strength
    bsdf.inputs['Roughness'].default_value=.39
    return mat


def terrain():
    m=new('SnowGround')
    body(m,0,0,[(-1.42,98,88,5),(-1.08,99,89,5),(-.38,99,89,5),
                (-.23,98.7,88.7,5),(-.23,76.5,68.5,.5),(0,76,68,.5)],
         ['shade','slate','snow','snow','metal'])
    # Face of the courtyard inset inside the snowy ground.
    m.colors[-1]='metal'
    finish(m)


def pad(index,x,y):
    m=new(f'Station{index:02d}')
    body(m,0,0,[(.008,21.15,8.15,.34),(.09,21.3,8.3,.36),(.18,21.25,8.25,.34),
                (.22,21.07,8.07,.32),(.22,20.33,7.33,.22),(.225,20.23,7.23,.22)],
         ['slate','ice','cream','cream','ice'])
    m.colors[-1]='ice'
    # Tessellate the top itself into ice floes. Narrow glints share edges with
    # the body of each floe, so there are no decals lying on the ice surface.
    m.faces.pop();m.colors.pop()
    outline=[V((a,b)) for a,b in octagon(20.23,7.23,.22)]
    rng=random.Random(190+index%3)
    sites=[V((u+rng.uniform(-1.65,1.65),v+rng.uniform(-.66,.66)))
           for u in (-9,-5,-.6,3.6,8.5) for v in (-2.6,.65,2.9)]
    for i,site in enumerate(sites):
        poly=outline[:]
        for other in sites:
            if other==site:continue
            delta=other-site; mid=(other+site)/2
            result=[]
            for a,b in zip(poly,poly[1:]+poly[:1]):
                da,db=(a-mid).dot(delta),(b-mid).dot(delta)
                if da<=0:result.append(a)
                if (da<=0)!=(db<=0):result.append(a.lerp(b,da/(da-db)))
            poly=result
        center=sum(poly,V((0,0)))/len(poly)
        inset=[p.lerp(center,.017) for p in poly]
        n=len(poly)
        points=[(p.x,p.y,.225) for p in poly+inset]+[(center.x,center.y,.225)]
        faces=[];shades=[]
        for j in range(n):
            k=(j+1)%n
            faces.extend([(j,k,k+n,j+n),(j+n,k+n,2*n)])
            shades.extend(['ice','aqua'])
        m.face_colors(points,faces,shades)
    obj=finish(m,x,y)
    # Weld the tiled ice top and its clipped perimeter into a single manifold.
    # The long boundary edges are split at the Voronoi intersections below.
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000003)
    boundary=[e for e in bm.edges if len(e.link_faces)==1]
    for e in boundary:
        if not e.is_valid:continue
        a,b=e.verts;d=b.co-a.co
        if d.length_squared<1e-11:continue
        split=[]
        for v in bm.verts:
            if v in (a,b):continue
            fraction=(v.co-a.co).dot(d)/d.length_squared
            if .00001<fraction<.99999 and (v.co-a.co-fraction*d).length<.000003:split.append((fraction,v))
        for t,v in sorted(split,key=lambda item:item[0],reverse=True):
            previous_length=(e.other_vert(a).co-a.co).length
            _,added=bmesh.utils.edge_split(e,a,t*d.length/previous_length)
            e=next(edge for edge in a.link_edges if added in edge.verts)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000003)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
    bm.to_mesh(obj.data);bm.free()
    light_faces(obj,ice_light,lambda p: .215 < p.center.z/STUD < .221 and p.normal.z>.98)
    obj['role']='queue_pad'


def fence():
    def line(name,a,b,posts,first,last):
        m=new(name)
        d=V((b[0]-a[0],b[1]-a[1],0)); direction=d.normalized()
        pts=[V((*a,0))+d*i/posts for i in range(posts+1)]
        for i,p in enumerate(pts):
            if (i==0 and not first) or (i==posts and not last): continue
            x,y,_=p
            body(m,x,y,[(-.28,.91,.91,.09),(2.96,.91,.91,.09),(3.10,1.05,1.05,.10),
                        (3.28,.96,.96,.13)],['wood','oak','snow'])
            if i%2==0 or i in (0,posts):
                body(m,x,y,[(3.282,.82,.82,.10),(3.43,.91,.91,.10),(3.48,.70,.70,.09),
                            (4.34,.70,.70,.09),(4.42,1.03,1.03,.10),(4.60,.76,.76,.10)],
                     ['bark','oak','sun','bark','snow'])
                for dx,dy in ((-.35,-.35),(-.35,.35),(.35,-.35),(.35,.35)):
                    m.box((x+dx,y+dy,3.91),(.07,.07,.84),'oak')
        for p,q in zip(pts,pts[1:]):
            for h in (.79,2.00):
                start=p+direction*.458+V((0,0,h)); end=q-direction*.458+V((0,0,h))
                center=(start+end)/2
                m.box(center,(abs(end.x-start.x)+(.34 if d.x==0 else 0),
                              abs(end.y-start.y)+(.34 if d.y==0 else 0),.39),'oak')
        obj=finish(m)
        uv=obj.data.uv_layers.active
        light_faces(obj,amber_light,lambda p: (uv.data[p.loop_start].uv-V(surface[1]['sun'])).length<.0005)
    line('Fence_Back',(-38,34),(38,34),10,True,True)
    for s,n in [(-1,'Left'),(1,'Right')]:
        line('Fence_'+n,(38*s,-34),(38*s,34),9,True,False)
        line('Fence_Entry_'+n,(38*s,-34),(5.5*s,-34),4,False,True)
        m=new('OpenGate_'+n)
        for x in (-1.64,1.64):m.box((x,0,1.39),(.29,.38,2.78),'oak')
        for z in (.36,2.43):m.box((0,0,z),(2.98,.28,.26),'wood')
        for x in (-.87,-.29,.29,.87):m.box((x,0,1.395),(.21,.21,1.78),'oak')
        finish(m,s*5.95,-35.98,0,s*75)


def booth(m,awning=False):
    body(m,0,0,[(.012,8.7,5.55,.31),(.18,8.93,5.76,.38),(.43,8.88,5.71,.34),
                (.54,8.56,5.40,.30)],['slate','metal','cream'])
    m.box((0,1.92,4.02),(6.82,.40,6.94),'oak')
    for x in (-3.79,3.79):
        slab(m,x,.12,.545,.71,4.53,7.13,.13,'cream')
        slab(m,x,-1.62,.549,1,1.20,.49,.14,'metal')
    body(m,0,0,[(7.69,8.64,5.28,.36),(7.91,8.94,5.53,.45),
                (8.12,8.94,5.53,.45),(8.28,8.78,5.46,.43),
                (8.51,7.42,4.43,.68),(8.55,6.46,3.7,.65)],
         ['wood','cream','snow','snow','snow'])
    if awning:
        for j in range(7):
            x=(j-3)*.94
            m.prism([(-2.43,7.40),(-1.9,7.67),(-1.58,7.67),(-2.11,7.16),(-2.43,7.15)],
                    x-.46,x+.46,'X','pine' if j%2==0 else 'cream')


def gift(m,x,y,z,w,col,tie):
    h=w*.92
    # Gift ribbon inlays divide the paper into separate adjacent colored faces.
    for zl,zu,belt in [(0,h*.44,False),(h*.44,h*.57,True),(h*.57,h,False)]:
        for xl,xu,band in [(-w/2,-w*.1,False),(-w*.1,w*.1,True),(w*.1,w/2,False)]:
            m.box((x+(xl+xu)/2,y,z+(zu+zl)/2),(xu-xl-.012,w*.83,zu-zl-.012),tie if belt or band else col)
    for s in (-1,1):
        pts=[(x+s*.02*w,y,z+h+.06*w),(x+s*.40*w,y,z+h+.39*w),
             (x+s*.46*w,y,z+h+.53*w),(x+s*.24*w,y,z+h+.48*w),(x+s*.03*w,y,z+h+.10*w)]
        m.tube(pts,.075*w,tie,6)
    m.blob((x,y-.015,z+h+.10*w),(.14*w,.14*w,.14*w),tie)


def rewards():
    m=new('Rewards')
    booth(m,True)
    slab(m,0,-.35,.56,6.51,2.66,.50,.18,'wood')
    for x,y,z,w,c,r in [(-1.99,-.42,1.07,1.72,'red','gold'),(.10,-.34,1.07,1.90,'aqua','gold'),
                           (2.15,-.52,1.07,1.45,'sun','rose'),(0,0,8.56,2.49,'red','gold')]:
        gift(m,x,y,z,w,c,r)
    finish(m,-23.65,22.53,0,25)


def workbench():
    m=new('Upgrades')
    booth(m)
    for x in (-1.95,1.95):
        slab(m,x,-.32,.55,2.16,2.08,2.05,.12,'spruce')
        for z in (1.07,1.94):
            m.box((x,-1.39,z),(1.68,.08,.63),'mint')
            m.box((x,-1.46,z+.10),(.65,.055,.09),'cream')
    slab(m,0,-.28,2.63,6.48,2.46,.42,.14,'wood')
    slab(m,0,1.62,3.35,6.29,.27,3.49,.09,'wood')
    for x in (-2.68,2.68):
        for z in (3.65,6.53):
            m.blob((x,1.44,z),(.09,.07,.09),'metal',6,3)
    # Tool silhouettes mounted off the pegboard, including an open-end wrench.
    wrench=[(-.16,-.92),(.13,-.92),(.18,.42),(.48,.65),(.49,.98),
            (.24,1.14),(.18,.82),(-.05,.75),(-.27,.9),(-.25,1.19),(-.51,.99),(-.51,.66),(-.18,.38)]
    m.prism([(-1.59+a+.26*b,5.10+b) for a,b in wrench],1.17,1.42,'Y','metal')
    m.beam((-.29,1.26,4.24),(.18,1.26,5.71),.24,.24,'oak')
    m.box((.19,1.26,5.84),(.93,.35,.41),'dark')
    m.beam((1.45,1.20,4.4),(1.77,1.2,5.21),.24,.24,'orange')
    m.beam((1.79,1.2,5.25),(2.1,1.2,6.08),.115,.115,'metal')
    slab(m,1.79,-.35,3.07,1.51,1.19,.59,.13,'red')
    finish(m,-14.02,25.90,0,16)


def figure(m,x,y,z,h,coat,legs='dark'):
    s=h/5.1
    def part(cx,cy,cz,w,d,dh,color):
        slab(m,x+s*cx,y+s*cy,z+s*cz,s*w,s*d,s*dh,.085*s,color)
    for sign in (-1,1):
        part(sign*.43,0,.305,.78,.83,1.325,legs)
        part(sign*.43,-.1,0,.80,1.00,.30,'bark')
        part(sign*1.09,0,2.07,.48,.68,1.27,coat)
        part(sign*1.09,0,1.76,.46,.65,.29,'skin')
    part(0,0,1.65,1.65,.83,1.80,coat)
    part(0,-.455,2.98,.28,.07,.45,'sun')
    part(0,0,3.46,.57,.52,.20,'skin')
    part(0,0,3.67,1.20,.94,1.13,'skin')
    part(0,0,4.81,1.31,1.02,.29,'cream')


def classes():
    m=new('Classes')
    booth(m,True)
    for x,coat,legs in [(-1.59,'blue','dark'),(1.59,'red','slate')]:
        m.lathe(x,-.45,[(1.22,.55),(1.28,.64),(1.24,.83)],12,'metal')
        figure(m,x,-.43,.84,4.96,coat,legs)
    finish(m,23.65,22.53,0,-25)


def disk(m,x,z,y,r,depth,col,n=32):
    m.prism([(x+r*cos(tau*i/n),z+r*sin(tau*i/n)) for i in range(n)],y-depth/2,y+depth/2,'Y',col)


def wheel():
    x,y,yaw=14.02,25.90,-16
    m=new('PrizeWheel_Kiosk')
    booth(m)
    slab(m,0,-.18,.56,4.62,2.8,.40,.20,'bark')
    m.box((0,.61,2.96),(.70,.74,4.0),'metal')
    m.prism([(-.37,7.35),(.37,7.35),(0,6.79)],-1.24,-1.04,'Y','red')
    finish(m,x,y,0,yaw)
    m=new('PrizeWheel_Rotor')
    disk(m,0,0,0,2.93,.44,'oak',40)
    hues=['red','orange','gold','green','aqua','blue','violet','rose']
    for j,col in enumerate(hues):
        a=tau*j/8+.012
        b=tau*(j+1)/8-.012
        arc=[a+(b-a)*k/5 for k in range(6)]
        p=[(r*cos(t),r*sin(t)) for r,angles in [(2.62,arc),(.38,reversed(arc))] for t in angles]
        m.prism(p,-.29,-.224,'Y',col)
    for j in range(16):
        a=tau*j/16
        disk(m,2.78*cos(a),2.78*sin(a),-.26,.105,.07,'sun',8)
    disk(m,0,0,-.32,.43,.17,'gold',16)
    disk(m,0,0,-.43,.24,.04,'cream',12)
    # Local Y is the spindle axis; the object origin is the exact wheel center.
    oy=-.46
    finish(m,x-sin(radians(yaw))*oy,y+cos(radians(yaw))*oy,4.14,yaw)


def board(idx,x,h,accent):
    m=new(f'Leaderboard{idx:02d}')
    slab(m,0,0,.012,5.72,2.45,.75,.20,'spruce')
    slab(m,0,0,.77,5.49,1.23,h-.77,.18,'slate')
    # Ground-facing display, dark glass with seven separate baked rank rows.
    m.box((0,-.646,(h+.91)/2),(5.01,.055,h-1.16),'dark')
    m.box((0,-.702,h-1.00),(4.71,.045,.92),accent)
    star=[(cos(pi/2+i*pi/5)*(.33 if i%2==0 else .145),
           sin(pi/2+i*pi/5)*(.33 if i%2==0 else .145)) for i in range(10)]
    m.prism([(u-1.75,v+h-1.0) for u,v in star],-.76,-.729,'Y','cream')
    m.box((.32,-.745,h-1.0),(2.55,.028,.13),'cream')
    for j in range(7):
        z=1.51+j*(h-3.68)/6
        c='gold' if j==6 else 'slate'
        disk(m,-1.91,z+.11,-.696,.135,.035,c,8)
        m.box((-1.91,-.695,z-.10),(.40,.034,.14),c)
        w=1.13+(j*7+idx)%5*.18
        m.box((-1.33+w/2,-.695,z+.025),(w,.034,.115),'slate')
        for k in range(2+j%2):
            m.box((1.99-k*.19,-.696,z+.03),(.105,.033,.19),c)
    body(m,0,0,[(h+.012,5.56,1.39,.17),(h+.15,5.62,1.44,.18),
                (h+.29,5.39,1.20,.20)],['snow','snow'])
    finish(m,x,27.63)


def tree(i,x,y,height,r,seed):
    m=new(f'SnowFir{i:02d}')
    n=11 if seed%2 else 9
    phase=.37*seed
    # One continuous trunk-and-crown shell. Snow, bough tips and undersides
    # are adjacent faces along wavy rings; there is no second shell for snow.
    rings=[]; bands=[]
    def ring(rad,level,ripple=0,warp=0):
        return [(r*rad*(1+warp*cos(k*3+seed))*cos(k*tau/n+phase),
                 r*rad*(1+warp*cos(k*3+seed))*sin(k*tau/n+phase),
                 height*(level+ripple*(.55*cos(k*3+seed)+.45*sin(k*1.9)))) for k in range(n)]
    rings.extend([ring(.115,0),ring(.10,.18)])
    bands.append('bark')
    for layer,(radius,low,high) in enumerate([(1,.17,.46),(.78,.36,.65),(.57,.56,.81),(.36,.738,.997)]):
        rings.extend([ring(radius,low,.035,.12),ring(radius*.90,low+.046,.039,.10),
                      ring(radius*.74,low+.103,.067,.13),ring(radius*(.04 if layer==3 else .29),high,.0008,.04)])
        bands.extend(['spruce','pine' if layer%2==0 else 'spruce','mint' if layer==1 else 'pine','snow'])
    m.loft(rings,bands)
    finish(m,x,y,-.227,seed*17)


def build():
    global collection,surface,ice_light,amber_light
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene
    s.unit_settings.system='METRIC'
    collection=bpy.data.collections.new('WinterLobby')
    s.collection.children.link(collection)
    allowed={r['hex'][1:] for r in json.loads((ROOT/'art/palette.json').read_text(encoding='utf8'))['colors']}
    assert set(COLORS.values())<=allowed
    plant_mesh.COLORS=COLORS
    surface=plant_mesh.palette()
    ice_light=glow('Ice edge — snow light',COLORS['snow'],2.9)
    amber_light=glow('Lantern — warm light',COLORS['sun'],3.1)
    surface[0].name='WinterLobby_Palette'
    bpy.data.images['GardenPlants_Palette'].name='WinterLobby_Swatches'
    terrain(); fence()
    for j,y in enumerate((-20,-6.5,7)):
        for k,x in enumerate((-15,15)):
            pad(2*j+k+1,x,y)
    for i,(x,h,c) in enumerate([(-5.82,9.08,'blue'),(0,9.94,'gold'),(5.82,9.08,'red')],1):
        board(i,x,h,c)
    rewards(); workbench(); wheel(); classes()
    for i,(x,y,h,r,seed) in enumerate([(-44,-29,11.9,3.45,1),(-44.9,-1,15.4,4.1,2),
            (-44,27,14.6,3.7,3),(-27,40.6,16.9,4.6,4),(-6,40,14.7,3.9,2),
            (17,40.8,17.5,4.35,3),(41,40.2,13.6,3.7,1),(44.8,13,15.1,4.2,4),
            (44.8,-18.5,12.7,3.7,2),(27,-39.9,10.7,2.95,1)],1):tree(i,x,y,h,r,seed)
    for a in bpy.context.screen.areas:
        if a.type=='VIEW_3D':
            sp=a.spaces.active
            sp.shading.color_type='TEXTURE'
            sp.overlay.show_overlays=False
            sp.region_3d.view_rotation=V((.015,-1,.67)).to_track_quat('Z','Y')
            sp.region_3d.view_distance=33
            sp.region_3d.view_location=(0,0,1.05)
            sp.region_3d.view_perspective='ORTHO'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'WinterLobby.blend'),compress=True)
    (ASSET/'export').mkdir(exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSET/'export/WinterLobby.glb'),export_format='GLB',export_extras=True)


if __name__=='__main__':
    build()
