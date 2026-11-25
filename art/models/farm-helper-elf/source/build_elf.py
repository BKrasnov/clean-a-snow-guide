"""Model the approved classic helper in bind T-pose; author three FK actions using two-link solves."""
from pathlib import Path
from math import sin,cos,pi,sqrt,radians
import sys,json
import bpy
from mathutils import Vector,Quaternion,Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT.parent/'starter-farmhouse/source'))
import build_farmhouse as kit
from check_surface_overlap import audit
from render_farmhouse import camera,light
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.render.fps=24;sc.unit_settings.system='METRIC'
S=.48
kit.MODEL='FarmHelper';kit.COLORS=dict(green='#54A577',pine='#3C8E63',red='#D6392B',snow='#FFFDF5',hair='#80401B',boot='#966240',ink='#2B1A11',skin='#F2C29A',rose='#CD925C',gold='#FFCE43',steel='#A0B0C4',tongue='#CE9ED2')
group=kit.collection('FarmHelper',sc.collection);surf=kit.palette()
bones={};body=kit.Mesh('FarmHelper_Body',group,surf);tool=kit.Mesh('Snow scoop',group,surf)
m=body;assign={body:[],tool:[]}
def bone(name,h,t,parent=None):
    global active
    active=name;bones[name]=(Vector(h),Vector(t),parent);return name
def paint(fn,*args):
    before=len(m.vertices);fn(*args);assign[m].extend([active]*(len(m.vertices)-before))
def box(x,y,z,l,w,h,c):paint(m.box,(x,y,z),(l,w,h),c)
def panel(points,y,depth,c):paint(m.prism,points,y-depth/2,y+depth/2,'Y',c)
def rings(rows,cols):
    # Octagonal box sections share faces across successive fabric bands.
    vs=[]
    for x,y,z,w,d,r in rows:
        a,b=w/2,d/2
        vs += [(x+u,y+v,z) for u,v in [(-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r),(a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r)]]
    fs=[tuple(range(7,-1,-1))];cs=[cols[0]]
    for j,c in enumerate(cols):
        for k in range(8):
            i=j*8+k;n=j*8+(k+1)%8;fs.append((i,n,n+8,i+8));cs.append(c)
    fs.append(tuple(range(len(vs)-8,len(vs))));cs.append(cols[-1]);paint(m.add,vs,fs,cols[0]);m.colors[-len(cs):]=cs
def stocking(x,y,levels,w,d):
    vs=[(x+a,y+b,z) for z in levels for a,b in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
    fs=[(3,2,1,0),(12,13,14,15)]+[(j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k) for j in range(3) for k in range(4)]
    paint(m.add,vs,fs,'snow');m.colors[-len(fs):]=['snow']*6+['red']*4+['snow']*4

def brick(x,y,z,w,d,h,c,r=.025):
    rings([(x,y,z-h/2,w,d,r),(x,y,z+h/2,w,d,r)],[c])
bone('Root',(0,0,0),(0,0,.18))
bone('Hips',(0,0,.69),(0,0,.88),'Root')
brick(0,0,.674,.55,.338,.17,'pine')
bone('Spine',(0,0,.78),(0,0,1.27),'Hips')
rings([(0,0,.63,.86,.49,.049),(0,0,.716,.85,.485,.045),(0,0,.908,.75,.436,.038),(0,0,1.003,.755,.44,.038),(0,0,1.29,.72,.43,.04)],['red','green','hair','green'])
for x in (-.33,-.11,.11,.33):
    panel([(x-.046,.70),(x+.048,.70),(x+.042,.761),(x-.036,.761)],-.241,.022,'red')
for x in (-.33,-.11,.11,.33):
    panel([(x-.045,.704),(x+.046,.704),(x+.040,.759),(x-.037,.759)],.242,.021,'red')
box(0,-.232,.956,.203,.045,.146,'gold');box(0,-.257,.955,.111,.018,.075,'ink')
panel([(-.27,1.30),(.27,1.30),(.25,1.235),(.155,1.235),(.155,1.19),(.075,1.19),(.075,1.15),(-.075,1.15),(-.075,1.19),(-.155,1.19),(-.155,1.235),(-.25,1.235)],-.214,.041,'snow')
bone('Head',(0,0,1.28),(0,0,1.91),'Spine')
brick(0,-.017,1.611,.728,.569,.589,'skin',.05)
brick(0,.162,1.616,.762,.252,.569,'hair',.045)
for s in (-1,1):
    panel([(s*.33,1.65),(s*.439,1.65),(s*.536,1.739),(s*.573,1.817),(s*.487,1.815),(s*.389,1.763),(s*.33,1.758)],-.004,.165,'skin')
    panel([(s*.27,1.36),(s*.433,1.36),(s*.49,1.419),(s*.49,1.504),(s*.421,1.504),(s*.421,1.604),(s*.30,1.604)],.003,.359,'hair')
    box(s*.154,-.306,1.635,.128,.034,.148,'ink')
    box(s*.134,-.325,1.674,.049,.017,.05,'snow')
    box(s*.246,-.304,1.51,.093,.022,.030,'rose')
    panel([(s*.34,1.824),(s*.116,1.824),(s*.116,1.776),(s*.19,1.776),(s*.19,1.744),(s*.276,1.744),(s*.276,1.713),(s*.34,1.713)],-.274,.118,'hair')
box(0,-.316,1.558,.080,.066,.044,'skin')
panel([(-.112,1.496),(.112,1.496),(.112,1.448),(.076,1.415),(-.07,1.415),(-.112,1.45)],-.304,.024,'ink')
box(.006,-.320,1.438,.100,.020,.029,'tongue')
brick(0,0,1.856,.87,.701,.137,'snow',.045)
# Single stepped cap profile, front and back are continuous surfaces.
cap=[(-.395,1.915),(.258,1.915),(.258,1.968),(.39,1.968),(.39,1.887),(.522,1.887),(.522,1.82),(.639,1.82),(.639,1.968),(.563,1.968),(.563,2.058),(.461,2.058),(.461,2.153),(.346,2.153),(.346,2.255),(.22,2.255),(.22,2.339),(-.028,2.339),(-.028,2.285),(-.147,2.285),(-.147,2.207),(-.251,2.207),(-.251,2.124),(-.327,2.124),(-.327,2.027),(-.395,2.027)]
def hat_depth(x,z):
    return max(.15,.54-.43*max(0,x)-.32*max(0,z-1.94))
hatverts=[(x,.02+max(0,x)*.28+side*hat_depth(x,z)/2,z) for side in (-1,1) for x,z in cap]
nc=len(cap)
paint(m.add,hatverts,[tuple(reversed(range(nc))),tuple(range(nc,2*nc))]+[(i,(i+1)%nc,nc+(i+1)%nc,nc+i) for i in range(nc)],'red')
brick(.647,.200,1.798,.19,.199,.176,'snow',.028)
for s,tag in [(-1,'R'),(1,'L')]:
    x=s*.194
    bone('Thigh_'+tag,(x,0,.694),(x,0,.411),'Hips')
    stocking(x,-.006,(.413,.495,.557,.701),.217,.241)
    bone('Shin_'+tag,(x,0,.411),(x,0,.146),'Thigh_'+tag)
    stocking(x,.002,(.148,.25,.327,.423),.185,.208)
    bone('Foot_'+tag,(x,0,.146),(x,-.175,.084),'Shin_'+tag)
    paint(m.prism,[(-.248,.0),(.139,.0),(.139,.207),(-.082,.207),(-.082,.155),(-.166,.155),(-.166,.201),(-.201,.24),(-.248,.23),(-.257,.183)],x-.121,x+.121,'X','hair')
    bone('UpperArm_'+tag,(s*.335,0,1.228),(s*.593,0,1.228),'Spine')
    box(s*.461,0,1.228,.27,.214,.230,'green')
    bone('Forearm_'+tag,(s*.593,0,1.228),(s*.811,0,1.228),'UpperArm_'+tag)
    box(s*.670,.002,1.228,.157,.184,.204,'green')
    box(s*.775,.001,1.229,.095,.23,.243,'snow')
    bone('Hand_'+tag,(s*.811,0,1.228),(s*.96,0,1.228),'Forearm_'+tag)
    brick(s*.89,-.002,1.229,.175,.21,.2,'skin',.019)
# Separate shovel follows a control in the same rig; hidden inside torso outside Dig.
m=tool;bone('Scoop',(0,0,.10),(0,0,.4),'Root')
box(0,.002,.52,.045,.032,.91,'boot')
box(0,0,.989,.154,.067,.05,'hair')
panel([(-.146,.24),(.146,.24),(.176,-.008),(.13,-.074),(-.13,-.074),(-.176,-.008)],-.010,.071,'steel')
tool.vertices=[(x,y,z+.10) for x,y,z in tool.vertices]
meshes=[]
for part in (body,tool):
    part.vertices=[tuple(k*S for k in p) for p in part.vertices]
    o=part.object();meshes.append(o)
    for name in dict.fromkeys(assign[part]):
        g=o.vertex_groups.new(name=name);g.add([i for i,n in enumerate(assign[part]) if n==name],1,'REPLACE')
arm=bpy.data.armatures.new('FarmHelper');rig=bpy.data.objects.new('FarmHelper_Rig',arm);group.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for name,(h,t,parent) in bones.items():
    b=arm.edit_bones.new(name);b.head=h*S;b.tail=t*S
    if parent:b.parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
for o in meshes:
    o.parent=rig;mod=o.modifiers.new('Skin','ARMATURE');mod.object=rig
arm.display_type='STICK'

# Animate absolute bone transforms, solved back into local FK channels. FK keys export directly.
def pose(name,pos,rot,scale=1):
    p=rig.pose.bones[name];rest=p.bone.matrix_local
    mat=Matrix.Translation(Vector(pos)*S) @ rot.to_matrix().to_4x4() @ rest.to_quaternion().to_matrix().to_4x4()
    if scale!=1:mat=mat@Matrix.Scale(scale,4)
    local=p.parent.bone.matrix_local.inverted()@rest if p.parent else rest
    parentmat=absolute[p.parent.name] if p.parent else Matrix.Identity(4)
    p.matrix_basis=local.inverted()@parentmat.inverted()@mat
    absolute[name]=mat
    for prop in ('location','rotation_quaternion','scale'):p.keyframe_insert(data_path=prop,frame=fr,group=name)
def rot(axis,deg):return Quaternion(axis,radians(deg))
I=Quaternion();X=(1,0,0);Y=(0,1,0);Z=(0,0,1)
def solve(first,second,last,a,goal,pole,endrot):
    a=Vector(a);delta=Vector(goal)-a;line=delta.normalized()
    v=bones[first][1]-bones[first][0];w=bones[second][1]-bones[second][0]
    d=min(v.length+w.length-.00005,max(abs(v.length-w.length)+.001,delta.length))
    tangent=Vector(pole)-line*Vector(pole).dot(line);tangent.normalize()
    mid=(v.length**2-w.length**2+d*d)/(2*d)
    b=a+line*mid+tangent*sqrt(max(0,v.length**2-mid**2));c=a+line*d
    q=v.rotation_difference(b-a);p=w.rotation_difference(c-b)
    if first.startswith('UpperArm'):
        normal=line.cross(tangent).normalized()
        def basis(axis,n):
            axis=axis.normalized();return Matrix((axis,n,axis.cross(n))).transposed().to_quaternion()
        q=basis(b-a,normal) @ basis(v,Vector((0,1,0))).inverted()
        p=basis(c-b,normal) @ basis(w,Vector((0,1,0))).inverted()
    pose(first,a,q);pose(second,b,p);pose(last,c,endrot if endrot is not None else p)
    return (c-Vector(goal)).length
periods={'Idle':64,'Walk':32,'Dig':80}
digkeys=[(0,.12,15,-.54,.38,-15),(8,.09,10,-.49,.48,-12),(17,.25,33,-.65,.195,-24),(23,.30,43,-.68,.078,-28),(29,.30,39,-.73,.09,-34),(36,.14,19,-.65,.38,-25),(40,.10,12,-.595,.48,-18),(48,.12,15,-.54,.38,-15)]
def digging(k):
    for j,(a,b) in enumerate(zip(digkeys,digkeys[1:])):
        if a[0]<=k<=b[0]:
            dt=b[0]-a[0];u=(k-a[0])/dt
            def slope(idx,col):
                count=len(digkeys)-1;prev=digkeys[(idx-1)%count];cur=digkeys[idx%count];nxt=digkeys[(idx+1)%count]
                left=(cur[col]-prev[col])/((cur[0]-prev[0])%48)
                right=(nxt[col]-cur[col])/((nxt[0]-cur[0])%48)
                return 2*left*right/(left+right) if left*right>0 else 0
            return [(2*u**3-3*u*u+1)*a[c]+(u**3-2*u*u+u)*dt*slope(j,c)+(-2*u**3+3*u*u)*b[c]+(u**3-u*u)*dt*slope(j+1,c) for c in range(1,6)]
actions={};reach=[]
for clip,N in periods.items():
    ad=rig.animation_data_create();ad.action=None
    action=bpy.data.actions.new(clip);action.use_fake_user=True;action.use_cyclic=True;ad.action=action
    actions[clip]=action
    for k in range(N+1):
        fr=k+1;t=2*pi*k/N
        absolute={};pose('Root',(0,0,0),I)
        dip,lean,tipy,tipz,angle=digging(k*48/N) if clip=='Dig' else (0,0,0,0,0)
        if clip=='Walk':dip=.055+.028*cos(2*t);lean=5
        if clip=='Idle':dip=.015+.011*cos(t);lean=1.6+1.5*sin(t)
        H=Vector((.022*sin(t) if clip=='Walk' else 0,0,.694-dip))
        pose('Hips',H,I)
        torso=rot(X,lean)@rot(Z,4*sin(t) if clip=='Walk' else 0)
        sp=H+Vector((0,0,.086));pose('Spine',sp,torso)
        hd=sp+torso@Vector((0,0,.50))
        pose('Head',hd,rot(X,lean*.60+2*sin(t))@rot(Z,4*sin(t) if clip=='Idle' else 0))
        tip=Vector((0,tipy,tipz))
        qr=rot(X,angle)
        pose('Scoop',tip if clip=='Dig' else sp,qr if clip=='Dig' else I,1 if clip=='Dig' else .001)
        for s,tag in [(-1,'R'),(1,'L')]:
            u=(k/N+(0 if s<0 else .5))%1
            if clip=='Walk':
                if u<.5:y=-.16*cos(2*pi*u);lift=0
                else:
                    f=(u-.5)*2;y=.16*cos(pi*f);lift=.129*sin(pi*f)**2
                foot=Vector((s*.194,y,.146+lift));footrot=rot(X,0 if u<.5 else 6*sin(4*pi*u)*sin(2*pi*u)**2)
            else:
                foot=Vector((s*.194,-.060*s if clip=='Dig' else 0,.146));footrot=I
            solve('Thigh_'+tag,'Shin_'+tag,'Foot_'+tag,H+Vector((s*.194,0,0)),foot,(0,-1,0),footrot)
            shoulder=sp+torso@Vector((s*.335,0,.448))
            if clip=='Dig':
                hand=tip+qr@Vector((s*.09,.025,.67 if s<0 else .94))
            else:
                hand=shoulder+Vector((s*.113,-.053+(.130*cos(2*pi*u) if clip=='Walk' else .016*sin(t)), -.397+.011*cos(t)))
            err=solve('UpperArm_'+tag,'Forearm_'+tag,'Hand_'+tag,shoulder,hand,(s*.95,.40,-.32),None)
            if clip=='Dig':reach.append(err*S)
sc.frame_start=1;sc.frame_end=periods['Idle']
rig.animation_data.action=actions['Idle'];sc.frame_set(1)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
        sp.region_3d.view_location=(0,0,.54);sp.region_3d.view_distance=2.25
        sp.region_3d.view_rotation=Vector((.34,-1,.14)).to_track_quat('Z','Y')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/FarmHelper_master.blend'))
rep={'actions':{},'dig_max_wrist_target_error_m':max(reach)}
for name,N in periods.items():
    rig.animation_data.action=actions[name];sc.frame_end=N+1
    sc.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes+[rig]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.fbx(filepath=str(ROOT/'export'/(name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='Z',axis_up='Y',apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
    overlaps={};first=None
    for i in range(1,N+2):
        sc.frame_set(i);deps=bpy.context.evaluated_depsgraph_get()
        orig=[o.data for o in meshes];posed=[bpy.data.meshes.new_from_object(o.evaluated_get(deps)) for o in meshes]
        coords=[v.co.copy() for geo in posed for v in geo.vertices]
        if first is None:first=coords
        for o,geo in zip(meshes,posed):o.data=geo
        audit_result=audit(.002,i==1,'FarmHelper')
        if audit_result['overlapping_face_pairs']:overlaps[i]=audit_result['overlapping_face_pairs']
        for o,geo,tmp in zip(meshes,orig,posed):o.data=geo;bpy.data.meshes.remove(tmp)
    rep['actions'][name]=dict(frames=N,closure=max((a-b).length for a,b in zip(first,coords)),overlaps=overlaps)
rep['tris']=audit_result['triangles_checked'];rep['bones']=len(bones)
(ROOT/'reports/clips.json').write_text(json.dumps(rep,indent=2)+'\n')
print('RESULT',rep,flush=True)
assert all(not x['overlaps'] and x['closure']<.0001 for x in rep['actions'].values())
if '--checks-only' in sys.argv: sys.exit(0)
sc.render.engine='CYCLES';sc.cycles.samples=5;sc.cycles.use_denoising=True
sc.world=bpy.data.worlds.new('Winter sky');sc.world.color=(.70,.77,.88)
sc.view_settings.view_transform='Khronos PBR Neutral'
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.009))
ground=bpy.context.object;ground.data.materials.append(bpy.data.materials.new('Snow'))
ground.data.materials[0].diffuse_color=(.67,.77,.92,1)
light(sc.collection,'Key',(-2,-3,4),(0,0,.55),165,3,(1,.93,.82))
light(sc.collection,'Fill',(2,1,3),(0,0,.5),100,3,(.78,.88,1))
camera(sc,sc.collection,(1.25,-4.4,1.62),(0,-.03,.55),ortho=1.58)
scratch=ROOT.parents[2]/'build/farm-helper-elf'
rig.data.pose_position='REST';meshes[1].hide_render=True
sc.render.resolution_x=800;sc.render.resolution_y=720;sc.render.resolution_percentage=100
camera(sc,sc.collection,(.66,-4.5,1.17),(0,0,.56),ortho=1.54)
sc.render.filepath=str(ROOT/'preview/helper.png');bpy.ops.render.render(write_still=True)
rig.data.pose_position='POSE';meshes[1].hide_render=False
for n,N in periods.items():
    rig.animation_data.action=actions[n]
    if n=='Dig':camera(sc,sc.collection,(2.9,-3.6,1.80),(0,-.12,.47),ortho=1.52)
    sc.render.resolution_x=480;sc.render.resolution_y=480;sc.render.resolution_percentage=100
    (scratch/n).mkdir(parents=True,exist_ok=True)
    for i in range(0,N,4):
        sc.frame_set(1+i);sc.render.filepath=str(scratch/n/f'{i//4:02}.png');bpy.ops.render.render(write_still=True)
