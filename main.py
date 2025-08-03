# main.py
import os
import shutil
import pygame
import time
import math
from config import *
from simulation import GameState
from renderer import Renderer
from audio_generator import generate_intro_audio
from video_compiler import compile_video
from fighter_selector import FighterSelector, get_fighter_classes

def cleanup():
    """Очистка временных файлов и создание необходимых папок"""
    if os.path.exists(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    
    # Создаем папку assets если её нет (для звуков)
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR, exist_ok=True)
        print(f"Создана папка {ASSETS_DIR} для звуковых файлов")

def create_fighters(fighter1_id, fighter2_id):
    """Создает бойцов на основе выбора пользователя"""
    fighter_classes = get_fighter_classes()
    selector = FighterSelector()
    
    # Получаем классы бойцов
    fighter1_class_name = selector.fighters[fighter1_id]['class']
    fighter2_class_name = selector.fighters[fighter2_id]['class']
    
    fighter1_class = fighter_classes[fighter1_class_name]
    fighter2_class = fighter_classes[fighter2_class_name]
    
    # Создаем бойцов в противоположных углах арены
    fighter1 = fighter1_class(x=ARENA_X + 100, y=ARENA_Y + 100)
    fighter2 = fighter2_class(x=ARENA_X + ARENA_WIDTH - 100, y=ARENA_Y + ARENA_HEIGHT - 100)
    
    return fighter1, fighter2

def main():
    pygame.init()
    
    # Инициализируем звук
    pygame.mixer.init()
    
    # НОВЫЙ ИНТЕРФЕЙС ВЫБОРА БОЙЦОВ
    print("🎮 Добро пожаловать в ЭПИЧЕСКУЮ АРЕНУ!")
    print("⚔️ Выберите ваших бойцов для дуэли!")
    
    selector = FighterSelector()
    fighter1_id, fighter2_id = selector.select_fighters()
    
    if fighter1_id is None or fighter2_id is None:
        print("Выбор отменен.")
        return
    
    # Создаем выбранных бойцов
    ball1, ball2 = create_fighters(fighter1_id, fighter2_id)
    
    print(f"🥊 {ball1.name} VS {ball2.name}")
    print(f"⚔️ {ball1.weapon_type.title()} против {ball2.weapon_type.title()}")
    
    # Сохраняем главный экран в переменную
    display_screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
    pygame.display.set_caption(f"Epic Ball Duel - {ball1.name} VS {ball2.name}!")

    cleanup()

    renderer = Renderer(WIDTH, HEIGHT)
    game_state = GameState(ball1, ball2)

    # Генерируем интро аудио с именами выбранных бойцов
    intro_text = f"Fight {ball1.name} versus {ball2.name} "
    generate_intro_audio(intro_text, INTRO_AUDIO_PATH)

    running = True
    frame_count = 0
    clock = pygame.time.Clock()
    max_frames = FPS * 150  # 2.5 минуты максимум

    print("🎮 Запускаем УЛУЧШЕННУЮ ПИКСЕЛЬНУЮ дуэль!")
    print("⚔️ НОВЫЕ ОСОБЕННОСТИ:")
    print("  ✅ 4 уникальных бойца с особыми способностями!")
    print("  ✅ Топор-берсерк: Рывок + неуязвимость каждые 5 сек")
    print("  ✅ Лучник: Растущее количество стрел, парирование стрел")
    print("  ✅ УЛУЧШЕННОЕ парирование: заморозка времени + эффекты")
    print("  ✅ Динамические заголовки и статистики")
    print("  ✅ Отдельные звуки для ударов и парирования")

    while running and frame_count < max_frames:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game_state.update()

        # Рендер
        screen_surface = renderer.draw(game_state)
        
        # Показываем на экране
        display_screen.blit(screen_surface, (0, 0))
        pygame.display.flip()

        # Сохранение кадра для видео
        frame_filename = os.path.join(FRAMES_DIR, f"frame_{frame_count:05d}.png")
        pygame.image.save(screen_surface, frame_filename)

        frame_count += 1
        clock.tick(FPS)

        # Показываем прогресс
        if frame_count % (FPS * 15) == 0:  # Каждые 15 секунд
            minutes = frame_count // FPS // 60
            seconds = (frame_count // FPS) % 60
            
            # Адаптивная статистика в зависимости от типа бойца
            stat1 = f"⚔️{int(ball1.weapon_length)}" if hasattr(ball1, 'weapon_length') else f"🏹{getattr(ball1, 'arrows_per_shot', 1)}"
            stat2 = f"⚔️{int(ball2.weapon_length)}" if hasattr(ball2, 'weapon_length') else f"🏹{getattr(ball2, 'arrows_per_shot', 1)}"
            
            print(f"⏱️ {minutes:02d}:{seconds:02d} | "
                  f"💚 {ball1.name}: {int(ball1.health)} ({stat1}) | "
                  f"💙 {ball2.name}: {int(ball2.health)} ({stat2}) | "
                  f"💥 Hits: {len(game_state.hit_events)} | "
                  f"✨ Parries: {len(game_state.parry_events)}")

        if game_state.winner:
            winner_ball = ball1 if game_state.winner == ball1.name else ball2
            print(f"🏆 ПОБЕДИТЕЛЬ: {game_state.winner}!")
            print(f"💪 Финальный урон: {int(winner_ball.stats['damage'])}")
            
            # Адаптивная финальная статистика
            if hasattr(winner_ball, 'weapon_length'):
                print(f"⚔️ Финальная длина оружия: {int(winner_ball.weapon_length)} пикселей!")
            elif hasattr(winner_ball, 'arrows_per_shot'):
                print(f"🏹 Финальное количество стрел: {winner_ball.arrows_per_shot} за залп!")
            
            print(f"💥 Всего ударов в бою: {len(game_state.hit_events)}")
            print(f"✨ Всего парирований: {len(game_state.parry_events)}")
            
            # Сохраняем еще 3 секунды кадров с победным экраном
            for victory_frame in range(FPS * 2):
                screen_surface = renderer.draw(game_state)
                display_screen.blit(screen_surface, (0, 0))
                pygame.display.flip()
                
                frame_filename = os.path.join(FRAMES_DIR, f"frame_{frame_count:05d}.png")
                pygame.image.save(screen_surface, frame_filename)
                frame_count += 1
                clock.tick(FPS)
            running = False

    pygame.quit()
    
    print("🎬 Компилируем финальное видео...")
    
    # Передаем как удары, так и парирования для звуков
    all_sound_events = game_state.hit_events + game_state.parry_events
    compile_video(FRAMES_DIR, INTRO_AUDIO_PATH, HIT_SOUND_PATH, all_sound_events, 
                 FINAL_VIDEO_PATH, FPS, game_state.parry_events)
    
    # Очищаем временные кадры
    if os.path.exists(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)
    
    print(f"✅ ГОТОВО! Эпическое видео с новыми бойцами: {FINAL_VIDEO_PATH}")
    print("🎥 Готово для TikTok/YouTube Shorts!")
    print(f"⚔️ Дуэль: {ball1.name} VS {ball2.name}")

if __name__ == "__main__":
    main()