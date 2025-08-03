# balls/china_ball.py
from .base_fighter import FightingBall
import pygame
import math
import random

class ChinaBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255), 
                         name="China", weapon_type="nunchucks")
        
        self.stats = {'damage': 6, 'range': 70, 'speed': 5, 'radius': self.radius}
        
        # Параметры нунчак
        self.nunchuck_length = 40
        self.nunchuck_angle1 = 0
        self.nunchuck_angle2 = 45
        self.nunchuck_speed = 8
        
        # Система клонирования
        self.hits_to_clone = 5  # Изначально нужно 5 ударов
        self.current_hits = 0
        self.clones = []  # Список клонов
        self.max_clones = 3  # Максимум клонов
        
        # Анимация нунчак
        self.nunchuck_animation_timer = 0
        
        # Для клонов
        self.is_clone = False
        self.clone_alpha = 255  # Прозрачность клона
        self.parent = None  # Ссылка на родителя для клонов

    def create_clone(self):
        """Создает клона"""
        if len(self.clones) >= self.max_clones:
            return None
        
        # Позиция клона рядом с оригиналом
        angle = random.uniform(0, 360)
        distance = 80
        clone_x = self.rect.centerx + distance * math.cos(math.radians(angle))
        clone_y = self.rect.centery + distance * math.sin(math.radians(angle))
        
        # Ограничиваем позицию клона аренойPYTHON_ARGCOMPLETE_OK
        from config import ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT
        clone_x = max(ARENA_X + 50, min(ARENA_X + ARENA_WIDTH - 50, clone_x))
        clone_y = max(ARENA_Y + 50, min(ARENA_Y + ARENA_HEIGHT - 50, clone_y))
        
        # Создаем клона
        clone = ChinaBall(clone_x, clone_y)
        clone.is_clone = True
        clone.clone_alpha = 200  # Клоны более прозрачные
        clone.parent = self
        clone.health = self.health // 2  # У клонов меньше здоровья
        clone.max_health = clone.health
        clone.hits_to_clone = max(3, self.hits_to_clone - 1)  # Клонам нужно меньше ударов
        
        # Клоны наследуют характеристики
        clone.stats = self.stats.copy()
        clone.nunchuck_length = self.nunchuck_length
        
        self.clones.append(clone)
        return clone

    def update_clones(self, target):
        """Обновляет всех клонов"""
        for clone in self.clones[:]:  # Копируем список для безопасного удаления
            if clone.health <= 0:
                self.clones.remove(clone)
                continue
            
            clone.update(target)
            
            # Клоны тоже могут атаковать
            if target and clone.can_attack():
                clone_weapon_rect = clone.get_weapon_rect()
                if clone_weapon_rect.colliderect(target.rect):
                    clone.attack(target)

    def get_weapon_rect(self):
        """Возвращает область нунчак"""
        center_x, center_y = self.rect.center
        
        # Первая часть нунчак
        end1_x = center_x + (self.radius + self.nunchuck_length) * math.cos(math.radians(self.nunchuck_angle1))
        end1_y = center_y + (self.radius + self.nunchuck_length) * math.sin(math.radians(self.nunchuck_angle1))
        
        # Вторая часть нунчак
        end2_x = end1_x + self.nunchuck_length * math.cos(math.radians(self.nunchuck_angle2))
        end2_y = end1_y + self.nunchuck_length * math.sin(math.radians(self.nunchuck_angle2))
        
        # Объединяем область обеих частей
        all_x = [center_x, end1_x, end2_x]
        all_y = [center_y, end1_y, end2_y]
        
        min_x = min(all_x) - 10
        max_x = max(all_x) + 10
        min_y = min(all_y) - 10
        max_y = max(all_y) + 10
        
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def update(self, other_ball=None):
        # Анимация нунчак
        self.nunchuck_animation_timer += 1
        self.nunchuck_angle1 += self.nunchuck_speed
        self.nunchuck_angle2 = self.nunchuck_angle1 + 45 + 30 * math.sin(self.nunchuck_animation_timer * 0.2)
        
        if self.nunchuck_angle1 >= 360:
            self.nunchuck_angle1 -= 360
        
        # Обновляем клонов (только если это оригинал)
        if not self.is_clone and other_ball:
            self.update_clones(other_ball)
        
        # Базовое обновление
        super().update(other_ball)

    def attack(self, target):
        """Переопределяем атаку для системы клонирования"""
        success = super().attack(target)
        
        if success and not self.is_clone:  # Только оригинал создает клонов
            self.current_hits += 1
            
            if self.current_hits >= self.hits_to_clone:
                self.create_clone()
                self.current_hits = 0
                # Увеличиваем требования для следующего клона
                self.hits_to_clone = min(8, self.hits_to_clone + 1)
        
        return success

    def draw_nunchucks(self, screen):
        """Рисует нунчаки"""
        center_x, center_y = self.rect.center
        
        # Начальная точка (у шарика)
        start_x = center_x + self.radius * math.cos(math.radians(self.nunchuck_angle1))
        start_y = center_y + self.radius * math.sin(math.radians(self.nunchuck_angle1))
        
        # Конец первой части
        end1_x = center_x + (self.radius + self.nunchuck_length) * math.cos(math.radians(self.nunchuck_angle1))
        end1_y = center_y + (self.radius + self.nunchuck_length) * math.sin(math.radians(self.nunchuck_angle1))
        
        # Конец второй части
        end2_x = end1_x + self.nunchuck_length * math.cos(math.radians(self.nunchuck_angle2))
        end2_y = end1_y + self.nunchuck_length * math.sin(math.radians(self.nunchuck_angle2))
        
        # Рисуем первую палку
        pygame.draw.line(screen, (101, 67, 33), (start_x, start_y), (end1_x, end1_y), 6)  # Дерево
        pygame.draw.line(screen, (60, 40, 20), (start_x, start_y), (end1_x, end1_y), 2)   # Контур
        
        # Рисуем вторую палку
        pygame.draw.line(screen, (101, 67, 33), (end1_x, end1_y), (end2_x, end2_y), 6)
        pygame.draw.line(screen, (60, 40, 20), (end1_x, end1_y), (end2_x, end2_y), 2)
        
        # Цепочка между палками
        chain_segments = 3
        for i in range(chain_segments + 1):
            progress = i / chain_segments
            chain_x = end1_x + (end1_x - end1_x) * progress * 0.1  # Небольшое провисание
            chain_y = end1_y + (end1_y - end1_y) * progress * 0.1 + 3 * math.sin(progress * math.pi)
            
            pygame.draw.circle(screen, (150, 150, 150), (int(chain_x), int(chain_y)), 2)
        
        # Рукоятки на концах
        pygame.draw.circle(screen, (80, 50, 30), (int(start_x), int(start_y)), 4)
        pygame.draw.circle(screen, (80, 50, 30), (int(end2_x), int(end2_y)), 4)
        
        # Эффект движения нунчак
        if abs(self.nunchuck_speed) > 5:
            # След от быстрого движения
            trail_alpha = 100
            trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (255, 255, 0, trail_alpha), (2, 2), 2)
            screen.blit(trail_surface, (end2_x - 2, end2_y - 2))

    def draw_clones(self, screen):
        """Рисует всех клонов"""
        for clone in self.clones:
            clone.draw(screen)

    def draw_stars(self, screen, center_x, center_y):
        """Рисует звезды на китайском флаге"""
        # Большая звезда
        big_star_x = center_x - self.radius // 2
        big_star_y = center_y - self.radius // 2
        self.draw_star(screen, big_star_x, big_star_y, 8, (255, 255, 0))
        
        # Четыре маленькие звезды
        small_positions = [
            (center_x - self.radius // 4, center_y - self.radius // 3),
            (center_x - self.radius // 6, center_y - self.radius // 6),
            (center_x - self.radius // 6, center_y + self.radius // 6),
            (center_x - self.radius // 4, center_y + self.radius // 3)
        ]
        
        for star_x, star_y in small_positions:
            self.draw_star(screen, star_x, star_y, 4, (255, 255, 0))

    def draw_star(self, screen, x, y, size, color):
        """Рисует пятиконечную звезду"""
        points = []
        for i in range(10):
            angle = math.pi * i / 5 - math.pi / 2
            if i % 2 == 0:
                radius = size
            else:
                radius = size * 0.4
            
            point_x = x + radius * math.cos(angle)
            point_y = y + radius * math.sin(angle)
            points.append((point_x, point_y))
        
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (200, 200, 0), points, 1)

    def draw(self, screen):
        # Применяем прозрачность для клонов
        if self.is_clone and self.clone_alpha < 255:
            # Создаем полупрозрачную поверхность для клона
            clone_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            
            # Рисуем на отдельной поверхности
            clone_center = (self.radius, self.radius)
            
            # Китайский флаг
            pygame.draw.circle(clone_surface, (238, 28, 37), clone_center, self.radius)
            
            # Звезды на клоне
            big_star_x = clone_center[0] - self.radius // 2
            big_star_y = clone_center[1] - self.radius // 2
            self.draw_star(clone_surface, big_star_x, big_star_y, 6, (255, 255, 0))
            
            # Применяем прозрачность
            clone_surface.set_alpha(self.clone_alpha)
            screen.blit(clone_surface, (self.rect.x, self.rect.y))
        else:
            # Обычное рисование для оригинала
            center_x, center_y = self.rect.center
            
            # Китайский флаг (красный фон)
            pygame.draw.circle(screen, (238, 28, 37), (center_x, center_y), self.radius)
            
            # Звезды
            self.draw_stars(screen, center_x, center_y)
        
        # Контур шарика
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.radius, 3)
        
        # Рисуем нунчаки
        self.draw_nunchucks(screen)
        
        # Рисуем клонов (только если это оригинал)
        if not self.is_clone:
            self.draw_clones(screen)
        
        # Здоровье
        if self.health > 0:
            health_text = f"{int(self.health)}"
            font = pygame.font.Font(None, 28)
            text_surface = font.render(health_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            
            shadow_surface = font.render(health_text, True, (0, 0, 0))
            shadow_rect = text_surface.get_rect(center=(self.rect.center[0] + 2, self.rect.center[1] + 2))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)

    def on_successful_attack(self, target):
        # Увеличиваем скорость нунчак
        self.stats['damage'] += 1.5
        self.nunchuck_speed = min(15, self.nunchuck_speed + 1)
        self.nunchuck_length += 3