# video_compiler.py
import os
import glob
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeAudioClip

def compile_video(frames_dir, intro_audio_path, hit_sound_path, hit_frames, output_path, fps, parry_frames=None):
    """
    Компилирует видео с НОВОЙ логикой звуков:
    - Удары (hit_frames) = звук удара + остановка времени
    - Парирования (parry_frames) = только звук парирования
    
    Args:
        frames_dir: Папка с кадрами
        intro_audio_path: Путь к интро аудио
        hit_sound_path: Путь к звуку удара
        hit_frames: Список кадров с ударами (с остановкой времени)
        output_path: Путь для сохранения видео
        fps: Частота кадров
        parry_frames: Список кадров с парированием (только звук)
    """
    print("Сборка видео с новой логикой звуков...")
    frame_files = sorted(glob.glob(os.path.join(frames_dir, "frame_*.png")))
    if not frame_files:
        print("Кадры не найдены!")
        return

    clip = ImageSequenceClip(frame_files, fps=fps)

    final_audio_clips = []
    
    # Добавляем интро аудио
    if os.path.exists(intro_audio_path):
        final_audio_clips.append(AudioFileClip(intro_audio_path))
    
    # Добавляем звуки УДАРОВ (с остановкой времени)
    if os.path.exists(hit_sound_path) and hit_frames:
        hit_sound = AudioFileClip(hit_sound_path)
        
        print(f"Добавляем {len(hit_frames)} звуков ударов...")
        for frame_num in hit_frames:
            time_sec = frame_num / fps
            # Громкий звук для ударов с остановкой времени
            final_audio_clips.append(hit_sound.volumex(1.0).set_start(time_sec))
    
    # Добавляем звуки ПАРИРОВАНИЙ (отдельный звук)
    parry_sound_path = "assets/sounds/parry.mp3"
    if os.path.exists(parry_sound_path) and parry_frames:
        try:
            parry_sound_effect = AudioFileClip(parry_sound_path)
            print(f"Добавляем {len(parry_frames)} звуков парирований...")
            
            for frame_num in parry_frames:
                time_sec = frame_num / fps
                # Более тихий и отличающийся звук для парирования
                final_audio_clips.append(parry_sound_effect.volumex(0.5).set_start(time_sec))
        except Exception as e:
            print(f"Не удалось загрузить звук парирования: {e}")
            # Если нет отдельного звука парирования, используем звук удара но тише
            if os.path.exists(hit_sound_path):
                parry_substitute = AudioFileClip(hit_sound_path)
                print(f"Используем звук удара для парирований (приглушенный)...")
                for frame_num in parry_frames:
                    time_sec = frame_num / fps
                    final_audio_clips.append(parry_substitute.volumex(0.1).set_start(time_sec))

    # Попытка добавить другие звуки
    sound_effects = {
        "dash": "assets/sounds/dash.mp3",
        "arrow": "assets/sounds/arrow.mp3", 
        "victory": "assets/sounds/victory.mp3"
    }
    
    for sound_name, sound_path in sound_effects.items():
        if os.path.exists(sound_path):
            print(f"Найден звуковой файл: {sound_name}")
        else:
            print(f"Звуковой файл не найден: {sound_path}")

    # Компилируем финальное аудио
    if final_audio_clips:
        final_audio = CompositeAudioClip(final_audio_clips)
        if final_audio.duration > clip.duration:
             final_audio = final_audio.subclip(0, clip.duration)
        clip = clip.set_audio(final_audio)

    # Сохраняем видео
    print("Экспортируем финальное видео...")
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=4, logger='bar')
    print(f"✅ Видео успешно сохранено в {output_path}")
    print(f"🔊 Ударов с остановкой времени: {len(hit_frames) if hit_frames else 0}")
    print(f"🔊 Парирований с звуком: {len(parry_frames) if parry_frames else 0}")