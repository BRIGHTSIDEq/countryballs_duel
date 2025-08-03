# audio_generator.py
from gtts import gTTS
import os

def generate_intro_audio(text, path):
    print("Генерация аудио...")
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(path)
        print(f"Аудио сохранено в {path}")
        return True
    except Exception as e:
        print(f"Ошибка при генерации аудио: {e}")
        return False