# purchase.wav

- Событие: покупка у стенда или в окне (ответ сервера purchased)
- Генератор: ElevenLabs Sound Effects (`eleven_text_to_sound_v2`, API `/v1/sound-generation`), 11.11.2026, карточка abc629.
- Параметры: duration_seconds 1.2, prompt_influence 0.6, output_format mp3_44100_128.
- Сырой файл: `Sources~/purchase.mp3`.
- Обработка: ffmpeg — обрезка тишины с краёв (порог −50 dB), моно 48 кГц, двухпроходный `loudnorm` I −16 LUFS, TP −1 dBTP, linear; WAV 16 бит.
- Roblox: id ставится в `src/ReplicatedStorage/CleanSnow/Data/sounds.json` после загрузки (только со слова владельца); до неё Studio играет этот файл локально.

## Prompt

Cheerful cash register ka-ching with a soft bell ding, casual kids game purchase confirmation, short and clean, no voice
