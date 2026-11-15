"""Grinch, version 3 (card e49171): the rig check within the Grinch's joint limits; the model file is never saved.

    blender -b <abs Grinch_master.blend> --python rig_limits_check.py -- --out <abs folder> [--size 320]

Runs the studio anim_check.py with the range-of-motion clip cut to rig_grinch.LIMIT_MOVES (the moves that go past
rig_grinch.JOINT_LIMITS; the others as in rom_clip.MOVES) and the motion profile source/motion-profile.json, so the
folder has the same anim-report.json, rom sheets and heat map as the full studio check. Then adds edges.json: for
every extreme of that clip the ten most strained edges (stretch and squeeze) with their rest length and the part of
the mesh they lie on, and the collapsed triangles by part; and game-poses.png: the poses the fight needs, within the
limits, close up (POSES; Workbench, the palette texture).
"""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True   # no __pycache__ next to the master
sys.path.insert(0, str(HERE))
import rig_grinch  # noqa: E402  (puts the studio scripts on the path)
import anim_check  # noqa: E402
import rom_clip  # noqa: E402


def part_names(ob):
    """The part of every vertex, as rig_grinch.classify names it (kind and side)."""
    names = np.empty(len(ob.data.vertices), dtype=object)
    for (kind, side), plist in rig_grinch.classify(ob.data).items():
        for p in plist:
            names[p.idx] = (side + ' ' + kind).strip()
    return names


def edge_report(rig, ob, folder):
    meshes = [ob]
    names = part_names(ob)
    rig.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    rest = anim_check.mesh_points(meshes)
    rig.data.pose_position = 'POSE'
    edges, tris = anim_check.topology(meshes)
    strain = anim_check.Strain(rest, edges, tris)
    length = np.linalg.norm(rest[edges[:, 0]] - rest[edges[:, 1]], axis=1)
    kept = np.nonzero(strain.keep)[0]
    _, segments = rom_clip.make_rom_action(rig)
    poses = []
    for seg in segments:
        for key in ('min', 'max'):
            bpy.context.scene.frame_set(seg[key])
            pts = anim_check.mesh_points(meshes)
            ratio = np.linalg.norm(pts[edges[kept, 0]] - pts[edges[kept, 1]], axis=1) / strain.length
            area = anim_check._areas(pts, tris) / np.maximum(strain.area, 1e-12)
            collapsed = {}
            for t in np.nonzero(area < 0.2)[0]:
                part = names[tris[t, 0]]
                collapsed[part] = collapsed.get(part, 0) + 1

            def row(i):
                e = kept[i]
                return {'ratio': round(float(ratio[i]), 3), 'rest_m': round(float(length[e]), 4),
                        'part': names[edges[e, 0]], 'at': [round(float(c), 3) for c in rest[edges[e, 0]]]}
            order = np.argsort(ratio)
            poses.append({'label': '%s %s' % (seg['label'], key), 'frame': seg[key],
                          'stretched': [row(i) for i in order[::-1][:10]],
                          'squeezed': [row(i) for i in order[:10]], 'collapsed': collapsed})
    (folder / 'edges.json').write_text(json.dumps({'poses': poses}, indent=2, ensure_ascii=False), encoding='utf-8')


# Poses of the fight (card 9c7419), within the limits: name, turns (bone, axis, degrees; the right side mirrors as in
# rom_clip) or 'squat', the camera target, the direction to the camera and the orthographic size, metres.
POSES = [
    ('руки вверх 50', [('LeftArm', 'Y', -50)], (0, 0, 2.1), (0, -1, 0), 3.2),
    ('руки вниз 45', [('LeftArm', 'Y', 45)], (0, 0, 1.5), (0, -1, 0), 3.2),
    ('удар вперёд', [('LeftArm', 'Z', -90), ('LeftForeArm', 'Z', -30)], (0, -0.4, 1.7), (1, -0.3, 0.3), 2.4),
    ('локоть 145, правая рука, 3/4', [('LeftForeArm', 'Z', -145)], (-0.6, -0.25, 1.79), (-0.8, -1, -0.5), 1.4),
    ('колено 140 сбоку', [('LeftLeg', 'X', 140)], (0.18, 0.25, 0.85), (1, 0, 0.05), 2.0),
    ('присед', 'squat', (0, 0, 1.4), (1, -0.4, 0.1), 3.4),
    ('сидит: бёдра 90, колени 90', [('LeftUpLeg', 'X', -90), ('LeftLeg', 'X', 90)], (0, -0.4, 1.6), (1, -0.3, 0.1), 3.6),
    ('корпус вперёд 30', [('Spine', 'X', 10), ('Spine1', 'X', 10), ('Spine2', 'X', 10)], (0, -0.3, 1.55), (1, 0, 0), 3.4),
    ('корпус вбок 25', [('Spine', 'Y', 8.3), ('Spine1', 'Y', 8.3), ('Spine2', 'Y', 8.3)], (0, 0, 1.7), (0, -1, 0), 2.6),
]
AXES = {'X': Vector((1, 0, 0)), 'Y': Vector((0, 1, 0)), 'Z': Vector((0, 0, 1))}


def pose_sheet(rig, folder, size=512):
    """Renders POSES close up and puts them on one sheet, three in a row."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light, shading.color_type, shading.show_object_outline = 'STUDIO', 'TEXTURE', True
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    data = bpy.data.cameras.new('PoseCam')
    data.type = 'ORTHO'
    cam = bpy.data.objects.new('PoseCam', data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    rig.hide_render = True
    rig.animation_data.action = None
    bones = rig.data.bones
    tiles = []
    for i, (name, turns, target, direction, ortho) in enumerate(POSES):
        for pb in rig.pose.bones:
            pb.rotation_quaternion, pb.location = Quaternion(), (0, 0, 0)
        if turns == 'squat':
            rotations, offset = rom_clip.squat(rig)
            for bone, q in rotations.items():
                rig.pose.bones[bone].rotation_quaternion = q
            rig.pose.bones[rom_clip.PREFIX + 'Hips'].location = offset
        else:
            for bone, axis, degrees in turns:
                for b, ax in ((bone, AXES[axis]), rom_clip.mirror(bone, AXES[axis]) or (None, None)):
                    if b and rom_clip.PREFIX + b in bones:
                        rig.pose.bones[rom_clip.PREFIX + b].rotation_quaternion = rom_clip.local_rotation(
                            bones[rom_clip.PREFIX + b], ax, degrees)
        bpy.context.view_layer.update()
        d = Vector(direction).normalized()
        cam.location = Vector(target) + d * 6
        cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        data.ortho_scale = ortho
        tile = folder / ('pose-%02d.png' % i)
        scene.render.filepath = str(tile)
        bpy.ops.render.render(write_still=True)
        tiles.append(tile)
    images = []
    for tile in tiles:
        im = bpy.data.images.load(str(tile))
        images.append(np.array(im.pixels[:]).reshape(size, size, 4))
        bpy.data.images.remove(im)
        tile.unlink()
    while len(images) % 3:
        images.append(np.zeros((size, size, 4)))
    rows = [np.concatenate(images[r:r + 3], 1) for r in range(0, len(images), 3)][::-1]
    grid = np.concatenate(rows, 0)
    sheet = bpy.data.images.new('GamePoses', grid.shape[1], grid.shape[0])
    sheet.pixels.foreach_set(grid.ravel().astype(np.float32))
    sheet.filepath_raw = str(folder / 'game-poses.png')
    sheet.file_format = 'PNG'
    sheet.save()
    return [p[0] for p in POSES]


def main(argv):
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--size', default='320')
    a = ap.parse_args(argv)
    rom_clip.MOVES[:] = rig_grinch.limited_moves(rom_clip.MOVES)
    profile = HERE / 'motion-profile.json'
    anim_check.main(['--', '--out', a.out, '--rig', rig_grinch.RIG, '--mesh', rig_grinch.BODY, '--size', a.size,
                     '--profile', str(profile)])
    edge_report(bpy.data.objects[rig_grinch.RIG], bpy.data.objects[rig_grinch.BODY], Path(a.out))
    names = pose_sheet(bpy.data.objects[rig_grinch.RIG], Path(a.out))
    print('GRINCH_POSES %s (game-poses.png, left to right, top to bottom)' % names)
    print('GRINCH_LIMITS moves=%s' % {k: v for k, v in rig_grinch.LIMIT_MOVES.items()})


if __name__ == '__main__':
    main(sys.argv)
