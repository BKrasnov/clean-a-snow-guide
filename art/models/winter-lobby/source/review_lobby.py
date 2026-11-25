"""Inspect the exported GLB and photograph it outside the editable master."""
from collections import defaultdict
from pathlib import Path
from math import radians
import json
import sys
import bpy
from mathutils import Vector
from mathutils.geometry import convex_hull_2d, intersect_line_line_2d
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
ROOT=ASSET.parents[2]
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE))
import build_lobby as design
V=Vector
S=design.STUD


def coplanar_area(subject,clip):
    def cross(a,b):return a.x*b.y-a.y*b.x
    direction=1 if cross(clip[1]-clip[0],clip[2]-clip[0])>0 else -1
    poly=subject
    for a,b in zip(clip,clip[1:]+clip[:1]):
        if not poly:return 0
        new=[]
        last=poly[-1]
        d0=direction*cross(b-a,last-a)
        for p in poly:
            d1=direction*cross(b-a,p-a)
            if (d0>=0)!=(d1>=0):
                new.append(last+(p-last)*(d0/(d0-d1)))
            if d1>=0:new.append(p)
            last,d0=p,d1
        poly=new
    return abs(sum(cross(p,q) for p,q in zip(poly,poly[1:]+poly[:1])))*.5


def measure(objects):
    planes=defaultdict(list)
    hits=defaultdict(int)
    counts={}; footprints={}; trees={}
    for o in objects:
        mesh=o.data
        mesh.calc_loop_triangles()
        counts[o.name]=len(mesh.loop_triangles)
        coords=[o.matrix_world@v.co/S for v in mesh.vertices]
        trees[o.name]=BVHTree.FromPolygons(coords,[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
        pts=[V(p.xy) for p in coords]
        footprints[o.name]=[pts[k] for k in convex_hull_2d(pts)]
        for tri in mesh.loop_triangles:
            a,b,c=(coords[k] for k in tri.vertices)
            n=(b-a).cross(c-a).normalized()
            axis=max(range(3),key=lambda k:abs(n[k]))
            key=(*[round(v,4) for v in n],round(n.dot(a),3))
            i,j=(axis+1)%3,(axis+2)%3
            poly=[V((p[i],p[j])) for p in (a,b,c)]
            xmin,xmax=min(p.x for p in poly),max(p.x for p in poly)
            ymin,ymax=min(p.y for p in poly),max(p.y for p in poly)
            for name,x0,x1,y0,y1,other in planes[key]:
                if min(xmax,x1)-max(xmin,x0)<.001 or min(ymax,y1)-max(ymin,y0)<.001:continue
                if coplanar_area(poly,other)>.001:hits[' / '.join(sorted((name,o.name)))]+=1
            planes[key].append((o.name,xmin,xmax,ymin,ymax,poly))
    def gap(n,m):
        a,b=footprints[n],footprints[m]
        if any(intersect_line_line_2d(p,q,r,s) is not None for p,q in zip(a,a[1:]+a[:1])
               for r,s in zip(b,b[1:]+b[:1])):return 0
        def dist(p,q,r):
            d=r-q
            return (p-q-d*max(0,min(1,(p-q).dot(d)/d.length_squared))).length if d.length_squared else (p-q).length
        return min(dist(p,q,r) for points,edges in ((a,b),(b,a)) for p in points for q,r in zip(edges,edges[1:]+edges[:1]))
    bank=['Rewards','Upgrades','Leaderboard01','Leaderboard02','Leaderboard03','PrizeWheel_Kiosk','Classes']
    names=[f'Station{i:02}' for i in range(1,7)]
    collisions={}
    above_ground=[o for o in trees if o!='SnowGround']
    for i,a in enumerate(above_ground):
        for b in above_ground[i+1:]:
            pairs=trees[a].overlap(trees[b])
            if pairs:collisions[a+' / '+b]=len(pairs)
    return dict(objects=len(objects),triangles=sum(counts.values()),per_object_triangles=counts,
        intersecting_object_surfaces_above_ground=collisions,
        material_count=len({m.name for o in objects for m in o.data.materials}),same_facing_coplanar_triangles=dict(hits),
        interval_units='Roblox studs',pad_count=len([o for o in objects if o.name.startswith('Station')]),
        avatar_height=5.1,gate_clearance=round(gap('OpenGate_Left','OpenGate_Right'),2),
        central_aisle=round(gap(names[0],names[1]),2),between_pads=round(gap(names[0],names[2]),2),
        approach_to_bank=round(min(gap(p,n) for p in names for n in bank),2),
        bank_gaps=[round(gap(a,b),3) for a,b in zip(bank,bank[1:])],
        tree_count=len([o for o in objects if o.name.startswith('SnowFir')]),
        tree_to_fence=round(min(gap(t,f) for t in footprints if t.startswith('SnowFir')
                                 for f in footprints if f.startswith('Fence')),2))


def pictures(scene,objects):
    scene.render.engine='CYCLES'
    scene.cycles.samples=16
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='Standard'
    scene.view_settings.exposure=-.38
    world=bpy.data.worlds.new('Review sky')
    scene.world=world;world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.73,.84,1,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.61
    nodes=world.node_tree.nodes;links=world.node_tree.links
    sky=nodes.new('ShaderNodeBackground');sky.inputs[0].default_value=(.36,.65,.94,1)
    rays=nodes.new('ShaderNodeLightPath');mix=nodes.new('ShaderNodeMixShader')
    links.new(rays.outputs['Is Camera Ray'],mix.inputs[0])
    links.new(nodes['Background'].outputs[0],mix.inputs[1]);links.new(sky.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],nodes['World Output'].inputs[0])
    light=bpy.data.lights.new('Winter sun','SUN');light.energy=2.35;light.angle=radians(12)
    light.color=(1,.89,.76)
    ob=bpy.data.objects.new('Review sunlight',light);scene.collection.objects.link(ob)
    ob.rotation_euler=V((.60,.55,-1)).to_track_quat('-Z','Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.43*S))
    ground=bpy.context.object
    mat=bpy.data.materials.new('Studio backdrop');mat.diffuse_color=(.53,.65,.78,1)
    ground.data.materials.append(mat)
    cam=bpy.data.cameras.new('Review camera');ob=bpy.data.objects.new('Review camera',cam)
    scene.collection.objects.link(ob);scene.camera=ob
    def shoot(name,position,target,width,lens=42):
        ob.location=V(position)*S
        ob.rotation_euler=(V(target)*S-ob.location).to_track_quat('-Z','Y').to_euler()
        cam.type='ORTHO' if width else 'PERSP'
        if width:cam.ortho_scale=width*S
        else:cam.lens=lens
        cam.clip_end=230
        scene.render.resolution_percentage=100
        scene.render.resolution_x=1440;scene.render.resolution_y=900
        scene.render.filepath=str(ASSET/'review'/(name+'.jpg'))
        scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=90
        bpy.ops.render.render(write_still=True)
    shoot('Plaza',(2,-136,88),(0,0,1),115)
    shoot('Entrance',(0,-66,23.5),(0,7,2.4),0,27)
    shoot('Stations',(0,-28,14.5),(0,24,4.35),0,30)
    # Comparison figure is generated only in this disposable photo scene.
    first=next(o for o in objects if o.name=='Classes')
    design.collection=scene.collection
    design.surface=(first.data.materials[0],{name:((i%8+.5)/8,(i//8+.5)/4) for i,name in enumerate(design.COLORS)})
    person=design.new('Scale reference')
    design.figure(person,0,0,0,5.1,'pine')
    design.finish(person,-3.4,-17,.015,150)
    shoot('FromGate',(1,-44,7.3),(0,14,2.7),0,24)


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ASSET/'export/WinterLobby.glb'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
(ASSET/'review').mkdir(exist_ok=True)
report=measure(objects)
(ASSET/'review/geometry.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('LOBBY_AUDIT',report,flush=True)
if '--audit-only' not in sys.argv:pictures(bpy.context.scene,objects)
