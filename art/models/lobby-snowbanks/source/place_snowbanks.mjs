// Deterministic dressing from the owner's current layout, with actual route clearances.
import fs from 'node:fs';
const asset = new URL('../', import.meta.url);
const templates = JSON.parse(fs.readFileSync(new URL('export/templates.json', asset))).templates;
const layout = JSON.parse(fs.readFileSync('build/lobby-snowbanks/layout.json'));
const groups = [], parts = [];
let partBudget = 148; // Reserve four eight-lobe tree bases.
const radians = (angle) => angle*Math.PI/180;
const rotate = (x,z,angle) => [Math.cos(angle)*x+Math.sin(angle)*z,-Math.sin(angle)*x+Math.cos(angle)*z];
function product(a,b) {
  const result=[];
  for(let i=0;i<3;i++) for(let j=0;j<3;j++) result.push([0,1,2].reduce((v,k)=>v+a[i*3+k]*b[k*3+j],0));
  return result;
}
function overlaps(a,b) { return Math.abs(a.x-b.x)<a.hx+b.hx && Math.abs(a.z-b.z)<a.hz+b.hz; }
function blocked(row) {
  const {x,z,hx,hz}=row;
  if(overlaps(row,{x:0,z:30,hx:10,hz:63})) return true;
  if(layout.queues.some(q=>overlaps(row,q))) return true;
  if(layout.visuals.some(q=>overlaps(row,q))) return true;
  return layout.interactions.some(q=>Math.hypot(Math.max(Math.abs(x-q.x)-hx,0),Math.max(Math.abs(z-q.z)-hz,0))<q.r);
}
function add(name,x,z,scale,yaw,category) {
  const theta=radians(yaw), c=Math.cos(theta), s=Math.sin(theta), spin=[c,0,s,0,1,0,-s,0,c];
  const candidate=templates[name].map((p,index)=>{
    const [dx,dz]=rotate(p.at[0]*scale,p.at[2]*scale,theta);
    const rotation=product(spin,p.rotation??[1,0,0,0,1,0,0,0,1]);
    const size=p.size.map(v=>v*scale);
    const relativeY=p.at[1]*scale-.035;
    const footprint=Math.sqrt(Math.max(0,1-(relativeY/(size[1]/2))**2));
    const hx=(Math.abs(rotation[0])*size[0]+Math.abs(rotation[2])*size[2])*footprint/2;
    const hz=(Math.abs(rotation[6])*size[0]+Math.abs(rotation[8])*size[2])*footprint/2;
    return {name:'Lobe'+(index+1),at:[x+dx,p.at[1]*scale-.035,z+dz],size,rotation,rgb:p.rgb,x:x+dx,z:z+dz,hx,hz};
  });
  if(parts.length+candidate.length>partBudget || candidate.some(blocked)) return false;
  const bounds={x:(Math.min(...candidate.map(p=>p.x-p.hx))+Math.max(...candidate.map(p=>p.x+p.hx)))/2,
    z:(Math.min(...candidate.map(p=>p.z-p.hz))+Math.max(...candidate.map(p=>p.z+p.hz)))/2};
  bounds.hx=Math.max(...candidate.map(p=>p.x+p.hx))-bounds.x;
  bounds.hz=Math.max(...candidate.map(p=>p.z+p.hz))-bounds.z;
  if(groups.some(g=>overlaps(bounds,g.bounds)))return false;
  const id='Bank'+String(groups.length+1).padStart(2,'0');
  groups.push({id,template:name,category,scale,yaw,at:[x,z],bounds});
  for(const p of candidate){delete p.x;delete p.z;delete p.hx;delete p.hz;parts.push({...p,group:id});}
  return true;
}
for(const side of [-1,1]) {
  for(const [i,z] of [-61,-39,-12,15,43,69,89].entries()) add(['Shoulder','Windbank','Pillow'][i%3],side*(96+(i%2)*2),z+(side<0?i%3*2:-i%3*2),.96+(i%3)*.045,side*(81+i%2*13),'fence');
  for(const [i,z] of [-13,12,49].entries()) add(i%2?'Pillow':'Windbank',side*(19+i%2*4),z+(side<0?-4:3),.68+i%2*.04,side*(79+i*9),'path-edge');
  for(const [i,z] of (side<0?[-23,6,40,61]:[-13,24,48,72]).entries()) add(['Crescent','Shoulder','Pillow'][i%3],side*(43+i%2*10),z,.85+i%2*.09,side*(12+i*38),'plaza-side');
  for(const [i,x] of [37,65,87].entries())add(i%2?'Clumps':'Crescent',side*x,85,.75,side*(20+i*29),'entrance-edge');
}
for(const [i,x]of[-80,-55,-26,3,32,64,85].entries())add(i%2?'Windbank':'Pillow',x,-67,.9,i%2?9:-12,'back-fence');
for(const side of [-1,1])for(const [i,z]of[-85,-53,-17,21,57,94].entries())add(i%2?'Pillow':'Shoulder',side*(122+i%2*5),z,.9+i%2*.15,side*(26+i*41),'forest-edge');
const trees=layout.trees.filter(t=>Math.abs(t.x)<145 && t.z>-110 && t.z<112)
  .sort((a,b)=>Math.abs(Math.abs(a.x)-110)+Math.abs(a.z)*.2-(Math.abs(Math.abs(b.x)-110)+Math.abs(b.z)*.2));
partBudget = 180;
for(const [i,t]of trees.entries()){if(groups.filter(g=>g.category==='tree').length>=4)break;add('TreeSkirt',t.x,t.z,.9+(i%3)*.12,i*47,'tree');}
for(const [i,g]of [...groups].entries())if(i%4===0)add('Clumps',g.bounds.x+(i%2?-1:1)*(g.bounds.hx+3.2),g.bounds.z+2.7,.7,i*27,'small-cluster');
if(groups.length<36)throw Error('Too few safe groups: '+groups.length+' ('+parts.length+' parts)');
const out={ownerLayoutBaseline:'ad9e4de42',origin:[14000,layout.floor,0],parts,groups};
fs.writeFileSync(new URL('export/placement.json',asset),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({groups:groups.length,parts:parts.length,categories:groups.reduce((a,g)=>(a[g.category]=(a[g.category]??0)+1,a),{})}));
