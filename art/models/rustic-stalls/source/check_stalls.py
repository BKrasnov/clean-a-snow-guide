"""Check independent exports and render the imported assets at avatar scale."""
from collections import defaultdict
from itertools import combinations
import json
from math import radians
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE))
from build_stalls import STUD,LAYOUT,lobby


def intersection_area(points, clip):
    area=lambda a,b:a.x*b.y-a.y*b.x
    winding=1 if area(clip[1]-clip[0],clip[2]-clip[0])>0 else -1
    for a,b in zip(clip,clip[1:]+clip[:1]):
        if not points:
            return 0
        output=[]
        for p,q in zip(points,points[1:]+points[:1]):
            dp=winding*area(b-a,p-a)
            dq=winding*area(b-a,q-a)
            if dp>=0:
                output.append(p)
            if (dp>=0)!=(dq>=0):
                output.append(p.lerp(q,dp/(dp-dq)))
        points=output
    return abs(sum(area(a,b) for a,b in zip(points,points[1:]+points[:1])))*.5


def inspect(obj):
    mesh=obj.data
    mesh.calc_loop_triangles()
    pts=[v.co/STUD for v in mesh.vertices]
    planes=defaultdict(list)
    overlaps=[]
    for tri in mesh.loop_triangles:
        a,b,c=(pts[i] for i in tri.vertices)
        normal=(b-a).cross(c-a).normalized()
        axis=max(range(3),key=lambda i:abs(normal[i]))
        key=(*(round(x,4) for x in normal),round(normal.dot(a),3))
        j,k=(axis+1)%3,(axis+2)%3
        projected=[Vector((p[j],p[k])) for p in (a,b,c)]
        for other in planes[key]:
            if intersection_area(projected,other)>.001:
                overlaps.append([tri.index,round(normal.dot(a),4),*[round(x,3) for x in normal],
                                 [round(x,3) for x in (a+b+c)/3]])
        planes[key].append(projected)
    bounds=[[round(min(p[k] for p in pts),3),round(max(p[k] for p in pts),3)] for k in range(3)]
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    bm.free()
    return dict(stud_bounds=bounds,triangles=len(mesh.loop_triangles),material_slots=len(mesh.materials),
                close_coplanar_pairs=overlaps,nonmanifold_edges_after_position_weld=nonmanifold)


def pictures(out, player):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=18
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='AgX'
    scene.world=bpy.data.worlds.new('Review sky')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.69,.83,1,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.72
    sun=bpy.data.lights.new('Winter sun','SUN')
    sun.energy=2.9
    sun.angle=radians(10)
    sun.color=(1,.88,.73)
    ob=bpy.data.objects.new('Winter sun',sun)
    scene.collection.objects.link(ob)
    ob.rotation_euler=Vector((.48,.59,-1)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=160,location=(0,0,-.01))
    floor=bpy.data.materials.new('Review backdrop')
    floor.diffuse_color=(.57,.67,.81,1)
    bpy.context.object.data.materials.append(floor)
    camera=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'))
    scene.collection.objects.link(camera)
    scene.camera=camera
    camera.data.type='ORTHO'
    scene.render.image_settings.file_format='JPEG'
    scene.render.image_settings.quality=89
    def shoot(name,position,target,width,res):
        camera.location=Vector(position)*STUD
        camera.rotation_euler=(Vector(target)*STUD-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.ortho_scale=width*STUD
        scene.render.resolution_x,scene.render.resolution_y=res
        scene.render.filepath=str(out/(name+'.jpg'))
        bpy.ops.render.render(write_still=True)
    shoot('Lineup',(1,-70,23),(0,0,4.2),61,(1800,670))
    shoot('StallsFromSide',(-30,-55,24),(0,.6,4.2),58,(1700,720))
    shoot('Back',(12,57,26),(0,0,4.2),62,(1500,650))
    player.hide_render=True
    shoot('RoofPlan',(0,0,40),(0,0,0),61,(1400,500))
    shoot('Profile',(-56,-2,14),(0,0,4.2),17,(770,690))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out=ASSET/'review'
    out.mkdir(exist_ok=True)
    objects=[]
    report={}
    for file in sorted((ASSET/'export').glob('*.glb')):
        before=set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(file),merge_vertices=True)
        added=list(set(bpy.data.objects)-before)
        assert len(added)==1 and added[0].name==file.stem, file
        obj=added[0]
        report[obj.name]=inspect(obj)
        x,y,a=LAYOUT[obj.name]
        obj.location=(x*STUD,y*STUD,0)
        obj.rotation_euler.z=radians(a)
        objects.append(obj)
    assert set(report)==set(LAYOUT)
    bpy.context.view_layer.update()
    def surface(obj):
        coords=[obj.matrix_world@v.co for v in obj.data.vertices]
        return BVHTree.FromPolygons(coords,[list(t.vertices) for t in obj.data.loop_triangles],all_triangles=True)
    by_name={o.name:surface(o) for o in objects}
    contacts={a+' / '+b:len(hits) for a,b in combinations(by_name,2)
              if (hits:=by_name[a].overlap(by_name[b]))}
    report=dict(assets=report,intersecting_model_pairs=contacts,avatar_height_studs=5.1)
    (out/'geometry.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('QA',[(n,x['triangles'],len(x['close_coplanar_pairs']),x['nonmanifold_edges_after_position_weld'])
                for n,x in report['assets'].items()],contacts,flush=True)
    if '--audit-only' in sys.argv:
        return
    lobby.collection=bpy.context.scene.collection
    colors={**lobby.COLORS,'earth':'966240'}
    lobby.surface=(objects[0].data.materials[0],{n:((i%8+.5)/8,(i//8+.5)/4) for i,n in enumerate(colors)})
    figure=lobby.new('Review avatar')
    lobby.figure(figure,0,0,0,5.1,'pine')
    avatar=lobby.finish(figure,-4,-7,0,138)
    pictures(out,avatar)


if __name__=='__main__':
    main()
