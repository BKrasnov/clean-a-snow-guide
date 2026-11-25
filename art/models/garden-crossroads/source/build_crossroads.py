"""Build the empty crossroads garden in studs, with a soil-level origin on each bed."""
from math import cos, sin, tau
from pathlib import Path
import sys
import bpy
from mathutils import Vector

SOURCE = Path(__file__).resolve().parent
ASSET = SOURCE.parent
ROOT = ASSET.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ASSET.parent / 'garden-plants/source'))
from plant_mesh import Plant, palette

STUD = .28
SOCKET = .58
HALF_X, HALF_Y = 7.95, 6.58

def rectangle(x,y,w,d,z):
    return [(x+a*w/2,y+b*d/2,z) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]

def plank(mesh,x,y,w,d,z0,z1,color,bevel=.035,end_axis=None):
    rings=[rectangle(x,y,w-2*bevel,d-2*bevel,z0),rectangle(x,y,w,d,z0+bevel),
           rectangle(x,y,w,d,z1-bevel),rectangle(x,y,w-2*bevel,d-2*bevel,z1)]
    mesh.loft(rings,[color]*3)
    if end_axis:
        start=len(mesh.colors)-14
        for edge in ([1,3] if end_axis=='X' else [0,2]):
            mesh.colors[start+5+edge]='bark'

def soil(mesh):
    # One closed soil volume with a continuous depression, rather than an overlapping dark disc.
    boundary=[(-1.98,-1.23),(0,-1.23),(1.98,-1.23),(1.98,0),(1.98,1.23),
              (0,1.23),(-1.98,1.23),(-1.98,0)]
    rings=[[(x,y,z) for x,y in boundary] for z in [.046,.793]]
    for rx,ry,z in [(.80,.63,.797),(.58,.45,.68),(.43,.34,SOCKET)]:
        rings.append([(rx*cos((i-3)*tau/8),ry*sin((i-3)*tau/8),z) for i in range(8)])
    mesh.loft(rings,['earth','earth','earth','bark'])

def bed(mesh):
    for i,(z0,z1) in enumerate([(0,.466),(.472,.94)]):
        # Alternate end joints in the stacked courses. The narrow seam separates the end faces.
        if i==0:
            for sign in (-1,1):
                plank(mesh,0,sign*1.34,4.50,.32,z0,z1,'tan',end_axis='X')
                plank(mesh,sign*2.08,0,.32,2.35,z0,z1-.004,'tan',end_axis='Y')
        else:
            for sign in (-1,1):
                plank(mesh,0,sign*1.34,3.75,.32,z0,z1,'wood',end_axis='X')
                plank(mesh,sign*2.065,0,.37,3,z0+.004,z1+.004,'wood',end_axis='Y')
    soil(mesh)

def post(mesh,x,y,gate=False):
    plank(mesh,x,y,.62,.62,0,1.64,'wood',.038)
    if gate:
        plank(mesh,x,y,.74,.74,1.632,1.89,'red',.055)

def rails(mesh,p,q):
    x,y=p
    dx,dy=q[0]-x,q[1]-y
    # Rails terminate inside posts, at different depths to the end faces of the posts.
    w,d=(abs(dx)-.55,.215) if dx else (.215,abs(dy)-.55)
    for z in (.28,1.025):
        plank(mesh,x+dx/2,y+dy/2,w,d,z,z+.38,'wood',.027)

def fence(mesh,points,owned,red=()):
    for a,b in zip(points,points[1:]):
        rails(mesh,a,b)
    for i in owned:
        post(mesh,*points[i],gate=i in red)

def finish(mesh, offset, pivot):
    mesh.vertices=[(Vector(p)-Vector(pivot))*STUD for p in mesh.vertices]
    ob=mesh.object()
    ob.location=(Vector(offset)+Vector(pivot))*STUD
    return ob

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    group=bpy.data.collections.new('Crossroads Garden')
    scene.collection.children.link(group)
    surface=palette()
    surface[0].name='M_GardenTimber'
    surface[0].node_tree.nodes.active.image.name='GardenTimber_Palette'
    def make(name):
        return Plant(name,group,surface)
    for name,x,y in [('Bed01',-4.50,-3.75),('Bed02',4.50,-3.75),
                     ('Bed03',-4.50,3.75),('Bed04',4.50,3.75)]:
        mesh=make(name)
        bed(mesh)
        ob=finish(mesh,(x,y,0),(0,0,SOCKET))
        ob['role']='planting_bed'
        ob['plant_origin']='object origin at centre of hollow'
    x,y=HALF_X,HALF_Y
    gate=2.5+.74/2
    spans=[
      ('FenceFrontLeft',[(-x,-y),(-gate,-y)],[0,1],[1]),
      ('FenceFrontRight',[(gate,-y),(x,-y)],[0,1],[0]),
      ('FenceLeft',[(-x,-y),(-x,-2.16),(-x,2.16),(-x,y)],[1,2],[]),
      ('FenceRight',[(x,-y),(x,-2.16),(x,2.16),(x,y)],[1,2],[]),
      ('FenceBack',[(-x,y),(-x/3,y),(x/3,y),(x,y)],[0,1,2,3],[])]
    for name,points,owned,red in spans:
        mesh=make(name)
        fence(mesh,points,owned,red)
        a,b=points[0],points[-1]
        finish(mesh,(0,0,0),((a[0]+b[0])/2,(a[1]+b[1])/2,0))
    bpy.context.preferences.filepaths.save_version=0
    bpy.context.view_layer.update()
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active
            s.shading.color_type='TEXTURE'
            s.shading.light='STUDIO'
            s.overlay.show_overlays=False
            s.region_3d.view_rotation=Vector((.12,-1,.80)).to_track_quat('Z','Y')
            s.region_3d.view_distance=9.3
            s.region_3d.view_perspective='ORTHO'
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'GardenCrossroads.blend'),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSET/'export/GardenCrossroads.glb'),export_format='GLB',
                              use_active_scene=True,export_animations=False,export_extras=True)

if __name__=='__main__':
    build()
