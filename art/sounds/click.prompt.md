# click.wav

- Событие: нажатие любой кнопки интерфейса
- Генератор: ElevenLabs Sound Effects (`eleven_text_to_sound_v2`, API `/v1/sound-generation`), 11.11.2026, карточка abc629.
- Параметры: duration_seconds 0.6, prompt_influence 0.7, output_format mp3_44100_128.
- Сырой файл: `Sources~/click.mp3`.
- Обработка: ffmpeg — обрезка тишины с краёв (порог −50 dB), моно 48 кГц, двухпроходный `loudnorm` I −16 LUFS, TP −1 dBTP, linear; WAV 16 бит. Первая генерация ("Soft rounded user interface button click, gentle bubbly pop...", 0.5 с) вышла почти тихой (−60 LUFS) и заменена. После обрезки щелчок 0,12 с — короче окна замера LUFS, поэтому громкость выставлена по пику: −0,9 dB, пик −1,3 dBFS.
- Roblox: id ставится в `src/ReplicatedStorage/CleanSnow/Data/sounds.json` после загрузки (только со слова владельца); до неё Studio играет этот файл локально.

## Prompt

Crisp bubbly pop sound of a cartoon game button being pressed, single short tap, clear and audible, no voice, no music
