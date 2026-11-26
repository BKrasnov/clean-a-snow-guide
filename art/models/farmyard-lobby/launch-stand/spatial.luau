local fs=require('@lune/fs');local r=require('@lune/roblox');local s=require('@lune/serde')
local a=r.deserializeModel(fs.readFile('build/launch-stand-tools/LobbyArea-before.rbxm'))[1];local b=r.deserializeModel(fs.readFile('models/lobby/Workspace/LobbyArea.rbxm'))[1]
local function bounds(m)
 local lo=r.Vector3.new(math.huge,math.huge,math.huge);local hi=-lo
 for _,p in m:GetDescendants() do if p:IsA('BasePart') then for _,x in {-1,1}do for _,y in {-1,1}do for _,z in {-1,1}do local q=p.CFrame:PointToWorldSpace(p.Size*r.Vector3.new(x,y,z)/2);lo=r.Vector3.new(math.min(lo.X,q.X),math.min(lo.Y,q.Y),math.min(lo.Z,q.Z));hi=r.Vector3.new(math.max(hi.X,q.X),math.max(hi.Y,q.Y),math.max(hi.Z,q.Z))end end end end end
 return {centerX=(lo.X+hi.X)/2,centerZ=(lo.Z+hi.Z)/2,width=hi.X-lo.X,bottomY=lo.Y,height=hi.Y-lo.Y}
end
local result={};for i=1,6 do local n=string.format('MapFrame%02d',i);local old,new=bounds(a.WinterPlaza.Farmyard[n]),bounds(b.WinterPlaza.Farmyard[n]);for _,k in {'centerX','centerZ','width','bottomY'}do assert(math.abs(old[k]-new[k])<(if k=='width' then .05 else .01),n..' changed '..k) end;table.insert(result,{name=n,before=old,after=new})end
fs.writeFile('art/frames/2026-11-26-launch-stand-picture/spatial.json',s.encode('json',result));fs.writeFile('build/launch-stand-tools/LobbyArea.xml',r.serializeModel({b},true));print('Spatial PASS: centers and bottom within .01; collision width within .05 (visual mesh width15.5)')
