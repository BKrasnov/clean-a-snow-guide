import fs from 'node:fs';
import {height} from './shape.mjs';
fs.mkdirSync('build/lobby-relief',{recursive:true});
const grid=[];
for(let x=13888;x<14112;x+=4){const column=[];for(let z=-80;z<96;z+=4)column.push(height(x+2-14000,z+2));grid.push(column)}
const code=`--!strict
assert(game.Name=='NaLovi.rbxl' and game.PlaceId==0 and game:GetService('RunService'):IsEdit())
local root=workspace.LobbyArea;local plaza=root.WinterPlaza
assert(plaza.PlazaSurface.Size==Vector3.new(208,.26,166),'unexpected owner layout')
if _G.LobbyReliefBusy then return 'already authoring' end
local region=Region3.new(Vector3.new(13888,108,-80),Vector3.new(14112,132,96))
local materials,occupancy=workspace.Terrain:ReadVoxels(region,4)
for x=1,56 do for y=1,6 do for z=1,44 do assert(materials[x][y][z]==Enum.Material.Snow or materials[x][y][z]==Enum.Material.Air,'foreign material in relief region')end end end
local grid=game:GetService('HttpService'):JSONDecode([==[${JSON.stringify(grid)}]==])
_G.LobbyReliefBusy=true
local recording=game:GetService('ChangeHistoryService'):TryBeginRecording('LobbySnowRelief','Snow relief inside lobby')
for x=1,56 do for z=1,44 do local h=grid[x][z];for y=1,6 do local value=math.clamp((h-2-108-(y-1)*4)/4,0,1);materials[x][y][z]=if value>0 then Enum.Material.Snow else Enum.Material.Air;occupancy[x][y][z]=value end end end
workspace.Terrain:WriteVoxels(region,4,materials,occupancy)
for _,part in {plaza.PlazaSurface,plaza.EntrancePath}do part.Transparency=1;part.Material=Enum.Material.Snow;part.MaterialVariant='';part:SetAttribute('WhiteGrassAsset',nil)end
local marker=plaza:FindFirstChild('SnowRelief') or Instance.new('Folder');marker.Name='SnowRelief';marker:SetAttribute('AuthoringOwner','lobby-snow-relief-20261127');marker.Parent=plaza
if recording then game:GetService('ChangeHistoryService'):FinishRecording(recording,Enum.FinishRecordingOperation.Commit)end
_G.LobbyReliefBusy=false
return 'SNOWRELIEF_INSTALLED: 56x6x44 voxels, no models moved'
`;
fs.writeFileSync('build/lobby-relief/install.luau',code);
console.log('Prepared 2464 height columns');
