import fs from 'node:fs';
import {graphicsSet,graphicsBack} from '../../../tools/studio-scenarios/_graphics.mjs';
const quality=process.argv[2]??'Level21';
if(!['Level21','Level01'].includes(quality))throw Error('Expected Level21 or Level01');
const low=quality==='Level01';

const client=`local player=game.Players.LocalPlayer;if not player.Character then player.CharacterAdded:Wait()end
local remote=game.ReplicatedStorage:WaitForChild('_SnowHillsQAEvent');task.wait(14)
local ok,err=pcall(function()
local root=workspace.CleanSnowWorld.Lobby;assert(not root.WinterPlaza:FindFirstChild('Snowbanks'),'old piles still exist');assert(root.WinterPlaza.SnowLandscape);assert(root.WinterPlaza.PlazaSurface:GetAttribute('WhiteGrassAsset')=='rbxassetid://131610776889867');assert(root.WinterPlaza.PlazaSurface.MaterialVariant=='LobbyWhiteGrass')
local rp=RaycastParams.new();rp.FilterType=Enum.RaycastFilterType.Include;rp.FilterDescendantsInstances={workspace.Terrain};for _,z in {0,-32,70}do local hit=workspace:Raycast(Vector3.new(14000,200,z),Vector3.new(0,-160,0),rp);assert(hit and hit.Position.Y<120.3,'terrain covers plaza at '..z..' y='..tostring(hit and hit.Position.Y))end;for _,v in {{-190,0},{190,0},{0,-190},{160,200}}do local hit=workspace:Raycast(Vector3.new(14000+v[1],220,v[2]),Vector3.new(0,-200,0),rp);assert(hit and hit.Material==Enum.Material.Snow and hit.Position.Y>125,'missing snow hill '..v[1]..','..v[2])end
local queues=0;for _,s in root.QueueStations:GetChildren()do assert(s.Zone:FindFirstChildWhichIsA('ProximityPrompt',true).Enabled,s.Name..' prompt disabled');queues+=1 end;assert(queues==6)
assert(root.SoloRecordsStand.Face);local found=false;for _,g in player.PlayerGui:GetChildren()do if g:IsA('SurfaceGui')and g.Name=='SoloRecordsBoard'and g.Adornee==root.SoloRecordsStand.Face then found=true end end;assert(found,'Records UI lost')
local module=player.PlayerScripts:FindFirstChild('PlayerModule');if module then local controls=require(module):GetControls();controls:Disable()end
${low?'':`local h=player.Character:WaitForChild('Humanoid');local hrp=player.Character:WaitForChild('HumanoidRootPart')
local function walk(x,z)h:MoveTo(Vector3.new(x,hrp.Position.Y,z));local deadline=os.clock()+10;repeat task.wait(.1)until (Vector3.new(hrp.Position.X,0,hrp.Position.Z)-Vector3.new(x,0,z)).Magnitude<3 or os.clock()>deadline;assert((Vector3.new(hrp.Position.X,0,hrp.Position.Z)-Vector3.new(x,0,z)).Magnitude<3,'Walk blocked at '..x..','..z..' actual '..tostring(hrp.Position))end
walk(14036,85);walk(14036,55);walk(14000,55);walk(14000,0);remote:FireServer('walk','four segments passed')`}
for _,g in player.PlayerGui:GetChildren()do if g:IsA('ScreenGui')then g.Enabled=false end end
local camera=workspace.CurrentCamera;local at,look;game:GetService('RunService'):BindToRenderStep('SnowHillsQA',10000,function()if at then camera.CameraType=Enum.CameraType.Scriptable;camera.CFrame=CFrame.lookAt(at,look);camera.FieldOfView=65 end end)
local function shot(name,a,b)at=Vector3.new(unpack(a));look=Vector3.new(unpack(b));task.wait(3);local done=false;game:GetService('CaptureService'):CaptureScreenshot(function(id)remote:FireServer('capture','${quality}-'..name,id);done=true end);local d=os.clock()+10;repeat task.wait(.1)until done or os.clock()>d;assert(done)end
shot('plaza',{14000,138,58},{14000,129,-65});shot('eye',{14000,125.8,25},{13976,123,5});shot('right',{14057,127,48},{14180,143,-25})
${low?'':`shot('left',{13964,127,37},{13820,144,-30});shot('front',{13935,155,105},{14015,134,260});shot('landscape',{13890,205,-140},{14080,142,-265});shot('overhead',{14280,310,280},{14000,125,-50})`}
remote:FireServer('pass','queues='..queues..' hills=4')
end);if not ok then remote:FireServer('fail',tostring(err))end`;
const server=`local r=Instance.new('RemoteEvent');r.Name='_SnowHillsQAEvent';r.Parent=game.ReplicatedStorage;r.OnServerEvent:Connect(function(p,kind,name,id)if kind=='capture'then print('SNOWHILLS_CAPTURE '..name..' '..id)elseif kind=='walk'then print('SNOWHILLS_WALK '..name)elseif kind=='pass'or kind=='fail'then print('SNOWHILLS_RESULT ${quality} '..kind..' '..tostring(name));task.delay(2,function()game:GetService('StudioTestService'):EndTest('snowhills-${quality}-'..kind)end)end end);task.delay(130,function()if r.Parent then game:GetService('StudioTestService'):EndTest('snowhills-timeout')end end)`;
fs.mkdirSync('build/lobby-snow-terrain',{recursive:true});
fs.writeFileSync('build/lobby-snow-terrain/arm.luau',`assert(game.Name=='NaLovi.rbxl'and game:GetService('RunService'):IsEdit())
for _,row in {{game.StarterPlayer.StarterPlayerScripts,'_SnowHillsQAClient'},{game.ServerScriptService,'_SnowHillsQAServer'}}do local old=row[1]:FindFirstChild(row[2]);if old then old:Destroy()end end
local c=Instance.new('LocalScript');c.Name='_SnowHillsQAClient';c.Source=[====[${client}]====];c.Parent=game.StarterPlayer.StarterPlayerScripts
local s=Instance.new('Script');s.Name='_SnowHillsQAServer';s.Source=[====[${server}]====];s.Parent=game.ServerScriptService;return 'Snowbanks QA armed'`);
fs.writeFileSync('build/lobby-snow-terrain/start.luau',`assert(game.Name=='NaLovi.rbxl'and game:GetService('RunService'):IsEdit())
${graphicsSet(quality)}
assert(settings().Rendering.QualityLevel==Enum.QualityLevel.${quality})
task.spawn(function()local ok,res=pcall(function()return game:GetService('StudioTestService'):ExecutePlayModeAsync({})end);${graphicsBack()};print('SNOWHILLS_END ${quality} '..tostring(ok)..' '..tostring(res))end);return 'Snowbanks Play started ${quality}'`);
if(!low)fs.writeFileSync('tools/studio-scenarios/lobby-snowbanks.json',JSON.stringify({description:'Snow hills: old piles removed, white-grass material, terrain raycasts on four sides, four-segment walk, six queues, records UI and live frames. Companion generator supports Level01 with Edit quality guard.',place:'place/NaLovi.rbxl',steps:[{on:'Server',luau:server},{on:'Client',luau:client}]},null,2)+'\n');
