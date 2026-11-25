# settings-camera-shake-256.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-23. Прозрачный фон запрошен.

## Prompt

Game UI icon sheet for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the attached icon sheet (second reference): the same thick dark brown outline, the same soft top-left light, the same flat colours, the same toy-like chunky shapes.
Three icons on a fully transparent background, in one row, evenly spaced with wide empty gaps between them so no two icons touch, each icon the same size and centred in its third of the picture. No text, no letters, no numbers, no square tiles, buttons or frames behind the icons, no shadows on the ground.
Every icon is drawn the same way: one chunky toy-like cartoon object, soft light from the top-left, flat colours, a thick dark brown outline #2B1A11. Simple bold shapes that read at 40 pixels on a phone.
1 Falling snow: three big chunky cartoon snowflakes of different sizes falling one above the other on a slight diagonal, each with six thick rounded arms, snow white #F3F6F5 with lavender shading #CDCDED on the lower right of every arm and a pale ice blue centre #A8DEE7.
2 Sound: one chunky cartoon loudspeaker seen from the front-left: a squat dark wood box #80401B with a light wood front #CD925C and a big round cone in cream #FFFDF5 shaded lavender #CDCDED, and two thick curved sound waves in crystal blue #8BE0FF coming out to the right.
3 Camera shake: one chunky cartoon photo camera seen from the front: a rounded body in dark wood #80401B with a light wood top #CD925C, a big round lens ring in stone grey #909282 around pale blue glass #A8DEE7 with a cream glint #FFFDF5, and three short thick shake lines in cream #FFFDF5 outlined dark brown on each side of the camera.
Readable at small phone size, no extra objects, no watermark. Colours only from: #F3F6F5 #CDCDED #A8DEE7 #8BE0FF #FFFDF5 #CD925C #80401B #909282 #2B1A11.

## Референсы

- `art/refs/hud-new/key/run-pc.png` — style reference.
- `art/ui/hud/hud-wood-icons-sheet.png` — style reference.
- `art/ui/hud/hud-fire-256.png` — style reference.

## Нарезка и проверка

- Попыток: 1 (карточка `6137fd`, часть 3 `4875c7`). Лист 2172×724, три значка в ряд (falling snow, sound, camera shake), этот — 3-й; лист в проект не положен — исходник по этому промпту.
- Этот файл — SETTINGS, строка «тряска камеры», ключ `Window:CameraShake` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau`.
- Нарезка (Pillow): значок между пустыми столбцами листа, квадрат вокруг него по альфе с полем около 2 %, 256×256; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11.
- Проверено: в середине значка альфа 255, в углу 0; на тёмной плитке окна значок читается, обводка ровная, фона и ореола нет.
- В Roblox не загружен: загрузка — только со слова владельца (`art/import.md`). Без id плитка значка в игре скрыта.
