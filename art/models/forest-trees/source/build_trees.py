"""Four static forest meshes, authored in tree-height units and exported in metres."""
from math import cos, sin, tau
from pathlib import Path
from random import Random
import sys
import bmesh
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ASSET.parent/'garden-plants/source'))
from plant_mesh import Plant,palette

STUD=.28
NAMES=('Spruce','ScotsPine','SilverBirch','Oak')
HEIGHTS=(16,19,15,14)
POSITIONS=(-24,-9,7,24)

def trunk(m,sections,color,root_radius,marks=False,phase=.15):
    """Shared fluted buttresses taper into a single trunk. Bark scars replace surface faces."""
    n=12 if marks or root_radius==0 else 20
    rings=[]
    for j,(x,y,z,r) in enumerate(sections):
        row=[]
        for k in range(n):
            a=tau*k/n+phase
            step=3 if n==12 else 4
            lobe=(1 if k%step==0 else .08)*(.87+.13*cos(3*a))
            foot=max(0,1-z/.15)
            extension=root_radius*lobe*foot**1.5
            rad=r*(1+.035*sin(3*a+j*.3))+extension
            lift=.012*(1-lobe)*foot if root_radius else 0
            if j==0 and k%step==0:
                lift=0
            row.append(Vector((x+rad*cos(a),y+.88*rad*sin(a),z+lift)))
        rings.append(row)
    verts=[]
    faces=[]
    shades=[]
    def push(row):
        base=len(verts)
        verts.extend(row)
        return [base+k for k in range(n)]
    def band(a,b,colors):
        for k in range(n):
            nxt=(k+1)%n
            faces.append((a[k],a[nxt],b[nxt],b[k]))
            shades.append(colors[k])
    prev=push(rings[0])
    hub=len(verts)
    verts.append(Vector((*sections[0][:2],sections[0][2]+.001)))
    for k in range(n):
        faces.append((hub,prev[(k+1)%n],prev[k]))
        shades.append(color)
    for j,(low,high) in enumerate(zip(rings,rings[1:])):
        if marks and (j>0 or root_radius==0):
            # Two asymmetric wedges wrap around adjacent facets. Both borders share vertices
            # with the ivory bark so markings cannot flicker or detach from the surface.
            start=(j*5+(2 if root_radius else 0))%n
            width=[.016]*n
            height=[.38+.085*sin(k+j) for k in range(n)]
            dark=set()
            for off in [0,6]:
                for i,w in enumerate([.012,.16,.25,.024]):
                    idx=(start+off+i)%n
                    width[idx]=w*(.74 if off else 1)
                    height[idx]+=.23 if off else 0
                    if i<3:
                        dark.add(idx)
            lower=push([a.lerp(b,h-w/2) for a,b,h,w in zip(low,high,height,width)])
            upper=push([a.lerp(b,h+w/2) for a,b,h,w in zip(low,high,height,width)])
            band(prev,lower,[color]*n)
            band(lower,upper,['dark' if k in dark else color for k in range(n)])
            prev=upper
        new=push(high)
        band(prev,new,[color]*n)
        prev=new
    faces.append(tuple(prev))
    shades.append(color)
    m.face_colors(verts,faces,shades)

def umbrella(m,center,radii,shade,seed,scalloped=False):
    """A shallow or domed crown with a continuous faceted underside and irregular rim."""
    x,y,z=center
    rx,ry,rz=radii
    rng=Random(seed)
    n=12 if scalloped else 11
    shape=[rng.uniform(.89,1.09) for _ in range(n)]
    start=rng.random()*tau
    verts=[(x+.04*rx,y,z-.57*rz)]
    profiles=[(.71,-.43,.04),(1,-.18,0),(.86,.37,.12),(.49,.78,.22)]
    for ring,(radius,h,twist) in enumerate(profiles):
        for k in range(n):
            a=start+tau*k/n+twist
            edge=(.22 if k%2==0 else -.27) if scalloped and ring==1 else 0
            verts.append((x+rx*shape[k]*radius*cos(a),y+ry*shape[k]*radius*sin(a),
                          z+rz*(h+edge+rng.uniform(-.08,.08))))
    top=len(verts)
    verts.append((x-.08*rx,y+.04*ry,z+rz))
    faces=[]
    for k in range(n):
        a,b=1+k,1+(k+1)%n
        faces.append((0,b,a))
        for j in range(len(profiles)-1):
            faces.append((a,b,b+n,a+n))
            a,b=a+n,b+n
        faces.append((a,b,top))
    if scalloped:
        m.add(verts,faces,shade)
    else:
        # Five faces per sector, from shaded underside to sunlit upper crown.
        shades=[col for k in range(n) for col in ('deep','deep','green','leaf','lime')]
        m.face_colors(verts,faces,shades)

def spruce(m):
    trunk(m,[(0,0,0,.057),(0,0,.04,.055),(.003,0,.11,.047),(0,0,.36,.042),
             (0,0,.68,.020)],'bark',.092)
    for i,(z,upper,r,shade) in enumerate([(.184,.634,.305,'deep'),(.355,.765,.244,'green'),
            (.540,.888,.192,'green'),(.700,1,.137,'lime')]):
        n=13
        rng=Random(42+i)
        phi=i*.40
        verts=[]
        outline=[rng.uniform(.91,1.07) for _ in range(n)]
        dips=[(.024 if k%2 else -.017)+rng.uniform(-.009,.009) for k in range(n)]
        for layer,(radius,h,shift) in enumerate([(.17,.017,0),(1,0,0),(.71,.31,.003),(.27,.75,.022)]):
            for k in range(n):
                a=phi+tau*k/n
                if layer==0:
                    zz=z+.018
                else:
                    zz=z+(upper-z)*h+dips[k]*(1. if layer==1 else .25)
                verts.append((r*radius*outline[k]*cos(a)+shift, r*.94*radius*outline[k]*sin(a),zz))
        verts.append((.065 if i==3 else .026,.018,upper))
        faces=[tuple(reversed(range(n)))]
        for j in range(3):
            for k in range(n):
                a=j*n+k;b=j*n+(k+1)%n
                faces.append((a,b,b+n,a+n))
        faces.extend((3*n+k,3*n+(k+1)%n,4*n) for k in range(n))
        m.add(verts,faces,shade)

def branch(m,points,radii,shade='bark',sides=7):
    m.tube(points,radii,shade,sides=sides)

def pine(m):
    trunk(m,[(0,0,0,.052),(.003,.004,.033,.047),(-.012,.004,.107,.053),
        (-.02,0,.285,.045),(-.004,.005,.52,.035),(.008,.005,.70,.033),
        (.034,.009,.79,.029),(.085,.026,.88,.016)],'wood',.124)
    branch(m,[(-.004,0,.40),(.055,-.014,.448),(.090,-.022,.486)],[.028,.016,.003],'wood',6)
    for pts,rs in [
        ([(.007,.006,.57),(-.080,-.005,.658),(-.212,-.025,.735)],[.033,.024,.012]),
        ([(.013,.008,.60),(.119,.012,.652),(.227,.018,.710)],[.031,.023,.011]),
        ([(.028,.007,.766),(-.010,.021,.84),(-.035,.030,.892)],[.026,.015,.009])]:
        branch(m,pts,rs,'wood')
    umbrella(m,(-.208,-.022,.753),(.187,.139,.076),'green',31)
    umbrella(m,(.226,.012,.718),(.146,.131,.061),'green',32)
    umbrella(m,(.075,.03,.908),(.245,.182,.092),'lime',33)

def birch(m):
    s=[(0,0,0,.052),(-.002,0,.043,.046)]
    for k in range(1,10):
        z=.045+k*.061
        s.append((-.009*sin(8*z),.008*sin(4*z),z,.042-.029*z))
    s.append((.010,.004,.632,.014))
    trunk(m,s,'cream',.136,marks=True,phase=-.12)
    limbs=[
        ([(.005,0,.44),(.079,-.009,.52),(.155,-.004,.62),(.218,-.012,.68)],[.041,.03,.021,.011]),
        ([(-.006,0,.56),(-.092,.002,.626),(-.176,.028,.692),(-.215,.04,.733)],[.036,.029,.020,.012]),
        ([(.005,0,.55),(.044,.121,.64),(.092,.163,.76)],[.032,.023,.012]),
        ([(.002,.005,.57),(-.035,-.108,.67),(-.048,-.14,.78)],[.032,.020,.012]),
        ([(0,0,.602),(.03,.008,.746),(-.006,.014,.90)],[.03,.023,.012])]
    for i,(pts,rs) in enumerate(limbs):
        if i<2:
            sections=[(*p,r) for p,r in zip(pts,rs)]
            x,y,z,r=sections[0]
            sections[0]=(x,y,z-.018,r*.45)
            trunk(m,sections,'cream',0,marks=True,phase=.24*i)
        else:
            branch(m,pts,rs,'cream')
    crowns=[(-.206,.029,.68,.164,.111,.115,'leaf'),(.205,-.006,.659,.161,.114,.119,'green'),
            (.13,.12,.719,.145,.107,.118,'green'),(-.12,-.09,.737,.153,.113,.126,'lime'),
            (.100,-.06,.773,.153,.123,.137,'leaf'),(-.112,.073,.798,.15,.115,.128,'green'),
            (.015,.093,.820,.152,.111,.122,'green'),(-.01,.007,.876,.143,.13,.124,'lime')]
    for i,(x,y,z,rx,ry,rz,col) in enumerate(crowns):
        umbrella(m,(x,y,z),(rx,ry,rz),col,70+i,True)
    for i,(x,y,z,direction) in enumerate([(-.19,.026,.69,-1),(.19,-.005,.675,1),
                                            (.108,.12,.747,1),(-.09,-.095,.740,-1)]):
        for j in range(2):
            side=direction*(.082+.041*j)
            base=Vector((x,y,z))
            elbow=base+Vector((side,.045*(-1)**j,-.032))
            end=elbow+Vector((side*.38,.021,-.098-.028*j))
            branch(m,[base,elbow,end],[.010,.006,.0025],'cream',5)
            for k in range(3):
                p=elbow.lerp(end,.15+.35*k)
                tip=p+Vector((direction*(.015+.021*(k%2)),(-1)**(i+j+k)*.023,-.064))
                m.leaf(p,tip,.025,'leaf' if k%2 else 'green',arch=.004)

def oak(m):
    trunk(m,[(0,0,0,.197),(-.001,.005,.052,.173),(.012,.005,.149,.134),
             (-.018,0,.293,.123),(-.072,.012,.427,.107),(-.084,.023,.565,.063)],
          'bark',.178,phase=.07)
    limbs=[
      ([(.01,0,.23),(.127,.004,.393),(.303,.037,.455),(.483,.041,.548)],[.117,.089,.065,.033]),
      ([(-.028,0,.32),(-.166,-.006,.442),(-.313,-.039,.509),(-.457,-.025,.56)],[.11,.083,.068,.034]),
      ([(-.055,.012,.39),(-.12,.048,.566),(-.074,.071,.733)],[.098,.069,.034]),
      ([(.08,.02,.35),(.23,.18,.473),(.30,.24,.643)],[.083,.055,.031]),
      ([(-.13,.01,.43),(-.188,-.163,.543),(-.211,-.213,.681)],[.066,.047,.029])]
    for pts,rs in limbs:
        branch(m,pts,rs,'bark',8)
    lobes=[(-.415,-.002,.553,.263,.248,.192,'lime'),(.43,.039,.548,.266,.216,.175,'green'),
           (-.265,.136,.702,.223,.189,.168,'deep'),(.304,.112,.686,.226,.205,.177,'green'),
           (-.207,-.174,.662,.238,.207,.174,'green'),(-.018,.032,.756,.274,.246,.244,'green'),
           (.091,-.124,.674,.189,.174,.17,'deep')]
    for i,(x,y,z,rx,ry,rz,col) in enumerate(lobes):
        bm=bmesh.new()
        bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        rng=Random(205+i)
        pts=[]
        for vert in bm.verts:
            v=vert.co
            jitter=rng.uniform(.93,1.04)
            pts.append((x+v.x*rx*jitter+.035*v.z,1.17*(y+v.y*ry*jitter),z+v.z*rz*jitter))
        faces=[tuple(v.index for v in f.verts) for f in bm.faces]
        bm.free()
        hues=[]
        for f in faces:
            nz=sum((pts[k][2]-z)/rz for k in f)/len(f)
            if nz<-.42:
                hue='deep'
            elif col=='lime':
                hue='lime' if nz>.63 else 'leaf' if nz>.05 else 'green'
            elif col=='deep':
                hue='green' if nz>.38 else 'deep'
            else:
                hue='leaf' if nz>.74 else 'green'
            hues.append(hue)
        m.face_colors(pts,faces,hues)

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    group=bpy.data.collections.new('Forest Trees')
    scene.collection.children.link(group)
    surface=palette()
    surface[0].name='M_ForestPalette'
    surface[0].node_tree.nodes.active.image.name='ForestPalette'
    trees=[]
    for name,height,fn in zip(NAMES,HEIGHTS,(spruce,pine,birch,oak)):
        mesh=Plant(name,group,surface)
        fn(mesh)
        zs=[v[2] for v in mesh.vertices]
        assert abs(min(zs))<1e-6
        mesh.vertices=[Vector(v)*height*STUD/max(zs) for v in mesh.vertices]
        ob=mesh.object()
        trees.append(ob)
        ob['height_studs']=height
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        bpy.context.view_layer.objects.active=ob
        bpy.ops.export_scene.gltf(filepath=str(ASSET/'export'/(name+'.glb')),export_format='GLB',
                                  use_selection=True,export_extras=True,export_animations=False)
    for ob,x in zip(trees,POSITIONS):
        ob.location.x=x*STUD
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.color_type='TEXTURE'
            space.overlay.show_overlays=False
            space.region_3d.view_rotation=Vector((0,-1,.055)).to_track_quat('Z','Y')
            space.region_3d.view_perspective='ORTHO'
            space.region_3d.view_location=(0,0,2.5)
            space.region_3d.view_distance=24
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'ForestTrees.blend'),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(ASSET/'export/ForestTrees.glb'),export_format='GLB',
                              use_active_scene=True,export_extras=True,export_animations=False)

if __name__=='__main__':
    build()
