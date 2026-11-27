export const smooth=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};
const segments=[[[0,10],[-67.49,-2.81]],[[0,30],[-72,30]],[[0,22],[65.32,20.99]],[[0,-12],[62,-15]]];
const foundations=[[-76.31,-11.63,17],[-84.81,25,17],[77.26,15.42,17],[70.99,-22.58,16]];
function segmentDistance(x,z,a,b){const dx=b[0]-a[0],dz=b[1]-a[1];const t=Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz)));return Math.hypot(x-a[0]-dx*t,z-a[1]-dz*t)}
export function protection(x,z){
 let mask=smooth((Math.abs(x)-12)/9);
 // The queue row, arch supports and the records approach remain at their original floor.
 mask=Math.min(mask,Math.max(smooth((Math.abs(x)-57)/9),smooth((Math.abs(z+38)-19)/9)));
 mask=Math.min(mask,Math.max(smooth((Math.abs(x)-50)/13),smooth((69-z)/15)));
 for(const [a,b]of segments)mask=Math.min(mask,smooth((segmentDistance(x,z,a,b)-9)/9));
 for(const [a,b,r]of foundations)mask=Math.min(mask,smooth((Math.hypot(x-a,z-b)-r)/13));
 return mask;
}
export function height(x,z){
 const falloff=(position,center,width)=>Math.exp(-.5*((position-center)/width)**2);
 // Keep the crests inside the yard. The tails meet the fence below its rail.
 const westBank=5.6*falloff(x,-87+2.4*Math.sin(z*.07),9)*(0.9+0.1*Math.cos((z-53)*.105));
 const eastBank=5.3*falloff(x,89+2.1*Math.sin(z*.081),9)*(0.92+0.08*Math.cos((z-53)*.13));
 const frontBank=4.3*falloff(z,77,7.5)*smooth((Math.abs(x)-48)/24);
 // Different widths and offsets leave a winding packed strip between the drifts.
 const westDrift=4.3*falloff(x,-31+3.2*Math.sin(z*.12),11)*falloff(z,56,18);
 const eastDrift=4.8*falloff(x,31+3*Math.sin(z*.11+.7),11.5)*falloff(z,52,19);
 const westShoulder=3.1*falloff(x,-51,14)*falloff(z,55,11);
 const eastShoulder=3.35*falloff(x,52,12)*falloff(z,60,13);
 const ripple=.19*(1+Math.sin(x*.28+Math.cos(z*.19))*Math.cos(z*.24));
 const outsideBlend=smooth((112-Math.abs(x))/9)*smooth((z+80)/10)*smooth((96-z)/10);
 const driftHeight=outsideBlend*protection(x,z)*(
  Math.max(westBank,eastBank,frontBank,westDrift,eastDrift,westShoulder,eastShoulder)+ripple
 );
 // A low apron at the rails leaves the wood visible along the whole fence.
 const railClearance=Math.min(103-Math.abs(x),89-z,z+73);
 const railHeight=1+4.9*smooth(railClearance/13);
 return 120.57+Math.min(driftHeight,railHeight);
}
