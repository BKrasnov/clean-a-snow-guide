assert(game.Name=='NaLovi.rbxl'and game:GetService('RunService'):IsEdit())
local root=workspace.LobbyArea;local fixed={}
for name,distance in {Upgrades_Node=16,Classes_Node=10,PrizeWheel_Kiosk_Node=6.659616947174072}do
 local p=root.WinterPlaza.ImportedModels[name].Interaction:FindFirstChildWhichIsA('ProximityPrompt');assert(p);p.MaxActivationDistance=distance;table.insert(fixed,name..'='..distance)
end
return table.concat(fixed,', ')
