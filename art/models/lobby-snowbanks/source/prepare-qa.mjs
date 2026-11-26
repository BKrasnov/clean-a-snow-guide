import fs from 'node:fs';
import {graphicsSet,graphicsBack} from '../../../../tools/studio-scenarios/_graphics.mjs';
const quality=process.argv[2]??'Level21';
if(!['Level21','Level01'].includes(quality))throw Error('Expected Level21 or Level01');
const low=quality==='Level01';
const expected=JSON.parse(fs.readFileSync(new URL('../export/placement.json',import.meta.url)));
const client=`local player=game.Players.LocalPlayer;if not player.Character then player.CharacterAdded:Wait()end
local remote=game.ReplicatedStorage:WaitForChild('_SnowbanksQAEvent');task.wait(14)
local ok,err=pcall(function()
local root=workspace.CleanSnowWorld.Lobby;local banks=root.WinterPlaza:WaitForChild('Snowbanks')
local parts=0;for _,p in banks:GetDescendants()do if p:IsA('BasePart')then parts+=1;assert(p.Anchored and not p.CanCollide and not p.CanTouch and not p.CanQuery)end end
assert(parts==${expected.parts.length} and #banks:GetChildren()==${expected.groups.length},'Counts '..parts..'/'..#banks:GetChildren());local queues=0;for _,s in root.QueueStations:GetChildren()do assert(s.Zone:FindFirstChildWhichIsA('ProximityPrompt',true).Enabled,s.Name..' prompt disabled');queues+=1 end;assert(queues==6)
assert(root.SoloRecordsStand.Face);local found=false;for _,g in player.PlayerGui:GetChildren()do if g:IsA('SurfaceGui')and g.Name=='SoloRecordsBoard'and g.Adornee==root.SoloRecordsStand.Face then found=true end end;assert(found,'Records UI lost')
local module=player.PlayerScripts:FindFirstChild('PlayerModule');if module then local controls=require(module):GetControls();controls:Disable()end
${low?'':`local h=player.Character:WaitForChild('Humanoid');local hrp=player.Character:WaitForChild('HumanoidRootPart')
local function walk(x,z)h:MoveTo(Vector3.new(x,hrp.Position.Y,z));local deadline=os.clock()+10;repeat task.wait(.1)until (Vector3.new(hrp.Position.X,0,hrp.Position.Z)-Vector3.new(x,0,z)).Magnitude<3 or os.clock()>deadline;assert((Vector3.new(hrp.Position.X,0,hrp.Position.Z)-Vector3.new(x,0,z)).Magnitude<3,'Walk blocked at '..x..','..z..' actual '..tostring(hrp.Position))end
walk(14036,85);walk(14036,55);walk(14000,55);walk(14000,0);remote:FireServer('walk','four segments passed')`}
for _,g in player.PlayerGui:GetChildren()do if g:IsA('ScreenGui')then g.Enabled=false end end
local camera=workspace.CurrentCamera;local at,look;game:GetService('RunService'):BindToRenderStep('SnowbanksQA',10000,function()if at then camera.CameraType=Enum.CameraType.Scriptable;camera.CFrame=CFrame.lookAt(at,look);camera.FieldOfView=65 end end)
local function shot(name,a,b)at=Vector3.new(unpack(a));look=Vector3.new(unpack(b));task.wait(3);local done=false;game:GetService('CaptureService'):CaptureScreenshot(function(id)remote:FireServer('capture','${quality}-'..name,id);done=true end);local d=os.clock()+10;repeat task.wait(.1)until done or os.clock()>d;assert(done)end
shot('plaza',{14000,138,58},{14000,124,-35});shot('eye',{14000,125.8,25},{13976,122.5,5});shot('right',{14057,126,48},{14095,123,15})
${low?'':`shot('left',{13964,126,37},{13917,123,14});shot('tree',{14106,124.3,-10},{14117.3,121.25,-.6});shot('overhead',{14000,215,10},{14000,120,10})`}
remote:FireServer('pass','parts='..parts..' queues='..queues)
end);if not ok then remote:FireServer('fail',tostring(err))end`;
const server=`local r=Instance.new('RemoteEvent');r.Name='_SnowbanksQAEvent';r.Parent=game.ReplicatedStorage;r.OnServerEvent:Connect(function(p,kind,name,id)if kind=='capture'then print('SNOWBANKS_CAPTURE '..name..' '..id)elseif kind=='walk'then print('SNOWBANKS_WALK '..name)elseif kind=='pass'or kind=='fail'then print('SNOWBANKS_RESULT ${quality} '..kind..' '..tostring(name));task.delay(2,function()game:GetService('StudioTestService'):EndTest('snowbanks-${quality}-'..kind)end)end end);task.delay(130,function()if r.Parent then game:GetService('StudioTestService'):EndTest('snowbanks-timeout')end end)`;
fs.mkdirSync('build/lobby-snowbanks',{recursive:true});
fs.writeFileSync('build/lobby-snowbanks/arm.luau',`assert(game.Name=='NaLovi.rbxl'and game:GetService('RunService'):IsEdit())
for _,row in {{game.StarterPlayer.StarterPlayerScripts,'_SnowbanksQAClient'},{game.ServerScriptService,'_SnowbanksQAServer'}}do local old=row[1]:FindFirstChild(row[2]);if old then old:Destroy()end end
local c=Instance.new('LocalScript');c.Name='_SnowbanksQAClient';c.Source=[====[${client}]====];c.Parent=game.StarterPlayer.StarterPlayerScripts
local s=Instance.new('Script');s.Name='_SnowbanksQAServer';s.Source=[====[${server}]====];s.Parent=game.ServerScriptService;return 'Snowbanks QA armed'`);
fs.writeFileSync('build/lobby-snowbanks/start.luau',`assert(game.Name=='NaLovi.rbxl'and game:GetService('RunService'):IsEdit())
${graphicsSet(quality)}
assert(settings().Rendering.QualityLevel==Enum.QualityLevel.${quality})
task.spawn(function()local ok,res=pcall(function()return game:GetService('StudioTestService'):ExecutePlayModeAsync({})end);${graphicsBack()};print('SNOWBANKS_END ${quality} '..tostring(ok)..' '..tostring(res))end);return 'Snowbanks Play started ${quality}'`);
if(!low)fs.writeFileSync('tools/studio-scenarios/lobby-snowbanks.json',JSON.stringify({description:'Snowbanks: actual four-segment walk, generated non-contact groups/parts count, six enabled queues, records binding, live screenshots. Companion generator supports Level01 with Edit quality guard.',place:'place/NaLovi.rbxl',steps:[{on:'Server',luau:server},{on:'Client',luau:client}]},null,2)+'\n');
