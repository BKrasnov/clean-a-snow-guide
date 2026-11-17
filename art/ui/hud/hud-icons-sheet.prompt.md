# hud-icons-sheet.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-17. Прозрачный фон запрошен.

## Prompt

Game UI icon sheet for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the attached icon sheet of snow tools (same thick dark brown outline, same soft top-left light, same flat colours, same toy-like chunky shapes).
Nine icons on a fully transparent background, laid out in a 3 by 3 grid, evenly spaced with wide empty gaps between them so no two icons touch, each icon the same size and centred in its cell. No text, no letters, no numbers, no square tiles, buttons or frames behind the icons, no shadows on the ground.
Every icon is drawn the same way: one chunky toy-like cartoon object seen from the front, soft light from the top-left, flat colours, a thick dark brown outline #2B1A11. Simple bold shapes that read at 40 pixels on a phone.
Row 1:
1 Coin: one thick round gold coin #FFCE43 seen almost from the front, a thick darker gold rim #C28E49, a small embossed sun emblem #C28E49 in the middle, a short cream shine #FFFDF5 at the top-left.
2 Gem: one chunky cut crystal gem shaped like a rhombus (a diamond standing on its point), bright crystal blue #8BE0FF, a pale facet #A8DEE7, a white sparkle facet #F3F6F5 at the top-left and a darker facet #80A0E6 at the bottom-right.
3 Clock: a round clock with a cream face #FFFDF5 and a thick gold ring #FFCE43, a small gold button on top, a short red hour hand #D6392B and a long dark minute hand #2B1A11, four small dark ticks at the top, bottom and sides. No numbers.
Row 2:
4 Settings: one chunky gear with eight thick rounded teeth, light steel #A0B0C4 with a pale highlight #F3F6F5, a round blue hub #80A0E6 in the middle with a dark hole #2B1A11.
5 News: one cream sheet of paper #FFFDF5 with its top-right corner folded down, one thick red headline bar #D6392B at the top and three blue-grey text bars #A0B0C4 under it. Bars only, no letters.
6 Stats: a bar chart of three chunky rounded bars standing side by side on a short dark base line #2B1A11, rising from left to right: short gold #FFCE43, taller gold #FFCE43, tallest green #5BB830.
Row 3:
7 Upgrades: a small wooden crate #CD925C with dark plank lines #80401B, and a big bright green arrow #5BB830 with a lighter edge #96DC6A pointing straight up out of the top of the crate.
8 Pets: one chunky animal paw print: a big rounded pad and three round toe beans above it, soft pink #CE9ED2 with cream highlights #FFFDF5.
9 Lock: one chunky gold padlock #FFCE43 with darker gold shading #C28E49, a rounded shackle on top and a dark keyhole #2B1A11. Only the padlock, nothing behind it.
Readable at small phone size, no extra objects, no watermark. Colours only from: #FFCE43 #C28E49 #FFFDF5 #8BE0FF #A8DEE7 #F3F6F5 #80A0E6 #D6392B #2B1A11 #A0B0C4 #5BB830 #96DC6A #CD925C #80401B #CE9ED2.

## Референсы

- `art/ui/hotbar/hotbar-icons-sheet.png` — style reference.
- `art/frames/02-snow-run.jpeg` — style reference.

## Нарезка и проверка

- Попыток: 1. Лист разрезан на девять значков `hud-<значок>-256.png`: coin (`Hud:Coin`), gem (`Hud:Gem`), clock, settings, news, stats, upgrades (ящик со стрелкой, кнопка UPGR), pets (лапа), lock (замок окна классов). Нарезка — сетка 3×3, в клетке все куски по альфе не меньше 2 % самого большого, квадрат с полем 12 px, альфа ниже 40 обнулена, цвет прозрачных пикселей — контур #2B1A11, 256×256; альфа 250–254 поднята до 255.
- Проверено: в середине значка альфа 255, в углу 0; все девять читаются в 56 px на доске #C28E49 и тёмном дереве #80401B.
- В Roblox не загружены: загрузка — только со слова владельца, id вписывается в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau` (`art/import.md`, карточка `701948`).
- Решение владельца 17.11.2026: лист утверждён (карточка `701948`).
