"""Build the two-ended snow processor in studs. Blender and GLB are metric."""
import json
from math import cos, sin, pi, tau
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
ROOT=ASSET.parents[2]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ASSET.parent/'garden-plants/source'))
from plant_mesh import Plant

STUD=.28
DRUM_Y=4.48
LEVELS={'Lower':1.68,'Upper':3.99}
ROTOR_NAMES=[f'{end}_{level}' for end in ('Front','Rear') for level in LEVELS]
COLORS={'ice':'A8DEE7','cyan':'8BE0FF','blue':'40A5FF','cream':'FFFDF5','silver':'A0B0C4',
        'light':'B3C2D4','dark':'2B1A11','gold':'FFCE43','orange':'F8AA3C','red':'D6392B'}

def palette():
    allowed={c['hex'].lstrip('#').upper() for c in json.loads((ROOT/'art/palette.json').read_text(encoding='utf-8-sig'))['colors']}
    assert set(COLORS.values())<=allowed
    image=bpy.data.images.new('ProcessorTower_Palette',32,8,alpha=False)
    shades=list(COLORS.values())
    pixels=[]
    for y in range(8):
        for x in range(32):
            c=shades[min(y//4*8+x//4,len(shades)-1)]
            pixels.extend([int(c[i:i+2],16)/255 for i in (0,2,4)]+[1])
    image.pixels.foreach_set(pixels)
    image.pack()
    mat=bpy.data.materials.new('M_ProcessorTower')
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    tex=nodes.new('ShaderNodeTexImage')
    tex.image=image
    tex.interpolation='Closest'
    nodes.active=tex
    shader=nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value=.67
    mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    return mat,{k:((i%8+.5)/8,(i//8+.5)/2) for i,k in enumerate(COLORS)}

class Skin:
    def __init__(self,m):
        self.mesh=m
        self.v=[]; self.f=[]; self.c=[]
    def ring(self,points):
        a=len(self.v)
        self.v.extend(Vector(p) for p in points)
        return list(range(a,len(self.v)))
    def face(self,ids,shade):
        self.f.append(tuple(ids));self.c.append(shade)
    def join(self,a,b,shade):
        for k in range(len(a)):
            j=(k+1)%len(a)
            self.face((a[k],a[j],b[j],b[k]),shade if isinstance(shade,str) else shade[k])
    def finish(self):
        self.mesh.face_colors(self.v,self.f,self.c)

def clipped(w,h,c):
    a,b=w/2,h/2
    return [(-a+c,-b),(a-c,-b),(a,-b+c),(a,b-c),(a-c,b),(-a+c,b),(-a,b-c),(-a,-b+c)]

def ring_xy(w,d,z,c):
    return [(a,b,z) for a,b in clipped(w,d,c)]

def mouth_ring(w,lo,hi,c,y):
    return [(a,y,b+(lo+hi)/2) for a,b in clipped(w,hi-lo,c)]

def body(m):
    s=Skin(m)
    profiles=[(-6.06,8.35,.065,5.79),(-5.92,8.58,0,5.91),(-5.50,8.58,0,5.91),
              (-5.38,8.20,.075,5.72),(5.38,8.20,.075,5.72),(5.50,8.58,0,5.91),
              (5.92,8.58,0,5.91),(6.06,8.35,.065,5.79)]
    rings=[s.ring(mouth_ring(w,l,h,.40,y)) for y,w,l,h in profiles]
    for i,(a,b) in enumerate(zip(rings,rings[1:])):
        s.join(a,b,(['ice','ice','ice','cream','cream','cream','ice','ice'] if i==3 else 'gold'))
    for sign,outer in [(-1,rings[0]),(1,rings[-1])]:
        lip=s.ring(mouth_ring(6.96,.49,5.27,.29,sign*6.06))
        s.join(outer,lip,['cream','gold','gold','gold','gold','gold','gold','gold'])
        throat=s.ring(mouth_ring(6.83,.56,5.19,.27,sign*5.92))
        s.join(lip,throat,['cream','orange','orange','orange','orange','orange','orange','orange'])
        deep=s.ring(mouth_ring(6.83,.56,5.19,.27,sign*3.04))
        s.join(throat,deep,'dark')
        s.face(deep,'dark')
    s.finish()

def paneled_tier(m,base,top,panels=True):
    s=Skin(m)
    a=s.ring(ring_xy(*base)); b=s.ring(ring_xy(*top))
    s.face(a,'ice'); s.face(b,'cream')
    for k in range(8):
        j=(k+1)%8; quad=[a[k],a[j],b[j],b[k]]
        if k%2 or not panels:
            s.face(quad,'cream' if k%2 else 'ice')
            continue
        p,q,r,t=[s.v[i] for i in quad]
        normal=(q-p).cross(t-p).normalized()
        def inset(u,v):
            return p.lerp(q,u).lerp(t.lerp(r,u),v)
        inner=[inset(u,v) for u,v in [(.045,.12),(.955,.12),(.955,.87),(.045,.87)]]
        cut=s.ring([v-.065*normal for v in inner])
        s.join(quad,cut,'ice'); s.face(cut,'blue')
    s.finish()

def pedestal(m,w,d,lo,hi,c,col):
    m.loft([ring_xy(w-.10,d-.10,lo,c),ring_xy(w,d,lo+.06,c),ring_xy(w,d,hi-.06,c),
            ring_xy(w-.10,d-.10,hi,c)], [col]*3)

def motor(m):
    pedestal(m,3.26,3.90,8.30,8.68,.16,'red')
    s=Skin(m)
    rows=[s.ring(ring_xy(3.02,3.60,z,.22)) for z in (8.64,9.26,9.78,10.30)]
    lower=s.ring(ring_xy(2.86,3.44,10.45,.19))
    s.face(rows[0],'gold');s.join(rows[-1],lower,'gold');s.face(lower,'gold')
    for a,b in zip(rows,rows[1:]):
        for k in range(8):
            j=(k+1)%8; quad=[a[k],a[j],b[j],b[k]]
            if k%2:
                s.face(quad,'gold');continue
            p,q,r,t=[s.v[i] for i in quad]
            normal=(q-p).cross(t-p).normalized()
            verts=[p.lerp(q,u).lerp(t.lerp(r,u),v) for u,v in [(.17,.29),(.83,.29),(.83,.71),(.17,.71)]]
            deep=s.ring([v-normal*.055 for v in verts])
            s.join(quad,deep,'gold');s.face(deep,'dark')
    s.finish()

def cylinder(m,p,q,radius,color,n=6):
    if n!=6:
        m.tube([p,q],[radius,radius],color,sides=n)
        return
    a,b=Vector(p),Vector(q)
    normal=(b-a).normalized()
    u=normal.cross(Vector((0,0,1))).normalized()
    v=normal.cross(u)
    # The conical back is seated below the panel. Only the flat hex head is exposed.
    verts=[b+radius*(u*cos(k*tau/6)+v*sin(k*tau/6)) for k in range(6)]
    m.add(verts+[a-normal*.15],[tuple(range(6))]+[(6,k,(k+1)%6) for k in range(6)],color)

def side_relief(m,outline,x0,x1,shade):
    m.loft([[(x,y,z) for y,z in outline] for x in (x0,x1)],[shade])

def side_detail(m):
    # Right-hand service pipes curve from the sloping shoulder to the base.
    for y in (.95,2.23):
        cylinder(m,(3.59,y,6.56),(3.85,y,6.56),.47,'blue',10)
        pts=[(3.53,y,6.56),(3.93,y,6.56),(4.25,y,6.44),(4.48,y,6.15),
             (4.52,y,5.92),(4.52,y,.68)]
        m.tube(pts,[.30]*len(pts),'blue',sides=8)
    for z in (1.61,4.60):
        m.box((4.50,1.59,z),(.83,2.27,.43),'cream')
        for y in (.94,2.24):
            cylinder(m,(4.90,y,z),(5.01,y,z),.165,'silver')
    for side in (-1,1):
        # Low ivory rail with two contrasting panels and a gold middle foot.
        outline=[(-5.43,.016),(5.42,.016),(5.42,.74),(5.18,.93),(-5.19,.93),(-5.43,.71)]
        side_relief(m,outline,side*4.06,side*4.39,'cream')
        for y in (-2.72,2.72):
            side_relief(m,[(y-1.42,.21),(y+1.42,.21),(y+1.22,.66),(y-1.18,.66)],
                        side*4.38,side*4.404,'blue')
        side_relief(m,[(-1.09,.037),(1.09,.037),(1.09,.49),(.93,.64),(-.93,.64),(-1.09,.49)],
                    side*4.37,side*4.52,'gold')
        for y in (-4.82,4.84):
            for z in (1.18,5.15):
                cylinder(m,(side*4.087,y,z),(side*4.18,y,z),.20,'silver')
    badge_y,badge_z=-2.68,3.29
    def hexagon(x,r):
        return [(x,badge_y+r*cos(k*tau/6),badge_z+r*sin(k*tau/6)) for k in range(6)]
    s=Skin(m)
    a=s.ring(hexagon(4.08,1.39));b=s.ring(hexagon(4.22,1.39));c=s.ring(hexagon(4.22,1.19))
    s.face(a,'gold');s.join(a,b,'orange');s.join(b,c,'gold');s.face(c,'cream');s.finish()
    outline=[]
    for k in range(6):
        a=k*tau/6+pi/2
        for along,across in [(.16,-.07),(.44,-.07),(.61,-.24),(.68,-.17),(.57,-.065),
                             (.89,-.065),(.89,.065),(.57,.065),(.68,.17),(.61,.24),(.44,.07),(.16,.07)]:
            outline.append((badge_y+along*cos(a)-across*sin(a),badge_z+along*sin(a)+across*cos(a)))
    # The back face sits within the enamel badge, and the front is raised.
    side_relief(m,outline,4.213,4.262,'blue')
    # A quiet service hatch on the opposite side leaves the main badge side distinctive.
    side_relief(m,[(-2.31,1.51),(2.31,1.51),(2.31,4.44),(2.11,4.66),(-2.11,4.66),(-2.31,4.44)],
                -4.08,-4.15,'cyan')
    for y in (-1.54,0,1.54):
        side_relief(m,[(y-.38,2.64),(y+.12,2.64),(y+.39,3.54),(y-.13,3.54)],-4.14,-4.18,'ice')

def housing(m):
    body(m)
    paneled_tier(m,(7.98,10.64,5.68,.29),(5.88,8.34,7.49,.28))
    paneled_tier(m,(4.44,5.90,7.46,.22),(4.04,5.28,8.38,.18))
    motor(m);side_detail(m)
    for sign in (-1,1):
        for side in (-1,1):
            cylinder(m,(side*1.12,sign*1.78,10.10),(side*1.12,sign*1.86,10.10),.126,'silver')
            cylinder(m,(sign*1.49,side*1.39,10.10),(sign*1.57,side*1.39,10.10),.126,'silver')
    for sign in (-1,1):
        for x in (-3.71,3.71):
            for z in (.49,5.38):
                cylinder(m,(x,sign*6.052,z),(x,sign*6.16,z),.237,'silver')
        for z in LEVELS.values():
            # Annular bearings: the shaft spins inside a bore without contacting the housing.
            for side in (-1,1):
                s=Skin(m)
                def circle(x,r):
                    return [(side*x,sign*DRUM_Y+r*cos(k*tau/6),z+r*sin(k*tau/6)) for k in range(6)]
                rings=[s.ring(circle(x,r)) for x,r in [(3.45,.46),(3.315,.45),(3.315,.285)]]
                for a,b in zip(rings,rings[1:]+rings[:1]):s.join(a,b,'silver')
                s.finish()

def roller(m, phase):
    # A continuous drum with integral journals. Each cross-bar is seated through
    # the drum and supplies two opposing teeth as one solid piece.
    s = Skin(m)
    profiles = [(-3.405,.21),(-3.17,.21),(-3.07,.72),
                (3.07,.72),(3.17,.21),(3.405,.21)]
    rings = []
    for x,r in profiles:
        rings.append(s.ring([(x,r*cos(k*tau/10),r*sin(k*tau/10)) for k in range(10)]))
    s.face(rings[0],'silver')
    for a,b in zip(rings,rings[1:]):
        s.join(a,b,'silver')
    s.face(rings[-1],'silver')
    s.finish()
    for center in (-2.28,-.76,.76,2.28):
        for row in range(3):
            theta = phase+row*pi/3
            radial = Vector((0,cos(theta),sin(theta)))
            across = Vector((0,-sin(theta),cos(theta)))
            # The tiny axial stagger keeps buried cross-bars off a common plane.
            anchor = Vector((center+(row-1)*.049,0,0))
            bar = Skin(m)
            ends = []
            for distance in (-.986,.986):
                tip = anchor+radial*distance
                ends.append(bar.ring([tip+Vector((x,0,0))+across*u
                                      for x,u in [(-.33,-.23),(.33,-.23),(.33,.23),(-.33,.23)]]))
            bar.face(ends[0],'light')
            bar.join(ends[0],ends[1],'silver')
            bar.face(ends[1],'light')
            bar.finish()

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    group=bpy.data.collections.new('Snow Processor Tower')
    scene.collection.children.link(group)
    surf=palette()
    def create(name,shape,loc=(0,0,0)):
        mesh=Plant(name,group,surf)
        shape(mesh)
        mesh.vertices=[Vector(v)*STUD for v in mesh.vertices]
        ob=mesh.object()
        edit=bmesh.new()
        edit.from_mesh(ob.data)
        bmesh.ops.dissolve_limit(edit,angle_limit=.0005,delimit={'UV'},verts=list(edit.verts),edges=list(edit.edges))
        bmesh.ops.triangulate(edit,faces=[f for f in edit.faces if len(f.verts)>4])
        edit.to_mesh(ob.data)
        edit.free()
        ob.location=Vector(loc)*STUD
        return ob
    create('ProcessorTower',housing)
    for end,sign in [('Front',-1),('Rear',1)]:
        for i,(level,z) in enumerate(LEVELS.items()):
            ob=create(f'{end}_{level}',lambda m,p=(-.08 if i else .08):roller(m,p),(0,sign*DRUM_Y,z))
            for face in ob.data.polygons:
                coords = [ob.data.vertices[j].co for j in face.vertices]
                if abs(face.normal.x)<.001 and all(abs((v.y*v.y+v.z*v.z)**.5/STUD-.72)<.001 for v in coords):
                    face.use_smooth = True
            ob['rotation_axis']='local X'
            ob['infeed_rotation_sign']=sign*(-1 if i else 1)
    bpy.context.view_layer.update()
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.color_type='TEXTURE';space.overlay.show_overlays=False
            space.region_3d.view_rotation=Vector((1.18,-1,.38)).to_track_quat('Z','Y')
            space.region_3d.view_location=(0,0,4.85*STUD)
            space.region_3d.view_perspective='ORTHO';space.region_3d.view_distance=8
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'SnowProcessorTower.blend'),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSET/'export/SnowProcessorTower.glb'),export_format='GLB',
                              use_active_scene=True,export_extras=True,export_animations=False)

if __name__=='__main__':build()
