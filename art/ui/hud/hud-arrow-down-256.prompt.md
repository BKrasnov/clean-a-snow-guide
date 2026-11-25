# hud-arrow-down-256.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-20. Прозрачный фон запрошен.

## Prompt

Game UI icon for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the big down arrow under the SELL sign on the attached prompts sheet (second reference): the same thick dark brown outline, the same soft top-left light, the same flat colours, the same toy-like chunky shapes.
One icon on a fully transparent background, centred, filling about 80 percent of the picture, nothing else in the picture. No text, no letters, no numbers, no wooden plank, no sign, no posts, no snow, no tile, frame or circle behind the icon, no shadow on the ground.
The icon: one chunky cartoon arrow pointing straight down, a short wide stem on top and a big wide triangular head at the bottom with rounded corners, gold #FFCE43 on the front with a soft orange #F8AA3C shade on its lower and right sides, a thin cream highlight #FFFDF5 along its upper left edges, and a thick dark brown outline #2B1A11 around the whole arrow.
Simple bold shapes that read at 40 pixels on a phone. Readable at small phone size, no extra objects, no watermark. Colours only from: #FFCE43 #F8AA3C #FFFDF5 #2B1A11.

## Референсы

- `art/refs/hud-new/key/run-pc.png` — style reference.
- `art/refs/hud-new/elements/19-prompts.png` — style reference.

## Нарезка и проверка

- Попыток: 1 (карточка `8a8c91`, волна 2 HUD). Исходник 1312×1199 в scratchpad, в проект положен только значок.
- Этот файл — стрелка вниз под табличкой SELL над лотком переработки (лист `art/refs/hud-new/elements/19-prompts.png`); ключ `Hud:ArrowDown` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau` (строку добавляет оркестратор).
- Нарезка (ImageMagick): прямоугольник по альфе `1023x1020+144+113`, дополнен прозрачным до квадрата 1128×1128 (поле около 12 px после уменьшения), 256×256, 8 бит; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11.
- Проверено: в середине стрелки альфа 255, в углах 0 (ffmpeg, ImageMagick `txt:`); на подложке «Камень» #909282 и на доске #C28E49 в 40 px стрелка читается, обводка ровная, фона, столбиков и ореола нет, букв нет.
- В Roblox не загружен: загрузка — только со слова владельца (`art/import.md`). Без id табличка SELL остаётся без стрелки.
