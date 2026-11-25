"""Review the furnished building with its real roof in place."""
from pathlib import Path
import sys
import bpy
from mathutils import Vector

here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(here.parents[1]/'starter-farmhouse/source'))
from render_farmhouse import camera, light, render

scene=bpy.context.scene
group=scene.collection
out=here.parent/'preview'
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Winter sky')
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.48,.59,.76,1);bg.inputs[1].default_value=.72
scene.view_settings.view_transform='Khronos PBR Neutral'
scene.view_settings.look='None'
scene.view_settings.exposure=-1.02
light(group,'Soft winter sun',(-5,-8,11),(0,0,1),2400,7,(1,.91,.81))
light(group,'Sky fill',(6,-3,9),(0,0,2),1700,7,(.72,.87,1))
light(group,'Back light',(-2,6,10),(0,0,2),1800,6,(.88,.94,1))
for i,(x,y) in enumerate([(-2.58,.67),(0,2.67),(2.6,.64)]):
    light(group,'Lantern light '+str(i),(x,y-.15,2.85),(0,0,0),36,.36,(1,.73,.36),'POINT')
light(group,'Hall bounced light',(-.4,-2.19,2.90),(0,2.85,.9),245,4,(.78,.90,1))
light(group,'Gift fill',(1.42,.64,2.79),(0,1.9,.66),85,2,(1,.90,.74))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.049))
mat=bpy.data.materials.new('Studio backdrop');mat.diffuse_color=(.54,.64,.79,1)
bpy.context.object.data.materials.append(mat)
camera(scene,group,(2.6,-16,6.1),(0,-.1,2.48),ortho=11.9)
render(scene,out,'exterior',(1200,850))
scene.frame_set(36)
camera(scene,group,(0,-3.06,1.64),(0,1.65,1.48),lens=14.1)
render(scene,out,'interior',(1250,780))
camera(scene,group,(-2.1,-7.2,16.1),(0,-.49,1.6),ortho=15.5)
bpy.data.collections['Removable roof'].hide_render=True
render(scene,out,'open-roof',(1100,850))
