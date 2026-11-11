# seed-find-rays-mask.png

Generated with ChatGPT Image: Codex CLI `codex exec`, model gpt-6.1-sol, built-in image_gen, through `node tools/imagegen/cli.mjs`.

Дата генерации: 2026-11-11.

## Prompt

Game effect mask texture: a cartoon sunburst of light rays, pure white on a pure flat black background #000000, square, centred.
Twelve soft wide rays radiating from the centre, alternating long and short, bright white near the centre fading smoothly to black toward the tips, soft but clean edges. A soft white round glow in the very centre. Four small crisp four-point star sparkles in white between the rays near the tips.
Only white and greys on black: no colour at all, no text, no letters, no frame, no noise, no extra objects, no watermark. The black must be perfectly flat and uniform to the image edges.

## Попытки и проверка

- Попыток: 3. Первые две — цветные лучи с `--transparent`: генератор дал грязную красно-жёлтую кайму вокруг лучей, они удалены.
- Третья — белые лучи на чёрном. Из неё сделан `seed-find-rays-512.png`: белый цвет, прозрачность = яркость маски (Pillow), 512×512. Цвет (золото `#FFCE43`, крем `#FFFDF5`) задаёт игра через `ImageColor3`.
- Проверено: в центре альфа 254, в углу 1.
