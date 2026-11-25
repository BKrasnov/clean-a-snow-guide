import bpy,sys,json
from pathlib import Path
here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(here.parents[1]/'starter-farmhouse/source'))
from check_surface_overlap import audit
out=here.parent/'reports'
report=audit(.002,True,'SnowStorage')
items={}
for o in bpy.data.collections['SnowStorage'].objects:
    o.data.calc_loop_triangles()
    items[o.name]={'tris':len(o.data.loop_triangles),'size_studs':[round(v/.28,2) for v in o.dimensions]}
report['items']=items
print(report)
(out/'geometry.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
assert not report['overlapping_face_pairs'] and all(300<=v['tris']<=600 for v in items.values())
