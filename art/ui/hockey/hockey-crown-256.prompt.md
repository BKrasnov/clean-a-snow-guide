# hockey-crown-256.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-19. Прозрачный фон запрошен.

## Prompt

Game UI icon sheet for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the attached icon sheet (third reference): the same thick dark brown outline, the same soft top-left light, the same flat colours, the same toy-like chunky shapes.
Two icons on a fully transparent background, side by side in one row, with a wide empty gap between them so they never touch, each icon the same size and centred in its half of the picture. No text, no letters, no numbers, no square tiles, buttons, ribbons or frames behind the icons, no shadows on the ground.
Every icon is drawn the same way: one chunky toy-like cartoon object, soft light from the top-left, flat colours, a thick dark brown outline #2B1A11. Simple bold shapes that read at 40 pixels on a phone.
1 Crown: one chunky winner's crown seen from the front, like the gold crown on top of the RED WINS ribbon in the attached hockey match sheet (second reference): a wide rounded gold band #FFCE43 with three big rounded points, a round ball on the tip of each point, a lighter straw highlight #FAD66E on the top-left faces, a deeper orange #F8AA3C shade on the lower right, one small red gem #D6392B in the middle of the band.
2 Hockey stick: one chunky cartoon ice hockey stick standing diagonally, the long handle going from the upper right down to the lower left, ending in a wide flat blade that bends to the left along the bottom, like the stick on the round gold button in the attached hockey match sheet: warm light wood #CD925C with darker wood grain #80401B, a cream tape wrap #FFFDF5 around the blade and a short cream grip tape #FFFDF5 at the top of the handle.
Readable at small phone size, no extra objects, no puck, no watermark. Colours only from: #FFCE43 #FAD66E #F8AA3C #D6392B #CD925C #80401B #FFFDF5 #2B1A11.

## Референсы

- `art/refs/hud-new/key/run-pc.png` — style reference.
- `art/refs/hud-new/elements/17-hockey-match.png` — style reference.
- `art/ui/hud/hud-icons-sheet.png` — style reference.

## Нарезка и проверка

- Попыток: 1 (карточка `73e79b`, волна 2 HUD). Генерировался лист из двух значков в ряд (корона, клюшка), 2172×724; лист в проект не положен — исходник по этому промпту.
- Этот файл — корона на ленте RED WINS! / BLUE WINS! в конце матча (лист 17), ключ `Hockey:Crown` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau`.
- Нарезка (ImageMagick): прямоугольник `710x592+201+76` вокруг значка по альфе, дополнен прозрачным до квадрата с полем около 12 px, 256×256; альфа ниже 40 обнулена, 250–254 поднята до 255, цвет прозрачных пикселей — контур #2B1A11.
- Проверено: в середине значка альфа 255, в углу 0; полупрозрачных пикселей около 1000 — только сглаженный край; на подложке «Камень» #909282 значок читается и в 48 px, обводка ровная, фона и ореола нет.
- В Roblox не загружен: загрузка — только со слова владельца (`art/import.md`). Без id значок в опубликованной игре скрыт.
