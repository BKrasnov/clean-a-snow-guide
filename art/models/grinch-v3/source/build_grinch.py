"""Grinch, version 3 (card e49171): bright, smooth and very cartoon, a soft toy in the manner of Meshy AI models.

    blender -b --factory-startup --python build_grinch.py -- --out <abs Grinch_master.blend> --texture <abs Grinch_Palette.png>

Concept: art/refs/grinch/grinch-v2.png (front, side, back, T-pose). Metres, Z up, the model faces -Y, feet on z = 0.
About twice a default Roblox avatar (1.45 m) with the hat on.
Owner's decision of 14.11.2026: this model leaves the "facets are seen" rule of the style. Every face is smooth and
only the edges sharper than SHARP_ANGLE (fur rims, the sole) are marked sharp, so the smoothness is in the normals of
the mesh itself and comes to Roblox with it.
Fur is big soft locks: a tier of a shell overhangs the tier below and its lower edge runs in a wave of round locks
with lighter tips.
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
    'green': '4FD61E',   # Мех Гринча: skin and fur
    'light': 'B6F23E',   # Светлый мех Гринча: tips of the locks
    'red': 'F5281C',     # Красный колпак: hat, sack, tongue
    'cream': 'FFFDF5',   # Крем: hat trim, pom-pom, eyes, fangs, stars
    'dark': '3C8E63',    # Тень хвои: boots
    'pine': '54A577',    # Хвоя: boot cuffs
    'brown': '80401B',   # Тёмное дерево: rope belt
    'ink': '2B1A11',     # Контур: brows, pupils, mouth
}
ORDER = list(COLORS)
GRID = 4
CELL = 16
SIZE = GRID * CELL
TAU = 2 * math.pi
SHARP_ANGLE = math.radians(120)

rng = random.Random(2714)
WORLD = (Vector((0, 0, 0)), Matrix.Identity(3))
UP = Vector((0, 0, 1))


def cell_uv(color):
    i = ORDER.index(color)
    col, row = i % GRID, i // GRID
    return ((col + 0.5) / GRID, (row + 0.5) / GRID)


def lerp_table(table, z):
    """Linear interpolation of the rows (z, a, b, ...) at z; the ends are held."""
    if z <= table[0][0]:
        return table[0][1:]
    for lo, hi in zip(table, table[1:]):
        if z <= hi[0]:
            t = (z - lo[0]) / (hi[0] - lo[0])
            t = t * t * (3 - 2 * t) * 0.5 + t * 0.5
            return tuple(a + (b - a) * t for a, b in zip(lo[1:], hi[1:]))
    return table[-1][1:]


def spline(points, radii, sub):
    """Catmull-Rom through the points, `sub` pieces per span; the radii go along."""
    pts = [Vector(p) for p in points]
    out_p, out_r = [], []
    n = len(pts)
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        for k in range(sub):
            t = k / sub
            t2, t3 = t * t, t * t * t
            out_p.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            out_r.append(radii[i] + (radii[i + 1] - radii[i]) * t)
    out_p.append(pts[-1])
    out_r.append(radii[-1])
    return out_p, out_r


class Ring:
    """`color` paints the band between the previous ring and this one; `faces` gives the faces of that band
    their own colours."""
    def __init__(self, pts, color, faces=None):
        self.pts, self.color, self.faces = pts, color, faces


def ring(z, rx, ry, segs, color, ox=0.0, oy=0.0, frame=WORLD, mod=None):
    """An ellipse in the frame's XY plane at height z."""
    pts = []
    for j in range(segs):
        a = TAU * j / segs
        p = Vector((ox + math.cos(a) * rx, oy + math.sin(a) * ry, z))
        if mod:
            p = mod(a, p)
        pts.append(frame[0] + frame[1] @ p)
    return Ring(pts, color)


PER = 8   # vertices on one lock of a fur edge


def tier(z, rx, ry, segs, oy, lengths, flare, grow, shift=0, mod=None):
    """The wavy lower edge of a fur tier, a continuation of its shell, with twice the vertices of the shell rings.
    Every lock takes PER vertices: one is the narrow notch at the height z, the other seven lie on a round arc
    that hangs down by the lock's length and bends out by `flare`. The locks are long and short by turns
    (`lengths`). Returns the rim ring and the ring above it; the band between them is the light lower third
    of each lock, a separate crescent thick in the middle: it thins out to the notches, which stay green.
    `grow` = (drx, dry, doy) is how the shell widens from the rim to the upper ring."""
    fine = segs * 2
    rim, upper, faces = [], [], []
    for j in range(fine):
        k = (j + shift) % fine
        t, lock = k % PER, k // PER
        a = TAU * j / fine
        if t == 0:
            dz, out, band = 0.0, 0.0, 0.012
        else:
            x = (t - PER / 2) / (PER / 2 - 0.5)
            arc = math.sqrt(1 - x * x)
            length = lengths[lock % len(lengths)]
            dz = -length * rng.uniform(0.94, 1.0) * arc
            out, band = flare * arc, 0.012 + max(0.05, length * 0.4) * arc ** 3
        faces.append('light' if 1 <= t <= PER - 2 else 'green')
        for pts, z1, r1, r2, o in ((rim, z + dz, rx + out, ry + out, oy),
                                   (upper, z + dz + band, rx + out * 0.6 + grow[0], ry + out * 0.6 + grow[1],
                                    oy + grow[2])):
            q = Vector((math.cos(a) * r1, o + math.sin(a) * r2, z1))
            pts.append(mod(a, q) if mod else q)
    return Ring(rim, 'green'), Ring(upper, 'light', faces)


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
        """A closed shell through the rings with a fan at both ends. A ring may have twice the vertices of its
        neighbour (a fur edge): that band is made of triangles."""
        vs = [[self.vert(p) for p in r.pts] for r in rings]
        for i in range(1, len(rings)):
            a, b, r = vs[i - 1], vs[i], rings[i]
            na, nb = len(a), len(b)
            if na == nb:
                for j in range(na):
                    k = (j + 1) % na
                    self.face([a[j], a[k], b[k], b[j]], r.faces[j] if r.faces else r.color)
            elif nb == 2 * na:
                for j in range(na):
                    k = (j + 1) % na
                    self.face([a[j], b[2 * j + 1], b[2 * j]], r.color)
                    self.face([a[j], a[k], b[2 * j + 1]], r.color)
                    self.face([a[k], b[(2 * j + 2) % nb], b[2 * j + 1]], r.color)
            else:
                for j in range(nb):
                    k = (j + 1) % nb
                    self.face([a[2 * j], a[2 * j + 1], b[j]], r.color)
                    self.face([a[2 * j + 1], b[k], b[j]], r.color)
                    self.face([a[2 * j + 1], a[(2 * j + 2) % na], b[k]], r.color)
        n = len(vs[0])
        c = self.vert(start)
        for j in range(n):
            self.face([vs[0][(j + 1) % n], vs[0][j], c], rings[1].color)
        n = len(vs[-1])
        c = self.vert(end)
        for j in range(n):
            self.face([vs[-1][j], vs[-1][(j + 1) % n], c], end_color or rings[-1].color)

    def ellipsoid(self, center, radii, segs, rings, color, matrix=None, flat_bottom=None, mod=None):
        """A UV sphere scaled to the radii; `mod` reshapes a unit-sphere point before the scale."""
        rx, ry, rz = radii
        m = matrix or Matrix.Identity(3)
        c = Vector(center)

        def at(u):
            if mod:
                u = mod(u)
            p = c + m @ Vector((u.x * rx, u.y * ry, u.z * rz))
            if flat_bottom is not None:
                p.z = max(p.z, flat_bottom)
            return p
        rr = []
        for i in range(1, rings):
            th = math.pi * i / rings
            rr.append(Ring([at(Vector((math.sin(th) * math.cos(TAU * j / segs), math.sin(th) * math.sin(TAU * j / segs),
                                       -math.cos(th)))) for j in range(segs)], color))
        self.shell(rr, at(Vector((0, 0, -1))), at(Vector((0, 0, 1))))

    def tube(self, path, radii, segs, color, side=UP, flat=1.0, thin=1.0, top=1.0, colors=None, round_ends=True, round_start=True):
        """Circles along a polyline. `side` fixes the ring orientation; `flat` scales the ring along `side`, `thin`
        across it, `top` scales the half of the ring on the `side` side. With round_ends the ends are domes."""
        path = [Vector(p) for p in path]
        rr = []
        last = len(path) - 1

        def circle(p, d, r, color):
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            pts = []
            for j in range(segs):
                a = TAU * j / segs
                cu = math.cos(a) * flat
                if cu > 0:
                    cu *= top
                pts.append(p + (u * cu + v * math.sin(a) * thin) * r)
            return Ring(pts, color)
        d0 = (path[1] - path[0]).normalized()
        d1 = (path[-1] - path[-2]).normalized()
        col = colors or [color] * len(path)
        if round_ends and round_start:
            rr.append(circle(path[0] - d0 * radii[0] * 0.45, d0, radii[0] * 0.72, col[0]))
        for i, (p, r) in enumerate(zip(path, radii)):
            d = (path[min(i + 1, last)] - path[max(i - 1, 0)]).normalized()
            rr.append(circle(p, d, r, col[i]))
        if round_ends:
            rr.append(circle(path[-1] + d1 * radii[-1] * 0.45, d1, radii[-1] * 0.72, col[-1]))
        k = 0.75 if round_ends else 0.4
        self.shell(rr, path[0] - d0 * radii[0] * k, path[-1] + d1 * radii[-1] * k)

    def loop_tube(self, points, radius, segs, color, side=UP):
        """A closed ring tube through `points` (the belt, the fur trim of the hat, the boot cuffs)."""
        n = len(points)
        rings = []
        for i in range(n):
            p = Vector(points[i])
            d = (Vector(points[(i + 1) % n]) - Vector(points[i - 1])).normalized()
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            r = radius(i) if callable(radius) else radius
            rings.append([self.vert(p + (u * math.cos(TAU * j / segs) + v * math.sin(TAU * j / segs)) * r)
                          for j in range(segs)])
        for i in range(n):
            a, b = rings[i], rings[(i + 1) % n]
            for j in range(segs):
                self.face([a[j], a[(j + 1) % segs], b[(j + 1) % segs], b[j]], color)

    def gem(self, outline, apex, back, color):
        """A raised flat shape on a surface: fans from the outline to the apex in front and to `back` inside."""
        vs = [self.vert(p) for p in outline]
        ca, cb = self.vert(apex), self.vert(back)
        n = len(vs)
        for j in range(n):
            self.face([vs[j], vs[(j + 1) % n], ca], color)
            self.face([vs[(j + 1) % n], vs[j], cb], color)


# The surfaces the small parts sit on, before LIFT: rows (z, rx, ry, oy) of the body and (z, rx, ry) of the head.
BODY = [(1.38, 0.575, 0.59, -0.155), (1.48, 0.56, 0.575, -0.145), (1.57, 0.50, 0.51, -0.12),
        (1.64, 0.485, 0.485, -0.105), (1.74, 0.50, 0.47, -0.09), (1.83, 0.45, 0.41, -0.07),
        (1.91, 0.34, 0.30, -0.05), (1.97, 0.20, 0.18, -0.03)]
HEAD_Y = -0.03
HEAD = [(1.93, 0.545, 0.475), (1.99, 0.557, 0.487), (2.10, 0.575, 0.505), (2.18, 0.59, 0.525),
        (2.29, 0.59, 0.525), (2.40, 0.57, 0.52), (2.50, 0.52, 0.49), (2.60, 0.445, 0.425)]
LIFT = 0.20      # everything above the legs is modelled 0.2 m lower and lifted: long bare legs
HEIGHT = 3.10    # the finished model is scaled to this height with the hat on
DOWN = Vector((0, 0, -1))
# Joints the rig bends (rig_grinch.py), before the final scale: the knee height and the elbow's distance from the
# body axis along the arm. The approved look had one ring at each; the rig needs two around it.
KNEE_Z = 0.88
ELBOW_X = 0.78


def surface(table, a, z):
    """The point of a ring surface at the angle a and the height z, the tangent down along it and the normal."""
    def at(zz):
        row = lerp_table(table, zz)
        oy = row[2] if len(row) > 2 else HEAD_Y
        return Vector((row[0] * math.cos(a), oy + row[1] * math.sin(a), zz)), row
    p, row = at(z)
    t = (at(z - 0.04)[0] - p).normalized()
    n = Vector((math.cos(a) / row[0], math.sin(a) / row[1], 0)).normalized()
    return p, t, n


def on_head(x, z, lift=0.0):
    """The point on the front of the head at (x, z), pushed `lift` along -Y."""
    rx, ry = lerp_table(HEAD, z)
    u = min(0.98, abs(x) / rx)
    return Vector((x, HEAD_Y - ry * math.sqrt(1 - u * u) - lift, z))


def on_belly(x, z, lift=0.0):
    rx, ry, oy = lerp_table(BODY, z)
    u = min(0.98, abs(x) / rx)
    return Vector((x, oy - ry * math.sqrt(1 - u * u) - lift, z))


def build(texture_path):
    b = Builder()

    def lock(p, t, n, length, w, curl=0.05, thick=0.38, hang=0.0):
        """A soft lock of fur: a plump drop lying on a surface from p along t, narrow at the root, widest at
        the middle, with a round end lifted off the surface by `curl`. The end is lighter.
        `hang` turns it from the surface tangent to straight down."""
        t = t.lerp(DOWN, hang).normalized()
        n = (n - t * n.dot(t)).normalized()
        across = n.cross(t).normalized()
        rr = []
        for along, off, k, color in ((0.0, -0.03, 0.6, 'green'), (0.42, curl * 0.6, 1.0, 'green'),
                                     (0.74, curl, 0.88, 'green'), (0.94, curl, 0.5, 'light')):
            c = p + t * (length * along) + n * off
            rr.append(Ring([c + (across * math.cos(TAU * j / 6) + n * math.sin(TAU * j / 6) * thick) * (w * k)
                            for j in range(6)], color))
        b.shell(rr, p - n * 0.03 - t * 0.01, p + t * length + n * (curl * 0.8), end_color='light')

    def locks(table, z, angles, length, w, **kw):
        for i, a in enumerate(angles):
            p, t, n = surface(table, a, z)
            lock(p, t, n, length * (1.0, 0.8, 0.92)[i % 3], w, **kw)

    # ---- Boots: plump, a round toe bigger than the heel, a flat sole, a fat soft cuff.
    for s in (1, -1):
        x = 0.20 * s

        def toe(u):
            k = 1 + 0.16 * -u.y
            return Vector((u.x * k, u.y, u.z * k if u.z > 0 else u.z))
        b.ellipsoid((0.235 * s, -0.13, 0.19), (0.25, 0.38, 0.22), 16, 6, 'dark', flat_bottom=0.0, mod=toe)
        b.loop_tube([(x + math.cos(TAU * j / 8) * 0.135, -0.01 + math.sin(TAU * j / 8) * 0.14, 0.41)
                     for j in range(8)], 0.082, 5, 'pine')

    # ---- Legs: long and thin. Two rings 0.07 m below and above the knee (KNEE_Z) let it bend; they lie on the
    # straight taper the single knee ring of the approved look gave.
    for s in (1, -1):
        x = 0.20 * s
        b.shell([ring(0.40, 0.10, 0.10, 8, 'green', ox=x),
                 ring(KNEE_Z - 0.07, 0.0983, 0.0983, 8, 'green', ox=x * 0.9829),
                 ring(KNEE_Z + 0.07, 0.1002, 0.1002, 8, 'green', ox=x * 0.9761),
                 ring(1.22 + LIFT, 0.115, 0.115, 8, 'green', ox=x * 0.95)],
                Vector((x, 0, 0.36)), Vector((x * 0.95, 0, 1.26 + LIFT)))
    b.bm.verts.ensure_lookup_table()
    lifted_from = len(b.bm.verts)

    # ---- Body: one smooth pear. The belly is a ball pushed forward, the belt lies in the waist. Fur: the shell
    # ends below in a hem of round locks, and a tier of locks hangs from the chest down to the belt.
    n = 24
    hem, hem_up = tier(1.25, 0.50, 0.51, n, -0.125, (0.09, 0.19), 0.05, (0.03, 0.032, -0.012))
    fluff_rim, fluff_up = tier(1.735, 0.495, 0.47, n, -0.098, (0.07, 0.115), 0.05, (0.0, -0.005, 0.005), shift=4)
    b.shell([ring(1.28, 0.30, 0.30, n, 'green', oy=-0.08), hem, hem_up]
            + [ring(z, rx, ry, n, 'green', oy=oy) for z, rx, ry, oy in BODY[:3]]
            + [ring(1.675, 0.47, 0.455, n, 'green', oy=-0.10), fluff_rim, fluff_up]
            + [ring(z, rx, ry, n, 'green', oy=oy) for z, rx, ry, oy in BODY[5:7]],   # BODY[7] lies inside the head
            Vector((0, -0.07, 1.25)), Vector((0, -0.03, 2.0)))

    # ---- Arms: T-pose, long and thin. A fat mitt: a round palm, three sausage
    # fingers and a thumb.
    AZ = 1.80
    for s in (1, -1):
        fr = (Vector((0, 0, AZ)), Matrix(((0, 0, s), (0, -s, 0), (1, 0, 0))))   # local z runs along the arm
        b.shell([
            ring(0.26, 0.13, 0.13, 8, 'green', frame=fr),
            ring(0.50, 0.118, 0.118, 8, 'green', frame=fr),
            ring(ELBOW_X - 0.07, 0.1045, 0.1045, 8, 'green', frame=fr),   # two rings around the elbow for the rig
            ring(ELBOW_X + 0.07, 0.0974, 0.0974, 8, 'green', frame=fr),
            ring(1.10, 0.088, 0.088, 8, 'green', frame=fr),
        ], Vector((0.22 * s, 0, AZ)), Vector((1.16 * s, 0, AZ)))
        b.ellipsoid((1.30 * s, 0.0, AZ), (0.235, 0.215, 0.20), 14, 6, 'green')
        for dy, tip in ((-0.145, 1.585), (0.0, 1.63), (0.145, 1.585)):
            b.tube([(1.40 * s, dy, AZ - 0.02), (tip * s, dy * 1.08, AZ - 0.035)], [0.09, 0.08], 8, 'green',
                   round_start=False)
        b.tube([(1.24 * s, -0.14, AZ - 0.03), (1.31 * s, -0.285, AZ - 0.04)], [0.09, 0.078], 8, 'green',
               round_start=False)

    # ---- Head: big and wide, widest at the cheeks. The shell ends below in a wavy beard collar over the chest
    # and the shoulders; a wavy fringe looks out from under the hat. A soft lock lies on each cheek.
    def bangs(a, p):
        # The fringe is shorter over the brows and hangs lower on the back of the head.
        p.z += 0.03 * max(0.0, math.cos(a - 1.5 * math.pi)) ** 2 - 0.05 * max(0.0, math.cos(a - 0.5 * math.pi)) ** 2
        return p
    beard, beard_up = tier(1.965, 0.54, 0.47, n, HEAD_Y, (0.09, 0.19), 0.05, (0.015, 0.015, 0))
    fringe, fringe_up = tier(2.60, 0.50, 0.475, n, HEAD_Y, (0.05, 0.08), 0.02, (-0.045, -0.045, 0), shift=4,
                             mod=bangs)
    b.shell([ring(2.0, 0.28, 0.26, n, 'green', oy=HEAD_Y), beard, beard_up]
            + [ring(z, rx, ry, n, 'green', oy=HEAD_Y) for z, rx, ry in HEAD[2:7]]
            + [ring(2.585, 0.445, 0.42, n, 'green', oy=HEAD_Y, mod=bangs), fringe, fringe_up,
               ring(2.72, 0.36, 0.34, n, 'green', oy=HEAD_Y)],
            Vector((0, HEAD_Y, 1.97)), Vector((0, HEAD_Y, 2.77)))
    front = -math.pi / 2
    locks(HEAD, 2.22, [front + sg * 1.62 for sg in (1, -1)], 0.17, 0.11, curl=0.02, thick=0.3, hang=0.2)

    for s in (1, -1):
        # Big pointy ears with a soft tip, out to the sides and a little up and back.
        base = Vector((0.48 * s, HEAD_Y + 0.05, 2.40))
        b.tube([base, base + Vector((0.16 * s, 0.02, 0.05)), base + Vector((0.31 * s, 0.05, 0.14))],
               [0.18, 0.14, 0.055], 6, 'green', side=Vector((0, 1, 0)), flat=0.45, round_start=False)

    # Eyes: big whites, flattened half-balls; big dark pupils looking a little inward with a white glint; thick
    # angry brows sloping down to the nose over the upper inner corner of each white, lying on the head.
    for s in (1, -1):
        # The poles of these balls look along Y, so their outline from the front is a ring of 12 vertices.
        fwd = Matrix.Rotation(math.radians(90), 3, 'X')
        tilt = Matrix.Rotation(math.radians(-10 * s), 3, 'Y') @ fwd
        b.ellipsoid(on_head(0.205 * s, 2.355, -0.04), (0.15, 0.158, 0.085), 14, 5, 'cream', matrix=tilt)
        b.ellipsoid(on_head(0.17 * s, 2.34, 0.033), (0.072, 0.082, 0.02), 12, 3, 'ink', matrix=fwd)
        b.ellipsoid(on_head(0.195 * s, 2.372, 0.05), (0.025, 0.027, 0.01), 8, 3, 'cream', matrix=fwd)
        b.tube([on_head(0.045 * s, 2.44, 0.004), on_head(0.20 * s, 2.52, 0.004), on_head(0.365 * s, 2.555, 0.0)],
               [0.045, 0.055, 0.032], 6, 'ink', thin=0.25)

    # Mouth: a wide open grin, a dark crescent with the horns up lying on the curve of the head; two fangs hang
    # from its upper edge inside it, the tongue lies in its lower third.
    half, tall, horn, mz = 0.25, 0.17, 0.05, 2.195

    def lips(x):
        u = (x / half) ** 2
        return mz + horn * u, mz + horn * u - tall * (1 - u)   # the upper and the lower edge at x
    cols = []
    for i in range(9):
        x = half * 0.97 * (i / 4 - 1)
        top, low = lips(x)
        mid = (top + low) / 2
        cols.append(Ring([on_head(x, top, 0.008), on_head(x, mid, 0.008), on_head(x, low, 0.008),
                          on_head(x, low, -0.03), on_head(x, top, -0.03)], 'ink'))
    b.shell(cols, on_head(-half, mz + horn, 0.0), on_head(half, mz + horn, 0.0))
    for s in (1, -1):
        x = 0.125 * s
        z = lips(x)[0] + 0.005
        b.tube([on_head(x, z, 0.012), on_head(x, z - 0.05, 0.014), on_head(x, z - 0.095, 0.012)],
               [0.034, 0.027, 0.009], 6, 'cream', side=Vector((1, 0, 0)), thin=0.5, round_start=False)
    b.ellipsoid(on_head(0.0, mz - tall + 0.04, 0.008), (0.09, 0.016, 0.035), 8, 3, 'red')

    # ---- The stolen Santa hat: a fat round fur roll, a tall red cone bent over to the left shoulder and hanging
    # down behind the ear, a big round pom-pom on its end.
    hz = 2.665
    b.loop_tube([(math.cos(TAU * j / 16) * 0.485, HEAD_Y + math.sin(TAU * j / 16) * 0.465, hz) for j in range(16)],
                lambda i: 0.112 * (1 + 0.05 * math.sin(i * TAU * 4 / 16 + 0.6)), 8, 'cream')
    pts, rad = spline([(0.0, HEAD_Y, hz - 0.02), (0.02, -0.005, 2.92), (0.17, 0.06, 3.07),
                       (0.37, 0.11, 3.09), (0.59, 0.16, 3.01), (0.80, 0.19, 2.87), (0.93, 0.21, 2.69)],
                      [0.45, 0.335, 0.215, 0.16, 0.125, 0.10, 0.085], 1)
    b.tube(pts, rad, 10, 'red', side=Vector((0, 1, 0)), round_ends=False)

    def fluff(u):
        return u * (1 + 0.04 * math.sin(5 * math.atan2(u.y, u.x)) * (1 - u.z * u.z))
    b.ellipsoid((0.97, 0.21, 2.50), (0.19, 0.19, 0.19), 14, 7, 'cream', mod=fluff)

    # ---- Rope belt in the waist, a knot in front and two ends lying on the belly.
    bz = 1.585
    brx, bry, boy = lerp_table(BODY, bz)
    b.loop_tube([(math.cos(TAU * j / 14) * (brx + 0.02), boy + math.sin(TAU * j / 14) * (bry + 0.02), bz)
                 for j in range(14)], 0.034, 5, 'brown')
    knot = on_belly(0.13, bz, 0.035)
    b.ellipsoid(knot, (0.085, 0.05, 0.07), 8, 4, 'brown')
    for dx, end in ((-0.04, 1.34), (0.055, 1.375)):
        x = knot.x + dx
        b.tube([on_belly(x, bz - 0.03, 0.012), on_belly(x + dx * 0.4, 1.51, 0.01),
                on_belly(x + dx * 0.7, 1.45, 0.01), on_belly(x + dx, end + 0.045, 0.008)],
               [0.028, 0.026, 0.026, 0.029], 5, 'brown', side=Vector((1, 0, 0)))

    # ---- The stolen sack on the left hip: a plump red bag wider at the bottom, tied at the neck, a frill above
    # the tie, two cream stars lying on it.
    sc = Vector((0.74, -0.16, 1.23))
    sr = (0.29, 0.265, 0.33)

    def pear(u):
        k = 1 - 0.16 * u.z
        return Vector((u.x * k, u.y * k, u.z))
    b.ellipsoid(sc, sr, 14, 7, 'red', mod=pear)
    neck = sc + Vector((-0.09, 0.03, 0.33))
    b.tube([neck + Vector((0.02, 0, -0.07)), neck + Vector((-0.01, 0, 0.03))], [0.10, 0.085], 8, 'brown',
           round_ends=False)
    b.tube([neck + Vector((-0.01, 0, 0.02)), neck + Vector((-0.03, 0, 0.09)), neck + Vector((-0.045, 0, 0.15))],
           [0.075, 0.115, 0.135], 8, 'red', round_ends=False)
    for dx, dz, r in ((0.02, 0.06, 0.072), (-0.06, -0.11, 0.05)):
        def on_sack(x, z, lift):
            w = (z - sc.z) / sr[2]
            k = 1 - 0.16 * w
            u = (x - sc.x) / (sr[0] * k)
            return Vector((x, sc.y - sr[1] * k * math.sqrt(max(0.0, 1 - u * u - w * w)) - lift, z))
        cx, cz = sc.x + dx, sc.z + dz
        pts = []
        for j in range(10):
            a = TAU * j / 10 + math.pi / 2
            rr = r if j % 2 == 0 else r * 0.55
            pts.append(on_sack(cx + math.cos(a) * rr, cz + math.sin(a) * rr, 0.003))
        b.gem(list(reversed(pts)), on_sack(cx, cz, 0.009), on_sack(cx, cz, -0.03), 'cream')

    # Long legs: lift everything above them; then bring the model to its height.
    b.bm.verts.ensure_lookup_table()
    for v in b.bm.verts[lifted_from:]:
        v.co.z += LIFT
    k = HEIGHT / max(v.co.z for v in b.bm.verts)
    for v in b.bm.verts:
        v.co *= k

    # One mesh. Every face is smooth; an edge is sharp only where two faces meet sharper than SHARP_ANGLE.
    mesh = bpy.data.meshes.new(MODEL + '_Body')
    bmesh.ops.recalc_face_normals(b.bm, faces=b.bm.faces[:])
    b.bm.normal_update()
    sharp = 0
    for f in b.bm.faces:
        f.smooth = True
    for e in b.bm.edges:
        e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0.0) > SHARP_ANGLE)
        sharp += not e.smooth
    b.bm.to_mesh(mesh)
    b.bm.free()
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
    bsdf.inputs['Roughness'].default_value = 0.7
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Closest'
    mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    mesh.materials.append(mat)
    return ob, img, sharp


def main(argv):
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--texture', required=True)
    a = p.parse_args(argv)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    ob, img, sharp = build(a.texture)
    bpy.ops.wm.save_as_mainfile(filepath=a.out)
    img.filepath = bpy.path.relpath(a.texture)
    bpy.ops.wm.save_mainfile()
    me = ob.data
    tris = sum(len(pg.vertices) - 2 for pg in me.polygons)
    lo = [min(v.co[i] for v in me.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in me.vertices) for i in range(3)]
    smooth = sum(1 for pg in me.polygons if pg.use_smooth)
    # The smoothness is in the mesh: corners of one vertex share a normal unless a sharp edge parts them.
    split = set()
    for loop, nor in zip(me.loops, me.corner_normals):
        split.add((loop.vertex_index, tuple(round(c, 3) for c in nor.vector)))
    print('GRINCH tris=%d verts=%d size=%s' % (tris, len(me.vertices), ['%.3f' % (h - l) for l, h in zip(lo, hi)]))
    print('GRINCH normals: smooth faces %d of %d, sharp edges %d of %d, normals domain %s, split normals %d on %d verts'
          % (smooth, len(me.polygons), sharp, len(me.edges), me.normals_domain, len(split), len(me.vertices)))


if __name__ == '__main__':
    main(sys.argv)
