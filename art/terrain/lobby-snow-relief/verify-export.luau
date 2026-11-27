--!strict
-- lune run art/terrain/lobby-snow-relief/verify-export.luau <saved Studio place.rbxl>
local fs=require('@lune/fs');local r=require('@lune/roblox');local process=require('@lune/process')
local T=require('../../../tools/places/terrain');local P=require('../lobby-snow-hills/preservation')
assert(process.args[1],'saved Studio file required')
local game=r.deserializePlace(fs.readFile(process.args[1]))
assert(not game.ServerScriptService:FindFirstChild('_LobbyReliefQAServer'))
assert(not game.StarterPlayer.StarterPlayerScripts:FindFirstChild('_LobbyReliefQAClient'))
local saved=game.Workspace.LobbyArea
local model=r.deserializeModel(fs.readFile('models/lobby/Workspace/LobbyArea.rbxm'))[1]
assert(P.protected(saved)==P.protected(model),'saved owner layout differs')
for _,name in {'PlazaSurface','EntrancePath'}do assert(saved.WinterPlaza[name].Transparency==1 and saved.WinterPlaza[name].Material==r.Enum.Material.Snow)end
local source={};for _,c in T.read(game.Workspace.Terrain.SmoothGrid)do source[c.x..','..c.y..','..c.z]=c end
local terrain=r.deserializeModel(fs.readFile('models/match/Workspace/Terrain.rbxm'))[1];local checked=0
for _,c in T.read(terrain.SmoothGrid)do if c.x>=108 and c.x<=110 and c.y==0 and c.z>=-1 and c.z<=0 then
 local actual=assert(source[c.x..','..c.y..','..c.z],'saved authoring chunk missing')
 assert(buffer.tostring(T.voxels(c.data))==buffer.tostring(T.voxels(actual.data)),'saved local terrain differs')
 checked+=1
end end
assert(checked==6)
print('ok: all six edited chunks match the saved Studio voxels exactly; owner layout retained, temporary QA absent')
