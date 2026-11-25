# hud-chest-256.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-19. Прозрачный фон запрошен.

## Prompt

Game UI icon sheet for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the attached icon sheet (second reference): the same thick dark brown outline, the same soft top-left light, the same flat colours, the same toy-like chunky shapes.
Three icons on a fully transparent background, in one row, evenly spaced with wide empty gaps between them so no two icons touch, each icon the same size and centred in its third of the picture. No text, no letters, no numbers, no square tiles, buttons or frames behind the icons, no shadows on the ground.
Every icon is drawn the same way: one chunky toy-like cartoon object, soft light from the top-left, flat colours, a thick dark brown outline #2B1A11. Simple bold shapes that read at 40 pixels on a phone.
1 Fire: one chunky cartoon flame with three rounded tongues, outer flame orange #F8AA3C, inner flame gold #FFCE43, a cream core #FFFDF5 near the bottom, a little red #D6392B at the outer bottom edge.
2 Truck: one chunky toy dump truck seen from the front-left three-quarter view, like the truck in the attached bucket counter sheet: a red cab #D6392B with a pale blue window #A8DEE7, a gold-yellow dump body #FFCE43 heaped with soft snow #F3F6F5 shaded lavender #CDCDED, round dark tyres #2B1A11 with grey hubs #A0B0C4.
3 Chest: one chunky treasure chest with a rounded lid, red wood #D6392B with gold bands #FFCE43 and a gold lock plate with a dark keyhole #2B1A11, and a big bold green check mark #5BB830 with a lighter edge #96DC6A overlapping its lower right corner, like the chest on the attached save note sheet.
Readable at small phone size, no extra objects, no watermark. Colours only from: #F8AA3C #FFCE43 #FFFDF5 #D6392B #A8DEE7 #F3F6F5 #CDCDED #2B1A11 #A0B0C4 #5BB830 #96DC6A.

## Референсы

- `art/refs/hud-new/key/run-pc.png` — style reference.
- `art/ui/hud/hud-icons-sheet.png` — style reference.
- `art/refs/hud-new/elements/07-bucket-counter.png` — style reference.
- `art/refs/hud-new/elements/08-tool-bar.png` — style reference.
- `art/refs/hud-new/elements/14-save-note.png` — style reference.

## Нарезка и проверка

- Попыток: 1 (карточка `f2de28`, волна 1 HUD). Генерировался лист из трёх значков в ряд (огонь, грузовик, сундук), 2172×724; лист в проект не положен — исходник по этому промпту, место листа — вопрос оркестратору.
- Этот файл — сундук с галочкой (плашка YOUR PROGRESS SAVES), ключ `Hud:Chest` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau`.
- Нарезка (ImageMagick): квадрат `608x608+1487+74` вокруг значка по альфе с полем 12 px, 256×256; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11.
- Проверено: в середине значка альфа 255, в углу 0; на подложке «Камень» #909282 значок читается, обводка ровная, фона и ореола нет.
- В Roblox не загружен: загрузка — только со слова владельца (`art/import.md`). Без id значок в игре скрыт.
