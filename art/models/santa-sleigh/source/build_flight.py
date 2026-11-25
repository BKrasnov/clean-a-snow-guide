"""Author an airborne gallop on the original bind rig, then verify and preview it."""
from math import cos, sin, pi, radians
from pathlib import Path
import bpy, sys, json
from mathutils import Quaternion, Vector
asset=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(asset.parent/'starter-farmhouse/source'))
from render_farmhouse import camera,light
from check_surface_overlap import audit

scene=bpy.context.scene
rig=bpy.data.objects['SantaSleigh_Rig']; mesh=bpy.data.objects['SantaSleigh_Body']
period=32
scene.render.fps=24
action=bpy.data.actions.new('SantaSleigh_Flight')
rig.animation_data_create().action=action
def turn(name,pitch=0,roll=0,yaw=0):
    p=rig.pose.bones[name]
    axes=p.bone.matrix_local.to_quaternion()
    q=(Quaternion((0,0,1),radians(yaw)) @ Quaternion((1,0,0),radians(roll))
       @ Quaternion((0,1,0),radians(pitch)))
    p.rotation_mode='QUATERNION';p.rotation_quaternion=axes.inverted() @ q @ axes
    p.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=name)
def move(name,xyz):
    p=rig.pose.bones[name];p.location=p.bone.matrix_local.to_quaternion().inverted() @ Vector(xyz)
    p.keyframe_insert(data_path='location',frame=frame,group=name)

for frame in range(1,period+2,2):
    t=2*pi*(frame-1)/period
    move('Root',(0,0,.64+.058*sin(t-.7)))
    turn('Sleigh',-4.0+1.65*sin(t-.94),.8*cos(t))
    turn('Santa_Spine',3.8+2.5*sin(t-.28))
    turn('Santa_Head',-.8-2.0*sin(t-.60),.6*cos(t),1.6*cos(t))
    for s,tag in [(-1,'R'),(1,'L')]:
        turn('Santa_UpperArm_'+tag,-2.0+3.2*sin(t+s*.21))
        turn('Santa_Forearm_'+tag,2.4+4*sin(t-.45+s*.24))
        turn('Santa_Hand_'+tag,-1.2-2.1*sin(t-.7+s*.24))
        d='Deer_'+tag+'_';u=t+s*.40
        move(d+'Body',(.055*cos(u),0,.29+.11*sin(u)))
        turn(d+'Body',-7+3.7*cos(u),s*.9*sin(u))
        turn(d+'Neck',-4+5*sin(u-.38));turn(d+'Head',3.3-3.7*sin(u-.71))
        turn(d+'Tail',-15-11*sin(u+.65))
        for ln,side in [('R',-.52),('L',.52)]:
            p=u+side
            for leg,upper,lower,foot in [
                ('Fore',-18-37*cos(p),27+25*sin(p-.15),-8-9*sin(p)),
                ('Hind',18+32*cos(p+.41),-25-18*sin(p+.72),11+9*sin(p+.16))]:
                turn(d+leg+'Upper_'+ln,upper);turn(d+leg+'Lower_'+ln,lower);turn(d+leg+'Hoof_'+ln,foot)
scene.frame_start=1;scene.frame_end=period;scene.frame_set(1)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(asset/'source/SantaSleigh_Flight.blend'))
# Include closing sample in the engine clip.
scene.frame_end=period+1
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True)
bpy.context.view_layer.objects.active=rig
clip=asset/'export/SantaSleigh_Flight.fbx'
bpy.ops.export_scene.fbx(filepath=str(clip),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='Z',axis_up='Y',apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
base=mesh.data;worst=0;minimum=100;overlaps={}
for i in range(1,period+2):
    scene.frame_set(i)
    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    posed=bpy.data.meshes.new_from_object(evaluated)
    coords=[v.co.copy() for v in posed.vertices]
    if i==1:first=coords
    if i==period+1:worst=max((a-b).length for a,b in zip(first,coords))
    minimum=min(minimum,min(v.z for v in coords))
    mesh.data=posed
    test=audit(.002,False,'SantaSleigh');overlaps[i]=test['overlapping_face_pairs']
    mesh.data=base;bpy.data.meshes.remove(posed)
report=dict(frames=period,fps=24,closure_m=worst,min_height_m=minimum,overlaps=overlaps)
(asset/'reports/flight.json').write_text(json.dumps(report,indent=2)+'\n')
assert worst<.0001 and minimum>.1
# Track the rig in the render. The repeating snow patches slide under its shadow.
scene.world=bpy.data.worlds.new('Winter daylight');scene.world.color=(.66,.76,.95)
scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=True
scene.view_settings.view_transform='Khronos PBR Neutral'
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.8))
ground=bpy.context.object
snow=bpy.data.materials.new('Snow');snow.diffuse_color=(.60,.73,.93,1);ground.data.materials.append(snow)
light(scene.collection,'Winter sun',(1,-5,8),(0,0,1),820,5,(1,.94,.86))
light(scene.collection,'Sky fill',(-4,3,6),(0,0,1),490,5,(.75,.89,1))
camera(scene,scene.collection,(4.5,-11,4.2),(-.21,0,1.86),ortho=7.65)
scene.render.resolution_x=720;scene.render.resolution_y=448;scene.render.resolution_percentage=100
scratch=asset.parents[2]/'build/santa-sleigh/flight'
scratch.mkdir(exist_ok=True,parents=True)
# Group wind-carved blue snow shapes into one repeated tile for a seamless pan.
streak=bpy.data.materials.new('Wind-packed snow');streak.diffuse_color=(.43,.59,.80,1)
patches=[]
for tile in range(-5,6):
    for x,y,l,w in [(0,1,1.2,.16),(1.5,-2,.74,.095),(2.7,-.45,.47,.06),(.84,3.2,.8,.10)]:
        xx=tile*4+x
        data=bpy.data.meshes.new('Snow streak')
        data.from_pydata([(-l/2,0,0),(-l*.22,-w/2,0),(l/2,0,0),(l*.17,w/2,0)],[],[(0,1,2,3)])
        o=bpy.data.objects.new('Snow streak',data);scene.collection.objects.link(o);o.data.materials.append(streak)
        patches.append((o,xx,y))
for i in range(1,period+1,2):
    scene.frame_set(i)
    for o,x,y in patches:o.location=(x-4*(i-1)/period,y,-.793)
    scene.render.filepath=str(scratch/f'{i:02}.png');bpy.ops.render.render(write_still=True)
