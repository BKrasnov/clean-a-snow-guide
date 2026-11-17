# robot-head.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-16. Прозрачный фон запрошен.

## Prompt

Game UI icon for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the attached icon sheets of snow tools and pets (same thick dark brown outline, same soft top-left light, same flat colours, same toy-like chunky shapes).
One single icon on a fully transparent background, centred, filling most of the square picture with a small empty margin around it: the head of a friendly toy hockey robot, seen from the front and turned very slightly to the side, like the little robot heads in the round places of the attached hockey team panel.
The robot head: a chunky rounded-square metal head #A0B0C4 with soft darker shading #909282 on the lower right, a big rounded cream face screen #FFFDF5 on the front, two round shiny dark eyes #2B1A11 with a small cream highlight #FFFDF5, a small happy curved smile #2B1A11, two round grey ear bolts #909282 on the sides, one short thin antenna stalk #909282 on top with a round red bulb #D6392B with a small cream highlight. Thick dark brown outline #2B1A11 around every shape.
Only the head: no neck, no body, no hockey stick, no helmet, no text, no letters, no numbers, no circle or square tile or frame behind it, no shadow on the ground, no snow, no extra objects.
Readable at a small phone size of about 40 pixels, no watermark. Colours only from: #A0B0C4 #909282 #FFFDF5 #2B1A11 #D6392B #CDCDED.

## Референсы

- `art/ui/hotbar/hotbar-icons-sheet.png` — style reference.
- `art/ui/pets/pets-icons-sheet.png` (лист карточки `907897`) — style reference.
- `art/refs/hockey/start-gui.png` — style reference.

## Нарезка и проверка

- Карточка `657ae9`: голова робота для пустых мест хоккейной панели (`HockeyTeamsPanel`, ключ `Hockey:Robot` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau`). Карточка `907897` голов хоккея не рисовала и оставила их `657ae9`. Решение по режиму «апрув везде» (владелец 16.11.2026): нарисовать по утверждённому референсу панели `art/refs/hockey/start-gui.png` (серая голова, кремовое лицо с улыбкой, антенна с красной лампочкой).
- Попыток: 1. `robot-head-256.png` вырезана из `robot-head.png`: альфа ниже 40 обнулена, квадрат с полем 12 px, 256×256.
- Проверено: в середине альфа 251–253, в углу 0; одна голова без букв, рамок и лишних предметов; читается в круге места панели.
- В Roblox не загружена: загрузка — только со слова владельца, id вписывается в `ItemPictures.luau` (поле `id`). До загрузки в опубликованной игре — прежняя 3D-голова.
