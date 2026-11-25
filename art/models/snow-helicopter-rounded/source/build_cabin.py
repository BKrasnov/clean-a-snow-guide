"""Rebuild the cabin on the saved vehicle, keeping the original master intact."""
from math import cos, sin, pi, radians
from pathlib import Path
import sys
import bpy
from mathutils import Vector

here = Path(__file__).resolve().parent
old = here.parents[1] / 'snow-helicopter/source/SnowHelicopter_master.blend'
bpy.ops.wm.open_mainfile(filepath=str(old))
sys.dont_write_bytecode = True
sys.path.insert(0, str(here.parents[1] / 'starter-farmhouse/source'))
from build_farmhouse import Mesh

previous = bpy.data.objects['Cabin']
collection = previous.users_collection[0]
paint = previous.data.materials[0]
uv = {name: ((i % 4 + .5)/4, (i//4 + .5)/4) for i,name in enumerate(
    ['ice','blue','gold','dark','metal','cream','snow','shadow','glazing'])}
bpy.data.objects.remove(previous, do_unlink=True)
bpy.data.objects.remove(bpy.data.objects['RunningLights'], do_unlink=True)
body = Mesh('Cabin', collection, (paint, uv))

# Height, half-width, nose station, tail station. Tangent-continuous interpolation
# between stations gives a forward belly, a raked windshield and a domed crown.
stations = [
    (3.04, 1.27, -2.40, 1.86), (3.21, 1.69, -3.47, 2.48),
    (3.50, 2.09, -4.36, 2.92), (3.85, 2.39, -5.06, 3.28),
    (4.18, 2.56, -5.43, 3.54), (4.54, 2.65, -5.56, 3.67),
    (4.94, 2.70, -5.53, 3.77), (5.55, 2.70, -5.33, 3.83),
    (6.16, 2.65, -4.97, 3.80), (6.75, 2.52, -4.44, 3.66),
    (7.24, 2.30, -3.78, 3.39), (7.57, 1.97, -3.10, 3.04),
    (7.80, 1.51, -2.34, 2.56), (7.91, 1.03, -1.49, 1.81)]
def dimensions(z):
    i = next((i for i in range(len(stations)-1) if z <= stations[i+1][0]), len(stations)-2)
    a,b = stations[i:i+2]
    left,right = stations[max(0,i-1)], stations[min(len(stations)-1,i+2)]
    span = b[0]-a[0]
    t = (z-a[0])/span
    def hermite(k):
        da = (b[k]-left[k])/(b[0]-left[0])*span
        db = (right[k]-a[k])/(right[0]-a[0])*span
        return (1-3*t*t+2*t**3)*a[k]+(3*t*t-2*t**3)*b[k]+t*(1-t)**2*da+t*t*(t-1)*db
    return [hermite(k) for k in (1,2,3)]

def height(angle, row):
    a = radians(abs(angle))
    side = (1-cos(a))/2
    sill = 4.54 + .84*side
    # A swept, rounded aft corner where the wraparound windshield meets the cowling.
    rear = max(0,min(1,(abs(angle)-89)/18))
    bottom = sill+.12+.19*rear**2
    top = 7.44+.10*sin(a)-.31*rear**2
    heights = [3.04,3.21,3.50,3.85,4.10+.46*side,sill-.19,sill,
               bottom, bottom+.06, *[bottom+(top-bottom)*v for v in (.16,.32,.42,.49,.57,.64,.72,.79,.88)],
               top-.06,top,top+.09,(top+.09+7.80)/2,7.80,7.91]
    return heights[row]

def position(angle,z):
    w,fore,aft=dimensions(z)
    a=radians(angle)
    return (w*sin(a), (fore+aft)/2-(aft-fore)/2*cos(a), z)

angles=sorted({0, *range(0,181,6), 1, 47, 49, 99,102,105,107,109,116,135,138})
angles=sorted(set([-a for a in angles]+angles)-{180})
rows=24
n=len(angles)
for row in range(rows):
    for a in angles:
        body.vertices.append(position(a,height(a,row)))
body.faces.append(tuple(reversed(range(n))))
body.colors.append('blue')
for row in range(rows-1):
    for i,a in enumerate(angles):
        k=(i+1)%n
        mid=abs((a+(angles[k] if k else 180))/2)
        face=(row*n+i,row*n+k,(row+1)*n+k,(row+1)*n+i)
        col='ice'
        if row<4: col='blue'
        elif row==5: col='cream'
        elif 7<=row<=18 and mid<107:
            col='glazing'
        if 116<=mid<=135 and row in (11,13,15): col='dark'
        body.faces.append(face)
        body.colors.append(col)
body.faces.append(tuple(range((rows-1)*n,rows*n)))
body.colors.append('ice')
body.vertices=[tuple(c*.28 for c in p) for p in body.vertices]
cabin=body.object()
# The frame is coloured directly on the outer surface; no window decals or layered faces.
tint=cabin.data.color_attributes.new(name='BaseTint',type='BYTE_COLOR',domain='CORNER')
for poly in cabin.data.polygons:
    poly.use_smooth = len(poly.vertices)==4
    for li in poly.loop_indices:
        color=(1,1,1,1)
        if (Vector(cabin.data.uv_layers.active.data[li].uv)-Vector(uv['glazing'])).length<.01:
            vid=cabin.data.loops[li].vertex_index
            a=abs(angles[vid%n])
            r=vid//n
            ids=list(poly.vertices)
            center_angle=sum(abs(angles[v%n]) for v in ids)/len(ids)
            rmin=min(v//n for v in ids)
            if center_angle<1 or 47<=center_angle<49 or center_angle>=105 or rmin in (7,18):
                color=(.038,.063,.115,1)
            else:
                light=max(0,min(1,(r-8)/9))
                color=(.070+.20*light,.11+.22*light,.18+.25*light,1)
        tint.data[li].color=color

# Both transparencies use the same material. Per-corner RGBA distinguishes the
# dark windscreen from the clear snow hopper without a third material slot.
hopper = bpy.data.objects['CollectorGlass']
glass = hopper.data.materials[0]
glass_nodes = glass.node_tree
shader = glass_nodes.nodes.get('Principled BSDF')
vertices = glass_nodes.nodes.new('ShaderNodeVertexColor')
vertices.layer_name = 'BaseTint'
glass_nodes.links.new(vertices.outputs['Color'], shader.inputs['Base Color'])
glass_nodes.links.new(vertices.outputs['Alpha'], shader.inputs['Alpha'])
shader.inputs['Roughness'].default_value = .19
for value in hopper.data.color_attributes['BaseTint'].data:
    value.color = (.39,.73,.80,.24)
cabin.data.materials.append(glass)
for face in cabin.data.polygons:
    indices = list(face.loop_indices)
    ids = list(face.vertices)
    if (Vector(cabin.data.uv_layers.active.data[indices[0]].uv)-Vector(uv['glazing'])).length >= .01:
        continue
    a = sum(abs(angles[i%n]) for i in ids)/len(ids)
    row = min(i//n for i in ids)
    if a < 1 or 47 <= a < 49 or a >= 105 or row in (7,18):
        continue
    face.material_index = 1
    for loop in indices:
        v = cabin.data.loops[loop].vertex_index
        light = max(0,min(1,(v//n-8)/9))
        tint.data[loop].color = (.027+.032*light,.053+.067*light,.125+.12*light,.68)

# Two solid seat shells with broad rounded shoulders and a low instrument hood.
inside = Mesh('CabinInterior',collection,(paint,uv))
def cushion(x,sections):
    rings=[]
    for z,y,w,d in sections:
        c=min(w,d)*.40
        footprint=[(-w+c,-d),(w-c,-d),(w,-d+c),(w,d-c),(w-c,d),(-w+c,d),(-w,d-c),(-w,-d+c)]
        rings.append([(x+i,y+j,z) for i,j in footprint])
    start=len(inside.vertices)
    inside.vertices.extend(p for ring in rings for p in ring)
    inside.faces.append(tuple(start+i for i in reversed(range(8))))
    inside.colors.append('glazing')
    for j in range(len(rings)-1):
        for k in range(8):
            a,b=start+j*8+k,start+j*8+(k+1)%8
            inside.faces.append((a,b,b+8,a+8))
            inside.colors.append('glazing')
    inside.faces.append(tuple(start+8*(len(rings)-1)+i for i in range(8)))
    inside.colors.append('glazing')
for x in (-1.04,1.04):
    cushion(x,[(3.65,-.55,.65,.65),(4.52,-.65,.88,.88),(4.76,-.65,.84,.84)])
    cushion(x,[(4.53,-.06,.81,.24),(5.73,.09,.84,.24),(6.22,.14,.65,.21),(6.34,.16,.52,.18)])
cushion(0,[(4.03,-3.21,1.18,.5),(4.80,-3.38,1.41,.47),(4.98,-3.30,1.32,.37)])
inside.vertices=[tuple(v*.28 for v in p) for p in inside.vertices]
seats=inside.object()
seat_tint=seats.data.color_attributes.new(name='BaseTint',type='BYTE_COLOR',domain='CORNER')
for value in seat_tint.data:
    value.color=(.047,.077,.146,1)

# Rounded lamps follow the forward surface and project only a narrow lens bezel.
lights=Mesh('RunningLights',collection,(paint,uv))
for sign in (-1,1):
    angle=sign*12
    anchor=Vector(position(angle,4.28))
    normal=Vector((sign*.24,-.95,-.18)).normalized()
    across=Vector((-normal.y,normal.x,0)).normalized()
    up=normal.cross(across).normalized()
    rim=[(-.17,-.115),(.17,-.115),(.235,-.065),(.235,.065),(.17,.115),(-.17,.115),(-.235,.065),(-.235,-.065)]
    start=len(lights.vertices)
    for depth,scale in [(-.10,1.15),(.055,1.15),(.083,1),(.102,.90)]:
        for x,z in rim:
            lights.vertices.append(tuple((anchor+normal*depth+(across*x+up*z)*scale)*.28))
    lights.faces.append(tuple(start+i for i in reversed(range(8))))
    lights.colors.append('blue')
    for j,col in enumerate(['blue','blue','cream']):
        for k in range(8):
            p=start+j*8
            lights.faces.append((p+k,p+(k+1)%8,p+8+(k+1)%8,p+8+k))
            lights.colors.append(col)
    lights.faces.append(tuple(start+24+i for i in range(8)))
    lights.colors.append('cream')
lamps=lights.object()
t=lamps.data.color_attributes.new(name='BaseTint',type='BYTE_COLOR',domain='CORNER')
for e in t.data: e.color=(1,1,1,1)

# Raise the mast enough to meet the new crowned roof at the foot of its fairing.
bpy.data.objects['MainRotor'].location.z += .23*.28
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'SnowHelicopterRounded_master.blend'))
nodes=paint.node_tree
texture=next(node for node in nodes.nodes if node.type=='TEX_IMAGE')
nodes.links.new(texture.outputs['Color'],nodes.nodes.get('Principled BSDF').inputs['Base Color'])
# glTF multiplies COLOR_0 with the base colour and alpha once at runtime.
for socket_name in ('Base Color','Alpha'):
    inp=shader.inputs[socket_name]
    for link in list(inp.links):
        glass_nodes.links.remove(link)
shader.inputs['Base Color'].default_value=(1,1,1,1)
shader.inputs['Alpha'].default_value=.999
bpy.ops.export_scene.gltf(filepath=str(here.parent/'export/SnowHelicopterRounded.glb'),
                          export_vertex_color='ACTIVE',export_all_vertex_colors=False)

