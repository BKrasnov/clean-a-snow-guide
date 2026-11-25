"""Validate source and both delivery formats, then render reimported geometry at a common scale."""
import json
from math import radians
from pathlib import Path
import sys
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
ROOT=ASSET.parents[2]
TMP=ROOT/'build/forest-trees'
REF=ROOT/'art/refs/map-border'
sys.dont_write_bytecode=True
sys.path[:0]=[str(HERE),str(ASSET.parent/'garden-plants/source'),str(ROOT/'.agents/skills/game-model-workflow/scripts')]
from build_trees import STUD,NAMES,HEIGHTS,POSITIONS
from contact_check import separate_parts
from review_exports import check_faces
from plant_mesh import COLORS
import model_check

def snapshot(ob):
    mesh=ob.data
    mesh.calc_loop_triangles()
    xyz=[ob.matrix_world@v.co for v in mesh.vertices]
    points=sorted(set(tuple(round(t,5) for t in p) for p in xyz))
    bounds=[[fn(p[k] for p in xyz) for k in range(3)] for fn in (min,max)]
    return points,bounds,len(mesh.loop_triangles)

def audit():
    bpy.ops.wm.open_mainfile(filepath=str(HERE/'ForestTrees.blend'))
    originals=list(bpy.context.scene.objects)
    assert {o.name for o in originals}==set(NAMES)
    report=model_check.inspect_model(originals)
    geometry={}
    for ob in originals:
        ob.location.x=0
    bpy.context.view_layer.update()
    for ob in originals:
        geometry[ob.name]=snapshot(ob)
    report['detached']={ob.name:separate_parts(ob.data) for ob in originals}
    report['exports']={}
    for name,height in zip(NAMES,HEIGHTS):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(ASSET/'export'/(name+'.glb')))
        ob,=bpy.context.scene.objects
        assert ob.type=='MESH' and ob.name==name and ob.location.length<1e-5
        points,bounds,tris=snapshot(ob)
        reference,_,expected=geometry[name]
        assert points==reference and tris==expected,(name,tris,expected)
        assert abs(bounds[0][2])<.0001 and abs(bounds[1][2]/STUD-height)<.001
        assert len(ob.data.materials)==1
        cols=list(COLORS)
        used={cols[int(v.uv.y*4)*8+int(v.uv.x*8)] for v in ob.data.uv_layers.active.data}
        assert used<=set(('deep','green','leaf','lime','bark','wood','cream','dark','tan','earth'))
        assert any(n.type=='TEX_IMAGE' and n.image.packed_file for n in ob.active_material.node_tree.nodes)
        report['exports'][name]={'studs':[round((b-a)/STUD,3) for a,b in zip(*bounds)],
            'triangles':tris,'materials':1,'colors':sorted(used),'coplanar':check_faces(ob)}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ASSET/'export/ForestTrees.glb'))
    objects={o.name:o for o in bpy.context.scene.objects}
    assert set(objects)==set(NAMES)
    for name,x in zip(NAMES,POSITIONS):
        ob=objects[name]
        assert abs(ob.location.x/STUD-x)<.001
        ob.location.x=0
        bpy.context.view_layer.update()
        points,_,tris=snapshot(ob)
        assert points==geometry[name][0] and tris==geometry[name][2],name
        ob.location.x=x*STUD
    bpy.context.view_layer.update()
    (ASSET/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    return objects,report

def mat(name,rgba):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgba,1)
    bs.inputs['Roughness'].default_value=.9
    return m

def review(objects):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=10
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='Khronos PBR Neutral'
    scene.cycles.diffuse_bounces=1
    scene.world=bpy.data.worlds.new('Studio')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.96,.97,1,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.53
    bpy.ops.mesh.primitive_plane_add(size=5000,location=(0,0,-.002))
    floor=bpy.context.object
    floor.data.materials.append(mat('Paper',(.49,.59,.71)))
    for aim,energy in [((-4,-6,9),2.0),((6,3,7),.65)]:
        light=bpy.data.lights.new('Daylight','SUN')
        light.energy=energy
        light.angle=radians(16)
        ob=bpy.data.objects.new('Daylight',light)
        scene.collection.objects.link(ob)
        ob.rotation_euler=(-Vector(aim)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add()
    cam=bpy.context.object
    cam.data.type='ORTHO'
    cam.data.ortho_scale=18.6
    scene.camera=cam
    def take(path,eye,target,scale=18.6):
        sight=(Vector(eye)-Vector(target)).normalized()
        cam.location=Vector(target)+300*sight
        cam.data.clip_end=1500
        cam.rotation_euler=(Vector(target)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale=scale
        scene.render.resolution_x=1780
        scene.render.resolution_y=650
        scene.render.resolution_percentage=100
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
    for name,degrees in [('front',0),('side',90),('back',180),('top',0),('three-quarter',26)]:
        for ob in objects.values():
            ob.rotation_mode='XYZ'
            # glTF importer bakes the Y-up conversion into the rotation; preserve it.
            ob.rotation_euler.z=radians(degrees)
        if name=='top':
            take(TMP/(name+'.png'),(.35,-.001,25),(.35,0,0))
        else:
            eye=(.35,-25,3.65 if name=='three-quarter' else 2.90)
            take(TMP/(name+'.png'),eye,(.35,0,2.48))
    for ob in objects.values():
        ob.rotation_euler.z=0
    avatar=mat('Player (preview)',(.18,.36,.48))
    def block(center,size):
        x,y,z=center
        bpy.ops.mesh.primitive_cube_add(size=1,location=((x+.0)*STUD,(y-1.3)*STUD,z*STUD))
        ob=bpy.context.object
        ob.dimensions=tuple(t*STUD for t in size)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        ob.data.materials.append(avatar)
        mod=ob.modifiers.new('Edges','BEVEL')
        mod.width=.014
        mod.segments=1
        ob.modifiers.new('Normals','WEIGHTED_NORMAL')
    for x in (-.50,.50):block((x,0,1),(.97,.96,2))
    block((0,0,3),(1.98,.98,2))
    for x in (-1.29,1.29):block((x,0,3),(.55,.96,1.97))
    block((0,0,4.55),(1.4,1.05,1.1))
    take(REF/'forest-models-scale.png',(.35,-25,4.1),(.35,0,2.52),18.6)

if __name__=='__main__':
    objects,report=audit()
    if '--audit-only' not in sys.argv:
        review(objects)
    assert report['ok'],report['issues']
    assert not any(report['detached'].values()),report['detached']
    assert all(not r['coplanar'] for r in report['exports'].values()),report['exports']
