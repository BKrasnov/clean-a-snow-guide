"""Well (card 55be02): the farm's wishing well, a cosy faceted low-poly prop with snow caps.

    blender -b --factory-startup --python build_well.py -- --out <abs Well_master.blend> --texture <abs Well_Palette.png>

Concept: art/refs/well/well-turnaround.png (front, left, back). The crank handle is on the right seen from the front (+X),
as on the front view; the left view of the concept draws it on the wrong side. Metres, Z up, the well faces -Y, its base on
z = 0, the pivot in the middle of the base. Size of the well now in the game (CartoonFarm.Decor.Well): base 2.24 m across,
about 3.2 m tall; this one: base 2.16 m across (stones to 2.44 m), 3.3 m tall.
One mesh Well_Body, one material M_Well_Palette over a 64 x 64 palette texture: every face points at the middle of its
colour's 16 x 16 cell, so the colours stay flat at every mip level. Flat shading: the facets show, as in the style guide.
Snow faces take their colour from their facing: up is Снег, sides and undersides Тень снега.
"""
import argparse
import math
import random
import sys

import bmesh
import bpy
from mathutils import Vector

MODEL = 'Well'
# Colours of art/palette.json core, in the order of their cells in the texture.
COLORS = {
    'snow': 'F3F6F5',     # Снег: snow caps (faces looking up)
    'shade': 'CDCDED',    # Тень снега: snow edges and undersides
    'ice': 'A8DEE7',      # Лёд: frozen water in the well
    'stone': '909282',    # Камень: the round base
    'rock': 'A0B0C4',     # Металл: the big light stones
    'wood': 'CD925C',     # Дерево: rim, crank beam, crank, bucket
    'dark': '80401B',     # Тёмное дерево: posts, bucket bands
    'red': 'D6392B',      # Красный амбар: roof
    'straw': 'FAD66E',    # Солома: rope
}
ORDER = list(COLORS)
GRID = 4
CELL = 16
SIZE = GRID * CELL
SNOW_UP = 0.42  # a snow face whose normal has more Z than this is lit snow, otherwise the snow shadow
CAP_UP = 0.15  # the same for the soft caps on the stones: only their hanging rim is in shadow

rng = random.Random(55)


def cell_uv(color):
    i = ORDER.index(color)
    col, row = i % GRID, i // GRID
    return ((col + 0.5) / GRID, (row + 0.5) / GRID)


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new('UVMap')
        self.auto = []  # snow faces, coloured by their normal at the end

    def face(self, verts, color):
        f = self.bm.faces.new(verts)
        if color in ('auto', 'cap'):
            self.auto.append((f, SNOW_UP if color == 'auto' else CAP_UP))
            color = 'snow'
        u = cell_uv(color)
        for loop in f.loops:
            loop[self.uv].uv = u
        return f

    def poly(self, verts, color):
        """A face of up to four corners; a longer outline is cut into a triangle and the rest (no n-gons)."""
        if len(verts) <= 4:
            return self.face(verts, color)
        self.face([verts[0], verts[1], verts[-1]], color)
        return self.poly(verts[1:], color)

    def vert(self, co):
        return self.bm.verts.new(co)

    def loft(self, rings, color, cap_start=True, cap_end=True, start_point=None, end_point=None, colors=None):
        """Rings of points lofted into a tube; colors[i] paints the band between ring i and i + 1."""
        vs = [[self.vert(p) for p in ring] for ring in rings]
        n = len(rings[0])
        for i, (a, b) in enumerate(zip(vs, vs[1:])):
            c = colors[i] if colors else color
            for j in range(n):
                self.face([a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]], c)
        if cap_start:
            c0 = colors[0] if colors else color
            if start_point is not None:
                c = self.vert(start_point)
                for j in range(n):
                    self.face([vs[0][(j + 1) % n], vs[0][j], c], c0)
            else:
                self.face(list(reversed(vs[0])), c0)
        if cap_end:
            c1 = colors[-1] if colors else color
            if end_point is not None:
                c = self.vert(end_point)
                for j in range(n):
                    self.face([vs[-1][j], vs[-1][(j + 1) % n], c], c1)
            else:
                self.face(vs[-1], c1)
        return vs

    def lathe(self, profile, segs, color, center=(0.0, 0.0), colors=None, phase=0.0, start=None, end=None):
        """Turns a (radius, z) profile round the Z axis; start/end close the first/last ring with a fan at that z."""
        cx, cy = center
        rings = []
        for r, z in profile:
            rings.append([Vector((cx + math.cos(2 * math.pi * (j + phase) / segs) * r,
                                  cy + math.sin(2 * math.pi * (j + phase) / segs) * r, z)) for j in range(segs)])
        sp = Vector((cx, cy, profile[0][1])) if start else None
        ep = Vector((cx, cy, profile[-1][1])) if end else None
        return self.loft(rings, color, cap_start=bool(start), cap_end=bool(end), start_point=sp, end_point=ep,
                         colors=colors)

    def torus_lathe(self, profile, segs, color, phase=0.0):
        """A closed (radius, z) profile turned round Z: a ring with no caps (the well rim)."""
        n = len(profile)
        rings = []
        for j in range(segs):
            a = 2 * math.pi * (j + phase) / segs
            rings.append([self.vert((math.cos(a) * r, math.sin(a) * r, z)) for r, z in profile])
        for j in range(segs):
            a, b = rings[j], rings[(j + 1) % segs]
            for k in range(n):
                self.face([a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]], color)

    def tube(self, path, radii, segs, color, side=Vector((0, 0, 1)), caps='flat', phase=0.0):
        """Circles along a polyline; `side` fixes the ring orientation. caps: 'flat', 'round' or None."""
        rings = []
        for i, (p, r) in enumerate(zip(path, radii)):
            p = Vector(p)
            d = (Vector(path[min(i + 1, len(path) - 1)]) - Vector(path[max(i - 1, 0)])).normalized()
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            ring = []
            for j in range(segs):
                a = 2 * math.pi * (j + phase) / segs
                ring.append(p + (u * math.cos(a) + v * math.sin(a)) * r)
            rings.append(ring)
        if caps == 'round':
            start = Vector(path[0]) - (Vector(path[1]) - Vector(path[0])).normalized() * radii[0] * 0.5
            end = Vector(path[-1]) + (Vector(path[-1]) - Vector(path[-2])).normalized() * radii[-1] * 0.5
        elif caps == 'flat':
            start, end = Vector(path[0]), Vector(path[-1])
        else:
            start = end = None
        return self.loft(rings, color, cap_start=bool(caps), cap_end=bool(caps), start_point=start, end_point=end)

    def loop_tube(self, points, radius, segs, color, side=Vector((0, 0, 1))):
        """A closed ring tube through `points` (a rope coil): the last ring joins the first."""
        n = len(points)
        rings = []
        for i in range(n):
            p = Vector(points[i])
            d = (Vector(points[(i + 1) % n]) - Vector(points[i - 1])).normalized()
            u = (side - d * side.dot(d)).normalized()
            v = d.cross(u)
            rings.append([self.vert(p + (u * math.cos(2 * math.pi * j / segs) + v * math.sin(2 * math.pi * j / segs))
                                    * radius) for j in range(segs)])
        for i in range(n):
            a, b = rings[i], rings[(i + 1) % n]
            for j in range(segs):
                self.face([a[j], a[(j + 1) % segs], b[(j + 1) % segs], b[j]], color)

    def hull(self, points, color):
        """The convex hull of the points: chunky stones, posts, roof planks, snow pillows."""
        tmp = bmesh.new()
        vs = [tmp.verts.new(p) for p in points]
        bmesh.ops.convex_hull(tmp, input=vs)
        used = {v for f in tmp.faces for v in f.verts}
        vmap = {v: self.vert(v.co) for v in used}
        for f in tmp.faces:
            self.face([vmap[v] for v in f.verts], color)
        tmp.free()


def chamfer_box(center, axes, half, c, jitter=0.0):
    """Points of a box with chamfered edges in the frame `axes` (three unit vectors), half sizes `half`: each corner
    gives three points, each pulled in by `c` along the two other axes. Their hull is the bevelled box."""
    pts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                s = (sx, sy, sz)
                corner = [s[m] * half[m] * (1 + rng.uniform(-jitter, jitter)) for m in range(3)]
                for k in range(3):
                    p = Vector(center)
                    for m in range(3):
                        o = corner[m] if m == k else corner[m] - s[m] * c
                        p += axes[m] * o
                    pts.append(p)
    return pts


def build(texture_path):
    b = Builder()
    Z, X, Y = Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0))

    # --- Base: a round stone drum, a little narrower at the foot.
    base_r, base_top = 1.02, 0.80
    b.lathe([(0.97, 0.0), (1.02, 0.30), (1.02, base_top)], 14, 'stone', start=True, end=True, phase=0.5)

    # Big light stones in two staggered rows, each turned a little; some get snow caps on top.
    # Angles are measured from the front (-Y) towards +X.
    stones = [
        # (angle deg, row z, width, height, depth, snow): five big stones above, five below, about 40 degrees apart
        (-58, 0.60, 0.68, 0.38, 0.36, True), (70, 0.60, 0.64, 0.36, 0.36, False), (145, 0.60, 0.70, 0.38, 0.36, True),
        (218, 0.60, 0.64, 0.36, 0.34, False), (290, 0.60, 0.68, 0.38, 0.36, True),
        (-95, 0.22, 0.66, 0.40, 0.36, False), (-12, 0.22, 0.72, 0.40, 0.38, False), (42, 0.22, 0.64, 0.38, 0.36, True),
        (125, 0.22, 0.68, 0.40, 0.36, False), (205, 0.22, 0.66, 0.40, 0.36, False),
    ]
    for ang, z, w, h, dep, snow in stones:
        a = math.radians(ang + rng.uniform(-3, 3))
        out = Vector((math.sin(a), -math.cos(a), 0))
        tan = Vector((math.cos(a), math.sin(a), 0))
        tilt = math.radians(rng.uniform(-3, 3))
        tan2 = (tan * math.cos(tilt) + Z * math.sin(tilt)).normalized()
        up2 = out.cross(tan2).normalized() * -1
        if up2.z < 0:
            up2 = -up2
        centre = out * (base_r + 0.02) + Vector((0, 0, z))
        pts = chamfer_box(centre, (tan2, out, up2), (w / 2, dep / 2, h / 2), 0.06, jitter=0.04)
        for q in pts:  # the lower row stands on the ground
            q.z = max(q.z, 0.0)
        b.hull(pts, 'rock')
        if snow:
            top = z + h / 2
            # a soft flat dome: three rings of eight points, the lowest hangs 3 cm over the stone's edge all round
            rings = []
            for inset, dz in ((-0.03, -0.03), (0.04, 0.06), (0.12, 0.09)):
                for j in range(8):
                    t = 2 * math.pi * (j + 0.5) / 8
                    q = centre + tan2 * math.cos(t) * (w / 2 - inset) + out * math.sin(t) * (dep / 2 - inset)
                    q.z = top + dz
                    rings.append(q)
            b.hull(rings, 'cap')

    # --- Thick wooden rim with a bevelled top edge, ice inside.
    rim_in, rim_out, rim_lo, rim_hi = 0.72, 1.08, base_top, 1.02
    b.torus_lathe([(rim_in, rim_lo), (rim_out, rim_lo), (rim_out, rim_hi - 0.05), (rim_out - 0.04, rim_hi),
                   (rim_in + 0.03, rim_hi), (rim_in, rim_hi - 0.03)], 16, 'wood', phase=0.5)
    b.lathe([(rim_in + 0.01, 0.90), (rim_in + 0.01, 0.94)], 16, 'ice', start=True, end=True, phase=0.5)

    # --- Two thick dark posts standing on the rim, up into the roof.
    post_x, post_half, post_lo, post_hi = 0.80, 0.15, 0.92, 2.42
    for s in (-1, 1):
        b.hull(chamfer_box((post_x * s, 0, (post_lo + post_hi) / 2), (X, Y, Z),
                           (post_half, post_half, (post_hi - post_lo) / 2), 0.03), 'dark')

    # --- Pitched roof of two thick planks, ridge along X; eaves wider than the ridge, as on the concept's front.
    ridge_z, eave_y, eave_z = 3.14, 1.0, 2.36
    ridge_half, eave_half, thick = 1.0, 1.18, 0.15
    slope = math.atan2(ridge_z - eave_z, eave_y)
    for s in (-1, 1):
        n = Vector((0, s * math.sin(slope), math.cos(slope)))
        top = [Vector((-ridge_half, 0.02 * -s, ridge_z + 0.015)), Vector((ridge_half, 0.02 * -s, ridge_z + 0.015)),
               Vector((eave_half, s * eave_y, eave_z)), Vector((-eave_half, s * eave_y, eave_z))]
        b.hull(top + [p - n * thick for p in top], 'red')
    # Gables: red triangles on the posts, set back under the roof.
    under = ridge_z - thick / math.cos(slope)  # the roof's underside over the ridge
    gb = post_hi - 0.03
    gy = (under - gb) / math.tan(slope)
    for s in (-1, 1):
        gx = post_x * s
        tri = [Vector((gx, -gy, gb)), Vector((gx, gy, gb)), Vector((gx, 0, under + 0.03))]
        b.hull([p + X * 0.05 for p in tri] + [p - X * 0.05 for p in tri], 'red')

    # --- Snow on the roof: one thick pillow over the ridge onto both slopes. In the middle it covers the top of each
    # slope; at the gable ends it runs almost down to the eaves; its lower edge is wavy and droops over the ends.
    nu, ns = 12, 3
    slope_len = math.hypot(eave_y, ridge_z - eave_z) + 0.04
    over, crest = 0.07, 0.10
    ext = {}
    for side in (-1, 1):
        ph = rng.uniform(0, math.pi)
        ext[side] = []
        for i in range(nu + 1):
            u = -1 + 2 * i / nu
            # two broad waves along the lower edge; at the gable ends the snow runs almost down to the eaves
            e = 0.40 + 0.50 * smoothstep(0.62, 0.97, abs(u)) + 0.06 * math.sin(u * 2 * math.pi + ph)
            ext[side].append(min(e, 0.90 if i in (0, nu) else 0.97))
    hmid = 0.19
    wave = rng.uniform(0, math.pi)

    def snow_point(i, side, kk, h_scale):
        """kk: 0 is the flat crest row `crest` metres from the ridge, 1..ns the slope, ns + 1 the rounded lip."""
        u = -1 + 2 * i / nu
        lip = kk == ns + 1
        frac = min(kk, ns) / ns
        f = frac * ext[side][i]
        # a soft pillow: broad low waves along the ridge; rounded shoulders at the gable ends
        end = smoothstep(0.7, 1.0, abs(u))
        # Only the crest thins at the ends (round shoulders seen from the front). On the slope the ends are as thick as
        # the thickest wave, so from the side no thicker middle part peeks out over them.
        w = (1 - end) * math.sin(u * 1.6 * math.pi + wave) + end
        hh = hmid * (1 + 0.1 * w) * (1 - 0.7 * end if kk == 0 else 1.0) * h_scale
        if lip:
            hh *= 0.15
        # wider than the gable ends near the ridge (a wide band from the front); the ends bulge out mid-slope
        half = (ridge_half + (eave_half - ridge_half) * f + over + 0.10 * (1 - f) + 0.03 * end * h_scale
                + 0.06 * end * math.sin(math.pi * frac))
        x = u * half
        if i in (0, nu) and kk >= ns:
            x -= math.copysign(0.05, u)  # the lower corners tuck in: no sharp tongue
        d = Vector((0, side * math.cos(slope), -math.sin(slope)))
        nn = Vector((0, side * math.sin(slope), math.cos(slope)))
        if kk == 0:  # the two crest rows meet flat over the ridge: a soft bevel, not a sharp edge
            return Vector((x, 0, ridge_z)) + d * crest + nn * hh
        v = max(f * slope_len, crest + 0.12) + (0.06 if lip else 0.0)
        return Vector((x, 0, ridge_z)) + d * v + nn * hh

    rows = [(-1, kk) for kk in range(ns + 1, -1, -1)] + [(1, kk) for kk in range(0, ns + 2)]
    m = len(rows)
    top = [[b.vert(snow_point(i, sd, kk, 1.0)) for sd, kk in rows] for i in range(nu + 1)]
    bot = [[b.vert(snow_point(i, sd, kk, 0.0) + Vector((0, 0, -0.012))) for sd, kk in rows] for i in range(nu + 1)]
    # Colours: the top and the upper part of the ends are snow; the rounded lips, the lower band of the ends and the
    # underside are the snow shadow.
    for i in range(nu):
        for k in range(m - 1):
            c = 'shade' if k == 0 or k == m - 2 else 'snow'
            b.face([top[i][k], top[i + 1][k], top[i + 1][k + 1], top[i][k + 1]], c)
            b.face([bot[i][k + 1], bot[i + 1][k + 1], bot[i + 1][k], bot[i][k]], 'shade')
    # the two ends over the gables are cut by a row at a third of the height
    mids = {i: [b.vert(snow_point(i, sd, kk, 0.35)) for sd, kk in rows] for i in (0, nu)}

    def side_verts(i, k):
        """Top, (mid,) bottom of column i at row k: the wall of the lip takes the end's middle vertex too."""
        return [top[i][k]] + ([mids[i][k]] if i in mids else []) + [bot[i][k]]
    for i in range(nu):  # the lips at both lower edges
        b.poly(side_verts(i, 0) + list(reversed(side_verts(i + 1, 0))), 'shade')
        b.poly(side_verts(i + 1, m - 1) + list(reversed(side_verts(i, m - 1))), 'shade')
    for i, flip in ((0, False), (nu, True)):
        mid = mids[i]
        for k in range(m - 1):
            lip = k == 0 or k == m - 2
            quads = [([top[i][k + 1], mid[k + 1], mid[k], top[i][k]], 'shade' if lip else 'snow'),
                     ([mid[k + 1], bot[i][k + 1], bot[i][k], mid[k]], 'shade')]
            for q, c in quads:
                b.face(list(reversed(q)) if flip else q, c)

    # --- Crank beam: a round log through both posts at 2.02 m, ends sticking out.
    beam_z, beam_r = 2.02, 0.085
    b.tube([(-1.02, 0, beam_z), (1.0, 0, beam_z)], [beam_r, beam_r], 10, 'wood', side=Z, phase=0.5)
    # Rope: three yellow coils round the middle of the beam, a short rope down to the bucket handle.
    for cx in (-0.075, 0.0, 0.075):
        coil = [(cx, math.cos(2 * math.pi * j / 10) * (beam_r + 0.02), beam_z + math.sin(2 * math.pi * j / 10)
                 * (beam_r + 0.02)) for j in range(10)]
        b.loop_tube(coil, 0.036, 6, 'straw', side=X)
    handle_top = 1.80
    b.tube([(0, 0, beam_z - beam_r - 0.02), (0, 0, handle_top - 0.01)], [0.032, 0.032], 6, 'straw', side=X)

    # --- Crank on the right (+X): a hub on the post, an axle, an arm down and forward, the grip out to the side.
    px = post_x + post_half
    b.tube([(px - 0.01, 0, beam_z), (px + 0.05, 0, beam_z)], [0.12, 0.12], 8, 'wood', side=Z, phase=0.5)
    b.tube([(px + 0.05, 0, beam_z), (px + 0.11, 0, beam_z)], [0.05, 0.05], 8, 'wood', side=Z)
    arm0, arm1 = Vector((px + 0.13, 0, beam_z)), Vector((px + 0.17, -0.10, beam_z - 0.26))
    b.tube([arm0 + Vector((0, 0, 0.05)), arm1 - Vector((0, 0, 0.04))], [0.05, 0.05], 4, 'wood', side=X, phase=0.5)
    b.tube([arm1 + Vector((-0.05, 0, 0)), arm1 + Vector((0.30, 0, 0))], [0.05, 0.05], 8, 'wood', side=Z)
    b.tube([arm1 + Vector((0.20, 0, 0)), arm1 + Vector((0.34, 0, 0))], [0.065, 0.06], 8, 'wood', side=Z, caps='round')

    # --- Wooden bucket: wider at the top, two dark bands, hollow, a handle arc.
    bot_z, top_z, r_bot, r_top = 1.16, 1.58, 0.19, 0.25

    def r_at(z):
        return r_bot + (r_top - r_bot) * (z - bot_z) / (top_z - bot_z)
    band = 0.016
    zs = [bot_z, 1.22, 1.29, 1.45, 1.52, top_z]
    prof = [(r_at(bot_z), bot_z), (r_at(1.22), 1.22), (r_at(1.22) + band, 1.22), (r_at(1.29) + band, 1.29),
            (r_at(1.29), 1.29), (r_at(1.45), 1.45), (r_at(1.45) + band, 1.45), (r_at(1.52) + band, 1.52),
            (r_at(1.52), 1.52), (r_top, top_z), (r_top - 0.03, top_z), (r_bot - 0.02, bot_z + 0.07)]
    cols = ['wood', 'dark', 'dark', 'dark', 'wood', 'dark', 'dark', 'dark', 'wood', 'wood', 'wood']
    b.lathe(prof, 8, 'wood', colors=cols, start=True, end=True, phase=0.5)
    del zs
    arc_c, arc_r = Vector((0, 0, 1.52)), r_top + 0.03
    arc = [arc_c + Vector((math.cos(math.pi * j / 8) * arc_r, 0, math.sin(math.pi * j / 8) * (handle_top - 1.52)))
           for j in range(9)]
    b.tube(arc, [0.022] * 9, 5, 'wood', side=Y, caps='round')
    for s in (-1, 1):
        b.tube([(s * (r_at(1.52) - 0.01), 0, 1.52), (s * (r_at(1.52) + 0.05), 0, 1.52)], [0.035, 0.035], 6, 'dark',
               side=Z)

    # --- One mesh, flat shaded; snow takes its colour from its facing.
    bmesh.ops.recalc_face_normals(b.bm, faces=b.bm.faces[:])
    for f, limit in b.auto:
        f.normal_update()
        u = cell_uv('snow' if f.normal.z > limit else 'shade')
        for loop in f.loops:
            loop[b.uv].uv = u
    mesh = bpy.data.meshes.new(MODEL + '_Body')
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
    px_ = [0.0] * (SIZE * SIZE * 4)
    for y in range(SIZE):
        for x in range(SIZE):
            i = (y // CELL) * GRID + x // CELL
            code = COLORS[ORDER[i]] if i < len(ORDER) else COLORS['stone']
            rgb = [int(code[k:k + 2], 16) for k in (0, 2, 4)]
            o = (y * SIZE + x) * 4
            px_[o:o + 4] = [rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 1.0]
    img.pixels.foreach_set(px_)
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
    bpy.context.scene.unit_settings.system = 'METRIC'
    ob, img = build(a.texture)
    bpy.ops.wm.save_as_mainfile(filepath=a.out)
    img.filepath = bpy.path.relpath(a.texture)
    bpy.ops.wm.save_mainfile()
    tris = sum(len(pg.vertices) - 2 for pg in ob.data.polygons)
    lo = [min(v.co[i] for v in ob.data.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in ob.data.vertices) for i in range(3)]
    print('WELL tris=%d size=%s' % (tris, ['%.3f' % (h - l) for l, h in zip(lo, hi)]))


if __name__ == '__main__':
    main(sys.argv)
