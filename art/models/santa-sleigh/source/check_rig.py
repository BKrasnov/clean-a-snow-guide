"""Check skinning, rein endpoints and articulation, then round-trip the rest rig."""
from pathlib import Path
from math import radians
import json,sys,bpy
from mathutils import Matrix
asset=Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(asset.parent/'starter-farmhouse/source'))
from check_surface_overlap import audit
ob=bpy.data.objects['SantaSleigh_Body']; rig=ob.find_armature()
assert rig and ob.parent==rig
vs=ob.data.vertices
assert all(abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in vs)
assert max(len(v.groups) for v in vs)==2
assert set(g.name for g in ob.vertex_groups)==set(b.name for b in rig.data.bones)-{'Root'}
base=ob.data
probes=[
 {'Santa_Head':(0,12,0),'Santa_Forearm_R':(18,0,0),'Santa_Hand_L':(-8,0,0),'Deer_R_ForeUpper_R':(0,0,27),'Deer_R_ForeLower_R':(0,0,-42),'Deer_L_Head':(0,-15,0),'Deer_L_HindUpper_L':(0,0,-19),'Deer_R_Neck':(0,0,-9)},
 {'Sleigh':(0,1,0),'Santa_Spine':(-4,0,0),'Santa_Forearm_L':(14,0,0),'Deer_L_ForeUpper_L':(0,0,-22),'Deer_R_HindUpper_R':(0,0,16),'Deer_L_Tail':(9,0,0)}
]
report={'triangles_budget':4000,'bones':len(rig.data.bones),'maximum_weights_per_vertex':2,'probe_poses':[]}
for angles in probes:
    for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
    for name,xyz in angles.items():
        p=rig.pose.bones[name];p.rotation_mode='XYZ';p.rotation_euler=[radians(a) for a in xyz]
    bpy.context.view_layer.update()
    obj_eval=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    posed=bpy.data.meshes.new_from_object(obj_eval)
    delta=max((a.co-b.co).length for a,b in zip(base.vertices,posed.vertices))
    assert delta>.05
    ob.data=posed
    surfaces=audit(.002,True,'SantaSleigh')
    ob.data=base;bpy.data.meshes.remove(posed)
    assert surfaces['overlapping_face_pairs']==0, surfaces
    report['probe_poses'].append({'bones_rotated':list(angles),'max_displacement_m':round(delta,3),'overlapping_face_pairs':surfaces['overlapping_face_pairs']})
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True);ob.select_set(True);bpy.context.view_layer.objects.active=rig
fbx=asset/'export/SantaSleigh.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='Z',axis_up='Y',apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
count=len(vs);bones={b.name for b in rig.data.bones}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(fbx))
mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
assert mesh.find_armature() and {b.name for b in mesh.find_armature().data.bones}==bones
assert len(mesh.data.vertices)==count and all(v.groups for v in mesh.data.vertices)
mesh.data.calc_loop_triangles();assert len(mesh.data.loop_triangles)<=4000 and any(i.packed_file for i in bpy.data.images)
report['fbx_roundtrip']={'vertices':count,'bones':len(bones),'triangles':len(mesh.data.loop_triangles),'embedded_palette':True}
(asset/'reports/rig.json').write_text(json.dumps(report,indent=2)+'\n')
