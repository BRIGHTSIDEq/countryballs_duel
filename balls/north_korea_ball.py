# balls/north_korea_ball.py - ОБНОВЛЕННАЯ ВЕРСИЯ
from .base_fighter import FightingBall
import pygame
import math
import random

class NorthKoreaBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255),
                         name="North Korea", weapon_type="missile")

        self.stats = {'damage': 20, 'range': 350, 'speed': 3, 'radius': self.radius}
        self.missile_cooldown = 0
        self.missile_cooldown_max = 120
        self.missile_damage = 20
        self.explosion_radius = 200
        self.missiles = []
        self.explosions = []

    def launch_missile(self, target):
        """Запускает ракету в цель"""
        if self.missile_cooldown <= 0:
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                accuracy = random.uniform(-0.1, 0.1)
                angle = math.atan2(dy, dx) + accuracy
                missile_speed = 6
                missile = {
                    'x': self.rect.centerx, 'y': self.rect.centery,
                    'vx': math.cos(angle) * missile_speed, 'vy': math.sin(angle) * missile_speed,
                    'lifetime': 600, 'trail': [], 'rotation': math.degrees(-angle)
                }
                self.missiles.append(missile)
                self.missile_cooldown = self.missile_cooldown_max
                return True
        return False

    def update_missiles(self, target):
        """Обновляет полет ракет"""
        for m in self.missiles[:]:
            m['x'] += m['vx']
            m['y'] += m['vy']
            m['lifetime'] -= 1
            m['trail'].append((m['x'], m['y']))
            if len(m['trail']) > 15: m['trail'].pop(0)

            if math.hypot(m['x'] - target.rect.centerx, m['y'] - target.rect.centery) < 20 or m['lifetime'] <= 0:
                self.create_explosion(m['x'], m['y'], target)
                self.missiles.remove(m)

    def create_explosion(self, x, y, target):
        """Создает взрыв"""
        self.explosions.append({'x': x, 'y': y, 'radius': 10, 'max_radius': self.explosion_radius, 'timer': 30})
        distance = math.hypot(x - target.rect.centerx, y - target.rect.centery)
        if distance < self.explosion_radius:
            ratio = 1.0 - (distance / self.explosion_radius)
            target.take_damage(self.missile_damage * ratio)
            if distance > 0:
                knockback = 15 * ratio
                dx = target.rect.centerx - x
                dy = target.rect.centery - y
                target.vx += (dx / distance) * knockback
                target.vy += (dy / distance) * knockback

    def update_explosions(self):
        """Обновляет эффекты взрывов"""
        for exp in self.explosions[:]:
            exp['timer'] -= 1
            exp['radius'] += 2
            if exp['timer'] <= 0: self.explosions.remove(exp)

    def update(self, other_ball=None):
        if self.missile_cooldown > 0: self.missile_cooldown -= 1
        
        if other_ball and self.missile_cooldown <= 0:
            if math.hypot(other_ball.rect.centerx - self.rect.centerx, other_ball.rect.centery - self.rect.centery) > 100:
                self.launch_missile(other_ball)

        if other_ball: self.update_missiles(other_ball)
        self.update_explosions()
        super().update(other_ball)

    def draw_star(self, screen, center_x, center_y, size, color):
        """Рисует пятиконечную звезду"""
        points = []
        for i in range(5):
            angle_deg = -90 + i * 72
            angle_rad = math.pi * angle_deg / 180
            points.append((center_x + size * math.cos(angle_rad), center_y + size * math.sin(angle_rad)))
        pygame.draw.polygon(screen, color, points)

    def draw_flag_pattern(self, screen):
        """Рисует правильный флаг Северной Кореи с помощью маски"""
        center_x, center_y = self.rect.center
        radius = self.radius
        
        flag_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        h = radius * 2
        # Пропорции полос (примерные): синий 1/6, белый 1/24, красный 2/3
        blue_h = h / 6
        white_h = h / 24
        red_h = h - 2 * blue_h - 2 * white_h

        # Рисуем полосы
        pygame.draw.rect(flag_surface, (11, 74, 158), (0, 0, h, blue_h))
        pygame.draw.rect(flag_surface, (255, 255, 255), (0, blue_h, h, white_h))
        pygame.draw.rect(flag_surface, (237, 28, 36), (0, blue_h + white_h, h, red_h))
        pygame.draw.rect(flag_surface, (255, 255, 255), (0, blue_h + white_h + red_h, h, white_h))
        pygame.draw.rect(flag_surface, (11, 74, 158), (0, h - blue_h, h, blue_h))

        # Белый круг и красная звезда
        star_circle_radius = red_h / 2.5
        star_circle_center = (radius * 0.7, radius) # Смещение влево
        pygame.draw.circle(flag_surface, (255, 255, 255), star_circle_center, star_circle_radius)
        self.draw_star(flag_surface, star_circle_center[0], star_circle_center[1], star_circle_radius * 0.8, (237, 28, 36))

        # Применяем маску
        mask_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (radius, radius), radius)
        flag_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        screen.blit(flag_surface, (center_x - radius, center_y - radius))

    def draw_missile(self, screen, missile):
        """Рисует ракету"""
        surf = pygame.Surface((40, 20), pygame.SRCALPHA)
        # Корпус
        pygame.draw.rect(surf, (150, 150, 150), (0, 7, 30, 6), border_radius=3)
        # Боеголовка
        pygame.draw.polygon(surf, (200, 0, 0), [(30, 7), (30, 13), (38, 10)])
        # Огонь
        pygame.draw.polygon(surf, (255, 150, 0), [(-5, 10), (0, 7), (0, 13)])
        
        rotated_surf = pygame.transform.rotate(surf, missile['rotation'])
        rect = rotated_surf.get_rect(center=(missile['x'], missile['y']))
        screen.blit(rotated_surf, rect)

    def draw_explosion(self, screen, explosion):
        """Рисует взрыв"""
        alpha = 255 * (explosion['timer'] / 30)
        color = (255, 200, 0, alpha)
        
        temp_surface = pygame.Surface((explosion['radius']*2, explosion['radius']*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, color, (explosion['radius'], explosion['radius']), explosion['radius'])
        screen.blit(temp_surface, (explosion['x'] - explosion['radius'], explosion['y'] - explosion['radius']), special_flags=pygame.BLEND_RGBA_ADD)


    def draw(self, screen):
        self.draw_flag_pattern(screen)
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.radius, 3)

        for missile in self.missiles: self.draw_missile(screen, missile)
        for explosion in self.explosions: self.draw_explosion(screen, explosion)

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
        self.missile_damage += 2
        self.explosion_radius = min(100, self.explosion_radius + 5)
        self.missile_cooldown_max = max(180, self.missile_cooldown_max - 15)