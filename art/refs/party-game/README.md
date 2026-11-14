# Окно отряда и отсчёт старта — референсы

Для Георгия: какие картинки к какому интерфейсу и где их код. Попросить ИИ поправить окно можно так: «окно отряда, референс `art/refs/party-game/party-window-snow.png`, код `Windows/Queue.luau`, сделай …».

| Картинка | Что это | Код в игре | Статус |
| --- | --- | --- | --- |
| `party-window-snow.png` | Окно START A RUN на площадке: размер отряда 1–4, CONTINUE · N % (зелёная) и NEW GAME (красная), вопрос «NEW GAME?» с YES, START OVER / NO, KEEP IT. Снежная шапка и сосульки. | `src/StarterPlayer/StarterPlayerScripts/CleanSnow/Windows/Queue.luau` | Утверждён владельцем 13.11.2026 (вариант A), в игре |
| `party-count.png` | Отсчёт старта внизу экрана: SOLO RUN / CREW 1 / 3, «Launching in 14», иконки игроков (у хозяина корона), пустые места с плюсом и «Open», LEAVE и INVITE. Полный отряд — красным. | `src/StarterPlayer/StarterPlayerScripts/CleanSnow/QueueCountdown.luau` | Утверждён 13.11.2026. В игре он мельче и без деревянной доски: надпись, иконки и кнопки прямо поверх игры под персонажем (как на видео владельца) |
| `../../ui/party/host-crown.png` | Корона хозяина над его иконкой в отсчёте. | `QueueCountdown.luau`, константа `CROWN_IMAGE` | Загружена 13.11.2026: `rbxassetid://135747414697142`, в игре |
| `party-window.jpg` | Первый вариант окна (без снега, со START A RUN). | — | Устарел, заменён `party-window-snow.png` |

Рядом с каждой картинкой лежит `.prompt.md` — промпт ChatGPT Image, по которому её сделали. Новую версию делать через `node tools/imagegen/cli.mjs` (skill `codex-imagegen`), передав старую картинку как `--ref`. Цвета — только из `art/palette.json`.

Числа: отсчёт одному `QueueCountdown` = 3 с, отряду `QueueCountdownParty` = 15 с (`src/ReplicatedStorage/CleanSnow/Data/play.json`). Логика старта — сервер, `src/ServerScriptService/CleanSnow/QueueService.luau`. Спека — `docs/superpowers/specs/2026-11-13-party-start-buttons-design.md`.
