"""Reimport GLB for dimensional, geometry and traversal checks, then render inspection views."""
import json
from math import hypot, radians
from pathlib import Path
import sys
import bpy
from mathutils import Vector

SOURCE=Path(__file__).resolve().parent
ASSET=SOURCE.parent
ROOT=ASSET.parents[2]
TMP=ROOT/'build/crossroads'
TMP.mkdir(parents=True,exist_ok=True)
REF=ROOT/'art/refs/garden-plot'
sys.dont_write_bytecode=True
sys.path[:0]=[str(SOURCE),str(ROOT/'.agents/skills/game-model-workflow/scripts'),
              str(ASSET.parent/'garden-plants/source')]
import model_check
from build_crossroads import STUD
from plant_mesh import COLORS
from review_exports import check_faces

def world_bounds(ob):
    coords=[ob.matrix_world@v.co/STUD for v in ob.data.vertices]
    return ([min(v[k] for v in coords) for k in range(3)],[max(v[k] for v in coords) for k in range(3)])

def measure(objects):
    by_name={ob.name:ob for ob in objects}
    beds=[by_name[f'Bed{i:02}'] for i in range(1,5)]
    fences={'FenceFrontLeft','FenceFrontRight','FenceLeft','FenceRight','FenceBack'}
    assert set(by_name)==fences|{ob.name for ob in beds}
    assert len({ob.data.name for ob in beds})==4
    bounds={ob.name:world_bounds(ob) for ob in objects}
    # Test a 3.3-stud-wide upright cylinder (covers the square diagonal of a 3 x 1 stud avatar).
    # Conservative obstacles are the complete world bounds of each exported mesh, including its caps.
    assert all(abs(low[2])<.0001 for low,high in bounds.values())
    obstacles=bounds.values()
    routes={'gate_and_central_aisle':[(0,-9),(0,3.75)],
            'cross_to_left':[(0,0),(-4.5,0)],'cross_to_right':[(0,0),(4.5,0)]}
    paths={}
    for name,(a,b) in routes.items():
        distances=[]
        for s in range(401):
            x,y=[a[k]+(b[k]-a[k])*s/400 for k in range(2)]
            for low,high in obstacles:
                dx=max(low[0]-x,0,x-high[0])
                dy=max(low[1]-y,0,y-high[1])
                distances.append(hypot(dx,dy))
        clearance=min(distances)-1.65
        assert clearance>.5,(name,clearance)
        paths[name]=round(clearance,4)
    clear={
        'gate':bounds['FenceFrontRight'][0][0]-bounds['FenceFrontLeft'][1][0],
        'south_north':bounds['Bed02'][0][0]-bounds['Bed01'][1][0],
        'east_west':bounds['Bed03'][0][1]-bounds['Bed01'][1][1]}
    assert all(abs(v-e)<.001 for v,e in zip(clear.values(),[5,4.5,4.5]))
    for ob in beds:
        hit,point,normal,face=ob.ray_cast(Vector((0,0,1)),Vector((0,0,-1)))
        assert hit and point.length<.0001,(ob.name,point[:])
    return {'ground_level_studs':0,'clear_width_studs':{k:round(v,4) for k,v in clear.items()},'avatar_height_studs':5.1,
            'test_diameter_studs':3.3,'min_side_margin_studs':paths,
            'plant_origins_studs':{ob.name:[round(x/STUD,3) for x in ob.matrix_world.translation] for ob in beds}}

def audit():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'GardenCrossroads.blend'))
    src=list(bpy.context.scene.objects)
    src_bounds={ob.name:world_bounds(ob) for ob in src}
    report=model_check.inspect_model(src)
    assert report['ok'],report['issues']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ASSET/'export/GardenCrossroads.glb'))
    objects=list(bpy.context.scene.objects)
    assert all(ob.type=='MESH' and len(ob.data.materials)==1 for ob in objects)
    assert len({o.active_material for o in objects})==1
    assert any(i.packed_file for i in bpy.data.images)
    assert len(objects)==len(src_bounds)
    assert all(max(abs(s-t) for row,new in zip(src_bounds[o.name],world_bounds(o))
                   for s,t in zip(row,new))<.001 for o in objects)
    total=0
    per_mesh={}
    verts=[]
    faces=[]
    for ob in objects:
        m=ob.data
        swatches=list(COLORS)
        used={swatches[int(uv.uv.y*4)*8+int(uv.uv.x*8)] for uv in m.uv_layers.active.data}
        assert used <= {'wood','tan','bark','earth','red'},(ob.name,used)
        m.calc_loop_triangles()
        total+=len(m.loop_triangles)
        per_mesh[ob.name]=len(m.loop_triangles)
        start=len(verts)
        verts.extend(ob.matrix_world@v.co for v in m.vertices)
        faces.extend([tuple(start+i for i in tri.vertices) for tri in m.loop_triangles])
    assert total==report['totals']['tris'] and total<=3000,total
    report['reimport']={'triangles':total,'per_mesh':per_mesh,'materials':1,'embedded_texture':True}
    report['clearance']=measure(objects)
    # Also check cross-object coplanarity in the assembled world-space triangle soup.
    combined=bpy.data.meshes.new('AuditGeometry')
    combined.from_pydata(verts,[],faces)
    proxy=bpy.data.objects.new('Audit',combined)
    conflicts=check_faces(proxy)
    bpy.data.objects.remove(proxy)
    bpy.data.meshes.remove(combined)
    report['coplanar_overlaps']=conflicts
    (ASSET/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    assert not conflicts,conflicts[:4]
    return objects

def review_material(name,rgba):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*rgba,1)
    shader.inputs['Roughness'].default_value=.87
    return mat

def render():
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=12
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='Standard'
    scene.world=bpy.data.worlds.new('Soft skylight')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.86,1,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.57
    groundmat=review_material('Grass (preview only)',(.23,.42,.24))
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003))
    bpy.context.object.data.materials.append(groundmat)
    light=bpy.data.lights.new('Window','AREA')
    light.energy=500
    light.shape='DISK'
    light.size=5
    lamp=bpy.data.objects.new('Window',light)
    scene.collection.objects.link(lamp)
    lamp.location=(-3,-4.5,7)
    lamp.rotation_euler=(-lamp.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add()
    cam=bpy.context.object
    cam.data.type='ORTHO'
    scene.camera=cam
    def snap(path,eye,target,scale,width,height):
        cam.location=Vector(eye)
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale=scale
        scene.render.resolution_x=width
        scene.render.resolution_y=height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
    for name,eye in [('front',(0,-8,.37)),('back',(0,8,.37)),('side',(8,0,.37)),('top',(0,0,8))]:
        snap(TMP/(name+'.png'),eye,(0,0,.35),5.6,820,690 if name=='top' else 450)
    snap(REF/'crossroads-model.png',(.30,-7,5.50),(0,0,.15),5.55,1250,900)
    # The scale mannequin stays in this disposable render scene only.
    avatar=review_material('Player scale',(.21,.38,.48))
    def block(center,size):
        bpy.ops.mesh.primitive_cube_add(size=1,location=tuple(v*STUD for v in center))
        ob=bpy.context.object
        ob.dimensions=tuple(v*STUD for v in size)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        ob.data.materials.append(avatar)
        mod=ob.modifiers.new('Corner','BEVEL')
        mod.width=.018
        mod.segments=1
        ob.modifiers.new('Normals','WEIGHTED_NORMAL')
    y=-6.45
    for x in (-.50,.50):block((x,y,1),(.98,.96,2))
    block((0,y,3),(1.99,1,2))
    for x in (-1.27,1.27):block((x,y,3),(.54,.96,1.96))
    block((0,y,4.55),(1.40,1.05,1.1))
    snap(REF/'crossroads-player-scale.png',(3,-7,5.3),(0,-.10,.26),6.5,1050,740)

if __name__=='__main__':
    audit()
    if '--audit-only' not in sys.argv:
        render()
