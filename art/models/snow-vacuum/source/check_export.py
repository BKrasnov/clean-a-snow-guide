"""Round-trip the exported asset, check coplanar triangle area, and render the preview."""
from collections import defaultdict
from pathlib import Path
import json
import bpy
from mathutils import Vector

folder = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(folder/'export/SnowVacuum.glb'))
objects = [ob for ob in bpy.context.scene.objects if ob.type == 'MESH']
planes = defaultdict(list)
points = []


def cross(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def overlap(poly, clip):
    """Sutherland-Hodgman intersection in the dominant projection plane."""
    orient = 1 if cross(*clip)>0 else -1
    for i,a in enumerate(clip):
        b = clip[(i+1)%3]
        clipped = []
        for j,p in enumerate(poly):
            q = poly[j-1]
            fp,fq = orient*cross(a,b,p),orient*cross(a,b,q)
            if (fp>0) != (fq>0):
                t = fq/(fq-fp)
                clipped.append(tuple(q[k]+t*(p[k]-q[k]) for k in (0,1)))
            if fp>=0:
                clipped.append(p)
        poly = clipped
    return abs(sum(x*q[1]-y*q[0] for (x,y),q in zip(poly,poly[1:]+poly[:1])))/2


conflicts = []
tris = 0
for ob in objects:
    mesh = ob.data
    mesh.calc_loop_triangles()
    for tri in mesh.loop_triangles:
        p = [ob.matrix_world @ mesh.vertices[k].co for k in tri.vertices]
        points.extend(p)
        tris += 1
        normal = (p[1]-p[0]).cross(p[2]-p[0]).normalized()
        axis = max(range(3),key=lambda k:abs(normal[k]))
        if normal[axis]<0:
            normal.negate()
        key = tuple(round(x,5) for x in (*normal,normal.dot(p[0])))
        uv = [tuple(v[k] for k in range(3) if k!=axis) for v in p]
        for other_name,other in planes[key]:
            if overlap(uv,other)>1e-9:
                conflicts.append((ob.name,other_name))
        planes[key].append((ob.name,uv))
dimensions = [(max(p[k] for p in points)-min(p[k] for p in points))/.28 for k in range(3)]
print('EXPORT_AUDIT',json.dumps(dict(tris=tris,studs=dimensions,coplanar=conflicts)))
assert not conflicts and tris <= 2000 and len(objects)==7
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.world=bpy.data.worlds.new('Studio')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.70,.79,.92,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
scene.view_settings.view_transform='AgX'
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001))
mat=bpy.data.materials.new('Backdrop')
mat.diffuse_color=(.44,.56,.72,1)
bpy.context.object.data.materials.append(mat)
for pos,energy,size in [((-2,-3,4),220,3),((2,-1,3),125,2),((0,3,3),160,2)]:
    bpy.ops.object.light_add(type='AREA',location=pos)
    lamp=bpy.context.object
    lamp.data.energy=energy
    lamp.data.shape='DISK'
    lamp.data.size=size
    lamp.rotation_euler=(Vector((0,0,.4))-lamp.location).to_track_quat('-Z','Y').to_euler()
target=Vector((0,-.24,.51))
bpy.ops.object.camera_add(location=target+Vector((2.65,-3.7,1.18)))
cam=bpy.context.object
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'
cam.data.ortho_scale=1.90
scene.camera=cam
scene.render.resolution_x=800
scene.render.resolution_y=680
scene.render.resolution_percentage=100
scene.render.filepath=str(folder/'preview/vacuum.png')
bpy.ops.render.render(write_still=True)

# Five-stud R6 proportion guide beside the vacuum, outside the export.
guide = bpy.data.materials.new('Scale guide')
guide.diffuse_color=(.31,.40,.51,1)
def block(center, size):
    x,y,z = center
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x-2)*.28,(y+1)*.28,z*.28))
    ob = bpy.context.object
    ob.dimensions = tuple(v*.28 for v in size)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(guide)
    bevel=ob.modifiers.new('Rounded corners','BEVEL')
    bevel.width=.023
    bevel.segments=2

for x in (-2.02,-1.02):
    block((x,-1.83,1),(.96,.97,2))
block((-1.52,-1.83,3),(1.98,1,1.98))
block((-1.52,-1.83,4.5),(1.45,1,1))
block((-3.02,-1.83,3),(.95,.97,1.98))
block((-.02,-1.83,3),(.95,.97,1.98))
target=Vector((-.54,-.24,.65))
cam.location=target+Vector((1.8,-4.8,1.65))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=2.62
scene.render.filepath=str(folder/'preview/player-scale.png')
bpy.ops.render.render(write_still=True)
