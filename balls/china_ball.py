# balls/china_ball.py - ОБНОВЛЕННАЯ ВЕРСИЯ (БАЛАНС)
from .base_fighter import FightingBall
import pygame
import math
import random

class ChinaBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255),
                         name="China", weapon_type="nunchucks")

        # ИЗМЕНЕНИЕ: Урон снижен с 6 до 4 для баланса
        self.stats = {'damage': 3, 'range': 70, 'speed': 5, 'radius': self.radius}

        # Параметры нунчак
        self.nunchuck_length = 45
        self.nunchuck_angle1 = 0
        self.nunchuck_angle2 = 45
        self.nunchuck_speed = 8
        self.nunchuck_animation_timer = 0

        # Система клонирования
        self.hits_to_clone = 5
        self.current_hits = 0
        self.clones = []
        self.max_clones = 3
        self.is_clone = False
        self.clone_alpha = 255
        self.parent = None

    def create_clone(self):
        """Создает клона"""
        if len(self.clones) >= self.max_clones: return None
        
        angle = random.uniform(0, 2 * math.pi)
        clone_x = self.rect.centerx + 80 * math.cos(angle)
        clone_y = self.rect.centery + 80 * math.sin(angle)
        
        clone = ChinaBall(clone_x, clone_y)
        clone.is_clone = True
        clone.clone_alpha = 180
        clone.parent = self
        # ИЗМЕНЕНИЕ: Здоровье клонов теперь фиксировано на 20
        clone.health = 20
        clone.max_health = 20
        clone.stats = self.stats.copy()
        self.clones.append(clone)
        return clone

    def update_clones(self, target):
        """Обновляет всех клонов"""
        for clone in self.clones[:]:
            if clone.health <= 0:
                self.clones.remove(clone)
                continue
            clone.update(target)
            if target and clone.can_attack() and clone.get_weapon_rect().colliderect(target.rect):
                clone.attack(target)

    def get_weapon_rect(self):
        """Возвращает область нунчак"""
        return self.rect.inflate(self.nunchuck_length * 2, self.nunchuck_length * 2)

    def update(self, other_ball=None):
        self.nunchuck_animation_timer += 1
        self.nunchuck_angle1 = (self.nunchuck_angle1 + self.nunchuck_speed) % 360
        self.nunchuck_angle2 = self.nunchuck_angle1 + 45 + 30 * math.sin(self.nunchuck_animation_timer * 0.1)

        if not self.is_clone and other_ball:
            self.update_clones(other_ball)
        super().update(other_ball)

    def attack(self, target):
        """Переопределяем атаку для системы клонирования"""
        success = super().attack(target)
        if success and not self.is_clone:
            self.current_hits += 1
            if self.current_hits >= self.hits_to_clone:
                self.create_clone()
                self.current_hits = 0
                self.hits_to_clone = min(8, self.hits_to_clone + 1)
        return success

    def draw_star(self, screen, center_x, center_y, size, angle=0, color=(255, 255, 0)):
        """Рисует пятиконечную звезду с возможностью поворота"""
        points = []
        angle_rad = math.radians(angle)
        for i in range(5):
            outer_angle = angle_rad + i * 2 * math.pi / 5
            points.append((center_x + size * math.cos(outer_angle), center_y + size * math.sin(outer_angle)))
            inner_angle = outer_angle + math.pi / 5
            points.append((center_x + size/2 * math.cos(inner_angle), center_y + size/2 * math.sin(inner_angle)))
        pygame.draw.polygon(screen, color, points)

    def draw_flag_pattern(self, screen, surface_to_draw, center, radius):
        """Рисует правильный флаг Китая"""
        pygame.draw.circle(surface_to_draw, (222, 41, 16), center, radius)
        main_star_pos = (center[0] - radius * 0.5, center[1] - radius * 0.5)
        self.draw_star(surface_to_draw, main_star_pos[0], main_star_pos[1], radius * 0.2, -90)
        small_star_size = radius * 0.07
        small_star_positions = [
            (center[0] - radius * 0.2, center[1] - radius * 0.7),
            (center[0],             center[1] - radius * 0.5),
            (center[0],             center[1] - radius * 0.2),
            (center[0] - radius * 0.2, center[1] - radius * 0.0)
        ]
        for i, pos in enumerate(small_star_positions):
            angle_to_main = math.degrees(math.atan2(main_star_pos[1] - pos[1], main_star_pos[0] - pos[0]))
            self.draw_star(surface_to_draw, pos[0], pos[1], small_star_size, angle_to_main)

    def draw_nunchucks(self, screen):
        """Рисует детализированные нунчаки"""
        center_x, center_y = self.rect.center
        start1_x = center_x + self.radius * math.cos(math.radians(self.nunchuck_angle1))
        start1_y = center_y + self.radius * math.sin(math.radians(self.nunchuck_angle1))
        end1_x = center_x + (self.radius + self.nunchuck_length) * math.cos(math.radians(self.nunchuck_angle1))
        end1_y = center_y + (self.radius + self.nunchuck_length) * math.sin(math.radians(self.nunchuck_angle1))
        end2_x = end1_x + self.nunchuck_length * math.cos(math.radians(self.nunchuck_angle2))
        end2_y = end1_y + self.nunchuck_length * math.sin(math.radians(self.nunchuck_angle2))
        pygame.draw.line(screen, (139, 69, 19), (start1_x, start1_y), (end1_x, end1_y), 8)
        pygame.draw.line(screen, (101, 67, 33), (start1_x, start1_y), (end1_x, end1_y), 4)
        pygame.draw.line(screen, (139, 69, 19), (end1_x, end1_y), (end2_x, end2_y), 8)
        pygame.draw.line(screen, (101, 67, 33), (end1_x, end1_y), (end2_x, end2_y), 4)
        pygame.draw.line(screen, (100, 100, 100), (end1_x, end1_y), (end2_x, end2_y), 2)
        pygame.draw.circle(screen, (80, 80, 80), (int(end1_x), int(end1_y)), 5)
        pygame.draw.circle(screen, (80, 80, 80), (int(end2_x), int(end2_y)), 5)

    def draw_clones(self, screen):
        """Рисует всех клонов"""
        for clone in self.clones:
            clone.draw(screen)

    def draw(self, screen):
        if self.is_clone:
            clone_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            self.draw_flag_pattern(clone_surface, clone_surface, (self.radius, self.radius), self.radius)
            clone_surface.set_alpha(self.clone_alpha)
            screen.blit(clone_surface, self.rect.topleft)
        else:
            self.draw_flag_pattern(screen, screen, self.rect.center, self.radius)
        
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.radius, 3)
        self.draw_nunchucks(screen)
        
        if not self.is_clone:
            self.draw_clones(screen)
        
        if self.health > 0:
            font = pygame.font.Font(None, 28)
            health_text = f"{int(self.health)}"
            text_surface = font.render(health_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            shadow_surface = font.render(health_text, True, (0, 0, 0))
            shadow_rect = text_surface.get_rect(center=(self.rect.center[0] + 2, self.rect.center[1] + 2))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)

    def on_successful_attack(self, target):
        self.stats['damage'] += 0.5 # Ослабляем прокачку
        self.nunchuck_speed = min(15, self.nunchuck_speed + 0.5)
        self.nunchuck_length += 2