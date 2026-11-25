# window-sheet.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-23. Прозрачный фон запрошен.

## Prompt

Game UI parts sheet for a Roblox cartoon winter farm game: the parts of the snowy wooden window of the attached approved window reference (the first reference, the UPGRADES window: a big wooden board with a soft cushion of snow on its top edge, a dark header plank, inset lighter wooden cards and dark icon tiles) in exactly its look and in the look of the attached snowy wood pieces of the game's HUD (the second reference): chunky rounded wooden boards, a thick dark brown outline, soft light from the top, a soft cartoon cushion of snow lying on the top edge.

Four separate parts on a fully transparent background, with a wide empty gap between them so they never touch. Every part is seen straight from the front, flat, no perspective, no tilt, no drop shadow, no background. The left half of the sheet holds part 1; the right half holds parts 2, 3 and 4 one under another.

1 (left half) Snowy window board: one big empty wooden board, a rounded rectangle exactly 1.25 times as wide as it is tall, the corner radius about one tenth of its height. Base plank colour #C28E49. A darker bevel #80401B runs along the inner edge all around, about one fortieth of the board's height thick, and a thick dark brown outline #2B1A11 of exactly the same thickness all around. The whole inside of the board, inside the bevel, is one flat even colour #C28E49: no wood grain lines, no plank seams, no knots, no texture, no gradient, nothing in the middle at all. The snow is part of the same picture: a thick soft cartoon cushion of snow #F3F6F5 with a lavender shade #CDCDED on its underside lies on the whole top edge. Across the middle two thirds of the width the snow is a perfectly even straight band, exactly one fifteenth of the board's height thick, with no drips and no bumps. The snow rounds over both top corners and runs a little down each side, and near each top corner two or three rounded drips hang down to about one eighth of the board's height. The snow has the same dark outline #2B1A11, a little thinner than the board's.

2 (right half, top) Header plank: one empty dark wooden plank, a rounded rectangle exactly five times as wide as it is tall, the corner radius about a third of its height. Colour #80401B with a slightly lighter top edge #966240, the same thick outline #2B1A11. The middle is one flat colour, no grain, no seams. No snow.

3 (right half, middle) Inset card: one empty lighter wooden card, a rounded rectangle exactly four times as wide as it is tall, the corner radius about one sixth of its height. Colour #CD925C, the same thick outline #2B1A11, and a soft darker inner edge #C28E49 along its inner top and left sides so it looks pressed into the board. The middle is one flat colour #CD925C, no grain, no seams. No snow.

4 (right half, bottom, left of centre) Icon tile: one empty square dark wooden tile with rounded corners, exactly as wide as it is tall, the corner radius about one fifth of its side. Colour #80401B with a soft darker inner edge along its inner top side, the same thick outline #2B1A11. The middle is one flat colour. No snow.

Nothing else on any part: no text, no letters, no numbers, no icons, no nails, no knots, no background, no extra frames or shadows. Colours only from: #C28E49 #CD925C #80401B #966240 #2B1A11 #F3F6F5 #CDCDED.

## Референсы

- `art/refs/windows-wood/upgrades-window.png` — style reference.
- `art/ui/wood/wood-sheet-v2.png` — style reference.
- `art/frames/01-lobby.jpeg` — style reference.

## Нарезка и проверка

- Карточка `6137fd`, попытка 1 из 3. Лист — исходник; в игре стоят куски (ImageMagick: рамка по альфе с полем 6 px, Lanczos, альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11):
  - `window-board-snow.png` 889×568 (вырезка `889x568+37+176`), ключ `Wood:Window`. 9-slice `HudWood.SLICE.Window`: центр `Rect.new(112, 158, 777, 495)`. Снег в середине — строки 12–66 (с контуром), подтёки до x 108 слева и от x 781 справа, вниз до строки 153; фаска внутри контура — 13 px; нижнее скругление — от строки 498. Середина доски — ровный цвет, растягивается без следов.
  - `window-header.png` 512×88 (вырезка `787x135+957+120`), ключ `Wood:Header`, центр `Rect.new(30, 24, 482, 70)`.
  - `window-card.png` 512×141 (вырезка `738x203+982+321`), ключ `Wood:Card`, центр `Rect.new(32, 32, 480, 110)`; тёмный внутренний край сверху и слева — до 20 px.
  - `window-tile.png` 126×128 (вырезка `209x213+989+582`), ключ `Wood:Tile`, центр `Rect.new(24, 22, 102, 104)`.
- `SliceScale` доски — от глубины снега (поле `snow`), у частей без снега — от угла (`corner`), края не больше самой доски (`HudWood.sliceScale`).
- В Roblox не загружены: загрузка — только со слова владельца (`art/import.md`). Без id `WindowWood` рисует доски кодом без снега. В Studio локальные копии кладёт `npm run ui:local`.
