"""Find disconnected islands with daylight between them on the editable mesh."""
from collections import defaultdict
from mathutils.bvhtree import BVHTree

def separate_parts(mesh,gap_m=.0015):
    # Group faces by welded topology; joined twigs and petals can remain editable islands.
    roots=list(range(len(mesh.vertices)))
    def root(i):
        while roots[i]!=i:
            roots[i]=roots[roots[i]]
            i=roots[i]
        return i
    for edge in mesh.edges:
        a,b=edge.vertices
        roots[root(b)]=root(a)
    chunks=defaultdict(list)
    for face in mesh.polygons:
        chunks[root(face.vertices[0])].append(tuple(face.vertices))
    solids=[]
    for faces in chunks.values():
        ids=sorted({v for f in faces for v in f})
        verts=[mesh.vertices[i].co.copy() for i in ids]
        index={v:i for i,v in enumerate(ids)}
        tree=BVHTree.FromPolygons(verts,[[index[k] for k in f] for f in faces])
        lo=[min(v[k] for v in verts) for k in range(3)]
        hi=[max(v[k] for v in verts) for k in range(3)]
        solids.append((tree,verts,lo,hi))
    roots=list(range(len(solids)))
    for i,(tree,verts,lo,hi) in enumerate(solids):
        for j in range(i):
            if root(i)==root(j):continue
            other,points,lower,upper=solids[j]
            if any(hi[k]+gap_m<lower[k] or upper[k]+gap_m<lo[k] for k in range(3)):continue
            touching=bool(tree.overlap(other))
            if not touching:
                for a,b in ((verts,other),(points,tree)):
                    # The nearest surface's outward normal also detects a fully buried end cap.
                    for p in a:
                        pos,n,idx,d=b.find_nearest(p)
                        if d<=gap_m or (p-pos).dot(n)<-1e-7:
                            touching=True
                            break
                    if touching:break
            if touching:roots[root(i)]=root(j)
    groups=defaultdict(list)
    for i,(_,verts,_,_) in enumerate(solids):
        groups[root(i)].extend(verts)
    loose=[]
    for group in sorted(groups.values(),key=len,reverse=True)[1:]:
        loose.append({'vertices':len(group),'centroid_m':[round(sum(v[k] for v in group)/len(group),4) for k in range(3)]})
    return loose
