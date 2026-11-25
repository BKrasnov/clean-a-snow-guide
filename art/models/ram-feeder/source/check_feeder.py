"""Round-trip both deliverables, sweep the mechanism at either intake and render the assembly."""
from itertools import combinations
import json
from pathlib import Path
import sys
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
ROOT = ASSET.parents[2]
TMP = ROOT/'build/ram-feeder'
REF = ROOT/'art/refs/snow-processing'
sys.dont_write_bytecode = True
sys.path[:0]=[str(HERE),str(ASSET.parent/'processor-tower/source'),
              str(ROOT/'.agents/skills/game-model-workflow/scripts')]
from build_feeder import STUD, AXIS_Z, TRAVEL, DISPLAY, DOCK, FRAME, HOME, MOVERS, NAME, TOWER_FILE
from check_processor import extent, world_points, triangles, daylight, check_faces, inspect_model, budget_report


def load_export(stem):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ASSET/'export'/(stem+'.glb')))
    return {o.name:o for o in bpy.context.scene.objects}


def no_coincident_faces(objs):
    points,faces=[],[]
    for obj in objs:
        faces.extend(tuple(k+len(points) for k in tri) for tri in triangles(obj))
        points.extend(world_points(obj))
    mesh=bpy.data.meshes.new('Coverage check')
    mesh.from_pydata(points,[],faces)
    proxy=bpy.data.objects.new('Coverage check',mesh)
    collisions=check_faces(proxy)
    bpy.data.objects.remove(proxy)
    bpy.data.meshes.remove(mesh)
    assert not collisions, collisions[:8]


def bounds_dict(objs):
    return {obj.name:extent(world_points(obj)) for obj in objs}


def close_enough(a,b):
    return max(abs(x-y) for v,w in zip(a,b) for x,y in zip(v,w)) < 1e-5


def check():
    bpy.ops.wm.open_mainfile(filepath=str(HERE/(NAME+'.blend')))
    original=list(bpy.context.scene.objects)
    frame=bpy.data.objects[FRAME]
    assert set(o.name for o in original)=={FRAME,*MOVERS}
    for stroke in (0, 1, DISPLAY):
        frame['Stroke']=stroke
        frame.update_tag()
        bpy.context.view_layer.update()
        for i,name in enumerate(MOVERS,1):
            assert abs(bpy.data.objects[name].matrix_world.translation.y/STUD-(HOME+i*TRAVEL/4*stroke))<.001
    expected=bounds_dict(original)
    report=inspect_model(original)
    print('MODEL CHECK:',report['issues'],flush=True)
    assert report['ok'],report['issues']
    report['budget'],issues=budget_report(report, ROOT/'art/budgets.json','big_prop',HERE/(NAME+'.blend'),original)
    assert not issues,issues
    alone=load_export(NAME)
    assert set(alone)==set(expected)
    assert all(close_enough(expected[n],extent(world_points(o))) for n,o in alone.items())
    assert sum(len(triangles(o)) for o in alone.values())==report['totals']['tris']
    assert len({o.active_material for o in alone.values()})==1
    assert any(img.packed_file for img in bpy.data.images)
    no_coincident_faces(alone.values())
    # Check the actual tower source and the ready-aligned GLB have the same five parts.
    bpy.ops.wm.open_mainfile(filepath=str(TOWER_FILE))
    tower_source=bounds_dict(bpy.context.scene.objects)
    assembly=load_export('RamFeederWithTower')
    assert set(assembly)==set(expected)|set(tower_source)
    for name,box in tower_source.items():
        assert close_enough(box,extent(world_points(assembly[name])))
    for name,box in expected.items():
        shifted=[[v[0],v[1]+DOCK*STUD,v[2]] for v in box]
        assert close_enough(shifted,extent(world_points(assembly[name])))
    no_coincident_faces(assembly.values())
    all_points={n:world_points(o) for n,o in assembly.items()}
    faces={n:triangles(o) for n,o in assembly.items()}
    def bvh(n,coords):
        return BVHTree.FromPolygons(coords,faces[n],all_triangles=True)
    tower_trees={n:bvh(n,all_points[n]) for n in tower_source}
    for end in ('front','rear'):
        def orient(p):
            return p if end=='front' else Vector((-p.x,-p.y,p.z))
        static=bvh(FRAME,[orient(v) for v in all_points[FRAME]])
        for n,tree in tower_trees.items():
            assert not static.overlap(tree),(end,FRAME,n)
        for sample in range(101):
            t=sample/100
            moving={}
            for i,name in enumerate(MOVERS,1):
                shift=Vector((0,(t-DISPLAY)*TRAVEL*i/4*STUD,0))
                moving[name]=bvh(name,[orient(p+shift) for p in all_points[name]])
                assert not moving[name].overlap(static),(end,name,'frame',t)
                for other,tree in tower_trees.items():
                    assert not moving[name].overlap(tree),(end,name,other,t)
            for a,b in combinations(MOVERS,2):
                assert not moving[a].overlap(moving[b]),(end,a,b,t)
    # Full spin envelope of the two front drums versus entire feeder forward reach.
    rotor_near=min(abs((o.matrix_world.translation.y-DOCK*STUD)/STUD)-
                   max((p-o.matrix_world.translation).yz.length/STUD for p in world_points(o))
                   for o in assembly.values() if o.name.startswith('Front_'))
    max_nose=max(expected[FRAME][1][1]/STUD,expected['Pusher'][1][1]/STUD+(1-DISPLAY)*TRAVEL)
    assert rotor_near-max_nose>.30
    # Raycasts through the exported centreline floor return the actual sill and deck heights.
    def top_at(objects,x,y,from_z):
        p=Vector((x,y,from_z))*STUD
        hits=[]
        for o in objects:
            mat=o.matrix_world
            hit,local,_,_=o.ray_cast(mat.inverted()@p,Vector((0,0,-1)))
            if hit: hits.append((mat@local).z/STUD)
        return max(hits)
    sill=top_at([assembly['ProcessorTower']],0,DOCK+.21,1.2)
    deck=top_at([assembly[FRAME]],0,DOCK+.21,1.2)
    assert abs(sill-.56)<.001 and abs(deck-.70)<.001
    report['fit']={'tower':TOWER_FILE.name,'dock_y_from_tower_origin_blender_studs':DOCK,
                   'tongue_top_studs':round(deck,3),'tower_sill_studs':round(sill,3),
                   'tongue_underside_gap_studs':round(.59-sill,3),
                   'fully_rotating_drum_envelope_clearance_studs':round(rotor_near-max_nose,3),
                   'straight_rail_height_studs':1.20,'player_height_studs':5.1,
                   'lowest_point_studs':round(expected[FRAME][0][2]/STUD,4)}
    report['mechanism']={'stroke_studs':TRAVEL,'rest_fraction':DISPLAY,
                         'sampled_positions_per_intake':101,'intakes_tested':['front','rear'],
                         'cross_part_intersections':0,'coplanar_overlaps_at_rest':0,
                         'minimum_sleeve_engagement_studs':round(2.97-.12-TRAVEL/4,4)}
    report['files']={p.name:p.stat().st_size for p in [HERE/(NAME+'.blend'),*sorted((ASSET/'export').glob('*.glb'))]}
    (ASSET/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    return assembly


def render(assembly):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=12
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='Standard'
    scene.world=bpy.data.worlds.new('Skylight')
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value=(.8,.87,1,1)
    bg.inputs[1].default_value=.65
    daylight('Key',(-.40,.60,-1),1.9)
    daylight('Rim',(.5,-.4,-.8),.55)
    def material(name,color):
        mat=bpy.data.materials.new(name)
        mat.use_nodes=True
        mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
        return mat
    bpy.ops.mesh.primitive_plane_add(size=400,location=(0,0,-.002))
    bpy.context.object.data.materials.append(material('Studio floor',(.45,.56,.76)))
    bpy.ops.object.camera_add()
    cam=bpy.context.object
    cam.data.type='ORTHO'
    scene.camera=cam
    def snap(path,shapes,direction,width,height):
        direction=Vector(direction).normalized()
        rotation=(-direction).to_track_quat('-Z','Y')
        coords=[rotation.inverted()@p for obj in shapes for p in world_points(obj)]
        lo,hi=extent(coords)
        focus=rotation@((Vector(lo)+Vector(hi))*.5)
        cam.rotation_euler=rotation.to_euler()
        cam.location=focus+direction*25
        cam.data.ortho_scale=max(hi[0]-lo[0],(hi[1]-lo[1])*width/height)*1.13
        scene.render.resolution_x,scene.render.resolution_y=width,height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
    tray=[assembly[n] for n in [FRAME,*MOVERS]]
    tower=[o for o in assembly.values() if o not in tray]
    for o in tower:o.hide_render=True
    for view,direction in [('front',(0,-1,0)),('back',(0,1,0)),('side',(1,0,0)),('top',(0,0,1))]:
        snap(TMP/(view+'.png'),tray,direction,800,610)
    snap(REF/'ram-feeder-model.png',tray,(.59,-.96,1.04),920,820)
    (TMP/'three-quarter.png').write_bytes((REF/'ram-feeder-model.png').read_bytes())
    for o in tower:o.hide_render=False
    person=material('5.1 stud scale',(.19,.30,.40))
    def block(x,z,size):
        bpy.ops.mesh.primitive_cube_add(size=1,location=Vector((x-5.45,-14.7,z))*STUD)
        o=bpy.context.object
        o.dimensions=Vector(size)*STUD
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(person)
        bevel=o.modifiers.new('Corners','BEVEL')
        bevel.width=.021
        bevel.segments=1
        o.modifiers.new('Face normals','WEIGHTED_NORMAL')
        return o
    player=[block(x,1,(.98,.96,2)) for x in (-.5,.5)]
    player += [block(0,3,(1.99,1,2)),block(0,4.55,(1.4,1.05,1.1))]
    player += [block(x,3,(.60,.95,1.96)) for x in (-1.31,1.31)]
    # Loose material belongs to the demonstration scene only.
    snow=material('Snow load for scale',(.896,.922,.913))
    snowballs=[]
    for x,y,rx,ry,rz,angle in [(.35,-4.4,1.22,1.14,.94,.21),(-.57,-5.35,.84,.8,.63,.77),
                               (.98,-5.28,.70,.65,.48,.4),(-1.59,-5.45,.30,.25,.22,.64)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,
            location=Vector((x,DOCK+y,.70+rz*.28))*STUD)
        obj=bpy.context.object
        obj.scale=Vector((rx,ry,rz))*STUD
        obj.rotation_euler.z=angle
        obj.data.materials.append(snow)
        snowballs.append(obj)
    snap(REF/'ram-feeder-docked.png',tray+tower+player+snowballs,(1.30,-.96,.79),1200,780)
    for o in player+snowballs:o.hide_render=True
    for i,n in enumerate(MOVERS,1):
        assembly[n].location.y+=(1-DISPLAY)*TRAVEL*i/4*STUD
    bpy.context.view_layer.update()
    snap(TMP/'extended.png',tray+tower,(.85,-1.3,1.28),900,690)
    (REF/'ram-feeder-extended.png').write_bytes((TMP/'extended.png').read_bytes())


if __name__=='__main__':
    TMP.mkdir(parents=True,exist_ok=True)
    objects=check()
    if '--audit-only' not in sys.argv:
        render(objects)
