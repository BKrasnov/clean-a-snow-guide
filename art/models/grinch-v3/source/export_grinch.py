"""Grinch v3 (card e49171): FBX files for Roblox Studio's Import 3D and the Animation Editor.

    blender -b <abs Grinch_master.blend> --python export_grinch.py -- --out <abs export folder>

Writes into --out:
- Grinch.fbx: the mesh Grinch_Body on Grinch_Rig in its T-pose, no animation, the palette texture embedded
  (Import 3D makes a skinned MeshPart with its bones and a SurfaceAppearance from it);
- Grinch_<Clip>.fbx for Idle, Walk, Attack, Hit, Stunned: the rig and the mesh with that one action only
  (the Animation Editor's "Import from FBX" takes one clip per file).
Units: metres with the FBX unit scale, so Import 3D reads 1 m and turns it into studs itself; -Z forward, Y up.
The master is not saved.
"""
import argparse
import sys
from pathlib import Path

import bpy

RIG, BODY = 'Grinch_Rig', 'Grinch_Body'
CLIPS = ('Idle', 'Walk', 'Attack', 'Hit', 'Stunned')


def export(path, animation):
    for ob in bpy.context.view_layer.objects:
        ob.select_set(False)
    rig, body = bpy.data.objects[RIG], bpy.data.objects[BODY]
    rig.select_set(True)
    body.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, object_types={'MESH', 'ARMATURE'},
        axis_forward='-Z', axis_up='Y', global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
        use_mesh_modifiers=False, use_triangles=True, mesh_smooth_type='FACE', add_leaf_bones=False,
        use_armature_deform_only=True, bake_anim=animation, bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True, bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0, path_mode='STRIP' if animation else 'COPY', embed_textures=not animation)


def main(argv):
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    out = Path(parser.parse_args(argv).out)
    out.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.fps = 30
    rig = bpy.data.objects[RIG]
    rig.animation_data_create()
    rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.matrix_basis.identity()
    export(out / 'Grinch.fbx', animation=False)
    print('GRINCH_EXPORT', out / 'Grinch.fbx')
    for name in CLIPS:
        action = bpy.data.actions[name]
        rig.animation_data.action = action
        if action.slots:
            rig.animation_data.action_slot = action.slots[0]
        start, end = (int(v) for v in action.frame_range)
        scene.frame_start, scene.frame_end = start, end
        path = out / ('Grinch_%s.fbx' % name)
        export(path, animation=True)
        print('GRINCH_EXPORT', path, start, end)


if __name__ == '__main__':
    main(sys.argv)
