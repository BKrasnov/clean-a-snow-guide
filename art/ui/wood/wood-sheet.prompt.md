# wood-sheet.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-19. Прозрачный фон запрошен.

## Prompt

Game UI parts sheet for a Roblox cartoon winter farm game: the snowy wooden boards of the HUD, in exactly the look of the attached approved element sheets (the wallet and quick menu boards of the first reference, the task line boards of the second): chunky rounded wooden boards with rich wood grain, a thick dark brown outline, soft light from the top, and a thin layer of snow lying on their top edge.
Four separate parts on a fully transparent background, laid out in a 2 by 2 grid with wide empty gaps so no two parts touch, each part centred in its cell. Every part is seen straight from the front, flat, no perspective, no tilt, no drop shadow, no background.
1 (top left) Snowy wood plaque: one empty wooden board shaped as a wide rounded rectangle, exactly four times as wide as it is tall, the corner radius about a third of its height. Rich saturated wood: base plank colour #C28E49, wood grain lines and a darker bevel along the inner bottom edge in #80401B, a lighter strip #CD925C along the inner top edge, one straight horizontal plank seam #80401B running the whole width exactly through the middle of its height, a thick dark brown outline #2B1A11 of exactly the same thickness all around. Snow is part of the same board: a thin layer of soft cartoon snow #F3F6F5 with a lavender shade #CDCDED on its underside lies right on the top edge of the board, hugs and rounds over both top corners and runs a little way down each side, with small uneven rounded drips hanging down only near the two top corners. Across the middle third of the width the snow layer is perfectly even in thickness, a smooth band with no drips and no bumps. The snow has the same thin dark outline #2B1A11 as the board. Nothing else on it: no text, no icons, no nails, no knots.
2 (top right) Bare wood plaque: exactly the same board as part 1, the same size, shape, wood, seam and outline, but with no snow at all: the clean wooden top edge with its lighter strip #CD925C is visible.
3 (bottom left) Round snowy wood button: one round wooden disc seen from the front, in the same rich wood as part 1: base #C28E49, grain and bottom bevel #80401B, lighter top #CD925C, a thick outline #2B1A11, and the same thin snow layer #F3F6F5 with lavender shade #CDCDED lying on its top arc and hugging it, with small drips. The middle is empty: no icon, no text.
4 (bottom right) Round snowy gold button: the same round disc in gold #FFCE43 with an orange-gold bevel #F8AA3C at the bottom and a cream shine #FFFDF5 at the top left, the same thick outline #2B1A11 and the same thin snow layer with small drips on its top arc. The middle is empty: no icon, no text.
No text, no letters, no numbers, no icons, no background, no extra frames or shadows. Colours only from: #C28E49 #CD925C #80401B #2B1A11 #F3F6F5 #CDCDED #FFCE43 #F8AA3C #FFFDF5.

## Референсы

- `art/refs/hud-new/elements/01-wallet-quick-menu.png` — style reference.
- `art/refs/hud-new/elements/10-task-line.png` — style reference.

## Нарезка и проверка

- Круг 2 карточки `f2de28` (замечание владельца 19.11.2026: снег отдельной полосой поверх доски выглядит плохо, плашку сразу генерировать со снегом, как на референсах). Попыток: 1. Этот лист заменил прежний лист с отдельной снежной шапкой; `snow-cap.png` и ключ `Wood:SnowCap` убраны.
- Лист — исходник; в игре стоят куски (ImageMagick: рамка по альфе с полем 6 px, Lanczos, альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11):
  - `wood-plaque-snow.png` 512×158 — плашка со снегом, ключ `Wood:PlaqueSnow` (вырезка `821x254+33+120`). 9-slice `HudWood.SLICE.PlaqueSnow`: центр `Rect.new(104, 52, 408, 110)`. Слева и справа по 104 px — углы с подтёками; в средней трети снег ровный (нижний край на y 24), поэтому растяжка по ширине незаметна. Сверху 52 px — снег и скругление, снизу 48 px — фаска и обводка. Шов доски (y 81–83) — в растягиваемой середине, поэтому на высокой плашке он остаётся посередине.
  - `wood-plaque.png` 512×155 — та же плашка без снега, ключ `Wood:Plaque` (вырезка `821x248+920+126`). Центр `Rect.new(56, 48, 456, 110)`.
  - Скругление угла у обеих плашек — около 46 px (`HudWood.PICTURE_CORNER`): `SliceScale = радиус / 46`, но углы не шире и не выше самой плашки.
  - `wood-round.png` 256×256 — круглая деревянная кнопка со снегом, ключ `Wood:Round` (квадрат `351x351+268+492`).
  - `wood-round-gold.png` 256×256 — круглая золотая кнопка со снегом, ключ `Wood:RoundGold` (квадрат `351x351+1155+491`).
- Проверено: в середине куска альфа 255, в углу 0, остатков 250–254 нет. На подложке «Камень» #909282 9-slice в размерах HUD (задание 520×56, кошелёк 210×132 со снегом и без, кнопка 60×60, ведро 236×86, панель раунда 280×204) снег — тонкий ровный слой на верхнем крае, обнимает оба угла, мелкие подтёки только у углов. Шов посередине; на высоких плашках волокна и шов толще, но не рвутся. Обводка ровная, ореола нет.
- В Roblox не загружены: загрузка — только со слова владельца (`art/import.md`). Без id игра рисует плашку кодом без снега (запасной вид, `HudWood`).
