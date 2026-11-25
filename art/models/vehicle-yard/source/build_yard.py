"""Build the snow-free equipment court in Roblox studs and export in metres."""
from math import cos, exp, pi, sin
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
STUD = .28
WIDTH = 83.15821
DEPTH = 45.44693
# Facing the array from the drive-out, local -Y is Roblox +Z.
ROWS = [
    (-22.723465, -26.7, 29.5), (-21.94, -29.0, 32.4), (-20.30, -32.6, 35.5),
    (-18.50, -36.7, 38.1), (-15.40, -39.3, 40.2), (-12.7, -39.8, 41.1),
    (-9.4, -41.579105, 41.0), (-5.2, -40.85, 41.579105), (-1.4, -40.55, 40.70),
    (2.2, -41.40, 39.9), (7.0, -41.37, 40.8), (11.3, -40.3, 40.6),
    (14.7, -41.35, 41.1), (17.9, -39.8, 39.8), (19.9, -38.1, 37.7),
    (21.0, -33.6, 33.9), (22.0, -27.8, 27.4), (22.723465, -19.5, 19.2),
]
# The four wheeled / tracked vehicles. The aircraft makes no ruts.
TRACKS = [(-21.14, 1.38, 6, .94, 6), (-9.67, 1.34, 3, .87, 8), (-3.01,.87,3, .84, 1),
          (4.50,.88,2, 1, 3), (11.66,.82,6, .87, 7), (18.89,.83,4, .75, 5),
          (28.56,.65,1.5, .37, 10), (34.40,.61,0, .26, 12)]


def palette():
    # Interpolation occurs between approved earth and plank swatches.
    image = bpy.data.images.new('VehicleYard_Palette', 8, 4, alpha=False)
    pixels = []
    for row in range(4):
        for col in range(8):
            color = (('966240' if col < 4 else 'C28E49') if row < 2 else
                     ('80401B' if col < 2 else '966240' if col < 4 else
                      'C28E49' if col < 6 else 'CD925C'))
            pixels.extend([int(color[i:i+2],16)/255 for i in (0,2,4)]+[1])
    image.pixels.foreach_set(pixels)
    image.pack()
    material = bpy.data.materials.new('M_VehicleYard_EarthAndWood')
    material.use_nodes = True
    graphite = material.node_tree
    tex = graphite.nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.extension = 'EXTEND'
    graphite.nodes.active = tex
    bsdf = graphite.nodes.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value = .93
    graphite.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    return material


def mesh_object(name, group, vertices, faces, uv, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x*STUD,y*STUD,z*STUD) for x,y,z in vertices],[],faces)
    mesh.update()
    mesh.materials.append(material)
    layer=mesh.uv_layers.new(name='Palette')
    for face, values in zip(mesh.polygons,uv,strict=True):
        for loop, value in zip(face.loop_indices,values,strict=True):
            layer.data[loop].uv=value
    obj=bpy.data.objects.new(name,mesh)
    group.objects.link(obj)
    return obj


def dirt(group, material):
    rng = random.Random(406)
    # Fixed normalized columns keep the seams shared from row to row.
    column_x = {-WIDTH/2, WIDTH/2, -34.5, -30.4, -26.5, -16.0,
                -6.25, .58, 8.2, 15.1, 23.5, 26.8, 38.9}
    for x, w, *_ in TRACKS:
        column_x.update((x-w-1.08, x-w, x+w, x+w+1.08))
    columns = sorted(x/WIDTH+.5 for x in column_x)
    n = len(columns)
    vertices, faces, uv = [], [], []
    colors = []
    for i,(y,left,right) in enumerate(ROWS):
        for j,u in enumerate(columns):
            inner = 0 < i < len(ROWS)-1 and 0 < j < n-1
            mx = (u-.5)*WIDTH
            travel = (max(0,-y-4)/19)**1.6
            sweep = (-7*exp(-((mx+18)/12)**2) + 3.6*exp(-((mx-13)/12)**2))
            shift = sweep * travel * (1-abs(mx)/42)
            x = left + (right-left)*u + shift
            yy = y
            vertices.append((x,yy,-.17 if not inner else 0))
            weights = [brightness*max(0,min(1,(w+1.05-abs(mx-pos))/1.00))*
                       max(0,min(1,(end+3-y)/7))*(.85+.15*cos(y*.175+phase))
                       for pos,w,end,brightness,phase in TRACKS]
            # Broad tone patches and visibly worn lanes are part of the surface.
            tone=.23+.09*sin(mx*.113+yy*.34)**2+rng.uniform(-.06,.065)+max(weights)*.73
            colors.append(tone)
    for i in range(len(ROWS)-1):
        for j in range(n-1):
            a=i*n+j
            quad=(a,a+1,a+n+1,a+n)
            tris=((0,1,2),(0,2,3)) if (i+j)%2 else ((0,1,3),(1,2,3))
            for slice_ in tris:
                face=tuple(quad[k] for k in slice_)
                faces.append(face)
                x=sum(vertices[k][0] for k in face)/3
                y=sum(vertices[k][1] for k in face)/3
                patch=0
                for px,py,rx,ry,shade in [(-28,-8,7.8,2.4,.11),(-7,10,5,3.3,.14),
                                         (22,-13,6.1,2.3,.13),(29,9.5,5.25,2.8,-.12)]:
                    if abs(x-px)/rx+abs(y-py)/ry<1:
                        patch+=shade
                uv.append([((3.5+max(.015,min(.985,colors[k]+patch)))/8,.25) for k in face])
    last=(len(ROWS)-1)*n
    perimeter=list(range(n))+[i*n+n-1 for i in range(1,len(ROWS))]
    perimeter+=list(range(last+n-2,last-1,-1))+[i*n for i in range(len(ROWS)-2,0,-1)]
    ring=len(vertices)
    vertices.extend((vertices[i][0],vertices[i][1],-.43513) for i in perimeter)
    for k,index in enumerate(perimeter):
        following=(k+1)%len(perimeter)
        faces.append((perimeter[following],index,ring+k,ring+following))
        uv.append([(.4375,.25)]*4)
    # Fan triangulation from the centre of the closed underside.
    tip=len(vertices)
    vertices.append((0,0,-.43513))
    for k in range(len(perimeter)):
        faces.append((tip,ring+(k+1)%len(perimeter),ring+k))
        uv.append([(.4375,.25)]*3)
    obj=mesh_object('VehicleYard_Ground',group,vertices,faces,uv,material)
    obj['RobloxStudMeters']=STUD
    obj['ExistingParkingSpanStuds']=[WIDTH,DEPTH]
    obj['Front']='Local -Y / Roblox +Z'
    return obj


def edging(group,material):
    rng=random.Random(14)
    # Groups of short log ends along the outer shoulders; no obstacle in the drive-out.
    positions=[(-37.3,-16.9),(-38.1,-15.1),(-39.0,-13.35),
               (-39.5,2.8),(-39.8,4.7),(-39.6,6.65),
               (-33.8,19.5),(-31.6,20.0),
               (30.0,19.9),(32.0,19.55),
               (38.85,11.1),(39.4,9.35),(39.25,7.4),
               (38.6,-13.4),(37.8,-15.2),(36.5,-16.8)]
    colors={key:((index+.5)/8,.75) for key,index in
            [('bark',1),('woodDark',3),('ring',5),('inner',7)]}
    vertices,faces,uv=[],[],[]
    for x,y in positions:
        count=7
        r=rng.uniform(.68,.89)
        height=rng.uniform(.245,.395)
        phase=rng.random()*pi
        corners=[(cos(phase+i*2*pi/count),sin(phase+i*2*pi/count),rng.uniform(.91,1.08))
                 for i in range(count)]
        base=len(vertices)
        levels=[(1,-.24),(1,height-.08),(.88,height),(.67,height+.014),(.40,height+.014)]
        for radius,z in levels:
            vertices.extend((x+r*radius*vx*factor,y+r*radius*vy*factor,z)
                            for vx,vy,factor in corners)
        for layer,shade in enumerate(('bark','woodDark','inner','ring')):
            for i in range(count):
                a=base+layer*count+i
                b=base+layer*count+(i+1)%count
                faces.append((a,b,b+count,a+count))
                uv.append([colors[shade]]*4)
        for level, shade in [(0,'bark'),(4,'inner')]:
            middle=len(vertices)
            vertices.append((x,y,levels[level][1]))
            for i in range(count):
                a=base+level*count+i
                b=base+level*count+(i+1)%count
                faces.append((middle,b,a) if level==0 else (middle,a,b))
                uv.append([colors[shade]]*3)
    return mesh_object('VehicleYard_LogEnds',group,vertices,faces,uv,material)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    group=bpy.data.collections.new('VehicleYard')
    scene.collection.children.link(group)
    material=palette()
    dirt(group,material)
    edging(group,material)
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.color_type='TEXTURE'
            space.overlay.show_overlays=False
            space.region_3d.view_rotation=Vector((.30,-1,.92)).to_track_quat('Z','Y')
            space.region_3d.view_perspective='ORTHO'
            space.region_3d.view_distance=23
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'VehicleYard.blend'),compress=True)
    export=ASSET/'export'
    export.mkdir(exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(export/'VehicleYard.glb'),
                              export_format='GLB',export_animations=False,export_extras=True)


if __name__=='__main__':
    main()
