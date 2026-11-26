"""Check combined and standalone GLBs, then photograph the imported geometry."""
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path[:0]=[str(HERE),str(HERE.parents[1]/'rustic-stalls/source')]
from build_decor import ASSET, LAYOUT, S
from check_stalls import inspect

out=ASSET/'review'
source=ASSET/'export'
standalone={}
for name in LAYOUT:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source/(name+'.glb')),merge_vertices=True)
    obj,=bpy.context.scene.objects
    assert obj.name==name and obj.location.length<1e-6
    standalone[name]=inspect(obj)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source/'HolidayDecor.glb'),merge_vertices=True)
objects={obj.name:obj for obj in bpy.context.scene.objects}
assert set(objects)==set(LAYOUT)
report={}
for name,obj in objects.items():
    report[name]=inspect(obj)
    assert report[name]==standalone[name] and (obj.location-Vector(LAYOUT[name])*S).length<1e-5
    report[name]['degenerate_triangles']=sum(t.area<1e-8 for t in obj.data.loop_triangles)
    record=report[name]
    budget=3000 if name=='ChristmasSpruce' else 1000
    assert record['triangles']<=budget and record['material_slots']==1
    assert not (record['degenerate_triangles'] or record['close_coplanar_pairs']
                or record['nonmanifold_edges_after_position_weld'])
    print('QA',name,report[name]['triangles'],len(report[name]['close_coplanar_pairs']),
          report[name]['nonmanifold_edges_after_position_weld'],report[name]['degenerate_triangles'],flush=True)
(out/'geometry.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def surface(obj,shift):
    coords=[v.co+Vector((shift*S,0,0)) for v in obj.data.vertices]
    return BVHTree.FromPolygons(coords,[t.vertices[:] for t in obj.data.loop_triangles],all_triangles=True)

modules=[objects['StringLights'],objects['PineGarland']]
for left in modules:
    for right in modules:
        assert not surface(left,0).overlap(surface(right,7.2)),(left.name,right.name)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=16
scene.cycles.use_denoising=True
scene.view_settings.view_transform='Khronos PBR Neutral'
scene.world=bpy.data.worlds.new('Cool studio')
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes['Background']
bg.inputs[0].default_value=(.75,.85,1,1); bg.inputs[1].default_value=.74
sun=bpy.data.lights.new('Softbox','SUN')
sun.energy=2.5; sun.angle=.19; sun.color=(1,.92,.82)
ob=bpy.data.objects.new('Softbox',sun);scene.collection.objects.link(ob)
ob.rotation_euler=Vector((.57,.70,-1)).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=300,location=(0,0,-.003))
floor=bpy.data.materials.new('Studio sweep')
floor.use_nodes=True
floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.44,.59,.78,1)
bpy.context.object.data.materials.append(floor)
camera=bpy.data.objects.new('Product camera',bpy.data.cameras.new('Product camera'))
scene.collection.objects.link(camera);scene.camera=camera
camera.data.type='ORTHO'
scene.render.image_settings.file_format='PNG'
scene.render.resolution_percentage=100

def shot(name,target,direction,width,size):
    target=Vector(target)*S
    ray=Vector(direction).normalized()
    camera.location=target+ray*40
    camera.rotation_euler=(-ray).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=width*S
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)

shot('Collection',(0,0,6.4),(.025,-1,.12),19.7,(1320,980))
objects['ChristmasSpruce'].hide_render=objects['WrappedGifts'].hide_render=True
shot('HangingFront',(4.8,.1,6.16),(.11,-1,.04),11.8,(1030,930))
shot('HangingBack',(4.8,.1,6.16),(-.17,1,.07),11.8,(1030,930))
