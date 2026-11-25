# buckets-snow-sheet.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-19. Прозрачный фон запрошен.

## Prompt

Game UI icon sheet for a Roblox low-poly cartoon winter farm game: the SAME five buckets as the attached bucket icon sheet (identical shapes, colours, outline, angle, light and size), but now each bucket is FULL OF SNOW. Keep every bucket exactly as on the attached sheet; only add the snow.
The snow: a soft rounded heap of packed snow filling the opening and rising a little above the rim, like a scoop of ice cream, made of a few big round lumps, bright white top #F3F6F5 with soft lavender-grey shade #CDCDED on the lower lumps and a little #B3C2D4 in the deepest creases, the same thick dark brown outline #2B1A11 around the snow as around the bucket. The heap hides the dark inside of the bucket. The handle still stands up over the snow and is drawn in front of the heap where it crosses it. A few tiny snow crumbs on top, nothing falling, no sparkles.
Layout: a fully transparent background, a 3 by 2 grid (three icons in the top row, two in the bottom row in the first two cells, the sixth cell bottom right left completely empty), evenly spaced with wide empty gaps between them so no two icons touch, each icon the same size and centred in its cell, the same cell positions as the attached sheet.
Row 1: 1 Starter bucket (plain grey-blue steel #A0B0C4, grey rim, foot ring and thin wire handle #909282). 2 Trail bucket (wooden barrel staves #CD925C, dark hoops #80401B, straw-yellow handle #FAD66E). 3 Expedition bucket (red body #D6392B, steel rim and foot ring #A0B0C4, steel handle with a wooden grip #CD925C).
Row 2: 4 Hauler bucket (big blue #80A0E6 with gold rim, middle hoop and foot ring #FFCE43, thick dark handle and side grips #2B1A11). 5 Glacier bucket (pale ice body #A8DEE7, crystal-blue rim, hoop, foot ring and handle #8BE0FF, white icicles #F3F6F5 under the rim).
All five buckets drawn at the SAME size. Chunky toy-like cartoon look, flat colours, soft top-left light, thick dark brown outline #2B1A11. No text, no letters, no numbers, no square tiles or frames behind the icons, no shadows on the ground, no extra objects, no watermark. Readable at small phone size.
Colours only from: #A0B0C4 #909282 #CD925C #80401B #FAD66E #D6392B #80A0E6 #FFCE43 #2B1A11 #A8DEE7 #8BE0FF #F3F6F5 #CDCDED #B3C2D4 #FFFDF5.

## Референсы

- `art/ui/buckets/buckets-icons-sheet.png` — style reference.
- `art/refs/hud-new/elements/07-bucket-counter.png` — style reference.
- `art/frames/02-snow-run.jpeg` — style reference.

## Нарезка и проверка

- Карточка `f2de28`, круг 6 (дизайн-критик, лист 07: ведро «9/15» со снегом). Попыток: 1.
- Лист разрезан на пять иконок `bucket-<имя>-snow-256.png` тем же способом, что `buckets-icons-sheet.png`: сетка 3×2 (шестая клетка пустая), в клетке куски по альфе не меньше 2 % самого большого, квадрат с полем 12 px, альфа ниже 40 обнулена, цвет прозрачных пикселей — контур #2B1A11, 256×256. Скрипт нарезки был временным (в scratchpad), в проект не входит.
- Проверено: в середине предмета альфа 254–255, в углу 0; рамка снежного Starter совпадает с пустым (40–215 по ширине, 12–243 по высоте), поэтому ведро при смене картинки не прыгает; все пять читаются на доске #C28E49 в 256 и 56 px.
- Ключи `BucketSnow:<bagId>` в `Shared/ItemPictures.luau`: счётчик ведра показывает их, когда в ведре есть снег (`ItemPictures.bucketKey`), пустое ведро — как раньше.
- В Roblox не загружены: загрузка — только со слова владельца (`art/import.md`).
