"""Additional close views of each template, without saving changes to the master."""
from pathlib import Path
import sys
import bpy
import bmesh

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'.agents/skills/game-model-workflow/scripts'))
import studio_scene

asset = Path(__file__).resolve().parent.parent
body = bpy.data.objects['Snowbanks_Body']
body.hide_render = True
names = ['Pillow','Windbank','Crescent','Clumps','TreeSkirt','Shoulder']
for index, name in enumerate(names):
    x, y = (index%3-1)*19*.28, -(index//3-.5)*14*.28
    obj = body.copy()
    obj.data = body.data.copy()
    obj.name = 'Detail_'+name
    bpy.context.scene.collection.objects.link(obj)
    obj.hide_render = False
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    outside = [v for v in bm.verts if abs(v.co.x-x)>9.5*.28 or abs(v.co.y-y)>7*.28]
    bmesh.ops.delete(bm, geom=outside, context='VERTS')
    bm.to_mesh(obj.data)
    bm.free()
    rig = studio_scene.add_review_rig([obj])
    bpy.context.scene.view_settings.exposure = -1.25
    studio_scene.render_views({'three-quarter':rig['three-quarter']}, asset/'review/details'/name, 768)
    obj.hide_render = True
    bpy.data.objects.remove(obj, do_unlink=True)
print('Six individual template views rendered; master not saved')
