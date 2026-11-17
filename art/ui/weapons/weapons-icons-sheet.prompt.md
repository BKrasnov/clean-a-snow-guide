# weapons-icons-sheet.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-17. Прозрачный фон запрошен.

## Prompt

Game UI icon sheet for a Roblox low-poly cartoon winter farm game, the exact same chunky 3D cartoon icon look as the attached icon sheet of snow tools (same thick dark brown outline, same soft top-left light, same flat colours, same toy-like chunky shapes). The six snow weapons follow the shapes and colour zones of the attached lineup of their in-game 3D models, redrawn in the icon style.
Eight icons on a fully transparent background, laid out in a 4 by 2 grid (four icons in the top row, four in the bottom row), evenly spaced with wide empty gaps between them so no two icons touch, each icon the same size and centred in its cell. No text, no letters, no numbers, no square tiles or frames behind the icons, no shadows on the ground, no fire, no smoke, no snow spray.
Every icon is drawn the same way: one chunky toy-like cartoon object, soft light from the top-left, flat colours, a thick dark brown outline #2B1A11; long tools lie diagonally with the handle at the bottom-left and the working end at the top-right.
Row 1:
1 Ice axe: a long gold-yellow shaft #FFCE43 with a darker gold band #C28E49 near the middle, a small square blue head #80A0E6 with a steel bolt at the top, a long curved steel pick #A0B0C4 with a jagged underside to one side and a short flat steel adze #A0B0C4 to the other side, a steel spike at the bottom end with a small red wrist strap #D6392B.
2 Big spoon: a huge steel ladle spoon #A0B0C4 with a bright rim #F3F6F5, a deep round bowl with a dark hole in its middle, a thick red handle #D6392B. Clearly metal, not wood.
3 Big shovel: a steel shaft #A0B0C4 with a dark grip #2B1A11 at the bottom-left end, a big square red blade #D6392B with two raised side walls and a pale shine #F3F6F5. Steel and red only, no wood.
4 Jackhammer: standing upright, a chunky gold-yellow ribbed body #FFCE43 with a darker band #C28E49, a dark T-bar handle #2B1A11 with steel #A0B0C4 between the two grips on top, a steel chisel bit #A0B0C4 pointing straight down, a curly dark air hose #2B1A11 hanging from one side.
Row 2:
5 Snowblower: a chunky machine seen from the front three-quarter: a blue front housing #80A0E6 with a steel spiral auger #A0B0C4 inside its open mouth, a gold-yellow engine box #FFCE43 on top with a small dark cap #2B1A11, a gold-yellow chute #FFCE43 sticking straight up, a red lever #D6392B at the back.
6 Heat gun: a chunky toy blaster lying diagonally with its barrel pointing to the top-right: a thick blue barrel #80A0E6 with a ribbed steel coil #A0B0C4 around its front, a gold-yellow nozzle ring #FFCE43, a red fuel tank #D6392B with gold bands #FFCE43 and a white cap #F3F6F5 on top, a dark grip #2B1A11 underneath.
7 Winter boots: a pair of chunky warm winter boots side by side, brown leather #CD925C with darker toes and heels #80401B, thick cream fur cuffs #FFFDF5, cream laces, dark rubber soles #2B1A11, a small white speed swoosh #F3F6F5 behind them.
8 Lucky find: a bright green four-leaf clover #5BB830 with lighter veins #96DC6A and a short stem, a small shiny golden snow nugget #FFC328 with a cream sparkle #FFFDF5 beside its stem.
Readable at small phone size, no extra objects, no watermark. Colours only from: #FFCE43 #C28E49 #80A0E6 #A0B0C4 #F3F6F5 #D6392B #2B1A11 #CD925C #80401B #FFFDF5 #5BB830 #96DC6A #FFC328.

## Референсы

- `art/ui/hotbar/hotbar-icons-sheet.png` — style reference.
- `art/refs/weapons/weapons-3d-lineup.png` — style reference.

## Нарезка и проверка

- Попыток: 1. Лист разрезан на восемь значков: оружие стоек в `art/ui/weapons/` — weapon-ice-axe (`IceAxe`), weapon-big-spoon (`SnowSpoon`), weapon-big-shovel (`SnowShovel`), weapon-jackhammer (`Jackhammer`), weapon-snowblower (`AugerSnowblower`), weapon-heat-gun (`ThermalGun`); строки GENERAL Мастерской в `art/ui/upgrades/` — upgrade-winter-boots (`WalkSpeed`), upgrade-lucky-finds (`Luck`). Нарезка — сетка 4×2, в клетке все куски по альфе не меньше 2 % самого большого, квадрат с полем 12 px, альфа ниже 40 обнулена, цвет прозрачных пикселей — контур #2B1A11, 256×256; альфа 250–254 поднята до 255.
- `art/refs/weapons/weapons-3d-lineup.png` — вырезки кадров 3D-оружия от первого лица (карточка `ded8c5`, 17.11.2026): по нему форма и цветовые зоны оружия.
- Проверено: в теле значка альфа 255, в углу 0; все восемь читаются в 56 px на доске #C28E49 и тёмном дереве #80401B.
- В Roblox не загружены: загрузка — только со слова владельца, id вписывается в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau` (`art/import.md`, карточка `701948`).
- Решение владельца 17.11.2026: лист утверждён (карточка `701948`).
