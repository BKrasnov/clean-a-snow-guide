# Что загрузить в Roblox

Картинки, которые уже готовы и ждут загрузки. Решение владельца 10.11.2026: грузим позже, когда владельца добавят в плейс. После загрузки вписать id в код, проверить кадром в игре и убрать строку отсюда.

| Картинка | Что это | Куда вписать id | Что будет до загрузки |
| --- | --- | --- | --- |
| `art/vfx/gold-ring-star-256.png` (исходник `art/vfx/gold-ring-star.png`, карточка `cb9f50`) | Белая четырёхлучевая звезда — звёздочки золотого кольца, когда уходит отрезанный кусок снега | `SPARKLE_TEXTURE` в `src/ReplicatedStorage/SnowSweep/PieceVanishFx.luau`: `"rbxassetid://<id>"` | Встроенный спрайт Roblox `sparkles_main.dds` (мягкий многолучевой) |
| `art/vfx/snowflake-256.png` (исходник `art/vfx/snowflake.png`) | Снежинка, частица слома снега (баг `BUG-20261110-004`, карточка `9d8916`) | `SnowFeedbackConfig.SnowflakeTexture` в `src/ReplicatedStorage/SnowCleaningDemo/SnowFeedbackConfig.luau`: `"rbxassetid://<id>"` | Снежинки уже есть: их рисует код (`SnowSprites`, карточка 40cbaf). Загрузка не обязательна: картинку можно подставить вместо нарисованной |
| `art/ui/hotbar/hotbar-spoon-256.png` (лист `art/ui/hotbar/hotbar-icons-sheet.png`, карточка `7852ff`) | Ложка (`SnowSpoon`) | Поле `id` ключа `Tool:SnowSpoon` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau` (карточка `fbac38`): панель иконок, кнопка действия, окна покупки и Мастерская | 3D-модель предмета |
| `art/ui/hotbar/hotbar-starter-shovel-256.png` | Лопата Starter Shovel | Та же таблица, ключ `Tool:StarterShovel` | 3D-модель предмета |
| `art/ui/hotbar/hotbar-steel-shovel-256.png` | Лопата Steel Shovel | Та же таблица, ключ `Tool:SteelShovel` | 3D-модель предмета |
| `art/ui/hotbar/hotbar-snow-pusher-256.png` | Snow Pusher | Та же таблица, ключ `Tool:SnowPusher` | 3D-модель предмета |
| `art/ui/hotbar/hotbar-ice-shovel-256.png` | Ice Shovel | Та же таблица, ключ `Tool:IceShovel` | 3D-модель предмета |
| `art/ui/hotbar/hotbar-snow-vacuum-256.png` | Пылесос Snow Vacuum (инструмент) | Та же таблица, ключ `Tool:SnowVacuum` | 3D-модель предмета |
| `art/ui/hotbar/hotbar-turbo-vacuum-256.png` | Turbo Vacuum (оружие `SnowVacuum`) | Та же таблица, ключ `Weapon:SnowVacuum` | 3D-модель предмета |
| `art/ui/hotbar/hotbar-molotov-256.png` | Молотов | Та же таблица, ключ `Weapon:Molotov` | 3D-модель предмета |
| `art/ui/hotbar/hotbar-donate-lock-256.png` | Замок донатной иконки | Та же таблица, ключ `Donate` | 3D-замок |
| `art/ui/buckets/bucket-starter-256.png` (лист `art/ui/buckets/buckets-icons-sheet.png`, карточка `907897`) | Ведро Starter Bucket (`StarterBag`) | Поле `id` ключа `Bucket:StarterBag` в общей таблице `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau` (карточка `fbac38`): счётчик снега внизу слева, окно покупки ведра | 3D-ведро `BucketArt` |
| `art/ui/buckets/bucket-trail-256.png` | Ведро Trail Bucket (`TrailBag`) | Та же таблица, ключ `Bucket:TrailBag` | 3D-ведро `BucketArt` |
| `art/ui/buckets/bucket-expedition-256.png` | Ведро Expedition Bucket (`ExpeditionBag`) | Та же таблица, ключ `Bucket:ExpeditionBag` | 3D-ведро `BucketArt` |
| `art/ui/buckets/bucket-hauler-256.png` | Ведро Hauler Bucket (`HaulerBag`) | Та же таблица, ключ `Bucket:HaulerBag` | 3D-ведро `BucketArt` |
| `art/ui/buckets/bucket-glacier-256.png` | Ведро Glacier Bucket (`GlacierBag`) | Та же таблица, ключ `Bucket:GlacierBag` | 3D-ведро `BucketArt` |
| `art/ui/buckets/snow-block-256.png` | Блок снега | Та же таблица, ключ `Snow:Block`: кнопка INDEX и кнопка переноса снега, полоска переработчика, снег в окнах Snow Index, переработки и итогов | 3D-кубик снега |
| `art/ui/upgrades/snow-block-golden-256.png` (лист `art/ui/upgrades/upgrades-icons-sheet.png`, карточка `907897`) | Золотой блок снега | Та же таблица, ключ `Snow:Golden`: карточка Golden в Snow Index | 3D-кубик, перекрашенный в золото |
| `art/ui/upgrades/processor-256.png` | Переработчик, улучшение Process (`ProcessorSpeed`) | Та же таблица, ключ `Upgrade:ProcessorSpeed`: улучшение Process в окне улучшений и Мастерской, плитка в окне SNOW PROCESSOR (карточка `4875c7`) | 3D-машина из старой карточки улучшений |
| `art/ui/pets/pet-snow-fox-256.png` (лист `art/ui/pets/pets-icons-sheet.png`, карточка `907897`) | Питомец песец (`SnowFox`) | Та же таблица, ключ `Pet:SnowFox` (карточка `657ae9`): карточка песца в окне Pets | 3D-модель питомца в окне Pets |
| `art/ui/pets/pet-owl-256.png` | Питомец полярная сова (`Owl`) | Та же таблица, ключ `Pet:Owl`: карточка совы в окне Pets | 3D-модель (голубая сова) |
| `art/ui/pets/pet-snow-hare-256.png` | Питомец заяц-беляк (`SnowHare`) | Та же таблица, ключ `Pet:SnowHare`: карточка зайца в окне Pets | 3D-модель питомца в окне Pets |
| `art/ui/hockey/robot-head-256.png` (исходник `art/ui/hockey/robot-head.png`, карточка `657ae9`) | Голова робота на пустом месте хоккейной панели составов | Та же таблица, ключ `Hockey:Robot`: панель составов над табло хоккея (`HockeyTeamsPanel.luau`) | 3D-голова робота |
| `art/ui/hockey/hockey-crown-256.png` (карточка `73e79b`) | Корона победителя | Та же таблица, ключ `Hockey:Crown`: корона над лентой RED WINS!/BLUE WINS! в конце матча (`HockeyMatchView.luau`) | Корона скрыта, остаётся лента со словами |
| `art/ui/hockey/hockey-stick-256.png` (карточка `73e79b`) | Клюшка на золотой кнопке | Та же таблица, ключ `Hockey:Stick`: золотая кнопка удара в матче (`HockeyMatchView.luau`) | Клюшка, нарисованная кодом из `Frame` |
| `art/ui/hud/hud-coin-256.png` (лист `art/ui/hud/hud-icons-sheet.png`, карточка `701948`) | Монета | Та же таблица, ключ `Hud:Coin`: счётчик монет, окна итогов, переработки и покупки, цены и баланс Мастерской, окно переработчика, хоккейный счёт | 3D-монета |
| `art/ui/hud/hud-gem-256.png` | Кристалл (гемы) | Та же таблица, ключ `Hud:Gem`: счётчик гемов | 3D-кристалл |
| `art/ui/hud/hud-clock-256.png` | Часы | Та же таблица, ключ `Hud:Clock`: таймер забега, окно итогов | 3D-часы |
| `art/ui/hud/hud-settings-256.png` | Шестерёнка | Та же таблица, ключ `Hud:Settings`: кнопка и окно настроек, окно переработки | 3D-шестерёнка |
| `art/ui/hud/hud-news-256.png` | Газета | Та же таблица, ключ `Hud:News`: кнопка и окно новостей | 3D-лист |
| `art/ui/hud/hud-stats-256.png` | Столбики | Та же таблица, ключ `Hud:Stats`: кнопка и окно статистики | 3D-столбики |
| `art/ui/hud/hud-upgrades-256.png` | Ящик со стрелкой | Та же таблица, ключ `Hud:Upgrades`: кнопка UPGR и шапка окна улучшений | 3D-ящик |
| `art/ui/hud/hud-pets-256.png` | Лапа | Та же таблица, ключ `Hud:Pets`: кнопка PETS и шапка окна Pets | 3D-лапа |
| `art/ui/hud/hud-lock-256.png` | Замок | Та же таблица, ключ `Hud:Lock`: окно классов (кнопка и строка Master) | 3D-замок |
| `art/ui/weapons/weapon-ice-axe-256.png` (лист `art/ui/weapons/weapons-icons-sheet.png`, карточка `701948`) | Ледоруб | Та же таблица, ключ `Weapon:IceAxe`: панель иконок внизу | 3D-модель оружия |
| `art/ui/weapons/weapon-big-spoon-256.png` | Большая ложка (оружие `SnowSpoon`) | Та же таблица, ключ `Weapon:SnowSpoon` | 3D-модель оружия |
| `art/ui/weapons/weapon-big-shovel-256.png` | Большая лопата (оружие `SnowShovel`) | Та же таблица, ключ `Weapon:SnowShovel` | 3D-модель оружия |
| `art/ui/weapons/weapon-jackhammer-256.png` | Отбойный молоток | Та же таблица, ключ `Weapon:Jackhammer` | 3D-модель оружия |
| `art/ui/weapons/weapon-snowblower-256.png` | Снегоуборщик | Та же таблица, ключ `Weapon:AugerSnowblower` | 3D-модель оружия |
| `art/ui/weapons/weapon-heat-gun-256.png` | Термопушка | Та же таблица, ключ `Weapon:ThermalGun` | 3D-модель оружия |
| `art/ui/upgrades/upgrade-winter-boots-256.png` (лист `art/ui/weapons/weapons-icons-sheet.png`) | Winter Boots (`WalkSpeed`) | Та же таблица, ключ `Upgrade:WalkSpeed`: строка GENERAL Мастерской | Картинка присланного плейса |
| `art/ui/upgrades/upgrade-lucky-finds-256.png` | Lucky Finds (`Luck`) | Та же таблица, ключ `Upgrade:Luck`: строка GENERAL Мастерской | Картинка присланного плейса |
| `art/ui/wood/wood-plaque-snow-v2.png` (лист `art/ui/wood/wood-sheet-v2.png`, карточка `f2de28`, круг 5) | Длинная деревянная плашка HUD с толстой подушкой снега на верхнем крае (9-slice) | Та же таблица, ключ `Wood:PlaqueSnow`: длинные плашки со снегом — монеты, ведро, задание, панель предметов, полоса оружия (`Shared/HudWood.luau`) | Запасной вид кодом: плашка цвета «Доска» с обводкой «Контур» и светом сверху, без снега и текстуры |
| `art/ui/wood/wood-button-snow.png` (тот же лист) | Квадратная деревянная кнопка в одну доску со снегом (9-slice) | Та же таблица, ключ `Wood:ButtonSnow`: кнопки меню, PETS/UPGR/INDEX, панель раунда | Запасной вид кодом, как у длинной плашки |
| `art/ui/wood/wood-plaque.png` | Та же плашка без снега (9-slice) | Та же таблица, ключ `Wood:Plaque`: деревянные плашки без снега | Запасной вид кодом, как у плашки со снегом |
| `art/ui/wood/wood-round.png` | Круглая деревянная кнопка со снегом | Та же таблица, ключ `Wood:Round`: круглые кнопки HUD | Запасной вид кодом: круглая плашка «Доска» без снега |
| `art/ui/wood/wood-round-gold.png` | Круглая золотая кнопка со снегом | Та же таблица, ключ `Wood:RoundGold`: подсвеченная круглая кнопка | Запасной вид кодом: круглая плашка «Золото» без снега |
| `art/ui/wood/window-board-snow.png` (лист `art/ui/wood/window-sheet.png`, карточка `6137fd`) | Большая доска окна со снегом на верхнем крае (9-slice) | Та же таблица, ключ `Wood:Window`: доска каждого окна (`Shared/WindowWood.luau`) | Запасной вид кодом: доска «Доска» с обводкой «Контур» и светом сверху, без снега |
| `art/ui/wood/window-header.png` (тот же лист) | Тёмная планка заголовка окна (9-slice) | Та же таблица, ключ `Wood:Header`: заголовки и плашки баланса окон | Запасной вид кодом: планка «Тёмное дерево» с обводкой |
| `art/ui/wood/window-card.png` (тот же лист) | Светлая вдавленная карточка (9-slice) | Та же таблица, ключ `Wood:Card`: строки и карточки окон | Запасной вид кодом: карточка «Дерево» с обводкой |
| `art/ui/wood/window-tile.png` (тот же лист) | Тёмная плитка под картинку (9-slice) | Та же таблица, ключ `Wood:Tile`: плитки картинок в строках окон | Запасной вид кодом: плитка «Тёмное дерево» с обводкой |
| `art/ui/wood/window-close.png` (лист `art/ui/wood/window-buttons-bare.png`, карточка `1cf3e9`) | Красная кнопка закрытия без снега с кремовым крестиком | Та же таблица, ключ `Wood:Close`: крестик каждого окна | Запасной вид кодом: красная кнопка без снега, крестик окна прежний |
| `art/ui/wood/button-green.png` (тот же лист) | Зелёная кнопка без снега (9-slice) | Та же таблица, ключ `Wood:Green`: главные кнопки окон, ON | Запасной вид кодом: зелёная кнопка |
| `art/ui/wood/button-red.png` (тот же лист) | Красная кнопка без снега (9-slice) | Та же таблица, ключ `Wood:Red`: NEW GAME и подтверждение в START A RUN | Запасной вид кодом: красная кнопка |
| `art/ui/wood/button-wood.png` (тот же лист) | Деревянная кнопка в одну доску без снега (9-slice) | Та же таблица, ключ `Wood:Button`: деревянные кнопки окон, OFF | Запасной вид кодом: кнопка «Доска» с обводкой |
| `art/ui/windows/settings-falling-snow-256.png` (карточка `6137fd`, часть 3 `4875c7`; промпт рядом) | Падающие снежинки | Поле `id` ключа `Window:FallingSnow` в `src/ReplicatedStorage/CleanSnow/Shared/ItemPictures.luau`: SETTINGS, строка FALLING SNOW (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/settings-sound-256.png` | Динамик со звуковыми волнами | Та же таблица, ключ `Window:Sound`: SETTINGS, строка SOUND EFFECTS (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/settings-camera-shake-256.png` | Фотоаппарат с чёрточками тряски | Та же таблица, ключ `Window:CameraShake`: SETTINGS, строка CAMERA SHAKE (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/settings-impact-words-256.png` | Снежок во вспышке удара | Та же таблица, ключ `Window:ImpactWords`: SETTINGS, строка IMPACT WORDS (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/settings-reduced-motion-256.png` | Улитка со снегом на раковине | Та же таблица, ключ `Window:ReducedMotion`: SETTINGS, строка REDUCED MOTION (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/stats-expeditions-256.png` | Флажок в сугробе | Та же таблица, ключ `Window:Expeditions`: YOUR EXPEDITION, строка EXPEDITIONS COMPLETED (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/stats-best-area-256.png` | Гора со звездой на вершине | Та же таблица, ключ `Window:BestArea`: YOUR EXPEDITION, строка BEST AREA (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/news-frostwood-256.png` | Ель со снегом | Та же таблица, ключ `Window:Frostwood`: WELCOME TO WINTER, история FROSTWOOD AWAITS (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/news-together-256.png` | Две варежки, красная и голубая | Та же таблица, ключ `Window:Together`: WELCOME TO WINTER, история BETTER TOGETHER (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/windows/news-follow-snow-256.png` | Деревянный указатель со снегом | Та же таблица, ключ `Window:FollowSnow`: WELCOME TO WINTER, история FOLLOW THE SNOW (плитка слева в строке, `WindowWood` `look.icons`) | Строка без картинки, как в части 2 |
| `art/ui/hud/hud-fire-256.png` (карточка `f2de28`) | Огонь | Та же таблица, ключ `Hud:Fire`: значок перегрева на полосе оружия | Иконка скрыта |
| `art/ui/hud/hud-bottle-256.png` (карточка `f2de28`) | Бутылка на полосе оружия | Та же таблица, ключ `Hud:Bottle`: значок ожидания Молотова на полосе оружия (лист 08) | Молотов: его картинка или 3D-модель, как старая иконка |
| `art/ui/hud/hud-truck-256.png` | Грузовик со снегом | Та же таблица, ключ `Hud:Truck`: счётчик кузова CARGO за рулём | Иконки нет: ведра на кузове тоже нет, остаются «n/N» и CARGO |
| `art/ui/hud/hud-tap-256.png` (карточка `819c27`) | Рука TAP | Та же таблица, ключ `Hud:Tap`: рука на кнопке действия, когда в руках оружие со стойки или особый предмет | Иконка скрыта, остаётся слово TAP |
| `art/ui/hud/hud-start-pad-256.png` (карточка `8a8c91`) | Площадка старта | Та же таблица, ключ `Hud:StartPad`: картинка слева на плашке первого забега в лобби | Картинка скрыта, слова сдвигаются влево |
| `art/ui/hud/hud-arrow-down-256.png` (карточка `8a8c91`) | Золотая стрелка вниз | Та же таблица, ключ `Hud:ArrowDown`: стрелка под табличкой SELL над поддоном | Стрелка скрыта, остаётся табличка SELL |
| `art/ui/hud/hud-chest-256.png` | Сундук с галочкой | Та же таблица, ключ `Hud:Chest`: плашка YOUR PROGRESS SAVES | Иконка скрыта, остаётся плашка с надписью |
| `art/ui/buckets/bucket-starter-snow-256.png` (лист `art/ui/buckets/buckets-snow-sheet.png`, карточка `f2de28`, круг 6) | Ведро Starter Bucket со снегом | Та же таблица, ключ `BucketSnow:StarterBag`: счётчик ведра, когда в ведре есть снег (`ItemPictures.bucketKey`) | 3D-ведро `BucketArt`, как у пустого |
| `art/ui/buckets/bucket-trail-snow-256.png` | Ведро Trail Bucket со снегом | Та же таблица, ключ `BucketSnow:TrailBag` | 3D-ведро `BucketArt` |
| `art/ui/buckets/bucket-expedition-snow-256.png` | Ведро Expedition Bucket со снегом | Та же таблица, ключ `BucketSnow:ExpeditionBag` | 3D-ведро `BucketArt` |
| `art/ui/buckets/bucket-hauler-snow-256.png` | Ведро Hauler Bucket со снегом | Та же таблица, ключ `BucketSnow:HaulerBag` | 3D-ведро `BucketArt` |
| `art/ui/buckets/bucket-glacier-snow-256.png` | Ведро Glacier Bucket со снегом | Та же таблица, ключ `BucketSnow:GlacierBag` | 3D-ведро `BucketArt` |
| `art/ui/hud/hud-sparkles-512.png` (карточка `f2de28`, круг 5) | Золотые искры кольцом с пустой серединой | Та же таблица, ключ `Hud:Sparkles`: искры вокруг полного ведра «15/15» (`Windows/Hud.luau`) | Искры скрыты, «15/15» остаётся зелёным |

Грузить как Image (Decal) через Asset Manager в Studio или Creator Hub. Для частиц нужен id картинки (Image), а не декаля.
