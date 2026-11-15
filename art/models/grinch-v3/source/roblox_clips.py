"""Grinch v3 (card e49171): the five clips as data for Roblox, one JSON per clip.

    blender -b <abs Grinch_master.blend> --python roblox_clips.py -- --out <abs folder> [--step 1]

For every frame (every --step-th, and the last one) and every deforming bone: the bone's turn from its rest in
armature space, D = R_pose * R_rest^-1 (quaternion w, x, y, z), and for the hips their move from rest in metres
(armature space). Roblox turns these into Bone.Transform poses of a KeyframeSequence (tools in Studio: the mapping
Blender (x, y, z) -> Roblox body space (-x, z, y), 1 m = 1 / 0.28 studs, is measured on the imported bones).
"""
import argparse
import json
import sys
from pathlib import Path

import bpy

RIG = 'Grinch_Rig'
CLIPS = ('Idle', 'Walk', 'Attack', 'Hit', 'Stunned')
LOOPS = {'Idle': True, 'Walk': True, 'Attack': False, 'Hit': False, 'Stunned': True}


def main(argv):
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--step', type=int, default=1)
    args = parser.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    rig = bpy.data.objects[RIG]
    bones = [b for b in rig.data.bones if b.use_deform]
    rest = {b.name: b.matrix_local.to_quaternion() for b in bones}
    rest_head = rig.data.bones['mixamorig:Hips'].head_local.copy()
    fps = scene.render.fps / scene.render.fps_base
    for name in CLIPS:
        action = bpy.data.actions[name]
        rig.animation_data.action = action
        if action.slots:
            rig.animation_data.action_slot = action.slots[0]
        start, end = (int(round(v)) for v in action.frame_range)
        frames = list(range(start, end + 1, args.step))
        if frames[-1] != end:
            frames.append(end)
        keys = []
        for f in frames:
            scene.frame_set(f)
            pose = {}
            for b in bones:
                pb = rig.pose.bones[b.name]
                d = pb.matrix.to_quaternion() @ rest[b.name].inverted()
                pose[b.name] = [round(v, 5) for v in (d.w, d.x, d.y, d.z)]
            hips = rig.pose.bones['mixamorig:Hips'].head - rest_head
            keys.append({'t': round((f - start) / fps, 4), 'q': pose, 'hips': [round(v, 5) for v in hips]})
        data = {'name': name, 'loop': LOOPS[name], 'length': round((end - start) / fps, 4), 'keys': keys}
        (out / ('%s.json' % name)).write_text(json.dumps(data, separators=(',', ':')), encoding='utf-8')
        print('ROBLOX_CLIP', name, len(keys), data['length'])


if __name__ == '__main__':
    main(sys.argv)
