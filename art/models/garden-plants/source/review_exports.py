"""Audit actual GLB triangle surfaces, then render all imports from five directions."""
import json
from collections import defaultdict
from math import radians
from pathlib import Path
import sys

import bpy
from mathutils import Euler, Vector

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
TMP=ASSET.parents[2]/'build/garden-models'
TMP.mkdir(exist_ok=True,parents=True)

def signed(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])

def intersection_area(triangle,clip):
    polygon=list(triangle)
    direction=1 if signed(*clip)>0 else -1
    for i,a in enumerate(clip):
        b=clip[(i+1)%3]
        result=[]
        for j,p in enumerate(polygon):
            q=polygon[j-1]
            dp,dq=direction*signed(a,b,p),direction*signed(a,b,q)
            if (dp>0)!=(dq>0):
                k=dq/(dq-dp)
                result.append(tuple(q[h]+k*(p[h]-q[h]) for h in (0,1)))
            if dp>=0: result.append(p)
        polygon=result
    return abs(sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(polygon,polygon[1:]+polygon[:1])))/2

def check_faces(ob):
    mesh=ob.data
    mesh.calc_loop_triangles()
    planes=defaultdict(list)
    conflicts=[]
    for tri in mesh.loop_triangles:
        points=[ob.matrix_world@mesh.vertices[n].co for n in tri.vertices]
        normal=(points[1]-points[0]).cross(points[2]-points[0]).normalized()
        axis=max(range(3),key=lambda k:round(abs(normal[k]),5))
        if normal[axis]<0: normal=-normal
        key=(axis,)+tuple(round(q,5) for q in (*normal,normal.dot(points[0])))
        projected=[tuple(p[k] for k in range(3) if k!=axis) for p in points]
        bounds=tuple(fn(t[k] for t in projected) for k in [0,1] for fn in [min,max])
        for old,other,b in planes[key]:
            if bounds[1]<=b[0] or b[1]<=bounds[0] or bounds[3]<=b[2] or b[3]<=bounds[2]:continue
            if intersection_area(projected,other)>1e-9:
                conflicts.append(dict(faces=[tri.index,old],location_m=[round(sum(p[k] for p in points)/3,4) for k in range(3)]))
        planes[key].append((tri.index,projected,bounds))
    return conflicts

def daylight(name,direction,power):
    lamp=bpy.data.lights.new(name,type='SUN')
    lamp.energy=power
    lamp.angle=radians(14)
    ob=bpy.data.objects.new(name,lamp)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler=Vector(direction).to_track_quat('-Z','Y').to_euler()

def render_sheets(plants):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=10
    scene.cycles.use_denoising=True
    scene.world=bpy.data.worlds.new('Daylight')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.82,.97,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.85
    scene.view_settings.view_transform='Standard'
    scene.render.film_transparent=True
    scene.render.image_settings.color_mode='RGBA'
    daylight('Key',(0.6,0.65,-1.0),2.1)
    daylight('Fill',(-.8,.1,-.4),.55)
    bpy.ops.object.camera_add(location=(0,-18,0),rotation=(radians(90),0,0))
    cam=bpy.context.object
    cam.data.type='ORTHO'
    cam.data.ortho_scale=6
    scene.camera=cam
    scene.render.resolution_x=scene.render.resolution_y=1920
    scene.render.resolution_percentage=100
    for name,pitch,yaw in [('front',0,0),('side',0,-90),('back',0,180),('top',90,0),('three-quarter',12,-16)]:
        rotation=Euler((radians(pitch),0,0)).to_matrix()@Euler((0,0,radians(yaw))).to_matrix()
        for i,ob in enumerate(plants):
            coords=[rotation@v.co for v in ob.data.vertices]
            xmin,xmax=min(p.x for p in coords),max(p.x for p in coords)
            zmin,zmax=min(p.z for p in coords),max(p.z for p in coords)
            scale=min(.88/(xmax-xmin),.86/(zmax-zmin))
            ob.rotation_euler=rotation.to_euler()
            ob.scale=(scale,)*3
            ob.location=(i%6-2.5-(xmin+xmax)*scale/2,0,2.51-i//6-(zmin+zmax)*scale/2)
        scene.render.filepath=str(TMP/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    render_beds(plants,scene,cam)

def render_beds(plants,scene,cam):
    """Check eight native-scale imports on one 4x2 arrangement beside a 5.1 stud block avatar."""
    root=ASSET.parents[2]
    bed=json.loads((root/'src/ReplicatedStorage/CleanSnow/Data/garden.json').read_text())['Plots']['Beds']
    def color(name,rgb):
        mat=bpy.data.materials.new(name)
        mat.diffuse_color=(*rgb,1)
        mat.use_nodes=True
        shader=mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value=(*rgb,1)
        shader.inputs['Roughness'].default_value=.95
        return mat
    def block(name,center,size,mat,bevel):
        bpy.ops.mesh.primitive_cube_add(size=1,location=tuple(n*.28 for n in center))
        ob=bpy.context.object
        ob.name=name
        ob.dimensions=tuple(n*.28 for n in size)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        ob.data.materials.append(mat)
        edge=ob.modifiers.new('Edges','BEVEL')
        edge.width=bevel*.28
        edge.segments=1
        ob.modifiers.new('Normals','WEIGHTED_NORMAL')
    soil=color('Bed',(.24,.115,.057))
    snow=color('Garden path',(.71,.81,.92))
    mannequin=color('Avatar',(.27,.39,.50))
    for ob in plants:ob.hide_render=True
    for i,number in enumerate([4,6,14,32,12,15,16,36]):
        x=(i%4-1.5)*(bed['SizeX']+bed['Gap'])
        y=(i//4-.5)*(bed['SizeZ']+bed['Gap'])
        ob=plants[number-1]
        ob.hide_render=False
        ob.scale=(1,1,1)
        ob.rotation_euler=(0,0,0)
        ob.location=(x*.28,y*.28,0)
        block('Bed', (x,y,-.135),(bed['SizeX'],bed['SizeZ'],.27),soil,.075)
    # Feet on the snow path. Model heights above use the bed top as the reference plane.
    for x in (-9.38,-8.38):
        block('Leg',(x,-.85,.73),(.97,.96,2),mannequin,.06)
    block('Torso',(-8.88,-.85,2.73),(1.98,1,1.98),mannequin,.06)
    for x in (-10.36,-7.40):
        block('Arm',(x,-.85,2.73),(.90,.96,1.98),mannequin,.06)
    block('Head',(-8.88,-.85,4.28),(1.42,1.09,1.10),mannequin,.12)
    block('Snow',(-1,0,-.46),(32,18,.38),snow,.14)
    target=Vector((-.34,0,.30))
    cam.location=target+Vector((1.1,-7.3,4.2))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=6.65
    scene.render.resolution_x=1100
    scene.render.resolution_y=600
    scene.render.film_transparent=False
    scene.render.filepath=str(ASSET/'reports/bed-scale.png')
    bpy.ops.render.render(write_still=True)

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    plants=[]
    rows=[]
    for path in sorted((ASSET/'export').glob('*.glb')):
        bpy.ops.import_scene.gltf(filepath=str(path))
        ob,=[o for o in bpy.context.selected_objects if o.type=='MESH']
        bpy.context.view_layer.update()
        coords=[ob.matrix_world@v.co for v in ob.data.vertices]
        dims=[round((max(p[k] for p in coords)-min(p[k] for p in coords))/.28,4) for k in range(3)]
        conflicts=check_faces(ob)
        nodes=ob.data.materials[0].node_tree.nodes
        images=[n.image for n in nodes if n.type=='TEX_IMAGE' and n.image]
        rows.append(dict(file=path.name,triangles=len(ob.data.loop_triangles),studs=dims,
                         min_z_m=round(min(p.z for p in coords),6),materials=len(ob.data.materials),
                         packed_palette=any(img.packed_file for img in images),coplanar=conflicts))
        # Bake importer transforms into the disposable review mesh.
        ob.data.transform(ob.matrix_world)
        ob.parent=None
        ob.rotation_mode='XYZ'
        ob.rotation_euler=(0,0,0)
        ob.location=(0,0,0)
        ob.scale=(1,1,1)
        plants.append(ob)
    (ASSET/'reports/exports.json').write_text(json.dumps(rows,indent=2))
    if '--audit-only' not in sys.argv:
        assert len(plants)==36
        render_sheets(plants)
    source_report=ASSET/'reports/models.json'
    if source_report.is_file() and len(rows)==36:
        originals={p['file']:p for p in json.loads(source_report.read_text(encoding='utf-8'))}
        for row in rows:
            original=originals[row['file']]
            assert original['ok'] and not original['disconnected'],row['file']
            assert row['triangles']==original['tris'] and row['materials']==1,row['file']
            assert row['packed_palette'] and not row['coplanar'],row['file']
            assert abs(row['min_z_m'])<=.00001,row['file']
            assert max(abs(a-b) for a,b in zip(row['studs'],original['dimensions_studs']))<.001,row['file']

if __name__=='__main__':main()
