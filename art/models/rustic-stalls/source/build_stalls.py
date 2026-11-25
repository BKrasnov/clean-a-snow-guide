"""Build standalone Roblox lobby props from the snowy market concept."""
from math import radians, tan
import os
from pathlib import Path
import random
import sys

import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
LOBBY = ASSET.parent / 'winter-lobby'
sys.dont_write_bytecode = True
sys.path.insert(0, str(LOBBY / 'source'))
import build_lobby as lobby

STUD = lobby.STUD
LAYOUT = {
    'Rewards': (-24.4, -2.2, 24),
    'Upgrades': (-14.4, 0, 16),
    'Leaderboard01': (-6.22, 1.7, 0),
    'Leaderboard02': (0, 1.7, 0),
    'Leaderboard03': (6.22, 1.7, 0),
    'PrizeWheel': (13.6, 0, -16),
    'Classes': (24.2, -2.2, -24),
}


def timber(m, center, size, color, bevel=.085):
    x, y, z = center
    w, d, h = size
    lobby.slab(m, x, y, z-h/2, w, d, h, min(bevel,w/4,d/4), color)


def canopy(m, seed):
    """Use real edge-to-edge timber and a faceted snow cap above it."""
    rng = random.Random(seed)
    pitch = tan(radians(12))
    high = 8.26
    for j in range(9):
        x = (j-4)*1.05 + rng.uniform(-.015,.015)
        y_near = -3.0+rng.uniform(-.21,.21)
        y_far = 2.44+rng.uniform(-.16,.20)
        w = .98+rng.uniform(-.014,.014)
        lower = [(y_near,high+y_near*pitch),(y_far,high+y_far*pitch)]
        upper = [(y,h+.29+rng.uniform(-.036,.025)) for y,h in reversed(lower)]
        m.prism(lower+upper,x-w/2,x+w/2,'X',rng.choice(['oak','wood','oak','earth']))
    for x in (-3.52,.16,3.53):
        m.beam((x,-2.77,high-2.77*pitch-.17),(x,2.21,high+2.21*pitch-.17),
               .24,.25,'bark')
    # Clipped plan with small overhang variation, single lofted snow shell.
    outline = [(-4.61,-2.83),(-3.7,-3.11),(-2.75,-3.02),(-1.9,-3.20),(-.75,-3.08),
               (.35,-3.18),(1.6,-3.10),(2.55,-3.23),(3.47,-3.06),(4.50,-2.98),
               (4.70,-2.58),(4.62,1.96),(4.21,2.30),(2.85,2.45),(1.42,2.36),
               (.03,2.40),(-1.4,2.35),(-2.65,2.47),(-4.36,2.29),(-4.71,1.90)]
    rings=[]
    for sx,sy,dz in [(.947,.96,.227),(1,1,.395),(.96,.95,.707),(.80,.73,.856)]:
        rings.append([(x*sx,y*sy,high+y*sy*pitch+dz+(
            rng.uniform(-.135,.137) if dz>.5 else rng.uniform(-.025,.018)))
                      for x,y in outline])
    m.loft(rings,['shade','snow','snow'])


def label(m, word, font):
    curve = bpy.data.curves.new(word, 'FONT')
    curve.body = word
    curve.font = font
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.resolution_u = 2
    curve.extrude = .027
    curve.size = 1
    obj = bpy.data.objects.new(word, curve)
    bpy.context.scene.collection.objects.link(obj)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    data = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    bm=bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000005)
    bm.to_mesh(data)
    bm.free()
    width = max(v.co.x for v in data.vertices) - min(v.co.x for v in data.vertices)
    height = max(v.co.y for v in data.vertices) - min(v.co.y for v in data.vertices)
    scale = min(5.63/width, .82/height)
    m.add([(v.co.x*scale, -2.57-v.co.z, 6.67+v.co.y*scale) for v in data.vertices],
          [tuple(p.vertices) for p in data.polygons], 'cream')
    bpy.data.meshes.remove(data)
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.curves.remove(curve)


def stall_frame(m, name, font, seed):
    rng=random.Random(seed)
    canopy(m, seed)
    for x,y,height in [(-3.68,-1.93,7.63),(3.69,-1.92,7.66),(-3.66,1.8,8.40),(3.65,1.77,8.39)]:
        timber(m,(x,y,height/2),(.43,.45,height),'oak')
        timber(m,(x,y,.302),(.61,.62,.58),'bark')
    for x in (-3.65,3.65):
        timber(m,(x,-.1,7.42),(.27,3.6,.28),'oak')
        m.beam((x,-1.68,6.04),(x,-.55,7.36),.29,.25,'oak')
        m.beam((x,1.63,6.34),(x,.45,7.35),.29,.25,'wood')
    timber(m,(0,-1.845,7.49),(7.34,.40,.35),'bark',.058)
    for side in (-1,1):
        m.beam((side*3.35,-1.905,5.95),(side*2.38,-1.905,7.30),.25,.27,'wood')
    for j in range(9):
        y=1.84+rng.uniform(-.035,.035)
        height=6.10+rng.uniform(-.15,.21)
        timber(m,((j-4)*.75,y,height/2+.009),(.716,.28,height),
               rng.choice(['wood','oak','bark']))
    for x in (-2.29,2.29):
        m.box((x,-2.075,7.225),(.16,.23,.53),'wood')
    outline=[(-3.26,6.16),(-3.40,6.37),(-3.28,7.09),(-2.99,7.25),
             (3.22,7.21),(3.38,7.03),(3.29,6.31),(3.08,6.13)]
    m.prism(outline,-2.54,-2.19,'Y','bark')
    for x in (-3.03,3.03):
        lobby.disk(m,x,6.68,-2.556,.105,.065,'oak',8)
    label(m,name.upper(),font)


def crate(m,x,y,base,w,h):
    for j in range(3):
        for s in (-1,1):
            m.box((x,y+s*.63,base+(j+.5)*h/3),(w-.12,.18,h/3-.045),'wood' if j%2 else 'oak')
            m.box((x+s*(w/2-.10),y,base+(j+.5)*h/3),(.18,1.07,h/3-.047),'bark' if j==1 else 'wood')
    for s in (-1,1):
        for t in (-1,1):
            timber(m,(x+s*(w/2-.11),y+t*.59,base+h/2),(.22,.20,h),'oak')


def bench(m):
    for i in range(4):
        timber(m,(.01,(i-1.5)*.60-.34,2.40+radians(i-1)),(6.76-.035*i,.575,.24),'oak' if i%2 else 'wood')


def make_stalls(font):
    for ix,name in enumerate(('Rewards','Upgrades','Classes')):
        m=lobby.new(name)
        stall_frame(m,name,font,72+ix)
        bench(m)
        for x in (-1.73,1.73):
            crate(m,x,-.41,0,3.13,2.24)
        if name=='Rewards':
            for x,y,w,paper,ribbon in [(-2.02,-.52,1.83,'red','gold'),(.03,-.17,1.57,'aqua','sun'),
                                       (1.79,-.53,1.29,'orange','cream')]:
                lobby.gift(m,x,y,2.58,w,paper,ribbon)
        if name=='Upgrades':
            timber(m,(0,1.58,4.28),(5.97,.21,2.69),'oak')
            wrench=[(-.14,-.87),(.14,-.87),(.16,.36),(.49,.66),(.46,.94),(.25,1.10),
                    (.17,.76),(-.10,.70),(-.30,.83),(-.28,1.11),(-.50,.92),(-.46,.60),(-.18,.33)]
            m.prism([(a-1.53+b*.28,b+4.32) for a,b in wrench],1.24,1.454,'Y','metal')
            m.beam((-.25,1.29,3.47),(.19,1.29,4.89),.23,.22,'wood')
            timber(m,(.24,1.25,5.02),(.94,.31,.33),'metal')
            m.beam((1.52,1.2,3.55),(1.98,1.2,4.43),.26,.23,'orange')
            m.beam((1.98,1.2,4.47),(2.38,1.2,5.27),.11,.11,'metal')
            for x,col in [(-1.82,'red'),(1.73,'gold')]:
                timber(m,(x,-.52,2.87),(1.39,.87,.59),col)
                m.beam((x-.30,-.52,3.2),(x+.30,-.52,3.2),.13,.15,'dark')
        if name=='Classes':
            for x,coat,legs in [(-1.78,'blue','dark'),(1.77,'red','slate')]:
                # Counter mannequins at approximately 2/3 player scale.
                lobby.figure(m,x,-.29,2.57,3.30,coat,legs)
        obj=lobby.finish(m)
        obj['display_name']=name.upper()


def scoreboard(index, height, accent):
    m=lobby.new(f'Leaderboard{index:02d}')
    for x,j in [(-2.63,0),(2.63,1)]:
        timber(m,(x,.07,(height-.47)/2),(.49,.71,height-.47),'oak' if j else 'wood')
        timber(m,(x,.07,.486),(.70,.92,.96),'bark')
        for z in (1.18,height-1.25):
            lobby.disk(m,x,z,-.31,.104,.075,'bark',8)
    timber(m,(0,.15,.67),(4.79,.82,.51),'bark')
    timber(m,(0,.05,(height-.32)/2+.52),(4.75,.55,height-1.36),'dark')
    timber(m,(0,-.265,height-1.11),(4.55,.065,.94),accent)
    for row in range(7):
        z=1.47+row*(height-3.4)/6
        color='sun' if row==6 else 'slate'
        lobby.disk(m,-1.90,z+.12,-.274,.13,.057,color,9)
        timber(m,(-1.90,-.271,z-.11),(.38,.054,.16),color,.02)
        length=1.25+((row*3+index)%5)*.18
        timber(m,(-1.42+length/2,-.271,z+.04),(length,.054,.12),'slate',.018)
        for k in range(2+row%2):
            timber(m,(1.91-.20*k,-.271,z+.02),(.105,.052,.18),color,.018)
    timber(m,(0,.02,height-.40),(5.96,.95,.45),'wood')
    lobby.body(m,0,.02,[(height-.176,5.90,.96,.15),(height+.026,6.04,1.05,.18),
                        (height+.14,5.73,.93,.18),(height+.22,4.62,.73,.19)],['shade','snow','snow'])
    lobby.finish(m)


def wheel():
    # Preserve the owner's connected wheel model and its visible wood stand.
    source=LOBBY/'source'/'WinterLobby.blend'
    with bpy.data.libraries.load(str(source),link=False) as (available,selected):
        assert 'PrizeWheel_Kiosk' in available.objects
        selected.objects=['PrizeWheel_Kiosk']
    obj=selected.objects[0]
    assert 'wheel_assembly' in obj, 'The source must contain the joined wheel and base'
    lobby.collection.objects.link(obj)
    obj.name='PrizeWheel'
    obj.data.name='PrizeWheel'
    obj.data.materials[0]=lobby.surface[0]
    # Bake the owner's scale and set the pivot on the platform soles.
    coordinates=[obj.matrix_world@v.co for v in obj.data.vertices]
    center=Vector([(min(v[k] for v in coordinates)+max(v[k] for v in coordinates))/2 for k in (0,1)]+
                  [min(v.z for v in coordinates)])
    angle=obj.rotation_euler.z
    from mathutils import Matrix
    inverse_yaw=Matrix.Rotation(-angle,3,'Z')
    for vertex,position in zip(obj.data.vertices,coordinates,strict=True):
        vertex.co=inverse_yaw@(position-center)
    obj.location=(0,0,0)
    obj.rotation_euler=(0,0,0)
    obj.scale=(1,1,1)


def export(obj, dest):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.gltf(filepath=str(dest/(obj.name+'.glb')),export_format='GLB',
                              use_selection=True,export_animations=False)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    lobby.collection=bpy.data.collections.new('RusticStalls')
    scene.collection.children.link(lobby.collection)
    lobby.plant_mesh.COLORS={**lobby.COLORS,'earth':'966240'}
    lobby.surface=lobby.plant_mesh.palette()
    lobby.surface[0].name='M_RusticStalls_Palette'
    fonts=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'
    font=bpy.data.fonts.load(str(fonts/'arialbd.ttf')) if (fonts/'arialbd.ttf').is_file() else bpy.data.fonts[0]
    make_stalls(font)
    for i,height,accent in [(1,8.5,'blue'),(2,9.38,'gold'),(3,8.5,'red')]:
        scoreboard(i,height,accent)
    wheel()
    out=ASSET/'export'
    out.mkdir(exist_ok=True)
    for obj in lobby.collection.objects:
        export(obj,out)
        x,y,angle=LAYOUT[obj.name]
        obj.location=(x*STUD,y*STUD,0)
        obj.rotation_euler.z=radians(angle)
    bpy.ops.object.select_all(action='DESELECT')
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.color_type='TEXTURE'
            area.spaces.active.overlay.show_overlays=False
            view=area.spaces.active.region_3d
            view.view_rotation=Vector((.05,-1,.38)).to_track_quat('Z','Y')
            view.view_location=(0,0,1.15)
            view.view_distance=19
            view.view_perspective='ORTHO'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'RusticStalls.blend'),compress=True)


if __name__=='__main__':
    main()
