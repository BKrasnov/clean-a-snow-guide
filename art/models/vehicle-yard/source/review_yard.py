"""Inspect the re-imported export, then render it over short grass."""
import json
from math import radians
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ASSET.parent/'rustic-stalls/source'))
from check_stalls import inspect
from build_yard import STUD

# Rounded outward from the RBXM coordinates of the skids, tracks and tyres.
CONTACTS={
    'KESTREL_07': (-35.79,-25.83,-6.81,10.25),
    'CartoonTank': (-22.59,-8.21,-10.88,11.65),
    'CartoonTruck': (-3.88,5.37,-7.74,6.53),
    'CartoonPickup': (10.91,19.65,-8.78,5.68),
    'CartoonSnowmobile': (27.37,35.57,-10.40,9.96),
}


def inspect_import(objects):
    data={obj.name:inspect(obj) for obj in objects}
    ground=next(obj for obj in objects if obj.name=='VehicleYard_Ground')
    logs=next(obj for obj in objects if obj.name=='VehicleYard_LogEnds')
    tree=BVHTree.FromPolygons([v.co/STUD for v in ground.data.vertices],
                              [p.vertices[:] for p in ground.data.polygons])
    log_tree=BVHTree.FromPolygons([v.co/STUD for v in logs.data.vertices],
                                  [p.vertices[:] for p in logs.data.polygons])
    def hit(bvh,x,y):
        return bvh.ray_cast((x,y,3),(0,0,-1),5)[0]
    placement={}
    for name,(left,right,front,back) in CONTACTS.items():
        samples=0
        for i in range(19):
            x=left+(right-left)*i/18
            for j in range(31):
                y=front+(back-front)*j/30
                contact=hit(tree,x,y)
                assert contact is not None and contact.z>-.173,(name,x,y)
                samples+=1
            for j in range(51):
                y=front+(-24-front)*j/50
                assert hit(log_tree,x,y) is None,(name,x,y)
        placement[name]={'contact_studs':[left,right,front,back],'surface_samples':samples,
                         'unobstructed_front':'No log ends across contact width toward local -Y'}
    assert all(not o['close_coplanar_pairs'] and not o['nonmanifold_edges_after_position_weld']
               for o in data.values()),data
    tris=sum(o['triangles'] for o in data.values())
    assert tris<=3000,tris
    return {'assets':data,'triangles':tris,'stud_meters':STUD,'vehicle_placement':placement,
            'yard_height_transition_studs':.17,'intentional_contacts':'Log bottoms embed in the dirt edge.'}


def pictures(scene,out):
    scene.render.engine='CYCLES'
    scene.cycles.samples=24
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='Standard'
    scene.view_settings.exposure=-.32
    scene.world=bpy.data.worlds.new('Soft daylight')
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value=(.52,.69,.90,1)
    bg.inputs[1].default_value=.55
    sun=bpy.data.lights.new('Sun','SUN')
    sun.energy=2.15
    sun.color=(1,.93,.81)
    sun.angle=radians(8)
    light=bpy.data.objects.new('Sun',sun)
    scene.collection.objects.link(light)
    light.rotation_euler=Vector((.48,.57,-1)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=300,location=(0,0,-.183*STUD))
    grass=bpy.data.materials.new('Short grass')
    grass.use_nodes=True
    grass.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.17,.49,.056,1)
    grass.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95
    bpy.context.object.data.materials.append(grass)
    camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
    scene.collection.objects.link(camera)
    scene.camera=camera
    camera.data.type='ORTHO'
    scene.render.image_settings.file_format='JPEG'
    scene.render.image_settings.quality=92
    def shoot(name,pos,target,width,res):
        camera.location=Vector(pos)*STUD
        camera.rotation_euler=(Vector(target)*STUD-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.ortho_scale=width*STUD
        scene.render.resolution_x,scene.render.resolution_y=res
        scene.render.filepath=str(out/(name+'.jpg'))
        bpy.ops.render.render(write_still=True)
    shoot('Court',(24,-87,74),(0,0,0),99,(1560,960))
    shoot('DriveOut',(4,-82,29),(0,-3,0),96,(1350,650))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source=ASSET/'export/VehicleYard.glb'
    bpy.ops.import_scene.gltf(filepath=str(source),merge_vertices=True)
    objects=list(bpy.context.scene.objects)
    assert {o.name for o in objects}=={'VehicleYard_Ground','VehicleYard_LogEnds'}
    out=ASSET/'review'
    out.mkdir(exist_ok=True)
    report=inspect_import(objects)
    (out/'geometry.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('YARD CHECK',report['triangles'],flush=True)
    if '--audit-only' not in sys.argv:
        pictures(bpy.context.scene,out)


if __name__=='__main__':
    main()
