--!strict
-- Selective export of actual Studio ReadVoxels, preserving every other voxel and authored object.
local fs=require('@lune/fs');local r=require('@lune/roblox');local s=require('@lune/serde');local T=require('../../../tools/places/terrain')
local data=s.decode('json',fs.readFile('build/lobby-relief/studio-export.json'))
assert(data.owner=='lobby-snow-relief-20261127')
local root=r.deserializeModel(fs.readFile('build/lobby-relief/LobbyArea-before.rbxm'))[1]
for name,props in data.props do
 local part=assert(root.WinterPlaza:FindFirstChild(name));assert(props.transparency==1 and props.material=='Snow' and props.variant=='')
 part.Transparency=props.transparency;part.Material=r.Enum.Material.Snow;part.MaterialVariant=props.variant;part:SetAttribute('WhiteGrassAsset',nil)
end
assert(not root.WinterPlaza:FindFirstChild('SnowRelief'))
local marker=r.Instance.new('Folder');marker.Name='SnowRelief';marker:SetAttribute('AuthoringOwner',data.owner);marker.Parent=root.WinterPlaza
local files={['models/lobby/Workspace/LobbyArea.rbxm']=r.serializeModel({root})}
local report={changedChunks={},changedVoxels=0,owner=data.owner}
for _,role in {'lobby','match'}do
 local terrain=r.deserializeModel(fs.readFile('build/lobby-relief/Terrain-'..role..'-before.rbxm'))[1]
 local chunks=T.read(terrain.SmoothGrid);local buffers={};local byKey={}
 for _,c in chunks do byKey[c.x..','..c.y..','..c.z]=c end
 -- Existing terrain determines the material code; no hardcoded terrain palette index.
 local snow
 for _,c in chunks do if c.x==109 and c.y==0 and c.z==0 then local b=T.voxels(c.data);local value=buffer.readu16(b,(12+4*32+28*1024)*2);snow=bit32.band(value,255)end end
 assert(snow and snow>0,'snow material was not found')
 local changed=0
 for ix=1,56 do for iy=1,6 do for iz=1,44 do
  local x,y,z=3472+ix-1,27+iy-1,-20+iz-1
  local cx,cy,cz=math.floor(x/32),math.floor(y/32),math.floor(z/32);local key=cx..','..cy..','..cz
  local c=assert(byKey[key],'expected existing lobby chunk '..key)
  local b=buffers[key];if not b then b=T.voxels(c.data);buffers[key]=b end
  local offset=((x%32)+(z%32)*32+(y%32)*1024)*2
  -- ReadVoxels uses 1/256 steps; saved SmoothGrid truncates to its 0..255 byte.
  -- Rounding raises partial voxels by one byte and no longer matches the saved Studio world.
  local occupancy=math.floor(data.occupancy[ix][iy][iz]*255)
  local value=if data.occupancy[ix][iy][iz]==0 then 0 else snow+occupancy*256
  if buffer.readu16(b,offset)~=value then changed+=1;buffer.writeu16(b,offset,value)end
 end end end
 local changedChunks=0
 for key,b in buffers do local c=byKey[key];local before=T.voxels(c.data);if buffer.tostring(before)~=buffer.tostring(b)then c.data=T.pack(b);changedChunks+=1 end end
 terrain.SmoothGrid=T.write(chunks);terrain.PhysicsGrid=''
 files['models/'..role..'/Workspace/Terrain.rbxm']=r.serializeModel({terrain})
 report.changedChunks[role]=changedChunks;report.changedVoxels=changed
end
for file,bytes in files do fs.writeFile(file,bytes)end
fs.writeFile('build/lobby-relief/export-report.json',s.encode('json',report));print('Exported Studio relief: '..report.changedVoxels..' voxels, '..report.changedChunks.lobby..' chunks. All other chunks and object geometry retained.')
