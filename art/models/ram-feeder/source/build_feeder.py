"""Build the ram feeder in studs, with a local dock datum and nested hollow rams."""
from math import cos, sin, pi, tau
from pathlib import Path
import sys
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
TOWER = ASSET.parent/'processor-tower/source'
sys.dont_write_bytecode = True
sys.path.insert(0, str(TOWER))
from build_processor import Plant, Skin, STUD, clipped, palette

DOCK = -6.06
FLOOR = .70
AXIS_Z = 1.26
AXES = (-1.55, 1.55)
TRAVEL = 10.64
HOME = -10.82
DISPLAY = .26
NAME = 'RamFeeder'
FRAME = 'FeederFrame'
MOVERS = ('Sleeves01', 'Sleeves02', 'Sleeves03', 'Pusher')
TOWER_FILE = TOWER/'SnowProcessorTower.blend'


def tray(m):
    # Each cross-section includes the underside, twin rails and recessed bed in one skin.
    # A short raised tongue clears the tower sill on both intakes.
    rows = [(-15.10,3.78,3.28,.03,.95),(-14.83,3.92,3.28,0,1.22),
            (-14.22,3.92,3.28,0,1.28),(-14.02,3.86,3.28,.02,1.20),
            (-2.06,3.86,3.28,.02,1.20),(-1.40,3.28,3.04,.12,1.12),
            (-.33,3.28,3.04,.13,1.12),(-.10,3.24,3.04,.59,1.09),
            (.23,3.24,3.04,.59,1.09)]
    s = Skin(m)
    sections = []
    for y,w,i,base,h in rows:
        c = .135 if y >= -.10 else .055
        profile = [(-w+c,base),(w-c,base),(w,base+c),(w,h-.105),(w-.10,h),
                   (i+.065,h),(i,h-.065),(i,FLOOR),(-i,FLOOR),(-i,h-.065),
                   (-i-.065,h),(-w+.10,h),(-w,h-.105),(-w,base+c)]
        sections.append(s.ring([(x,y,z) for x,z in profile]))
    for j,(a,b) in enumerate(zip(sections,sections[1:])):
        shell = 'gold' if j < 3 else 'ice'
        top = 'gold' if j < 3 else 'cream'
        s.join(a,b,['silver',shell,shell,top,top,top,'ice','dark','ice',top,top,top,shell,shell])
    s.face(sections[0],'gold')
    s.face(sections[-1],'dark')
    s.finish()


def block(m, cx, y0, y1, z0, z1, w, cut, shade):
    def contour(y):
        return [(cx+x,y,(z0+z1)/2+z) for x,z in clipped(w,z1-z0,cut)]
    m.loft([contour(y0),contour(y1)],[shade])


def disk_ring(x,y,z,r):
    return [(x+r*cos(tau*k/12),y,z+r*sin(tau*k/12)) for k in range(12)]


def open_sleeve(m,x,y0,y1,outer,bore,shade):
    s = Skin(m)
    rings = [s.ring(disk_ring(x,y,AXIS_Z,r)) for y,r in
             [(y0,outer),(y1-.055,outer),(y1,outer-.012),(y1,bore),(y0,bore)]]
    for a,b,col in zip(rings,rings[1:]+rings[:1],[shade,'light','silver','dark','silver']):
        s.join(a,b,col)
    s.finish()


def mount(m,x):
    # Radial loops form a square housing with a real, continuous bore for the rod stack.
    s = Skin(m)
    ring = []
    for y,half,round_radius in [(-14.62,.575,None),(-13.67,.575,None),(-13.54,.49,None),
                                (-13.54,0,.375),(-14.62,0,.375)]:
        points = []
        for k in range(12):
            a = tau*k/12
            u,v = cos(a),sin(a)
            r = round_radius if round_radius else half/max(abs(u),abs(v))
            points.append((x+r*u,y,AXIS_Z+r*v))
        ring.append(s.ring(points))
    for a,b,c in zip(ring,ring[1:]+ring[:1],['cream','cream','cream','silver','cream']):
        s.join(a,b,c)
    s.finish()
    block(m,x,-14.689,-14.596,.737,1.791,1.07,.070,'cream')
    block(m,x,-14.42,-13.83,1.811,1.995,.63,.045,'red')
    open_sleeve(m,x,-14.56,-11.59,.38,.328,'silver')


def frame(m):
    tray(m)
    # Tail fascia. The blue inset is part of the front face.
    s = Skin(m)
    def sill(w,y,low,high,c):
        return [(x,y,(low+high)/2+z) for x,z in clipped(w,high-low,c)]
    a=s.ring(sill(6.66,-14.66,.069,1.13,.10))
    b=s.ring(sill(6.70,-15.14,.051,1.045,.09))
    c=s.ring(sill(6.12,-15.16,.245,.815,.075))
    s.face(a,'cream'); s.join(a,b,'cream'); s.join(b,c,'cream'); s.face(c,'blue'); s.finish()
    for side in (-1,1):
        for y0,y1 in [(-13.76,-8.18),(-7.64,-2.48)]:
            s = Skin(m)
            def sidepanel(x,inset):
                y,z=y0+inset,.255+inset
                end,top=y1-inset,.969-inset
                return [(side*x,y,z),(side*x,end-.16,z),(side*x,end,top),
                        (side*x,y+.16,top)]
            rings = [s.ring(sidepanel(x,v)) for x,v in [(3.852,0),(3.897,0),(3.907,.085)]]
            s.face(rings[0],'ice');s.join(rings[0],rings[1],'ice')
            s.join(rings[1],rings[2],'cream');s.face(rings[2],'blue');s.finish()
        for y in (-13.92,-7.92,-2.26):
            m.tube([(side*3.85,y,.88),(side*3.925,y,.88)], [.085,.10],'silver',sides=6)
        m.tube([(side*3.55,-2.24,1.185),(side*3.55,-2.24,1.25)],[.115,.12],'silver',sides=6)
        m.tube([(side*3.56,-15.08,.61),(side*3.56,-15.165,.61)],[.14,.16],'silver',sides=6)
    for x in AXES:
        mount(m,x)


def moving_part(m,level):
    radii=[(.316,.275),(.264,.220),(.209,.171)]
    for x in AXES:
        y0 = -14.56+.12*level
        y1 = -11.59+.12*level
        if level<4:
            r,bore=radii[level-1]
            open_sleeve(m,x,y0,y1,r,bore,'light' if level==2 else 'silver')
        else:
            m.loft([disk_ring(x,y0,AXIS_Z,.159),disk_ring(x,HOME-.255,AXIS_Z,.159)],['silver'])
            block(m,x,HOME-.372,HOME-.205,.924,1.628,.72,.07,'cream')
    if level!=4:
        return
    # Single moving blade; the safety cap wraps over the sloping shoulders.
    sections=[(.749,5.75,.42,'blue'),(.84,5.91,.56,'blue'),(2.30,5.91,.56,'blue'),
              (2.39,5.88,.66,'gold'),(2.60,5.83,.66,'gold'),(2.77,5.54,.48,'gold')]
    rings=[[(x,HOME+y,z) for x,y in clipped(w,d,.10)] for z,w,d,col in sections]
    m.loft(rings,[row[3] for row in sections[1:]])


def append_tower():
    with bpy.data.libraries.load(str(TOWER_FILE)) as (available,taken):
        taken.objects=[n for n in available.objects if n=='ProcessorTower' or n.startswith(('Front_','Rear_'))]
    assert len(taken.objects)==5
    for obj in taken.objects:
        bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.update()
    return taken.objects


def export_glb(name):
    target=ASSET/'export'
    target.mkdir(exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(target/(name+'.glb')),export_format='GLB',
                              export_extras=True,export_animations=False,use_active_scene=True)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    group=bpy.data.collections.new('Ram feeder')
    scene.collection.children.link(group)
    material,swatches=palette()
    material.name='M_RamFeeder'
    bpy.data.images['ProcessorTower_Palette'].name='RamFeeder_Palette'
    def mesh(name,shape,origin):
        data=Plant(name,group,(material,swatches))
        shape(data)
        data.vertices=[(Vector(p)-origin)*STUD for p in data.vertices]
        obj=data.object()
        obj.location=origin*STUD
        return obj
    chassis=mesh(FRAME,frame,Vector((0,0,0)))
    chassis['Stroke']=DISPLAY
    chassis.id_properties_ui('Stroke').update(min=0,max=1,description='Full piston stroke, 0 to 1')
    for i,name in enumerate(MOVERS,1):
        origin=Vector((0,HOME,AXIS_Z))
        moving=mesh(name,lambda m,n=i:moving_part(m,n),origin)
        moving['travel_studs']=i*TRAVEL/4
        drv=moving.driver_add('location',1).driver
        var=drv.variables.new()
        var.name='stroke'
        var.targets[0].id=chassis
        var.targets[0].data_path='["Stroke"]'
        drv.expression=f'{HOME*STUD} + stroke * {i*TRAVEL/4*STUD}'
    bpy.context.view_layer.update()
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.color_type='TEXTURE'
            space.overlay.show_overlays=False
            space.region_3d.view_rotation=Vector((.78,-1,.95)).to_track_quat('Z','Y')
            space.region_3d.view_location=(0,-7.4*STUD,.30)
            space.region_3d.view_perspective='ORTHO'
            space.region_3d.view_distance=7.2
    bpy.context.view_layer.objects.active=chassis
    chassis.select_set(True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/(NAME+'.blend')),compress=True)
    export_glb(NAME)
    # Bake the preview position before moving the feeder into the tower's coordinate system.
    for obj in group.objects:
        pos=obj.matrix_world.translation.copy()
        obj.animation_data_clear()
        obj.location=pos+Vector((0,DOCK*STUD,0))
    append_tower()
    export_glb('RamFeederWithTower')


if __name__=='__main__':
    build()
