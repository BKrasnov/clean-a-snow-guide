"""Build the wheeled snow vacuum. Shape dimensions below are in Roblox studs."""
from math import cos, sin, pi
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parents[1] / "snow-storage/source"))
import build_storage as storage

farm = storage.farm
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
farm.MODEL = "SnowVacuum"
farm.COLORS = dict(red="#D6392B", cream="#FFFDF5", rubber="#2B1A11", boot="#80401B",
                   hose="#C28E49", gold="#FFCE43", alloy="#A0B0C4", green="#54A577",
                   blue="#40A5FF")
surface = farm.palette()
group = farm.collection("SnowVacuum", scene.collection)


def part(name):
    return farm.Mesh("SnowVacuum_" + name, group, surface)


def finish(m):
    m.vertices = [tuple(v * .28 for v in p) for p in m.vertices]
    return m.object()


def outline(w, h, bevel):
    return [(-w+bevel,-h),(w-bevel,-h),(w,-h+bevel),(w,h-bevel),
            (w-bevel,h),(-w+bevel,h),(-w,h-bevel),(-w,-h+bevel)]


def round_axis(m, axis, center, profile, colors, n):
    rings = []
    for distance, radius in profile:
        ring = []
        for k in range(n):
            angle = 2*pi*(k+.5)/n
            a,b = radius*cos(angle),radius*sin(angle)
            offset = (distance,a,b) if axis=='X' else (a,distance,b)
            ring.append(tuple(x+y for x,y in zip(center,offset)))
        rings.append(ring)
    storage.loft(m, rings, colors)


def sweep(m, points, radii, colors, n=12):
    pts = list(map(Vector, points))
    rings = []
    for i,p in enumerate(pts):
        tangent = (pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
        u = tangent.cross(Vector((1,0,0))).normalized()
        v = tangent.cross(u)
        rings.append([tuple(p+radii[i]*(cos(2*pi*k/n)*u+sin(2*pi*k/n)*v)) for k in range(n)])
    storage.loft(m, rings, colors)


# Contiguous profile from brown bumper through red vessel and ivory lid.
body = part("Canister")
profile = [(.84,.73,.38),(.94,.83,.46),(.94,.83,.69),(.88,.77,.75),
           (.87,.76,1.94),(.84,.74,2.00),(.91,.80,2.045),(.91,.80,2.27),(.79,.68,2.43)]
storage.loft(body, [[(x,y,z) for x,y in outline(w,h,.24)] for w,h,z in profile],
             ['boot','boot','boot','red','red','cream','cream','cream'])
# A bent rectangular handle, with daylight under the crossbar.
handle = [(-.52,2.41),(-.45,2.70),(-.37,2.78),(.37,2.78),(.45,2.70),(.52,2.41),
          (.32,2.41),(.28,2.59),(-.28,2.59),(-.32,2.41)]
body.prism(handle,-.38,-.14,'Y','cream')
round_axis(body,'Y',(0,0,1.56),[(-.75,.153),(-.794,.184),(-.83,.18),(-.857,.141),(-.898,.118)],
           ['boot','boot','green','green'],14)
finish(body)

# Spindle, tire sidewall and inset yellow hub are a single revolved profile.
for sign,name in [(-1,'WheelL'),(1,'WheelR')]:
    wheel = part(name)
    profile = [(.84,.20),(.98,.20),(.985,.595),(1.04,.70),(1.25,.70),(1.325,.61),
               (1.325,.233),(1.35,.224),(1.373,.19)]
    round_axis(wheel,'X',(0,.045,.70*cos(pi/20)),[(sign*x,r) for x,r in profile],
               ['rubber']*6+['gold','gold'],20)
    finish(wheel)

# One continuous surface from socket to wand, insulated grip and hose arch.
tube = part("HoseAndWand")
path = [(0,-2.76,.47,.19),(0,-2.70,.62,.235),(0,-2.62,.79,.18),
        (0,-2.60,.84,.137),(0,-1.91,2.31,.137),(0,-1.89,2.35,.195),
        (0,-1.76,2.63,.195),(0,-1.74,2.68,.158)]
path += [(0,y,z,.158) for y,z in [(-1.62,2.98),(-1.46,3.25),(-1.26,3.48),
        (-1.02,3.66),(-.74,3.77),(-.45,3.82),(-.20,3.80),(.015,3.72),
        (.20,3.59),(.34,3.39),(.42,3.17),(.44,2.93),(.44,2.68)]]
path += [(0,.44,2.66,.205),(0,.44,2.42,.205)]
sweep(tube,[p[:3] for p in path],[p[3] for p in path],
      ['cream','cream','boot','alloy','boot','boot','boot'] + ['hose']*(len(path)-10) + ['boot','boot'])
finish(tube)

# Walk around the shell, over the lip and into the intake; cap inside the throat.
head = part("Intake")
profiles = [(-2.48,.67,.15,.225),(-2.59,.89,.236,.257),(-3.09,1.00,.26,.267),
            (-3.30,1.0,.258,.26),(-3.36,.955,.218,.258),(-3.36,.773,.132,.257),
            (-3.24,.752,.132,.257),(-2.72,.61,.092,.244)]
storage.loft(head,[[(x,y,z+t) for x,t in outline(w,h,min(.112,h*.6))] for y,w,h,z in profiles],
             ['cream','cream','gold','gold','gold','boot','rubber'])
finish(head)

vent = part("Exhaust")
storage.loft(vent,[[(x,y,1.49+z) for x,z in outline(w,h,.05)]
                   for y,w,h in [(.742,.49,.30),(.81,.51,.31),(.843,.485,.285)]],['blue','blue'])
for z in [1.34,1.49,1.64]:
    vent.prism([(-.37,z-.028),(.34,z-.028),(.37,z+.026),(-.34,z+.026)],
               .839,.855,'Y','rubber')
finish(vent)

tow = part("TowEye")
# Extruded pierced towing eye; rectangular shank terminates inside its solid flank.
tow.box((0,1.02,.52),(.17,.52,.15),'boot')
n = 10
loops = [[(x,1.44+r*cos(2*pi*k/n),.52+r*sin(2*pi*k/n)) for k in range(n)]
         for x,r in [(-.105,.235),(.105,.235),(.105,.108),(-.105,.108)]]
tow.add(sum(loops,[]),[(j*n+k,j*n+(k+1)%n,((j+1)%4)*n+(k+1)%n,((j+1)%4)*n+k)
                        for j in range(4) for k in range(n)],'boot')
finish(tow)

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp = area.spaces.active
            sp.shading.type='MATERIAL'
            sp.region_3d.view_location=(0,-.20,.46)
            sp.region_3d.view_rotation=Vector((5,-5,2.4)).to_track_quat('Z','Y')
            sp.region_3d.view_distance=2.4
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'SnowVacuum_master.blend'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(HERE.parent/'export/SnowVacuum.glb'),use_selection=True,
                          export_format='GLB')
