"""Grinch (card e49171): the tall green goblin boss in a stolen Santa hat, built from faceted low-poly shapes.

    blender -b --factory-startup --python build_grinch.py -- --out <abs Grinch_master.blend> --texture <abs Grinch_Palette.png>

Concept: art/refs/grinch/grinch-v2.png (front, side, back, T-pose). Metres, Z up, the model faces -Y, feet on z = 0.
Twice a default Roblox avatar (about 1.45 m): the top of the head 2.62 m, the hat 3.0 m.
One mesh Grinch_Body, one material M_Grinch_Palette over a 64 x 64 palette texture: every face points at the middle of
its colour's 16 x 16 cell, so the colours stay flat at every mip level. Flat shading: the facets show, as in the style guide.
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
    'light': '96DC6A',   # Трава: light fur tufts
    'dark': '3C8E63',    # Тень хвои: boots
    'red': 'D6392B',     # Красный амбар: hat and sack
    'cream': 'FFFDF5',   # Крем: hat trim, pom-pom, eyes, fangs, stars
    'brown': '80401B',   # Тёмное дерево: rope belt, tongue
    'ink': '2B1A11',     # Контур: brows, pupils, mouth
}
ORDER = list(COLORS)
GRID = 4
CELL = 16
SIZE = GRID * CELL

rng = random.Random(1713)


def cell_uv(color):
    i = ORDER.index(color)
    col, row = i % GRID, i // GRID
    return ((col + 0.5) / GRID, (row + 0.5) / GRID)


class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new('UVMap')
        self.colour_of = {}

    def face(self, verts, color):
        f = self.bm.faces.new(verts)
        u = cell_uv(color)
        for loop in f.loops:
            loop[self.uv].uv = u
        return f

    def vert(self, co):
        return self.bm.verts.new(co)

    # Rings of points lofted into a closed tube: rings[i] is a list of the same length.
    def loft(self, rings, color, cap_start=True, cap_end=True, start_point=None, end_point=None):
        vs = [[self.vert(p) for p in ring] for ring in rings]
        n = len(rings[0])
        for a, b in zip(vs, vs[1:]):
            for j in range(n):
                self.face([a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]], color)
        if cap_start:
            if start_point is not None:
                c = self.vert(start_point)
                for j in range(n):
                    self.face([vs[0][(j + 1) % n], vs[0][j], c], color)
            else:
                self.face(list(reversed(vs[0])), color)
        if cap_end:
            if end_point is not None:
                c = self.vert(end_point)
                for j in range(n):
                    self.face([vs[-1][j], vs[-1][(j + 1) % n], c], color)
            else:
                self.face(vs[-1], color)
        return vs

    def ellipsoid(self, center, radii, segs, rings, color, jitter=0.0, matrix=None, flat_bottom=None):
        """A low UV sphere; jitter moves inner vertices along the normal for a hand-cut look."""
        cx, cy, cz = center
        rx, ry, rz = radii
        m = matrix or Matrix.Identity(3)
        ring_pts = []
        for i in range(1, rings):
            th = math.pi * i / rings
            ring = []
            for j in range(segs):
                ph = 2 * math.pi * j / segs
                k = 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
                local = Vector((math.sin(th) * math.cos(ph) * rx * k, math.sin(th) * math.sin(ph) * ry * k,
                                -math.cos(th) * rz * k))
                p = m @ local + Vector(center)
                if flat_bottom is not None:
                    p.z = max(p.z, flat_bottom)
                ring.append(p)
            ring_pts.append(ring)
        bottom = m @ Vector((0, 0, -rz)) + Vector(center)
        if flat_bottom is not None:
            bottom.z = max(bottom.z, flat_bottom)
        top = m @ Vector((0, 0, rz)) + Vector(center)
        return self.loft(ring_pts, color, start_point=bottom, end_point=top)

    def tube(self, path, radii, segs, color, side=Vector((0, 0, 1)), flat=1.0, jitter=0.0, caps=True):
        """Circles along a polyline; `side` fixes the ring orientation, `flat` squashes the ring along it."""
        rings = []
        for i, (p, r) in enumerate(zip(path, radii)):
            p = Vector(p)
            d = (Vector(path[min(i + 1, len(path) - 1)]) - Vector(path[max(i - 1, 0)])).normalized()
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            ring = []
            for j in range(segs):
                a = 2 * math.pi * j / segs
                k = 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
                ring.append(p + (u * math.cos(a) * flat + v * math.sin(a)) * r * k)
            rings.append(ring)
        start = Vector(path[0]) - (Vector(path[1]) - Vector(path[0])).normalized() * radii[0] * 0.5 if caps else None
        end = Vector(path[-1]) + (Vector(path[-1]) - Vector(path[-2])).normalized() * radii[-1] * 0.5 if caps else None
        return self.loft(rings, color, cap_start=caps, cap_end=caps, start_point=start, end_point=end)

    def spike(self, base_a, base_b, inner, tip, color):
        a, b, c, t = (self.vert(p) for p in (base_a, base_b, inner, tip))
        self.face([a, b, t], color)
        self.face([b, c, t], color)
        self.face([c, a, t], color)
        self.face([a, c, b], color)

    def flat_poly(self, points, normal_push, color):
        """A thin plate: the outline on a surface and a copy pushed along `normal_push` (a star, a brow, the mouth);
        both sides are fans round their middle, so there are no n-gons."""
        back = [self.vert(p) for p in points]
        front = [self.vert(Vector(p) + normal_push) for p in points]
        n = len(points)
        mid = sum((Vector(p) for p in points), Vector()) / n
        cf, cb = self.vert(mid + normal_push), self.vert(mid)
        for j in range(n):
            self.face([front[j], front[(j + 1) % n], cf], color)
            self.face([back[(j + 1) % n], back[j], cb], color)
            self.face([back[j], back[(j + 1) % n], front[(j + 1) % n], front[j]], color)

    def loop_tube(self, points, radius, segs, color, side=Vector((0, 0, 1)), jitter=0.0):
        """A closed ring tube through `points` (a belt, a fur trim): no caps, the last ring joins the first."""
        n = len(points)
        rings = []
        for i in range(n):
            p = Vector(points[i])
            d = (Vector(points[(i + 1) % n]) - Vector(points[i - 1])).normalized()
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            r = radius(i) if callable(radius) else radius
            ring = []
            for j in range(segs):
                a = 2 * math.pi * j / segs
                k = 1 + (rng.uniform(-jitter, jitter) if jitter else 0)
                ring.append(self.vert(p + (u * math.cos(a) + v * math.sin(a)) * r * k))
            rings.append(ring)
        for i in range(n):
            a, b = rings[i], rings[(i + 1) % n]
            for j in range(segs):
                self.face([a[j], a[(j + 1) % segs], b[(j + 1) % segs], b[j]], color)


def fur_ring(b, center, rx, ry, z, count, length, out, color, droop=1.0, phase=0.0, arc=None, inset=0.05, rise=0.02):
    """Zigzag of fur points around an ellipse at height z: each point leans out and down, the base sits on the surface."""
    cx, cy = center
    a0, a1 = arc if arc else (0.0, 2 * math.pi)
    full = arc is None
    steps = count if full else count
    for i in range(steps):
        ta = a0 + (a1 - a0) * (i + phase) / count
        tb = a0 + (a1 - a0) * (i + 1 + phase) / count
        tm = (ta + tb) / 2
        k = 1 + rng.uniform(-0.15, 0.15)

        def at(t, s=1.0, dz=0.0):
            return Vector((cx + math.cos(t) * rx * s, cy + math.sin(t) * ry * s, z + dz))
        pa, pb = at(ta), at(tb)
        inner = at(tm, 1 - inset / max(rx, ry), rise)
        tip = at(tm, 1 + out * k / max(rx, ry), -length * k * droop)
        b.spike(pa, pb, inner, tip, color)


def build(texture_path):
    b = Builder()

    # Boots: big rounded dark-green clogs, toes forward, flat soles; a cuff where the thin leg goes in.
    for s in (1, -1):
        b.ellipsoid((0.25 * s, -0.10, 0.10), (0.22, 0.31, 0.16), 8, 5, 'dark', jitter=0.03, flat_bottom=0.0)
        b.tube([(0.17 * s, -0.02, 0.24), (0.17 * s, -0.02, 0.40)], [0.12, 0.11], 8, 'dark', side=Vector((1, 0, 0)))

    # Legs: long and thin, a little wider at the top.
    for s in (1, -1):
        b.tube([(0.17 * s, -0.02, 0.36), (0.165 * s, -0.01, 0.75), (0.16 * s, 0.0, 1.06)], [0.068, 0.072, 0.085], 8,
               'green', side=Vector((1, 0, 0)))

    # Body: a pear of fur, narrow chest and a round belly that sticks out in front.
    torso = [
        (1.00, 0.20, 0.18, 0.00), (1.08, 0.36, 0.32, -0.02), (1.26, 0.45, 0.39, -0.05), (1.46, 0.45, 0.39, -0.05),
        (1.64, 0.40, 0.34, -0.03), (1.82, 0.32, 0.28, -0.01), (1.98, 0.25, 0.22, 0.0), (2.08, 0.16, 0.15, 0.0),
    ]
    segs = 14
    rings = []
    for z, rx, ry, oy in torso:
        ring = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            k = 1 + rng.uniform(-0.035, 0.035)
            ring.append(Vector((math.cos(a) * rx * k, oy + math.sin(a) * ry * k, z + rng.uniform(-0.015, 0.015))))
        rings.append(ring)
    b.loft(rings, 'green', start_point=Vector((0, 0, 0.97)), end_point=Vector((0, 0, 2.12)))
    # Fur on the body: tufts that break the outline of the belly at its sides, short light tips of a collar, a jagged hem.
    # Each tuft is a thick wedge (its inner corner raised), so it reads from the front and the side, not as a blade.
    for lo, hi in ((-50, 50), (130, 230)):
        for z, rx, ry, oy, ph in ((1.58, 0.435, 0.375, -0.04, 0.0), (1.38, 0.45, 0.39, -0.05, 0.5)):
            fur_ring(b, (0, oy), rx, ry, z, 5, 0.07, 0.04, 'green', phase=ph, rise=0.06,
                     arc=(math.radians(lo), math.radians(hi)))
    # Rows of short wide zigzags across the belly in front and across the back, as on the concept.
    # Light like the collar, so they read from afar; one row over the belt and one under it, front and back.
    # (height, half width, half depth, centre y): on the belly's own surface there, from the torso rings.
    for (z, rx, ry, oy), (lo, hi), length, out in (
            ((1.68, 0.38, 0.33, -0.03), (215, 325), 0.10, 0.06), ((1.62, 0.405, 0.345, -0.03), (35, 145), 0.10, 0.06),
            ((1.30, 0.448, 0.388, -0.05), (220, 320), 0.09, 0.05), ((1.24, 0.44, 0.38, -0.047), (40, 140), 0.09, 0.05)):
        fur_ring(b, (0, oy), rx, ry, z, 7, length, out, 'light', rise=0.04, arc=(math.radians(lo), math.radians(hi)))
    fur_ring(b, (0, -0.01), 0.31, 0.27, 1.86, 12, 0.06, 0.04, 'light')
    fur_ring(b, (0, -0.02), 0.37, 0.33, 1.09, 18, 0.12, 0.04, 'green', phase=0.25)

    # Arms: straight out at the shoulders (T-pose), thin, a tuft at each shoulder.
    for s in (1, -1):
        b.tube([(0.24 * s, 0.0, 1.92), (0.62 * s, 0.0, 1.925), (0.98 * s, 0.0, 1.93), (1.14 * s, 0.0, 1.93)],
               [0.12, 0.10, 0.095, 0.09], 8, 'green', side=Vector((0, 0, 1)), flat=1.0)
        # Big mitt hands, palms down: a fat palm and three round fingers, about 0.3 m tall from the front.
        b.ellipsoid((1.28 * s, 0.0, 1.93), (0.17, 0.15, 0.13), 8, 5, 'green', jitter=0.03)
        # Fat sausage fingers grown into the palm: a mitt, not a bunch of balls.
        for dy, tip in ((-0.095, 1.50), (0.0, 1.53), (0.095, 1.50)):
            b.tube([(1.33 * s, dy, 1.93), (tip * s, dy * 1.05, 1.92)], [0.075, 0.07], 6, 'green',
                   side=Vector((0, 0, 1)))

    # Head: a round furry ball, sitting on the chest without a neck.
    hc = Vector((0.0, -0.02, 2.30))
    head_r = (0.40, 0.35, 0.34)
    b.ellipsoid(hc, head_r, 14, 9, 'green', jitter=0.035)
    # Cheek fluff: points hanging round the jaw, and a ring of fur peeking out under the hat.
    fur_ring(b, (0, -0.02), 0.33, 0.29, 2.12, 14, 0.11, 0.06, 'green', arc=(math.radians(150), math.radians(390)))
    # Tufts at the sides of the head and on the back of it: the outline is jagged, not a bald ball.
    for lo, hi in ((-55, 45), (135, 235)):
        fur_ring(b, (0, -0.02), 0.38, 0.33, 2.21, 6, 0.08, 0.06, 'green', rise=0.07,
                 arc=(math.radians(lo), math.radians(hi)))
    fur_ring(b, (0, -0.02), 0.37, 0.32, 2.46, 9, 0.08, 0.08, 'green', rise=0.07, arc=(math.radians(20), math.radians(160)))
    fur_ring(b, (0, -0.02), 0.40, 0.35, 2.30, 8, 0.09, 0.06, 'light', rise=0.05, arc=(math.radians(30), math.radians(150)))
    # Pointy ears, out to the sides and a little up.
    for s in (1, -1):
        base = Vector((0.33 * s, 0.0, 2.36))
        b.tube([base, base + Vector((0.16 * s, 0.01, 0.05)), base + Vector((0.32 * s, 0.03, 0.13))],
               [0.11, 0.07, 0.012], 6, 'green', side=Vector((0, 1, 0)), flat=0.45, caps=True)

    def on_head(x, z, lift=0.0):
        """The point on the front of the head at (x, z), pushed `lift` along -Y."""
        dx, dz = (x - hc.x) / head_r[0], (z - hc.z) / head_r[2]
        y = hc.y - head_r[1] * math.sqrt(max(0.0, 1 - dx * dx - dz * dz))
        return Vector((x, y - lift, z))

    # Eyes: white almonds with dark pupils looking a little inward; thick angry brows slanting down to the nose.
    for s in (1, -1):
        e = on_head(0.13 * s, 2.37, 0.0)
        tilt = Matrix.Rotation(math.radians(-14 * s), 3, 'Y')
        b.ellipsoid(e, (0.085, 0.045, 0.06), 6, 4, 'cream', matrix=tilt)
        p = on_head(0.115 * s, 2.36, 0.035)
        b.ellipsoid(p, (0.038, 0.02, 0.042), 6, 4, 'ink')
        inner, outer = on_head(0.04 * s, 2.43, 0.01), on_head(0.24 * s, 2.50, -0.01)
        mid_hi = on_head(0.15 * s, 2.51, 0.015)
        brow = [inner + Vector((0, 0, -0.02)), outer + Vector((0, 0, -0.035)), outer + Vector((0, 0, 0.02)),
                mid_hi + Vector((0, 0, 0.02)), inner + Vector((0, 0, 0.035))]
        if s < 0:
            brow.reverse()
        b.flat_poly(brow, Vector((0, -0.025, 0)), 'ink')
    # A green muzzle under the eyes gives the grin a volume from the side.
    mc = Vector((0.0, -0.32, 2.21))
    muzzle_r = (0.25, 0.12, 0.12)
    b.ellipsoid(mc, muzzle_r, 8, 5, 'green', jitter=0.02)

    def on_muzzle(x, z, lift=0.0):
        dx, dz = (x - mc.x) / muzzle_r[0], (z - mc.z) / muzzle_r[2]
        y = mc.y - muzzle_r[1] * math.sqrt(max(0.0, 1 - dx * dx - dz * dz))
        return Vector((x, y - lift, z))

    # Wide grin: a D-shaped dark mouth (straight upper lip, round bottom), a brown tongue, two white fangs.
    def d_shape(cx, top, half, depth, lift, count=10):
        pts = [on_muzzle(cx - half, top, lift), on_muzzle(cx + half, top, lift)]
        for j in range(1, count):
            a = math.pi * j / count
            pts.append(on_muzzle(cx + half * math.cos(a), top - depth * math.sin(a), lift))
        return pts
    b.flat_poly(d_shape(0.0, 2.25, 0.17, 0.12, -0.005), Vector((0, -0.02, 0)), 'ink')
    tongue = []
    for j in range(9):
        a = math.pi * j / 8
        tongue.append(on_muzzle(0.07 * math.cos(a), 2.16 - 0.03 * math.sin(a) + 0.03, 0.017))
    b.flat_poly(list(reversed(tongue)), Vector((0, -0.008, 0)), 'brown')
    for s in (1, -1):
        top = on_muzzle(0.09 * s, 2.25, 0.025)
        b.spike(top + Vector((-0.03, 0, 0)), top + Vector((0.03, 0, 0)), top + Vector((0, 0.03, 0)),
                top + Vector((0.0, -0.005, -0.08)), 'cream')

    # The stolen Santa hat: a cream fur trim, a red cone that bends over to the side, a pom-pom on its tip.
    trim_c = Vector((0.0, -0.01, 2.60))
    tilt = Matrix.Rotation(math.radians(-7), 3, 'Y')
    trim = [trim_c + tilt @ Vector((math.cos(2 * math.pi * j / 14) * 0.37, math.sin(2 * math.pi * j / 14) * 0.335, 0))
            for j in range(14)]
    b.loop_tube(trim, lambda i: 0.085 * (1 + rng.uniform(-0.1, 0.1)), 6, 'cream', jitter=0.08)
    hat_path = [(0.0, -0.01, 2.62), (0.03, 0.0, 2.80), (0.11, 0.02, 2.95), (0.25, 0.04, 3.00), (0.40, 0.05, 2.95),
                (0.52, 0.06, 2.84), (0.58, 0.06, 2.74)]
    b.tube(hat_path, [0.33, 0.29, 0.22, 0.15, 0.10, 0.065, 0.035], 8, 'red', side=Vector((0, 1, 0)), jitter=0.03)
    b.ellipsoid((0.60, 0.06, 2.65), (0.11, 0.11, 0.11), 8, 6, 'cream', jitter=0.08)

    # Rope belt round the belly, a knot in front and two hanging ends.
    bz = 1.44
    belt = [(math.cos(2 * math.pi * j / 16) * 0.465, -0.05 + math.sin(2 * math.pi * j / 16) * 0.405, bz) for j in range(16)]
    b.loop_tube(belt, 0.035, 5, 'brown')
    knot = Vector((0.12, -0.46, bz))
    b.ellipsoid(knot, (0.06, 0.04, 0.05), 6, 4, 'brown')
    # The two ends follow the belly down: a middle point lies on it, so they do not hang in the air.
    for dx, end in ((-0.02, 1.20), (0.04, 1.22)):
        x = knot.x + dx
        b.tube([Vector((x, knot.y + 0.005, bz - 0.03)), Vector((x + dx * 0.3, -0.445, 1.31)),
                Vector((x + dx * 0.5, -0.412, end))], [0.026, 0.025, 0.024], 5, 'brown', side=Vector((1, 0, 0)))

    # The stolen sack on the left hip: red, tied at the neck to the belt, two cream stars on it.
    sc = Vector((0.52, -0.08, 1.16))
    b.ellipsoid(sc, (0.24, 0.20, 0.29), 8, 6, 'red', jitter=0.04)
    neck = sc + Vector((-0.05, 0.0, 0.33))
    b.tube([neck + Vector((0, 0, -0.06)), neck + Vector((-0.02, 0, 0.04))], [0.07, 0.055], 6, 'brown')
    b.tube([neck + Vector((-0.02, 0, 0.04)), neck + Vector((-0.04, 0, 0.13))], [0.06, 0.10], 6, 'red', jitter=0.1)
    for (dx, dz, r) in ((0.07, 0.06, 0.06), (-0.06, -0.12, 0.045)):
        centre = sc + Vector((dx, 0, dz))
        u = (dx / 0.24)
        w = (dz / 0.29)
        centre.y = sc.y - 0.20 * math.sqrt(max(0.0, 1 - u * u - w * w)) - 0.004
        pts = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            rr = r if j % 2 == 0 else r * 0.45
            pts.append(centre + Vector((math.cos(a) * rr, 0, math.sin(a) * rr)))
        b.flat_poly(pts, Vector((0, -0.012, 0)), 'cream')

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

    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
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
