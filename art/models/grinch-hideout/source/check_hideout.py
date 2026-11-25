"""Verify player clearances and surface separation on the saved Blender scene."""
from pathlib import Path
import sys
import json
import bpy
from mathutils import Vector

asset = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(asset.parent / 'starter-farmhouse/source'))
from check_surface_overlap import audit

scene = bpy.context.scene
def hit(point, direction, length):
    result = scene.ray_cast(bpy.context.evaluated_depsgraph_get(), Vector(point),
                            Vector(direction), distance=length)
    return result[4].name if result[0] else None

report = {}
for frame in (1, 36):
    scene.frame_set(frame)
    overlaps = audit(.002, False, 'GrinchHideout')
    report[f'overlaps_frame_{frame}'] = overlaps
    assert overlaps['overlapping_face_pairs'] == 0, overlaps
    if frame == 1:
        assert hit((0,-5,1.5),(0,1,0),3) == 'Entrance gate - hinged'
    else:
        for x in (-.8, 0, .8):
            for z in (.24, .95, 1.94):
                assert hit((x,-5,z),(0,1,0),4.4) is None, (x,z)
for x in (-.64,.64):
    for y in (-1.92,-.76):
        for dx in (-.30,0,.30):
            for dy in (-.20,0,.20):
                p = (x+dx,y+dy,.14)
                assert hit(p,(0,0,1),1.82) is None, p
                assert hit(p,(0,0,-1),.04) == 'Snow floor', p
guards = bpy.data.collections['NPC preview - three guards'].objects
assert len(guards) == 3 and len({g.data for g in guards}) == 1
guards[0].data.calc_loop_triangles()
assert all(i.packed_file for i in bpy.data.images if i.type == 'IMAGE' and i.has_data)
assert len([o for o in scene.objects if o.name.startswith('Gift ')]) == 4
report.update(open_gate_rays=9, clear_avatar_positions=4, clearance_height_m=1.82,
              guard_instances=len(guards), triangles_per_guard=len(guards[0].data.loop_triangles))
(asset/'reports/walkthrough.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
