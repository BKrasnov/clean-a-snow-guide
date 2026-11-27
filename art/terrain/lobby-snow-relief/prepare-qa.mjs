import fs from 'node:fs';
import {graphicsSet,graphicsBack} from '../../../tools/studio-scenarios/_graphics.mjs';
const photoOnly=process.argv.includes('--photos');
const client=`${graphicsSet('Level21')}
local player=game.Players.LocalPlayer
local remote=game.ReplicatedStorage:WaitForChild('_LobbyReliefQA');task.wait(15)
local ok,err=pcall(function()
local lobby=workspace.CleanSnowWorld.Lobby;local hrp=player.Character:WaitForChild('HumanoidRootPart');local humanoid=player.Character:WaitForChild('Humanoid')
local lighting=game:GetService('Lighting')
assert(lighting.ClockTime>15 and lighting.Ambient.R<remote:GetAttribute('BaselineAmbient').R,'lobby shadow settings were not applied')
remote:FireServer('light',('lobby clock=%.2f ambient=%s outdoor=%s'):format(lighting.ClockTime,tostring(lighting.Ambient),tostring(lighting.OutdoorAmbient)))
local module=player.PlayerScripts:FindFirstChild('PlayerModule');if module then require(module):GetControls():Disable()end
local function walk(x,z)local goal=Vector3.new(14000+x,hrp.Position.Y,z);humanoid:MoveTo(goal);local untilTime=os.clock()+12;repeat task.wait(.15)until (Vector3.new(hrp.Position.X,0,hrp.Position.Z)-Vector3.new(goal.X,0,goal.Z)).Magnitude<3 or os.clock()>untilTime;assert((Vector3.new(hrp.Position.X,0,hrp.Position.Z)-Vector3.new(goal.X,0,goal.Z)).Magnitude<3,'blocked walk '..x..','..z..' actual '..tostring(hrp.Position))end
${photoOnly?'':"walk(0,55);walk(0,10);walk(-64,-3);walk(0,10);walk(63,21);remote:FireServer('walk','5 segments passed')"}
local rp=RaycastParams.new();rp.FilterType=Enum.RaycastFilterType.Include;rp.FilterDescendantsInstances={workspace.Terrain}
for _,point in {{0,58,120.4,120.72},{-88,54,124,126.5},{88,54,124,126.5},{-28,58,123.2,126},{28,58,123.2,126}}do
 local hit=workspace:Raycast(Vector3.new(14000+point[1],150,point[2]),Vector3.new(0,-50,0),rp)
 assert(hit and hit.Material==Enum.Material.Snow and hit.Position.Y>=point[3] and hit.Position.Y<=point[4],'snow relief height out of range at '..point[1]..','..point[2])
 remote:FireServer('height',point[1]..','..point[2]..'='..hit.Position.Y)
end
local n=0;for _,station in lobby.QueueStations:GetChildren()do assert(station.Zone:FindFirstChildWhichIsA('ProximityPrompt',true).Enabled);n+=1 end;assert(n==6)
local camera=workspace.CurrentCamera;local at,look;player:SetAttribute('CleanSnowCutscene',true)
game:GetService('RunService'):BindToRenderStep('LobbyReliefQA',10000,function()if at then camera.CameraType=Enum.CameraType.Scriptable;camera.CFrame=CFrame.lookAt(at,look);camera.FieldOfView=65 end end)
local function shot(name,a,b,hud)
 for _,gui in player.PlayerGui:GetChildren()do if gui:IsA('ScreenGui')then gui.Enabled=hud end end
 at=Vector3.new(unpack(a));look=Vector3.new(unpack(b));task.wait(2)
 local done=false;game:GetService('CaptureService'):CaptureScreenshot(function(id)remote:FireServer('capture',name,id,os.clock());done=true end);local finish=os.clock()+10;repeat task.wait(.1)until done or os.clock()>finish;assert(done)
end
shot('overview',{13912,181,145},{14000,121,3},false)
shot('ground',{14012,125.8,52},{13955,121,34},false)
shot('snowbank',{14077,126.8,54},{14097,122,10},false)
shot('stands',{13965,129,43},{13921,124,4},false)
shot('trail',{14000,134,78},{14000,121,22},false)
${photoOnly?'':`
walk(0,10);walk(0,-20);walk(42.5,-30)
local request=game.ReplicatedStorage.CleanSnow.Remotes.ActionRequest
request:FireServer({requestId='lobby-snow-contrast',kind='QueueStart',payload={stationId='Station06',targetSize=1,mode='new',slot=1}})
local deadline=os.clock()+32
repeat task.wait(.15) until (player:GetAttribute('CleanSnowSessionId') and math.abs(hrp.Position.X-14000)>300
 and lighting.Ambient==remote:GetAttribute('BaselineAmbient')) or os.clock()>deadline
assert(player:GetAttribute('CleanSnowSessionId') and math.abs(hrp.Position.X-14000)>300,'solo run did not start')
assert(lighting.Ambient==remote:GetAttribute('BaselineAmbient') and lighting.ClockTime==remote:GetAttribute('BaselineClock')
 and lighting.OutdoorAmbient==remote:GetAttribute('BaselineOutdoor'),'valley lighting was not restored')
remote:FireServer('light','restored valley lighting in solo run')
`}
${graphicsBack()}
remote:FireServer('pass','${photoOnly?'photos':'walk=8, solo run=1'}, queues=6, snow raycasts=5')
end);if not ok then remote:FireServer('fail',tostring(err))end`;
const server=`local r=Instance.new('RemoteEvent');r.Name='_LobbyReliefQA'
local lighting=game:GetService('Lighting')
r:SetAttribute('BaselineAmbient',lighting.Ambient);r:SetAttribute('BaselineOutdoor',lighting.OutdoorAmbient);r:SetAttribute('BaselineClock',lighting.ClockTime)
r.Parent=game.ReplicatedStorage
r.OnServerEvent:Connect(function(p,kind,name,id,clock)
 print('LOBBYRELIEF '..kind..' '..tostring(name)..' '..tostring(id)..' '..tostring(clock))
 if kind=='pass'or kind=='fail'then task.delay(2,function()game:GetService('StudioTestService'):EndTest('lobbyrelief-'..kind)end)end
end)
task.delay(130,function()if r.Parent then game:GetService('StudioTestService'):EndTest('lobbyrelief-timeout')end end)`;
const arm=`assert(game.Name=='NaLovi.rbxl' and game:GetService('RunService'):IsEdit())
for _,row in {{game.StarterPlayer.StarterPlayerScripts,'_LobbyReliefQAClient',${JSON.stringify(client)}},{game.ServerScriptService,'_LobbyReliefQAServer',${JSON.stringify(server)}}}do local old=row[1]:FindFirstChild(row[2]);if old then old:Destroy()end;local s=Instance.new(if row[1]==game.ServerScriptService then 'Script' else 'LocalScript');s.Name=row[2];s.Source=row[3];s.Parent=row[1]end
return 'QA armed'`;
fs.writeFileSync('build/lobby-relief/arm.luau',arm);
fs.writeFileSync('build/lobby-relief/start.luau',`assert(game:GetService('RunService'):IsEdit());${graphicsSet('Level21')};task.spawn(function()local ok,result=pcall(function()return game:GetService('StudioTestService'):ExecutePlayModeAsync({})end);${graphicsBack()};print('LOBBYRELIEF END '..tostring(ok)..' '..tostring(result))end);return 'Play started'`);
if(!photoOnly)fs.writeFileSync('tools/studio-scenarios/lobby-snow-relief.json',JSON.stringify({description:'Lobby snowdrifts and shadows, clear walking routes and six queue prompts, with valley lighting restored on solo start. Edit arm/start companion used when shared CLI is unavailable.',place:'place/NaLovi.rbxl',steps:[{on:'Server',luau:server},{on:'Client',luau:client}]},null,2)+'\n');
