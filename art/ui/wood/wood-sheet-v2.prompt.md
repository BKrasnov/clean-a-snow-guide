# wood-sheet-v2.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-19. Прозрачный фон запрошен.

## Prompt

Game UI parts sheet for a Roblox cartoon winter farm game: the snowy wooden boards of the HUD, in exactly the look of the attached approved element sheets (the quick menu buttons and wallet board of the first reference, the bucket counter boards of the second, the key screen of the third) and of the wood of the fourth reference: chunky rounded wooden boards with rich wood grain, a thick dark brown outline, soft light from the top, and a soft cushion of snow lying on their top edge.
Two separate parts on a fully transparent background, side by side with a wide empty gap so they do not touch, each part centred in its half. Every part is seen straight from the front, flat, no perspective, no tilt, no drop shadow, no background.
1 (left) Snowy wood plaque: one empty wooden board shaped as a wide rounded rectangle, exactly four times as wide as it is tall, the corner radius about a quarter of its height. Rich saturated wood: base plank colour #C28E49, wood grain lines and a darker bevel along the inner bottom edge in #80401B, one straight horizontal plank seam #80401B running the whole width exactly through the middle of its height, a thick dark brown outline #2B1A11 of exactly the same thickness all around. The snow is part of the same board and clearly visible: a thick soft cartoon cushion of snow #F3F6F5 with a lavender shade #CDCDED on its underside lies on the whole top edge. Across the middle third of the width the snow is a perfectly even band, exactly one sixth of the board's height thick, with no drips and no bumps. The snow rounds over both top corners and runs down each side, and near each top corner two or three rounded drips hang down to about one third of the board's height. The snow has the same thin dark outline #2B1A11 as the board.
2 (right) Snowy wood button: one empty square wooden button with rounded corners, exactly as wide as it is tall, the corner radius about one fifth of its side, in the same rich wood as part 1 (base #C28E49, grain and bottom bevel #80401B, the same thick outline #2B1A11) but one single plank with no seam. The same thick soft snow cushion #F3F6F5 with lavender shade #CDCDED lies on its whole top edge: an even band about one eighth of its side thick in the middle, rounding over both top corners, with one or two small rounded drips near each top corner reaching down to about a quarter of its side. The middle is empty.
Nothing else on them: no text, no letters, no numbers, no icons, no nails, no knots, no background, no extra frames or shadows. Colours only from: #C28E49 #CD925C #80401B #2B1A11 #F3F6F5 #CDCDED.

## Референсы

- `art/refs/hud-new/elements/01-wallet-quick-menu.png` — style reference.
- `art/refs/hud-new/elements/07-bucket-counter.png` — style reference.
- `art/refs/hud-new/key/run-pc.png` — style reference.
- `art/ui/wood/wood-sheet.png` — style reference.

## Нарезка и проверка

- Круг 5 карточки `f2de28` (дизайн-критик прогона 4: снег на плашках почти не виден, на кнопках меню его нет). У первого листа (`wood-sheet.png`) снег 12 px из 158, при `SliceScale` около 0,26 — около 6 точек на экране, а на кнопке 60×60 углы с подтёками не помещались. Попыток по снежной плашке: 2 из 3 (первая — `wood-sheet.png`).
- Лист — исходник; в игре стоят куски (ImageMagick: рамка по альфе с полем 6 px, Lanczos, альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11):
  - `wood-plaque-snow-v2.png` 512×168 — длинная плашка со снегом, ключ `Wood:PlaqueSnow` (вырезка `1206x395+65+180`). 9-slice `HudWood.SLICE.PlaqueSnow`: центр `Rect.new(56, 74, 456, 118)`. Снег в середине — 21 px (строки 8–28), подтёки до x 51 слева и от x 460 справа, вниз до строки 70; шов доски — строки 86–89; нижнее скругление — от строки 118.
  - `wood-button-snow.png` 256×256 — квадратная плашка в одну доску со снегом, ключ `Wood:ButtonSnow` (вырезка `499x498+1562+134`). Центр `Rect.new(62, 84, 194, 198)`. Снег в середине — 24 px (строки 9–32), подтёки до x 58 и от x 197, вниз до строки 79; нижнее скругление — от строки 198.
- `SliceScale` — от глубины снега: 9,5 единицы элемента (`HudWood.sliceScale`), то есть 10–12 точек на экране 1920×1080; края куска не шире и не выше плашки. Квадратная доска — у кнопок меню, PETS/UPGR/INDEX и панели раунда (высокая длинная доска растягивала шов в тёмную полосу).
- Проверено: в середине кусков альфа 255, в углу 0, остатков 250–254 нет. На подложке «Камень» #909282 9-slice в размерах HUD (ведро 210×86, задание 370×56, кошелёк 150×132, панель раунда 280×236, кнопки 60×60 и 120×98, панель предметов 600×97, полоса оружия 400×42, плашка сохранения 480×100) снег — заметная подушка, подтёки у углов, обводка ровная, ореола нет. На полосе оружия высотой 42 края ограничивают масштаб: снег около 7 единиц.
- В Roblox не загружены: загрузка — только со слова владельца (`art/import.md`). Без id игра рисует плашку кодом без снега (запасной вид, `HudWood`). В Studio локальные копии кладёт `npm run ui:local`.
