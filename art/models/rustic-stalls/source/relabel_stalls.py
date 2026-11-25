"""Card 1cf3e9 (owner 23.11.2026): the hub signs REWARDS, UPGRADES and CLASSES in the game's font, Fredoka One.

Reads the owner's edited stalls (export/RusticStalls_Updated.glb) and changes nothing of them but the letters of the
three shop signs: the old letters (the cream faces in front of the sign plank) go, Fredoka One letters of the same
cream, as deep and in the box the old build gave them (build_stalls.label: 5.63 x 0.82 studs) take their place, centred
where the old ones stood. Each stall is then turned by its yaw on the lobby (LAYOUT of build_stalls.py), as the meshes
in the game are (their InitialSize is these bounding boxes to 0.0001), and written as export/roblox/<Name>.fbx for
the studio's FBX import, with a check of each: the rest of the stall keeps its faces and normals and the box is the
old box. Close-ups of each sign before and after go to review/<Name>-sign-before.jpg and -after.png.

  blender -b --python relabel_stalls.py -- <FredokaOne-Regular.ttf> [out-dir]

Roblox Studio carries the font: content/fonts/FredokaOne-Regular.ttf of its version folder.
"""
from collections import Counter
from math import radians
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
SOURCE = ASSET / 'export' / 'RusticStalls_Updated.glb'
REVIEW = ASSET / 'review'
STUD = 0.28
YAW = {'Rewards': 24.0, 'Upgrades': 16.0, 'Classes': -24.0}
BOX = (5.63 * STUD, 0.82 * STUD)  # build_stalls.label: the letters' widest and tallest
SIGN = (0.83, 1.70, 2.05)  # the letters' region on the stall (metres): |x| below, z between; the sign's bolts stand at |x| 0.82..0.88
PLANK_FRONT = -2.54 * STUD  # build_stalls.stall_frame: the sign plank's front face; the letters stand just in front of it


def args():
    rest = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not rest:
        raise SystemExit('usage: blender -b --python relabel_stalls.py -- <FredokaOne-Regular.ttf> [out-dir]')
    font = Path(rest[0])
    out = Path(rest[1]) if len(rest) > 1 else ASSET / 'export' / 'roblox'
    return font, out


def face_uv(face, uv):
    return tuple(round(c, 5) for c in face.loops[0][uv].uv)


def old_letters(bm, uv):
    """The letters: the faces in front of the sign plank, in the letters' region, of the swatch most of them have (the cream)."""
    ahead = [f for f in bm.faces if all(abs(v.co.x) < SIGN[0] and SIGN[1] < v.co.z < SIGN[2]
                                        and PLANK_FRONT - .03 < v.co.y < PLANK_FRONT for v in f.verts)]
    swatch = Counter(face_uv(f, uv) for f in ahead).most_common(1)[0][0]
    letters = [f for f in ahead if face_uv(f, uv) == swatch]
    return letters, swatch


def text_mesh(word, font):
    curve = bpy.data.curves.new(word, 'FONT')
    curve.body = word
    curve.font = font
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.resolution_u = 2
    curve.extrude = 0.027
    curve.size = 1
    obj = bpy.data.objects.new(word, curve)
    bpy.context.scene.collection.objects.link(obj)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    data = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.curves.remove(curve)
    return data


def corner_normals(me, faces):
    normals = me.corner_normals
    return [tuple(round(c, 4) for c in normals[i].vector) for f in faces for i in me.polygons[f].loop_indices]


def relabel(obj, font):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    uv = bm.loops.layers.uv.active
    letters, swatch = old_letters(bm, uv)
    pts = [v.co.copy() for f in letters for v in f.verts]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = Vector((0, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2))  # the sign is symmetric about x = 0
    old = set(letters)
    kept = [f.index for f in bm.faces if f not in old]
    print(f'{obj.name}: {len(letters)} old letter faces, swatch {swatch}, box x {lo.x:.4f}..{hi.x:.4f} '
          f'y {lo.y:.4f}..{hi.y:.4f} z {lo.z:.4f}..{hi.z:.4f}')
    before = corner_normals(me, kept)
    loose = {v for f in letters for v in f.verts}
    bmesh.ops.delete(bm, geom=letters, context='FACES_ONLY')
    bmesh.ops.delete(bm, geom=[v for v in loose if v.is_valid and not v.link_faces], context='VERTS')
    bm.to_mesh(me)
    bm.free()

    # The new letters: Fredoka One, in the old build's box, centred where the old letters stood, as deep as they were.
    data = text_mesh(obj.name.upper(), font)
    tb = bmesh.new()
    tb.from_mesh(data)
    bmesh.ops.remove_doubles(tb, verts=list(tb.verts), dist=0.000005)
    bmesh.ops.triangulate(tb, faces=list(tb.faces))
    tuv = tb.loops.layers.uv.verify()
    for f in tb.faces:
        f.smooth = False
        for loop in f.loops:
            loop[tuv].uv = swatch
    tb.to_mesh(data)
    tb.free()
    xs = [v.co.x for v in data.vertices]
    ys = [v.co.y for v in data.vertices]
    zs = [v.co.z for v in data.vertices]
    width, height, depth = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    scale = min(BOX[0] / width, BOX[1] / height)
    mid = Vector(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, (max(zs) + min(zs)) / 2))
    deep = (hi.y - lo.y) / depth
    for v in data.vertices:
        x, y, z = v.co - mid
        # Text lies in its XY plane facing +Z; on the sign it faces -Y (the stall's front), upright along Z.
        v.co = Vector((centre.x + x * scale, centre.y - z * deep, centre.z + y * scale))
    data.uv_layers.active.name = me.uv_layers.active.name
    data.materials.append(me.materials[0])
    added = bpy.data.objects.new(obj.name + '_Letters', data)
    bpy.context.scene.collection.objects.link(added)
    new_faces = len(data.polygons)
    bpy.ops.object.select_all(action='DESELECT')
    added.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    assert len(obj.data.polygons) == len(kept) + new_faces, 'the join lost or added faces'
    after = corner_normals(obj.data, range(len(kept)))
    assert after == before, f'{obj.name}: the normals of the rest of the stall changed'
    print(f'{obj.name}: {new_faces} new letter faces, scale {scale:.4f}, '
          f'letters {width * scale:.4f} x {height * scale:.4f} m')


def box(points):
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi


def export(obj, out):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    out.mkdir(parents=True, exist_ok=True)
    # As export_well.py of this game; no texture goes with it: the MeshPart keeps the stalls' palette texture.
    bpy.ops.export_scene.fbx(filepath=str(out / f'{obj.name}.fbx'), use_selection=True, object_types={'MESH'},
                             axis_forward='-Z', axis_up='Y', global_scale=1.0, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_UNITS', use_mesh_modifiers=False, use_triangles=True,
                             mesh_smooth_type='FACE', add_leaf_bones=False, bake_anim=False, path_mode='STRIP')


def preview(obj, path):
    """A close-up of the sign from the front (the stall's -Y side), as the palette texture colours it."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'TEXTURE'
    scene.render.resolution_x, scene.render.resolution_y = 1200, 420
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = 88
    if scene.world is None:
        scene.world = bpy.data.worlds.new('World')
    cam = bpy.data.objects.get('SignCamera')
    if cam is None:
        cam = bpy.data.objects.new('SignCamera', bpy.data.cameras.new('SignCamera'))
        scene.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 2.1
    cam.location = (0, -3, 1.87)
    cam.rotation_euler = (radians(90), 0, 0)
    scene.camera = cam
    for other in scene.objects:
        if other.type == 'MESH':
            other.hide_render = other is not obj
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    font_file, out = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE))
    font = bpy.data.fonts.load(str(font_file))
    for name, yaw in YAW.items():
        obj = bpy.data.objects[name]
        # The GLB places the stalls as on the lobby; the game's mesh is the stall's own mesh, so it stands at the origin.
        obj.parent = None
        obj.matrix_world = Matrix.Identity(4)
        before = box([v.co for v in obj.data.vertices])
        preview(obj, REVIEW / f'{name}-sign-before.jpg')
        relabel(obj, font)
        preview(obj, REVIEW / f'{name}-sign-after.jpg')
        after = box([v.co for v in obj.data.vertices])
        assert all(abs(a - b) < 1e-4 for a, b in zip([*before[0], *before[1]], [*after[0], *after[1]])), \
            f'{name}: the new letters changed the bounding box {before} -> {after}'
        turn = Matrix.Rotation(radians(yaw), 4, 'Z')
        obj.data.transform(turn)
        lo, hi = box([v.co for v in obj.data.vertices])
        size = hi - lo
        print(f'{name}: turned {yaw}, box {size.x:.4f} x {size.z:.4f} x {size.y:.4f} (Roblox X x Y x Z)')
        export(obj, out)


if __name__ == '__main__':
    main()
