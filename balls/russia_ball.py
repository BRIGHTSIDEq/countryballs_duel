# balls/russia_ball.py
from .base_fighter import FightingBall
import pygame
import math
import random

class RussiaBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255), 
                         name="Russia", weapon_type="vodka")
        
        self.stats = {'damage': 5, 'range': 150, 'speed': 3, 'radius': self.radius}
        
        # Параметры бутылки водки
        self.bottle_cooldown = 0
        self.bottle_cooldown_max = 120  # 2 секунды между бросками
        
        # Брошенные бутылки
        self.bottles = []
        
        # Эффект отравления цели
        self.poison_target = None
        self.poison_level = 0  # Уровень отравления
        self.poison_timer = 0   # Таймер для сброса отравления
        self.poison_reset_time = 420  # 7 секунд без попаданий

    def throw_bottle(self, target):
        """Бросает бутылку водки в цель"""
        if self.bottle_cooldown <= 0:
            # Направление к цели
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Создаем бутылку
                bottle_speed = 8
                bottle = {
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vx': (dx / distance) * bottle_speed,
                    'vy': (dy / distance) * bottle_speed,
                    'rotation': 0,
                    'lifetime': 300  # 5 секунд полета
                }
                self.bottles.append(bottle)
                self.bottle_cooldown = self.bottle_cooldown_max
                return True
        return False

    def update_bottles(self, target):
        """Обновляет полет бутылок и проверяет попадания"""
        for bottle in self.bottles[:]:  # Копируем список для безопасного удаления
            # Обновляем позицию
            bottle['x'] += bottle['vx']
            bottle['y'] += bottle['vy']
            bottle['vy'] += 0.3  # Гравитация
            bottle['rotation'] += 15  # Вращение бутылки
            bottle['lifetime'] -= 1
            
            # Проверка попадания в цель
            bottle_rect = pygame.Rect(bottle['x'] - 10, bottle['y'] - 15, 20, 30)
            if bottle_rect.colliderect(target.rect):
                self.apply_poison(target)
                self.bottles.remove(bottle)
                continue
            
            # Проверка на выход за границы или время жизни
            from config import ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT
            if (bottle['x'] < ARENA_X or bottle['x'] > ARENA_X + ARENA_WIDTH or
                bottle['y'] < ARENA_Y or bottle['y'] > ARENA_Y + ARENA_HEIGHT or
                bottle['lifetime'] <= 0):
                self.bottles.remove(bottle)

    def apply_poison(self, target):
        """Применяет эффект отравления к цели"""
        self.poison_target = target
        self.poison_level = min(5, self.poison_level + 1)  # Максимум 5 уровней
        self.poison_timer = self.poison_reset_time
        
        # Немедленный урон
        target.take_damage(self.stats['damage'] + self.poison_level)
        
        # Уменьшаем скорость цели
        poison_slowdown = 0.9 - (self.poison_level * 0.1)
        target.max_speed *= poison_slowdown

    def update_poison_effects(self):
        """Обновляет эффекты отравления"""
        if self.poison_target and self.poison_level > 0:
            self.poison_timer -= 1
            
            # Постепенный урон от яда каждые 0.5 секунд
            if self.poison_timer % 30 == 0:
                self.poison_target.take_damage(self.poison_level * 0.5)
            
            # Сброс отравления если долго не попадали
            if self.poison_timer <= 0:
                self.poison_level = 0
                self.poison_target = None

    def update(self, other_ball=None):
        # Обновляем кулдаун бутылки
        if self.bottle_cooldown > 0:
            self.bottle_cooldown -= 1
        
        # Автоматически бросаем бутылку
        if other_ball and self.bottle_cooldown <= 0:
            distance = math.sqrt((other_ball.rect.centerx - self.rect.centerx)**2 + 
                               (other_ball.rect.centery - self.rect.centery)**2)
            if distance < 300:  # В пределах досягаемости
                self.throw_bottle(other_ball)
        
        # Обновляем бутылки
        if other_ball:
            self.update_bottles(other_ball)
        
        # Обновляем эффекты отравления
        self.update_poison_effects()
        
        # Базовое обновление
        super().update(other_ball)

    def draw_flag_pattern(self, screen):
        """Рисует российский флаг на шарике"""
        center_x, center_y = self.rect.center
        
        # Белая полоса (верх)
        white_rect = pygame.Rect(center_x - self.radius, center_y - self.radius, 
                                self.radius * 2, self.radius * 2 // 3)
        pygame.draw.rect(screen, (255, 255, 255), white_rect)
        
        # Синяя полоса (средняя)
        blue_rect = pygame.Rect(center_x - self.radius, center_y - self.radius // 3, 
                               self.radius * 2, self.radius * 2 // 3)
        pygame.draw.rect(screen, (0, 57, 166), blue_rect)
        
        # Красная полоса (нижняя)
        red_rect = pygame.Rect(center_x - self.radius, center_y + self.radius // 3, 
                              self.radius * 2, self.radius * 2 // 3)
        pygame.draw.rect(screen, (213, 43, 30), red_rect)
        
        # Обрезаем по кругу
        mask_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (self.radius, self.radius), self.radius)
        
        flag_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        flag_surface.blit(screen.subsurface(pygame.Rect(center_x - self.radius, center_y - self.radius, 
                                                       self.radius * 2, self.radius * 2)), (0, 0))
        
        # Рисуем круглый флаг
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y - self.radius//3), self.radius)
        pygame.draw.circle(screen, (0, 57, 166), (center_x, center_y), self.radius)  
        pygame.draw.circle(screen, (213, 43, 30), (center_x, center_y + self.radius//3), self.radius)
        
        # Финальная обрезка кругом
        pygame.draw.circle(screen, (255, 255, 255), center_x, center_y, self.radius, 0)
        pygame.draw.circle(screen, (0, 57, 166), (center_x, center_y), self.radius)
        pygame.draw.circle(screen, (213, 43, 30), (center_x, center_y), self.radius)

    def draw_vodka_bottle(self, screen, x, y, rotation=0):
        """Рисует бутылку водки"""
        # Основное тело бутылки (темно-зеленое стекло)
        bottle_points = [
            (x - 6, y + 15),  # низ
            (x + 6, y + 15),  # низ
            (x + 5, y - 10),  # плечики
            (x + 3, y - 12),  # горлышко
            (x + 3, y - 15),  # верх горлышка
            (x - 3, y - 15), # верх горлышка
            (x - 3, y - 12), # горлышко
            (x - 5, y - 10)  # плечики
        ]
        
        # Поворачиваем точки
        if rotation != 0:
            cos_r = math.cos(math.radians(rotation))
            sin_r = math.sin(math.radians(rotation))
            rotated_points = []
            for px, py in bottle_points:
                rx = x + (px - x) * cos_r - (py - y) * sin_r
                ry = y + (px - x) * sin_r + (py - y) * cos_r
                rotated_points.append((rx, ry))
            bottle_points = rotated_points
        
        # Рисуем бутылку
        pygame.draw.polygon(screen, (40, 80, 40), bottle_points)  # Темно-зеленое стекло
        pygame.draw.polygon(screen, (20, 40, 20), bottle_points, 2)  # Контур
        
        # Этикетка
        if rotation == 0:
            label_rect = pygame.Rect(x - 4, y - 5, 8, 10)
            pygame.draw.rect(screen, (255, 255, 255), label_rect)
            pygame.draw.rect(screen, (200, 0, 0), label_rect, 1)
            
            # Надпись "VODKA"
            font = pygame.font.Font(None, 12)
            text = font.render("V", True, (200, 0, 0))
            screen.blit(text, (x - 3, y - 3))
        
        # Пробка
        cork_x = x - 2 if rotation == 0 else x
        cork_y = y - 16 if rotation == 0 else y - 16
        pygame.draw.rect(screen, (139, 69, 19), (cork_x, cork_y, 4, 3))

    def draw_bottles(self, screen):
        """Рисует все летящие бутылки"""
        for bottle in self.bottles:
            self.draw_vodka_bottle(screen, int(bottle['x']), int(bottle['y']), bottle['rotation'])

    def draw_poison_effects(self, screen):
        """Рисует эффекты отравления на цели"""
        if self.poison_target and self.poison_level > 0:
            target_center = self.poison_target.rect.center
            
            # Зеленоватый дым вокруг отравленной цели
            for i in range(self.poison_level * 2):
                angle = (pygame.time.get_ticks() * 2 + i * 60) % 360
                distance = self.poison_target.radius + 10 + math.sin(math.radians(angle * 3)) * 5
                
                smoke_x = target_center[0] + distance * math.cos(math.radians(angle))
                smoke_y = target_center[1] + distance * math.sin(math.radians(angle))
                
                alpha = 80 + int(40 * math.sin(math.radians(angle * 2)))
                smoke_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surface, (0, 150, 0, alpha), (4, 4), 4)
                screen.blit(smoke_surface, (smoke_x - 4, smoke_y - 4))

    def draw(self, screen):
        # Рисуем российский флаг как тело шарика
        center_x, center_y = self.rect.center
        
        # Белая полоса
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius)
        
        # Синяя полоса (средняя треть)
        blue_points = []
        for angle in range(0, 360, 5):
            if 60 <= angle <= 240:  # Средняя треть по вертикали
                x = center_x + self.radius * math.cos(math.radians(angle))
                y = center_y + self.radius * math.sin(math.radians(angle))
                blue_points.append((x, y))
        
        if len(blue_points) > 2:
            pygame.draw.polygon(screen, (0, 57, 166), blue_points)
        
        # Красная полоса (нижняя треть)
        red_points = []
        for angle in range(0, 360, 5):
            if 120 <= angle <= 300:  # Нижняя треть
                x = center_x + self.radius * math.cos(math.radians(angle))
                y = center_y + self.radius * math.sin(math.radians(angle))
                red_points.append((x, y))
        
        if len(red_points) > 2:
            pygame.draw.polygon(screen, (213, 43, 30), red_points)
        
        # Контур шарика
        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), self.radius, 3)
        
        # Рисуем летящие бутылки
        self.draw_bottles(screen)
        
        # Рисуем эффекты отравления
        self.draw_poison_effects(screen)
        
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
        # Увеличиваем эффективность бутылок
        self.stats['damage'] += 1.0
        self.bottle_cooldown_max = max(60, self.bottle_cooldown_max - 5)  # Быстрее кидает