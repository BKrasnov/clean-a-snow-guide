"""Round-trip all deliveries and photograph the imported meshes at one common scale."""
import json
from math import radians
from pathlib import Path
import sys
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
MODELS = ASSET.parent
ROOT = MODELS.parents[1]
REVIEW = ASSET/'review'
sys.dont_write_bytecode = True
sys.path[:0] = [str(HERE),str(MODELS/'forest-trees/source'),str(MODELS/'garden-plants/source'),
                str(ROOT/'.agents/skills/game-model-workflow/scripts')]
from build_snow_trees import STUD, TREES
from check_trees import snapshot, mat
from review_exports import check_faces
from contact_check import separate_parts
import model_check


def imported(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return {o.name:o for o in bpy.context.scene.objects}


def inspect():
    bpy.ops.wm.open_mainfile(filepath=str(HERE/'LobbySnowTrees.blend'))
    originals = list(bpy.context.scene.objects)
    base = model_check.inspect_model(originals)
    assert base['ok'],base['issues']
    expected = {}
    audit = {}
    for ob in originals:
        ob.location.x = 0
    bpy.context.view_layer.update()
    for ob in originals:
        expected[ob.name] = snapshot(ob)
        assert not separate_parts(ob.data),ob.name
    for name,height,offset,draw in TREES:
        objects = imported(ASSET/'export'/(name+'.glb'))
        assert set(objects)=={name}
        ob = objects[name]
        points,bounds,tris = snapshot(ob)
        assert points==expected[name][0] and tris==expected[name][2]
        assert ob.location.length < .00001 and abs(bounds[0][2])<.00001
        assert abs(bounds[1][2]/STUD-height)<.0001
        assert tris<=1200 and len(ob.data.materials)==1
        assert any(n.type=='TEX_IMAGE' and n.image.packed_file for n in ob.active_material.node_tree.nodes)
        overlaps=check_faces(ob)
        assert not overlaps,(name,overlaps[:6])
        audit[name] = dict(studs=[round((b-a)/STUD,2) for a,b in zip(*bounds)],
                           triangles=tris,coplanar_overlaps=len(overlaps),materials=1)
    objects = imported(ASSET/'export/LobbySnowTrees.glb')
    assert set(objects)==set(expected)
    for name,height,offset,draw in TREES:
        ob=objects[name]
        assert abs(ob.location.x/STUD-offset)<.001
        ob.location.x=0
        bpy.context.view_layer.update()
        points,_,tris=snapshot(ob)
        assert points==expected[name][0] and tris==expected[name][2]
        ob.location.x=offset*STUD
    bpy.context.view_layer.update()
    (REVIEW/'report.json').write_text(json.dumps(dict(source=base,exports=audit),indent=2),encoding='utf8')
    return objects


def render(objects):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=10
    scene.cycles.use_denoising=True
    scene.world=bpy.data.worlds.new('Winter daylight')
    scene.world.use_nodes=True
    sky=scene.world.node_tree.nodes.get('Background')
    sky.inputs[0].default_value=(.86,.92,1,1)
    sky.inputs[1].default_value=.62
    scene.view_settings.view_transform='Khronos PBR Neutral'
    bpy.ops.mesh.primitive_plane_add(size=600,location=(0,0,-.004))
    bpy.context.object.data.materials.append(mat('Backdrop',(.40,.54,.66)))
    for pos,energy in [((-5,-6,9),2.1),((4,2,6),.55)]:
        light=bpy.data.lights.new('Soft Sun','SUN')
        light.energy=energy
        light.angle=radians(17)
        ob=bpy.data.objects.new('Soft Sun',light)
        scene.collection.objects.link(ob)
        ob.rotation_euler=(-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add()
    cam=bpy.context.object
    cam.data.type='ORTHO'
    cam.data.ortho_scale=16.95
    scene.camera=cam
    scene.render.resolution_x=1536
    scene.render.resolution_y=550
    scene.render.resolution_percentage=100
    for name,angle,elevation in [('front',0,.035),('side',90,.035),('back',180,.035),
                                  ('top',0,10000),('three-quarter',24,.16)]:
        for ob in objects.values():
            ob.rotation_mode='XYZ'
            ob.rotation_euler.z=radians(angle)
        target=Vector((-.45,0,0 if name=='top' else 2.47))
        direction=Vector((0,-1,elevation)).normalized()
        cam.location=target+direction*45
        cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(REVIEW/(name+'.png'))
        bpy.ops.render.render(write_still=True)

if __name__=='__main__':
    REVIEW.mkdir(exist_ok=True)
    render(inspect())
