import {test} from 'node:test';
import assert from 'node:assert/strict';
import {height,protection} from './shape.mjs';
test('central packed route, all six starts and stand approaches stay below the old floor',()=>{
 for(let z=-40;z<=86;z+=2)assert.ok(height(0,z)<=120.72);
 for(const x of [-42.5,-25.5,-8.5,8.5,25.5,42.5])for(let dx=-7;dx<=7;dx+=2)for(let dz=-6;dz<=6;dz+=2)assert.ok(height(x+dx,-32+dz)<=120.72);
 for(const [x,z] of [[-67.49,-2.81],[65.32,20.99],[62,-15],[-72,30],[0,80]])assert.ok(protection(x,z)<.01&&height(x,z)<=120.72);
});
test('visible snowdrifts frame both sides of the packed trail and stay walkable',()=>{
 let peak=0,maxSlope=0;
 for(let x=-104;x<=104;x+=2)for(let z=-74;z<=90;z+=2){
  const h=height(x,z);assert.ok(Number.isFinite(h)&&h>=120.1&&h<=126.5);peak=Math.max(peak,h);
  maxSlope=Math.max(maxSlope,Math.abs(h-height(x+1,z)),Math.abs(h-height(x,z+1)));
 }
 assert.ok(peak>=125,'missing pronounced relief');assert.ok(maxSlope<.8,`slope ${maxSlope}`);
 for(const side of [-1,1]){
  const drift=height(side*28,58)-height(0,58);
  assert.ok(drift>=2.8,`drift on side ${side} is too shallow: ${drift}`);
  assert.ok(height(side*89,53)>=124.3,'missing fence-side snowdrift');
  for(let z=-73;z<=89;z+=2)assert.ok(height(side*103,z)<=121.6,'snow buries the side fence rail');
 }
 for(let x=-103;x<=103;x+=2)assert.ok(height(x,89)<=121.6,'snow buries the entrance fence rail');
});
