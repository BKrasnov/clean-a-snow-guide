# hud-sparkles-512.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-19. Прозрачный фон запрошен.

## Prompt

Game UI effect picture for a Roblox cartoon winter farm game, in exactly the look of the gold sparkles around the full bucket counter "15/15" on the attached bucket counter sheet (the third board from the left): a burst of chunky cartoon gold sparkles that rings an empty middle.
One wide oval ring of sparkles on a fully transparent background, twice as wide as it is tall, filling the picture edge to edge with a small margin. The ring is made of about fourteen short thick rounded gold dashes #FFCE43 pointing outward like rays, evenly spread around the oval with gaps between them, and six small round gold dots #FFCE43 between the dashes, plus four small four-pointed gold stars #FFCE43 at the outer left, right, top and bottom. Every dash, dot and star has a thin dark brown outline #2B1A11 and a tiny cream highlight #FFFDF5 on its upper left. The whole middle of the oval, about two thirds of its width and height, is empty and fully transparent: nothing is drawn there.
Flat cartoon style, soft and friendly, readable at small phone size. No text, no letters, no numbers, no bucket, no board, no glow haze, no background, no shadows. Colours only from: #FFCE43 #2B1A11 #FFFDF5.

## Референсы

- `art/refs/hud-new/elements/07-bucket-counter.png` — style reference.
- `art/ui/hud/hud-icons-sheet.png` — style reference.

## Нарезка и проверка

- Круг 5 карточки `f2de28` (лист `art/refs/hud-new/elements/07-bucket-counter.png`: полное ведро «15/15» в искрах). Попыток: 1. Сгенерировано 1774×887; исходник в проект не положен, этот файл — его вырезка.
- Ключ `Hud:Sparkles` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau`: искры вокруг полного ведра (`Windows/Hud.luau`, `layBag`). Без картинки искры скрыты, «15/15» остаётся зелёным.
- Нарезка (ImageMagick): рамка по альфе с полем 6 px (`1771x857+2+7`), 512×248; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11.
- Проверено: середина овала пустая (альфа 0), в звезде альфа 254 → 255 после нарезки, угол 0; на подложке «Камень» #909282 чёрточки, точки и звёзды золотые #FFCE43 с тонким контуром #2B1A11 и кремовым бликом, ореола нет.
- В Roblox не загружено: загрузка — только со слова владельца (`art/import.md`).
