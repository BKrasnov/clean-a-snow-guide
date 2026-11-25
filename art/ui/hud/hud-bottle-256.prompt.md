# hud-bottle-256.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-19. Прозрачный фон запрошен.

## Prompt

Game UI icon for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the attached flame icon (second reference): the same thick dark brown outline, the same soft top-left light, the same flat colours, the same toy-like chunky shape.
One icon on a fully transparent background, centred, filling most of the picture with a small empty margin. No text, no letters, no numbers, no square tile, button, plaque or frame behind the icon, no shadow on the ground, no other objects.
The icon: one chunky squat cartoon glass bottle, exactly like the small bottle at the left end of the wooden bar in the first reference: a wide rounded body almost as wide as it is tall, a short thick neck and a cork stopper on top. Pale blue glass #A8DEE7 with a crystal blue lower half #8BE0FF, a soft cream highlight #FFFDF5 on the upper left of the body, a cork of light wood #CD925C shaded with dark wood #80401B, a thick dark brown outline #2B1A11 around everything. No flame, no wick, no label, no liquid line drawn as text.
Simple bold shape that reads at 40 pixels on a phone, about as big and heavy as the flame icon of the second reference. No watermark. Colours only from: #A8DEE7 #8BE0FF #FFFDF5 #CD925C #80401B #2B1A11.

## Референсы

- `art/refs/hud-new/elements/08-tool-bar.png`, вырезка `560x190+1100+720` (третья полоса с бутылкой) — style reference.
- `art/ui/hud/hud-fire-256.png` — style reference.
- `art/refs/hud-new/key/run-pc.png` — style reference.

## Нарезка и проверка

- Попыток: 1 (карточка `f2de28`, круг 7: дизайн-критик прогона 11 — бутылка Молотова на полосе мелкая, на листе 08 — пузатая бутылка с пробкой размером с огонь). Сгенерирован один значок 1254×1254; исходник в проект не положен.
- Ключ `Hud:Bottle` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau`: значок полосы оружия, пока Молотов ждёт броска (`WeaponController`). Без картинки там старая иконка Молотова (его картинка или 3D-модель).
- Нарезка (ImageMagick): квадрат `1234x1234+2+21` вокруг значка по альфе с полем около 2 %, 256×256; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11. Значок занимает 198×246 из 256, как огонь (212×246).
- Проверено: в середине стекла и на пробке альфа 255, в углу 0; на подложке «Камень» #909282 и на доске #C28E49 в 44 пикселях значок читается, обводка ровная, фона и ореола нет.
- В Roblox не загружен: загрузка — только со слова владельца (`art/import.md`). Без id в опубликованной игре на полосе стоит старая иконка Молотова.
