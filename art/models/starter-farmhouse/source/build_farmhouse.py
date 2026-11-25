"""Build the selected farmhouse as an editable, metric Blender scene."""

import argparse
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector


MODEL = "StarterFarmhouse"
STUD = 0.28
HALF_W = 16 * STUD
HALF_D = 15 * STUD
FLOOR = 0.42
EAVE = 3.86
WALL = 0.24
ENTRY = 4.48
ENTRY_TOP = 3.43
PORCH_FRONT = -5.98
PORCH_REAR = -4.15
PORCH_EDGE_Z = 3.31
PORCH_WALL_Z = 3.72
PORCH_THICKNESS = 0.21
POST_X = 2.50
POST_WIDTH = 0.37
AVATAR_HEIGHT = 6.5 * STUD
LANTERN_ROWS = [(-1, "LeftLantern", 3.13), (1, "RightLantern", 3.13)]
ROOF = [(-4.94, 3.76), (-3.03, 6.12), (0, 6.92), (3.03, 6.12), (4.94, 3.76)]
ROOF_DEPTHS = [4.68, 4.49, 4.44, 4.49, 4.68]
COLORS = {
    "red": "#D6392B",
    "blue": "#80A0E6",
    "trim": "#FFFDF5",
    "glass": "#A8DEE7",
    "wood": "#CD925C",
    "dark": "#80401B",
    "earth": "#966240",
    "metal": "#A0B0C4",
    "lamp": "#FAD66E",
    "snow": "#F3F6F5",
    "snow_shade": "#CDCDED",
}


def palette():
    size, tile = 64, 16
    colors = list(COLORS.values())
    pixels = []
    for y in range(size):
        for x in range(size):
            index = min(y // tile * 4 + x // tile, len(colors) - 1)
            color = colors[index]
            pixels.extend([int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)] + [1.0])
    image = bpy.data.images.new(MODEL + "_Palette", size, size, alpha=False)
    image.pixels.foreach_set(pixels)
    image.pack()
    material = bpy.data.materials.new("M_" + MODEL + "_Palette")
    material.use_nodes = True
    graph = material.node_tree
    shader = graph.nodes.get("Principled BSDF")
    shader.inputs["Roughness"].default_value = 0.84
    shader.inputs["Specular IOR Level"].default_value = 0.24
    texture = graph.nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.interpolation = "Closest"
    graph.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
    uv = {name: ((i % 4 + 0.5) / 4, (i // 4 + 0.5) / 4) for i, name in enumerate(COLORS)}
    return material, uv


def collection(name, parent):
    result = bpy.data.collections.new(name)
    parent.children.link(result)
    return result


class Mesh:
    def __init__(self, name, group, surface):
        self.name = name
        self.group = group
        self.material, self.swatches = surface
        self.vertices = []
        self.faces = []
        self.colors = []

    def add(self, vertices, faces, color):
        offset = len(self.vertices)
        self.vertices.extend(vertices)
        for face in faces:
            self.faces.append(tuple(offset + index for index in face))
            self.colors.append(color)

    def box(self, center, size, color):
        cx, cy, cz = center
        hx, hy, hz = (value / 2 for value in size)
        self.add(
            [(cx + x, cy + y, cz + z) for z in (-hz, hz)
             for x, y in [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]],
            [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
            color,
        )

    def plane_box(self, span, level, normal, axis, color):
        u, z = ((a + b) / 2 for a, b in (span, level))
        n = (normal[0] + normal[1]) / 2
        width, height, depth = (b - a for a, b in (span, level, normal))
        if axis == "Y":
            self.box((u, n, z), (width, depth, height), color)
        else:
            self.box((n, u, z), (depth, width, height), color)

    def prism(self, profile, lower, upper, axis, color):
        """Extrude a polygon along the given axis."""
        count = len(profile)
        if axis == "Y":
            vertices = [(u, depth, z) for depth in (lower, upper) for u, z in profile]
        elif axis == "X":
            vertices = [(depth, u, z) for depth in (lower, upper) for u, z in profile]
        else:
            vertices = [(u, v, depth) for depth in (lower, upper) for u, v in profile]
        sides = [(i, (i + 1) % count, (i + 1) % count + count, i + count) for i in range(count)]
        caps = [tuple(range(count - 1, -1, -1)), tuple(range(count, count * 2))]
        self.add(vertices, caps + sides, color)

    def panel(self, columns, rows, holes, normal, axis, color, top_height=None):
        """One closed extrusion with rectangular openings and optional pitched top."""
        vertices, indices, faces, perimeter = [], {}, [], {}

        def corner(u, z, side):
            n = normal[side]
            height = top_height(u, n) if top_height and z == rows[-1] else z
            co = (u, n, height) if axis == "Y" else (n, u, height)
            if co not in indices:
                indices[co] = len(vertices)
                vertices.append(co)
            return indices[co]

        for a, b in zip(columns, columns[1:]):
            for low, high in zip(rows, rows[1:]):
                u, z = (a + b) / 2, (low + high) / 2
                if any(l < u < r and bottom < z < top for l, r, bottom, top in holes):
                    continue
                quad = [(a, low), (b, low), (b, high), (a, high)]
                for side in (0, 1):
                    faces.append(tuple(corner(*point, side) for point in quad))
                for p, q in zip(quad, quad[1:] + quad[:1]):
                    if (q, p) in perimeter:
                        del perimeter[q, p]
                    else:
                        perimeter[p, q] = True
        for p, q in perimeter:
            faces.append((corner(*p, 0), corner(*q, 0), corner(*q, 1), corner(*p, 1)))
        self.add(vertices, faces, color)

    def beam(self, a, b, width, depth, color):
        start, end = Vector(a), Vector(b)
        axis = (end - start).normalized()
        reference = Vector((0, 1, 0)) if abs(axis.y) < 0.96 else Vector((1, 0, 0))
        cross = axis.cross(reference).normalized() * width / 2
        normal = axis.cross(cross).normalized() * depth / 2
        vertices = [tuple(p + sx * cross + sy * normal)
                    for p in (start, end) for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
        self.add(vertices, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                            (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], color)

    def lathe(self, x, y, profile, segments, color, phase=0):
        vertices = [(x + radius * math.cos(2 * math.pi * i / segments + phase),
                     y + radius * math.sin(2 * math.pi * i / segments + phase), z)
                    for radius, z in profile for i in range(segments)]
        sides = [(j * segments + i, j * segments + (i + 1) % segments,
                  (j + 1) * segments + (i + 1) % segments, (j + 1) * segments + i)
                 for j in range(len(profile) - 1) for i in range(segments)]
        last = (len(profile) - 1) * segments
        caps = [(0, i + 1, i) for i in range(1, segments - 1)]
        caps.extend((last, last + i, last + i + 1) for i in range(1, segments - 1))
        self.add(vertices, sides + caps, color)

    def object(self):
        mesh = bpy.data.meshes.new(self.name)
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.materials.append(self.material)
        layer = mesh.uv_layers.new(name="Palette")
        for poly, color in zip(mesh.polygons, self.colors, strict=True):
            for i in poly.loop_indices:
                layer.data[i].uv = self.swatches[color]
        edit = bmesh.new()
        edit.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(edit, faces=list(edit.faces))
        bmesh.ops.triangulate(edit, faces=[face for face in edit.faces if len(face.verts) > 4])
        edit.to_mesh(mesh)
        edit.free()

        obj = bpy.data.objects.new(self.name, mesh)
        self.group.objects.link(obj)
        return obj


def wall_with_windows(mesh, half, normal, axis, windows, z0, z1):
    holes = [(u - w / 2, u + w / 2, z0, z1) for u, w in windows]
    columns = sorted({-half, half, *(x for l, r, _, _ in holes for x in (l, r))})
    pitch = (lambda u, n: roof_height(abs(n)) - 0.16) if axis == "X" else None
    mesh.panel(columns, [0.10 if axis == "X" else 0.115, z0, z1, EAVE],
               holes, normal, axis, "red", pitch)


def window(mesh, center, width, bottom, top, wall_center, axis, panes):
    lo, hi = center - width / 2, center + width / 2
    frame = 0.145
    frame_depth = (wall_center - 0.16, wall_center + 0.16)
    mesh.plane_box((lo + 0.045, hi - 0.045), (bottom + 0.045, top - 0.045),
                   (wall_center - 0.035, wall_center + 0.035), axis, "glass")
    cols = [lo + frame]
    for i in range(1, panes[0]):
        u = lo + width * i / panes[0]
        cols.extend((u - 0.052, u + 0.052))
    cols.append(hi - frame)
    rows = [bottom + frame]
    if panes[1] == 2:
        mid = (bottom + top) / 2
        rows.extend((mid - 0.055, mid + 0.055))
    rows.append(top - frame)
    holes = [(l, r, b, t) for l, r in zip(cols[::2], cols[1::2]) for b, t in zip(rows[::2], rows[1::2])]
    mesh.panel([lo - 0.02, *cols, hi + 0.02], [bottom - 0.048, *rows, top + 0.045],
               holes, frame_depth, axis, "trim")
    sill = frame_depth[0] - 0.06, frame_depth[1] + 0.06
    mesh.plane_box((lo - 0.11, hi + 0.11), (bottom - 0.145, bottom - 0.035), sill, axis, "trim")


def roof_height(x):
    for (left, a), (right, b) in zip(ROOF, ROOF[1:]):
        if left <= x <= right:
            return a + (b - a) * (x - left) / (right - left)
    raise ValueError(x)


def rake_trim(mesh, side):
    """Continuous gable fascia offset down from the roof, with mitred bends."""
    path = [Vector(point) for point in ROOF]
    directions = [(b - a).normalized() for a, b in zip(path, path[1:])]
    normals = [Vector((d.y, -d.x)) for d in directions]
    directions_down = [normals[0]]
    for a, b in zip(normals, normals[1:]):
        bisector = (a + b).normalized()
        directions_down.append(bisector / bisector.dot(a))
    directions_down.append(normals[-1])
    vertices = []
    for point, down, depth in zip(path, directions_down, ROOF_DEPTHS, strict=True):
        top = point + 0.10 * down
        bottom = point + 0.34 * down
        for xz, y in [(top, depth - 0.055), (top, depth + 0.025),
                      (bottom, depth + 0.025), (bottom, depth - 0.055)]:
            vertices.append((xz.x, y * side, xz.y))
    faces = [(0, 3, 2, 1), tuple(range(len(vertices) - 4, len(vertices)))]
    for i in range(len(path) - 1):
        step = i * 4
        for j in range(4):
            a, b = step + j, step + (j + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    mesh.add(vertices, faces, "trim")


def snow_cap(mesh, center, half_x, half_y, surface_height, max_thickness):
    """A sealed low-poly cap with shallow irregular ridges and a tapered lip."""
    across = [-1.0, -0.83, -0.52, 0.0, 0.52, 0.83, 1.0]
    along = [-1.0, -0.89, -0.67, -0.40, -0.16, 0.12, 0.37, 0.68, 0.88, 1.0]
    points = []
    for top in (False, True):
        for v in along:
            for u in across:
                edge_shift = 0.983 + 0.012 * math.sin(4.2 * v + 0.6) + 0.005 * math.cos(7.8 * v)
                x = center[0] + half_x * u * edge_shift
                y = center[1] + half_y * v + 0.019 * math.sin(5.0 * u + 0.4) * v
                thickness = max_thickness * (1 - 0.86 * abs(u) ** 3) * (1 - 0.47 * abs(v) ** 8)
                thickness *= 1 + 0.10 * math.sin(5.4 * v + 3.1 * u + 0.4)
                z = surface_height(x, y) + (thickness if top else -0.018)
                points.append((x, y, z))
    width, length = len(across), len(along)
    offset = width * length
    bottom, top = [], []
    for j in range(length - 1):
        for i in range(width - 1):
            a = j * width + i
            row = [a, a + 1, a + width + 1, a + width]
            for tri in [row[:3], [row[0], row[2], row[3]]]:
                bottom.append(tri)
                top.append([index + offset for index in tri])
    edge = list(range(width))
    edge.extend(j * width + width - 1 for j in range(1, length))
    edge.extend(range(offset - 2, offset - width - 1, -1))
    edge.extend(j * width for j in range(length - 2, 0, -1))
    skirt = [(a, b, b + offset, a + offset) for a, b in zip(edge, edge[1:] + edge[:1])]
    mesh.add(points, bottom + skirt + top, "snow")
    mesh.colors[-len(top) - len(skirt):-len(top)] = ["snow_shade"] * len(skirt)


def build_shell(shell, roof_group, surface, blockout):
    floor = Mesh("Floor", shell, surface)
    floor.box((0, -0.085, 0.205), (2 * HALF_W - 0.18, 2 * HALF_D - 0.11, 0.375), "wood")
    plank_count = 25 if not blockout else 1
    # The first board starts at the back edge of the landing, with one plank seam.
    start, end = -4.181, HALF_D - 0.08
    stride = (end - start) / plank_count
    for i in range(plank_count):
        floor.box((0, start + stride * (i + 0.5), FLOOR - 0.016),
                  (2 * HALF_W - 0.10, stride - 0.004, 0.032), "wood")
    floor.object()

    front = Mesh("FrontWall", shell, surface)
    face = (-HALF_D, -HALF_D + WALL)
    end_half = HALF_W - 0.014
    front.panel([-end_half, -ENTRY / 2, ENTRY / 2, end_half], [0.115, ENTRY_TOP, EAVE],
                [(-ENTRY / 2, ENTRY / 2, 0, ENTRY_TOP)], face, "Y", "red")
    if not blockout:
        for x in (-ENTRY / 2, ENTRY / 2):
            front.box((x, -HALF_D - 0.039, 1.905), (0.17, 0.13, 3.01), "trim")
        front.box((0, -HALF_D - 0.04, ENTRY_TOP + 0.04), (ENTRY + 0.19, 0.16, 0.17), "trim")
    front.object()

    pairs = [(-1.79, 1.68), (1.79, 1.68)]
    for name, axis, depth, half, windows in [
        ("RearWall", "Y", (HALF_D - WALL, HALF_D), end_half, pairs),
        ("RightWall", "X", (HALF_W - WALL, HALF_W), HALF_D - WALL + 0.018, pairs),
        ("LeftWall", "X", (-HALF_W, -HALF_W + WALL), HALF_D - WALL + 0.018, pairs),
    ]:
        wall = Mesh(name, shell, surface)
        wall_with_windows(wall, half, depth, axis, windows, 1.44, 3.00)
        if not blockout:
            for center, width in windows:
                window(wall, center, width, 1.44, 3.00, sum(depth) / 2, axis, (2, 2))
        wall.object()

    front_gable = Mesh("FrontGable", roof_group, surface)
    rear_gable = Mesh("RearGable", roof_group, surface)
    # The long front window is punched through the gable above the porch.
    x0, x1, z0, z1 = -1.50, 1.50, 4.66, 5.65
    gable_half = end_half - 0.014
    base = EAVE - 0.012
    def build_gable(mesh, depths, has_window):
        cols = [-gable_half, -3.03, x0, 0, x1, 3.03, gable_half]
        rows = [base, z0, z1, 7.0] if has_window else [base, 7.0]
        # At the outer eaves there is less wall than the height of the window.
        # Interpolate intermediate rings into the available height in each column.
        holes = [(x0, x1, z0, z1)] if has_window else []
        first = len(mesh.vertices)
        mesh.panel(cols, rows, holes, depths, "Y", "red")
        for i in range(first, len(mesh.vertices)):
            x, y, z = mesh.vertices[i]
            ridge = roof_height(x) - 0.175
            if z == rows[-1]:
                z = ridge
            elif abs(x) > abs(x1):
                z = base + (z - base) * (ridge - base) / (roof_height(x1) - 0.175 - base)
            mesh.vertices[i] = (x, y, z)

    build_gable(front_gable, (face[0] + 0.009, face[1] - 0.009), True)
    if not blockout:
        window(front_gable, 0, x1 - x0, z0, z1, sum(face) / 2, "Y", (3, 1))
    front_gable.object()
    build_gable(rear_gable, (HALF_D - WALL + 0.009, HALF_D - 0.009), False)
    rear_gable.object()

    roof = Mesh("MainRoof", roof_group, surface)
    rings = [(x, y, h) for (x, z), d in zip(ROOF, ROOF_DEPTHS, strict=True)
             for y, h in [(-d, z), (d, z), (d, z - 0.18), (-d, z - 0.18)]]
    faces = [(0, 1, 2, 3), tuple(range(len(rings) - 4, len(rings)))]
    for start in range(0, len(rings) - 4, 4):
        for k in range(4):
            a, b = start + k, start + (k + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    roof.add(rings, faces, "blue")
    if not blockout:
        for s in (-1, 1):
            rake_trim(roof, s)
            roof.box((s * 4.81, 0, 3.54), (0.24, 9.29, 0.24), "trim")
        snow_cap(roof, (0, 0), 1.60, 4.40, lambda x, _y: roof_height(x), 0.15)
    roof.object()

    chimney = Mesh("Chimney", roof_group, surface)
    chimney.box((1.74, 2.23, 6.75), (1.02, 1.05, 1.03), "red")
    if not blockout:
        for z in (6.66, 6.97):
            chimney.box((1.74, 2.23, z), (1.046, 1.076, 0.025), "earth")
        chimney.box((1.74, 2.23, 7.30), (1.19, 1.22, 0.14), "trim")
        snow_cap(chimney, (1.74, 2.23), 0.59, 0.60, lambda _x, _y: 7.37, 0.075)
    chimney.object()

    porch = Mesh("Porch", shell, surface)
    porch.box((0, -4.99, (FLOOR + 0.034) / 2), (5.62, 1.61, FLOOR - 0.034), "wood")
    porch.box((0, -5.99, 0.105), (4.70, 0.49, 0.21), "wood")
    for s in (-1, 1):
        for z, width, height in [(1.93, POST_WIDTH, 2.70), (0.52, 0.48, 0.24), (3.17, 0.47, 0.19)]:
            porch.box((s * POST_X, -5.48, z), (width, width, height), "wood")
    porch.object()
    canopy = Mesh("PorchCanopy", shell, surface)
    canopy.prism([(PORCH_FRONT, PORCH_EDGE_Z), (PORCH_REAR, PORCH_WALL_Z),
                  (PORCH_REAR, PORCH_WALL_Z - PORCH_THICKNESS),
                  (PORCH_FRONT, PORCH_EDGE_Z - PORCH_THICKNESS)],
                 -3.23, 3.23, "X", "blue")
    if not blockout:
        fall = (PORCH_WALL_Z - PORCH_EDGE_Z) / (PORCH_REAR - PORCH_FRONT)
        snow_cap(canopy, (0, -5.02), 3.08, 0.88,
                 lambda _x, y: PORCH_EDGE_Z + (y - PORCH_FRONT) * fall, 0.19)
    canopy.object()

    if blockout:
        return
    trim = Mesh("CornerBoards", shell, surface)
    for x in (-HALF_W + 0.16, HALF_W - 0.16):
        for y in (-HALF_D + 0.12, HALF_D - 0.12):
            trim.box((x, y, 1.94), (0.36, 0.36, 3.88), "trim")
    trim.box((0, HALF_D, 0.13), (2 * HALF_W - 0.09, 0.15, 0.24), "trim")
    for s in (-1, 1):
        trim.box((s * HALF_W, 0, 0.13), (0.15, 2 * HALF_D - 0.36, 0.24), "trim")
        trim.box((s * 3.40, -HALF_D, 0.13), (1.95, 0.13, 0.24), "trim")
    trim.object()

    for s, label in [(-1, "LeftDoor"), (1, "RightDoor")]:
        door = Mesh(label, shell, surface)
        x, y = s * 3.34, -HALF_D - 0.13
        bottom, top, width = 0.51, 3.34, 1.91
        door.box((x, y, (bottom + top) / 2), (width - 0.038, 0.15, top - bottom - 0.038), "red")
        l, r = x - width / 2, x + width / 2
        door.panel([l, l + 0.132, r - 0.132, r], [bottom, bottom + 0.14, top - 0.14, top],
                   [(l + 0.132, r - 0.132, bottom + 0.14, top - 0.14)],
                   (y - 0.128, y - 0.028), "Y", "trim")
        door.beam((x - width / 2 + 0.15, y - 0.087, bottom + 0.14),
                  (x + width / 2 - 0.15, y - 0.087, top - 0.14), 0.135, 0.095, "trim")
        door.beam((x + width / 2 - 0.15, y - 0.099, bottom + 0.14),
                  (x - width / 2 + 0.15, y - 0.099, top - 0.14), 0.135, 0.095, "trim")
        door.object()


def table(mesh, x, y, width, depth, height, slab, leg, top="wood"):
    mesh.box((x, y, FLOOR + height - slab / 2), (width, depth, slab), top)
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = x + sx * (width / 2 - leg * 0.75)
            py = y + sy * (depth / 2 - leg * 0.75)
            mesh.box((px, py, FLOOR + (height - slab) / 2), (leg, leg, height - slab + 0.024), "wood")


def crate(mesh, x, y, z, w, d, h):
    mesh.box((x, y, z + h / 2), (w, d, h - 0.04), "wood")
    for dz in (0.045, h - 0.045):
        mesh.box((x, y, z + dz), (w + 0.04, d + 0.062, 0.106), "wood")
    for a in (-1, 1):
        for b in (-1, 1):
            mesh.box((x + a * (w / 2 - 0.035), y + b * (d / 2 - 0.025), z + h / 2),
                     (0.085, 0.085, h - 0.18), "wood")
        mesh.beam((x - w / 2 + 0.061, y + a * (d / 2 + 0.012), z + 0.092),
                  (x + w / 2 - 0.061, y + a * (d / 2 + 0.012), z + h - 0.092),
                  0.071, 0.046, "wood")
        mesh.beam((x + a * (w / 2 + 0.012), y - d / 2 + 0.061, z + 0.092),
                  (x + a * (w / 2 + 0.012), y + d / 2 - 0.061, z + h - 0.092),
                  0.071, 0.046, "wood")


def build_furniture(group, surface):
    for i in range(6):
        stand = Mesh(f"Display_{i + 1:02}", group, surface)
        table(stand, -3.30 + 1.19 * i, 3.43, 1.09, 0.70, 0.45, 0.105, 0.115)
        stand.object()

    bench = Mesh("Bench", group, surface)
    for i in range(3):
        bench.box((-3.87 + 0.168 * (i - 1), -2.54, FLOOR + 0.415), (0.164, 1.72, 0.095), "wood")
    for y in (-3.16, -1.92):
        bench.box((-3.87, y, FLOOR + 0.184), (0.435, 0.14, 0.392), "wood")
    bench.object()

    work = Mesh("Workbench", group, surface)
    table(work, -3.73, 1.03, 0.92, 2.18, 0.94, 0.14, 0.145, "dark")
    work.box((-3.73, 1.03, FLOOR + 0.22), (0.91, 2.05, 0.10), "wood")
    crate(work, -3.75, 0.90, FLOOR + 0.27, 0.60, 0.65, 0.44)
    # Three small hand tools stay as dressing at the workbench.
    top = FLOOR + 0.94
    work.beam((-3.99, 0.23, top + 0.04), (-3.99, 0.62, top + 0.04), 0.075, 0.067, "wood")
    work.beam((-4.11, 0.25, top + 0.049), (-3.86, 0.25, top + 0.049), 0.11, 0.10, "metal")
    work.beam((-3.51, 0.26, top + 0.029), (-3.51, 0.46, top + 0.029), 0.040, 0.040, "metal")
    work.beam((-3.51, 0.44, top + 0.031), (-3.51, 0.68, top + 0.031), 0.076, 0.073, "lamp")
    jaw = [(-0.044, 1.10), (0.044, 1.10), (0.044, 1.54), (0.14, 1.64), (0.13, 1.81),
           (0.072, 1.81), (0.072, 1.69), (0, 1.625), (-0.072, 1.69), (-0.072, 1.81),
           (-0.13, 1.81), (-0.14, 1.64), (-0.044, 1.54)]
    work.prism([(-3.69 + dx, y) for dx, y in jaw], top - 0.006, top + 0.061, "Z", "metal")
    # Leave a gap behind the tabletop for the projecting window sill.
    work.object().location.x = 0.11

    shelf = Mesh("RightShelving", group, surface)
    for x in (3.54, 4.09):
        for y in (-0.434, 1.36):
            shelf.box((x, y, FLOOR + 0.805), (0.15, 0.15, 1.63), "dark")
    for height in (0.22, 1.08):
        shelf.box((3.82, 0.455, FLOOR + height), (0.74, 1.97, 0.12), "wood")
    shelf.box((4.085, 0.455, FLOOR + 1.53), (0.13, 1.97, 0.19), "dark")
    crate(shelf, 3.82, 0.05, FLOOR + 1.14, 0.48, 0.58, 0.44)
    crate(shelf, 3.82, 0.76, FLOOR + 1.14, 0.54, 0.62, 0.48)
    z = FLOOR + 0.28
    shelf.lathe(3.80, 0.44, [(0.19, z - 0.009), (0.23, z + 0.055), (0.23, z + 0.44),
                            (0.13, z + 0.55), (0.13, z + 0.66),
                            (0.10, z + 0.66), (0.10, z + 0.53)], 12, "metal")
    for s in (-1, 1):
        y = 0.44 + s * 0.19
        handle = [(0, 0.47), (0.10, 0.45), (0.108, 0.315), (0, 0.30),
                  (0, 0.337), (0.071, 0.345), (0.067, 0.42), (0, 0.435)]
        shelf.prism([(y + s * dy, z + h) for dy, h in handle], 3.783, 3.817, "X", "metal")
    shelf.object().location.x = -0.06

    barrel = Mesh("Barrel", group, surface)
    x, y, z = 3.63, 3.22, FLOOR
    barrel.lathe(x, y, [(0.32, z - 0.009), (0.395, z + 0.21), (0.42, z + 0.52),
                       (0.39, z + 0.80), (0.323, z + 0.99),
                       (0.27, z + 0.99), (0.26, z + 0.79)], 12, "wood")
    for level, lower, upper in [(0.16, 0.399, 0.417), (0.74, 0.415, 0.402)]:
        barrel.lathe(x, y, [(lower, z + level), (upper, z + level + 0.09)], 12, "earth")
    barrel.object()

    for s, label, y in LANTERN_ROWS:
        lantern = Mesh(label, group, surface)
        x = s * 3.98
        lantern.box((s * 4.19, y, 2.91), (0.12, 0.23, 0.64), "dark")
        lantern.box((s * 4.04, y, 3.17), (0.37, 0.18, 0.11), "dark")
        lantern.box((x, y, 2.67), (0.346, 0.334, 0.10), "dark")
        lantern.box((x, y, 2.875), (0.26, 0.25, 0.35), "lamp")
        lantern.lathe(x, y, [(0.255, 3.04), (0.11, 3.16)], 4, "dark", phase=math.pi / 4)
        for sx in (-1, 1):
            for sy in (-1, 1):
                lantern.box((x + sx * 0.139, y + sy * 0.133, 2.874),
                            (0.045, 0.045, 0.32), "dark")
        lantern.object()


def validate_scale(scene, out):
    graph = bpy.context.evaluated_depsgraph_get()
    clear_height = min(ENTRY_TOP - 0.045, PORCH_EDGE_Z - PORCH_THICKNESS) - FLOOR
    clear_width = min(ENTRY - 0.17, 2 * POST_X - 0.48)
    assert clear_height > AVATAR_HEIGHT + 0.60
    assert clear_width > 2 * 3 * STUD
    for x in (-1.30, 0.0, 1.30):
        for relative_height in (0.10, 0.90, AVATAR_HEIGHT):
            hit, *_ = scene.ray_cast(graph, (x, -6.50, FLOOR + relative_height), (0, 1, 0), distance=8.45)
            assert not hit, (x, relative_height, "blocked entrance or aisle")
    step_levels = []
    for y, expected in [(-6.07, 0.21), (-5.46, FLOOR), (-3.80, FLOOR)]:
        hit, point, *_ = scene.ray_cast(graph, (0, y, 1.9), (0, 0, -1), distance=2.0)
        assert hit and math.isclose(point.z, expected, abs_tol=0.01), (y, point, expected)
        step_levels.append(round(point.z, 3))
    data = {
        "stud_m": STUD,
        "wall_footprint_m": [2 * HALF_W, 2 * HALF_D],
        "wall_footprint_studs": [32, 30],
        "clear_entrance_m": [round(clear_width, 3), round(clear_height, 3)],
        "clear_entrance_studs": [round(clear_width / STUD, 2), round(clear_height / STUD, 2)],
        "tested_avatar_height_studs": AVATAR_HEIGHT / STUD,
        "free_route_width_m": 2.60,
        "free_route_ray_count": 9,
        "step_tops_m": step_levels,
        "bench_seat_m_above_floor": 0.4625,
        "workbench_top_m_above_floor": 0.94,
        "stand_top_m_above_floor": 0.45,
        "shelf_levels_m_above_floor": [0.28, 1.14],
    }
    out.with_name("scale-check.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--blockout", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene["roblox_stud_m"] = STUD
    scene["entry_faces"] = "-Y"
    bpy.context.preferences.filepaths.save_version = 0
    model = collection(MODEL, scene.collection)
    shell = collection("Shell and porch", model)
    roof = collection("Main roof and gables", model)
    surface = palette()
    build_shell(shell, roof, surface, args.blockout)
    if not args.blockout:
        build_furniture(collection("Furniture", model), surface)
        bpy.context.view_layer.update()
        validate_scale(scene, out)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                view = area.spaces.active
                view.shading.type = "MATERIAL"
                view.region_3d.view_location = (0, -0.45, 2.90)
                view.region_3d.view_rotation = Vector((9, -15, 8)).to_track_quat("Z", "Y")
                view.region_3d.view_distance = 20
    bpy.ops.wm.save_as_mainfile(filepath=str(out))


if __name__ == "__main__":
    main()
