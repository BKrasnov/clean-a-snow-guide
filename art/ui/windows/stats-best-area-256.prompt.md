# stats-best-area-256.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-23. Прозрачный фон запрошен.

## Prompt

Game UI icon sheet for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the attached icon sheet (second reference): the same thick dark brown outline, the same soft top-left light, the same flat colours, the same toy-like chunky shapes.
Three icons on a fully transparent background, in one row, evenly spaced with wide empty gaps between them so no two icons touch, each icon the same size and centred in its third of the picture. No text, no letters, no numbers, no square tiles, buttons or frames behind the icons, no shadows on the ground.
Every icon is drawn the same way: one chunky toy-like cartoon object, soft light from the top-left, flat colours, a thick dark brown outline #2B1A11. Simple bold shapes that read at 40 pixels on a phone.
1 Best area: one chunky cartoon mountain with two rounded peaks, blue-grey rock #A0B0C4 with snowy tops #F3F6F5 shaded lavender #CDCDED, and a big bold gold star #FFCE43 with an orange edge #F8AA3C sitting on the higher peak.
2 Frostwood: one chunky cartoon pine tree with three rounded layers, green #3C8E63 with lighter green edges #54A577, every layer heaped with soft snow #F3F6F5 shaded lavender #CDCDED, a short dark wood trunk #80401B.
3 Together: two chunky cartoon winter mittens giving each other a high five, one red #D6392B and one crystal blue #8BE0FF, each with a cream cuff #FFFDF5, and a small gold sparkle #FFCE43 where they touch.
Readable at small phone size, no extra objects, no watermark. Colours only from: #A0B0C4 #F3F6F5 #CDCDED #FFCE43 #F8AA3C #3C8E63 #54A577 #80401B #D6392B #8BE0FF #FFFDF5 #2B1A11.

## Референсы

- `art/refs/hud-new/key/run-pc.png` — style reference.
- `art/ui/hud/hud-wood-icons-sheet.png` — style reference.
- `art/ui/hud/hud-fire-256.png` — style reference.

## Нарезка и проверка

- Попыток: 1 (карточка `6137fd`, часть 3 `4875c7`). Лист 2172×724, три значка в ряд (best area, Frostwood, together), этот — 1-й; лист в проект не положен — исходник по этому промпту.
- Этот файл — YOUR EXPEDITION, строка лучшей зоны, ключ `Window:BestArea` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau`.
- Нарезка (Pillow): значок между пустыми столбцами листа, квадрат вокруг него по альфе с полем около 2 %, 256×256; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11.
- Проверено: в середине значка альфа 255, в углу 0; на тёмной плитке окна значок читается, обводка ровная, фона и ореола нет.
- В Roblox не загружен: загрузка — только со слова владельца (`art/import.md`). Без id плитка значка в игре скрыта.
