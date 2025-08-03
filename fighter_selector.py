# fighter_selector.py
import pygame
import sys
from config import WIDTH, HEIGHT, VANILLA, BLACK, WHITE, GOLD

class FighterSelector:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Выберите страны для эпической дуэли!")
        
        try:
            self.font_large = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf", 80)
            self.font_medium = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf", 50)
            self.font_small = pygame.font.Font("assets/fonts/BebasNeue-Regular.ttf", 35)
        except:
            self.font_large = pygame.font.Font(None, 80)
            self.font_medium = pygame.font.Font(None, 50)
            self.font_small = pygame.font.Font(None, 35)
        
        self.fighters = {
            1: {
                'name': 'Russia',
                'color': (213, 43, 30),
                'description': 'Vodka Bottles',
                'special': 'Poison effect stacks with each hit',
                'class': 'RussiaBall',
                'sound': 'assets/sounds/vodka_throw.mp3'
            },
            2: {
                'name': 'USA', 
                'color': (178, 34, 52),
                'description': 'Revolver',
                'special': '6 bullets, 2sec reload time',
                'class': 'USABall',
                'sound': 'assets/sounds/gunshot.mp3'
            },
            3: {
                'name': 'France',
                'color': (0, 85, 164),
                'description': 'Baguette',
                'special': 'Blocks bullets, strong knockback',
                'class': 'FranceBall',
                'sound': 'assets/sounds/baguette_hit.mp3'
            },
            4: {
                'name': 'China',
                'color': (238, 28, 37),
                'description': 'Nunchucks',
                'special': 'Creates clones after hits',
                'class': 'ChinaBall',
                'sound': 'assets/sounds/nunchuck_swing.mp3'
            },
            5: {
                'name': 'Canada',
                'color': (255, 0, 0),
                'description': 'Politeness',
                'special': 'Very weak but apologetic',
                'class': 'CanadaBall',
                'sound': 'assets/sounds/sorry.mp3'
            },
            6: {
                'name': 'North Korea',
                'color': (237, 28, 36),
                'description': 'Missiles',
                'special': '15 damage explosion every 5sec',
                'class': 'NorthKoreaBall',
                'sound': 'assets/sounds/missile_launch.mp3'
            }
        }
        
        self.selected_fighter1 = None
        self.selected_fighter2 = None
        self.selection_stage = 1  # 1 = выбор первого бойца, 2 = выбор второго

    def draw_text_with_shadow(self, text, font, color, x, y, center=True):
        """Рисует текст с тенью"""
        # Тень
        shadow_surface = font.render(text, True, BLACK)
        shadow_rect = shadow_surface.get_rect()
        if center:
            shadow_rect.center = (x + 2, y + 2)
        else:
            shadow_rect.topleft = (x + 2, y + 2)
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Основной текст
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_country_flag(self, screen, country_name, x, y, size):
        """Рисует упрощенный флаг страны"""
        if country_name == 'Russia':
            # Российский флаг
            pygame.draw.rect(screen, (255, 255, 255), (x, y, size, size//3))
            pygame.draw.rect(screen, (0, 57, 166), (x, y + size//3, size, size//3))
            pygame.draw.rect(screen, (213, 43, 30), (x, y + 2*size//3, size, size//3))
        
        elif country_name == 'USA':
            # Американский флаг (упрощенно)
            stripe_height = size // 13
            for i in range(13):
                color = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
                pygame.draw.rect(screen, color, (x, y + i * stripe_height, size, stripe_height))
            # Синий квадрат
            pygame.draw.rect(screen, (60, 59, 110), (x, y, size//2, size//2))
        
        elif country_name == 'France':
            # Французский флаг
            pygame.draw.rect(screen, (0, 85, 164), (x, y, size//3, size))
            pygame.draw.rect(screen, (255, 255, 255), (x + size//3, y, size//3, size))
            pygame.draw.rect(screen, (239, 65, 53), (x + 2*size//3, y, size//3, size))
        
        elif country_name == 'China':
            # Китайский флаг
            pygame.draw.rect(screen, (238, 28, 37), (x, y, size, size))
            # Упрощенная звезда
            star_x, star_y = x + size//4, y + size//4
            pygame.draw.circle(screen, (255, 255, 0), (star_x, star_y), 8)
        
        elif country_name == 'Canada':
            # Канадский флаг
            pygame.draw.rect(screen, (255, 0, 0), (x, y, size//4, size))
            pygame.draw.rect(screen, (255, 255, 255), (x + size//4, y, size//2, size))
            pygame.draw.rect(screen, (255, 0, 0), (x + 3*size//4, y, size//4, size))
            # Упрощенный кленовый лист
            leaf_center = (x + size//2, y + size//2)
            pygame.draw.circle(screen, (255, 0, 0), leaf_center, 6)
        
        elif country_name == 'North Korea':
            # Северокорейский флаг (упрощенно)
            pygame.draw.rect(screen, (0, 61, 165), (x, y, size, size//4))
            pygame.draw.rect(screen, (255, 255, 255), (x, y + size//4, size, size//8))
            pygame.draw.rect(screen, (237, 28, 36), (x, y + 3*size//8, size, size//4))
            pygame.draw.rect(screen, (255, 255, 255), (x, y + 5*size//8, size, size//8))
            pygame.draw.rect(screen, (0, 61, 165), (x, y + 3*size//4, size, size//4))
            # Звезда
            pygame.draw.circle(screen, (255, 255, 255), (x + size//4, y + size//2), 6)

    def draw_fighter_card(self, fighter_id, x, y, width, height, is_selected=False, is_available=True):
        """Рисует карточку страны-бойца"""
        fighter = self.fighters[fighter_id]
        
        # Цвет рамки в зависимости от состояния
        border_color = GOLD if is_selected else WHITE
        if not is_available:
            border_color = (100, 100, 100)
        
        # Основная рамка
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, fighter['color'] if is_available else (80, 80, 80), card_rect)
        pygame.draw.rect(self.screen, border_color, card_rect, 5)
        
        # Флаг страны в уменьшенном виде
        flag_size = 60
        flag_x = x + width - flag_size - 10
        flag_y = y + 10
        self.draw_country_flag(self.screen, fighter['name'], flag_x, flag_y, flag_size)
        
        # Номер бойца
        number_text = str(fighter_id)
        self.draw_text_with_shadow(number_text, self.font_large, WHITE, x + 30, y + 30, False)
        
        # Имя страны
        name_color = WHITE if is_available else (150, 150, 150)
        self.draw_text_with_shadow(fighter['name'], self.font_medium, name_color, 
                                   x + width//2, y + 60, True)
        
        # Описание оружия
        desc_color = (220, 220, 220) if is_available else (120, 120, 120)
        self.draw_text_with_shadow(fighter['description'], self.font_small, desc_color,
                                   x + width//2, y + 110, True)
        
        # Особенность
        special_color = GOLD if is_available else (150, 120, 80)
        special_lines = self.wrap_text(fighter['special'], self.font_small, width - 20)
        for i, line in enumerate(special_lines):
            self.draw_text_with_shadow(line, self.font_small, special_color,
                                       x + width//2, y + 150 + i*30, True)

    def wrap_text(self, text, font, max_width):
        """Переносит текст на несколько строк"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def draw_selection_screen(self):
        """Рисует экран выбора"""
        # Градиентный фон
        for y in range(HEIGHT):
            color_ratio = y / HEIGHT
            r = int(243 * (1 - color_ratio) + 200 * color_ratio)
            g = int(229 * (1 - color_ratio) + 220 * color_ratio)
            b = int(171 * (1 - color_ratio) + 180 * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Заголовок
        if self.selection_stage == 1:
            title = "ВЫБЕРИТЕ ПЕРВУЮ СТРАНУ"
            subtitle = "Нажмите цифру 1-6"
        else:
            title = "ВЫБЕРИТЕ ВТОРУЮ СТРАНУ"
            subtitle = f"Первая страна: {self.fighters[self.selected_fighter1]['name']}"
        
        self.draw_text_with_shadow(title, self.font_large, BLACK, WIDTH//2, 80, True)
        self.draw_text_with_shadow(subtitle, self.font_medium, (100, 100, 100), WIDTH//2, 140, True)
        
        # Карточки стран (3x2 сетка)
        card_width = 220
        card_height = 250
        spacing = 30
        start_x = (WIDTH - 3 * card_width - 2 * spacing) // 2
        start_y = 200
        
        positions = [
            (start_x, start_y),                                                    # 1
            (start_x + card_width + spacing, start_y),                           # 2
            (start_x + 2 * (card_width + spacing), start_y),                     # 3
            (start_x, start_y + card_height + spacing),                          # 4
            (start_x + card_width + spacing, start_y + card_height + spacing),   # 5
            (start_x + 2 * (card_width + spacing), start_y + card_height + spacing)  # 6
        ]
        
        for i, (x, y) in enumerate(positions):
            fighter_id = i + 1
            is_available = (self.selection_stage == 1 or fighter_id != self.selected_fighter1)
            self.draw_fighter_card(fighter_id, x, y, card_width, card_height, 
                                 False, is_available)
        
        # Инструкции
        if self.selection_stage == 1:
            instruction = "Нажмите цифру от 1 до 6 для выбора страны"
        else:
            instruction = "Выберите вторую страну (не может быть такой же как первая)"
        
        self.draw_text_with_shadow(instruction, self.font_small, BLACK, 
                                   WIDTH//2, HEIGHT - 100, True)
        
        # ESC для выхода
        self.draw_text_with_shadow("ESC - Выход", self.font_small, (100, 100, 100),
                                   50, HEIGHT - 50, False)

    def select_fighters(self):
        """Основной цикл выбора бойцов"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    
                    # Выбор бойца по цифрам
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                        choice = event.key - pygame.K_0  # Преобразуем в число
                        
                        if self.selection_stage == 1:
                            self.selected_fighter1 = choice
                            self.selection_stage = 2
                        else:
                            if choice != self.selected_fighter1:
                                self.selected_fighter2 = choice
                                return self.selected_fighter1, self.selected_fighter2
                            # Если выбрал ту же страну - игнорируем
            
            self.draw_selection_screen()
            pygame.display.flip()
            clock.tick(60)
        
        return None, None

def get_fighter_classes():
    """Возвращает словарь классов стран-бойцов"""
    from balls.russia_ball import RussiaBall
    from balls.usa_ball import USABall  
    from balls.france_ball import FranceBall
    from balls.china_ball import ChinaBall
    from balls.canada_ball import CanadaBall
    from balls.north_korea_ball import NorthKoreaBall
    
    return {
        'RussiaBall': RussiaBall,
        'USABall': USABall,
        'FranceBall': FranceBall,
        'ChinaBall': ChinaBall,
        'CanadaBall': CanadaBall,
        'NorthKoreaBall': NorthKoreaBall
    }