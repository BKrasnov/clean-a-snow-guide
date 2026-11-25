"""Build the editable lineup and 36 origin-centred, metric Roblox imports."""
import argparse
import importlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
ROOT=ASSET.parents[2]
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/'.agents/skills/game-model-workflow/scripts'))
import model_check
from plant_mesh import Plant,palette
from contact_check import separate_parts

STUD=.28
BEDS=json.loads((ROOT/'src/ReplicatedStorage/CleanSnow/Data/garden.json').read_text())['Plots']['Beds']
PLANT_LIMITS=json.loads((ROOT/'art/budgets.json').read_text(encoding='utf-8'))['classes']['plant']
# The tall trees and simple, low fruits should still have different sizes in one bed.
HEIGHTS=[1.65,2.05,1.66,.98,2.50,1.54,1.80,2.05,2.11,3.18,2.30,3.60,
         1.44,.99,3.68,3.69,2.70,2.29,3.52,2.68,3.61,1.50,1.82,2.27,
         1.15,2.22,2.42,3.55,2.52,3.37,2.45,1.24,2.94,2.50,3.75,2.66]
WIDTHS=[1.8,1.48,1.55,1.69,2.35,2.16,2.24,1.6,1.78,2.06,2.10,2.65,
        2.64,2.66,2.04,2.68,2.06,2.36,2.67,2.42,2.62,1.70,1.97,2.38,
        2.43,1.60,1.95,2.68,2.42,2.53,2.10,2.47,1.91,2.22,2.68,2.11]

def bounds(vertices):
    return ([min(p[i] for p in vertices) for i in range(3)],
            [max(p[i] for p in vertices) for i in range(3)])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--only',nargs='*',type=int)
    opts=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    scene.view_settings.view_transform='AgX'
    surface=palette()
    collection=bpy.data.collections.new('Garden plants')
    scene.collection.children.link(collection)
    (ASSET/'export').mkdir(exist_ok=True)
    (ASSET/'reports').mkdir(exist_ok=True)
    report=[]
    objects=[]
    for ref in sorted((ROOT/'art/refs/garden-plants').glob('*.png')):
        num=int(ref.stem[:2])
        if opts.only and num not in opts.only:
            continue
        module='crops' if num<=14 else 'exotics' if num<=28 else 'mythics'
        builder=Plant(ref.stem+'_Body',collection,surface)
        importlib.import_module(module).build(num,builder)
        lo,hi=bounds(builder.vertices)
        span=[b-a for a,b in zip(lo,hi)]
        scale=STUD*min(HEIGHTS[num-1]/span[2],WIDTHS[num-1]/max(span[:2]))
        center=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
        builder.vertices=[(Vector(p)-center)*scale for p in builder.vertices]
        obj=builder.object()
        objects.append(obj)
        obj['catalog_id']=num
        obj['reference']=ref.name
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        path=ASSET/'export'/(ref.stem+'.glb')
        bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB')
        check=model_check.inspect_model([obj])
        dimensions=[round(v*scale/STUD,4) for v in span]
        assert max(dimensions[:2])<=BEDS['PlantWidth'] and dimensions[2]<=BEDS['PlantHeight']
        loose=separate_parts(obj.data)
        limits_ok=(check['totals']['tris']<=PLANT_LIMITS['tris'] and
                   len(check['totals']['materials'])<=PLANT_LIMITS['materials'])
        report.append(dict(id=num,file=path.name,dimensions_studs=dimensions,disconnected=loose,
                           tris=check['totals']['tris'],materials=len(check['totals']['materials']),
                           issues=check['issues'],ok=check['ok'] and not loose and limits_ok))
        print('PLANT_CHECK',num,report[-1]['tris'],check['issues'],flush=True)
    if opts.only:
        out=ROOT/'build/garden-models'/('subset-'+str(min(opts.only))+'.json')
    else:
        assert len(objects)==36
        for i,obj in enumerate(objects):
            obj.location=((i%6-2.5)*4.3*STUD,(2.5-i//6)*4.6*STUD,0)
        bpy.ops.object.select_all(action='DESELECT')
        for area in bpy.context.screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active
                space.shading.type='SOLID'
                space.shading.color_type='TEXTURE'
                space.shading.light='STUDIO'
                space.overlay.show_floor=False
                space.region_3d.view_rotation=Vector((.2,-7,5)).to_track_quat('Z','Y')
                space.region_3d.view_perspective='ORTHO'
                space.region_3d.view_location=(0,0,.23)
                space.region_3d.view_distance=13
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'GardenPlants_master.blend'),compress=True)
        out=ASSET/'reports/models.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
