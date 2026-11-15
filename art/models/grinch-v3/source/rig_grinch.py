"""Grinch, version 3 (card e49171): the skeleton and the skin weights.

    blender -b <abs Grinch_master.blend> --python rig_grinch.py -- [--out <abs .blend>]

Opens the master built by build_grinch.py, adds the studio biped skeleton Grinch_Rig (Mixamo names and axes,
biped_rig.build_biped, T-pose, no finger bones: the Grinch wears mittens), binds Grinch_Body to it (an Armature
modifier, the rig is the parent) and adds the studio-only range-of-motion action ROM (rom_clip.make_rom_action).
Saves to --out, by default over the opened file. A rig of an earlier run is replaced.

The joints are measured on the mesh: the rings of the legs and arms, the mitt, the boots, the body and the head.
The weights go part by part, since the mesh is many separate parts (fur shells, eyes, hat, sack, belt):
- the head shell and everything on it (eyes, mouth, fangs, tongue, ears, cheek locks, hat, pom-pom) -> Head;
- the body shell with its fur tiers -> the spine bones by height, linear between the middles of the bones, and the
  shoulder bone near the arm root;
- the belt and its knot -> the body weights at the height of their middle, the rope ends -> at their own height; the sack with its tie and stars, rigid -> the
  body weights at the tie;
- the arms -> Shoulder, Arm, ForeArm, Hand along the arm with smooth blends at the shoulder, elbow and wrist;
  the mitt, fingers and thumb -> Hand;
- the legs -> UpLeg, Leg, Foot with smooth blends at the knee and the ankle; boots and cuffs -> Foot, the front of
  the boot blends into ToeBase.
At most 4 bones a vertex, sums 1, no vertex without a weight.
"""
import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
for skills in ('.agents', '.claude'):
    scripts = ROOT / skills / 'skills' / 'game-model-workflow' / 'scripts'
    if (scripts / 'biped_rig.py').exists():
        sys.path.insert(0, str(scripts))
        break
import biped_rig  # noqa: E402
import rom_clip  # noqa: E402

RIG, BODY = 'Grinch_Rig', 'Grinch_Body'
P = biped_rig.PREFIX
MAX_INFLUENCES = 4
# Blend widths, metres: the knee and elbow blend over 0.5 m (the two rings around them lie at +-0.063 m, the
# next rings 0.4 m away take a little of the bend too), the wrist over 0.1 m inside the mitt.
KNEE_BLEND, ELBOW_BLEND, WRIST_BLEND = 0.50, 0.50, 0.10
# The knee and elbow pivots sit on the inner surface of the bend (the knee at the back, the elbow at the front):
# a deep bend then stretches the outer side and does not fold the inner one (anim-critic round 1: 15 collapsed
# triangles at the knee, 12 at the elbow; the bend axes stay those of Mixamo, the tilt of the bones is about them).
KNEE_IN, ELBOW_IN = 0.10, 0.09
# The ankle: the leg's lowest ring, inside the boot cuff, is half Foot; the shin above it is Leg (no rubber shin).
ANKLE_FOOT, ANKLE_BLEND = 0.5, 0.10
# The arm root: the shoulder share falls linearly to 0 at SHOULDER_TO off the body axis over SHOULDER_SPAN:
# the arm ring in the body (0.23 m) is half Shoulder, the ring at the body side (0.45 m) 0.16.
SHOULDER_TO, SHOULDER_SPAN = 0.55, 0.63
# The body near the arm root follows the shoulder bone: up to SHOULDER_BODY from 0.22 m off the axis, over
# 0.20 m, within 0.08 m of the arm height and fading over 0.20 m more.
SHOULDER_BODY = 0.6
# The Hips share of the body fades from this far below the hips joint.
HIPS_LOW = 0.0
# The front of the boot bends with ToeBase: from y = TOE_FROM forward over TOE_SPAN (a wide soft blend: a
# narrow one folds the sole, anim-critic round 1).
TOE_FROM, TOE_SPAN = -0.05, 0.35


# Joint limits of the Grinch (anim-critic round 1): degrees about the T-pose axes as in rom_clip.py (Z up, the model
# faces -Y, its left side is +X), left side; the right mirrors. Beyond them his big head, wide belly and wide boots
# get in the way: a raised arm goes into the head and the hat, a lowered arm into the belly, legs crossed inward
# put one boot into the other; past 30 degrees forward the round belly folds into the chest fur, past 25 degrees
# sideways the side of the body stretches more than 1.6 times. Clips keep within them (motion-profile.json, the joint_limit flag of anim_check.py).
# The spine, neck and head limits are per bone: the studio ROM shares those moves between the bones.
# The foot lifts its toe up to 35 degrees, not the ROM's 20 (clips_grinch.py): the knee pivot sits 0.10 m back, so the
# rest leg bends slightly backwards and a standing leg with its knee forward tilts the shin 20-30 degrees off rest
# while the boot stands flat; the ROM's squat checks the foot at -35 degrees (SQUAT_SHIN).
JOINT_LIMITS = {
    'Neck': {'x': [-12.5, 10], 'y': [-10, 10], 'z': [-35, 35]},
    'Head': {'x': [-12.5, 10], 'y': [-10, 10], 'z': [-35, 35]},
    'Spine': {'x': [-10, 10], 'y': [-8.3, 8.3], 'z': [-15, 15]},
    'Spine1': {'x': [-10, 10], 'y': [-8.3, 8.3], 'z': [-15, 15]},
    'Spine2': {'x': [-10, 10], 'y': [-8.3, 8.3], 'z': [-15, 15]},
    'LeftShoulder': {'y': [-25, 10]},
    'LeftArm': {'x': [-70, 70], 'y': [-50, 45], 'z': [-90, 40]},
    'LeftForeArm': {'z': [-145, 0]},
    'LeftHand': {'y': [-60, 70], 'z': [-30, 30]},
    'LeftUpLeg': {'x': [-100, 30], 'y': [-45, 3], 'z': [-40, 40]},
    'LeftLeg': {'x': [0, 140]},
    'LeftFoot': {'x': [-35, 45], 'y': [-20, 20]},
    'LeftToeBase': {'x': [-30, 30]},
}
# The studio ROM moves that go past the limits, cut to them: label -> (minimum, maximum) of the move in rom_clip.MOVES.
LIMIT_MOVES = {
    'голова кивок': (-25, 20),
    'голова наклон': (-20, 20),
    'корпус вперёд-назад': (-30, 30),
    'корпус вбок': (-25, 25),
    'руки вверх-вниз': (-50, 45),
    'руки вперёд-назад': (-90, 40),
    'ноги в стороны': (-45, 3),
}


def limited_moves(moves):
    """rom_clip.MOVES with the moves of LIMIT_MOVES cut to the Grinch's limits."""
    out = []
    for label, seconds, entries in moves:
        if label in LIMIT_MOVES and entries:
            low, high = LIMIT_MOVES[label]
            entries = [(bones, axis, low, high, split) for bones, axis, _, _, split in entries]
        out.append((label, seconds, entries))
    return out


def write_profile(path):
    """The motion profile of the Grinch: the joint limits, with the rig prefix; the clip modes clips_grinch.py wrote
    into it are kept."""
    import json
    old = json.loads(Path(path).read_text(encoding='utf-8')) if Path(path).exists() else {}
    profile = {'model': 'Grinch', 'note': 'Пределы суставов Гринча (rig_grinch.JOINT_LIMITS): градусы вокруг осей '
               'T-позы, как в rom_clip.py, левая сторона; правая зеркалится.',
               'limits': {'joints': {P + bone: limit for bone, limit in JOINT_LIMITS.items()}}}
    if 'clips' in old:
        profile['clips'] = old['clips']
    Path(path).write_text(json.dumps(profile, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def parts(me):
    """Connected parts of the mesh: lists of vertex indices."""
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    seen, out = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        seen.add(v.index)
        stack, comp = [v], []
        while stack:
            x = stack.pop()
            comp.append(x.index)
            for e in x.link_edges:
                o = e.other_vert(x)
                if o.index not in seen:
                    seen.add(o.index)
                    stack.append(o)
        out.append(comp)
    bm.free()
    return out


class Part:
    def __init__(self, me, idx):
        self.idx = idx
        self.co = [me.vertices[i].co.copy() for i in idx]
        self.lo = Vector([min(c[k] for c in self.co) for k in range(3)])
        self.hi = Vector([max(c[k] for c in self.co) for k in range(3)])
        self.mid = (self.lo + self.hi) / 2
        self.size = self.hi - self.lo

    def rings(self, axis, digits=3):
        """Centres of the rings of a tube along `axis` (0 = x, 2 = z): vertices grouped by that coordinate."""
        groups = {}
        for c in self.co:
            groups.setdefault(round(c[axis], digits), []).append(c)
        return sorted((k, sum(g, Vector()) / len(g)) for k, g in groups.items() if len(g) >= 6)


def classify(me):
    """Names every part of the Grinch mesh by its place and size (left side and centre; right mirrors)."""
    found = {}
    for idx in parts(me):
        p = Part(me, idx)
        side = 'Left' if p.mid.x > 0 else 'Right'
        if p.hi.z < 0.40 and len(idx) > 60:
            kind = 'boot'
        elif p.lo.z > 0.25 and p.hi.z < 0.50:
            kind = 'cuff'
        elif p.lo.z < 0.40 and p.hi.z > 1.2 and p.size.x < 0.3:
            kind = 'leg'
        elif p.lo.z > 1.5 and p.hi.z < 2.0 and p.size.x > 0.6 and abs(p.mid.x) > 0.3:
            kind = 'arm'
        elif abs(p.mid.x) > 0.95 and 1.5 < p.mid.z < 2.0:
            kind = 'hand'
        elif len(idx) > 300 and p.hi.z < 2.0:
            kind = 'body'
        elif p.mid.z > 1.95:
            kind = 'head'
        elif p.mid.x > 0.38 and 0.9 < p.mid.z < 1.8:
            kind, side = 'sack', ''
        elif abs(p.mid.x) < 0.5 and 1.35 < p.mid.z < 1.7:
            kind, side = 'belt', ''
        else:
            raise SystemExit('rig_grinch: unknown part at %s, %d vertices' % (tuple(round(c, 3) for c in p.mid), len(idx)))
        if kind in ('body', 'head', 'sack', 'belt'):
            side = ''
        found.setdefault((kind, side), []).append(p)
    return found


def measure(found, me):
    """Joints of the skeleton, left side and centre, metres."""
    leg = found[('leg', 'Left')][0]
    rings = leg.rings(2)
    # Rings of the leg (the cap points are no rings): the ankle ring, the two knee rings, the hip ring.
    inner = [c for _, c in rings]
    assert len(inner) == 4, inner
    ankle_ring, knee_lo, knee_hi, hip_ring = inner[0], inner[1], inner[2], inner[-1]
    knee = (knee_lo + knee_hi) / 2
    hip = Vector((hip_ring.x, 0.0, hip_ring.z - 0.03))
    boot = found[('boot', 'Left')][0]
    arm = found[('arm', 'Left')][0]
    arings = [c for _, c in arm.rings(0)]   # in the body, at its side, two around the elbow, in the mitt
    assert len(arings) == 5, arings
    elbow = (arings[2] + arings[3]) / 2
    arm_z = elbow.z
    body = found[('body', '')][0]
    mitt = min(found[('hand', 'Left')], key=lambda p: p.lo.x)
    wrist_x = mitt.lo.x + 0.04
    side_x = max(c.x for c in body.co if abs(c.z - arm_z) < 0.05)
    head = found[('head', '')]
    head_shell = max(head, key=lambda p: len(p.idx))
    hat_trim_top = max(p.hi.z for p in head if p.lo.z > 2.3 and p.hi.z < 2.75)

    def body_y(z):
        band = [c.y for c in body.co if abs(c.z - z) < 0.04]
        return (min(band) + max(band)) / 2 if band else 0.0
    hips_z = hip.z + 0.06
    neck_z = head_shell.lo.z + 0.13          # the head sits on the body: the neck joint just under the head shell
    head_z = neck_z + 0.10
    spine2_z = arm_z - 0.05
    spine_z = hips_z + (spine2_z - hips_z) / 3
    spine1_z = hips_z + (spine2_z - hips_z) * 2 / 3
    joints = {
        'Hips': (0.0, body_y(hips_z) * 0.3, hips_z),
        'Spine': (0.0, body_y(spine_z) * 0.5, spine_z),
        'Spine1': (0.0, body_y(spine1_z) * 0.5, spine1_z),
        'Spine2': (0.0, body_y(spine2_z) * 0.5, spine2_z),
        'Neck': (0.0, head_shell.mid.y, neck_z),
        'Head': (0.0, head_shell.mid.y, head_z),
        'HeadTop_End': (0.0, head_shell.mid.y, hat_trim_top),
        'LeftShoulder': (0.09, 0.0, arm_z - 0.02),
        'LeftArm': (side_x - 0.03, 0.0, arm_z),   # just inside the body side: hanging arms clear the belly more
        'LeftForeArm': (elbow.x, -ELBOW_IN, arm_z),
        'LeftHand': (wrist_x, 0.0, arm_z),
        'LeftUpLeg': tuple(hip),
        'LeftLeg': (knee.x, KNEE_IN, knee.z),
        'LeftFoot': (ankle_ring.x, 0.0, 0.24),
        'LeftToeBase': (boot.mid.x, -0.22, 0.07),
        'LeftToe_End': (boot.mid.x, boot.lo.y, 0.07),
    }
    joints = {k: tuple(round(c, 4) for c in v) for k, v in joints.items()}
    numbers = {'ankle_ring_z': ankle_ring.z, 'knee_z': knee.z, 'elbow_x': elbow.x, 'wrist_x': wrist_x,
               'arm_z': arm_z, 'body_side_x': side_x}
    return joints, numbers


def spine_weights(z, joints):
    """Spine bones by height, linear between the middles of the bones; the Hips share is full only below the
    hips joint, so the bend of the lower back spreads over a longer band (the belly is big)."""
    names = ['Hips', 'Spine', 'Spine1', 'Spine2', 'Neck']
    ends = names[1:] + ['Head']
    mids = [(joints[a][2] + joints[b][2]) / 2 for a, b in zip(names, ends)]
    mids[0] = joints['Hips'][2] - HIPS_LOW
    if z <= mids[0]:
        return {'Hips': 1.0}
    for (a, za), (b, zb) in zip(zip(names, mids), zip(names[1:], mids[1:])):
        if z <= zb:
            t = (z - za) / (zb - za)
            return {a: 1 - t, b: t}
    return {'Neck': 1.0}


def body_weights(co, joints, n):
    w = spine_weights(co.z, joints)
    side = 'Left' if co.x > 0 else 'Right'
    near = smooth((abs(co.x) - 0.22) / 0.20) * (1 - smooth((abs(co.z - n['arm_z']) - 0.08) / 0.20))
    s = SHOULDER_BODY * near
    if s > 1e-4:
        w = {k: v * (1 - s) for k, v in w.items()}
        w[side + 'Shoulder'] = s
    return w


def arm_weights(co, side, n):
    x = abs(co.x)
    hand = smooth((x - (n['wrist_x'] - 0.06)) / WRIST_BLEND)
    fore = smooth((x - (n['elbow_x'] - ELBOW_BLEND / 2)) / ELBOW_BLEND)
    sh = min(1.0, max(0.0, (SHOULDER_TO - x) / SHOULDER_SPAN))
    rest = (1 - hand) * (1 - fore)
    return {side + 'Hand': hand, side + 'ForeArm': (1 - hand) * fore, side + 'Shoulder': rest * sh,
            side + 'Arm': rest * (1 - sh)}


def leg_weights(co, side, n):
    up = smooth((co.z - (n['knee_z'] - KNEE_BLEND / 2)) / KNEE_BLEND)
    foot = ANKLE_FOOT * (1 - smooth((co.z - n['ankle_ring_z']) / ANKLE_BLEND))
    return {side + 'UpLeg': up, side + 'Foot': (1 - up) * foot, side + 'Leg': (1 - up) * (1 - foot)}


def boot_weights(co, side):
    toe = smooth((TOE_FROM - co.y) / TOE_SPAN)
    return {side + 'ToeBase': toe, side + 'Foot': 1 - toe}


def clean(w):
    """At most MAX_INFLUENCES bones, tiny weights dropped, the sum 1."""
    items = sorted(((k, v) for k, v in w.items() if v > 1e-3), key=lambda kv: -kv[1])[:MAX_INFLUENCES]
    total = sum(v for _, v in items)
    return {k: v / total for k, v in items}


def skin(ob, found, joints, n):
    weights = {}
    for (kind, side), plist in found.items():
        for p in plist:
            for i, co in zip(p.idx, p.co):
                if kind == 'head':
                    w = {'Head': 1.0}
                elif kind == 'hand':
                    w = {side + 'Hand': 1.0}
                elif kind == 'cuff':
                    w = {side + 'Foot': 1.0}
                elif kind == 'boot':
                    w = boot_weights(co, side)
                elif kind == 'leg':
                    w = leg_weights(co, side, n)
                elif kind == 'arm':
                    w = arm_weights(co, side, n)
                elif kind == 'body':
                    w = body_weights(co, joints, n)
                elif kind == 'belt':
                    # A rope keeps its round section: every vertex takes the body weights at the height of the
                    # part's middle (the belt loop, the knot) or of its own ring (the ends hanging on the belly).
                    # The knot is 0.125 m tall, the ends 0.16-0.19: the round caps of an end take the weights of
                    # its first and last rings.
                    z = min(max(co.z, p.lo.z + 0.04), p.hi.z - 0.04) if p.size.z > 0.14 else p.mid.z
                    w = body_weights(Vector((co.x, co.y, z)), joints, n)
                else:
                    continue
                weights[i] = clean(w)
    # The sack hangs from the belt as one rigid piece: every vertex takes the body weights at the tie, the top
    # of the sack's neck where it meets the belt.
    sack = found.get(('sack', ''), [])
    if sack:
        tie_part = max(sack, key=lambda p: p.hi.z)
        tie = Vector((tie_part.mid.x, tie_part.mid.y, tie_part.lo.z))
        w = clean(body_weights(tie, joints, n))
        for p in sack:
            for i in p.idx:
                weights[i] = dict(w)
    ob.vertex_groups.clear()
    groups = {}
    for i, w in weights.items():
        for bone, value in w.items():
            name = P + bone
            if name not in groups:
                groups[name] = ob.vertex_groups.new(name=name)
            groups[name].add([i], value, 'REPLACE')
    return weights


def main(argv):
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    out = a.out or bpy.data.filepath
    ob = bpy.data.objects[BODY]
    old = bpy.data.objects.get(RIG)
    if old is not None:
        data = old.data
        bpy.data.objects.remove(old)
        bpy.data.armatures.remove(data)
    for m in [m for m in ob.modifiers if m.type == 'ARMATURE']:
        ob.modifiers.remove(m)
    ob.parent = None
    found = classify(ob.data)
    joints, n = measure(found, ob.data)
    collection = ob.users_collection[0]
    height = max(v.co.z for v in ob.data.vertices)
    rig = biped_rig.build_biped(name=RIG, joints=joints, height=height, fingers=False, collection=collection)
    weights = skin(ob, found, joints, n)
    ob.parent = rig
    ob.matrix_parent_inverse.identity()
    mod = ob.modifiers.new('Armature', 'ARMATURE')
    mod.object = rig
    mod.use_vertex_groups = True
    mod.use_deform_preserve_volume = False
    _, segments = rom_clip.make_rom_action(rig)
    rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.context.scene.frame_set(1)
    bpy.context.preferences.filepaths.save_version = 0   # no .blend1 next to the master
    bpy.ops.wm.save_as_mainfile(filepath=out)
    unweighted = len(ob.data.vertices) - len(weights)
    most = max(len(w) for w in weights.values())
    sums = max(abs(sum(w.values()) - 1) for w in weights.values())
    write_profile(Path(__file__).resolve().parent / 'motion-profile.json')
    print('GRINCH_RIG bones=%d deform_groups=%d max_influences=%d unweighted=%d sum_error=%.2e rom_moves=%d'
          % (len(rig.data.bones), len(ob.vertex_groups), most, unweighted, sums, len(segments)))
    print('GRINCH_RIG parts=%s' % {'%s%s' % (s, k): len(v) for (k, s), v in sorted(found.items())})
    print('GRINCH_RIG measured=%s' % {k: round(v, 4) for k, v in n.items()})
    print('GRINCH_RIG joints=%s' % joints)


if __name__ == '__main__':
    main(sys.argv)
