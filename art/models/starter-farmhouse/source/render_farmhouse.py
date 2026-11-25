"""Render the saved master from outside, in cutaway, and at player height."""

import argparse
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
from build_farmhouse import FLOOR, LANTERN_ROWS, MODEL, STUD, Mesh, collection


def camera(scene, group, position, target, ortho=None, lens=26):
    data = bpy.data.cameras.new("ReviewCamera")
    camera_object = bpy.data.objects.new("ReviewCamera", data)
    group.objects.link(camera_object)
    camera_object.location = position
    camera_object.rotation_euler = (Vector(target) - camera_object.location).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        data.type = "ORTHO"
        data.ortho_scale = ortho
    data.lens = lens
    data.clip_start = 0.05
    data.clip_end = 100
    scene.camera = camera_object


def light(group, name, position, target, energy, size, color, kind="AREA"):
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    data.color = color
    if kind == "AREA":
        data.shape = "DISK"
        data.size = size
    else:
        data.shadow_soft_size = size
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def render(scene, out, name, size):
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(out / (name + ".png"))
    bpy.ops.render.render(write_still=True)


def clip_wall(name, height, slope=0):
    obj = bpy.data.objects[name]
    edit = bmesh.new()
    edit.from_mesh(obj.data)
    sliced = bmesh.ops.bisect_plane(
        edit, geom=[*edit.verts, *edit.edges, *edit.faces], dist=0.00001,
        plane_co=(0, 0, height), plane_no=(0, -slope, 1), clear_outer=True,
    )
    cut_edges = [edge for edge in sliced["geom_cut"] if isinstance(edge, bmesh.types.BMEdge) and edge.is_boundary]
    if cut_edges:
        faces = bmesh.ops.holes_fill(edit, edges=cut_edges, sides=0)["faces"]
        uvs = edit.loops.layers.uv.active
        for face in faces:
            for loop in face.loops:
                loop[uvs].uv = (0.625, 0.125)
    bmesh.ops.recalc_face_normals(edit, faces=list(edit.faces))
    edit.to_mesh(obj.data)
    edit.free()


def avatar(group):
    material = bpy.data.materials["M_" + MODEL + "_Palette"]
    surf = material, {"body": (0.875, 0.375), "head": (0.625, 0.125)}
    dummy = Mesh("Scale reference 5 studs", group, surf)
    x, y, base = -1.37, 0.15, FLOOR
    for offset in (-0.14, 0.14):
        dummy.box((x + offset, y, base + STUD), (0.25, 0.29, 2 * STUD), "body")
    dummy.box((x, y, base + 3 * STUD), (0.55, 0.30, 2 * STUD), "body")
    dummy.box((x, y, base + 4.5 * STUD), (0.315, 0.29, STUD), "head")
    for offset in (-0.38, 0.38):
        dummy.box((x + offset, y, base + 2.95 * STUD), (0.18, 0.25, 1.88 * STUD), "body")
    return dummy.object()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    group = collection("Temporary render setup", scene.collection)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.24
    scene.world = bpy.data.worlds.new("Review World")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs[0].default_value = (0.42, 0.51, 0.66, 1)
    scene.world.node_tree.nodes.get("Background").inputs[1].default_value = 0.70
    light(group, "Key", (-6, -9, 14), (0, -1, 2), 3800, 12, (1.0, 0.92, 0.82))
    light(group, "Cool fill", (9, -3, 10), (0, 0, 1), 1850, 11, (0.77, 0.88, 1.0))
    light(group, "Roof fill", (-4, 6, 10), (0, 0, 2), 2700, 9, (0.81, 0.90, 1.0))
    hall = light(group, "Hall bounce", (0, -0.9, 3.0), (0, 2.2, 0.5), 285, 4.0, (1, 0.84, 0.65))
    lamps = [light(group, name + " light", (s * 3.75, y, 2.84), (0, 0, 0),
                   26, 0.30, (1.0, 0.60, 0.27), kind="POINT") for s, name, y in LANTERN_ROWS]

    camera(scene, group, (11, -17, 9.1), (0, -0.48, 3.65), ortho=15.5)
    render(scene, out, "exterior", (1450, 1040))

    dummy = avatar(group)
    camera(scene, group, (0.03, -5.18, 2.25), (0, 2.72, 1.85), lens=20)
    render(scene, out, "player-scale", (1250, 780))
    dummy.hide_render = True

    bpy.data.collections["Main roof and gables"].hide_render = True
    bpy.data.objects["PorchCanopy"].hide_render = True
    for name in ("FrontWall", "LeftDoor", "RightDoor", "Porch"):
        clip_wall(name, 1.15)
    clip_wall("CornerBoards", 2.50, 0.32)
    for name in ("LeftWall", "RightWall"):
        clip_wall(name, 2.86, 0.19)
    clip_wall("RearWall", 3.79)
    hall.hide_render = True
    for lamp in lamps:
        lamp.data.energy = 12
    camera(scene, group, (-2.8, -15.8, 13.6), (0, -0.95, 1.50), lens=40)
    render(scene, out, "interior-cutaway", (1420, 1120))


if __name__ == "__main__":
    main()
