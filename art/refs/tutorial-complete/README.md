# Плашка TUTORIAL COMPLETE: промпты референса

Карточки `9a75f4` и `983641`. Референс не нарисован: 22.11.2026 у ChatGPT Image кончился лимит (сброс 25.11.2026, 11:54). Плашку в игре собрали из одобренных плашек нового HUD (решение Леонида 22.11.2026), переделка по референсу — `983641`.

- `variant-a.prompt.txt` — большая деревянная плашка со снежной шапкой, под ней пилюля «+5» с гемом. Референсы: `art/refs/hud-new/key/run-pc.png`, `art/refs/hud-new/elements/15-zone-notice.png`.
- `variant-b.prompt.txt` — буквы «TUTORIAL / COMPLETE!» золотом без плашки, как «BUCKET FULL! GO SELL!», и крупный гем «+5». Референсы: `art/refs/hud-new/key/run-pc.png`, `art/hud-current/frames/10-run-bucket-full-pc.jpg`.

```bash
node tools/imagegen/cli.mjs --out art/refs/tutorial-complete/variant-a.png --prompt-file art/refs/tutorial-complete/variant-a.prompt.txt --ref art/refs/hud-new/key/run-pc.png --ref art/refs/hud-new/elements/15-zone-notice.png
```
