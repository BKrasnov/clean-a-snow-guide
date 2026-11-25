"""Check the editable model and its GLB, exercise the shafts, render the actual import."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SOURCE = Path(__file__).resolve().parent
ASSET = SOURCE.parent
ROOT = ASSET.parents[2]
TMP = ROOT / 'build/processor-tower'
GALLERY = ROOT / 'art/refs/snow-processing'
sys.dont_write_bytecode = True
sys.path[:0] = [str(SOURCE), str(ROOT / '.agents/skills/game-model-workflow/scripts'),
                str(ASSET.parent / 'garden-plants/source')]
from build_processor import STUD, LEVELS, ROTOR_NAMES, DRUM_Y
from model_check import budget_report, inspect_model
from review_exports import check_faces, daylight


def world_points(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def extent(points):
    return [[fn(v[k] for v in points) for k in range(3)] for fn in (min, max)]


def triangles(obj):
    obj.data.calc_loop_triangles()
    return [tuple(t.vertices) for t in obj.data.loop_triangles]


def audit():
    TMP.mkdir(exist_ok=True, parents=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE / 'SnowProcessorTower.blend'))
    objects = list(bpy.context.scene.objects)
    report = inspect_model(objects)
    report['budget'], issues = budget_report(report, ROOT/'art/budgets.json', 'big_prop',
                                            SOURCE/'SnowProcessorTower.blend', objects)
    assert not issues, issues
    assert report['ok'], report['issues']
    source_bounds = {o.name:extent(world_points(o)) for o in objects}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ASSET / 'export/SnowProcessorTower.glb'))
    objects = {o.name:o for o in bpy.context.scene.objects}
    assert set(objects) == {'ProcessorTower', *ROTOR_NAMES}
    assert len({o.data for o in objects.values()}) == 5
    assert len({o.active_material for o in objects.values()}) == 1
    img = next(i for i in bpy.data.images if i.packed_file)
    assert tuple(img.size) == (32,8)
    verts, faces = [], []
    polys = {n:triangles(o) for n,o in objects.items()}
    for name, obj in objects.items():
        points = world_points(obj)
        assert max(abs(a-b) for aa,bb in zip(source_bounds[name],extent(points))
                   for a,b in zip(aa,bb)) < 1e-5
        faces.extend(tuple(i+len(verts) for i in f) for f in polys[name])
        verts.extend(points)
    assert len(faces) == report['totals']['tris'] and len(faces) <= 3000
    mesh = bpy.data.meshes.new('World triangles')
    mesh.from_pydata(verts, [], faces)
    proxy = bpy.data.objects.new('Audit', mesh)
    conflicts = check_faces(proxy)
    bpy.data.objects.remove(proxy)
    bpy.data.meshes.remove(mesh)
    low, high = extent(verts)
    assert abs(low[2]) < 1e-5
    report['assembly'] = dict(mesh_triangles={n:len(t) for n,t in polys.items()},
                              dimensions_studs=[round((b-a)/STUD,3) for a,b in zip(low,high)],
                              materials=1, texture=list(img.size), class_limits={'big_prop':3000},
                              coplanar_overlaps=conflicts, scale_player_studs=5.1)
    def collision_tree(points, tris):
        return BVHTree.FromPolygons(points, tris, all_triangles=True)
    body = collision_tree(world_points(objects['ProcessorTower']), polys['ProcessorTower'])
    clearances = {}
    for end, sign in [('Front',-1), ('Rear',1)]:
        radii = []
        for level,z in LEVELS.items():
            name = f'{end}_{level}'
            obj = objects[name]
            expected = Vector((0,sign*DRUM_Y,z))*STUD
            assert (obj.matrix_world.translation-expected).length < 1e-5
            unit_x = Vector((1,0,0))
            assert (obj.matrix_world.to_3x3() @ unit_x-unit_x).length < 1e-5
            assert obj['rotation_axis']=='local X'
            rel = [p-expected for p in world_points(obj)]
            radii.append(max(math.hypot(p.y,p.z) for p in rel)/STUD)
            for degree in range(360):
                rot = Matrix.Rotation(math.radians(degree),3,'X')
                tree = collision_tree([expected+rot@p for p in rel],polys[name])
                assert not tree.overlap(body), (name,degree)
        # The maximum radial envelopes are disjoint even with unrelated angular velocities.
        gap = LEVELS['Upper']-LEVELS['Lower']-sum(radii)
        assert gap > .25
        clearances[end] = round(gap,4)
    report['rotation'] = dict(local_axis='X', steps_per_revolution=360, rotor_housing_contacts=0,
                              minimum_inter_rotor_clearance_studs=clearances)
    (ASSET/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert not conflicts, conflicts[:10]
    return list(objects.values())


def render(objects):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = 'Standard'
    scene.world = bpy.data.worlds.new('Skylight')
    scene.world.use_nodes = True
    sky = scene.world.node_tree.nodes['Background']
    sky.inputs[0].default_value = (.79,.87,1,1)
    sky.inputs[1].default_value = .58
    daylight('Key',(-.46,.6,-1),2.0)
    daylight('Rim',(.38,-.65,-.7),.65)
    bpy.ops.mesh.primitive_plane_add(size=600, location=(0,0,-.002))
    ground = bpy.data.materials.new('Studio floor')
    ground.use_nodes = True
    ground.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.48,.60,.79,1)
    bpy.context.object.data.materials.append(ground)
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    camera.data.type = 'ORTHO'
    def snap(path, direction, items, size):
        direction = Vector(direction).normalized()
        rotation = (-direction).to_track_quat('-Z','Y')
        coords = [rotation.inverted() @ p for obj in items for p in world_points(obj)]
        low,high = extent(coords)
        mid = rotation @ ((Vector(low)+Vector(high))*.5)
        camera.rotation_euler = rotation.to_euler()
        camera.location = mid+direction*25
        camera.data.ortho_scale = max(high[0]-low[0],(high[1]-low[1])*size[0]/size[1])*1.15
        scene.render.resolution_x,scene.render.resolution_y = size
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
    for view,direction in [('front',(0,-1,0)),('back',(0,1,0)),('side',(1,0,0)),('top',(0,0,1))]:
        snap(TMP/(view+'.png'),direction,objects,(720,640))
    snap(GALLERY/'tower-model.png',(.89,-1,.34),objects,(940,900))
    (TMP/'three-quarter.png').write_bytes((GALLERY/'tower-model.png').read_bytes())
    player = bpy.data.materials.new('Player scale')
    player.use_nodes = True
    player.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.17,.32,.43,1)
    def block(x,z,size):
        bpy.ops.mesh.primitive_cube_add(size=1,location=Vector((x-5,-6.35,z))*STUD)
        obj = bpy.context.object
        obj.dimensions = Vector(size)*STUD
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        obj.data.materials.append(player)
        bevel = obj.modifiers.new('Corners','BEVEL')
        bevel.width,bevel.segments=.017,1
        obj.modifiers.new('Face normals','WEIGHTED_NORMAL')
        return obj
    mannequin = [block(x,1,(.98,.96,2)) for x in (-.5,.5)]
    mannequin += [block(0,3,(1.99,1,2)),block(0,4.55,(1.4,1.05,1.1))]
    mannequin += [block(x,3,(.61,.96,1.96)) for x in (-1.31,1.31)]
    snap(GALLERY/'tower-player-scale.png',(.47,-1,.19),objects+mannequin,(960,720))


if __name__=='__main__':
    checked = audit()
    if '--audit-only' not in sys.argv:
        render(checked)
