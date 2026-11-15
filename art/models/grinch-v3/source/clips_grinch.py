"""Grinch, version 3 (card e49171): the game clips from Mixamo on the approved rig.

    blender -b <abs Grinch_master.blend> --python clips_grinch.py -- [--backup <abs .blend>] [--out <abs .blend>]

Opens the rigged master (rig_grinch.py), gives Grinch_Rig the five Mixamo clips of source/mixamo/ (FBX without skin,
30 fps) as the actions Idle, Walk, Attack, Hit and Stunned and brings each to the Grinch:
- Idle and Walk, in-place cycles: clip_polish.polish (hips scale, loop seam, feet planted by X Bot's ankles, head and
  neck lag, floor lift) with the liveliness numbers of CYCLES, then the joint limits of the motion profile.
- Attack and Hit, one-shot clips from Idle to Idle: hips scale, joint limits, a new timing (ONCE anchors: the Attack's
  windup lasts 0.8 s, card 9c7419), the ends blended into the first pose of Idle, the feet planted by X Bot's ankles
  from the stance of Idle (two-bone IK; the Hit stands its ground: the Grinch is hit ten times a fight and must not
  wander off), the hips lowered where a leg would go straight, the floor lift.
- Stunned, a seated cycle (it starts seated; how the Grinch sits down is the owner's question): hips scale, joint
  limits, loop seam, seated on the floor.
Joint limits (motion-profile.json, rig_grinch.JOINT_LIMITS): a turn beyond them, about the axes of the T-pose, is cut
back to them per axis (limit_axes): a bone whose whole range fits within the limit is shifted inside it (the arms
hang 45 degrees down at most: the Grinch's belly is wide), a larger one is squeezed softly into it near its ends.
Curves of bones the rig has not (Mixamo's fingers) are removed: the FBX export takes only actions whose curves all
resolve on the armature.

Writes the clip modes into source/motion-profile.json and the record of the polish into reports/clips-report.json;
backs the master up to --backup first (by default the system's temporary folder), then saves to --out, by default over
the opened file.
"""
import argparse
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True   # no __pycache__ next to the master
ROOT = Path(__file__).resolve().parents[4]
for skills in ('.agents', '.claude'):
    scripts = ROOT / skills / 'skills' / 'game-model-workflow' / 'scripts'
    if (scripts / 'clip_polish.py').exists():
        sys.path.insert(0, str(scripts))
        break
import biped_rig  # noqa: E402
import clip_polish  # noqa: E402
import motion_profile  # noqa: E402
import studio_scene  # noqa: E402

RIG, BODY = 'Grinch_Rig', 'Grinch_Body'
P = biped_rig.PREFIX
FPS = 30
SIDES = ('Left', 'Right')
MIXAMO = HERE / 'mixamo'
PROFILE = HERE / 'motion-profile.json'
REPORT = HERE.parent / 'reports' / 'clips-report.json'

# How each clip plays (motion_profile.clip_mode): the game moves the Grinch, the cycles stay in place.
CLIP_MODES = {
    'Idle': {'mode': 'in_place'},
    'Walk': {'mode': 'in_place'},
    'Attack': {'mode': 'once', 'from': 'Idle', 'to': 'Idle'},
    'Hit': {'mode': 'once', 'from': 'Idle', 'to': 'Idle'},
    'Stunned': {'mode': 'in_place'},
}
SOURCES = {
    'Idle': 'Idle_BreathingIdle.fbx',
    'Walk': 'Walk_WalkingWithASwagger_InPlace.fbx',
    'Attack': 'Attack_ZombiePunching.fbx',
    'Hit': 'Hit_ZombieReactionHitStumbleBack.fbx',
    'Stunned': 'Stunned_SittingDazed.fbx',
}
# The liveliness numbers of clip_polish.polish, from the keeper's (references/workflow.md, section 6); the Grinch's
# legs are 1.27 times X Bot's, so the walk's swing lift and the idle's sway are a little larger.
CYCLES = {
    'Idle': dict(sway=0.035, lift=0.0, window=0, nod=4.0, delay=0.25, gain=0.3, neck=(0.9, 0.2)),
    'Walk': dict(lift=0.045, window=0, nod=4.0, delay=0.15, gain=1.6),
}
# The one-shot clips. anchors: (source frame, clip frame), a smooth monotone time map through them (frame 1 is the
# clip's start); blend_in, blend_out: frames the clip comes out of and goes back into the first pose of Idle;
# arms_out: (first, last) clip frames over which the arms go back to Idle early; feet: the share of X Bot's steps the
# feet take (0: they stand where Idle stands); lift: how high a moving foot rises (m; X Bot's zombie steps drag the
# foot along the floor); hips: (the most the hips go off their start along the floor in metres, the share of their
# rise and fall kept, the share of their sideways move kept: the zombie's hips swing 0.25 m over the standing left
# leg and turned its thigh inward past its 3 degrees) or None; hips_turn: the share of the pelvis' own turn kept (the planted legs follow it and the
# thighs turned inward past their 3 degrees); smooth: [1, 2, 1] passes over the arms (the strike's speed changes at
# the anchors jolted them).
ONCE = {
    # Zombie Punching: still to source 8, the backswing 8-22, the overhead swing 22-35 (its top at 35-37), down to the
    # front 35-43, low follow-through to 48, a second swing up 49-58 (left out: arms_out), back to the stance by 70.
    # Windup 8-35 -> 0.8 s (card 9c7419: "замах 0,8 с ... и удар"), the strike 35-43 at its own speed.
    'Attack': dict(anchors=[(8, 1), (35, 25), (43, 33), (70, 60), (78, 66)], blend_in=10, blend_out=14,
                   arms_out=(35, 46), feet=0.25, lift=0.08, hips=(0.10, 0.3, 0.2), hips_turn=0.2, smooth=6),
    # Zombie Reaction Hit Stumble Back: still to source 11, the hit 11-19, two steps back 19-46, standing 46-66.
    # In place: the feet stand, the hips rock back at most 0.12 m and come back with the blend into Idle.
    'Hit': dict(anchors=[(10, 1), (46, 31), (58, 41)], blend_in=8, blend_out=14, arms_out=None, feet=0.0, lift=0.0,
                hips=(0.10, 1.0, 1.0), hips_turn=0.3, smooth=5),
}
# Hips lowered after polish (m), the legs solved again (settle).
SETTLE = {'Walk': 0.025}
# Cycles whose soles are pinned to one floor speed (pin_soles): a sole under CONTACT stands (anim_check.py's 0.023 m
# for the Grinch's 1.0 m legs, and a little more), a swinging one clears CLEAR.
PIN_SOLES = ('Walk',)
CONTACT, CLEAR, MIN_STANCE = 0.03, 0.065, 4
# The Stunned cycle: the whole seated clip, its seam closed; the lowest point of the mesh on the floor.
SEATED_DEPTH = 0.004
# Joint limits: a bone of SHIFT_BONES whose range on an axis fits within SHIFT_FIT of the limit's width is shifted
# into it, SHIFT_MARGIN degrees inside; any other is squeezed softly over SOFT degrees (at most a quarter of the width)
# at the end it goes past.
SHIFT_BONES = ('Shoulder', 'Arm', 'Spine', 'Neck', 'Head')
SHIFT_FIT, SHIFT_MARGIN, SOFT, SOFT_MARGIN = 0.8, 1.0, 8.0, 0.3
# The head's turn beyond its limits goes to the neck first (each has half of the Grinch's 20-25 degrees).
PASS_ON = (('Head', 'Neck'),)
LEG_BONES = ('UpLeg', 'Leg', 'Foot', 'ToeBase')
# A planted boot lifts its heel rather than bend the ankle past this (degrees about X; the profile allows -35).
FOOT_PITCH = -33.0
# Legs of a one-shot clip stay bent at least this much (share of their length from hip to ankle).
REACH = 0.985
KNEE_LIMIT = 140.0


# Curves ---------------------------------------------------------------------------------------------------------------

def curves_of(action):
    """{data path: {index: F-curve}}."""
    out = {}
    for fc in studio_scene.action_fcurves(action):
        out.setdefault(fc.data_path, {})[fc.array_index] = fc
    return out


def rot_path(bone):
    return 'pose.bones["%s"].rotation_quaternion' % bone


def loc_path(bone):
    return 'pose.bones["%s"].location' % bone


def key_frames(curves):
    return sorted({round(k.co[0]) for fc in curves.values() for k in fc.keyframe_points})


def read_quats(curves, frames):
    return [Quaternion([curves[i].evaluate(f) for i in range(4)]).normalized() for f in frames]


def write_values(curves, frames, values):
    """Keys at `frames` with `values` (lists per frame, one value per array index), replacing the curve's keys."""
    for i, fc in curves.items():
        fc.keyframe_points.clear()
        fc.keyframe_points.add(len(frames))
        for k, f, v in zip(fc.keyframe_points, frames, values):
            k.co = (f, v[i])
            k.interpolation = 'BEZIER'
            k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
        fc.update()


def continuous(quats):
    """The same turns, each in the hemisphere of the one before (no flip between keys)."""
    out = []
    for q in quats:
        q = q.copy()
        if out and out[-1].dot(q) < 0:
            q.negate()
        out.append(q)
    return out


def tidy(rig, action):
    """Removes the curves of bones the rig has not, the bones' scale and every location but the hips'."""
    names = {b.name for b in rig.data.bones}
    removed = 0
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in list(bag.fcurves):
                    path = fc.data_path
                    bone = path.split('"')[1] if path.startswith('pose.bones["') else None
                    if bone is None or bone not in names or path.endswith('.scale') or \
                            (path.endswith('.location') and bone != P + 'Hips'):
                        bag.fcurves.remove(fc)
                        removed += 1
    return removed


# Time -----------------------------------------------------------------------------------------------------------------

def time_map(anchors):
    """Source frame for every clip frame 1..N: a monotone cubic through the anchors (Fritsch-Carlson), so the speed
    changes smoothly at each anchor."""
    x = np.array([a[1] for a in anchors], dtype=float)
    y = np.array([a[0] for a in anchors], dtype=float)
    h = np.diff(x)
    d = np.diff(y) / h
    m = np.zeros_like(x)
    m[0], m[-1] = d[0], d[-1]
    for k in range(1, len(x) - 1):
        m[k] = 0.0 if d[k - 1] * d[k] <= 0 else 3 * (h[k - 1] + h[k]) / ((2 * h[k] + h[k - 1]) / d[k - 1] +
                                                                         (h[k] + 2 * h[k - 1]) / d[k])
    out = []
    for f in range(1, int(x[-1]) + 1):
        k = min(max(int(np.searchsorted(x, f, side='right')) - 1, 0), len(x) - 2)
        t = (f - x[k]) / h[k]
        h00, h10, h01, h11 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t, -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
        out.append(float(h00 * y[k] + h10 * h[k] * m[k] + h01 * y[k + 1] + h11 * h[k] * m[k + 1]))
    return out


def resample(action, times):
    """Every curve of `action` keyed at clip frames 1..len(times) with its value at source frame times[i]; the
    rotations normalised."""
    frames = list(range(1, len(times) + 1))
    for path, curves in curves_of(action).items():
        values = [[curves[i].evaluate(t) if i in curves else 0.0 for i in range(max(curves) + 1)] for t in times]
        if path.endswith('rotation_quaternion') and len(curves) == 4:
            quats = continuous([Quaternion(v).normalized() for v in values])
            values = [list(q) for q in quats]
        write_values(curves, frames, values)
    return frames


# Joint limits ---------------------------------------------------------------------------------------------------------

def _rotvec(q):
    axis, angle = q.to_axis_angle()
    if angle > math.pi:
        angle -= 2 * math.pi
    return np.array(axis) * math.degrees(angle)


def _soft(v, low, high):
    """`v` squeezed into (low, high): unchanged inside, approaching the limit smoothly over the last SOFT degrees."""
    k = min(SOFT, 0.25 * (high - low))
    high, low = high - SOFT_MARGIN, low + SOFT_MARGIN
    top, bottom = high - k, low + k
    return np.where(v > top, top + k * np.tanh((v - top) / k), np.where(v < bottom, bottom - k * np.tanh((bottom - v) / k), v))


def _turns(rig, curves, bone):
    rest = rig.data.bones[bone].matrix_local.to_quaternion()
    frames = key_frames(curves)
    return rest, frames, np.array([_rotvec(rest @ q @ rest.inverted()) for q in read_quats(curves, frames)])


def _write_turns(curves, rest, frames, turns):
    out = []
    for r in turns:
        angle = float(np.linalg.norm(r))
        qa = Quaternion(Vector(r / angle), math.radians(angle)) if angle > 1e-9 else Quaternion()
        out.append(rest.inverted() @ qa @ rest)
    write_values(curves, frames, [list(q) for q in continuous(out)])


def pass_on(rig, action, limits):
    """The part of each PASS_ON bone's turn beyond its limits, axis by axis, moved to the next bone (head -> neck):
    the dazed head of Stunned nods 44 degrees, more than the head alone may. Returns {bone: {axis: largest moved}}."""
    by_path = curves_of(action)
    done = {}
    for a, b in PASS_ON:
        for side in ('',):
            src, dst = P + side + a, P + side + b
            if src not in limits or rot_path(src) not in by_path or rot_path(dst) not in by_path:
                continue
            rest_a, frames, ta = _turns(rig, by_path[rot_path(src)], src)
            rest_b, frames_b, tb = _turns(rig, by_path[rot_path(dst)], dst)
            if frames != frames_b:
                continue
            moved = {}
            for axis, (low, high) in limits[src].items():
                if axis not in motion_profile.AXES:
                    continue
                k = motion_profile.AXES.index(axis)
                excess = ta[:, k] - np.clip(ta[:, k], low, high)
                if np.abs(excess).max() > 1e-6:
                    ta[:, k] -= excess
                    tb[:, k] += excess
                    moved[axis] = round(float(np.abs(excess).max()), 1)
            if moved:
                _write_turns(by_path[rot_path(src)], rest_a, frames, ta)
                _write_turns(by_path[rot_path(dst)], rest_b, frames, tb)
                done[src] = moved
    return done


def limit_axes(rig, action, limits, bones=None):
    """Brings every bone of `limits` ({bone: {axis: (min, max)}}, motion_profile.joint_limits) keyed in `action`
    within its limits about the axes of the T-pose; `bones` - only these. Returns {bone: {axis: [how, before, after]}}."""
    curves_by_path = curves_of(action)
    done = {}
    for bone, lim in limits.items():
        if bones is not None and bone not in bones:
            continue
        axes = {a: r for a, r in lim.items() if a in motion_profile.AXES}
        curves = curves_by_path.get(rot_path(bone))
        if not axes or not curves or len(curves) < 4 or bone not in rig.data.bones:
            continue
        rest = rig.data.bones[bone].matrix_local.to_quaternion()
        frames = key_frames(curves)
        quats = read_quats(curves, frames)
        turns = np.array([_rotvec(rest @ q @ rest.inverted()) for q in quats])
        changed = {}
        for axis, (low, high) in axes.items():
            k = motion_profile.AXES.index(axis)
            v = turns[:, k]
            lo, hi = float(v.min()), float(v.max())
            if lo >= low and hi <= high:
                continue
            short = bone[len(P):].replace('Left', '').replace('Right', '')
            if any(short.startswith(s) for s in SHIFT_BONES) and hi - lo <= SHIFT_FIT * (high - low):
                shift = (high - SHIFT_MARGIN - hi) if hi > high else (low + SHIFT_MARGIN - lo)
                turns[:, k] = v + shift
                how = 'shift %.1f' % shift
            else:
                turns[:, k] = _soft(v, low, high)
                how = 'soft'
            changed[axis] = [how, [round(lo, 1), round(hi, 1)],
                             [round(float(turns[:, k].min()), 1), round(float(turns[:, k].max()), 1)]]
        if not changed:
            continue
        _write_turns(curves, rest, frames, turns)
        done[bone] = changed
    return done


# Poses ----------------------------------------------------------------------------------------------------------------

def pose_at(rig, action, frame):
    """{bone: (rotation, location)} and the feet {side: (ankle, world turn, toe rotation, knee side)} at `frame` of
    `action`; the knee side is where the knee points off the hip-ankle line, in the pelvis' rest frame."""
    rig.animation_data.action = action
    bpy.context.scene.frame_set(frame)
    bones = rig.pose.bones
    pose = {pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in bones}
    turned = pelvis_turn(rig)
    feet = {}
    for s in SIDES:
        hip, knee, ankle = (bones[P + s + b].head.copy() for b in clip_polish.LEG)
        axis = (ankle - hip).normalized()
        side = knee - (hip + axis * (knee - hip).dot(axis))
        feet[s] = (ankle, bones[P + s + 'Foot'].matrix.to_quaternion(), bones[P + s + 'ToeBase'].rotation_quaternion.copy(),
                   turned.inverted() @ side.normalized())
    rig.animation_data.action = None
    return pose, feet


def pelvis_turn(rig):
    """The pelvis' turn from rest, world space (3 x 3)."""
    pelvis = rig.pose.bones[P + 'Hips']
    return pelvis.matrix.to_3x3() @ pelvis.bone.matrix_local.to_3x3().inverted()


def reset_pose(rig):
    """Rest pose without an action: rotation, location and scale of every pose bone (solving a leg by its matrix
    leaves a float step of scale, BUG-20261025-002, and a location the next clip would inherit)."""
    rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def ramp(frames, first, last, rising=True):
    """Cosine weights over `frames`: 0 before `first`, 1 after `last` (or the other way round)."""
    out = []
    for f in frames:
        t = min(max((f - first) / max(last - first, 1), 0.0), 1.0)
        w = 0.5 - 0.5 * math.cos(math.pi * t)
        out.append(w if rising else 1.0 - w)
    return out


def smooth_keys(action, bones, passes):
    """[1, 2, 1] / 4 over the keys of the rotations of `bones`, `passes` times; the first and last keys stay."""
    for bone in bones:
        curves = curves_of(action).get(rot_path(bone))
        if not curves:
            continue
        frames = key_frames(curves)
        q = np.array([list(v) for v in continuous(read_quats(curves, frames))])
        for _ in range(passes):
            q[1:-1] = (q[:-2] + 2 * q[1:-1] + q[2:]) / 4.0
        write_values(curves, frames, [list(Quaternion(v).normalized()) for v in q])


def blend_to(action, pose, weights, bones=None, rotation_only=False):
    """Every rotation (and the hips' location) of `action` blended toward `pose` by weights[frame index]."""
    for path, curves in curves_of(action).items():
        bone = path.split('"')[1]
        if bone not in pose or (bones is not None and bone not in bones):
            continue
        frames = key_frames(curves)
        if path.endswith('rotation_quaternion') and len(curves) == 4:
            target = pose[bone][0]
            out = []
            for q, w in zip(read_quats(curves, frames), weights):
                t = target.copy()
                if q.dot(t) < 0:
                    t.negate()
                out.append(q.slerp(t, w))
            write_values(curves, frames, [list(q) for q in continuous(out)])
        elif path.endswith('.location') and not rotation_only:
            target = pose[bone][1]
            values = [[curves[i].evaluate(f) * (1 - w) + target[i] * w if i in curves else 0.0 for i in range(3)]
                      for f, w in zip(frames, weights)]
            write_values(curves, frames, values)


# X Bot ----------------------------------------------------------------------------------------------------------------

def xbot_legs(fbx, times):
    """X Bot of the FBX: its left hip height at rest and, at each source time, the world hip, knee and ankle of both
    legs (clip_polish.source_legs at the clip's own timing). What the FBX brought is removed again."""
    scene = bpy.context.scene
    before, actions = set(bpy.data.objects), set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    new = [ob for ob in bpy.data.objects if ob not in before]
    arm = next(ob for ob in new if ob.type == 'ARMATURE')
    height = (arm.matrix_world @ arm.data.bones[P + 'LeftUpLeg'].head_local).z
    sample = []
    for t in times:
        scene.frame_set(int(math.floor(t)), subframe=t - math.floor(t))
        sample.append({s: [(arm.matrix_world @ arm.pose.bones[P + s + b].head).copy() for b in clip_polish.LEG]
                       for s in SIDES})
    for ob in new:
        data = ob.data
        bpy.data.objects.remove(ob)
        if data is not None and data.users == 0:
            (bpy.data.armatures if isinstance(data, bpy.types.Armature) else bpy.data.meshes).remove(data)
    for old in [a for a in bpy.data.actions if a not in actions and a.users == 0]:
        bpy.data.actions.remove(old)
    return height, sample


# Legs of a one-shot clip ------------------------------------------------------------------------------------------------

def hips_lower(rig, action, targets, frames):
    """Lowers the hips where a leg would have to stretch beyond REACH of its length to its target: one drop per
    frame, widened over three frames each side and smoothed (no kink). Returns the largest drop in metres."""
    bones = rig.pose.bones
    rig.animation_data.action = action
    drops = []
    for i, f in enumerate(frames):
        bpy.context.scene.frame_set(f)
        need = 0.0
        for s in SIDES:
            up, leg = bones[P + s + 'UpLeg'], bones[P + s + 'Leg']
            allowed = REACH * (up.length + leg.length)
            hip, target = up.head, targets[s][i]
            flat = (hip - target).to_2d().length
            if flat >= allowed:
                need = max(need, hip.z - target.z)
                continue
            height = math.sqrt(allowed * allowed - flat * flat)
            need = max(need, (hip.z - target.z) - height)
        drops.append(need)
    rig.animation_data.action = None
    d = np.array(drops)
    n = len(d)
    wide = np.array([d[max(0, i - 3):i + 4].max() for i in range(n)])
    for _ in range(6):
        wide = np.maximum(wide, np.convolve(np.pad(wide, 1, mode='edge'), [0.25, 0.5, 0.25], mode='valid'))
        wide = np.convolve(np.pad(wide, 1, mode='edge'), [0.25, 0.5, 0.25], mode='valid')
    if wide.max() <= 0:
        return 0.0
    curves = curves_of(action)[loc_path(P + 'Hips')]
    rest = rig.data.bones[P + 'Hips'].matrix_local.to_3x3().inverted()
    values = []
    for f, drop in zip(frames, wide):
        local = rest @ Vector((0.0, 0.0, -float(drop)))
        values.append([curves[i].evaluate(f) + local[i] for i in range(3)])
    write_values(curves, frames, values)
    return round(float(wide.max()), 4)


def _foot_pitch(rig, side):
    """The foot's turn from rest about the T-pose X axis, degrees (as anim_check.py measures the limit)."""
    foot = rig.pose.bones[P + side + 'Foot']
    rest = foot.bone.matrix_local.to_quaternion()
    return float(_rotvec(rest @ foot.matrix_basis.to_quaternion() @ rest.inverted())[0])


def _solve_leg(rig, side, target, bend):
    """Thigh and shin of `side` so the ankle reaches `target`, the knee toward `bend`; the foot's world turn kept."""
    bones = rig.pose.bones
    up, leg, foot = (bones[P + side + b] for b in clip_polish.LEG)
    foot_world = foot.matrix.to_quaternion()
    hip = up.head.copy()
    a, b = up.length, leg.length
    reach = target - hip
    d = min(reach.length, (a + b) * 0.9999)
    axis = reach.normalized()
    bend = bend - axis * bend.dot(axis)
    bend.normalize()
    along = (a * a - b * b + d * d) / (2 * d)
    knee = hip + axis * along + bend * max(a * a - along * along, 0.0) ** 0.5
    for pb, start, end in ((up, hip, knee), (leg, knee, hip + axis * d)):
        current = (pb.tail - pb.head).normalized()
        turn = current.rotation_difference((end - start).normalized()).to_matrix().to_4x4()
        m = pb.matrix.copy()
        pb.matrix = Matrix.Translation(start) @ turn @ Matrix.Translation(-m.translation) @ m
        bpy.context.view_layer.update()
    foot.matrix = Matrix.Translation(foot.head) @ foot_world.to_matrix().to_4x4()
    bpy.context.view_layer.update()


def heel_lift(rig, side, target):
    """A planted foot whose shin leans further than FOOT_PITCH over it lifts its heel about the ball of the foot (the
    toe bone's joint), the ankle rising with it: a boot kept flat under a leaning shin bent the ankle 47 degrees.
    Returns the lift in degrees."""
    pitch = _foot_pitch(rig, side)
    if pitch >= FOOT_PITCH:
        return 0.0
    bones = rig.pose.bones
    foot, toe, leg = bones[P + side + 'Foot'], bones[P + side + 'ToeBase'], bones[P + side + 'Leg']
    lateral = (pelvis_turn(rig) @ Vector((1.0, 0.0, 0.0))).normalized()
    need = FOOT_PITCH - pitch
    best = None
    for sign in (1.0, -1.0):
        r = Matrix.Rotation(math.radians(sign * need), 3, lateral)
        ball, ankle = toe.head.copy(), foot.head.copy()
        new_ankle = ball + r @ (ankle - ball)
        if best is None or new_ankle.z > best[1].z:
            best = (r, new_ankle)
    r, new_ankle = best
    knee_side = leg.head - (bones[P + side + 'UpLeg'].head + (target - bones[P + side + 'UpLeg'].head).normalized() *
                            (leg.head - bones[P + side + 'UpLeg'].head).dot((target - bones[P + side + 'UpLeg'].head).normalized()))
    turn = (r @ foot.matrix.to_3x3()).to_4x4()
    foot.matrix = Matrix.Translation(foot.head) @ turn
    bpy.context.view_layer.update()
    _solve_leg(rig, side, new_ankle, knee_side)
    return need


def plant_once(rig, action, frames, sample, targets, flat, idle_feet):
    """Two-bone IK on every frame (clip_polish.plant_feet's solve): each ankle to its target, the knee in X Bot's knee
    plane and at most KNEE_LIMIT (the knee where Idle's points, turned with the pelvis: X Bot's stepping knee turned
    the thigh inward), the
    foot keeping its world turn from the clip, turned flat as at Idle by `flat`; the toe blended to Idle's by `flat`
    too. Returns the largest ankle correction in metres."""
    bones = rig.pose.bones
    rig.animation_data.action = action
    largest = 0.0
    for i, frame in enumerate(frames):
        bpy.context.scene.frame_set(frame)
        for s in SIDES:
            up, leg, foot = (bones[P + s + b] for b in clip_polish.LEG)
            toe = bones[P + s + 'ToeBase']
            target = targets[s][i]
            foot_world = foot.matrix.copy()
            hip = up.head.copy()
            a, b = up.length, leg.length
            reach = target - hip
            d_min = (a * a + b * b - 2 * a * b * math.cos(math.radians(180.0 - KNEE_LIMIT))) ** 0.5
            d = min(max(reach.length, d_min), (a + b) * 0.9999)
            largest = max(largest, (foot.head - target).length)
            axis = reach.normalized()
            bend = pelvis_turn(rig) @ idle_feet[s][3]
            bend = bend - axis * bend.dot(axis)
            if bend.length < 1e-6:
                bend = (leg.head - hip) - axis * (leg.head - hip).dot(axis)
            bend.normalize()
            along = (a * a - b * b + d * d) / (2 * d)
            knee = hip + axis * along + bend * max(a * a - along * along, 0.0) ** 0.5
            for pb, start, end in ((up, hip, knee), (leg, knee, hip + axis * d)):
                current = (pb.tail - pb.head).normalized()
                turn = current.rotation_difference((end - start).normalized()).to_matrix().to_4x4()
                m = pb.matrix.copy()
                pb.matrix = Matrix.Translation(start) @ turn @ Matrix.Translation(-m.translation) @ m
                bpy.context.view_layer.update()
            turn = foot_world.to_quaternion()
            w = flat[s][i]
            if w:
                idle_turn = idle_feet[s][1].copy()
                if turn.dot(idle_turn) < 0:
                    idle_turn.negate()
                turn = turn.slerp(idle_turn, w)
            foot.matrix = Matrix.Translation(foot.head) @ turn.to_matrix().to_4x4()
            bpy.context.view_layer.update()
            heel_lift(rig, s, target)
            if w:
                t = idle_feet[s][2].copy()
                if toe.rotation_quaternion.dot(t) < 0:
                    t.negate()
                toe.rotation_quaternion = toe.rotation_quaternion.slerp(t, w)
            for pb in (up, leg, foot, toe):
                pb.keyframe_insert('rotation_quaternion', frame=frame)
    rig.animation_data.action = None
    return round(largest, 4)


def pin_stances(path, speed=0.2):
    """A foot standing (moving slower than `speed` m/s along the floor) stays where its stance began; each swing
    is bent to go from one pinned place to the next. X Bot's zombie feet creep 8 cm while they stand."""
    n = len(path)
    v = [(path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).to_2d().length * FPS / 2.0 for i in range(n)]
    stand = [x < speed for x in v]
    anchor = [None] * n
    i = 0
    while i < n:
        if stand[i]:
            j = i
            while j < n and stand[j]:
                j += 1
            place = path[i].copy()
            for k in range(i, j):
                anchor[k] = Vector((place.x, place.y, path[k].z))
            i = j
        else:
            i += 1
    out = [p.copy() for p in path]
    i = 0
    while i < n:
        if anchor[i] is not None:
            out[i] = anchor[i]
            i += 1
            continue
        j = i
        while j < n and anchor[j] is None:
            j += 1
        a = i - 1
        da = (anchor[a] - path[a]) if a >= 0 else Vector()
        db = (anchor[j] - path[j]) if j < n else da
        for k in range(i, j):
            u = (k - a) / (j - a) if j < n and a >= 0 else 0.0
            u = u * u * (3 - 2 * u)   # eased: a straight blend jolted the leg where the stance ends
            shift = da * (1 - u) + db * u
            out[k] = path[k] + Vector((shift.x, shift.y, 0.0))
        i = j
    return out


def once_clip(rig, body, name, spec, idle, limits):
    """A one-shot clip from Idle to Idle (see the module's notes); returns its report."""
    fbx = MIXAMO / SOURCES[name]
    times = time_map(spec['anchors'])
    height, sample = xbot_legs(fbx, times)
    factor = rig.data.bones[P + 'LeftUpLeg'].head_local.z / height
    old = bpy.data.actions.get(name)
    if old is not None:
        bpy.data.actions.remove(old)
    action = biped_rig.import_mixamo_clip(rig, fbx, name)
    rig.animation_data.action = None
    report = {'source': fbx.name, 'removed_curves': tidy(rig, action)}
    clip_polish.scale_hips(action, factor)
    report['hips_scale'] = round(factor, 4)
    report['pass_on'] = pass_on(rig, action, limits)
    report['turn_limits'] = limit_axes(rig, action, limits)
    frames = resample(action, times)
    n = len(frames)
    report['timing'] = {'anchors': spec['anchors'], 'frames': n, 'seconds': round((n - 1) / FPS, 3)}
    idle_pose, idle_feet = idle
    # The hips along the floor at most spec['hips'][0] off their start, their rise and fall times spec['hips'][1]
    # (the Hit stands its ground; the Attack steps in, it does not lunge 0.56 m).
    hips = curves_of(action)[loc_path(P + 'Hips')]
    if spec['hips'] is not None:
        reach, rise, sideways = spec['hips']
        rest = rig.data.bones[P + 'Hips'].matrix_local.to_3x3()
        local = [Vector([hips[i].evaluate(f) for i in range(3)]) for f in frames]
        world = [rest @ v for v in local]
        start = world[0].copy()
        off = [Vector(((w.x - start.x) * sideways, w.y - start.y, 0.0)) for w in world]
        top = max(o.length for o in off)
        k = min(1.0, reach / top) if top > 1e-6 else 1.0
        # From Idle's place: the zombie stands 0.12 m to the side and lower, and the blend into it swung the pelvis
        # over the standing left leg.
        base = rest @ idle_pose[P + 'Hips'][1]
        values = [list(rest.inverted() @ (base + o * k + Vector((0.0, 0.0, (w.z - start.z) * rise))))
                  for w, o in zip(world, off)]
        write_values(hips, frames, values)
        report['hips_travel'] = {'source_m': round(top, 3), 'kept': round(k, 3), 'rise_kept': rise,
                                 'sideways_kept': sideways}
    if spec.get('hips_turn', 1.0) < 1.0:
        blend_to(action, {P + 'Hips': (idle_pose[P + 'Hips'][0], None)}, [1.0 - spec['hips_turn']] * n,
                 {P + 'Hips'}, rotation_only=True)
    if spec.get('smooth'):
        smooth_keys(action, [P + s + b for s in SIDES for b in ('Shoulder', 'Arm', 'ForeArm', 'Hand')] +
                    [P + b for b in ('Spine2', 'Neck', 'Head')], spec['smooth'])
    w_in = ramp(frames, 1, 1 + spec['blend_in'], rising=False)
    w_out = ramp(frames, n - spec['blend_out'], n)
    if spec['arms_out']:
        arms = {P + s + b for s in SIDES for b in ('Shoulder', 'Arm', 'ForeArm', 'Hand')}
        blend_to(action, idle_pose, ramp(frames, *spec['arms_out']), arms)
    blend_to(action, idle_pose, [max(a, b) for a, b in zip(w_in, w_out)])
    # The feet: Idle's stance plus X Bot's steps (spec['feet'] of them), back on Idle's at the end.
    targets, flat = {}, {}
    for s in SIDES:
        base = idle_feet[s][0]
        first = sample[0][s][2]
        path = []
        for i in range(n):
            step = (sample[i][s][2] - first) * factor * spec['feet'] * (1.0 - w_out[i])
            step.x = 0.0   # steps go fore and aft only: X Bot's foot crossing under the body rolled the boot 34 degrees
            path.append(base + step)
        path = pin_stances(path)
        # A foot moving along the floor rises: up to spec['lift'] from 0.05 to 0.25 m/s (clip_polish.plant_feet's ramp).
        speeds = [(path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).to_2d().length * FPS / 2.0 for i in range(n)]
        rise = np.array([min(max((v - 0.05) / 0.20, 0.0), 1.0) for v in speeds])
        for _ in range(3):
            rise = np.convolve(np.pad(rise, 1, mode='edge'), [0.25, 0.5, 0.25], mode='valid')
        targets[s] = [p + Vector((0.0, 0.0, spec['lift'] * float(r))) for p, r in zip(path, rise)]
        # The boots stay level as at Idle: X Bot's foot turns rolled the Grinch's wide boot 40 degrees.
        flat[s] = [1.0] * n
    report['hips_drop'] = hips_lower(rig, action, targets, frames)
    report['ankle_fix'] = plant_once(rig, action, frames, sample, targets, flat, idle_feet)
    report['turn_limits_after_ik'] = limit_axes(rig, action, limits,
                                                [b for b in limits if not any(x in b for x in LEG_BONES)])
    report['floor_fix'] = clip_polish.floor_lift(rig, body, action)
    action.use_cyclic = False
    action.use_fake_user = True
    return action, report


def settle(rig, body, action, fbx, drop, spec, foot_drop):
    """After polish: the hips `drop` metres lower and the legs solved again (clip_polish.plant_feet and the steps after
    it in polish): on the Grinch's legs X Bot's stride pulled the leg straight (the knee snapped)."""
    height, rest_source, sample = clip_polish.source_legs(fbx)
    factor = rig.data.bones[P + 'LeftUpLeg'].head_local.z / height
    local = rig.data.bones[P + 'Hips'].matrix_local.to_3x3().inverted() @ Vector((0.0, 0.0, -drop))
    for fc in studio_scene.action_fcurves(action):
        if fc.data_path == loc_path(P + 'Hips'):
            for key in fc.keyframe_points:
                key.co[1] += local[fc.array_index]
                key.handle_left[1] += local[fc.array_index]
                key.handle_right[1] += local[fc.array_index]
            fc.update()
    clip_polish.close_sample_loop(sample)
    legs = {'lift': spec.get('lift', 0.0), 'window': spec.get('window', 0), 'prefix': P,
            'drop': foot_drop if max(foot_drop.values()) > 0.003 else None}
    fix = clip_polish.plant_feet(rig, action, sample, rest_source, factor, **legs)
    clip_polish.smooth_turns(action)
    clip_polish.close_loop(action, [s + b for s in SIDES for b in clip_polish.LEG_SEAM_BONES], 6, 4, P)
    return {'drop': drop, 'ankle_fix': fix, 'floor_fix': clip_polish.floor_lift(rig, body, action)}


def pin_soles(rig, body, action, contact=CONTACT, edge=5):
    """An in-place cycle: while a sole is on the floor (its lowest point under `contact`) its middle goes back at one
    floor speed, the median of both soles' speeds on the floor (anim_check.py measures the slide so); the whole foot
    is moved by the difference, blended out over `edge` frames, and the leg solved again from the hip with its knee in
    the same plane and the foot's world turn kept. On the Grinch's long boots X Bot's heel roll slid the toe back 17 cm
    in each push-off. Returns the largest move in metres."""
    rig.animation_data.action = action
    first, last = (int(f) for f in action.frame_range)
    ring = list(range(first, last))   # Mixamo's loop: the last frame repeats the first
    n = len(ring)
    ids = {s: clip_polish._sole_ids(rig, body, s, P) for s in SIDES}
    centre, low = {s: [] for s in SIDES}, {s: [] for s in SIDES}
    for f in ring:
        bpy.context.scene.frame_set(f)
        pts = clip_polish.evaluated(body)
        for s in SIDES:
            sole = [pts[i] for i in ids[s]]
            centre[s].append(sum((p.to_2d() for p in sole), Vector((0.0, 0.0))) / len(sole))
            low[s].append(min(p.z for p in sole))
    down = {s: [h < contact for h in low[s]] for s in SIDES}
    # A stance is at least MIN_STANCE frames (the swagger's swinging toe dips to the floor for a frame or two: it is
    # raised, not pinned) and goes on one frame past the last on the floor, so the foot leaves at the floor's speed.
    for s in SIDES:
        runs, i = [], 0
        marks = down[s]
        if all(marks):
            continue
        start = next(i for i in range(n) if not marks[i])
        i = 0
        while i < n:
            j = (start + i) % n
            if marks[j]:
                k = i
                while k < n and marks[(start + k) % n]:
                    k += 1
                runs.append([(start + m) % n for m in range(i, k)])
                i = k
            else:
                i += 1
        kept = [False] * n
        for run in runs:
            if len(run) >= MIN_STANCE:
                for j in run + [(run[-1] + 1) % n]:
                    kept[j] = True
        down[s] = kept
    speeds = [(centre[s][(i + 1) % n] - centre[s][i]) * FPS for s in SIDES for i in range(n)
              if down[s][i] and down[s][(i + 1) % n]]
    ground = Vector((float(np.median([v.x for v in speeds])), float(np.median([v.y for v in speeds]))))
    delta = {}
    for s in SIDES:
        d = [Vector((0.0, 0.0)) for _ in range(n)]
        weight = [0.0] * n
        starts = [i for i in range(n) if down[s][i] and not down[s][i - 1]]
        for i0 in starts:
            run = [i0]
            while down[s][(run[-1] + 1) % n] and len(run) < n:
                run.append((run[-1] + 1) % n)
            # The run anchored so its mean error is nought: the foot keeps its average place.
            offset = sum((centre[s][i] - ground * (k / FPS) for k, i in enumerate(run)), Vector((0.0, 0.0))) / len(run)
            for k, i in enumerate(run):
                d[i] = offset + ground * (k / FPS) - centre[s][i]
                weight[i] = 1.0
            for j in range(1, edge + 1):
                w = 0.5 + 0.5 * math.cos(math.pi * j / (edge + 1))
                for i, src in (((run[-1] + j) % n, run[-1]), ((run[0] - j) % n, run[0])):
                    if weight[i] < w:
                        d[i], weight[i] = d[src] * w, w
        # The swing clears the floor: a foot two frames or more off its stance stays CLEAR over its lowest point.
        rise = []
        for i in range(n):
            near = any(down[s][(i + j) % n] for j in (-2, -1, 0, 1, 2))
            rise.append(0.0 if near else max(0.0, CLEAR - low[s][i]))
        for _ in range(2):
            rise = [(rise[i - 1] + 2 * rise[i] + rise[(i + 1) % n]) / 4.0 for i in range(n)]
        delta[s] = [Vector((v.x, v.y, r)) for v, r in zip(d, rise)]
    bones = rig.pose.bones
    largest = 0.0
    for k, f in enumerate(ring + [last]):
        i = k % n
        bpy.context.scene.frame_set(f)
        for s in SIDES:
            shift = delta[s][i]
            largest = max(largest, shift.length)
            up, leg, foot = (bones[P + s + b] for b in clip_polish.LEG)
            hip, knee, ankle = up.head.copy(), leg.head.copy(), foot.head.copy()
            foot_world = foot.matrix.to_quaternion()
            target = ankle + shift
            a, b = up.length, leg.length
            reach = target - hip
            d = min(reach.length, (a + b) * 0.9999)
            axis = reach.normalized()
            bend = knee - (hip + axis * (knee - hip).dot(axis))
            if bend.length < 1e-6:
                bend = Vector((0.0, -1.0, 0.0)) - axis * -axis.y
            bend.normalize()
            along = (a * a - b * b + d * d) / (2 * d)
            new_knee = hip + axis * along + bend * max(a * a - along * along, 0.0) ** 0.5
            for pb, start, end in ((up, hip, new_knee), (leg, new_knee, hip + axis * d)):
                current = (pb.tail - pb.head).normalized()
                turn = current.rotation_difference((end - start).normalized()).to_matrix().to_4x4()
                m = pb.matrix.copy()
                pb.matrix = Matrix.Translation(start) @ turn @ Matrix.Translation(-m.translation) @ m
                bpy.context.view_layer.update()
            foot.matrix = Matrix.Translation(foot.head) @ foot_world.to_matrix().to_4x4()
            bpy.context.view_layer.update()
            for pb in (up, leg, foot):
                pb.keyframe_insert('rotation_quaternion', frame=f)
    rig.animation_data.action = None
    return {'ground_speed': [round(ground.x, 3), round(ground.y, 3)], 'largest_move': round(largest, 4)}


def cycle_clip(rig, body, name, limits):
    action, report = clip_polish.polish(rig, body, MIXAMO / SOURCES[name], name, **CYCLES[name])
    report = {'source': SOURCES[name], **report}
    if SETTLE.get(name):
        report['settle'] = settle(rig, body, action, MIXAMO / SOURCES[name], SETTLE[name], CYCLES[name],
                                  report['foot_drop'])
    if name in PIN_SOLES:
        report['pin_soles'] = pin_soles(rig, body, action)
        # One [1, 2, 1] pass over the legs: the lift-off after the pinned stance jolted the thigh (12 deg/frame^2).
        clip_polish.smooth_turns(action, [P + s + b for s in SIDES for b in ('UpLeg', 'Leg')], 1, '')
        clip_polish.close_loop(action, [s + b for s in SIDES for b in clip_polish.LEG_SEAM_BONES], 6, 4, P)
    report['removed_curves'] = tidy(rig, action)
    report['pass_on'] = pass_on(rig, action, limits)
    report['turn_limits'] = limit_axes(rig, action, limits, [b for b in limits if 'ToeBase' in b or
                                                             not any(x in b for x in LEG_BONES)])
    report['floor_fix_after_limits'] = clip_polish.floor_lift(rig, body, action)
    return action, report


def seated_clip(rig, body, name, limits):
    """Stunned: hips scale, joint limits, loop seam; the lowest point of the clip on the floor."""
    fbx = MIXAMO / SOURCES[name]
    height, _, _ = clip_polish.source_legs(fbx)
    factor = rig.data.bones[P + 'LeftUpLeg'].head_local.z / height
    old = bpy.data.actions.get(name)
    if old is not None:
        bpy.data.actions.remove(old)
    action = biped_rig.import_mixamo_clip(rig, fbx, name)
    rig.animation_data.action = None
    report = {'source': fbx.name, 'removed_curves': tidy(rig, action)}
    clip_polish.scale_hips(action, factor)
    report['hips_scale'] = round(factor, 4)
    report['pass_on'] = pass_on(rig, action, limits)
    report['turn_limits'] = limit_axes(rig, action, limits)
    clip_polish.close_loop(action)
    action.use_cyclic = True
    action.use_fake_user = True
    # Seated: one shift of the hips so the lowest point of the mesh over the clip is SEATED_DEPTH under the floor.
    rig.animation_data.action = action
    first, last = (int(f) for f in action.frame_range)
    lowest = 9.0
    for frame in range(first, last + 1):
        bpy.context.scene.frame_set(frame)
        lowest = min(lowest, min(v.z for v in clip_polish.evaluated(body)))
    rig.animation_data.action = None
    shift = -SEATED_DEPTH - lowest
    local = rig.data.bones[P + 'Hips'].matrix_local.to_3x3().inverted() @ Vector((0.0, 0.0, shift))
    for fc in studio_scene.action_fcurves(action):
        if fc.data_path == loc_path(P + 'Hips'):
            for key in fc.keyframe_points:
                key.co[1] += local[fc.array_index]
                key.handle_left[1] += local[fc.array_index]
                key.handle_right[1] += local[fc.array_index]
            fc.update()
    report['floor_shift'] = round(shift, 4)
    return action, report


def write_modes(path):
    """The clip modes into the motion profile, its other parts kept."""
    profile = json.loads(Path(path).read_text(encoding='utf-8'))
    profile['clips'] = CLIP_MODES
    motion_profile.check(profile)
    Path(path).write_text(json.dumps(profile, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main(argv):
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--out')
    ap.add_argument('--backup', default=str(Path(tempfile.gettempdir()) / 'Grinch_master.before-clips.blend'))
    a = ap.parse_args(argv)
    source = bpy.data.filepath
    out = a.out or source
    shutil.copy2(source, a.backup)
    scene = bpy.context.scene
    scene.render.fps, scene.render.fps_base = FPS, 1.0
    rig, body = bpy.data.objects[RIG], bpy.data.objects[BODY]
    write_modes(PROFILE)
    limits = motion_profile.joint_limits(motion_profile.load(PROFILE))
    report = {'fps': FPS, 'clips': {}}
    for name in ('Idle', 'Walk'):
        reset_pose(rig)
        _, report['clips'][name] = cycle_clip(rig, body, name, limits)
    reset_pose(rig)
    idle = pose_at(rig, bpy.data.actions['Idle'], 1)
    for name, spec in ONCE.items():
        reset_pose(rig)
        _, report['clips'][name] = once_clip(rig, body, name, spec, idle, limits)
    reset_pose(rig)
    _, report['clips']['Stunned'] = seated_clip(rig, body, 'Stunned', limits)
    for name, clip in report['clips'].items():
        action = bpy.data.actions[name]
        first, last = (int(f) for f in action.frame_range)
        clip.update({'frames': [first, last], 'seconds': round((last - first) / FPS, 3), 'cyclic': action.use_cyclic,
                     'mode': CLIP_MODES[name]})
    reset_pose(rig)
    idle_range = bpy.data.actions['Idle'].frame_range
    scene.frame_start, scene.frame_end = int(idle_range[0]), int(idle_range[1])
    scene.frame_set(1)
    bpy.context.preferences.filepaths.save_version = 0   # no .blend1 next to the master
    bpy.ops.wm.save_as_mainfile(filepath=out)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for name, clip in report['clips'].items():
        print('GRINCH_CLIP %s frames=%s seconds=%s cyclic=%s' % (name, clip['frames'], clip['seconds'], clip['cyclic']))
    print('GRINCH_CLIPS backup=%s saved=%s' % (a.backup, out))


if __name__ == '__main__':
    main(sys.argv)
