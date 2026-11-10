# Палитра

Лист цветов из `art/palette.json` и кадр забега, перекрашенный только в цвета палитры. Правила — `docs/style.md`. После правки `art/palette.json` картинки перерисовать: `uv run --no-project --with pillow --with numpy python tools/art/palette_sheets.py .`
