# Что загрузить в Roblox

Картинки, которые уже готовы и ждут загрузки. Решение владельца 10.11.2026: грузим позже, когда владельца добавят в плейс. После загрузки вписать id в код, проверить кадром в игре и убрать строку отсюда.

| Картинка | Что это | Куда вписать id | Что будет до загрузки |
| --- | --- | --- | --- |
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
| `art/ui/upgrades/processor-256.png` | Переработчик, улучшение Process (`ProcessorSpeed`) | Та же таблица, ключ `Upgrade:ProcessorSpeed`: улучшение Process в окне улучшений и Мастерской | 3D-машина из старой карточки улучшений |
| `art/ui/pets/pet-snow-fox-256.png` (лист `art/ui/pets/pets-icons-sheet.png`, карточка `907897`) | Питомец песец (`SnowFox`) | Та же таблица, ключ `Pet:SnowFox` (карточка `657ae9`): карточка песца в окне Pets | 3D-модель питомца в окне Pets |
| `art/ui/pets/pet-owl-256.png` | Питомец полярная сова (`Owl`) | Та же таблица, ключ `Pet:Owl`: карточка совы в окне Pets | 3D-модель (голубая сова) |
| `art/ui/pets/pet-snow-hare-256.png` | Питомец заяц-беляк (`SnowHare`) | Та же таблица, ключ `Pet:SnowHare`: карточка зайца в окне Pets | 3D-модель питомца в окне Pets |
| `art/ui/hockey/robot-head-256.png` (исходник `art/ui/hockey/robot-head.png`, карточка `657ae9`) | Голова робота на пустом месте хоккейной панели составов | Та же таблица, ключ `Hockey:Robot`: панель составов над табло хоккея (`HockeyTeamsPanel.luau`) | 3D-голова робота |
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

Грузить как Image (Decal) через Asset Manager в Studio или Creator Hub. Для частиц нужен id картинки (Image), а не декаля.
