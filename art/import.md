# Что загрузить в Roblox

Картинки, которые уже готовы и ждут загрузки. Решение владельца 10.11.2026: грузим позже, когда владельца добавят в плейс. После загрузки вписать id в код, проверить кадром в игре и убрать строку отсюда.

| Картинка | Что это | Куда вписать id | Что будет до загрузки |
| --- | --- | --- | --- |
| `art/vfx/snowflake-256.png` (исходник `art/vfx/snowflake.png`) | Снежинка, частица слома снега (баг `BUG-20261110-004`, карточка `9d8916`) | `SnowFeedbackConfig.SnowflakeTexture` в `src/ReplicatedStorage/SnowCleaningDemo/SnowFeedbackConfig.luau`: `"rbxassetid://<id>"` | При сломе снега есть вспышка и кубики, снежинок нет |

Грузить как Image (Decal) через Asset Manager в Studio или Creator Hub. Для частиц нужен id картинки (Image), а не декаля.
