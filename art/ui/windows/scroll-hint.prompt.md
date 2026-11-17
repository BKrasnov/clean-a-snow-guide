# scroll-hint.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-15. Прозрачный фон запрошен. Попытка 2 из 3 (действующая).

## Prompt (попытка 2)

A single small game UI hint icon for a kids' Roblox snow game: a cartoon hand with the index finger pointing up and slightly to the left, as if touching a phone screen, and next to the finger a tall curved double-headed arrow that points up and down (swipe up and down to scroll). Keep the same drawing as the attached hint icon (the first reference), only recolour the arrow. The hand is cream white #FFFDF5 with soft lavender shade #CDCDED on its darker side, a short light cuff at the wrist. The double arrow is ice blue #A8DEE7 with a deeper periwinkle-blue side #80A0E6, rounded chunky arrow heads at both ends; no saturated bright blue anywhere. A thick dark-brown outline (#2B1A11) around every shape, small white highlights, flat cartoon style like the attached windows. Seen from the front, centered, the hand and the arrow together fill most of the image, the arrow to the left of the hand. Transparent background, nothing else in the image: no text, no letters, no frame, no panel, no shadow on the ground, no screen.

Цвета из `art/palette.json`: Крем #FFFDF5, Тень снега #CDCDED, Лёд #A8DEE7, Синяя гора #80A0E6, Контур #2B1A11.

## Референсы

- `art/ui/windows/scroll-hint.png` (попытка 1) — тот же рисунок, меняется только цвет стрелки.
- `docs/superpowers/specs/phone-touch-sizes/30c439-ref-phone-classes.png` — style reference.

## Почему вторая попытка

Попытка 1 (тот же рисунок, стрелка Кристалл #8BE0FF с тёмной стороной #40A5FF) прошла проверку, но критик дизайна в круге 1 (15.11.2026, замечание m2) напомнил: синий #40A5FF в палитре — цвет редкости «Редкий», в подсказке его быть не должно. Режим «апрув везде» 15.11.2026: стрелку перекрасили генерацией в Лёд и Синюю гору; той же причиной полоска прокрутки стала «Синяя гора» вместо «Редкого».

## Итог

- Фон прозрачный: углы и всё вне рисунка с альфой 0, проверено по пикселям (Pillow). Пикселей рядом с #40A5FF — 0 (у попытки 1 — 842).
- `scroll-hint-256.png` — для игры: рисунок обрезан по краю с полем 12 и уменьшен до 252×256 (Lanczos).
- В Studio картинку показывает `npm run ui:local` (`rbxasset://textures/cleansnow/windows/scroll-hint-256.png`, `WindowPins.HINT_LOCAL`); в Roblox — после загрузки со слова владельца, id в `WindowPins.HINT_IMAGE`.
