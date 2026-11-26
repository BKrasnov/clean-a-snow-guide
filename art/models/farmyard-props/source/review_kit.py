"""Round-trip geometry audit and product renders. Studio backdrop is review-only."""
import json
from itertools import combinations
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE))
from build_kit import ASSET, S, L
from check_stalls import inspect

out=ASSET/'review'
out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ASSET/'export/FarmyardProps.glb'),merge_vertices=True)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
trees={}
report={}
for obj in meshes:
    report[obj.name]=inspect(obj)
    mesh=obj.data
    report[obj.name]['degenerate_triangles']=sum(t.area < 1e-8 for t in mesh.loop_triangles)
    trees[obj.name]=BVHTree.FromPolygons([obj.matrix_world@v.co for v in mesh.vertices],
                                          [t.vertices[:] for t in mesh.loop_triangles],all_triangles=True)
contacts={a+' / '+b:len(pairs) for a,b in combinations(trees,2) if (pairs:=trees[a].overlap(trees[b]))}
rotor=bpy.data.objects['PrizeWheel_Dial']
assert rotor.parent and rotor.parent.name=='PrizeWheel'
rotor_rest=rotor.matrix_world.copy()
rotation_contacts={}
for deg in range(0,360,15):
    transform=rotor_rest @ Matrix.Rotation(math.radians(deg),4,'Y')
    posed=BVHTree.FromPolygons([transform@v.co for v in rotor.data.vertices],
                                [t.vertices[:] for t in rotor.data.loop_triangles],all_triangles=True)
    hits=[name for name,tree in trees.items() if name!=rotor.name and posed.overlap(tree)]
    if hits: rotation_contacts[deg]=hits
audit=dict(assets=report,surface_contacts=contacts,dial_rotation_step_deg=15,dial_rotation_contacts=rotation_contacts,
           avatar_height_studs=5.1,stud_metres=S)
(out/'geometry.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf8')
print('AUDIT',[(name,len(r['close_coplanar_pairs'])) for name,r in report.items()],contacts,flush=True)
assert len(meshes)==19 and not contacts and not rotation_contacts
assert all(not (r['close_coplanar_pairs'] or r['degenerate_triangles'] or
                r['nonmanifold_edges_after_position_weld']) for r in report.values())
if '--audit-only' in sys.argv:
    sys.exit(0)

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.cycles.use_denoising=True
scene.view_settings.view_transform='Khronos PBR Neutral'
scene.world=bpy.data.worlds.new('Studio sky')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.80,.88,1,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.68
sun=bpy.data.lights.new('Winter sun','SUN')
sun.energy=3.0
sun.angle=.19
sun.color=(1,.89,.77)
ob=bpy.data.objects.new('Winter sun',sun)
scene.collection.objects.link(ob)
ob.rotation_euler=Vector((.49,.64,-1)).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=250,location=(0,0,-.007))
floor=bpy.data.materials.new('Studio sweep')
floor.diffuse_color=(.36,.47,.63,1)
floor.use_nodes=True
floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=floor.diffuse_color
bpy.context.object.data.materials.append(floor)
camera=bpy.data.objects.new('Product camera',bpy.data.cameras.new('Product camera'))
scene.collection.objects.link(camera)
scene.camera=camera
camera.data.type='ORTHO'
scene.render.image_settings.file_format='PNG'
scene.render.resolution_percentage=100
L.plant_mesh.COLORS={**L.COLORS,'earth':'966240','grass':'96DC6A'}
L.collection=scene.collection
L.surface=L.plant_mesh.palette()
player=L.new('Scale figure - review only')
L.figure(player,0,0,0,5.1,'blue')
avatar=L.finish(player)

def shoot(name,target,dir,width,size,visible=None,figure=None):
    for obj in meshes:
        obj.hide_render=visible is not None and obj.name not in visible
    avatar.hide_render=figure is None
    if figure:
        avatar.location=Vector(figure)*S
    center=Vector(target)*S
    ray=Vector(dir).normalized()
    camera.location=center+ray*55
    camera.rotation_euler=(-ray).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=width*S
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)

shoot('Overview',(4,-18,5),(.015,-1,.56),157,(1920,680),figure=(-4,-21,0))
launch={o.name for o in meshes if o.name.startswith(('Start','Launch','Leaderboard','Prize'))}
shoot('Launch',(6.5,-1.8,6.25),(.015,-1,.18),91,(1740,530),launch,(-18,-11,0))
shoot('Cabin',(65,-35,8.0),(.53,-1,.37),34,(920,760),{'LogCabin'},(56,-46,0))
shoot('Garage',(-55,-35,8.6),(.48,-1,.31),35,(920,760),{'BarnGarage','GarageSnowplow'},(-63,-47,0))
shoot('Wheel',(37.2,-3,7.18),(-.04,-1,.20),28,(980,670),{'LeaderboardRight','PrizeWheel','PrizeWheel_Dial'},(36.5,-9,0))
shoot('Market',(-44,-7,4.65),(.49,-1,.24),25,(940,620),{'Rewards','Upgrades'})
