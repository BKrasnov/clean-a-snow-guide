# Уборка снега «как сейчас»: кадры, время, нагрузка

Карточка `d53b16`, шаг 1 «Разбор сейчас». Кадры живые: Play в Studio, снимок окна без паузы. Это опорные кадры «до»; кадры «после» снимаются тем же сценарием на новом коде.

## Как снято

- **Код.** Коммит `cf859209` (HEAD 15.11.2026). В рабочей папке во время съёмки был изменён чужой `src/ServerScriptService/CleanSnow/MapSnowService.luau`: карточка `a43c15`, другой чат, срез снега машиной и доля груза. Ручные инструменты эта правка не меняет. Раннер вписывал файл в окно каждый раз, когда тот менялся. `src/` в этой работе не менялся.
- **Окно.** Studio `06ce5619-a317-4492-81cb-54477c997bb9` (окно чата, копия `place/NaLovi.rbxl` со скриптами из `src`). Экран игры 1202×536, снимок 1503×670. Режим Dev, свежий забег соло (очередь `Station01`), зона 1 Frostwood, снег Powder.
- **Стойка.** Игрок стоит в свежем участке, в 3 стадах перед его серединой, ногами на земле. Глаза примерно на 0,84 стада над снегом. Камера смотрит на верх снега в 2 стадах за серединой, со стороны от золотой обводки урока. Молотов бросается с 14 стадов. Участки выбирает сценарий: свежие, глубина больше 0,8, открытая зона, без редкого снега, все 4 соседа тоже такие. Участок `-13,257` исключён: там кусок с 1/3 HP на свежем участке.
- **Режимы.** «High» — качество графики High. «Low» — качество Low. «Меньше движения» — High с настройкой «меньше движения» (reduced motion).
- **Часы в кадре.** Строка сверху слева: `clk` — секунды от нажатия кнопки мыши, `fx` — от первого кадра, где появились детали эффекта (`SnowBreakFlash`/`SnowBreakBurst`), `up` — от отпускания. В таблицах ниже время прочитано с этой строки. У Big Shovel, Jackhammer и Auger вспышка идёт в кадре клика, поэтому их время — `clk`.
- **Фазы.** «Вспышка» снимается около 0,05–0,2 с после начала эффекта, «разлёт» около 0,25–0,5 с, «затухание» около 0,7–1,1 с, «после конца» около 1,3–1,6 с. Кадр, который не попал в фазу, переснят на новом участке.

## Как переснять «после»

```
node tools/studio-scenarios/_gen-snow-removal-frames.mjs
npm run play -- snow-removal-frames-spoon
npm run play -- snow-removal-frames-shovels
npm run play -- snow-removal-frames-vacuum
npm run play -- snow-removal-frames-molotov
npm run play -- snow-removal-frames-weapons
npm run play -- snow-removal-frames-retake
```

- Генератор пишет 6 сценариев: ложка (150 шагов), лопаты (108), пылесос (59), Молотов (67), стационарное оружие (54), пересъёмка зачистки ложкой (49). `retake` снимает зачистку ложкой High ещё раз на участках №13 и №14 списка.
- Кадры появляются в `build/studio-play/snow-removal-frames-<способ>-<время>/`, имена у них те же, что в таблицах ниже. Папка `build/` не коммитится, поэтому полные кадры живут только локально. Уменьшенные копии хранят листы.
- В `output.txt` прогона смотреть строки `[cas]`:
  - `CASLOAD` — пик деталей эффекта;
  - `CASOBJ` — число объектов до и после серии;
  - `CASAFTER` — сколько снега осталось;
  - `aim … pitch … eye … over the snow` — как стояла камера. Норма: `eye` 0,84 у свежего снега, 2,2 после одного слоя, 3,5 после двух.
  - `the snow at the aim answered the raycast after …` — ожидание снега после телепорта.
- Окно Studio чата не открывать заново. Раннер сам ставит Play и Stop.

## Листы

| Лист | Кадров | Откуда кадры |
|---|---|---|
| `sheet-spoon.jpg` | 22 | один прогон `spoon-20261115-173747`, текущий сценарий |
| `sheet-shovels.jpg` | 17 | Starter Shovel — `shovels-20261115-174047` (текущий сценарий). Big Shovel — `shovels-20261115-165551`: в ранней версии сценария её кадры отсчитывались от начала эффекта, у текущей версии в 174047 затухание пришло поздно (1,23 с) |
| `sheet-vacuum.jpg` | 16 | 3 ряда — `vacuum-20261115-174328` (текущий сценарий); последний ряд — ранний `vacuum-20261115-165036`, камера на 40° вниз |
| `sheet-molotov.jpg` | 13 | один прогон `molotov-20261115-175214`, текущий сценарий |
| `sheet-weapons.jpg` | 3 | один прогон `weapons-20261115-173445`, текущий сценарий |

Все 6 сценариев в текущей версии прошли целиком: `spoon` 173747, `shovels` 174047, `vacuum` 174328, `molotov` 175214, `weapons` 173445, `retake` 173629. Время в названиях прогонов — по часам раннера.

## Кадры

### spoon: `art/vfx/snow-removal/now/sheet-spoon.jpg`

| # | Кадр (абсолютный путь) | Событие и фаза | Качество | Меньше движения | Время по часам кадра | Прогон |
|---|---|---|---|---|---|---|
| 1 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-layer-early-0-before.jpg` | Spoon layer: before | High | нет | before the strike (3/3 HP) | spoon-20261115-173747 |
| 2 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-layer-early-1-flash.jpg` | Spoon layer: flash | High | нет | clk 0.27 s, fx 0.05 s | spoon-20261115-173747 |
| 3 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-layer-late-2-spread.jpg` | Spoon layer: spread | High | нет | clk 0.47 s, fx 0.23 s | spoon-20261115-173747 |
| 4 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-layer-early-3-fade.jpg` | Spoon layer: fade | High | нет | clk 0.92 s, fx 0.69 s | spoon-20261115-173747 |
| 5 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-layer-late-4-after.jpg` | Spoon layer: after the end | High | нет | clk 1.59 s, fx 1.36 s | spoon-20261115-173747 |
| 6 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-clear-early-0-before.jpg` | Spoon clear: before | High | нет | before (patch at 1/3 HP) | spoon-20261115-173747 |
| 7 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-clear-early-1-flash.jpg` | Spoon clear: flash | High | нет | clk 0.26 s, fx 0.02 s | spoon-20261115-173747 |
| 8 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-clear-late-2-spread.jpg` | Spoon clear: spread | High | нет | clk 0.48 s, fx 0.25 s | spoon-20261115-173747 |
| 9 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-clear-early-3-fade.jpg` | Spoon clear: fade | High | нет | clk 0.93 s, fx 0.69 s | spoon-20261115-173747 |
| 10 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-high-clear-late-4-after.jpg` | Spoon clear: after the end | High | нет | clk 1.60 s, fx 1.37 s | spoon-20261115-173747 |
| 11 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-low-layer-mid-2-spread.jpg` | Spoon layer: spread | Low | нет | clk 0.47 s, fx 0.22 s | spoon-20261115-173747 |
| 12 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-low-layer-mid-3-fade.jpg` | Spoon layer: fade | Low | нет | clk 1.40 s, fx 1.15 s | spoon-20261115-173747 |
| 13 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-low-clear-mid-2-spread.jpg` | Spoon clear: spread | Low | нет | clk 0.50 s, fx 0.25 s | spoon-20261115-173747 |
| 14 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-low-clear-mid-3-fade.jpg` | Spoon clear: fade | Low | нет | clk 1.07 s, fx 0.82 s | spoon-20261115-173747 |
| 15 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-calm-layer-early-1-flash.jpg` | Spoon layer: flash | High | да | clk 0.29 s, fx 0.05 s | spoon-20261115-173747 |
| 16 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-calm-layer-late-2-spread.jpg` | Spoon layer: spread | High | да | clk 0.46 s, fx 0.21 s | spoon-20261115-173747 |
| 17 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-calm-layer-early-3-fade.jpg` | Spoon layer: fade | High | да | clk 0.98 s, fx 0.74 s | spoon-20261115-173747 |
| 18 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-calm-layer-late-4-after.jpg` | Spoon layer: after the end | High | да | clk 1.61 s, fx 1.36 s | spoon-20261115-173747 |
| 19 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-calm-clear-early-1-flash.jpg` | Spoon clear: flash | High | да | clk 0.26 s, fx 0.05 s | spoon-20261115-173747 |
| 20 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-calm-clear-late-2-spread.jpg` | Spoon clear: spread | High | да | clk 0.48 s, fx 0.27 s | spoon-20261115-173747 |
| 21 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-calm-clear-early-3-fade.jpg` | Spoon clear: fade | High | да | clk 1.08 s, fx 0.87 s | spoon-20261115-173747 |
| 22 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-spoon-20261115-173747\spoon-calm-clear-late-4-after.jpg` | Spoon clear: after the end | High | да | clk 1.56 s, fx 1.35 s | spoon-20261115-173747 |

### shovels: `art/vfx/snow-removal/now/sheet-shovels.jpg`

| # | Кадр (абсолютный путь) | Событие и фаза | Качество | Меньше движения | Время по часам кадра | Прогон |
|---|---|---|---|---|---|---|
| 1 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-layer-early-0-before.jpg` | Starter 2 layers: before | High | нет | before the strike (3/3 HP) | shovels-20261115-174047 |
| 2 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-layer-early-1-flash.jpg` | Starter 2 layers: flash | High | нет | clk 0.25 s, fx 0.09 s | shovels-20261115-174047 |
| 3 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-layer-late-2-spread.jpg` | Starter 2 layers: spread | High | нет | clk 0.49 s, fx 0.33 s | shovels-20261115-174047 |
| 4 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-layer-early-3-fade.jpg` | Starter 2 layers: fade | High | нет | clk 0.97 s, fx 0.81 s | shovels-20261115-174047 |
| 5 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-layer-late-4-after.jpg` | Starter 2 layers: after the end | High | нет | clk 1.49 s, fx 1.34 s | shovels-20261115-174047 |
| 6 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-clear-early-0-before.jpg` | Starter clear: before | High | нет | before (patch at 1/3 HP) | shovels-20261115-174047 |
| 7 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-clear-early-1-flash.jpg` | Starter clear: flash | High | нет | clk 0.31 s, fx 0.16 s | shovels-20261115-174047 |
| 8 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-clear-late-2-spread.jpg` | Starter clear: spread | High | нет | clk 0.50 s, fx 0.35 s | shovels-20261115-174047 |
| 9 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-clear-early-3-fade.jpg` | Starter clear: fade | High | нет | clk 0.85 s, fx 0.70 s | shovels-20261115-174047 |
| 10 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-174047\starter-high-clear-late-4-after.jpg` | Starter clear: after the end | High | нет | clk 1.49 s, fx 1.34 s | shovels-20261115-174047 |
| 11 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-165551\bigshovel-high-clear-early-0-before.jpg` | Big Shovel x3: before | High | нет | before the strike (run 16:55) | shovels-20261115-165551 |
| 12 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-165551\bigshovel-high-clear-early-1-flash.jpg` | Big Shovel x3: flash | High | нет | clk 0.27 s, flash from the click (16:55) | shovels-20261115-165551 |
| 13 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-165551\bigshovel-high-clear-late-2-spread.jpg` | Big Shovel x3: spread | High | нет | clk 0.49 s (run 16:55) | shovels-20261115-165551 |
| 14 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-165551\bigshovel-high-clear-early-3-fade.jpg` | Big Shovel x3: fade | High | нет | clk 0.93 s (run 16:55) | shovels-20261115-165551 |
| 15 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-165551\bigshovel-high-clear-late-4-after.jpg` | Big Shovel x3: after the end | High | нет | clk 1.49 s (run 16:55) | shovels-20261115-165551 |
| 16 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-165551\bigshovel-low-clear-mid-2-spread.jpg` | Big Shovel x3: spread | Low | нет | clk 0.38 s (run 16:55) | shovels-20261115-165551 |
| 17 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-shovels-20261115-165551\bigshovel-low-clear-mid-3-fade.jpg` | Big Shovel x3: fade | Low | нет | clk 0.95 s (run 16:55) | shovels-20261115-165551 |

### vacuum: `art/vfx/snow-removal/now/sheet-vacuum.jpg`

| # | Кадр (абсолютный путь) | Событие и фаза | Качество | Меньше движения | Время по часам кадра | Прогон |
|---|---|---|---|---|---|---|
| 1 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-high-0-before.jpg` | Vacuum: before | High | нет | before the press | vacuum-20261115-174328 |
| 2 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-high-hold-0_3s.jpg` | Vacuum: hold 0.3 s | High | нет | held 0.44 s, fx 0.23 s | vacuum-20261115-174328 |
| 3 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-high-hold-1_0s.jpg` | Vacuum: hold 1.0 s | High | нет | held 1.27 s, fx 1.07 s | vacuum-20261115-174328 |
| 4 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-high-hold-2_0s.jpg` | Vacuum: hold 2.0 s | High | нет | held 2.01 s, fx 1.81 s | vacuum-20261115-174328 |
| 5 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-high-up-0_3s.jpg` | Vacuum: 0.3 s after release | High | нет | 0.13 s after release | vacuum-20261115-174328 |
| 6 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-high-up-1_5s.jpg` | Vacuum: 1.5 s after release | High | нет | 1.53 s after release | vacuum-20261115-174328 |
| 7 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-low-hold-1_0s.jpg` | Vacuum: hold 1.0 s | Low | нет | held 1.20 s, fx 0.99 s | vacuum-20261115-174328 |
| 8 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-low-up-1_5s.jpg` | Vacuum: 1.5 s after release | Low | нет | 1.35 s after release | vacuum-20261115-174328 |
| 9 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-calm-hold-1_0s.jpg` | Vacuum: hold 1.0 s | High | да | held 1.17 s, fx 1.03 s | vacuum-20261115-174328 |
| 10 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-174328\vacuum-calm-up-1_5s.jpg` | Vacuum: 1.5 s after release | High | да | 1.35 s after release | vacuum-20261115-174328 |
| 11 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-165036\vacuum-high-0-before.jpg` | Vacuum: before | High | нет | before the press | vacuum-20261115-165036 |
| 12 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-165036\vacuum-high-hold-0_3s.jpg` | Vacuum: hold 0.3 s | High | нет | held 0.44 s, fx 0.31 s | vacuum-20261115-165036 |
| 13 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-165036\vacuum-high-hold-1_0s.jpg` | Vacuum: hold 1.0 s | High | нет | held 1.00 s, fx 0.87 s | vacuum-20261115-165036 |
| 14 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-165036\vacuum-high-hold-2_0s.jpg` | Vacuum: hold 2.0 s | High | нет | held 1.99 s, fx 1.86 s | vacuum-20261115-165036 |
| 15 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-165036\vacuum-high-up-0_3s.jpg` | Vacuum: 0.3 s after release | High | нет | 0.12 s after release (held 2.47 s) | vacuum-20261115-165036 |
| 16 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-vacuum-20261115-165036\vacuum-high-up-1_5s.jpg` | Vacuum: 1.5 s after release | High | нет | 1.48 s after release | vacuum-20261115-165036 |

### molotov: `art/vfx/snow-removal/now/sheet-molotov.jpg`

| # | Кадр (абсолютный путь) | Событие и фаза | Качество | Меньше движения | Время по часам кадра | Прогон |
|---|---|---|---|---|---|---|
| 1 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-high-0-before.jpg` | Molotov: before | High | нет | before the throw | molotov-20261115-175214 |
| 2 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-high-1-flight.jpg` | Molotov: bottle in the air | High | нет | throw +0.12 s, no fire yet | molotov-20261115-175214 |
| 3 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-high-2-fire-0_1s.jpg` | Molotov: fire touches the snow | High | нет | fire 0.22 s (throw +0.95 s) | molotov-20261115-175214 |
| 4 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-high-3-fire-0_4s.jpg` | Molotov: fire spreads | High | нет | fire 0.82 s | molotov-20261115-175214 |
| 5 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-high-4-fire-1_2s.jpg` | Molotov: burning (tick) | High | нет | fire 1.42 s | molotov-20261115-175214 |
| 6 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-high-5-fire-2_5s.jpg` | Molotov: burning late | High | нет | fire 2.49 s | molotov-20261115-175214 |
| 7 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-high-6-fire-4_5s.jpg` | Molotov: after the end | High | нет | fire 4.49 s | molotov-20261115-175214 |
| 8 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-low-2-fire-0_1s.jpg` | Molotov: fire touches the snow | Low | нет | fire 0.13 s | molotov-20261115-175214 |
| 9 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-low-3-fire-0_4s.jpg` | Molotov: fire spreads | Low | нет | fire 0.85 s | molotov-20261115-175214 |
| 10 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-low-4-fire-4_5s.jpg` | Molotov: after the end | Low | нет | fire 4.55 s | molotov-20261115-175214 |
| 11 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-calm-2-fire-0_1s.jpg` | Molotov: fire touches the snow | High | да | fire 0.15 s | molotov-20261115-175214 |
| 12 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-calm-3-fire-0_4s.jpg` | Molotov: fire spreads | High | да | fire 1.00 s | molotov-20261115-175214 |
| 13 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-molotov-20261115-175214\molotov-calm-4-fire-4_5s.jpg` | Molotov: after the end | High | да | fire 4.53 s | molotov-20261115-175214 |

### weapons: `art/vfx/snow-removal/now/sheet-weapons.jpg`

| # | Кадр (абсолютный путь) | Событие и фаза | Качество | Меньше движения | Время по часам кадра | Прогон |
|---|---|---|---|---|---|---|
| 1 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-weapons-20261115-173445\jackhammer-high-work-1_0s.jpg` | Jackhammer: 1 s of work | High | нет | held 1.10 s, fx 0.78 s | weapons-20261115-173445 |
| 2 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-weapons-20261115-173445\thermalgun-high-work-1_0s.jpg` | ThermalGun: 1 s of work | High | нет | held 1.13 s, fx 0.86 s | weapons-20261115-173445 |
| 3 | `C:\Users\User\development\slime_studio\games\clean-a-snow\build\studio-play\snow-removal-frames-weapons-20261115-173445\augersnowblower-high-work-1_0s.jpg` | AugerSnowblower: 1 s of work | High | нет | held 1.12 s, fx 0.85 s | weapons-20261115-173445 |

## Нагрузка

Пробник `CASLOAD` в каждом кадре рендера считает:

- видимые детали эффекта в папках `SnowBreakFlash`, `SnowBreakBurst`, `SnowIslandRing` и `WeaponFx`;
- включённые излучатели частиц (потоковые);
- снежинки-билборды;
- лучи (Beam);
- куски золотой вспышки на экране (`SnowIslandFx`).

В таблице — пик за событие. «Уже при клике» — сколько деталей было видно ещё в кадре нажатия. Лучей (Beam) нет нигде.

| Способ и событие | Режим | Пик деталей | Из них | Уже при клике | Излучатели | Снежинки | Экранная вспышка | Прогон |
|---|---|---|---|---|---|---|---|---|
| Ложка, слой | High | 254 | Flash 240, Burst 14 | 0 | 0 | 5–6 | 0 | spoon-173747 |
| Ложка, зачистка | High | 184–264 | Flash 144–224, Ring 40 | 0 | 0 | 9–10 | 11 | spoon-173747 |
| Ложка, слой | Low | 264 | Flash 264 | 0 | 0 | 4 | 0 | spoon-173747 |
| Ложка, зачистка | Low | 360 | Flash 320, Ring 40 | 0 | 0 | 6 | 11 | spoon-173747 |
| Ложка, слой | меньше движения | 80–116 | Flash | 0 | 0 | 1–2 | 0 | spoon-173747 |
| Ложка, зачистка | меньше движения | 96–160 | Flash | 0 | 0 | 1–2 | 0 | spoon-173747 |
| Starter Shovel, 2 слоя | High | 254 | Flash 240, Burst 14 | 0 | 0 | 5–6 | 0 | shovels-174047 |
| Starter Shovel, зачистка | High | 184–284 | Flash 144–224, Burst 0–20, Ring 40 | 0 | 0 | 9–10 | 11 | shovels-174047 |
| Big Shovel, 3 участка | High | 304–360 | Flash 264–320, Ring 40 | 264–320 | 0 | 19 | 11 | shovels-165551, 174047 |
| Big Shovel, 3 участка | Low | 200–208 | Flash 160–168, Ring 40 | 160–168 | 0 | 11 | 11 | shovels-165551, 174047 |
| Пылесос, камера по HUD | High | 144 | Flash 144 | 0 | 0 | 8 | 0 | vacuum-174328 |
| Пылесос, камера на 40° вниз | High | 194 | Burst 10, Flash 144, Ring 40 | 0 | 0 | 13 | 11 | vacuum-165036 |
| Пылесос | Low | 336 | Flash 336 | 0 | 0 | 5 | 0 | vacuum-174328 |
| Пылесос | меньше движения | 164 | Flash 164 | 0 | 0 | 1 | 0 | vacuum-174328 |
| Молотов | High | 100 | Burst 60, Ring 40 | 0 | 2 | 27 | 11 | molotov-175214 |
| Молотов | Low | 70 | Burst 30, Ring 40 | 0 | 2 | 15 | 11 | molotov-175214 |
| Молотов | меньше движения | 96 | Flash 96 | 0 | 2 | 3 | 0 | molotov-175214 |
| Jackhammer | High | 306 | Flash 272, Burst 34 | 240 | 0 | 18 | 0 | weapons-173445 |
| ThermalGun | High | 280 | Flash 240, Ring 40 | 0 | 0 | 14 | 11 | weapons-173445 |
| AugerSnowblower | High | 184 | Flash 144, Ring 40 | 144 | 0 | 19 | 11 | weapons-173445 |

Пробник `CASOBJ` считает объекты до и после каждой серии:

- `MapSnowFeedback` — всегда 1203 (плюс 94–95 объектов подсказки, HUD и машины). Пул эффекта не растёт.
- `CleanSnowLocalEffects` и `WeaponFx` после каждой серии — 0.
- После серии Молотова остаются 5 объектов огня и бутылки: последний огонь («меньше движения») ещё горит.
- Всего объектов в `workspace` за серию прибавляется 480–820: например, у ложки с 75365 до 76186, у Молотова с 75480 до 76202. Пул эффекта при этом постоянный, так что, вероятно, это геометрия ям в снегу. Точно не проверено.

Что видно по числам:

- **Low не легче High по деталям.** У ложки Low даёт 264–360 деталей против 184–264 на High, у пылесоса 336 против 144. Кольцо и экранная вспышка на Low остаются.
- **Легче только «меньше движения».** Остаётся одна вспышка-копия снега (80–164 детали) и 1–3 снежинки. Кубиков, кольца и золотой вспышки нет.
- **Big Shovel, Jackhammer и Auger показывают 144–320 деталей вспышки уже в кадре клика.** Размаха у них нет.
- **Потоковые излучатели есть только у Молотова** — 2, это огонь.

## Ограничения и пробелы

- **Разовые выбросы не посчитаны.** Частицы `ParticleEmitter:Emit` Roblox не отдаёт, их число неизвестно.
- **Кадр приходит с задержкой.** Он идёт через 0,2–0,5 с после шага сценария, а время фаз гуляет на ±0,1–0,3 с между прогонами. Фазу надо читать по часам в кадре. Пример: затухание Big Shovel в прогоне 174047 пришло на 1,23 с, поэтому на листе Big Shovel из прогона 165551.
- **Вспышку стационарного оружия раньше ~0,25 с не снять.** У Big Shovel, Jackhammer и Auger она начинается в кадре клика.
- **Часы Big Shovel могут начаться заново посреди удара** (второе нажатие во входе). В 174047 кадр «разлёт Low» показывает `clk 0.14`, хотя по картинке это разлёт.
- **Кадр Молотова «огонь растекается» (цель 0,4 с) приходит на 0,8–1,0 с.**
- **Пылесос и ThermalGun смотрят на горизонт.**
  - HUD показывает их участок в основном при камере, поднятой на 6–9°. Конус тогда тянет дальние участки, и кадр смотрит на горизонт (Low и «меньше движения» у пылесоса, ThermalGun).
  - Пробовали камеру на 45° вниз (прогон 175040): снег не взялся на 2 участках из 3. Пробовали только ровную камеру (175519): кончился список участков. Обе попытки в сценарий не вошли.
  - Последний ряд листа пылесоса — ранний прогон 165036. Там камера случайно смотрела на 40° вниз, и видно, как свой участок становится зелёным.
- **После телепорта снег 2–7 с не отвечает на луч `MapSnowRaycast`.** Телепорт бывает на старте забега, после магазина и после лотка переработчика. До правки сценария камера в таких местах смотрела на 43° вниз, в толщу снега, а запись `eye 4.84 over the snow` на деле означала «над землёй». Теперь сценарий ждёт ответа (строка `answered the raycast`). Таких кадров на листах нет, кроме последнего ряда пылесоса — он оставлен намеренно.
- **После лотка переработчика камера иногда стоит выше нормы.** Глаза держатся примерно на 1,2 стада выше 15 с и дольше: ложка Low, Auger. В Output это видно по строке `eyes high … waited 15 s`, затем `eye 2.0 over the snow`. Кадры годные, но камера чуть выше.
- **`CASAFTER` может мерить соседний кусок.** Он смотрит снег в 2 стадах за серединой участка, и на участке из нескольких кусков попадает на соседний: у слоёв встречаются 2,50 и 1,25 стада.
- **На экране всегда есть посторонние детали:**
  - задание урока внизу по центру (`BREAK THE SNOW`, `CUT AROUND THE ISLAND`, `BUY THE STARTER SHOVEL`);
  - надписи редкого снега вдали;
  - модель инструмента в руках;
  - у Молотова и Auger — плашка `BUCKET FULL! GO SELL!`: одно действие наполняет ведро на 15.
- **Участок `-13,257` исключён.** На свежем участке там кусок с 1/3 HP, и зачистка ложкой снимала слой.
- **Машины не снимались** по заданию.

## Что видно сейчас (коротко)

- **Ложка, слой.** Бледно-сиреневые кубики с фаской взлетают на 2–4 стада. Ещё видны белые комки, 2–6 снежинок, `+1` и пустая полоска HP над снегом. Слой опускается, под ним сиреневый и бирюзовый нижний слой. Через 1,3 с ничего не остаётся. Ложка закрывает правую середину кадра.
- **Зачистка (ложка, Starter, пылесос на 40° вниз).** Через 0,05 с весь экран золотисто-жёлтый с лучами. На земле белая дуга кольца, летят голубые кубики и снежинки, открывается зелёная земля. После — чистая яма.
- **«Меньше движения».** Мягкая вспышка снега и 1–2 снежинки. Кольца и золота нет.
- **Starter Shovel.** Снимает 2 слоя (`+2`). Белая вспышка-копия может обнять камеру, когда игрок стоит в участке. Красное лезвие закрывает низ середины кадра.
- **Big Shovel.** Эффект с первого кадра:
  - большие белые клубы и крупные голубые кубики высоко в воздухе;
  - белое кольцо вокруг 3 участков;
  - очень крупные снежинки у камеры;
  - `+3`, `+6`, `+9`.
- **Пылесос.** Струи всасывания не видно. При камере на 40° вниз к 1 с экран бледно-белый со слабыми золотыми лучами, к 2 с участок зелёный. При камере по HUD эффект далеко у горизонта. Модель занимает правую треть.
- **Молотов.**
  - Бутылка в воздухе.
  - От касания до 2,5 с горящая земля лимонно-жёлтая. На Low видны оранжевые полосы, под ними светлая дымка, слабые оранжевые кубики, кольцо, `+15`.
  - Под 1,4–2,5 с земля жёлтая, оранжевая полоса перезарядки внизу.
  - К 4,5 с видна зелёная земля, а на Low — коричневая полоса.
- **Jackhammer.** Голубые кубики, `+1`, отбойник в центре кадра.
- **ThermalGun.** Эффект далеко у горизонта, пушка закрывает правую половину кадра.
- **AugerSnowblower.** Впереди зелёная расчищенная полоса и мелкие клубы.
