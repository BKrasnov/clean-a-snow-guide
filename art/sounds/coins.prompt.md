# coins.wav

- Событие: монеты за переработанный снег и награды за животных (Processed, RabbitCaught, AnimalReward, BirdReward)
- Генератор: ElevenLabs Sound Effects (`eleven_text_to_sound_v2`, API `/v1/sound-generation`), 11.11.2026, карточка abc629.
- Параметры: duration_seconds 1.0, prompt_influence 0.6, output_format mp3_44100_128.
- Сырой файл: `Sources~/coins.mp3`.
- Обработка: ffmpeg — обрезка тишины с краёв (порог −50 dB), моно 48 кГц, двухпроходный `loudnorm` I −16 LUFS, TP −1 dBTP, linear; WAV 16 бит. Итог: −17 LUFS, пик −1 dBTP (ограничен пиком).
- Roblox: id ставится в `src/ReplicatedStorage/CleanSnow/Data/sounds.json` после загрузки (только со слова владельца); до неё Studio играет этот файл локально.

## Prompt

Bright cartoon coins clinking and dropping into a small pile, cheerful casual kids game reward, crisp and short, no music, no voice
