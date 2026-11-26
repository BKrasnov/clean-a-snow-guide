local fs=require('@lune/fs');local r=require('@lune/roblox');local s=require('@lune/serde')
local a=r.deserializeModel(fs.readFile('build/launch-stand-tools/LobbyArea-before.rbxm'))[1];local b=r.deserializeModel(fs.readFile('models/lobby/Workspace/LobbyArea.rbxm'))[1]
local function xml(n)return (r.serializeModel({n},true):gsub('%s*<Content name="ExplorerIconContent">%s*<null>%s*</null>%s*</Content>',''))end
local protected={};local function compareChildren(x,y,except)
 for _,c in x:GetChildren() do if not except(c.Name) then local d=assert(y:FindFirstChild(c.Name));assert(xml(c)==xml(d),'Unexpected change '..c:GetFullName());table.insert(protected,c:GetFullName())end end
 for _,c in y:GetChildren() do if not except(c.Name) then assert(x:FindFirstChild(c.Name),'Unexpected child '..c:GetFullName())end end
end
compareChildren(a,b,function(n)return n=='WinterPlaza'end)
compareChildren(a.WinterPlaza,b.WinterPlaza,function(n)return n=='Farmyard'end)
compareChildren(a.WinterPlaza.Farmyard,b.WinterPlaza.Farmyard,function(n)return n:match('^MapFrame0[1-6]$')~=nil end)
local frames={};for i=1,6 do local name=string.format('MapFrame%02d',i);local new=b.WinterPlaza.Farmyard[name];assert(new:GetAttribute('ImportedLaunchStand'));local picture=new.PictureSurface.Landscape.Artwork;assert(xml(picture):find('rbxassetid://123239346194001',1,true));assert(new.PictureSurface.Landscape.Face==r.Enum.NormalId.Front)
local mesh=new:FindFirstChildWhichIsA('MeshPart',true);assert(xml(mesh):find('rbxassetid://92810403654391',1,true));assert(not mesh.CanCollide and not mesh.CanTouch and mesh.Anchored)
table.insert(frames,{name=name,image='rbxassetid://123239346194001',mesh='rbxassetid://92810403654391'})end
fs.writeFile('art/frames/2026-11-26-launch-stand-picture/preservation.json',s.encode('json',{result='pass',baseline='acc6496f2',protectedSubtrees=protected,frames=frames}))
print('Exact XML preservation of '..#protected..' subtrees, including all queue stations, prompts, spawn, other Farmyard objects: PASS')
