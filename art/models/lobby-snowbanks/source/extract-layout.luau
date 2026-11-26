local fs=require('@lune/fs');local r=require('@lune/roblox');local s=require('@lune/serde')
local root=r.deserializeModel(fs.readFile('models/lobby/Workspace/LobbyArea.rbxm'))[1]
local out={floor=root.WinterPlaza.PlazaSurface.CFrame.Position.Y+root.WinterPlaza.PlazaSurface.Size.Y/2,queues={},interactions={},visuals={},trees={}}
for _,station in root.QueueStations:GetChildren()do local p=station.Zone;table.insert(out.queues,{x=p.CFrame.Position.X-14000,z=p.CFrame.Position.Z,hx=p.Size.X/2+2,hz=p.Size.Z/2+2})end
for _,name in {'Upgrades_Node','Classes_Node','PrizeWheel_Kiosk_Node'}do local p=root.WinterPlaza.ImportedModels[name].Interaction;table.insert(out.interactions,{x=p.CFrame.Position.X-14000,z=p.CFrame.Position.Z,r=6})end
for _,folder in {root.WinterPlaza.ImportedModels,root.SoloRecordsStand}do for _,p in folder:GetDescendants()do if p:IsA('MeshPart') and not p:GetFullName():find('Fence') and not p:GetFullName():find('Lantern')then
 local c=p.CFrame;local size=p.Size;table.insert(out.visuals,{x=c.Position.X-14000,z=c.Position.Z,hx=(math.abs(c.RightVector.X)*size.X+math.abs(c.LookVector.X)*size.Z)/2+1.5,hz=(math.abs(c.RightVector.Z)*size.X+math.abs(c.LookVector.Z)*size.Z)/2+2})
end end end
for _,p in root.WinterPlaza.SnowFirs:GetChildren()do if p:IsA('BasePart')then local c=p.CFrame.Position;table.insert(out.trees,{x=c.X-14000,z=c.Z})end end
fs.writeFile('build/lobby-snowbanks/layout.json',s.encode('json',out));print('Current owner layout extracted: '..#out.visuals..' meshes, '..#out.trees..' trees')
