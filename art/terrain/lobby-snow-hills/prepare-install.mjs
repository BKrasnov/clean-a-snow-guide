import fs from 'node:fs';import {profile as p,height}from './shape.mjs';
const samples=[[-180,0],[180,0],[0,-180],[140,220],[0,0],[110,99]];const code=`--!strict
assert(game.Name=='NaLovi.rbxl' and not game:GetService('RunService'):IsRunning())
if _G.SnowHillsAuthoringBusy then return 'Already authoring snow hills' end
_G.SnowHillsAuthoringBusy=true
local p=game:GetService('HttpService'):JSONDecode([==[${JSON.stringify(p)}]==])
local function smooth(t) t=math.clamp(t,0,1);return t*t*(3-2*t)end
local function height(x,z)
 local q,e=p.protected,p.edge;local dx=math.max(math.abs(x)-q.halfX,0);local dz=math.max(math.abs(z-q.centerZ)-q.halfZ,0)
 local mask=smooth(math.sqrt(dx*dx+dz*dz)/q.blend)
 mask=math.min(mask,math.max(smooth((math.abs(x)-q.entranceHalfWidth)/q.blend),smooth(math.max(q.entranceZ-z,z-q.entranceEnd,0)/q.blend)))
 local sum=0;for _,g in p.hills do local v=g[3]*math.exp(-.5*((x-g[1])^2/g[4]^2+(z-g[2])^2/g[5]^2));sum+=v*v end
 local edge=smooth(math.min(e.halfX-math.abs(x),e.halfZ-math.abs(z))/e.blend)
 return p.region.min[2]+(p.floor-p.region.min[2]+math.sqrt(sum)*mask)*edge
end
${samples.map(([x,z])=>`assert(math.abs(height(${x},${z})-${height(x,z)})<.00001,'profile mismatch')`).join('\n')}
local root=workspace.LobbyArea;local plaza=root.WinterPlaza;local terrain=workspace.Terrain
local old=plaza:FindFirstChild('SnowLandscape');assert(not old or old:GetAttribute('AuthoringOwner')=='lobby-snow-terrain-20261126','foreign landscape')
if not old then
 local m,o=terrain:ReadVoxels(Region3.new(Vector3.new(unpack(p.region.min)),Vector3.new(unpack(p.region.max))),4)
 for x=1,#o do for y=1,#o[x]do for z=1,#o[x][y]do assert(o[x][y][z]==0,'Existing ground in authoring region; do not overwrite')end end end
end
for sx=p.region.min[1],p.region.max[1]-1,64 do
 local ex=math.min(sx+64,p.region.max[1]);local nx=(ex-sx)/4;local ny=(p.region.max[2]-p.region.min[2])/4;local nz=(p.region.max[3]-p.region.min[3])/4
 local materials,occupancy={},{}
 for x=1,nx do materials[x]={};occupancy[x]={};for y=1,ny do materials[x][y]={};occupancy[x][y]={}end;for z=1,nz do local h=height(sx+(x-.5)*4-p.originX,p.region.min[3]+(z-.5)*4);for y=1,ny do local o=math.clamp((h-2-p.region.min[2]-(y-1)*4)/4,0,1);materials[x][y][z]=if o>0 then Enum.Material.Snow else Enum.Material.Air;occupancy[x][y][z]=o end end end
 terrain:WriteVoxels(Region3.new(Vector3.new(sx,p.region.min[2],p.region.min[3]),Vector3.new(ex,p.region.max[2],p.region.max[3])),4,materials,occupancy)
 task.wait()
end
local banks=plaza:FindFirstChild('Snowbanks');if banks then assert(banks:GetAttribute('AuthoringOwner')=='lobby-snowbanks-20261126');banks:Destroy()end
local marker=old or Instance.new('Folder');marker.Name='SnowLandscape';marker:SetAttribute('AuthoringOwner','lobby-snow-terrain-20261126');marker:SetAttribute('Profile',${JSON.stringify(JSON.stringify(p))});marker.Parent=plaza
local moved=0;for _,tree in plaza.SnowFirs:GetChildren()do if tree:IsA('BasePart')then local c=tree.CFrame;local original=tree:GetAttribute('SnowTerrainOriginalY') or c.Position.Y;local h=height(c.Position.X-p.originX,c.Position.Z);local dy=math.max(0,h-(original-tree.Size.Y/2));if dy>.01 then tree:SetAttribute('SnowTerrainOriginalY',original);tree.CFrame=c+(Vector3.new(0,original+dy-c.Position.Y,0));moved+=1 end end end
local service=game:GetService('MaterialService');local mat=service:FindFirstChild('LobbyWhiteGrass');assert(not mat or mat:GetAttribute('AuthoringOwner')=='lobby-snow-terrain-20261126','foreign material');if not mat then mat=Instance.new('MaterialVariant');mat.Name='LobbyWhiteGrass';mat.Parent=service end
mat.BaseMaterial=Enum.Material.Grass;mat.ColorMap=p.texture;mat.StudsPerTile=8;mat:SetAttribute('AuthoringOwner','lobby-snow-terrain-20261126')
for _,part in {plaza.PlazaSurface,root.SnowGround}do part.Material=Enum.Material.Grass;part.MaterialVariant=mat.Name;part:SetAttribute('WhiteGrassAsset',p.texture)end
_G.SnowHillsAuthoringBusy=false
print('SNOWHILLS_INSTALLED movedTrees='..moved..' texture='..mat.ColorMap)
`;
fs.writeFileSync('build/lobby-snow-terrain/install.luau',code);console.log('Authoring script prepared')
