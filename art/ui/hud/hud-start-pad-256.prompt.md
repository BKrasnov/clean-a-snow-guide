# hud-start-pad-256.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-20. Прозрачный фон запрошен.

## Prompt

Game UI icon for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the start pad picture on the left of the attached first-run plate sheet (second reference): the same thick dark brown outline, the same soft top-left light, the same flat colours, the same toy-like chunky shapes.
One icon on a fully transparent background, centred, filling about 80 percent of the picture, nothing else in the picture. No text, no letters, no numbers, no wooden plank, no snow, no tile, frame or circle behind the icon, no shadow on the ground.
The icon: one chunky square start pad seen from the front-left three-quarter view from a little above, like a low square platform: a bright green top #5BB830 with a lighter green raised rim #96DC6A around it, a thick grey stone base #909282 with lighter metal grey sides #A0B0C4, and four chunky gold corner caps #FFCE43 on its corners. A thick dark brown outline #2B1A11 around the pad, the rim and each corner cap.
Simple bold shapes that read at 40 pixels on a phone. Readable at small phone size, no extra objects, no watermark. Colours only from: #5BB830 #96DC6A #909282 #A0B0C4 #FFCE43 #2B1A11 #FFFDF5.

## Референсы

- `art/refs/hud-new/key/run-pc.png` — style reference.
- `art/refs/hud-new/elements/04-first-run-plate.png` — style reference.

## Нарезка и проверка

- Попыток: 1 (карточка `8a8c91`, волна 2 HUD). Исходник 1448×1086 в scratchpad, в проект положен только значок.
- Этот файл — площадка старта на плашке первого забега (лист `art/refs/hud-new/elements/04-first-run-plate.png`); ключ `Hud:StartPad` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau` (строку добавляет оркестратор).
- Нарезка (ImageMagick): прямоугольник по альфе `1145x821+145+126`, дополнен прозрачным до квадрата 1263×1263 (поле около 12 px после уменьшения), 256×256, 8 бит; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11.
- Проверено: в середине площадки альфа 255, в углах 0 (ffmpeg, ImageMagick `txt:`); на подложке «Камень» #909282 и на доске #C28E49 в 40 px значок читается, обводка ровная, фона, плитки и ореола нет, букв нет.
- В Roblox не загружен: загрузка — только со слова владельца (`art/import.md`). Без id плашка первого забега остаётся без картинки, строки сдвигаются влево.
