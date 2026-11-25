# hud-tap-256.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-20. Прозрачный фон запрошен.

## Prompt

Game UI icon for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the hand on the TAP button of the attached action button sheet (second reference): the same thick dark brown outline, the same soft top-left light, the same flat colours, the same toy-like chunky shapes.
One icon on a fully transparent background, centred, filling about 80 percent of the picture, nothing else in the picture. No text, no letters, no numbers, no round wooden button, no plank, no snow, no tile, frame or circle behind the icon, no shadow on the ground.
The icon: one chunky cartoon hand seen from the back, the index finger pointing up and a little to the left as if tapping a screen, the other fingers curled into the palm, the thumb tucked at the side. Skin #F2C29A with a slightly darker skin crease line in dark brown #2B1A11, a chunky green sleeve cuff #5BB830 with a lighter top edge #96DC6A at the wrist in the lower right. Three short bold gold tap marks #FFCE43 with a dark brown outline fan out around the fingertip at the upper left, like the tap marks on the attached sheet. A thick dark brown outline #2B1A11 around the hand, the cuff and each tap mark.
Simple bold shapes that read at 40 pixels on a phone. Readable at small phone size, no extra objects, no watermark. Colours only from: #F2C29A #5BB830 #96DC6A #FFCE43 #2B1A11 #FFFDF5.

## Референсы

- `art/refs/hud-new/key/run-pc.png` — style reference.
- `art/refs/hud-new/elements/18-action-button.png` — style reference.

## Нарезка и проверка

- Попыток: 1 (карточка `819c27`, волна 2 HUD). Исходник 1199×1312 в scratchpad, в проект положен только значок.
- Этот файл — рука TAP на круглой кнопке действия (лист `art/refs/hud-new/elements/18-action-button.png`), когда в руках оружие со стойки или особый предмет; ключ `Hud:Tap` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau` (строку добавляет оркестратор).
- Нарезка (ImageMagick): прямоугольник по альфе `968x1215+94+45`, дополнен прозрачным до квадрата 1341×1341 (поле около 12 px после уменьшения), 256×256; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11.
- Проверено: в середине руки альфа 255, в углах 0; на подложке «Камень» #909282 значок читается, обводка ровная, фона, кружка и ореола нет, букв нет.
- В Roblox не загружен: загрузка — только со слова владельца (`art/import.md`). Без id на кнопке остаётся слово TAP без иконки.
