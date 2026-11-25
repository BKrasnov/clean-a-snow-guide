# Ролик Санты: референсы (карточка 784f91)

Спека `docs/superpowers/specs/2026-11-22-santa-after-tutorial-design.md`, раздел «Ролик, как в видео».

Два кадра ChatGPT Image (`codex-imagegen`), ждут генерации: 22.11.2026 лимит ChatGPT Image исчерпан до 25.11.2026 11:54.

- `burst.prompt.txt` — сани над зоной 1, мешок срывается, 8 подарков разлетаются; надпись «SANTA'S GIFTS ARE EVERYWHERE!» и кнопка SKIP.
- `landed.prompt.txt` — вид сверху: подарки легли по всей зоне 1 и светятся, сани улетают; та же надпись и SKIP.
- `ref-sleigh.png`, `ref-gift.png` — нынешние сани и подарок, кадры из Studio 22.11.2026.

Команда (из корня репозитория):

```bash
node tools/imagegen/cli.mjs --out art/refs/santa-cutscene/burst.png --prompt-file art/refs/santa-cutscene/burst.prompt.txt --ref art/refs/hud-new/key/run-pc.png --ref art/frames/02-snow-run.jpeg --ref art/refs/santa-cutscene/ref-sleigh.png --ref art/refs/santa-cutscene/ref-gift.png
```

Для второго кадра — `landed` вместо `burst`.
