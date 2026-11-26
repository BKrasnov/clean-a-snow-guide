--!strict
-- Authoring only: preserve runtime anchors, replace the selected imported visuals.
assert(game.Name=='NaLovi.rbxl' and game.PlaceId==0 and game:GetService('RunService'):IsEdit())
local lobby=assert(workspace:FindFirstChild('LobbyArea'))
local yard=lobby.WinterPlaza.Farmyard
assert(not yard:GetAttribute('ImportedStandsInstalled'),'Replacement already applied')
local names={'StartGameArch_Node','Rewards_Node','Upgrades_Node','Classes_Node','PrizeWheel_Node','LeaderboardLeft_Node','LeaderboardRight_Node'}
local incoming={}
for _,name in names do
 local source=assert(workspace:FindFirstChild(name),'Missing '..name)
 assert(source:IsA('Model'))
 for _,item in source:GetDescendants() do assert(not item:IsA('LuaSourceContainer') and not item:IsA('ProximityPrompt'),'Unexpected imported behavior') end
 incoming[name]=source:Clone()
end
_G.LobbySwapOriginal=lobby:Clone()
local floor=120.75
local function fit(model: Model,x: number,z: number,width: number?)
 local _,size=model:GetBoundingBox()
 if width then model:ScaleTo(model:GetScale()*width/size.X) end
 model:PivotTo(CFrame.Angles(0,math.pi,0))
 local box,ext=model:GetBoundingBox()
 model:PivotTo(model:GetPivot()+Vector3.new(x-box.Position.X,floor-(box.Position.Y-ext.Y/2),z-box.Position.Z))
 for _,part in model:GetDescendants() do if part:IsA('BasePart') then part.Anchored=true;part.CanCollide=false;part.CanTouch=false;part.CanQuery=false end end
 model:SetAttribute('ImportedReplacement',true)
 return ext
end
local function collider(parent: Instance,name: string,size: Vector3,at: Vector3)
 local part=Instance.new('Part');part.Name=name;part.Size=size;part.CFrame=CFrame.new(at)
 part.Anchored=true;part.Transparency=1;part.CanCollide=true;part.CanTouch=false;part.CanQuery=true;part.CastShadow=false;part.Parent=parent
 return part
end
local arch=incoming.StartGameArch_Node
local archSize=fit(arch,14000,-49,122.25)
arch.Name='LaunchArch';yard.LaunchArch:Destroy();arch.Parent=yard
for _,sign in {-1,1} do collider(arch,'PillarCollider',Vector3.new(4.1,27,3.7),Vector3.new(14000+sign*56.85,floor+13.5,-49)) end
local imported=lobby.WinterPlaza.ImportedModels
local placements={
 {'Rewards_Node','Rewards_Node',13945,-4,14},
 {'Upgrades_Node','Upgrades_Node',13929,-34,14},
 {'Classes_Node','Classes_Node',14050,-4,14},
 {'PrizeWheel_Node','PrizeWheel_Kiosk_Node',14078,-38,17},
 {'LeaderboardLeft_Node','Leaderboard01_Node',13930,-51,11},
 {'LeaderboardRight_Node','Leaderboard03_Node',14070,-58,11},
}
for _,row in placements do
 local visual=incoming[row[1]]
 local size=fit(visual,row[3],row[4],row[5])
 local target=assert(imported:FindFirstChild(row[2]),'Missing existing wrapper '..row[2])
 for _,old in target:GetChildren() do if old.Name~='Interaction' then old:Destroy() end end
 visual.Name='UserVisual';visual:SetAttribute('ImportedSourceName',row[1]);visual.Parent=target
 if row[1]=='PrizeWheel_Node' then
  collider(visual,'BaseCollider',Vector3.new(size.X*.64,.8,size.Z*.8),Vector3.new(row[3],floor+.4,row[4]))
  collider(visual,'PostCollider',Vector3.new(.8,9,.8),Vector3.new(row[3],floor+4.5,row[4]-1.4))
 elseif row[1]:match('Leaderboard') then
  collider(visual,'BoardCollider',Vector3.new(size.X*.88,size.Y-.6,.6),Vector3.new(row[3],floor+size.Y/2,row[4]))
 else
  collider(visual,'CounterCollider',Vector3.new(size.X*.82,3.4,size.Z*.62),Vector3.new(row[3],floor+1.7,row[4]))
 end
 local interaction=target:FindFirstChild('Interaction')
 if interaction and interaction:IsA('BasePart') then interaction.CFrame=CFrame.new(row[3],floor+3.6,row[4]+size.Z/2+1.5) end
end
for _,name in {'Garage','House','GarageExhibits','Rewards','Upgrades','Classes'} do local old=yard:FindFirstChild(name);if old then old:Destroy() end end
for _,name in names do workspace[name]:Destroy() end
yard:SetAttribute('ImportedStandsInstalled',true)
game:GetService('Selection'):Set({yard})
workspace.CurrentCamera.CFrame=CFrame.lookAt(Vector3.new(14000,148,111),Vector3.new(14000,132,-24))
return 'Seven imported visuals installed; garage/house removed; original queue zones/prompts preserved'
