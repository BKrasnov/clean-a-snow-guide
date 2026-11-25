"""Inspect round-tripped modules, check ports in every pairing, then render review views."""
import json
from math import pi
from pathlib import Path
import sys
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
ROOT=ASSET.parents[2]
TMP=ROOT/'build/classic-conveyor'
GALLERY=ROOT/'art/refs/snow-processing'
sys.dont_write_bytecode=True
sys.path[:0]=[str(HERE),str(ASSET.parent/'ram-feeder/source')]
from build_conveyor import DIRS, DOCK, LAYOUT, PITCH, PORTS, STUD
from check_feeder import close_enough, no_coincident_faces
from check_processor import budget_report, daylight, extent, inspect_model, triangles, world_points


def load(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ASSET/'export'/(name+'.glb')))
    return {o.name:o for o in bpy.context.scene.objects}


def tree(points,surface):
    return BVHTree.FromPolygons(points,surface,all_triangles=True)


def audit():
    bpy.ops.wm.open_mainfile(filepath=str(HERE/'ClassicConveyor.blend'))
    originals={o.name:o for o in bpy.context.scene.objects}
    bounds={n:extent(world_points(o)) for n,o in originals.items()}
    reports={}
    for n,o in originals.items():
        r=inspect_model([o])
        r['budget'],issues=budget_report(r,ROOT/'art/budgets.json','small_prop',HERE/'ClassicConveyor.blend',[o])
        assert r['ok'] and not issues,(n,r['issues'],issues)
        reports[n]=r
    points={}
    polys={}
    ports=[]
    for name in LAYOUT:
        objs=load(name)
        assert list(objs)==[name]
        o=objs[name]
        assert o.matrix_world.translation.length<1e-6
        assert any(i.packed_file for i in bpy.data.images)
        no_coincident_faces([o])
        points[name]=world_points(o)
        polys[name]=triangles(o)
        assert len(polys[name])==reports[name]['totals']['tris']
        offset=Vector((*LAYOUT[name],0))*STUD
        assert close_enough(bounds[name],extent([v+offset for v in points[name]]))
        if name=='TowerAdapter':
            ports.append((name,1,Vector((0,4,0))))
        else:
            for d in PORTS[name]:
                ports.append((name,d,Vector((*DIRS[d],0))*2))
    # Turn every port into the same east-facing interface at the origin.
    ends=[]
    for name,d,port in ports:
        rot=Matrix.Rotation(-d*pi/2,3,'Z')
        pts=[rot@(p-port*STUD) for p in points[name]]
        surface=tree(pts,polys[name])
        for lateral in (-1.22,0,1.22):
            hit=surface.ray_cast(Vector((-.04,lateral,2))*STUD,Vector((0,0,-1)))[0]
            assert hit and abs(hit.z/STUD-.70)<.0005,(name,d,lateral,hit)
        ends.append((surface,tree([Vector((-p.x,-p.y,p.z)) for p in pts],polys[name]),name,d))
    pairs=0
    for a,_,an,ad in ends:
        for _,b,bn,bd in ends:
            assert not a.overlap(b),(an,ad,bn,bd)
            pairs+=1
    kit=load('ClassicConveyorKit')
    assert set(kit)==set(LAYOUT)
    assert len({o.active_material for o in kit.values()})==1
    for name,o in kit.items():
        assert close_enough(bounds[name],extent(world_points(o)))
        assert (o.matrix_world.translation-Vector((*LAYOUT[name],0))*STUD).length<1e-5
    assembled=load('ClassicConveyorWithProcessor')
    adapter=assembled['TowerAdapter']
    hood=tree(world_points(adapter),triangles(adapter))
    assert (adapter.matrix_world.translation-Vector((0,DOCK,0))*STUD).length<1e-5
    for name,o in assembled.items():
        if name!='TowerAdapter':
            assert not hood.overlap(tree(world_points(o),triangles(o))),name
    for i in range(3):
        o=assembled[f'Run{i+1:02d}']
        assert abs(o.matrix_world.translation.y/STUD-(DOCK+6+i*PITCH))<.0001
    assert assembled['Pusher'].matrix_world.translation.y<0
    rotors=[assembled[n] for n in ('Rear_Upper','Rear_Lower')]
    nose=min(v.y for v in world_points(adapter))/STUD
    drum_end=max(o.matrix_world.translation.y/STUD+
                 max((v-o.matrix_world.translation).yz.length for v in world_points(o))/STUD for o in rotors)
    assert nose-drum_end>.3
    report={'modules':reports,'mates_tested':pairs,'through_deck_studs':.7,'pitch_studs':PITCH,
            'belt_width_studs':2.6,'rear_dock_studs':DOCK,'minimum_rotor_clearance_studs':round(nose-drum_end,4),
            'kit_meshes':len(kit),'combined_meshes':len(assembled),'avatar_studs':5.1,
            'exports_bytes':{p.name:p.stat().st_size for p in sorted((ASSET/'export').glob('*.glb'))}}
    (ASSET/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')


def studio():
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=12
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='Standard'
    scene.world=bpy.data.worlds.new('Skylight')
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value=(.78,.87,1,1)
    bg.inputs[1].default_value=.66
    daylight('Key',(-.45,.6,-1),1.9)
    daylight('Rim',(.6,-.6,-.7),.60)
    bpy.ops.mesh.primitive_plane_add(size=400,location=(0,0,-.003))
    mat=bpy.data.materials.new('Studio floor')
    mat.use_nodes=True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.48,.61,.81,1)
    bpy.context.object.data.materials.append(mat)
    bpy.ops.object.camera_add()
    cam=bpy.context.object
    cam.data.type='ORTHO'
    scene.camera=cam
    return cam


def snap(path,cam,objs,direction,size):
    direction=Vector(direction).normalized()
    rotation=(-direction).to_track_quat('-Z','Y')
    lo,hi=extent([rotation.inverted()@p for obj in objs for p in world_points(obj)])
    target=rotation@((Vector(lo)+Vector(hi))*.5)
    cam.rotation_euler=rotation.to_euler()
    cam.location=target+direction*30
    w,h=size
    cam.data.ortho_scale=max(hi[0]-lo[0],(hi[1]-lo[1])*w/h)*1.10
    scene=bpy.context.scene
    scene.render.resolution_x,scene.render.resolution_y=w,h
    scene.render.resolution_percentage=100
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)


def render():
    kit=load('ClassicConveyorKit')
    cam=studio()
    for tag,vector in [('front',(0,-1,0)),('side',(1,0,0)),('back',(0,1,0)),('top',(0,0,1))]:
        snap(TMP/(tag+'.png'),cam,kit.values(),vector,(960,600))
    # Rotate the detached hood for the catalogue so the wide open flange faces the viewer.
    kit['TowerAdapter'].rotation_mode='XYZ'
    kit['TowerAdapter'].rotation_euler.z=-1.06
    kit['TowerAdapter'].location.x+=1.35*STUD
    kit['Straight'].rotation_mode='XYZ'
    kit['Straight'].rotation_euler.z=-1.1
    for n in ('Straight','TurnLeft','TurnRight'):
        kit[n].location.y+=2.0*STUD
    bpy.context.view_layer.update()
    snap(GALLERY/'classic-conveyor-kit.png',cam,kit.values(),(.12,-1,.83),(1200,770))
    (TMP/'three-quarter.png').write_bytes((GALLERY/'classic-conveyor-kit.png').read_bytes())
    # Real plug-together examples: each open arm gets one unchanged four-stud tile.
    for o in kit.values():o.hide_render=True
    networks=[]
    for n,offset in [('Tee',-6.8),('Cross',6.8)]:
        hub=kit[n]
        hub.hide_render=False
        hub.location=Vector((offset,0,0))*STUD
        networks.append(hub)
        for d in PORTS[n]:
            tile=kit['Straight'].copy()
            bpy.context.scene.collection.objects.link(tile)
            tile.hide_render=False
            tile.rotation_mode='XYZ'
            tile.rotation_euler.z=pi/2 if d%2==0 else 0
            tile.location=hub.location+Vector((*DIRS[d],0))*PITCH*STUD
            networks.append(tile)
    bpy.context.view_layer.update()
    for tile in networks:
        if tile.name.startswith('Straight'):
            h=min((obj for obj in networks if obj.name in ('Tee','Cross')),
                  key=lambda obj:(tile.location-obj.location).length)
            axis=(tile.matrix_world.to_3x3()@Vector((0,1,0))).normalized()
            assert abs(axis.dot((tile.location-h.location).normalized()))>.999
    snap(GALLERY/'classic-conveyor-junctions.png',cam,networks,(.15,-.7,1.15),(1300,680))
    assembly=load('ClassicConveyorWithProcessor')
    cam=studio()
    mannequin=[]
    mat=bpy.data.materials.new('Player height')
    mat.use_nodes=True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.18,.33,.43,1)
    def block(x,z,size):
        bpy.ops.mesh.primitive_cube_add(size=1,location=Vector((x-3.4,13.0,z))*STUD)
        o=bpy.context.object
        o.dimensions=Vector(size)*STUD
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(mat)
        bevel=o.modifiers.new('Corners','BEVEL');bevel.width=.018;bevel.segments=1
        o.modifiers.new('Normals','WEIGHTED_NORMAL')
        mannequin.append(o)
    for x in (-.50,.50):block(x,1,(.98,.96,2))
    block(0,3,(1.99,1,2));block(0,4.55,(1.4,1.05,1.1))
    for x in (-1.31,1.31):block(x,3,(.60,.95,1.96))
    snap(GALLERY/'classic-conveyor-docked.png',cam,list(assembly.values())+mannequin,(1,-.28,.39),(1400,635))


if __name__=='__main__':
    audit()
    if '--audit-only' not in sys.argv:
        render()
