# config.py

# Настройки экрана и видео (вертикальный формат для Shorts/TikTok)
WIDTH = 720
HEIGHT = 1280
FPS = 60

# Цвета (RGB)
VANILLA = (243, 229, 171) # Ванильный фон
GREY = (220, 220, 220) # Серовато-белый для арены
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

# ИСПРАВЛЕННЫЕ настройки арены - более по центру экрана
ARENA_PADDING_X = 60
ARENA_PADDING_Y = 300  # Центрируем арену по вертикали
ARENA_X = ARENA_PADDING_X
ARENA_Y = ARENA_PADDING_Y
ARENA_WIDTH = WIDTH - 2 * ARENA_PADDING_X  # 600px
ARENA_HEIGHT = 480  # Арена чуть меньше для лучшего размещения

# UI зоны для TikTok/YouTube Shorts
SAFE_ZONE_TOP = 100  # Зона сверху для UI TikTok
SAFE_ZONE_BOTTOM = 200  # Больше места снизу для статистик

# Позиции для UI элементов
TITLE_Y = 150  # Заголовок выше арены
HEALTH_BAR_TOP_Y = ARENA_Y - 50
HEALTH_BAR_BOTTOM_Y = ARENA_Y + ARENA_HEIGHT + 20
STATS_Y = ARENA_Y + ARENA_HEIGHT + 80  # Статистики ниже

# Пути
FONT_PATH = "assets/fonts/BebasNeue-Regular.ttf"
ASSETS_DIR = "assets" # Папка для звуков
OUTPUT_DIR = "output"
FRAMES_DIR = f"{OUTPUT_DIR}/frames"
FINAL_VIDEO_PATH = f"{OUTPUT_DIR}/final_video.mp4"
INTRO_AUDIO_PATH = f"{OUTPUT_DIR}/intro.mp3"

# ЗВУКОВЫЕ ФАЙЛЫ ДЛЯ COUNTRY BALLS
# Звуки оружия стран
VODKA_SOUND_PATH = "assets/sounds/vodka_throw.mp3"      # Россия - бросок бутылки
GUNSHOT_SOUND_PATH = "assets/sounds/gunshot.mp3"        # США - выстрел из револьвера
BAGUETTE_SOUND_PATH = "assets/sounds/baguette_hit.mp3"  # Франция - удар багетом
NUNCHUCK_SOUND_PATH = "assets/sounds/nunchuck_swing.mp3" # Китай - взмах нунчак
SORRY_SOUND_PATH = "assets/sounds/sorry.mp3"            # Канада - извинения
MISSILE_SOUND_PATH = "assets/sounds/missile_launch.mp3" # Северная Корея - запуск ракеты

# Эффекты
EXPLOSION_SOUND_PATH = "assets/sounds/explosion.mp3"    # Взрыв ракеты
DEFLECT_SOUND_PATH = "assets/sounds/deflect.mp3"       # Отражение пули багетом
POISON_SOUND_PATH = "assets/sounds/poison.mp3"         # Эффект отравления

# Для обратной совместимости
HIT_SOUND_PATH = "assets/sounds/hit.mp3"               # Общий звук удара
PARRY_SOUND_PATH = "assets/sounds/parry.mp3"           # Звук парирования  
WIN_SOUND_PATH = "assets/sounds/victory.mp3"           # Звук победы