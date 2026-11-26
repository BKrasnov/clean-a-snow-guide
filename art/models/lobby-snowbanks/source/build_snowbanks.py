"""Six snowbank templates; the same ellipsoids are instanced in Roblox as SpecialMesh spheres.

Only the visible cap is authored for review. Studio buries the lower geometry
under the existing snow ground. No uploaded mesh or texture is required.
"""
import json
import math
from pathlib import Path
import bpy
import bmesh
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
S = 0.28
T = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))
# center XYZ and full ellipsoid size, in studs; Y=0 is the ground plane.
TEMPLATES = {
    'Pillow': [((-1.1, 0, 0), (10, 3.1, 6.4)), ((3.1, -.08, .7), (6.4, 2.1, 4.8)), ((5.2, -.06, 1.3), (3.5, 1.25, 3.1))],
    'Windbank': [((-3, 0, .5), (10, 2.8, 4.4)), ((2.5, -.04, 0), (11, 2.05, 5.2)), ((6, -.04, -.4), (5.5, 1.2, 3.7))],
    'Crescent': [((-3, 0, 0), (5.8, 2.2, 5.4)), ((0, -.04, 1.7), (7.1, 2.05, 3.8)), ((3.2, -.02, .1), (5.4, 2.35, 5.0))],
    'Clumps': [((-1.3, 0, 0), (3.5, 1.8, 3.0)), ((.8, -.02, .3), (3.1, 1.5, 2.8)), ((2.2, -.03, -.1), (2.0, .95, 1.9))],
    'TreeSkirt': [((-2.1, 0, 0), (2.7, 1.6, 4.0)), ((0, -.02, 2), (4.2, 1.55, 2.5)), ((2.1, 0, 0), (2.7, 1.9, 4.0)), ((0, -.02, -2), (4, 1.25, 2.5))],
    'Shoulder': [((-2.4, 0, .3), (9.7, 2.05, 5.4)), ((1.0, -.04, 0), (8.2, 3.05, 5.7)), ((4.1, -.04, .3), (5.2, 1.65, 4.4))],
}
# Review round 1: merge the large masses, and make the trunk opening circular.
TEMPLATES['Pillow'][-1] = ((5.2, -.12, 1.3), (3.8, 1.0, 3.3))
TEMPLATES['Shoulder'][-1] = ((3.5, -.14, .3), (5.8, 1.30, 4.6))
TEMPLATES['Crescent'] = [((-2.1, 0, -.05), (6.2, 2.2, 5.5)),
                         ((0, -.25, 1.35), (8.2, 1.55, 4.4)),
                         ((2.2, -.04, -.05), (6.0, 2.3, 5.3))]
TEMPLATES['TreeSkirt'] = [((1.65*math.cos(a), -.05, 1.65*math.sin(a)),
                         (2.2, .48, 4.5), -math.degrees(a))
                        for i in range(8) for a in [math.tau*i/8]]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
collection = bpy.data.collections.new('Export')
bpy.context.scene.collection.children.link(collection)
material = bpy.data.materials.new('M_Snowbanks_Snow')
rgb = [int('F3F6F5'[i:i+2], 16)/255 for i in (0,2,4)]
rgba = tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb) + (1,)
material.diffuse_color = rgba
material.use_nodes = True
shader = material.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value = rgba
shader.inputs['Roughness'].default_value = .85
metadata = {}
objects = []
for index, (name, lobes) in enumerate(TEMPLATES.items()):
    offset = Vector(((index % 3 - 1)*19, 0, (index // 3 - .5)*14))
    records = []
    for j, values in enumerate(lobes):
        center, size = values[:2]
        angle = values[2] if len(values)>2 else 0
        rotate = Matrix.Rotation(math.radians(angle), 3, 'Y')
        size = (size[0], size[1]*1.5, size[2])
        # Round 2: only a shallow cap rises above ground, with a gently sloped foot.
        # Preserve visible height and ground footprint, while burying the equator.
        k = .72
        vertical_radius = (size[1]/2)/(1-k)
        footprint_ratio = math.sqrt(1-k*k)
        size = (size[0]/footprint_ratio, vertical_radius*2, size[2]/footprint_ratio)
        center = (center[0], center[1]-k*vertical_radius, center[2])
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=.5)
        obj = bpy.context.object
        obj.name = name + str(j)
        for c in list(obj.users_collection): c.objects.unlink(obj)
        collection.objects.link(obj)
        for vertex in obj.data.vertices:
            local = Vector((vertex.co.x*size[0], vertex.co.z*size[1], -vertex.co.y*size[2]))
            vertex.co = T @ rotate @ local * S
            vertex.co += T @ Vector(center) * S
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        cut = bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                                   dist=1e-7, plane_co=(0,0,0), plane_no=(0,0,1), clear_inner=True)
        boundary = [e for e in bm.edges if e.is_boundary]
        if boundary: bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
        bmesh.ops.triangulate(bm, faces=[face for face in bm.faces if len(face.verts)>4])
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.materials.append(material)
        obj.location = T @ offset * S
        for poly in obj.data.polygons: poly.use_smooth = poly.normal.z > -.99
        obj.data.calc_loop_triangles()
        records.append({'at': list(center), 'size': list(size), 'kind':'Ball', 'rgb':'F3F6F5',
                        'rotation':[round(rotate[i][k],7) for i in range(3) for k in range(3)],
                        'triangles':len(obj.data.loop_triangles)})
        objects.append(obj)
    metadata[name] = records
    assert sum(row['triangles'] for row in records) <= 1000
bpy.ops.object.select_all(action='DESELECT')
for obj in objects: obj.select_set(True)
bpy.context.view_layer.objects.active = objects[0]
bpy.ops.object.join()
body = bpy.context.object
body.name = 'Snowbanks_Body'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
body.data.calc_loop_triangles()
assert len(body.data.loop_triangles) <= 3000
ASSET.joinpath('export').mkdir(parents=True, exist_ok=True)
(ASSET/'export/templates.json').write_text(json.dumps({'units':'studs','templates':metadata,
    'visibleTriangles':len(body.data.loop_triangles),'primitiveParts':len(objects)}, indent=2)+'\n', encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'Snowbanks_master.blend'), compress=True)
print('SNOWBANKS_BUILT',len(body.data.loop_triangles),'triangles;',len(objects),'ellipsoid parts')
