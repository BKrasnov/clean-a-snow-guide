--!strict
local fs=require('@lune/fs');local r=require('@lune/roblox');local s=require('@lune/serde');local T=require('../../../tools/places/terrain');local P=require('./preservation')
local Vector3=r.Vector3;local outputs={}
local baseline=r.deserializeModel(fs.readFile('build/lobby-snow-terrain/LobbyArea-before.rbxm'))[1]
local process=require('@lune/process');local game=r.deserializePlace(fs.readFile(process.args[1] or 'place/NaLovi.rbxl'));assert(not game.ServerScriptService:FindFirstChild('_SnowHillsQAServer'));assert(not game.StarterPlayer.StarterPlayerScripts:FindFirstChild('_SnowHillsQAClient'))
local saved=game.Workspace.LobbyArea
for index,tree in baseline.WinterPlaza.SnowFirs:GetChildren()do if tree:IsA('BasePart')then local now=assert(saved.WinterPlaza.SnowFirs:GetChildren()[index]);local a={tree.CFrame:GetComponents()};local b={now.CFrame:GetComponents()};for i=1,12 do if i~=2 then assert(math.abs(a[i]-b[i])<.0001,'tree moved horizontally: '..tree.Name)end end;assert(now.CFrame.Position.Y>=tree.CFrame.Position.Y-.0001,'tree lowered');end end
assert(P.protected(baseline)==P.protected(saved),'Saved world changed outside approved visual fields')
local old=baseline.WinterPlaza:FindFirstChild('Snowbanks');assert(old and old:GetAttribute('AuthoringOwner')=='lobby-snowbanks-20261126');old:Destroy()
saved.WinterPlaza.SnowLandscape:Clone().Parent=baseline.WinterPlaza
for index,p in baseline.WinterPlaza.SnowFirs:GetChildren()do local now=saved.WinterPlaza.SnowFirs:GetChildren()[index];if p:IsA('BasePart')and now:GetAttribute('SnowTerrainOriginalY')then local dy=now.CFrame.Position.Y-p.CFrame.Position.Y;p.CFrame+=Vector3.new(0,dy,0);p:SetAttribute('SnowTerrainOriginalY',now:GetAttribute('SnowTerrainOriginalY'))end end
for _,pair in {{baseline.WinterPlaza.PlazaSurface,saved.WinterPlaza.PlazaSurface},{baseline.SnowGround,saved.SnowGround}}do pair[1].Material=pair[2].Material;pair[1].MaterialVariant=pair[2].MaterialVariant;pair[1]:SetAttribute('WhiteGrassAsset',pair[2]:GetAttribute('WhiteGrassAsset'))end
local normalized=r.serializeModel({baseline},true):gsub('%s*<Content name="ExplorerIconContent">%s*<null>%s*</null>%s*</Content>','')
local bytes=r.serializeModel(r.deserializeModel(normalized));assert(P.protected(r.deserializeModel(bytes)[1])==P.protected(saved),'Protected roundtrip mismatch');outputs['models/lobby/Workspace/LobbyArea.rbxm']=bytes
local terrain=game.Workspace.Terrain;local chunks=T.read(terrain.SmoothGrid);assert(T.write(chunks)==terrain.SmoothGrid,'Unknown saved grid format')
local additions={};local source={};for _,c in chunks do source[c.x..','..c.y..','..c.z]=c;if c.x>=105 and c.x<=113 and c.y>=0 and c.y<=1 and c.z>=-4 and c.z<=3 then table.insert(additions,c)end end;assert(#additions>20 and #additions<150,'Unexpected lobby grid extent')
local hashes={}
for _,role in {'lobby','match'}do
 local before=r.deserializeModel(fs.readFile('build/lobby-snow-terrain/Terrain-'..role..'-before.rbxm'))[1];local oldChunks=T.read(before.SmoothGrid);local combined={};local occupied={}
 for _,c in oldChunks do local key=c.x..','..c.y..','..c.z;occupied[key]=true;local now=source[key];if role=='match'then assert(now and buffer.tostring(T.voxels(now.data))==buffer.tostring(T.voxels(c.data)),'Original valley voxel changed: '..key)end;table.insert(combined,c)end
 for _,c in additions do local key=c.x..','..c.y..','..c.z;assert(not occupied[key],'Lobby overwrites an existing chunk');table.insert(combined,c)end
 before.SmoothGrid=T.write(combined);before.PhysicsGrid='';local data=r.serializeModel({before});outputs['models/'..role..'/Workspace/Terrain.rbxm']=data;hashes[role]=s.hash('sha256',data)
end
local mat=game.MaterialService.LobbyWhiteGrass;assert(tostring(mat.ColorMapContent):find('131610776889867') or P.xml(mat):find('131610776889867'));outputs['models/shared/MaterialService/LobbyWhiteGrass.rbxm']=r.serializeModel({mat})
for path,data in outputs do fs.writeFile(path,data)end
fs.writeFile('art/frames/2026-11-26-lobby-snow-hills/preservation.json',s.encode('json',{result='pass',protectedSha256=s.hash('sha256',P.protected(baseline)),lobbyChunks=#additions,originalValleyChunks=#T.read(r.deserializeModel(fs.readFile('build/lobby-snow-terrain/Terrain-match-before.rbxm'))[1].SmoothGrid),terrainHashes=hashes,modelSha256=s.hash('sha256',bytes)}));print('PASS: owner layout and original valley voxels preserved; '..#additions..' lobby terrain chunks exported')
