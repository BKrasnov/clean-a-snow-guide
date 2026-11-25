"""Build the six classic belt modules, keeping grid pivots independent of bounds."""
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
ROOT = ASSET.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0,str(ASSET.parent/'processor-tower/source'))
from build_processor import Plant, Skin, STUD, clipped, palette

PITCH = 4.0
END = 1.99
W = 1.41  # centres of the two .22-stud rails
DOCK = 6.06
LAYOUT = {'Straight':(-6,4),'TurnLeft':(0,4),'TurnRight':(6,4),
          'Tee':(-6,-2),'Cross':(0,-2),'TowerAdapter':(6,-4)}
DIRS = [(1,0),(0,1),(-1,0),(0,-1)]
PORTS = {'Straight':[1,3], 'TurnLeft':[2,3], 'TurnRight':[0,3],
         'Tee':[0,2,3], 'Cross':[0,1,2,3]}
V = Vector


def rail(m,path):
    """Continuous metal sill with blue skirt, yellow lip and integral end cuffs."""
    pts=[V(p) for p in path]
    directions=[(b-a).normalized() for a,b in zip(pts,pts[1:])]
    tangents=[directions[0]]+[(a+b).normalized() for a,b in zip(directions,directions[1:])]+[directions[-1]]
    lengths=[0.]
    for a,b in zip(pts,pts[1:]):
        lengths.append(lengths[-1]+(b-a).length)
    total=lengths[-1]
    marks=sorted(set([.018,.08,.24,total-.24,total-.08,total-.018]+lengths[1:-1]))
    s=Skin(m)
    rings=[]
    for dist in marks:
        k=next(i for i in range(len(directions)) if dist<=lengths[i+1]+1e-7)
        pos=pts[k]+directions[k]*(dist-lengths[k])
        fraction=(dist-lengths[k])/(lengths[k+1]-lengths[k])
        tangent=tangents[k].lerp(tangents[k+1],fraction).normalized()
        normal=V((-tangent.y,tangent.x))
        cuff=min(dist,total-dist)<=.24+1e-6
        width=.129 if cuff else .11
        bottom=.254 if cuff else .28
        cap=.938 if cuff else .90
        section=[(-width,bottom),(width,bottom),
                 (width,.665),(width,cap-.05),(width-.043,cap),
                 (-width+.043,cap),(-width,cap-.05),(-width,.665)]
        rings.append(s.ring([(*(pos+normal*u),z) for u,z in section]))
    s.face(rings[0],'gold')
    for k,(a,b) in enumerate(zip(rings,rings[1:])):
        mid=(marks[k]+marks[k+1])/2
        if min(mid,total-mid)<.241:
            s.join(a,b,'gold')
        else:
            s.join(a,b,['silver','ice','gold','gold','gold','gold','gold','ice'])
    s.face(rings[-1],'gold')
    s.finish()


def deck(m,outline):
    s=Skin(m)
    rings=[s.ring([(x,y,z) for x,y in outline]) for z in (.32,.43,.70)]
    s.face(rings[0],'silver')
    s.join(rings[0],rings[1],'cream')
    s.join(rings[1],rings[2],'dark')
    s.face(rings[-1],'dark')
    s.finish()


def foot(m,x,y):
    m.box((x,y,.1725),(.47,.47,.345),'blue')


def port_hardware(m,direction,center,feet=True):
    axis=V(direction)
    side=V((-axis.y,axis.x))
    for sign in (-1,1):
        normal=sign*side
        # A small axle pin is visible on the outer face of each yellow cuff.
        p=V(center)-axis*.13+normal*W
        head=p+normal*.153
        rim=[(*(head+axis*(.068*math.cos(j*math.tau/6))),.52+.068*math.sin(j*math.tau/6)) for j in range(6)]
        m.add(rim+[(*(p+normal*.078),.52)],[tuple(range(6))]+[(6,j,(j+1)%6) for j in range(6)],'silver')
        if feet:
            q=V(center)-axis*.32+normal*1.16
            foot(m,*q)


def track(m,name):
    if name=='Straight':
        paths=[[(-W,-END),(-W,END)],[(W,END),(W,-END)]]
    elif name.startswith('Turn'):
        sign=1 if name=='TurnRight' else -1
        # Parametric parallel arcs share a common centre at a corner of the grid cell.
        def arc(r):
            delta=.01/r
            return [(sign*(2-r*math.cos(t)),-2+r*math.sin(t)) for t in
                    [delta+(math.pi/2-2*delta)*i/12 for i in range(13)]]
        paths=[arc(2-W),list(reversed(arc(2+W)))]
    else:
        ports=PORTS[name]
        paths=[]
        for i,index in enumerate(ports):
            turns=(ports[(i+1)%len(ports)]-index)%4
            if turns==2:
                path=[(END,W),(-END,W)]
            else:
                r=.22
                path=[(END,W)]
                for step in range(4):
                    t=-math.pi/2-step*math.pi/6
                    path.append((W+r+r*math.cos(t),W+r+r*math.sin(t)))
                path.append((W,END))
            a,b=DIRS[index]
            paths.append([(a*x-b*y,b*x+a*y) for x,y in path])
    deck(m,[p for path in paths for p in path])
    for path in paths:
        rail(m,path)
    for i in PORTS[name]:
        d=V(DIRS[i])
        port_hardware(m,d,d*END)
    if name in ('Tee','Cross'):
        rings=[[(r*math.cos(t*math.tau/20),r*math.sin(t*math.tau/20),z) for t in range(20)]
               for r,z in [(.81,.686),(.81,.749),(.775,.775)]]
        m.loft(rings,['gold','gold'])


def adapter(m):
    """Hollow reducing hood. Its tongue clears the tower sill; all decks meet at .70."""
    s=Skin(m)
    def section(y,w,lo,hi,c):
        return s.ring([(x,y,z+(lo+hi)/2) for x,z in clipped(w,hi-lo,c)])
    outer=[section(*args) for args in [(-.13,6.50,.588,4.83,.27),
           (.055,6.91,.539,4.96,.27),(.31,6.91,.539,4.96,.27),
           (.38,6.63,.54,4.78,.19),(3.17,3.06,.34,1.78,.11),
           (3.24,3.09,.33,1.79,.11)]]
    for k,(a,b) in enumerate(zip(outer,outer[1:])):
        if k!=3:
            s.join(a,b,'gold' if k<3 else 'cream')
            continue
        for j in range(8):
            h=(j+1)%8
            quad=[a[j],a[h],b[h],b[j]]
            if j not in (2,4,6):
                s.face(quad,'cream')
                continue
            p,q,r,t=[s.v[n] for n in quad]
            inset=s.ring([p.lerp(q,u).lerp(t.lerp(r,u),v) for u,v in
                          [(.09,.04),(.91,.04),(.89,.92),(.11,.92)]])
            s.join(quad,inset,'cream')
            s.face(inset,'cyan' if j==4 else 'blue')
    inner=[section(*args) for args in [(-.13,6.18,.70,4.57,.17),
           (.35,6.17,.70,4.50,.17),(3.24,2.66,.70,1.54,.06)]]
    s.join(outer[0],inner[0],'gold')
    s.join(outer[-1],inner[-1],'cream')
    for a,b in zip(inner,inner[1:]):
        s.join(a,b,['dark','dark','ice','ice','ice','ice','ice','dark'])
    s.finish()
    # Nose stub. End faces are separated by a .01-stud expansion seam.
    outlines=[[(-W,3.25),(-W,3.99)],[(W,3.99),(W,3.25)]]
    deck(m,[p for path in outlines for p in path])
    for path in outlines:rail(m,path)
    port_hardware(m,(0,1),(0,3.99))
    for x in (-2.66,2.66):
        m.box((x,.55,.29),(.53,.65,.58),'blue')


def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.update()
    bpy.ops.export_scene.gltf(filepath=str(ASSET/'export'/(name+'.glb')),export_format='GLB',
                              use_selection=True,export_extras=True,export_animations=False)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    material,uv=palette()
    material.name='M_ClassicConveyor'
    bpy.data.images['ProcessorTower_Palette'].name='ClassicConveyor_Palette'
    pieces={}
    for name,(x,y) in LAYOUT.items():
        mesh=Plant(name,scene.collection,(material,uv))
        if name=='TowerAdapter':adapter(mesh)
        else:track(mesh,name)
        mesh.vertices=[V(p)*STUD for p in mesh.vertices]
        obj=mesh.object()
        edit=bmesh.new()
        edit.from_mesh(obj.data)
        bmesh.ops.dissolve_limit(edit,angle_limit=.0005,delimit={'UV'},verts=list(edit.verts),edges=list(edit.edges))
        bmesh.ops.triangulate(edit,faces=[f for f in edit.faces if len(f.verts)>4])
        edit.to_mesh(obj.data)
        edit.free()
        obj['grid_pitch_studs']=PITCH
        if name in PORTS:obj['ports_blender_xy']=','.join(['E','N','W','S'][i] for i in PORTS[name])
        export(name,[obj])
        obj.location=V((x,y,0))*STUD
        pieces[name]=obj
    bpy.ops.object.select_all(action='DESELECT')
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.color_type='TEXTURE'
            space.overlay.show_overlays=False
            space.region_3d.view_rotation=V((.30,-.82,1.63)).to_track_quat('Z','Y')
            space.region_3d.view_location=(0,.2,.22)
            space.region_3d.view_perspective='ORTHO'
            space.region_3d.view_distance=9
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'ClassicConveyor.blend'),compress=True)
    export('ClassicConveyorKit',pieces.values())
    station_file=ASSET.parent/'ram-feeder/export/RamFeederWithTower.glb'
    bpy.ops.import_scene.gltf(filepath=str(station_file))
    station=list(bpy.context.selected_objects)
    assert len(station)==10
    dock=pieces['TowerAdapter']
    dock.location=V((0,DOCK,0))*STUD
    line=[]
    for i in range(3):
        obj=pieces['Straight'].copy()
        scene.collection.objects.link(obj)
        obj.name=f'Run{i+1:02d}'
        obj.location=V((0,DOCK+6+i*PITCH,0))*STUD
        line.append(obj)
    export('ClassicConveyorWithProcessor',station+[dock]+line)


if __name__=='__main__':
    build()
