"""Grinch, version 2 (card e49171): chunkier, shaggier and more cartoon than art/models/grinch.

    blender -b --factory-startup --python build_grinch.py -- --out <abs Grinch_master.blend> --texture <abs Grinch_Palette.png>

Concept: art/refs/grinch/grinch-v2.png (front, side, back, T-pose). Metres, Z up, the model faces -Y, feet on z = 0.
About twice a default Roblox avatar (1.45 m) with the hat on.
Fur is not loose spikes: the body, the head, the arms and the legs are single shells whose tiers overhang the tier
below and end in a jagged fringe of the lighter green, so nearly every triangle is seen.
One mesh Grinch_Body, one material M_Grinch_Palette over a 64 x 64 palette texture (16 x 16 cells, Closest).
"""
import argparse
import math
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

MODEL = 'Grinch'
# Colours of art/palette.json core, in the order of their cells in the texture.
COLORS = {
    'green': '5BB830',   # Зелёная кнопка: skin and fur
    'light': '96DC6A',   # Трава: light fringes of the fur
    'dark': '3C8E63',    # Тень хвои: boots
    'pine': '54A577',    # Хвоя: boot cuffs
    'red': 'D6392B',     # Красный амбар: hat and sack
    'cream': 'FFFDF5',   # Крем: hat trim, pom-pom, eyes, fangs, stars
    'brown': '80401B',   # Тёмное дерево: rope belt, tongue
    'ink': '2B1A11',     # Контур: brows, pupils, mouth
}
ORDER = list(COLORS)
GRID = 4
CELL = 16
SIZE = GRID * CELL
TAU = 2 * math.pi
HEAD_DZ = -0.12   # the head, the face and the hat are modelled 0.12 m higher and moved down

rng = random.Random(2714)
WORLD = (Vector((0, 0, 0)), Matrix.Identity(3))


def cell_uv(color):
    i = ORDER.index(color)
    col, row = i % GRID, i // GRID
    return ((col + 0.5) / GRID, (row + 0.5) / GRID)


class Ring:
    """A ring of a shell: `tips` is None for a plain ring or the parity of the fringe tips of a jagged one."""
    def __init__(self, pts, color, tips=None):
        self.pts, self.color, self.tips = pts, color, tips


def ring(z, rx, ry, segs, color, ox=0.0, oy=0.0, zig=None, parity=0, jit=0.0, frame=WORLD, mod=None):
    """An ellipse in the frame's XY plane at height z; `color` paints the band between the previous ring and this one.
    zig = (dz, dr): every second vertex is a notch, moved by dz along the axis and pulled in by the share dr;
    the others are the tips of the fringe. The tips differ in length and stand a little off their places,
    so the fringe is a hand-cut fur edge and not a saw."""
    pts = []
    for j in range(segs):
        a = TAU * j / segs
        r, dz = 1.0, 0.0
        if zig:
            if (j + parity) % 2:
                dz, r = zig[0], 1 - zig[1]
            else:
                a += TAU / segs * rng.uniform(-0.22, 0.22)
                r = 1 + rng.uniform(-0.02, 0.05)
                dz = -zig[0] * rng.uniform(-0.25, 0.35)
        elif jit:
            r = 1 + rng.uniform(-jit, jit)
        p = Vector((ox + math.cos(a) * rx * r, oy + math.sin(a) * ry * r, z + dz))
        if mod:
            p = mod(a, p)
        pts.append(frame[0] + frame[1] @ p)
    return Ring(pts, color, parity if zig else None)


class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new('UVMap')

    def face(self, verts, color):
        f = self.bm.faces.new(verts)
        u = cell_uv(color)
        for loop in f.loops:
            loop[self.uv].uv = u
        return f

    def vert(self, co):
        return self.bm.verts.new(co)

    def shell(self, rings, start, end, end_color=None):
        """A closed shell through the rings with a fan at both ends. A band next to a jagged ring is cut so that every
        tooth is two facets meeting on a ridge."""
        vs = [[self.vert(p) for p in r.pts] for r in rings]
        n = len(vs[0])
        for i in range(1, len(rings)):
            a, b, color = vs[i - 1], vs[i], rings[i].color
            zb, za = rings[i].tips, rings[i - 1].tips
            for j in range(n):
                k = (j + 1) % n
                if zb is None and za is None:
                    self.face([a[j], a[k], b[k], b[j]], color)
                    continue
                parity = zb if zb is not None else za
                tip_at_j = (j + parity) % 2 == 0
                if tip_at_j:
                    self.face([a[j], a[k], b[k]], color)
                    self.face([a[j], b[k], b[j]], color)
                else:
                    self.face([a[j], a[k], b[j]], color)
                    self.face([a[k], b[k], b[j]], color)
        c = self.vert(start)
        for j in range(n):
            self.face([vs[0][(j + 1) % n], vs[0][j], c], rings[1].color)
        c = self.vert(end)
        for j in range(n):
            self.face([vs[-1][j], vs[-1][(j + 1) % n], c], end_color or rings[-1].color)

    def ellipsoid(self, center, radii, segs, rings, color, jitter=0.0, matrix=None, flat_bottom=None):
        """A low UV sphere; jitter moves the vertices along the normal for a hand-cut look."""
        rx, ry, rz = radii
        m = matrix or Matrix.Identity(3)
        c = Vector(center)
        rr = []
        for i in range(1, rings):
            th = math.pi * i / rings
            pts = []
            for j in range(segs):
                ph = TAU * j / segs
                k = 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
                p = c + m @ Vector((math.sin(th) * math.cos(ph) * rx * k, math.sin(th) * math.sin(ph) * ry * k,
                                    -math.cos(th) * rz * k))
                if flat_bottom is not None:
                    p.z = max(p.z, flat_bottom)
                pts.append(p)
            rr.append(Ring(pts, color))
        bottom = c + m @ Vector((0, 0, -rz))
        if flat_bottom is not None:
            bottom.z = max(bottom.z, flat_bottom)
        self.shell(rr, bottom, c + m @ Vector((0, 0, rz)))

    def tube(self, path, radii, segs, color, side=Vector((0, 0, 1)), flat=1.0, jitter=0.0, turn=0.0):
        """Circles along a polyline; `side` fixes the ring orientation, `flat` squashes the ring along it."""
        rr = []
        for i, (p, r) in enumerate(zip(path, radii)):
            p = Vector(p)
            d = (Vector(path[min(i + 1, len(path) - 1)]) - Vector(path[max(i - 1, 0)])).normalized()
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            pts = []
            for j in range(segs):
                a = TAU * j / segs + turn
                k = 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
                pts.append(p + (u * math.cos(a) * flat + v * math.sin(a)) * r * k)
            rr.append(Ring(pts, color))
        start = Vector(path[0]) - (Vector(path[1]) - Vector(path[0])).normalized() * radii[0] * 0.5
        end = Vector(path[-1]) + (Vector(path[-1]) - Vector(path[-2])).normalized() * radii[-1] * 0.5
        self.shell(rr, start, end)

    def loop_tube(self, points, radius, segs, color, side=Vector((0, 0, 1)), jitter=0.0):
        """A closed ring tube through `points` (the belt, the fur trim of the hat)."""
        n = len(points)
        rings = []
        for i in range(n):
            p = Vector(points[i])
            d = (Vector(points[(i + 1) % n]) - Vector(points[i - 1])).normalized()
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            r = radius(i) if callable(radius) else radius
            rg = []
            for j in range(segs):
                a = TAU * j / segs
                k = 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
                rg.append(self.vert(p + (u * math.cos(a) + v * math.sin(a)) * r * k))
            rings.append(rg)
        for i in range(n):
            a, b = rings[i], rings[(i + 1) % n]
            for j in range(segs):
                self.face([a[j], a[(j + 1) % segs], b[(j + 1) % segs], b[j]], color)

    def gem(self, outline, apex, back, color):
        """A raised facet shape on a surface: fans from the outline to the apex in front and to `back` inside."""
        vs = [self.vert(p) for p in outline]
        ca, cb = self.vert(apex), self.vert(back)
        n = len(vs)
        for j in range(n):
            self.face([vs[j], vs[(j + 1) % n], ca], color)
            self.face([vs[(j + 1) % n], vs[j], cb], color)


def build(texture_path):
    b = Builder()

    # ---- Boots: fat clogs with a flat sole and a thick lighter cuff.
    for s in (1, -1):
        x = 0.20 * s
        b.ellipsoid((0.235 * s, -0.13, 0.15), (0.25, 0.37, 0.21), 8, 5, 'dark', jitter=0.03, flat_bottom=0.0)
        b.shell([ring(0.20, 0.15, 0.16, 8, 'pine', ox=x, oy=-0.01),
                 ring(0.40, 0.185, 0.195, 8, 'pine', ox=x, oy=-0.01, jit=0.03),
                 ring(0.44, 0.10, 0.10, 8, 'pine', ox=x, oy=-0.01)],
                Vector((x, -0.01, 0.18)), Vector((x, -0.01, 0.43)))

    # ---- Legs: long and bare, thicker than in version 1; a ring at the knee for the rig.
    for s in (1, -1):
        x = 0.20 * s
        b.shell([ring(0.42, 0.098, 0.098, 8, 'green', ox=x),
                 ring(0.80, 0.10, 0.10, 8, 'green', ox=x * 0.98),
                 ring(1.24, 0.11, 0.11, 8, 'green', ox=x * 0.95)],
                Vector((x, 0, 0.40)), Vector((x * 0.95, 0, 1.28)))

    # ---- Body: one pear-shaped shell of three fur tiers. The chest is narrow, the belly is a ball pushed forward,
    # the back is nearly flat, the belt cuts into the waist. Only the teeth of each fringe are light.
    n = 20
    b.shell([
        ring(1.20, 0.30, 0.30, n, 'green', oy=-0.07),
        ring(1.15, 0.41, 0.41, n, 'green', oy=-0.09, zig=(0.10, 0.03)),              # hem
        ring(1.27, 0.485, 0.49, n, 'light', oy=-0.12),
        ring(1.38, 0.555, 0.565, n, 'green', oy=-0.145),                             # the belly at its widest
        ring(1.49, 0.535, 0.545, n, 'green', oy=-0.135),
        ring(1.56, 0.475, 0.48, n, 'green', oy=-0.11),                               # waist: the belt
        ring(1.635, 0.47, 0.47, n, 'green', oy=-0.10),
        ring(1.59, 0.545, 0.535, n, 'green', oy=-0.115, zig=(0.10, 0.04), parity=1),  # over the belt
        ring(1.71, 0.515, 0.495, n, 'light', oy=-0.10),
        ring(1.79, 0.45, 0.42, n, 'green', oy=-0.07),
        ring(1.845, 0.385, 0.35, n, 'green', oy=-0.05),
        ring(1.805, 0.455, 0.41, n, 'green', oy=-0.055, zig=(0.085, 0.04)),          # chest
        ring(1.905, 0.42, 0.375, n, 'light', oy=-0.045),
        ring(1.97, 0.33, 0.30, n, 'green', oy=-0.03),
        ring(2.03, 0.21, 0.19, n, 'green', oy=-0.02),
    ], Vector((0, -0.06, 1.18)), Vector((0, -0.02, 2.07)))

    # ---- Arms: T-pose, thinner to the wrist. A short soft fur tier at the shoulder; a huge mitt, twice as tall
    # as the arm, with three fat fingers and a thumb.
    AZ = 1.86
    for s in (1, -1):
        fr = (Vector((0, 0, AZ)), Matrix(((0, 0, s), (0, -s, 0), (1, 0, 0))))   # local z runs along the arm
        b.shell([
            ring(0.28, 0.125, 0.125, 10, 'green', frame=fr),
            ring(0.42, 0.135, 0.135, 10, 'green', frame=fr),
            ring(0.49, 0.15, 0.15, 10, 'light', frame=fr, zig=(-0.065, 0.08)),
            ring(0.47, 0.115, 0.115, 10, 'green', frame=fr),
            ring(0.76, 0.105, 0.105, 10, 'green', frame=fr),
            ring(1.06, 0.09, 0.09, 10, 'green', frame=fr),
        ], Vector((0.24 * s, 0, AZ)), Vector((1.12 * s, 0, AZ)))
        b.ellipsoid((1.28 * s, 0.0, AZ), (0.24, 0.215, 0.195), 8, 5, 'green', jitter=0.03)
        for dy, tip in ((-0.145, 1.60), (0.0, 1.64), (0.145, 1.60)):
            b.tube([(1.40 * s, dy, AZ - 0.02), (tip * s, dy * 1.05, AZ - 0.035)], [0.085, 0.072], 6, 'green',
                   side=Vector((0, 0, 1)))
        b.ellipsoid((1.27 * s, -0.235, AZ - 0.04), (0.09, 0.09, 0.13), 6, 3, 'green', jitter=0.02,
                    matrix=Matrix.Rotation(math.radians(90), 3, 'X') @ Matrix.Rotation(math.radians(25 * s), 3, 'Y'))

    b.bm.verts.ensure_lookup_table()
    head_from = len(b.bm.verts)
    # ---- Head: a big shell with a beard tier round the cheeks and the jaw and a fringe under the hat.
    hc = Vector((0.0, -0.02, 2.40))
    head_r = (0.47, 0.44, 0.46)
    n = 16

    def bangs(a, p):
        w = max(0.0, math.cos(a - 1.5 * math.pi)) ** 2   # 1 at the face: the fringe is shorter over the brows
        p.z += 0.05 * w
        p.y += 0.02 * w
        return p
    b.shell([
        ring(2.09, 0.24, 0.22, n, 'green', oy=-0.02),
        ring(2.02, 0.44, 0.395, n, 'green', oy=-0.02, zig=(0.135, 0.09)),             # beard and cheek fluff
        ring(2.175, 0.405, 0.375, n, 'light', oy=-0.02),
        ring(2.29, 0.455, 0.425, n, 'green', oy=-0.02),
        ring(2.42, 0.475, 0.445, n, 'green', oy=-0.02),                               # widest at the eyes
        ring(2.54, 0.445, 0.415, n, 'green', oy=-0.02),
        ring(2.645, 0.355, 0.335, n, 'green', oy=-0.02),
        ring(2.585, 0.42, 0.39, n, 'green', oy=-0.02, zig=(0.085, 0.05), parity=1, mod=bangs),  # fringe under the hat
        ring(2.685, 0.395, 0.365, n, 'light', oy=-0.02, mod=bangs),
        ring(2.77, 0.32, 0.30, n, 'green', oy=-0.02),
    ], Vector((0, -0.02, 2.04)), Vector((0, -0.02, 2.84)))

    # Big pointy ears, out to the sides and a little up and back.
    for s in (1, -1):
        base = Vector((0.38 * s, 0.02, 2.45))
        b.tube([base, base + Vector((0.17 * s, 0.02, 0.07)), base + Vector((0.36 * s, 0.05, 0.19))],
               [0.15, 0.10, 0.02], 6, 'green', side=Vector((0, 1, 0)), flat=0.5)

    def on_head(x, z, lift=0.0):
        """The point on the front of the head ball at (x, z), pushed `lift` along -Y."""
        dx, dz = (x - hc.x) / head_r[0], (z - hc.z) / head_r[2]
        y = hc.y - head_r[1] * math.sqrt(max(0.0, 1 - dx * dx - dz * dz))
        return Vector((x, y - lift, z))

    # Eyes: big bulging whites, dark pupils looking a little inward, angry brows sloping down to the nose
    # that cover only the upper inner corner of each white.
    for s in (1, -1):
        tilt = Matrix.Rotation(math.radians(-8 * s), 3, 'Y')
        b.ellipsoid(on_head(0.16 * s, 2.45, -0.015), (0.105, 0.08, 0.09), 8, 4, 'cream', matrix=tilt)
        b.ellipsoid(on_head(0.125 * s, 2.435, 0.055), (0.047, 0.03, 0.052), 6, 3, 'ink')
        b.tube([on_head(0.04 * s, 2.50, 0.055), on_head(0.17 * s, 2.575, 0.052), on_head(0.31 * s, 2.615, 0.02)],
               [0.034, 0.042, 0.026], 6, 'ink', side=Vector((0, 0, 1)), flat=0.6)

    # Mouth: a short upper lip no wider than the mouth, a big dark open mouth under it, a small chin;
    # fangs and a tongue. Nothing sticks out of the face further than 0.1 m.
    b.ellipsoid((0.0, -0.405, 2.25), (0.245, 0.105, 0.048), 8, 4, 'green')
    b.ellipsoid((0.0, -0.365, 2.165), (0.235, 0.115, 0.13), 8, 4, 'ink')
    b.ellipsoid((0.0, -0.40, 2.015), (0.16, 0.095, 0.05), 6, 4, 'green')
    b.ellipsoid((0.0, -0.43, 2.075), (0.095, 0.055, 0.035), 6, 3, 'brown')
    for s in (1, -1):
        top = Vector((0.12 * s, -0.47, 2.215))
        b.gem([top + Vector((-0.045, 0.0, 0)), top + Vector((0, -0.035, 0)), top + Vector((0.045, 0.0, 0)),
               top + Vector((0, 0.04, 0))], top + Vector((0, -0.005, -0.125)), top + Vector((0, 0.0, 0.04)), 'cream')

    # ---- The stolen Santa hat: a fat fur roll with a jagged lower edge, a red cone bent over to the side
    # and hanging down past the ear, a big pom-pom on its end.
    n = 16
    tf = (Vector((0.0, -0.02, 2.74)), Matrix.Rotation(math.radians(-5), 3, 'Y'))
    b.shell([
        ring(-0.07, 0.37, 0.345, n, 'cream', frame=tf),
        ring(-0.14, 0.47, 0.44, n, 'cream', frame=tf, zig=(0.075, 0.02)),
        ring(-0.01, 0.51, 0.48, n, 'cream', frame=tf, jit=0.025),
        ring(0.09, 0.475, 0.445, n, 'cream', frame=tf, jit=0.02),
        ring(0.12, 0.38, 0.355, n, 'cream', frame=tf),
    ], tf[0] + Vector((0, 0, -0.05)), tf[0] + Vector((0, 0, 0.13)))
    hat_path = [(0.0, -0.02, 2.80), (0.02, -0.01, 2.95), (0.10, 0.0, 3.04), (0.26, 0.03, 3.07), (0.46, 0.07, 3.03),
                (0.66, 0.10, 2.93), (0.82, 0.12, 2.80), (0.90, 0.12, 2.62)]
    b.tube(hat_path, [0.40, 0.33, 0.245, 0.175, 0.135, 0.105, 0.08, 0.06], 8, 'red', side=Vector((0, 1, 0)), jitter=0.03)
    b.ellipsoid((0.92, 0.12, 2.45), (0.16, 0.16, 0.16), 8, 5, 'cream', jitter=0.07)

    for v in list(b.bm.verts)[head_from:]:
        v.co.z += HEAD_DZ

    # ---- Rope belt in the waist, a knot in front and two ends lying on the belly.
    bz = 1.565
    count = 14
    belt = [(math.cos(TAU * j / count) * 0.505, -0.11 + math.sin(TAU * j / count) * 0.51, bz) for j in range(count)]
    b.loop_tube(belt, 0.048, 4, 'brown')
    knot = Vector((0.13, -0.635, bz))
    b.ellipsoid(knot, (0.085, 0.06, 0.07), 6, 4, 'brown')
    for dx, end in ((-0.035, 1.33), (0.05, 1.355)):
        x = knot.x + dx
        b.tube([Vector((x, knot.y + 0.01, bz - 0.03)), Vector((x + dx * 0.3, -0.688, 1.50)),
                Vector((x + dx * 0.6, -0.72, 1.42)), Vector((x + dx * 0.8, -0.70, end))],
               [0.034, 0.032, 0.032, 0.034], 4, 'brown', side=Vector((1, 0, 0)))

    # ---- The stolen sack on the left hip: a fat red bag tied at the neck, two raised cream stars.
    sc = Vector((0.71, -0.16, 1.23))
    sr = (0.28, 0.25, 0.32)
    b.ellipsoid(sc, sr, 8, 6, 'red', jitter=0.04)
    neck = sc + Vector((-0.08, 0.03, 0.33))
    b.tube([neck + Vector((0.02, 0, -0.08)), neck + Vector((-0.01, 0, 0.04))], [0.09, 0.07], 6, 'brown')
    b.tube([neck + Vector((-0.01, 0, 0.03)), neck + Vector((-0.04, 0, 0.14))], [0.07, 0.125], 6, 'red', jitter=0.1)
    for dx, dz, r in ((0.07, 0.07, 0.085), (-0.09, -0.11, 0.06)):
        def on_sack(x, z, lift):
            u, w = (x - sc.x) / sr[0], (z - sc.z) / sr[2]
            return Vector((x, sc.y - sr[1] * math.sqrt(max(0.0, 1 - u * u - w * w)) - lift, z))
        cx, cz = sc.x + dx, sc.z + dz
        pts = []
        for j in range(10):
            a = TAU * j / 10 + math.pi / 2
            rr = r if j % 2 == 0 else r * 0.5
            pts.append(on_sack(cx + math.cos(a) * rr, cz + math.sin(a) * rr, 0.004))
        b.gem(list(reversed(pts)), on_sack(cx, cz, 0.03), on_sack(cx, cz, -0.03), 'cream')

    # One mesh, flat shaded.
    mesh = bpy.data.meshes.new(MODEL + '_Body')
    bmesh.ops.recalc_face_normals(b.bm, faces=b.bm.faces[:])
    b.bm.to_mesh(mesh)
    b.bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = False
    ob = bpy.data.objects.new(MODEL + '_Body', mesh)
    col = bpy.data.collections.new(MODEL)
    bpy.context.scene.collection.children.link(col)
    col.objects.link(ob)

    # Palette texture and material.
    img = bpy.data.images.new(MODEL + '_Palette', SIZE, SIZE, alpha=False)
    px = [0.0] * (SIZE * SIZE * 4)
    for y in range(SIZE):
        for x in range(SIZE):
            i = (y // CELL) * GRID + x // CELL
            code = COLORS[ORDER[i]] if i < len(ORDER) else COLORS['green']
            rgb = [int(code[k:k + 2], 16) for k in (0, 2, 4)]
            o = (y * SIZE + x) * 4
            px[o:o + 4] = [rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1.0]
    img.pixels.foreach_set(px)
    img.filepath_raw = texture_path
    img.file_format = 'PNG'
    img.save()
    mat = bpy.data.materials.new('M_' + MODEL + '_Palette')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next(nd for nd in nodes if nd.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.85
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Closest'
    mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    mesh.materials.append(mat)
    return ob, img


def main(argv):
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--texture', required=True)
    a = p.parse_args(argv)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    ob, img = build(a.texture)
    bpy.ops.wm.save_as_mainfile(filepath=a.out)
    img.filepath = bpy.path.relpath(a.texture)
    bpy.ops.wm.save_mainfile()
    tris = sum(len(pg.vertices) - 2 for pg in ob.data.polygons)
    lo = [min(v.co[i] for v in ob.data.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in ob.data.vertices) for i in range(3)]
    print('GRINCH tris=%d size=%s' % (tris, ['%.3f' % (h - l) for l, h in zip(lo, hi)]))


if __name__ == '__main__':
    main(sys.argv)
