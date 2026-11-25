"""Closed, flat-shaded plant parts with one project-palette atlas per asset."""
from math import cos, pi, sin
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'starter-farmhouse/source'))
from build_farmhouse import Mesh

COLORS = {
    'green':'54A577', 'leaf':'77C98D', 'deep':'3C8E63', 'lime':'96DC6A',
    'wood':'CD925C', 'bark':'80401B', 'earth':'966240', 'tan':'C28E49',
    'straw':'FAD66E', 'red':'D6392B', 'orange':'F8AA3C', 'gold':'FFCE43',
    'cream':'FFFDF5', 'snow':'F3F6F5', 'ice':'A8DEE7', 'blue':'80A0E6',
    'violet':'A096DE', 'pink':'CE9ED2', 'shadow':'B3C2D4', 'crystal':'8BE0FF',
    'dark':'2B1A11', 'berry':'FF948B'
}

def palette():
    values = list(COLORS.values())
    image = bpy.data.images.new('GardenPlants_Palette',64,32,alpha=False)
    pixels = []
    for y in range(32):
        for x in range(64):
            shade = values[min(len(values)-1, (y//8)*8+x//8)]
            pixels.extend([int(shade[j:j+2],16)/255 for j in (0,2,4)] + [1])
    image.pixels.foreach_set(pixels)
    image.pack()
    mat = bpy.data.materials.new('M_GardenPlants_Palette')
    mat.use_nodes = True
    graph = mat.node_tree
    shader = graph.nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = .83
    shader.inputs['Specular IOR Level'].default_value = .22
    texture = graph.nodes.new('ShaderNodeTexImage')
    texture.image = image
    texture.interpolation = 'Closest'
    graph.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
    graph.nodes.active = texture
    return mat, {name:((i%8+.5)/8,(i//8+.5)/4) for i,name in enumerate(COLORS)}

class Plant(Mesh):
    def face_colors(self,verts,faces,colors):
        assert len(faces)==len(colors)
        self.add(verts,faces,colors[0])
        self.colors[-len(faces):] = colors

    def loft(self,rings,colors):
        n = len(rings[0])
        assert len(colors)==len(rings)-1 and all(len(r)==n for r in rings)
        faces = [tuple(reversed(range(n)))]
        shades = [colors[0]]
        for j,col in enumerate(colors):
            for k in range(n):
                a,b=j*n+k,j*n+(k+1)%n
                faces.append((a,b,b+n,a+n))
                shades.append(col)
        faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
        self.face_colors([p for ring in rings for p in ring],faces,shades+[colors[-1]])

    def tube(self,points,radii,color,sides=6):
        pts = [Vector(p) for p in points]
        radius = [radii]*len(pts) if isinstance(radii,(int,float)) else radii
        rings = []
        previous = None
        for i,(p,r) in enumerate(zip(pts,radius,strict=True)):
            tangent = (pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
            if previous is None or abs(previous.dot(tangent))>.99:
                previous = min((Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))),key=lambda v:abs(v.dot(tangent)))
            u = (previous-tangent*tangent.dot(previous)).normalized()
            v = tangent.cross(u)
            previous = u
            rings.append([p+r*(u*cos(2*pi*k/sides)+v*sin(2*pi*k/sides)) for k in range(sides)])
        self.loft(rings,[color]*(len(pts)-1))

    def blob(self,center,radii,color,sides=8,rings=4,phase=0):
        x,y,z=center
        rx,ry,rz=radii
        verts=[(x,y,z-rz)]
        for j in range(1,rings):
            lat=pi*j/rings
            for k in range(sides):
                a=2*pi*k/sides+phase
                verts.append((x+rx*sin(lat)*cos(a),y+ry*sin(lat)*sin(a),z-rz*cos(lat)))
        top=len(verts)
        verts.append((x,y,z+rz))
        faces=[]
        for k in range(sides):
            a,b=1+k,1+(k+1)%sides
            faces.append((0,b,a))
            for j in range(rings-2):
                faces.append((a,b,b+sides,a+sides))
                a,b=a+sides,b+sides
            faces.append((a,b,top))
        self.add(verts,faces,color)

    def leaf(self,base,tip,width,color,arch=.12):
        a,b=Vector(base),Vector(tip)
        d=b-a
        side=Vector((-d.y,d.x,0))
        side=side.normalized() if side.length>.001 else Vector((1,0,0))
        up=d.cross(side).normalized()
        mid=a+d*.46+Vector((0,0,arch))
        # A folded blade with real thickness and pointed ends.
        verts=[a,mid-side*width,mid+up*(width*.34),mid+side*width,mid-up*(width*.16),b]
        faces=[]
        for k in range(4):
            p,q=1+k,1+(k+1)%4
            faces.extend([(0,p,q),(5,q,p)])
        self.add(verts,faces,color)
