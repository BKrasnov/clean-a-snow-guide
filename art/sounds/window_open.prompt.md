# window_open.wav

- Событие: открылось окно (Modals)
- Генератор: ElevenLabs Sound Effects (`eleven_text_to_sound_v2`, API `/v1/sound-generation`), 11.11.2026, карточка abc629.
- Параметры: duration_seconds 0.6, prompt_influence 0.6, output_format mp3_44100_128.
- Сырой файл: `Sources~/window_open.mp3`.
- Обработка: ffmpeg — обрезка тишины с краёв (порог −50 dB), моно 48 кГц, двухпроходный `loudnorm` I −16 LUFS, TP −1 dBTP, linear; WAV 16 бит.
- Roblox: id ставится в `src/ReplicatedStorage/CleanSnow/Data/sounds.json` после загрузки (только со слова владельца); до неё Studio играет этот файл локально.

## Prompt

Soft playful whoosh and pop of a menu panel opening, casual cartoon game user interface, short, no voice
