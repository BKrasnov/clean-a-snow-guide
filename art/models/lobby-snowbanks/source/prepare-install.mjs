import fs from 'node:fs';
const asset = new URL('../', import.meta.url);
const payload = fs.readFileSync(new URL('export/placement.json',asset),'utf8');
const source = fs.readFileSync(new URL('source/assemble.luau',asset),'utf8');
fs.mkdirSync('build/lobby-snowbanks',{recursive:true});
fs.writeFileSync('build/lobby-snowbanks/install.luau',
  `local payload=game:GetService('HttpService'):JSONDecode([====[${payload}]====])\n${source}`);
