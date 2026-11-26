"""Five detachable Christmas decorations. Coordinates in studs, front toward -Y."""
from math import cos, pi, sin, tau
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

ASSET = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ASSET.parent / 'winter-lobby/source'))
import build_lobby as L

V = Vector
S = L.STUD
LAYOUT = {'ChristmasSpruce': (-4.5, 0, 0), 'WrappedGifts': (-.7, -2.5, 0),
          'StringLights': (4.8, .2, 10.8), 'PineGarland': (4.8, .2, 7.4),
          'BellWreath': (5.1, .2, 4.5)}


def radial(m, x, y, levels, colors, sides=12, phase=0):
    m.loft([[(x+r*cos(phase+tau*i/sides), y+r*sin(phase+tau*i/sides), z)
             for i in range(sides)] for z,r in levels],colors)


def jewel(m,center,radii,col,angle=0):
    if not hasattr(jewel,'shape'):
        bm=bmesh.new()
        bmesh.ops.create_icosphere(bm,subdivisions=1,radius=1)
        bm.verts.index_update()
        jewel.shape=([v.co.copy() for v in bm.verts],[tuple(v.index for v in f.verts) for f in bm.faces])
        bm.free()
    points,faces=jewel.shape
    verts=[]
    for vx,vy,vz in points:
        x=vx*radii[0]; y=vy*radii[1]
        verts.append((center[0]+x*cos(angle)-y*sin(angle),center[1]+x*sin(angle)+y*cos(angle),center[2]+vz*radii[2]))
    m.add(verts,faces,col)


def ring(m, center, radius, thickness, depth, col, n=20, sides=6):
    x,y,z=center
    verts=[]
    faces=[]
    for i in range(n):
        a=tau*i/n
        for j in range(sides):
            b=tau*j/sides
            r=radius+thickness*cos(b)
            verts.append((x+r*sin(a),y+depth*sin(b),z+r*cos(a)))
            faces.append((i*sides+j,i*sides+(j+1)%sides,
                          ((i+1)%n)*sides+(j+1)%sides,((i+1)%n)*sides+j))
    m.add(verts,faces,col)


def spruce():
    m=L.new('ChristmasSpruce')
    radial(m,0,0,[(0,1.39),(.10,1.46),(.72,1.55),(.78,1.63),(1.08,1.67),
                  (1.14,1.60),(1.65,1.73),(1.79,1.71),(1.79,1.44),(1.61,1.40)],
           ['oak','wood','bark','bark','earth','wood','oak','oak','earth'],9)
    radial(m,0,0,[(1.59,.74),(2.55,.69),(3.55,.62)],['bark','earth'],8)
    tiers=[(2.80,4.03,4.65),(5.13,3.45,4.08),(7.12,2.82,3.55),(9.02,2.02,2.86)]
    n=16
    for layer,(z,r,h) in enumerate(tiers):
        phase=layer*.21
        def skirt(radius,height,amount):
            pts=[]
            for i in range(n):
                a=phase+tau*i/n
                lobe=cos(5*a+layer*.49)*.16+sin(8*a+layer)*.085
                rr=radius*(1+.039*cos(5*a+layer*.49))
                pts.append((rr*cos(a),rr*sin(a),height+lobe*amount))
            return pts
        levels=[(.88,.10,.85),(1,.28,1),(.99,.48,1),(.86,.29*h,.63)]
        cols=['spruce','pine','pine']
        if layer>=2:
            levels.extend([(.70,.45*h,.90),(.71,.50*h,.88),(.66,.58*h,.65),(.085,h,.02)])
            cols.extend(['pine','shade','snow','snow'])
        else:
            levels.append((.07,h,.04))
            cols.append('pine')
        m.loft([skirt(r*rr,z+height,amount) for rr,height,amount in levels],cols)
        count=(7,7,6,4)[layer]
        for j in range(count):
            a=-pi/2+tau*j/count+(.42 if layer%2 else 0)
            height=.27*h
            rr=r*.885
            radius=(.395,.36,.32,.285)[layer]
            jewel(m,(rr*cos(a),rr*sin(a),z+height),(radius*1.11,)*3,
                  'red' if (j+layer)%2 else 'gold',.17*j)
        if layer in (1,3):
            # Two closed scalloped necklaces follow the taper of the boughs.
            def bead_location(a):
                rise=.60-.28*cos(3*(a+pi/2))
                edge_wave=cos(5*a+layer*.49)*.16+sin(8*a+layer)*.085
                # Interpolate the same radial profile as the crown above;
                # offset in front of its facets even at a scalloped hem.
                frac=max(0,min(1,(rise-.48-edge_wave)/(.29*h-.48-.37*edge_wave)))
                rr=r*(.99-.13*frac)*(1+.039*cos(5*a+layer*.49))+.105
                return V((rr*cos(a),rr*sin(a),z+rise))
            pts=[bead_location(tau*i/24) for i in range(24)]
            for j in range(4):
                arc=[pts[(6*j+k)%24] for k in range(7)]
                # Cover the string joins with a bead; terminate inside its volume.
                arc[0]=arc[0].lerp(arc[1],.055)
                arc[-1]=arc[-1].lerp(arc[-2],.055)
                m.tube(arc,.053,'gold',3)
            count=34 if layer==1 else 22
            for j in range(count):
                a=tau*j/count
                p=bead_location(a)
                length=(bead_location(a+tau/count)-p).length
                jewel(m,p,(length*.424,.167,.17),'gold',a+pi/2)
    # Faceted five-point star with raised front and back, narrow gold edge.
    outline=[]
    for i in range(10):
        a=pi/2+pi*i/5
        r=.82 if i%2==0 else .405
        outline.append((r*cos(a),12.18+r*sin(a)))
    verts=[(x,y,z) for y in (-.12,.12) for x,z in outline]+[(0,-.29,12.18),(0,.29,12.18)]
    faces=[]; colors=[]
    for i in range(10):
        j=(i+1)%10
        faces.extend([(i,j,20),(i,i+10,j+10,j),(j+10,i+10,21)])
        colors.extend(['gold' if i%2 else 'sun','orange','gold'])
    m.face_colors(verts,faces,colors)
    return L.finish(m)


def bow(m,x,y,z,size,col,tails=False):
    """Folded loops with a true opening. The knot closes the seam."""
    for side in (-1,1):
        outline=[(.028,.015),(.18,.28),(.42,.47),(.54,.445),(.61,.33),(.56,.13),(.37,.038)]
        loops=[]
        for inset,depth in [(1,-.092),(.53,-.068),(.81,.14)]:
            ringpoints=[]
            for u,v in outline:
                u=.35+(u-.35)*inset; v=.22+(v-.22)*inset
                ringpoints.append((x+side*u*size,y+(depth+.14*v+.11*u)*size,z+v*size))
            loops+=ringpoints
        n=len(outline)
        m.add(loops,[(j*n+i,j*n+(i+1)%n,((j+1)%3)*n+(i+1)%n,((j+1)%3)*n+i)
                     for j in range(3) for i in range(n)],col)
        if tails:
            poly=[(.025,.025),(.16,.012),(.41,-.59),(.28,-.55),(.19,-.64)]
            m.prism([(x+side*u*size,z+v*size) for u,v in poly],
                    y+.038*size,y+.125*size,'Y',col)
    jewel(m,(x,y-.018*size,z+.09*size),(.15*size,.16*size,.15*size),col)


def parcel(m,x,y,size,height,col,ribbon):
    # Ribbon and wrapping share the same outer surface, including the lid.
    for base,top,scale in [(0,height*.74,1),(height*.737,height,1.055)]:
        rings=[]
        for z,factor in [(base,.965),(base+.043,1),(top-.047,1),(top,.966)]:
            a=size/2*scale*factor
            d=a*.86
            c=.065*size
            band=.117*size
            outline=[(-a+c,-d),(-band,-d),(band,-d),(a-c,-d),(a,-d+c),(a,d-c),
                     (a-c,d),(band,d),(-band,d),(-a+c,d),(-a,d-c),(-a,-d+c)]
            rings.append([(x+u,y+v,z) for u,v in outline])
        n=len(outline)
        faces=[tuple(reversed(range(n)))]; cols=[col]
        for j in range(3):
            for k in range(n):
                a=j*n+k;b=j*n+(k+1)%n
                faces.append((a,b,b+n,a+n));cols.append(ribbon if k in (1,7) else col)
        first=3*n
        for cap,color in [([0,1,8,9,10,11],col),([1,2,7,8],ribbon),([2,3,4,5,6,7],col)]:
            faces.append(tuple(first+i for i in cap));cols.append(color)
        m.face_colors([p for layer in rings for p in layer],faces,cols)
    bow(m,x,y,height-.006,size*.82,ribbon)


def gifts():
    m=L.new('WrappedGifts')
    parcel(m,-.17,.39,1.68,1.84,'red','gold')
    parcel(m,-1.10,-.92,1.06,1.08,'pine','cream')
    parcel(m,.47,-1.02,1.25,1.31,'aqua','gold')
    return L.finish(m)


def drop(x,sag):
    return -sag*(1-(x/3.6)**2)


def lights():
    m=L.new('StringLights')
    points=[(x,0,drop(x,.86)-.20) for x in [i*3.46/6 for i in range(-6,7)]]
    m.tube(points,.063,'dark',5)
    for sign in (-1,1):
        m.tube([(sign*(3.45+.096*cos(a)),0,-.016+.16*sin(a))
                for a in [-pi*.56+i*pi*1.66/7 for i in range(8)]],.052,'earth',4)
        m.tube([(sign*3.39,0,-.239),(sign*3.44,0,-.174)],.077,'bark',5)
    for i in range(7):
        x=i*1.00-3.00
        z=drop(x,.86)-.20
        radial(m,x,0,[(z-.76,.067),(z-.69,.192),(z-.51,.265),(z-.40,.249),
                       (z-.234,.144),(z-.212,.166),(z-.015,.128)],
               ['bulb','bulb','bulb','bulb','earth','bark'],7,.17)
    return L.finish(m)


def sprig(m,base,tip,width,col):
    a,b=V(base),V(tip)
    axis=b-a
    side=V((axis.z,0,-axis.x)).normalized()
    mid=a+axis*.48
    front=V((0,-width*.55,0))
    v=[a,mid-side*width,mid+front,mid+side*width,mid-front*.72,b]
    faces=[f for i in range(4) for f in [(0,1+i,1+(i+1)%4),(5,1+(i+1)%4,1+i)]]
    m.add(v,faces,col)


def berries(m,x,y,z,r):
    for i,(dx,dy,dz) in enumerate([(-.92,.06,.55),(.92,.17,.46),(.02,-.29,-.84)]):
        jewel(m,(x+r*dx,y+r*dy,z+r*dz),(r,r,r),'red',i*.38)


def garland():
    m=L.new('PineGarland')
    m.tube([(x,.16,drop(x,1.02)-.06) for x in [i*.69 for i in range(-5,6)]],.105,'earth',4)
    for sign in (-1,1):
        ring(m,(sign*3.45,.15,0),.108,.044,.048,'bark',6,3)
        for i in range(7):
            x=sign*(3.39-i*.485)
            z=drop(x,1.02)
            for j,(dx,dz,w,col) in enumerate([(-.85,.12,.28,'pine'),(-.79,-.32,.34,'mint'),(-.44,-.67,.33,'pine')]):
                if j==0 and i in (0,3,6): continue
                sprig(m,(x,.07-j*.073+i*.006,z+.11),(x+sign*dx,-.045-j*.056+i*.009,z+dz+.032*sin(i)),w,col)
        bow(m,sign*3.04,-.33,-.32,.91,'red',True)
    for x in (-1.95,.02,1.94):
        z=drop(x,1.02)
        berries(m,x,-.33,z-.19,.17)
        m.blob((x-.14,.008,z+.12),(.48,.23,.14),'snow',6,2,.25)
    for x in (-2.76,-1.38,0,1.38,2.76):
        m.box((x,.165,drop(x,1.02)-.044),(.20,.26,.32),'wood')
    return L.finish(m)


def bells(m):
    for j in range(3):
        x=(j-1)*.35; z=-2.97-(.10 if j==1 else 0)
        start=len(m.vertices)
        # Hollow lip, visible inside and clapper.
        radial(m,0,0,[(-.26,.17),(-.32,.217),(-.27,.233),(.13,.122),(.22,.065)],
               ['earth','sun','gold','gold'],7)
        m.blob((0,0,-.323),(.078,.078,.074),'orange',4,2)
        angle=(j-1)*.41
        for k in range(start,len(m.vertices)):
            u,v,w=m.vertices[k]
            m.vertices[k]=(x+u*cos(angle)-w*sin(angle),-.42+v+w*.24,z+u*sin(angle)+w*cos(angle))


def wreath():
    m=L.new('BellWreath')
    ring(m,(0,.065,-1.64),1.06,.235,.14,'earth',13,4)
    ring(m,(0,.07,-.14),.14,.052,.055,'gold',8,3)
    m.box((0,.066,-.32),(.15,.15,.18),'oak')
    for i in range(13):
        a=tau*i/13
        for j,(r0,r1,angle,w,col) in enumerate([(.98,1.52,.64,.32,'spruce' if i%3 else 'mint'),
                                                 (1.20,.76,.68,.32,'pine')]):
            sprig(m,(r0*sin(a),-.025-j*.062,-1.64+r0*cos(a)),
                  (r1*sin(a+angle),-.12-j*.062,-1.64+r1*cos(a+angle)),w,col)
    for a in (-1.05,.14,1.24):
        x=1.17*sin(a);z=-1.64+1.17*cos(a)
        berries(m,x,-.337,z-.10,.113)
        m.blob((x-.064,-.09,z+.17),(.254,.165,.115),'snow',7,2)
    for a in (0,2.12,-2.12):
        x=1.06*sin(a);z=-1.64+1.06*cos(a)
        m.beam((x-.22*sin(a),.185,z-.22*cos(a)),(x+.22*sin(a),.185,z+.22*cos(a)),.18,.11,'wood')
    bells(m)
    bow(m,0,-.414,-2.83,1.18,'red',True)
    return L.finish(m)


def soften(obj):
    soft={'ChristmasSpruce':('pine','spruce','snow','shade','gold','red'),
          'StringLights':('bulb',),'PineGarland':('pine','mint','red','snow'),
          'BellWreath':('pine','spruce','mint','red','snow','gold','sun'),
          'WrappedGifts':()}[obj.name]
    swatches={tuple(round(v,5) for v in L.surface[1][col]) for col in soft}
    mesh=obj.data
    uv=mesh.uv_layers.active
    for p in mesh.polygons:
        if obj.name=='ChristmasSpruce' and p.center.z>11.59*S: continue
        p.use_smooth=tuple(round(v,5) for v in uv.data[p.loop_start].uv) in swatches


def bulb_material(obj):
    # Only the glass swatch emits. The cable and sockets stay matte and the
    # single-material module remains usable separately from the rest of the kit.
    mat=obj.data.materials[0].copy()
    mat.name='Holiday | amber bulbs'
    obj.data.materials[0]=mat
    mask=bpy.data.images.new('Holiday light mask',64,32,alpha=False)
    idx=list(L.plant_mesh.COLORS).index('bulb')
    pixels=[]
    for y in range(32):
        for x in range(64):
            active=(y//8)*8+x//8==idx
            pixels.extend((1,.81,.32,1) if active else (0,0,0,1))
    mask.pixels.foreach_set(pixels);mask.pack()
    graph=mat.node_tree
    node=graph.nodes.new('ShaderNodeTexImage')
    node.image=mask;node.interpolation='Closest'
    shader=graph.nodes.get('Principled BSDF')
    graph.links.new(node.outputs['Color'],shader.inputs['Emission Color'])
    shader.inputs['Emission Strength'].default_value=.70


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    L.collection=bpy.data.collections.new('HolidayDecor')
    bpy.context.scene.collection.children.link(L.collection)
    bpy.context.scene.unit_settings.system='METRIC'
    L.plant_mesh.COLORS={**L.COLORS,'earth':'966240','bulb':'FAD66E'}
    L.surface=L.plant_mesh.palette()
    L.surface[0].name='Holiday | painted wood and pine'
    L.surface[0].node_tree.nodes.get('Image Texture').image.name='Holiday palette'
    objects=[spruce(),gifts(),lights(),garland(),wreath()]
    for obj in objects: soften(obj)
    bulb_material(objects[2])
    for obj in objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(ASSET/'export'/(obj.name+'.glb')),export_format='GLB',
                                  use_selection=True,export_animations=False)
        obj.location=V(LAYOUT[obj.name])*S
    bpy.ops.object.select_all(action='DESELECT')
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.color_type='TEXTURE'
            space.overlay.show_overlays=False
            space.region_3d.view_rotation=V((.02,-1,.11)).to_track_quat('Z','Y')
            space.region_3d.view_location=(0,0,1.76)
            space.region_3d.view_distance=8
            space.region_3d.view_perspective='ORTHO'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET/'source/HolidayDecor.blend'),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSET/'export/HolidayDecor.glb'),export_format='GLB',export_animations=False)


if __name__=='__main__':
    main()
