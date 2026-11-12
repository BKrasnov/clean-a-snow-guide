# hotbar-icons-sheet.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-12. Прозрачный фон запрошен.

## Prompt

Game UI icon sheet for a Roblox low-poly cartoon winter farm game, the same chunky 3D cartoon icon look as the icons in the bottom icon bar of the reference screenshot (the wooden spoon, the bottle and the grey padlock).
Nine tool icons on a fully transparent background, laid out in a 3 by 3 grid, evenly spaced with wide empty gaps between them so no two icons touch, each icon the same size and centred in its cell. No text, no letters, no numbers, no square tiles or frames behind the icons, no shadows on the ground.
Every tool is drawn the same way: one chunky toy-like cartoon object, soft light from the top-left, flat colours, a thick dark brown outline #2B1A11, long tools lie diagonally with the handle at the bottom-left and the working end at the top-right.
Row 1:
1 Wooden snow spoon: a big wooden spoon #CD925C with a darker grip #80401B, a heap of snow #F3F6F5 with shadow #CDCDED in its bowl.
2 Starter snow shovel: wooden handle #CD925C, short red blade #D6392B with lighter red ribs, a dark T-grip #2B1A11 with red sides #D6392B.
3 Steel snow shovel: wooden handle #CD925C, grey steel blade #A0B0C4 with a bright metal rim #F3F6F5, dark T-grip #2B1A11.
Row 2:
4 Snow pusher: wooden handle #CD925C, a very wide yellow pusher blade #FFCE43 with darker edges #C28E49 and a steel lip #A0B0C4, yellow T-grip.
5 Ice shovel: steel handle #A0B0C4, icy blue blade #8BE0FF with pale ice ribs #A8DEE7, blue-grey T-grip.
6 Snow vacuum: a short metal pipe handle #A0B0C4 with a T-grip, a round wooden-orange canister #C28E49 with dark caps #2B1A11 and a tiny green light #5BB830, a wide gold intake mouth #FFCE43 at the top-right end.
Row 3:
7 Turbo vacuum: a bigger blue backpack-style vacuum body #80A0E6 with gold bands #FFCE43, a dark rubber hose #2B1A11, a wide gold and orange nozzle #FFCE43 #C28E49, a steel grill #A0B0C4; it must look clearly stronger and different from icon 6.
8 Fire bottle: a chunky glass bottle #A8DEE7 with a cloth wick #F3F6F5 and a small flame #FFCE43 #D6392B on top, exactly like the bottle icon in the reference.
9 Locked slot content: a faded flat silhouette of a big snow tool in #A0B0C4 behind a chunky gold padlock #FFCE43 with a dark keyhole #2B1A11, exactly like the padlock icon in the reference.
Readable at small phone size, no extra objects, no watermark. Colours only from: #F3F6F5 #CDCDED #A8DEE7 #8BE0FF #CD925C #80401B #2B1A11 #C28E49 #FFCE43 #D6392B #A0B0C4 #80A0E6 #5BB830 #FFFDF5.

## Референсы

- `art/refs/run-hotbar/run-hotbar.png` — style reference.
- `art/frames/02-snow-run.jpeg` — style reference.

## Нарезка и проверка

- Попыток: 1. Лист разрезан на девять иконок `hotbar-<предмет>-256.png`: spoon, starter-shovel, steel-shovel, snow-pusher, ice-shovel, snow-vacuum (инструмент Snow Vacuum), turbo-vacuum (оружие `SnowVacuum`, Turbo Vacuum), molotov, donate-lock. Нарезка — сетка 3×3, в клетке самый большой кусок по альфе, квадрат с полем 12 px, альфа ниже 40 обнулена, 256×256.
- Проверено: в середине предмета альфа 253–254, в углу 0; на тёмном дереве #80401B все девять читаются.
- В Roblox не загружены (карточка `7852ff`): загрузка — только со слова владельца, до неё в игре 3D-модели. Загруженные id вписываются в `ICON_IMAGES` в `RunHotbarView.luau`.
