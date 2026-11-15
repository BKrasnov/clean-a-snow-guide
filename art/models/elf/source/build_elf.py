"""Elf (card a76ac5): the Grinch's mean elf henchman, built from faceted low-poly shapes.

    blender -b --factory-startup --python build_elf.py -- --out <abs Elf_master.blend> --texture <abs Elf_Palette.png>

Concept: art/refs/grinch/elf.png (front, side, back, T-pose). Metres, Z up, the model faces -Y, feet on z = 0.
A child-sized elf, a little shorter than a Roblox avatar (about 1.45 m): the top of the head 1.04 m, the hat 1.4 m.
One mesh Elf_Body, one material M_Elf_Palette over a 64 x 64 palette texture: every face points at the middle of
its colour's 16 x 16 cell, so the colours stay flat at every mip level. Flat shading: the facets show.
Face features, patches and the collar are decals: outlines cast onto the faceted surface along a ray, lifted a few
millimetres off it and closed by a cone that goes back inside the body, so nothing sticks out sideways as a plate.
"""
import argparse
import math
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

MODEL = 'Elf'
# Colours of art/palette.json core, in the order of their cells in the texture.
SKINS = {
    'peach': ('F2C29A', 'FF78BE'),  # Кожа (palette, Leonid 14.11.2026), Конфетный снег blush
    'wood': ('CD925C', 'FF78BE'),   # Дерево skin, Конфетный снег blush
    'straw': ('FAD66E', 'FF78BE'),  # Солома skin, Конфетный снег blush
}
COLORS = {
    'skin': 'F2C29A',    # Кожа: face, ears, hands (set from SKINS by --skin)
    'blush': 'FF78BE',   # Конфетный снег: cheeks
    'green': '54A577',   # Хвоя: hat and tunic
    'dgreen': '3C8E63',  # Тень хвои: patches, stocking stripes, under the skirt
    'lime': '96DC6A',    # Трава: hem, cuffs, collar, stocking stripes
    'brown': '80401B',   # Тёмное дерево: hair, belt, boots, buckle window
    'grey': '909282',    # Камень: pom-pom, buckle
    'cream': 'FFFDF5',   # Крем: eye whites, fang
    'ink': '2B1A11',     # Контур: pupils, brows, mouth
}
ORDER = list(COLORS)
GRID = 4
CELL = 16
SIZE = GRID * CELL

rng = random.Random(4471)


def cell_uv(color):
    i = ORDER.index(color)
    col, row = i % GRID, i // GRID
    return ((col + 0.5) / GRID, (row + 0.5) / GRID)


def V(*a):
    return Vector(a)


class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new('UVMap')
        self.bvh = None

    def face(self, verts, color):
        f = self.bm.faces.new(verts)
        u = cell_uv(color)
        for loop in f.loops:
            loop[self.uv].uv = u
        return f

    def vert(self, co):
        return self.bm.verts.new(co)

    def loft(self, rings, colors, start_point=None, end_point=None, start_color=None, end_color=None, close=False):
        """Rings of the same length lofted into a tube; colors[i] paints the strip between ring i and ring i + 1
        (a single colour paints all). The ends close as fans round start_point / end_point; `close` joins the last
        ring to the first (a torus)."""
        vs = [[p if isinstance(p, bmesh.types.BMVert) else self.vert(p) for p in ring] for ring in rings]
        n = len(vs[0])
        strips = list(zip(vs, vs[1:])) + ([(vs[-1], vs[0])] if close else [])
        for i, (a, b) in enumerate(strips):
            c = colors if isinstance(colors, str) else colors[i]
            for j in range(n):
                self.face([a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]], c)
        if start_point is not None:
            c = self.vert(start_point)
            col = start_color or (colors if isinstance(colors, str) else colors[0])
            for j in range(n):
                self.face([vs[0][(j + 1) % n], vs[0][j], c], col)
        if end_point is not None:
            c = self.vert(end_point)
            col = end_color or (colors if isinstance(colors, str) else colors[-1])
            for j in range(n):
                self.face([vs[-1][j], vs[-1][(j + 1) % n], c], col)
        return vs

    def ellipsoid(self, center, radii, segs, rings, color, jitter=0.0, matrix=None, flat_bottom=None):
        """A low UV sphere with its poles on the local Z axis; `matrix` turns it; jitter gives a hand-cut look."""
        rx, ry, rz = radii
        m = matrix or Matrix.Identity(3)
        c = Vector(center)
        ring_pts = []
        for i in range(1, rings):
            th = math.pi * i / rings
            ring = []
            for j in range(segs):
                ph = 2 * math.pi * j / segs
                k = 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
                p = m @ V(math.sin(th) * math.cos(ph) * rx * k, math.sin(th) * math.sin(ph) * ry * k,
                          -math.cos(th) * rz * k) + c
                if flat_bottom is not None:
                    p.z = max(p.z, flat_bottom)
                ring.append(p)
            ring_pts.append(ring)
        bottom = m @ V(0, 0, -rz) + c
        top = m @ V(0, 0, rz) + c
        if flat_bottom is not None:
            bottom.z = max(bottom.z, flat_bottom)
        return self.loft(ring_pts, color, start_point=bottom, end_point=top)

    def tube(self, path, radii, segs, color, side=V(0, 0, 1), flat=1.0, jitter=0.0, caps=True, twist=0.0):
        """Circles along a polyline; `side` fixes the ring orientation, `flat` squashes the ring along it."""
        rings = []
        for i, (p, r) in enumerate(zip(path, radii)):
            p = Vector(p)
            d = (Vector(path[min(i + 1, len(path) - 1)]) - Vector(path[max(i - 1, 0)])).normalized()
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            ring = []
            for j in range(segs):
                a = 2 * math.pi * j / segs + twist
                k = 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
                ring.append(p + (u * math.cos(a) * flat + v * math.sin(a)) * r * k)
            rings.append(ring)
        start = Vector(path[0]) - (Vector(path[1]) - Vector(path[0])).normalized() * radii[0] * 0.5 if caps else None
        end = Vector(path[-1]) + (Vector(path[-1]) - Vector(path[-2])).normalized() * radii[-1] * 0.5 if caps else None
        return self.loft(rings, color, start_point=start, end_point=end)

    def box(self, lo, hi, color):
        (x0, y0, z0), (x1, y1, z1) = lo, hi
        v = [self.vert(V(x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
        for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            self.face([v[i] for i in f], color)

    # Decals: outlines cast onto the solid body built so far.
    def freeze(self):
        """Take the solid body as the surface for decals."""
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        self.bm.normal_update()
        self.bvh = BVHTree.FromBMesh(self.bm)

    def cast(self, p, d):
        loc, nrm, _, _ = self.bvh.ray_cast(p - d * 2.0, d)
        if loc is None:
            raise RuntimeError('decal ray missed the body at %s' % (tuple(round(x, 3) for x in p),))
        if nrm.dot(d) > 0:
            nrm = -nrm
        return loc, nrm

    def decal(self, points, d, color, lift=0.008, depth=0.03, dome=0.002):
        """A flat patch: `points` (a star-shaped outline in front of the body) cast along `d`, lifted `lift` off the
        hit faces; a fan round the lifted middle in front, a cone to a point `depth` inside the body behind."""
        d = Vector(d).normalized()
        hits = [self.cast(Vector(p), d) for p in points]
        mid = sum((Vector(p) for p in points), Vector()) / len(points)
        cl, cn = self.cast(mid, d)
        front = [self.vert(loc + n * lift) for loc, n in hits]
        cf = self.vert(cl + cn * (lift + dome))
        back = self.vert(cl - cn * depth)
        n = len(front)
        for j in range(n):
            self.face([front[j], front[(j + 1) % n], cf], color)
            self.face([front[(j + 1) % n], front[j], back], color)

    def strip(self, line, widths, d, up, color, lift=0.008, depth=0.025):
        """A band along `line` (points in front of the body), `widths[i]` half-wide across it in the plane facing
        `d`, cast along `d`: a lifted front, two walls into the body and two end caps."""
        d = Vector(d).normalized()
        line = [Vector(p) for p in line]
        tops, bots, mids = [], [], []
        for i, (p, w) in enumerate(zip(line, widths)):
            t = (line[min(i + 1, len(line) - 1)] - line[max(i - 1, 0)]).normalized()
            across = d.cross(t).normalized()
            if across.dot(up) < 0:
                across = -across
            lt, nt = self.cast(p + across * w, d)
            lb, nb = self.cast(p - across * w, d)
            lm, nm = self.cast(p, d)
            tops.append(self.vert(lt + nt * lift))
            bots.append(self.vert(lb + nb * lift))
            mids.append(self.vert(lm - nm * depth))
        for i in range(len(line) - 1):
            self.face([tops[i], tops[i + 1], bots[i + 1], bots[i]], color)
            self.face([tops[i + 1], tops[i], mids[i], mids[i + 1]], color)
            self.face([bots[i], bots[i + 1], mids[i + 1], mids[i]], color)
        self.face([tops[0], bots[0], mids[0]], color)
        self.face([tops[-1], mids[-1], bots[-1]], color)


def plane_outline(center, d, pts2d):
    """2D points (across, up) on the plane through `center` facing `d` (up stays world Z)."""
    d = Vector(d).normalized()
    across = d.cross(V(0, 0, 1)).normalized()
    up = across.cross(d).normalized()
    return [Vector(center) + across * a + up * b for a, b in pts2d]


def square_patch(half, notch=0.007, turn=0.2):
    """A square patch with a stitch notch in the middle of every side, turned by `turn` radians."""
    pts = []
    for i in range(4):
        a = turn + math.pi / 2 * i
        side = V(math.cos(a), math.sin(a), 0)              # the outward normal of this side
        along = V(-math.sin(a), math.cos(a), 0)
        for t, inset in ((-1.0, 0.0), (-0.3, 0.0), (0.0, notch), (0.3, 0.0)):
            p = side * (half - inset) + along * half * t
            pts.append((p.x, p.y))
    return pts


def stitched(r, n=12, notch=0.72, squash=1.0, turn=0.25):
    """A patch outline: a rough square-ish blob with stitch notches."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + turn
        k = notch if i % 3 == 1 else 1.0
        k *= 1 + rng.uniform(-0.06, 0.06)
        sq = 1 / max(abs(math.cos(a)), abs(math.sin(a))) ** 0.45
        pts.append((math.cos(a) * r * k * sq, math.sin(a) * r * k * sq * squash))
    return pts


HEAD_C = V(0.0, 0.0, 0.875)
HEAD_R = (0.205, 0.195, 0.165)


def head_point(phi, z, grow=0.0):
    """The point of the head ellipsoid at azimuth `phi` (0 = +X, -90 deg = front) and height z, grown by `grow`."""
    dz = max(-0.999, min(0.999, (z - HEAD_C.z) / HEAD_R[2]))
    s = math.sqrt(1 - dz * dz)
    return V(HEAD_C.x + (HEAD_R[0] * s + grow) * math.cos(phi), HEAD_C.y + (HEAD_R[1] * s + grow) * math.sin(phi), z)


def build(texture_path):
    b = Builder()

    # Boots: a shaft with a thick cuff, a foot pointing forward on a flat sole, the toe curling up and back.
    for s in (1, -1):
        pivot = V(0.09 * s, 0.0, 0.0)
        turn = Matrix.Rotation(math.radians(40 * s), 3, 'Z')

        def T(p):
            return turn @ Vector(p) + pivot
        segs = 8
        shaft = [(0.0, 0.076), (0.095, 0.076), (0.095, 0.092), (0.165, 0.09)]
        rings = []
        for z, r in shaft:
            rings.append([T(V(math.cos(2 * math.pi * j / segs + math.pi / 8) * r,
                              0.015 + math.sin(2 * math.pi * j / segs + math.pi / 8) * r * 0.95, z))
                          for j in range(segs)])
        b.loft(rings, 'brown', start_point=T(V(0, 0.015, 0.0)), end_point=T(V(0, 0.015, 0.165)))
        foot = Matrix.Rotation(math.radians(90), 3, 'X')
        b.ellipsoid(T(V(0, -0.04, 0.052)), (0.075, 0.055, 0.115), 8, 4, 'brown', jitter=0.03,
                    matrix=turn @ foot, flat_bottom=0.0)
        curl = [V(0, -0.10, 0.05), V(0, -0.16, 0.05), V(0, -0.205, 0.085), V(0, -0.195, 0.128), V(0, -0.162, 0.126)]
        b.tube([T(p) for p in curl], [0.046, 0.04, 0.032, 0.028, 0.026], 5, 'brown',
               side=turn @ V(1, 0, 0), flat=1.0)

    # Legs: striped stockings, dark green and lime, from inside the boot up into the skirt.
    for s in (1, -1):
        zs = [0.15, 0.205, 0.24, 0.275, 0.34]
        cols = ['lime', 'dgreen', 'lime', 'dgreen']
        segs = 6
        rings = [[V(0.09 * s + math.cos(2 * math.pi * j / segs) * 0.066,
                    math.sin(2 * math.pi * j / segs) * 0.064, z) for j in range(segs)] for z in zs]
        b.loft(rings, cols, start_point=V(0.09 * s, 0, zs[0] - 0.02), end_point=V(0.09 * s, 0, zs[-1] + 0.02))

    # Tunic: a bell of 12-sided rings; the belt is a step out; a lime collar round the neck.
    segs = 12

    def ring(z, rx, ry, oy=0.0, n=segs, jit=0.02, zj=0.0, phase=0.0):
        pts = []
        for j in range(n):
            a = 2 * math.pi * (j + phase) / n
            k = 1 + rng.uniform(-jit, jit)
            pts.append(V(math.cos(a) * rx * k, oy + math.sin(a) * ry * k, z + rng.uniform(-zj, zj)))
        return pts
    torso = [
        ring(0.37, 0.232, 0.188),             # top of the hem (shared with the zigzag)
        ring(0.388, 0.228, 0.186, jit=0.0),   # belt bottom
        ring(0.468, 0.212, 0.172, jit=0.0),
        ring(0.468, 0.194, 0.158, jit=0.0),   # step back in over the belt
        ring(0.55, 0.172, 0.142),
        ring(0.64, 0.156, 0.128),
        ring(0.695, 0.138, 0.114, jit=0.0),   # shoulders
        ring(0.728, 0.074, 0.07, jit=0.0),    # the neck, under the chin
    ]
    tv = b.loft(torso, ['green', 'brown', 'brown', 'green', 'green', 'green', 'lime'],
                end_point=V(0, 0, 0.79), end_color='skin')
    # The hem: green teeth pointing down into a lime zigzag band, 12 teeth round the skirt.
    h1 = tv[0]
    h2, h3 = [], []
    for k in range(2 * segs):
        a = 2 * math.pi * k / (2 * segs)
        r2 = (0.244, 0.198)
        r3 = (0.252, 0.205)
        h2.append(b.vert(V(math.cos(a) * r2[0], math.sin(a) * r2[1], 0.335)))
        z3 = 0.278 if k % 2 else 0.31
        h3.append(b.vert(V(math.cos(a) * r3[0], math.sin(a) * r3[1], z3)))
    for j in range(segs):
        a, c = h1[j], h1[(j + 1) % segs]
        b.face([a, h2[2 * j], h2[2 * j + 1]], 'lime')
        b.face([a, h2[2 * j + 1], c], 'green')
        b.face([c, h2[2 * j + 1], h2[(2 * j + 2) % (2 * segs)]], 'lime')
    n2 = 2 * segs
    for k in range(n2):
        b.face([h2[k], h3[k], h3[(k + 1) % n2], h2[(k + 1) % n2]], 'lime')
    under = b.vert(V(0, 0, 0.33))
    for k in range(n2):
        b.face([h3[(k + 1) % n2], h3[k], under], 'dgreen')

    # Belt buckle: a grey block on the front of the belt (its dark window is a decal below).
    b.box((-0.062, -0.205, 0.38), (0.062, -0.165, 0.474), 'grey')

    # Arms: straight out at the shoulders (T-pose), thick sleeves, lime cuffs, mitten hands palm down.
    az = 0.625
    for s in (1, -1):
        segs_a = 8
        prof = [(0.09, 0.07, 'green'), (0.30, 0.066, 'green'), (0.405, 0.061, 'lime'),
                (0.405, 0.075, 'lime'), (0.458, 0.074, 'lime'), (0.458, 0.05, None)]
        rings = [[V(x * s, math.cos(2 * math.pi * j / segs_a + math.pi / 8) * r,
                    az + math.sin(2 * math.pi * j / segs_a + math.pi / 8) * r) for j in range(segs_a)]
                 for x, r, _ in prof]
        b.loft(rings, [c for _, _, c in prof[:-1]], start_point=V(0.06 * s, 0, az),
               end_point=V(0.47 * s, 0, az), start_color='green', end_color='skin')
        mitt = Matrix.Rotation(math.radians(90 * s), 3, 'Y')
        b.ellipsoid(V(0.512 * s, -0.004, az - 0.004), (0.054, 0.064, 0.074), 8, 4, 'skin', jitter=0.03, matrix=mitt)
        b.ellipsoid(V(0.478 * s, -0.058, az + 0.006), (0.026, 0.03, 0.024), 5, 3, 'skin', jitter=0.03)

    # Head: a wide round ball, no neck; a little round nose; big thick pointy ears out, up and back.
    # The head ball stops at the ring at z 0.94: above it the hair and the hat hide it, a low cone closes it.
    head_rings = []
    for i in range(1, 6):
        th = math.pi * i / 8
        ring = []
        for j in range(12):
            ph = 2 * math.pi * j / 12
            k = 1 + rng.uniform(-0.015, 0.015)
            ring.append(HEAD_C + V(math.sin(th) * math.cos(ph) * HEAD_R[0] * k,
                                   math.sin(th) * math.sin(ph) * HEAD_R[1] * k, -math.cos(th) * HEAD_R[2] * k))
        head_rings.append(ring)
    b.loft(head_rings, 'skin', start_point=HEAD_C - V(0, 0, HEAD_R[2]), end_point=HEAD_C + V(0, 0, 0.11))
    b.ellipsoid(V(0, -0.192, 0.836), (0.038, 0.034, 0.046), 6, 4, 'skin', jitter=0.03,
                matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
    for s in (1, -1):
        path = [V(0.15 * s, 0.02, 0.866), V(0.23 * s, 0.04, 0.884), V(0.31 * s, 0.07, 0.922), V(0.375 * s, 0.10, 0.985)]
        b.tube(path, [0.07, 0.064, 0.042, 0.01], 6, 'skin', side=V(0, 1, 0), flat=0.42, twist=math.pi / 6)

    # Hair: a shell over the head under the hat, a wavy edge: a fringe under the cuff, short locks at the temples,
    # down to the nape at the back.
    nh = 14

    def hairline(phi):
        th = abs(((phi + math.pi / 2) + math.pi) % (2 * math.pi) - math.pi)   # 0 at the front, pi at the back
        keys = [(0.0, 0.898), (0.7, 0.892), (1.25, 0.86), (1.9, 0.80), (math.pi, 0.755)]
        for (t0, z0), (t1, z1) in zip(keys, keys[1:]):
            if th <= t1:
                f = (th - t0) / (t1 - t0)
                return z0 + (z1 - z0) * f
        return keys[-1][1]
    rows = [[], [], [], []]
    for k in range(nh):
        phi = 2 * math.pi * (k + 0.5) / nh
        th = abs(((phi + math.pi / 2) + math.pi) % (2 * math.pi) - math.pi)
        ze = hairline(phi) - ((0.014 if th < 0.8 else 0.028) if k % 2 else 0.0)
        zl = hairline(phi)
        rows[0].append(head_point(phi, ze + 0.02, -0.02))              # tucked inside the head
        rows[1].append(head_point(phi, ze, 0.026))                     # the wavy edge
        rows[2].append(head_point(phi, zl + (1.0 - zl) * 0.3, 0.032))
        rows[3].append(head_point(phi, zl + (1.0 - zl) * 0.65, 0.032))
    b.loft(rows, 'brown', start_point=V(0, 0.0, 0.9), end_point=V(0, 0.01, 1.04))

    # The hat: a thick crooked cuff, a cone that bends over to the elf's left and back, a grey pom-pom.
    tilt = Matrix.Rotation(math.radians(-5), 3, 'Y') @ Matrix.Rotation(math.radians(3), 3, 'X')
    hc = V(0.0, 0.01, 0.975)
    cuff_sec = [(0.0, -0.052), (0.068, -0.044), (0.074, 0.036), (-0.018, 0.05)]
    rings = []
    for dr, dz in cuff_sec:
        rr = []
        for j in range(10):
            a = 2 * math.pi * (j + 0.5) / 10
            k = 1 + rng.uniform(-0.03, 0.03)
            rr.append(hc + tilt @ V(math.cos(a) * (0.188 + dr) * k, math.sin(a) * (0.18 + dr) * k, dz))
        rings.append(rr)
    b.loft(rings, 'green', close=True)
    hat = [V(0.0, 0.01, 0.96), V(0.012, 0.02, 1.11), V(0.05, 0.05, 1.25), V(0.12, 0.10, 1.335), V(0.20, 0.17, 1.35),
           V(0.26, 0.225, 1.29), V(0.285, 0.255, 1.21)]
    b.tube(hat, [0.192, 0.162, 0.11, 0.072, 0.052, 0.036, 0.026], 8, 'green',
           side=V(1, -1, 0).normalized(), jitter=0.04)
    b.ellipsoid(V(0.29, 0.262, 1.148), (0.068, 0.068, 0.066), 8, 4, 'grey', jitter=0.08)

    # Everything below is a decal on the solid body.
    b.freeze()
    fwd = V(0, 1, 0)
    up = V(0, 0, 1)

    def front(x, z):
        return V(x, -0.6, z)

    def aim(target, d):
        """A point in front of `target` on the ray along `d` that hits it."""
        return Vector(target) - Vector(d).normalized() * 0.8
    for s in (1, -1):
        # Narrowed eye whites: a straight lid slanting down to the nose, a round bottom.
        inner, outer = (0.04, 0.843), (0.13, 0.865)
        pts = [front(inner[0] * s, inner[1]), front(outer[0] * s, outer[1])]
        for i in range(1, 7):
            t = i / 7
            x = outer[0] - (outer[0] - inner[0]) * t
            zl = inner[1] + (x - inner[0]) / (outer[0] - inner[0]) * (outer[1] - inner[1])
            pts.append(front(x * s, zl - 0.056 * math.sin(math.pi * t)))
        b.decal(pts, fwd, 'cream', lift=0.007)
        # Big dark pupils close to the nose under the lid: a sly side look.
        b.decal([front(0.07 * s + math.cos(2 * math.pi * j / 8) * 0.023, 0.826 + math.sin(2 * math.pi * j / 8) * 0.023)
                 for j in range(8)], fwd, 'ink', lift=0.012)
        # Thick angry brows, low at the nose, high at the temple.
        b.strip([front(0.026 * s, 0.855), front(0.08 * s, 0.868), front(0.132 * s, 0.876)], [0.011, 0.013, 0.011],
                fwd, up, 'ink', lift=0.01)
        # Rosy cheeks.
        dc = V(-0.75 * s, 1, 0)
        b.decal(plane_outline(aim((0.13 * s, -0.112, 0.79), dc), dc,
                              [(math.cos(2 * math.pi * j / 6) * 0.03, math.sin(2 * math.pi * j / 6) * 0.025)
                               for j in range(6)]), dc, 'blush', lift=0.005)
    # A short mean smirk on the front of the face, rising to the left cheek; one fang under the raised end.
    smirk = [(-0.055, 0.752), (-0.025, 0.744), (0.0, 0.743), (0.03, 0.748), (0.052, 0.76), (0.062, 0.772)]
    b.strip([front(x, z) for x, z in smirk], [0.006, 0.008, 0.008, 0.008, 0.007, 0.006], fwd, up, 'ink',
            lift=0.008)
    b.decal([front(0.022, 0.747), front(0.046, 0.752), front(0.036, 0.728)], fwd, 'cream', lift=0.011)

    # Lime V-neck down the chest.
    b.strip([front(-0.1, 0.704), front(-0.05, 0.656), front(0.0, 0.606), front(0.05, 0.656), front(0.1, 0.704)],
            [0.02, 0.02, 0.024, 0.02, 0.02], fwd, up, 'lime', lift=0.006)
    # Patches: one on the chest at the elf's left, two on the hat (front left, back right).
    for target, d, r, turn in (((0.10, -0.123, 0.53), V(-0.3, 1, 0), 0.048, 0.2),
                               ((0.059, -0.12, 1.135), V(-0.3, 1, 0), 0.05, -0.22),
                               ((-0.038, 0.171, 1.10), V(0.3, -1, 0), 0.046, 0.15)):
        b.decal(plane_outline(aim(target, d), d, square_patch(r, turn=turn)), d, 'dgreen', lift=0.006)
    # The buckle's dark window.
    b.decal([front(x, z) for x, z in ((-0.03, 0.41), (0.03, 0.41), (0.03, 0.444), (-0.03, 0.444))], fwd, 'brown',
            lift=0.004, depth=0.012)

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
    p.add_argument('--skin', choices=sorted(SKINS), default='peach')
    a = p.parse_args(argv)
    COLORS['skin'], COLORS['blush'] = SKINS[a.skin]
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
    print('ELF tris=%d size=%s min=%s' % (tris, ['%.3f' % (h - l) for l, h in zip(lo, hi)], ['%.3f' % v for v in lo]))


if __name__ == '__main__':
    main(sys.argv)
