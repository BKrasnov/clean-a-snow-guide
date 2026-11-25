# window-buttons-bare.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-23. Прозрачный фон запрошен.

## Prompt

Game UI parts sheet for a Roblox cartoon winter farm game: the window buttons of the first attached sheet (a red close button, a green button, a red button) and the square wooden button of the second attached sheet, in exactly their look, but with NO snow at all: chunky rounded buttons, a thick dark brown outline, soft light from the top, a thin darker bevel along the inner bottom edge. The top edge of every button is a plain rounded edge with the same thick outline as the sides and the bottom: no snow cushion, no drips, no white or lavender anywhere.

Four separate square buttons on a fully transparent background, in a two by two grid, with a wide empty gap between them so they never touch, each centred in its quarter of the sheet. Every button is seen straight from the front, flat, no perspective, no tilt, no drop shadow, no background. All four have exactly the same size and shape: a square with rounded corners, exactly as wide as it is tall, the corner radius about one fifth of its side, a thick dark brown outline #2B1A11 of the same thickness all around, a soft lighter band along the inner top edge, and a thin darker bevel along the inner bottom edge (its colour is given for each button).

1 (top left) Close button: red #D6392B with a bottom bevel #80401B, and in its middle a bold cartoon cross made of two thick rounded bars, cream #FFFDF5 with the thick dark outline #2B1A11, about half as wide as the button.
2 (top right) Green button: green #5BB830 with a bottom bevel #3C8E63. Everything inside is one flat even green: no text, no icon, no gradient, no texture.
3 (bottom left) Red button: red #D6392B with a bottom bevel #80401B. Everything inside is one flat even red: no text, no icon, no gradient, no texture.
4 (bottom right) Wooden button: one single plank of rich wood with no seam, base #C28E49, soft wood grain lines and the bottom bevel #80401B, like the square wooden button of the second sheet without its snow. The middle is empty.

Nothing else: no letters, no numbers, no icons except the cross of button 1, no nails, no knots, no snow, no background, no extra frames or shadows. Colours only from: #D6392B #5BB830 #3C8E63 #C28E49 #80401B #FFFDF5 #2B1A11.

## Референсы

- `art/ui/wood/window-buttons.png` — style reference.
- `art/ui/wood/wood-sheet-v2.png` — style reference.
- `art/refs/windows-wood/upgrades-window.png` — style reference.

## Нарезка и проверка

- Карточка `1cf3e9` (владелец 23.11.2026: снег остаётся только на деревянных плашках — доске окна и плашке заголовка, кнопки окон и крестик без снега), попытка 1 из 3.
- Кнопка на листе — квадрат с краями по альфе (порог 128): закрытие `(58, 57)–(584, 582)`, зелёная `(669, 57)–(1195, 582)`, красная `(58, 671)–(584, 1196)`, деревянная `(669, 671)–(1196, 1196)`. Каждая вырезана с полем 6 пикселей и уменьшена до 256×256 с весом цвета по альфе (без тёмной каймы). Края куска — пиксели 3…252.
  - `window-close.png`, ключ `Wood:Close`: центр в один пиксель (`Rect.new(126, 200, 127, 201)`), `whole` — кнопка масштабируется целиком, крестик не растягивается.
  - `button-green.png`, `button-red.png`, `button-wood.png`, ключи `Wood:Green`, `Wood:Red`, `Wood:Button`: центр `Rect.new(56, 56, 200, 200)`, угол 44–45 пикселей, обводка около 10, светлая полоса сверху — строки 13–25, фаска снизу — 225–242.
- В Roblox не загружены (`art/import.md`). Без id — кнопки кодом без снега, как раньше.
