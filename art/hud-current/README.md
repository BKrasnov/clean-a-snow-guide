# Текущий HUD: кадры и индекс

Весь HUD игры как он есть 17.11.2026 (коммит `a1a1ba122`), снятый в живой игре: лобби, забег, машина, хоккей, на компьютере и на телефоне. Это исходник для референсов нового вида HUD (ChatGPT Image), сами референсы здесь не делались. Карточка `f23072`.

- [overview-pc.jpg](overview-pc.jpg) — все кадры компьютера на одном листе, [overview-phone.jpg](overview-phone.jpg) — все кадры телефона.
- `frames/` — полные кадры мест и состояний, `frames/prompt-*.jpg` — подсказки E (их рисует сам Roblox).
- `elements/` — каждый элемент вырезан по своему прямоугольнику: по одному разу на вид (экран, текст без чисел, размер), из первого кадра, где он появился. Список вырезок с текстом и прямоугольником — [elements.json](elements.json).

## Как снято

- Сценарии Studio `tools/studio-scenarios/hud-tour-run.json`, `hud-tour-vehicle.json`, `hud-tour-hockey.json` (их пишет `_gen-hud-tour.mjs`). Забег — шаги первого забега нового игрока (`first-run-bucket-full.json`), машина — `cargo-hud.json`, хоккей — `hockey-match.json`. Перед каждым кадром сценарий меряет все видимые элементы экрана, `_hud-tour-crops.mjs` режет по этим меркам кадры и вырезки.
- Компьютер: окно Studio 2019x771 точек. Оно шире обычного монитора 16:9, поэтому HUD здесь мельче (масштаб HUD 0,94); на мониторе 1920x1080 элементы примерно на пятую часть крупнее.
- Телефон: экран 844x390 (касание) подставлен в Studio атрибутами `ScreenSize` и `TouchScreen`, кадр обрезан по этому экрану. Это раскладка игры для такого экрана, а не настоящий телефон: верхней панели Roblox, джойстика и кнопки прыжка в кадре нет.
- Подсказки E и табличка SELL рисуются поверх всего (CoreGui и AlwaysOnTop), снимок Studio их не видит. Их кадры — снимок самого окна Studio в этот момент (`_hud-tour-prompts.mjs`), поэтому в них видны кнопки меню Roblox слева сверху.
- Состояния оружия (нагрев, перегрев, ожидание Молотова) и полный кузов машины показаны атрибутами, которые пишет сервер: снят только вид, без настоящей стрельбы.

Пересъёмка: `node tools/studio-scenarios/_gen-hud-tour.mjs`, затем для каждого тура `npm run play -- hud-tour-run > build/hud-tour-run.log 2>&1` и рядом `node tools/studio-scenarios/_hud-tour-prompts.mjs build/hud-tour-run.log build/hud-tour-prompts`, в конце `node tools/studio-scenarios/_hud-tour-crops.mjs build/studio-play/<папки трёх туров> --prompts build/hud-tour-prompts --view 13,270,2522,890`. `--view` — игровое поле внутри снимка окна, у другого окна Studio оно своё.

## Кадры

Номер кадра — место: 01–03 лобби, 04–19 забег, 21–24 машина, 31–33 хоккей. У кадра с пометкой «да» в колонке «Телефон» есть пара `-phone.jpg`.

| Кадр | Место | Состояние | Что видно | Телефон |
| --- | --- | --- | --- | --- |
| [01-lobby-pc.jpg](frames/01-lobby-pc.jpg) | лобби | новый игрок до первого забега | плашка FIRST RUN / START A RUN, монеты и кристаллы, кнопки слева сверху и справа, MORE ACTIONS закрыто | да |
| [02-lobby-more-actions-pc.jpg](frames/02-lobby-more-actions-pc.jpg) | лобби | MORE ACTIONS открыто | список: грузовик, DAILY GEMS, GEM WHEEL | да |
| [03-queue-countdown-pc.jpg](frames/03-queue-countdown-pc.jpg) | лобби | на площадке старта | SOLO RUN, Launching in 3, LEAVE, INVITE | нет |
| [04-run-start-pc.jpg](frames/04-run-start-pc.jpg) | забег | начало забега | таймер и участок, ведро 0/15, ложка в руке, панель из 2 ячеек, задание BREAK THE SNOW, прицел; на телефоне кнопка SCOOP | да |
| [05-run-strike-pc.jpg](frames/05-run-strike-pc.jpg) | забег | удар ложкой по снегу | задание BREAK THE SNOW, снег в ведре | нет |
| [06-run-bring-snow-pc.jpg](frames/06-run-bring-snow-pc.jpg) | забег | снег набран | задание BRING SNOW TO THE TRAY | да |
| [07-run-selling-pc.jpg](frames/07-run-selling-pc.jpg) | забег | сдача на поддоне | задание SELLING YOUR SNOW 0/25 COINS, всплывающая плашка | нет |
| [08-run-hold-focus-pc.jpg](frames/08-run-hold-focus-pc.jpg) | забег | первые монеты | подсказка OPEN UPGRADES / LATER с затемнением, подсвеченная кнопка UPGR | да |
| [09-run-shovel-count-pc.jpg](frames/09-run-shovel-count-pc.jpg) | забег | копит на лопату | задание BREAK SNOW FOR A SHOVEL N/20 COINS, плашка | да |
| [10-run-bucket-full-pc.jpg](frames/10-run-bucket-full-pc.jpg) | забег | ведро полное | BUCKET FULL! GO SELL!, ведро 15/15 | да |
| [11-run-toast-pc.jpg](frames/11-run-toast-pc.jpg) | забег | у переработчика | всплывающая плашка о сдаче | да |
| [11b-run-target-pc.jpg](frames/11b-run-target-pc.jpg) | забег | прицел на снегу | имя снега и полоса прочности (кадр первого прохода тура) | нет |
| [12-run-seed-found-pc.jpg](frames/12-run-seed-found-pc.jpg) | забег | найдено семечко | картинка семечка, You found, Strawberry, Common | нет |
| [13-run-seed-counter-pc.jpg](frames/13-run-seed-counter-pc.jpg) | забег | после семечка | счётчик Seeds 1/7 сверху | да |
| [14-run-more-actions-pc.jpg](frames/14-run-more-actions-pc.jpg) | забег | MORE ACTIONS открыто | список забега, с кнопкой возврата в лобби | да |
| [15-run-weapon-heat-pc.jpg](frames/15-run-weapon-heat-pc.jpg) | забег | тепловая пушка греется | панель из 7 ячеек, оранжевая полоса нагрева | да |
| [16-run-weapon-overheat-pc.jpg](frames/16-run-weapon-overheat-pc.jpg) | забег | перегрев | красная полоса | нет |
| [17-run-molotov-wait-pc.jpg](frames/17-run-molotov-wait-pc.jpg) | забег | ожидание Молотова | жёлтая полоса | нет |
| [18-run-save-note-pc.jpg](frames/18-run-save-note-pc.jpg) | забег | открыто меню Roblox | надпись YOUR PROGRESS SAVES (само меню Roblox в кадр не попадает) | нет |
| [19-run-shop-stand-pc.jpg](frames/19-run-shop-stand-pc.jpg) | забег | у стойки оружия фермы | HUD у стойки; её подсказка E — `prompt-shop-stand` | нет |
| [21-vehicle-locked-pc.jpg](frames/21-vehicle-locked-pc.jpg) | машина | у закрытой машины | табличка в мире N/1,500 Snow Cleaned, HUD забега | нет |
| [22-vehicle-drive-truck-pc.jpg](frames/22-vehicle-drive-truck-pc.jpg) | машина | в грузовике | CARGO N/1000, надпись у стены участка | да |
| [23-vehicle-drive-tank-pc.jpg](frames/23-vehicle-drive-tank-pc.jpg) | машина | в танке | CARGO N/2000 | нет |
| [24-vehicle-cargo-full-pc.jpg](frames/24-vehicle-cargo-full-pc.jpg) | машина | кузов полон | CARGO FULL! GO SELL! | да |
| [31-hockey-team-panel-pc.jpg](frames/31-hockey-team-panel-pc.jpg) | хоккей | у катка после E | панель команд: красные, VS, синие, START, время, крестик | да |
| [32-hockey-match-pc.jpg](frames/32-hockey-match-pc.jpg) | хоккей | матч идёт | счёт, секундомер, EXIT, кнопка клюшки | да |
| [33-hockey-end-pc.jpg](frames/33-hockey-end-pc.jpg) | хоккей | конец матча | табло DRAW | да |
| [prompt-queue-plate.jpg](frames/prompt-queue-plate.jpg) | лобби | на площадке старта | подсказка E START A RUN | нет |
| [prompt-bucket-full-sell.jpg](frames/prompt-bucket-full-sell.jpg) | забег | ведро полное | табличка SELL над поддоном | нет |
| [prompt-shop-stand.jpg](frames/prompt-shop-stand.jpg) | забег | у стойки оружия | подсказка E покупки | нет |
| [prompt-conveyor-build.jpg](frames/prompt-conveyor-build.jpg) | машина | у призрака конвейера рядом с грузовиком | подсказка E Build с ценой | нет |
| [prompt-hockey-join.jpg](frames/prompt-hockey-join.jpg) | хоккей | у красного круга катка | подсказка E входа в команду | нет |

## Элементы HUD

Где виден — по всем кадрам, где элемент измерен. Кадр — первый, где он появился. Вырезки других состояний того же элемента (текст, размер) лежат в `elements/` под именем своего кадра.

| Элемент | Где виден | Состояние | Кадр | Вырезка | Код |
| --- | --- | --- | --- | --- | --- |
| Кнопки слева сверху: статистика, новости, настройки | лобби, забег, машина, хоккей, телефон | всегда | [01-lobby-pc.jpg](frames/01-lobby-pc.jpg) | [ПК](elements/01-lobby-pc--QuickMenu.png), [телефон](elements/01-lobby-phone--QuickMenu.png) | `models/ (CleanSnowUI)`, [InterfaceController.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/InterfaceController.luau) |
| Монеты и кристаллы | лобби, забег, машина, хоккей, телефон | число растёт со счётом | [01-lobby-pc.jpg](frames/01-lobby-pc.jpg) | [ПК](elements/01-lobby-pc--Currency.png), [телефон](elements/01-lobby-phone--Currency.png) | `models/ (CleanSnowUI)`, [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau), [CounterFeedback.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/CounterFeedback.luau) |
| MORE ACTIONS (закрыто) | лобби, забег, машина, хоккей, телефон | кнопка | [01-lobby-pc.jpg](frames/01-lobby-pc.jpg) | [ПК](elements/01-lobby-pc--ExpeditionActions.Toggle.png), [телефон](elements/01-lobby-phone--ExpeditionActions.Toggle.png) | [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau) |
| MORE ACTIONS (открыто): грузовик, DAILY GEMS, GEM WHEEL, в лобби | лобби, забег, телефон | строки списка | [02-lobby-more-actions-pc.jpg](frames/02-lobby-more-actions-pc.jpg) | [ПК](elements/02-lobby-more-actions-pc--ExpeditionActions.Truck.png), [телефон](elements/02-lobby-more-actions-phone--ExpeditionActions.Truck.png) | [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau) |
| Кнопки справа: PETS, UPGR, INDEX | лобби, забег, машина, хоккей, телефон | всегда; UPGR подсвечен в подсказке Hold | [01-lobby-pc.jpg](frames/01-lobby-pc.jpg) | [ПК](elements/01-lobby-pc--SideMenu.png), [телефон](elements/01-lobby-phone--SideMenu.png) | `models/ (CleanSnowUI)`, [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau), [SnowUpgradeFocus.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/SnowUpgradeFocus.luau) |
| Плашка первого забега FIRST RUN / START A RUN | лобби, телефон | только в лобби до первого забега | [01-lobby-pc.jpg](frames/01-lobby-pc.jpg) | [ПК](elements/01-lobby-pc--TutorialGuide.png), [телефон](elements/01-lobby-phone--TutorialGuide.png) | [TutorialController.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/TutorialController.luau) |
| Отсчёт старта SOLO RUN / Launching in 3, LEAVE, INVITE | лобби | на площадке старта | [03-queue-countdown-pc.jpg](frames/03-queue-countdown-pc.jpg) | [ПК](elements/03-queue-countdown-pc--QueueCountdown.Line.png) | [QueueCountdown.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/QueueCountdown.luau) |
| Таймер, имя участка, AREA, полоса и процент расчистки, подпись открытия участка | забег, машина, хоккей, телефон | в забеге; Locked у закрытого участка | [04-run-start-pc.jpg](frames/04-run-start-pc.jpg) | [ПК](elements/04-run-start-pc--RoundStatus.png), [телефон](elements/04-run-start-phone--RoundStatus.png) | [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau) |
| Ведро: счётчик снега (в машине — CARGO) и примерная цена «~N COINS» | забег, машина, хоккей, телефон | 0/15 ... 15/15; в машине N/1000, N/2000 | [04-run-start-pc.jpg](frames/04-run-start-pc.jpg) | [ПК](elements/04-run-start-pc--Bag.png), [телефон](elements/04-run-start-phone--Bag.png) | [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau), [CounterFeedback.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/CounterFeedback.luau) |
| Ведро в руке (кадр от 17.11.2026) | забег, машина, хоккей, телефон | в забеге, пустое и полное | [04-run-start-pc.jpg](frames/04-run-start-pc.jpg) | [ПК](elements/04-run-start-pc--FirstPersonBucket.Bucket.png), [телефон](elements/04-run-start-phone--FirstPersonBucket.Bucket.png) | Убрано 19.11.2026 |
| Панель инструментов (1 — ложка, дальше оружие, замок) | забег, машина, хоккей, телефон | 2 ячейки в начале, 7 со стойками оружия | [04-run-start-pc.jpg](frames/04-run-start-pc.jpg) | [ПК](elements/04-run-start-pc--Hotbar.png), [телефон](elements/04-run-start-phone--Hotbar.png) | [RunHotbarView.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/RunHotbarView.luau) |
| Ячейки оружия: ледоруб, лопата, отбойник, тепловая пушка, Молотов | забег, телефон | по одной картинке | [15-run-weapon-heat-pc.jpg](frames/15-run-weapon-heat-pc.jpg) | [ПК](elements/15-run-weapon-heat-pc--Hotbar.SpecialSlot2.png), [телефон](elements/15-run-weapon-heat-phone--Hotbar.SpecialSlot2.png) | [RunHotbarView.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/RunHotbarView.luau), [InterfaceIcons.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/InterfaceIcons.luau) |
| Прицел | забег, машина, хоккей, телефон | в забеге | [04-run-start-pc.jpg](frames/04-run-start-pc.jpg) | [ПК](elements/04-run-start-pc--Reticle.png), [телефон](elements/04-run-start-phone--Reticle.png) | [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau) |
| Задание по центру внизу: BREAK THE SNOW, BRING SNOW TO THE TRAY, SELLING YOUR SNOW, BREAK SNOW FOR A SHOVEL | забег, машина, хоккей, телефон | меняется по шагам забега | [04-run-start-pc.jpg](frames/04-run-start-pc.jpg) | [ПК](elements/04-run-start-pc--SnowTask.png), [телефон](elements/04-run-start-phone--SnowTask.png) | [SnowMatchHud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/SnowMatchHud.luau), [InterfaceController.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/InterfaceController.luau) |
| Имя снега и полоса прочности под прицелом | забег | когда прицел на снегу | [11b-run-target-pc.jpg](frames/11b-run-target-pc.jpg) | [ПК](elements/11b-run-target-pc--TargetInfo.png) | [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau) |
| Всплывающая плашка (уведомление) | забег, телефон | сдача, переработка, подсказки | [07-run-selling-pc.jpg](frames/07-run-selling-pc.jpg) | [ПК](elements/07-run-selling-pc--Toast.png), [телефон](elements/08-run-hold-focus-phone--Toast.png) | [InterfaceController.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/InterfaceController.luau) |
| Подсказка OPEN UPGRADES / LATER с затемнением | забег, телефон | после первых монет | [08-run-hold-focus-pc.jpg](frames/08-run-hold-focus-pc.jpg) | [ПК](elements/08-run-hold-focus-pc--SnowUpgradeFocus.Hint.png), [телефон](elements/08-run-hold-focus-phone--SnowUpgradeFocus.Hint.png) | [SnowUpgradeFocus.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/SnowUpgradeFocus.luau) |
| BUCKET FULL! GO SELL! / CARGO FULL! GO SELL! | забег, машина, телефон | полное ведро или кузов | [10-run-bucket-full-pc.jpg](frames/10-run-bucket-full-pc.jpg) | [ПК](elements/10-run-bucket-full-pc--BagFullText.png), [телефон](elements/10-run-bucket-full-phone--BagFullText.png) | [BagFullGuide.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/BagFullGuide.luau) |
| Найденное семечко: картинка, You found, имя и редкость | забег | на 3 секунды | [12-run-seed-found-pc.jpg](frames/12-run-seed-found-pc.jpg) | [ПК](elements/12-run-seed-found-pc--SeedFind.png) | `SeedFindView.luau` (удалён 22.11.2026 вместе с семенами, карточка `adff0e`) |
| Счётчик семян Seeds N/7 | забег, телефон | после первого семечка | [12-run-seed-found-pc.jpg](frames/12-run-seed-found-pc.jpg) | [ПК](elements/12-run-seed-found-pc--SeedCounter.png), [телефон](elements/13-run-seed-counter-phone--SeedCounter.png) | `SeedFindView.luau` (удалён 22.11.2026 вместе с семенами, карточка `adff0e`) |
| Полоса оружия: нагрев, перегрев, ожидание Молотова | забег, телефон | оранжевая, красная, жёлтая | [15-run-weapon-heat-pc.jpg](frames/15-run-weapon-heat-pc.jpg) | [ПК](elements/15-run-weapon-heat-pc--WeaponStatus.Frame.png), [телефон](elements/15-run-weapon-heat-phone--WeaponStatus.Frame.png) | [WeaponController.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/WeaponController.luau) |
| Надпись YOUR PROGRESS SAVES | забег | пока открыто меню Roblox | [18-run-save-note-pc.jpg](frames/18-run-save-note-pc.jpg) | [ПК](elements/18-run-save-note-pc--SnowSaveReminder.Reminder.png) | [SnowMatchHud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/SnowMatchHud.luau) |
| Надпись у стены участка Clear Area N first to go further! | машина, телефон | у закрытого участка | [22-vehicle-drive-truck-pc.jpg](frames/22-vehicle-drive-truck-pc.jpg) | [ПК](elements/22-vehicle-drive-truck-pc--ZoneWallText.png), [телефон](elements/22-vehicle-drive-truck-phone--ZoneWallText.png) | [ZoneBarrierController.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/ZoneBarrierController.luau) |
| Панель команд хоккея: красные, VS, синие, START, время, крестик | хоккей, телефон | у катка после E | [31-hockey-team-panel-pc.jpg](frames/31-hockey-team-panel-pc.jpg) | [ПК](elements/31-hockey-team-panel-pc--HockeyTeams.Panel.png), [телефон](elements/31-hockey-team-panel-phone--HockeyTeams.Panel.png) | [HockeyTeamsPanel.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/HockeyTeamsPanel.luau) |
| Счёт матча, секундомер, EXIT | хоккей, телефон | во время матча | [32-hockey-match-pc.jpg](frames/32-hockey-match-pc.jpg) | [ПК](elements/32-hockey-match-pc--HockeyMatch.Top.png), [телефон](elements/32-hockey-match-phone--HockeyMatch.Top.png) | [HockeyMatchView.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/HockeyMatchView.luau) |
| Кнопка клюшки | хоккей, телефон | во время матча | [32-hockey-match-pc.jpg](frames/32-hockey-match-pc.jpg) | [ПК](elements/32-hockey-match-pc--HockeyMatch.Shoot.png), [телефон](elements/32-hockey-match-phone--HockeyMatch.Shoot.png) | [HockeyMatchView.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/HockeyMatchView.luau) |
| Табло конца матча (DRAW, победа) | хоккей, телефон | конец матча | [33-hockey-end-pc.jpg](frames/33-hockey-end-pc.jpg) | [ПК](elements/33-hockey-end-pc--HockeyMatch.Result.png), [телефон](elements/33-hockey-end-phone--HockeyMatch.Result.png) | [HockeyMatchView.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/HockeyMatchView.luau) |
| Кнопка действия для пальца (SCOOP / TAP) | забег, машина, хоккей, телефон | только телефон и планшет | [04-run-start-phone.jpg](frames/04-run-start-phone.jpg) | [телефон](elements/04-run-start-phone--ActionButton.png) | [Windows/Hud.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Hud.luau), [TouchSizes.luau](../../src/StarterPlayer/StarterPlayerScripts/CleanSnow/TouchSizes.luau) |

## Что видно на кадрах

Наложения, которые стоит учесть в новом виде HUD:

- Телефон: задание по центру внизу ложится на панель инструментов (04, 09).
- Телефон: надпись у стены участка Clear Area 1 first to go further! наезжает на таймер и участок или на задание (22, 24).
- Телефон: панель команд хоккея закрывает ведро и кнопку SCOOP (31).
- Телефон: панель из 7 ячеек упирается в кнопку SCOOP (15).
- Компьютер: YOUR PROGRESS SAVES стоит поверх Seeds 1/7 (18), найденное семечко — поверх BUCKET FULL! (12).
- В панели команд хоккея аватар белый или чёрный: Studio не грузит картинки аватаров, в опубликованной игре там лицо игрока.

Ограничение подстановки телефона: всплывающая плашка, подсказка OPEN UPGRADES и полоса оружия раскладываются по всему окну Studio, а не по экрану 844x390, поэтому в кадр телефона не попадают. Их вырезки с телефона помечены в `elements.json` как `offPhoneScreen`: `08-run-hold-focus-phone--Toast.png`, `11-run-toast-phone--Toast.png`, `08-run-hold-focus-phone--SnowUpgradeFocus.Hint.png`, `...Later.png`, `15-run-weapon-heat-phone--WeaponStatus.Frame.png`, а также край списка MORE ACTIONS и ведра в руке (`01-lobby-phone--ExpeditionActions.png`, `04-run-start-phone--FirstPersonBucket.Bucket.png`). Их вид на компьютере — кадры 07, 08, 11, 15–17.

## Что снять не удалось

| Что | Почему |
| --- | --- |
| Кнопки Roblox для пальца: прыжок, джойстик | их рисует сам Roblox только на настоящем касании; нужен телефон или эмулятор устройств Studio, а он требует управления мышью (computer use), которое в этой задаче запрещено |
| Кнопки машины для пальца (выйти, стрелять) | кнопки ContextActionService тоже появляются только на настоящем касании, причина та же |
| Подсказка E «сесть в машину» | снимок окна в этот момент поймал подсказку Build конвейера рядом (`prompt-conveyor-build`), а подсказки посадки в нём нет |
| Само меню Roblox (Esc) | это CoreGui Roblox, снимок Studio его не видит; снята только надпись игры YOUR PROGRESS SAVES под ним |
| Отсчёт старта на телефоне | отсчёт идёт 3 секунды, в туре успевает только кадр компьютера |
| HUD аркадных мини-игр и полоса боя с Гринчем в убежище | отдельные режимы, в эти туры не входят; старые кадры — `art/frames/live-audit/arcade-results-max.jpg`, `art/frames/live-audit/hideout-grinch-windup.jpg` |
| Таблички в мире: таймер аркадного зала, полоса переработчика, сад | это не HUD, а щиты в мире; отдельно не снимались. Случайно попали в кадры: маяки редкого снега (GOLDEN SNOW, CANDY SNOW), замок машины N/M Snow Cleaned (21), табло SOLO RECORDS, занавес участка |

## Большие окна (вне этой задачи)

Их не снимали: это окна поверх игры, у них свой критик и своя таблица размеров. Каждое открывается своей кнопкой или стойкой из HUD.

| Окно | Откуда открывается | Код |
| --- | --- | --- |
| Мастерская улучшений | кнопка UPGR справа, клавиша Tab | `Windows/Workshop.luau` |
| Индекс снега | кнопка INDEX справа | `Windows/Upgrades.luau` (вкладка Index) |
| Питомцы (PETS) | кнопка справа | `Windows/Pets.luau` |
| Статистика и таблица рекордов | первая кнопка слева сверху | `Windows/Stats.luau` |
| Новости | вторая кнопка слева сверху | `Windows/News.luau` |
| Настройки | шестерёнка слева сверху | `Windows/Settings.luau` |
| Старт забега (START A RUN) | E на площадке старта в лобби | `Windows/Queue.luau` |
| Итоги забега | конец забега | `Windows/Results.luau` |
| Ежедневные кристаллы (DAILY GEMS) | MORE ACTIONS | `Windows/DailyGems.luau`, `GemWindowShell.luau` |
| Колесо кристаллов (GEM WHEEL) | MORE ACTIONS | `Windows/GemWheel.luau`, `GemWindowShell.luau` |
| Классы | E у домика CLASSES в лобби | `Windows/Classes.luau` |
| Улучшение переработчика | E у переработчика | `Windows/ProcessorUpgrade.luau` |
| Переработка | переработчик | `Windows/Processing.luau` |
| Магазин и покупка инструмента | сейчас не открываются (продают стойки фермы, карточка 51a4ef) | `Windows/Shop.luau`, `Windows/ToolPurchase.luau` |
