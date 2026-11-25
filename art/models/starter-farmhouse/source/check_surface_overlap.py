"""Detect overlapping parallel triangles in the saved model, including partial overlaps."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import bpy


def cross(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def shared_area(first, second):
    # Clip the first triangle by all three inside half-planes of the second.
    sign = 1 if cross(*second) > 0 else -1
    points = first
    for a, b in zip(second, second[1:] + second[:1]):
        clipped = []
        for p, q in zip(points, points[1:] + points[:1]):
            dp, dq = sign * cross(a, b, p), sign * cross(a, b, q)
            if dp >= 0:
                clipped.append(p)
            if (dp < 0) != (dq < 0):
                t = dp / (dp - dq)
                clipped.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        points = clipped
    if len(points) < 3:
        return 0
    return abs(sum(cross(points[0], p, q) for p, q in zip(points[1:], points[2:]))) / 2


def triangles(collection):
    for obj in sorted(bpy.data.collections[collection].all_objects, key=lambda ob: ob.name):
        if obj.type != "MESH":
            continue
        mesh = obj.data
        mesh.calc_loop_triangles()
        coords = [obj.matrix_world @ v.co for v in mesh.vertices]
        for tri in mesh.loop_triangles:
            points = [coords[i] for i in tri.vertices]
            normal = (points[1] - points[0]).cross(points[2] - points[0]).normalized()
            if normal.length_squared == 0:
                raise ValueError(f"Degenerate triangle in {obj.name}, face {tri.polygon_index}")
            axis = max(range(3), key=lambda k: abs(normal[k]))
            uv = [(p[(axis + 1) % 3], p[(axis + 2) % 3]) for p in points]
            low = tuple(min(p[k] for p in points) for k in range(3))
            high = tuple(max(p[k] for p in points) for k in range(3))
            yield (low, high, obj.name, tri.polygon_index, normal, points, axis, uv)


def audit(distance, details, collection="StarterFarmhouse"):
    ordered = sorted(triangles(collection), key=lambda t: t[0][0])
    groups = Counter()
    pairs = set()
    for i, (low, high, name, face, n, points, axis, uv) in enumerate(ordered):
        for j in range(i + 1, len(ordered)):
            lo, hi, other, index, m, corners, other_axis, other_uv = ordered[j]
            if lo[0] > high[0] + distance:
                break
            if any(lo[k] > high[k] + distance or hi[k] < low[k] - distance for k in (1, 2)):
                continue
            if name == other and face == index:
                continue
            if n.cross(m).length > 0.001 or max(abs(n.dot(p - points[0])) for p in corners) > distance:
                continue
            if axis != other_axis:
                other_uv = [(p[(axis + 1) % 3], p[(axis + 2) % 3]) for p in corners]
            area = shared_area(uv, other_uv) / abs(n[axis])
            if area < 1e-7:
                continue
            pair = tuple(sorted(((name, face), (other, index))))
            if pair not in pairs:
                pairs.add(pair)
                groups[" / ".join(sorted((name, other)))] += 1
                if details:
                    print("OVERLAP", pair, "axis", axis, "plane", round(points[0][axis], 4), "area", round(area, 5))
    return {"triangles_checked": len(ordered), "parallel_plane_tolerance_m": distance,
            "min_overlap_area_m2": 1e-7, "overlapping_face_pairs": len(pairs),
            "by_object": dict(sorted(groups.items()))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    report = audit(0.002, args.details)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    if report["overlapping_face_pairs"]:
        raise RuntimeError("Overlapping parallel surfaces in saved master")
