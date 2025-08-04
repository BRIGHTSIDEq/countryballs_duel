# balls/canada_ball.py - ОБНОВЛЕННАЯ ВЕРСИЯ
from .base_fighter import FightingBall
import pygame
import math
import random

class CanadaBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255),
                         name="Canada", weapon_type="politeness")

        self.stats = {'damage': 1, 'range': 30, 'speed': 2, 'radius': self.radius}
        self.politeness_level = 100
        self.apology_timer = 0
        self.apology_messages = ["Sorry!", "Eh?", "My bad!", "Pardon!", "Oops!"]
        self.current_apology = ""
        self.max_speed = 4

    def apologize(self):
        self.current_apology = random.choice(self.apology_messages)
        self.apology_timer = 120

    def attack(self, target):
        if not self.can_attack(): return False
        success = target.take_damage(self.stats['damage'])
        if success:
            self.attack_cooldown = self.attack_cooldown_duration
            self.apologize()
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                target.vx += (dx / distance) * 2
                target.vy += (dy / distance) * 2
            self.on_successful_attack(target)
        return success

    def take_damage(self, amount):
        result = super().take_damage(amount)
        if result: self.apologize()
        return result

    def update(self, other_ball=None):
        if self.apology_timer > 0:
            self.apology_timer -= 1
        else:
            self.current_apology = ""

        if other_ball:
            distance = math.hypot(other_ball.rect.centerx - self.rect.centerx, other_ball.rect.centery - self.rect.centery)
            if distance < 100 and distance > 0:
                self.vx -= (other_ball.rect.centerx - self.rect.centerx) / distance
                self.vy -= (other_ball.rect.centery - self.rect.centery) / distance

        super().update(other_ball)

    def draw_maple_leaf(self, screen, center_x, center_y, size):
        """Рисует более точный кленовый лист"""
        color = (255, 0, 0)
        s = size
        # Points for an 11-pointed maple leaf, adjusted for the ball
        points = [
            (0, -s), (-s/5, -s*0.9), (-s*0.4, -s*0.5), (-s*0.3, -s*0.4),
            (-s*0.9, -s*0.3), (-s*0.6, 0), (-s*0.7, s*0.4), (-s*0.3, s*0.3),
            (-s*0.2, s*0.8), (0, s*0.6), (s*0.2, s*0.8), (s*0.3, s*0.3),
            (s*0.7, s*0.4), (s*0.6, 0), (s*0.9, -s*0.3), (s*0.3, -s*0.4),
            (s*0.4, -s*0.5), (s/5, -s*0.9)
        ]
        # Translate points to center
        translated_points = [(p[0] + center_x, p[1] + center_y) for p in points]
        pygame.draw.polygon(screen, color, translated_points)


    def draw_flag_pattern(self, screen):
        """Рисует правильный флаг Канады с помощью маски"""
        center_x, center_y = self.rect.center
        radius = self.radius
        
        flag_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        # Пропорции флага: 1:2:1
        red_width = (radius * 2) / 4
        white_width = (radius * 2) / 2
        
        # Красные полосы
        pygame.draw.rect(flag_surface, (255, 0, 0), (0, 0, red_width, radius * 2))
        pygame.draw.rect(flag_surface, (255, 0, 0), (red_width + white_width, 0, red_width, radius * 2))
        # Белая полоса
        pygame.draw.rect(flag_surface, (255, 255, 255), (red_width, 0, white_width, radius * 2))

        # Рисуем лист на белой части
        self.draw_maple_leaf(flag_surface, radius, radius, radius * 0.6)

        # Применяем маску
        mask_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (radius, radius), radius)
        flag_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        screen.blit(flag_surface, (center_x - radius, center_y - radius))

    def draw_apology_bubble(self, screen):
        """Рисует пузырь с извинениями"""
        if self.apology_timer > 0 and self.current_apology:
            font = pygame.font.Font(None, 22)
            text_surf = font.render(self.current_apology, True, (0,0,0))
            padding = 10
            bubble_rect = text_surf.get_rect(center=self.rect.center).inflate(padding, padding)
            bubble_rect.center = (self.rect.centerx, self.rect.centery - self.radius - 20)
            
            pygame.draw.rect(screen, (255, 255, 255), bubble_rect, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), bubble_rect, 1, border_radius=10)
            screen.blit(text_surf, text_surf.get_rect(center=bubble_rect.center))


    def draw(self, screen):
        self.draw_flag_pattern(screen)
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.radius, 3)
        self.draw_apology_bubble(screen)
        
        if self.health > 0:
            font = pygame.font.Font(None, 28)
            health_text = f"{int(self.health)}"
            text_surface = font.render(health_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.rect.center)
            shadow_surface = font.render(health_text, True, (255, 255, 255))
            shadow_rect = text_surface.get_rect(center=(self.rect.center[0] + 1, self.rect.center[1] + 1))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)

    def on_successful_attack(self, target):
        self.politeness_level += 10
        self.apologize()