# balls/russia_ball.py - ОБНОВЛЕННАЯ ВЕРСИЯ
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
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                bottle_speed = 8
                bottle = {
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vx': (dx / distance) * bottle_speed,
                    'vy': (dy / distance) * bottle_speed,
                    'rotation': 0,
                    'lifetime': 300
                }
                self.bottles.append(bottle)
                self.bottle_cooldown = self.bottle_cooldown_max
                return True
        return False

    def update_bottles(self, target):
        """Обновляет полет бутылок и проверяет попадания"""
        for bottle in self.bottles[:]:
            bottle['x'] += bottle['vx']
            bottle['y'] += bottle['vy']
            bottle['vy'] += 0.3  # Гравитация
            bottle['rotation'] += 15  # Вращение бутылки
            bottle['lifetime'] -= 1

            bottle_rect = pygame.Rect(bottle['x'] - 10, bottle['y'] - 20, 20, 40)
            if bottle_rect.colliderect(target.rect):
                self.apply_poison(target)
                self.bottles.remove(bottle)
                continue

            from config import ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT
            if (bottle.get('y', 0) > ARENA_Y + ARENA_HEIGHT or
                bottle.get('lifetime', 0) <= 0):
                if bottle in self.bottles:
                    self.bottles.remove(bottle)


    def apply_poison(self, target):
        """Применяет эффект отравления к цели"""
        self.poison_target = target
        self.poison_level = min(5, self.poison_level + 1)
        self.poison_timer = self.poison_reset_time
        target.take_damage(self.stats['damage'] + self.poison_level)

        poison_slowdown = 0.9 - (self.poison_level * 0.1)
        target.max_speed = max(1, target.max_speed * poison_slowdown)


    def update_poison_effects(self):
        """Обновляет эффекты отравления"""
        if self.poison_target and self.poison_level > 0:
            self.poison_timer -= 1
            if self.poison_timer % 30 == 0:
                self.poison_target.take_damage(self.poison_level * 0.5)
            if self.poison_timer <= 0:
                self.poison_target.max_speed = self.poison_target.original_speed
                self.poison_level = 0
                self.poison_target = None

    def update(self, other_ball=None):
        if self.bottle_cooldown > 0:
            self.bottle_cooldown -= 1

        if other_ball and self.bottle_cooldown <= 0:
            distance = math.hypot(other_ball.rect.centerx - self.rect.centerx,
                                  other_ball.rect.centery - self.rect.centery)
            if distance < 300:
                self.throw_bottle(other_ball)

        if other_ball:
            self.update_bottles(other_ball)
        self.update_poison_effects()
        super().update(other_ball)

    def draw_flag_pattern(self, screen):
        """Рисует правильный российский флаг на шарике с помощью маски"""
        center_x, center_y = self.rect.center
        radius = self.radius

        # Создаем временную поверхность для флага
        flag_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        stripe_height = (radius * 2) / 3

        # Рисуем полосы флага
        pygame.draw.rect(flag_surface, (255, 255, 255), (0, 0, radius * 2, stripe_height))
        pygame.draw.rect(flag_surface, (0, 57, 166), (0, stripe_height, radius * 2, stripe_height))
        pygame.draw.rect(flag_surface, (213, 43, 30), (0, stripe_height * 2, radius * 2, stripe_height))

        # Создаем круглую маску
        mask_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (radius, radius), radius)

        # Применяем маску к флагу (вырезаем круг из прямоугольного флага)
        flag_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Отображаем готовый флаг на экране
        screen.blit(flag_surface, (center_x - radius, center_y - radius))


    def draw_vodka_bottle(self, screen, x, y, rotation=0):
        """Рисует более крупную и детализированную бутылку водки"""
        bottle_height = 40
        bottle_width = 12

        # Создаем поверхность для бутылки, чтобы вращение было корректным
        bottle_surf = pygame.Surface((bottle_width + 10, bottle_height + 10), pygame.SRCALPHA)
        surf_center_x, surf_center_y = (bottle_width + 10) // 2, (bottle_height + 10) // 2

        # Тело бутылки
        body_rect = pygame.Rect(surf_center_x - bottle_width//2, surf_center_y - bottle_height//2 + 5, bottle_width, bottle_height - 10)
        pygame.draw.rect(bottle_surf, (30, 70, 30), body_rect) # Темно-зеленое стекло

        # Горлышко
        neck_points = [
            (surf_center_x - 3, surf_center_y - bottle_height//2 + 5),
            (surf_center_x + 3, surf_center_y - bottle_height//2 + 5),
            (surf_center_x + 2, surf_center_y - bottle_height//2 - 2),
            (surf_center_x - 2, surf_center_y - bottle_height//2 - 2),
        ]
        pygame.draw.polygon(bottle_surf, (40, 80, 40), neck_points)

        # Этикетка
        label_rect = pygame.Rect(surf_center_x - 5, surf_center_y - 5, 10, 12)
        pygame.draw.rect(bottle_surf, (250, 250, 240), label_rect)
        pygame.draw.rect(bottle_surf, (200, 0, 0), label_rect, 1) # Красная рамка

        # Пробка
        cork_rect = pygame.Rect(surf_center_x - 3, surf_center_y - bottle_height//2 - 5, 6, 3)
        pygame.draw.rect(bottle_surf, (150, 150, 150), cork_rect)

        # Вращение и отображение
        rotated_bottle = pygame.transform.rotate(bottle_surf, -rotation)
        new_rect = rotated_bottle.get_rect(center=(x, y))
        screen.blit(rotated_bottle, new_rect)


    def draw_bottles(self, screen):
        """Рисует все летящие бутылки"""
        for bottle in self.bottles:
            self.draw_vodka_bottle(screen, int(bottle['x']), int(bottle['y']), bottle['rotation'])

    def draw_poison_effects(self, screen):
        """Рисует эффекты отравления на цели"""
        if self.poison_target and self.poison_level > 0:
            target_center = self.poison_target.rect.center
            for i in range(self.poison_level * 3):
                angle = (pygame.time.get_ticks() * 0.1 * (i+1)) % 360
                distance = self.poison_target.radius + 8 + math.sin(math.radians(angle * 4)) * 4
                smoke_x = target_center[0] + distance * math.cos(math.radians(angle))
                smoke_y = target_center[1] + distance * math.sin(math.radians(angle))
                alpha = 60 + int(30 * math.sin(math.radians(pygame.time.get_ticks()*0.2 + i*20)))
                pygame.draw.circle(screen, (0, 150, 0, alpha), (smoke_x, smoke_y), 3)

    def draw(self, screen):
        """Основная функция отрисовки"""
        # Рисуем флаг
        self.draw_flag_pattern(screen)
        # Контур шарика
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.radius, 3)

        self.draw_bottles(screen)
        self.draw_poison_effects(screen)

        # Здоровье
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
        self.stats['damage'] += 1.0
        self.bottle_cooldown_max = max(60, self.bottle_cooldown_max - 5)