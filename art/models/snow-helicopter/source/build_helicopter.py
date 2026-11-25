"""Ice-blue cyclone helicopter. Dimensions in studs, nose towards -Y."""
from pathlib import Path
from math import sin,cos,pi
import bpy,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(here.parents[1]/'snow-storage/source'))
import build_storage as s
f=s.farm
bpy.ops.wm.read_factory_settings(use_empty=True)
f.MODEL='SnowHelicopter'
f.COLORS=dict(ice='#A8DEE7',blue='#80A0E6',gold='#FFCE43',dark='#2B1A11',metal='#A0B0C4',cream='#FFFDF5',snow='#F3F6F5',shadow='#B3C2D4',glazing='#80A0E6')
surf=f.palette()
group=f.collection(f.MODEL,bpy.context.scene.collection)
def mesh(n):return f.Mesh(n,group,surf)
def finish(m):
    m.vertices=[tuple(v*.28 for v in p) for p in m.vertices]
    ob=m.object()
    tint=ob.data.color_attributes.new(name='BaseTint',type='BYTE_COLOR',domain='CORNER')
    for e in tint.data:e.color=(1,1,1,1)
    return ob
def column(m,x,y,profile,colors,n=16):
    s.loft(m,[[(x+r*cos(k*2*pi/n),y+r*sin(k*2*pi/n),z) for k in range(n)] for z,r in profile],colors)
def glass(ob,alpha):
    mat=bpy.data.materials.get('Canopy and collector glass')
    if not mat:
        mat=bpy.data.materials.new('Canopy and collector glass')
        mat.use_nodes=True
        sh=mat.node_tree.nodes['Principled BSDF']
        sh.inputs['Base Color'].default_value=(.39,.73,.80,1)
        sh.inputs['Alpha'].default_value=alpha
        sh.inputs['Roughness'].default_value=.23
        mat.diffuse_color=(.39,.73,.80,alpha)
    ob.data.materials.clear()
    ob.data.materials.append(mat)

m=mesh('Cabin')
# Plan sections follow the windshield rake and taper towards the tail.
sections=[(3.1,1.56,-2.8,2.4),(3.52,2.17,-3.64,3.10),(4.20,2.48,-4.05,3.52),(4.39,2.53,-4.12,3.6),(4.62,2.54,-4.13,3.65),(4.87,2.57,-4.15,3.67),(7.05,2.32,-3.05,3.38),(7.50,1.94,-2.48,2.95),(7.68,1.45,-1.84,2.38)]
def section(w,front,back,z):
    return [(x*w,front+(back-front)*t,z) for x,t in [(0,0),(.69,.035),(.94,.17),(1,.39),(1,.58),(.90,.80),(.62,.95),(0,1),(-.62,.95),(-.90,.80),(-1,.58),(-1,.39),(-.94,.17),(-.69,.035)]]
rings=[section(w,a,b,z) for z,w,a,b in sections]
s.loft(m,rings,['blue','blue','ice','cream','ice','ice','ice','ice'])
# Colour faces of the canopy itself. Pillars are short strips cut into those faces.
for j in (5,6):
    for k in [0,1,2,3,10,11,12,13]:
        idx=1+14*j+k
        m.colors[idx]='dark'
        a,b,c,d=[Vector(m.vertices[i]) for i in m.faces[idx]]
        # Replace existing quad with inset pane and its four adjoining frame faces.
        mid=(a+b+c+d)/4
        inner=[v.lerp(mid,.024) for v in (a,b,c,d)]
        start=len(m.vertices)
        m.vertices.extend(map(tuple,inner))
        old=m.faces[idx]
        m.faces[idx]=tuple(range(start,start+4))
        for h in range(4):
            m.faces.append((old[h],old[(h+1)%4],start+(h+1)%4,start+h))
            m.colors.append('blue')
# Cut three vent slits into each rear side panel, all sharing the skin topology.
for k in (4,9):
    idx=1+14*5+k
    corners=[Vector(m.vertices[i]) for i in m.faces[idx]]
    old=m.faces[idx]
    def patch_point(u,v):
        return tuple(corners[0].lerp(corners[1],u).lerp(corners[3].lerp(corners[2],u),v))
    us=[0,.20,.83,1]
    vs=[0,.21,.31,.41,.51,.61,.71,1]
    inside=[]
    for v in vs[1:-1]:
        row=[]
        for u in us[1:-1]:
            row.append(len(m.vertices))
            m.vertices.append(patch_point(u,v))
        inside.append(row)
    faces=[(old[0],old[1],inside[0][1],inside[0][0]),(inside[-1][0],inside[-1][1],old[2],old[3])]
    cols=['ice','ice']
    for j in range(len(inside)-1):
        a,b=inside[j];d,c=inside[j+1]
        faces.extend([(a,b,c,d),(old[0],a,d),(old[1],c,b)])
        cols.extend(['dark' if j%2==0 else 'ice','ice','ice'])
    faces.extend([(old[0],inside[-1][0],old[3]),(old[1],old[2],inside[-1][1])])
    cols.extend(['ice','ice'])
    m.faces[idx]=faces[0]
    m.faces.extend(faces[1:])
    m.colors.extend(cols[1:])
# Blue daylight in the tinted windshield, with two distinct flat panel tones.
for j in (5,6):
    for k in [0,1,2,3,10,11,12,13]:
        m.colors[1+14*j+k]='glazing'
body=finish(m)
# Baked ambient tint makes the blue windows read darker than the painted belly.
tint=body.data.color_attributes["BaseTint"]
for face in body.data.polygons:
    for loop in face.loop_indices:
        u,v=body.data.uv_layers.active.data[loop].uv
        gu,gv=surf[1]['glazing']
        tint.data[loop].color=(.10,.16,.29,1) if abs(u-gu)+abs(v-gv)<.01 else (1,1,1,1)
mat=surf[0]
graph=mat.node_tree
base=graph.nodes.get('Principled BSDF').inputs['Base Color']
texture=base.links[0].from_socket
mix=graph.nodes.new('ShaderNodeMixRGB')
mix.blend_type='MULTIPLY'
mix.inputs[0].default_value=1
vc=graph.nodes.new('ShaderNodeVertexColor')
vc.layer_name="BaseTint"
graph.links.new(texture,mix.inputs[1])
graph.links.new(vc.outputs['Color'],mix.inputs[2])
graph.links.new(mix.outputs[0],base)
# Windshield tint controlled by a second palette lookup swatch, only on cockpit panels.
# Use the darkest palette base with a blue glass reflection from the sky.
m=mesh('Tail')
s.loft(m,[[(w*cos(i*pi/4),y,z+h*sin(i*pi/4)) for i in range(8)] for y,w,h,z in [(2.85,1.12,.84,5.85),(5.3,.76,.61,6.03),(11.8,.31,.38,6.85)]],['ice','ice'])
m.prism([(10.7,6.74),(12.05,9.06),(12.65,9.06),(12.30,6.83),(12.7,5.42),(12.22,5.43)],-.16,.16,'X','ice')
for y in (2.3,4.1):
    s.tube(m,[(0,y,7.0 if y<3 else 6.46),(0,y+.38,8.01 if y<3 else 7.3)],[.105,.08],'shadow')
finish(m)
m=mesh('LandingSkids')
for side in (-1,1):
    x=side*2.52
    s.tube(m,[(x,y,z) for y,z in [(-4.65,.58),(-4.42,.32),(-4.04,.19),(3.76,.19),(4.14,.26),(4.48,.54)]],[.15,.20,.205,.205,.20,.15],'blue',8)
    for y in (-1.68,1.64):
        s.tube(m,[(x,y*1.48,.26),(side*1.58,y,3.58)],[.17,.22],'metal',8)
        m.box((side*1.60,y,3.22),(.51,.58,.65),'gold')
finish(m)
m=mesh('VacuumBell')
# Continuous inner throat and outer flared lip, with a short blue hose and collar.
column(m,0,-.12,[(.80,.66),(.44,1.04),(.43,1.19),(.55,1.21),(.90,.94),(1.01,.84),(1.05,.90),(1.20,.92),(1.26,.88),(1.37,.86)],['dark','gold','gold','gold','gold','blue','blue','blue','blue'])
m.vertices=[(x,y-.18*(1.37-z),z-.19*(y+.12)) for x,y,z in m.vertices]
finish(m)
m=mesh('CollectorGlass')
column(m,0,-.12,[(1.34,.84),(1.48,.97),(2.80,1.44),(3.16,1.41)],['ice']*3,20)
glass(finish(m),.24)
m=mesh('Snow')
for layer,z,radius,num in [(0,1.74,.46,4),(1,2.31,.82,6),(2,2.84,.90,7)]:
    for k in range(num):
        ang=2*pi*k/num+layer*.65
        x,y=radius*cos(ang),-.12+radius*sin(ang)
        r=.32 if layer==0 else .40
        levels=[(z-r,.13),(z-r*.46,r*.88),(z+r*.30,r),(z+r*.86,r*.55)]
        column(m,x,y,levels,['snow']*3,7)
finish(m)
m=mesh('MainRotor')
column(m,0,0,[(7.63,.93),(7.96,.75),(8.00,.36),(8.52,.34),(8.55,.53),(8.77,.54),(8.86,.45)],['blue','blue','blue','dark','gold','gold'])
for sign in (-1,1):
    s.loft(m,[[(sign*d,y,z) for y,z in [(-w,8.57),(w,8.57),(w,8.69),(-w,8.69)]] for d,w in [(.40,.22),(7.70,.30),(9.25,.25),(9.39,.18)]],['dark','gold','gold'])
finish(m)
m=mesh('TailRotor')
s.tube(m,[(.10,11.84,6.87),(.52,11.84,6.87)],[.29,.25],'gold',12)
for sign in (-1,1):
    s.loft(m,[[(x,11.84+sign*.45*d+y,6.87+sign*.92*d) for x,y in [(.36,-w),(.47,-w),(.47,w),(.36,w)]] for d,w in [(.15,.14),(1.23,.18),(1.52,.16)]],['dark','gold'])
finish(m)
m=mesh('RunningLights')
for x in (-.55,.55):
    m.box((x,-4.035,4.28),(.44,.22,.24),'cream')
finish(m)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        sp=a.spaces.active
        sp.shading.type='MATERIAL'
        sp.region_3d.view_rotation=Vector((1,-.84,.24)).to_track_quat('Z','Y')
        sp.region_3d.view_location=(0,.78,1.26)
        sp.region_3d.view_distance=9
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'SnowHelicopter_master.blend'))
graph.links.new(texture,base)
bpy.ops.export_scene.gltf(export_vertex_color='ACTIVE',export_all_vertex_colors=False,filepath=str(here.parent/'export/SnowHelicopter.glb'))


