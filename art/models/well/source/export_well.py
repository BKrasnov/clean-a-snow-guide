"""Well (card 55be02): Well.fbx for Roblox Studio's Import 3D — the mesh Well_Body with its palette texture embedded,
a static prop.

    blender -b <abs Well_master.blend> --python export_well.py -- --out <abs export folder>

Metres with the FBX unit scale (Import 3D, Scale Unit: Meter), -Z forward, Y up. The master is not saved.
"""
import argparse
import sys
from pathlib import Path

import bpy


def main(argv):
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    out = Path(parser.parse_args(argv).out)
    out.mkdir(parents=True, exist_ok=True)
    for ob in bpy.context.view_layer.objects:
        ob.select_set(ob.name == 'Well_Body')
    path = out / 'Well.fbx'
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, object_types={'MESH'}, axis_forward='-Z', axis_up='Y',
        global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', use_mesh_modifiers=True,
        use_triangles=True, mesh_smooth_type='FACE', bake_anim=False, path_mode='COPY', embed_textures=True)
    print('WELL_EXPORT', path)


if __name__ == '__main__':
    main(sys.argv)
