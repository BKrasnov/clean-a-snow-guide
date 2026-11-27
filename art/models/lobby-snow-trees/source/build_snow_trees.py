"""Build the four approved tree turnarounds at Roblox metre scale."""
from math import cos, sin, tau
from pathlib import Path
from random import Random
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ASSET.parent / 'garden-plants/source'))
from plant_mesh import Plant, palette

STUD = .28


def stem(mesh, stations, color='wood', scars=()):
    """Polygonal tapered wood. Birch marks occupy faces in the skin itself."""
    sides = 9
    rings = []
    for x, y, z, radius in stations:
        rings.append([(x + radius*cos(tau*k/sides+.20),
                       y + .91*radius*sin(tau*k/sides+.20), z) for k in range(sides)])
    for j in sorted({row for row,_ in scars}):
        thickness = stations[j+1][2]-stations[j][2]
        for k in range(sides):
            x,y,z = rings[j+1][k]
            angle = tau*k/sides + 1.8*j
            shift = .25*thickness*sin(angle)
            low = rings[j][k]
            rings[j][k] = (*low[:2],low[2]+shift)
            rings[j+1][k] = (x,y,z+shift-thickness*(.46+.40*cos(angle)))
    faces = [tuple(reversed(range(sides)))]
    colors = [color]
    for j in range(len(rings)-1):
        for k in range(sides):
            a = j*sides+k
            b = j*sides+(k+1)%sides
            faces.append((a,b,b+sides,a+sides))
            colors.append('bark' if (j,k) in scars else color)
    faces.append(tuple(range((len(rings)-1)*sides,len(rings)*sides)))
    mesh.face_colors([p for ring in rings for p in ring],faces,colors+[color])


def crown(mesh, x, y, z, rx, ry, height, seed, flat=False, lean=0):
    """Single closed foliage volume. The jagged snow boundary is a shared ring."""
    rng = Random(seed)
    n = 10 if flat else 9
    phase = rng.uniform(0,.65)
    outline = [rng.uniform(.94,1.06) for _ in range(n)]
    angles = [phase+tau*k/n for k in range(n)]
    # radius, height, vertical irregularity
    profiles = ([(.62,.025,.04),(1,.24,.055),(.91,.59,.11),(.57,.88,.05)]
                if flat else [(.50,.025,.045),(1,.115,.07),(.78,.48,.12),(.34,.81,.055)])
    verts = [(x,y,z)]
    jagged = [rng.uniform(-1,1) for _ in range(n)]
    for layer,(radius,h,irregular) in enumerate(profiles):
        for k,a in enumerate(angles):
            dz = irregular*(.6*cos(3*a+.8)+.4*rng.uniform(-1,1))
            drift = .14*jagged[k] if layer==2 else 0
            # Extend the snow down the existing slope in a few angular tongues.
            spread = radius - drift*.35
            verts.append((x+rx*(spread*outline[k]*cos(a)+lean*h),
                          y+ry*(spread*outline[k]*sin(a)+.055*h), z+height*(h+dz+drift)))
    top = len(verts)
    verts.append((x+rx*lean,y+ry*.055,z+height))
    faces, colors = [], []
    for k in range(n):
        a,b = 1+k,1+(k+1)%n
        faces.append((0,b,a))
        colors.append('deep')
        for color in ('deep','green','snow'):
            faces.append((a,b,b+n,a+n))
            colors.append(color)
            a,b = a+n,b+n
        faces.append((a,b,top))
        colors.append('snow')
    mesh.face_colors(verts,faces,colors)


def fir(m):
    stem(m,[(0,0,0,.057),(0,0,.15,.042),(.003,0,.62,.027),(.015,.004,.88,.015)])
    for i,(x,z,r,h) in enumerate([(-.008,.14,.27,.224),(.006,.36,.194,.216),
                                    (.014,.575,.139,.188),(.018,.762,.089,.238)]):
        crown(m,x,0,z,r,r*.82,h,16+i,lean=.22 if i==3 else .015)


def limb(m, stations, color='wood'):
    m.tube([p[:3] for p in stations],[p[3] for p in stations],color,sides=7)


def pine(m):
    stem(m,[(0,0,0,.091),(-.008,0,.24,.073),(-.12,-.005,.425,.06),
            (-.195,.012,.52,.052),(-.225,.024,.69,.039),(-.33,.025,.84,.019)])
    limb(m,[(-.17,0,.484,.042),(-.31,-.015,.49,.027),(-.395,-.03,.542,.014)])
    limb(m,[(-.203,.009,.54,.047),(-.03,.01,.565,.042),(.12,-.003,.62,.028),(.185,-.015,.68,.018)])
    limb(m,[(-.24,.02,.69,.033),(-.16,.068,.78,.023),(-.102,.095,.84,.012)])
    for i,(x,y,z,rx,ry,h) in enumerate([(-.39,-.032,.50,.17,.134,.105),
            (.183,-.015,.615,.285,.175,.147),(-.33,.015,.805,.266,.212,.195),
            (-.088,.101,.779,.197,.163,.153)]):
        crown(m,x,y,z,rx,ry,h,30+i,flat=True,lean=-.06)


def birch(m):
    # The two bark stripes on the tall trunk and one on the smaller trunk
    # wrap partway round, so the rear view also has markings.
    marks = {(j,k) for j in (3,5) for k in (0,1,3,4,5,6,7)}
    stem(m,[(0,0,0,.105),(-.017,0,.10,.061),(-.035,.005,.215,.054),
        (-.04,.008,.367,.05),(-.041,.008,.389,.05),(-.052,.013,.523,.044),
        (-.052,.013,.543,.044),(-.077,.014,.714,.039),(-.053,.035,.848,.028),
        (-.032,.05,.945,.017),(-.025,.052,1,.004)],'cream',marks)
    stem(m,[(.008,-.002,.042,.064),(.04,.003,.124,.056),(.091,.02,.229,.042),
        (.123,.034,.296,.037),(.13,.038,.315,.037),(.174,.052,.404,.029),
        (.235,.073,.488,.018),(.262,.093,.54,.005)],'cream',
        {(3,k) for k in (0,1,4,5,6,7)})
    for path in [
       [(-.072,.017,.70,.043),(-.164,-.016,.782,.032),(-.211,-.044,.854,.019),(-.237,-.059,.906,.004)],
       [(-.151,-.012,.777,.024),(-.14,-.106,.816,.017),(-.15,-.135,.862,.004)],
       [(-.061,.01,.625,.037),(.075,-.026,.718,.029),(.159,-.039,.809,.015),(.18,-.057,.852,.004)],
       [(.076,-.026,.725,.023),(.153,.038,.754,.014),(.199,.059,.791,.004)],
       [(-.056,.033,.831,.028),(.042,.064,.871,.025),(.091,.103,.95,.006)],
       [(.18,.051,.419,.022),(.135,-.012,.489,.018),(.125,-.031,.553,.006)]]:
        limb(m,path,'cream')
    for pt,sz in [((-.085,.007,.759),(.05,.048,.048)),((.169,.044,.444),(.032,.027,.033)),
                  ((.062,.003,.204),(.041,.034,.042))]:
        m.blob(pt,sz,'snow',sides=7,rings=3,phase=.35)


def cedar(m):
    stem(m,[(0,0,0,.176),(.008,.003,.158,.131),(-.015,.01,.33,.107),
            (-.012,.035,.58,.070),(-.024,.035,.8,.024)])
    limb(m,[(-.024,0,.188,.102),(-.17,-.025,.279,.081),(-.29,-.065,.396,.059),
            (-.335,-.08,.63,.024)])
    limb(m,[(.043,.009,.213,.097),(.182,.053,.277,.078),(.313,.094,.391,.055),
            (.349,.11,.527,.025)])
    for i,(x,y,z,r,h) in enumerate([(-.015,.06,.326,.345,.44),(-.026,.065,.628,.26,.372),
          (-.33,-.077,.262,.262,.343),(-.339,-.08,.492,.195,.283),
          (.34,.10,.246,.239,.27),(.355,.115,.413,.174,.24)]):
        crown(m,x,y,z,r,r*.86,h,51+i,lean=.085)


TREES = [('AlpineFir',18,-25,fir),('WindPine',16,-9,pine),
         ('WinterBirch',15,7,birch),('SnowCedar',13,20,cedar)]


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    group = bpy.data.collections.new('Lobby Snow Trees')
    sc.collection.children.link(group)
    surface = palette()
    surface[0].name = 'M_LobbySnowTrees'
    surface[0].node_tree.nodes.active.image.name = 'LobbySnowTrees_Palette'
    out = ASSET/'export'
    out.mkdir(exist_ok=True)
    for name,height,offset,draw in TREES:
        part = Plant(name,group,surface)
        draw(part)
        scale = height*STUD/max(v[2] for v in part.vertices)
        part.vertices = [Vector(v)*scale for v in part.vertices]
        obj = part.object()
        obj['height_studs'] = height
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),use_selection=True,export_animations=False)
        obj.location.x = offset*STUD
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            view = area.spaces.active
            view.shading.color_type='TEXTURE'
            view.overlay.show_overlays=False
            view.region_3d.view_rotation=Vector((0,-1,.09)).to_track_quat('Z','Y')
            view.region_3d.view_perspective='ORTHO'
            view.region_3d.view_location=(-.6,0,2.3)
            view.region_3d.view_distance=21
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'LobbySnowTrees.blend'),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(out/'LobbySnowTrees.glb'),export_animations=False)

if __name__=='__main__':
    build()
