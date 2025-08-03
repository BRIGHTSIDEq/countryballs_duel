# balls/canada_ball.py
from .base_fighter import FightingBall
import pygame
import math
import random

class CanadaBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255), 
                         name="Canada", weapon_type="politeness")
        
        # Канада - самый слабый боец (это шутка)
        self.stats = {'damage': 1, 'range': 30, 'speed': 2, 'radius': self.radius}
        
        # У Канады нет оружия, только вежливость
        self.politeness_level = 100
        self.apology_timer = 0
        self.apology_messages = [
            "Sorry!", "Eh?", "My bad!", "Pardon!", "Oops!"
        ]
        self.current_apology = ""
        
        # Канада двигается медленнее
        self.max_speed = 4
        self.bounce_energy = 0.8  # Меньше энергии отскока

    def apologize(self):
        """Канада извиняется после любого контакта"""
        self.current_apology = random.choice(self.apology_messages)
        self.apology_timer = 120  # 2 секунды извинений

    def attack(self, target):
        """Канада 'атакует' очень слабо и сразу извиняется"""
        if not self.can_attack():
            return False

        # Очень слабая атака
        target.last_attacker_pos = self.rect.center
        success = target.take_damage(self.stats['damage'])
        
        if success:
            self.attack_cooldown = self.attack_cooldown_duration
            self.apologize()  # Сразу извиняется
            
            # Очень слабый отброс
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                knockback_force = 2  # Очень слабый отброс
                target.vx += (dx / distance) * knockback_force
                target.vy += (dy / distance) * knockback_force
            
            self.on_successful_attack(target)
        
        return success

    def take_damage(self, amount):
        """Канада извиняется даже когда получает урон"""
        result = super().take_damage(amount)
        if result:
            self.apologize()
        return result

    def update(self, other_ball=None):
        # Обновляем таймер извинений
        if self.apology_timer > 0:
            self.apology_timer -= 1
            if self.apology_timer <= 0:
                self.current_apology = ""
        
        # Канада пытается избегать конфликтов
        if other_ball:
            dx = other_ball.rect.centerx - self.rect.centerx
            dy = other_ball.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Если слишком близко - пытается отойти
            if distance < 100:
                avoidance_force = 1
                if distance > 0:
                    self.vx -= (dx / distance) * avoidance_force
                    self.vy -= (dy / distance) * avoidance_force
        
        # Базовое обновление
        super().update(other_ball)

    def draw_maple_leaf(self, screen, center_x, center_y, size, color):
        """Рисует кленовый лист"""
        # Упрощенный кленовый лист из многоугольника
        leaf_points = [
            (center_x, center_y - size),  # верх
            (center_x - size//3, center_y - size//2),  # левый верх
            (center_x - size//2, center_y - size//3),  # левый
            (center_x - size//4, center_y),  # левый центр
            (center_x - size//2, center_y + size//3),  # левый низ
            (center_x - size//4, center_y + size//2),  # левый нижний
            (center_x, center_y + size),  # низ (стебель)
            (center_x + size//4, center_y + size//2),  # правый нижний
            (center_x + size//2, center_y + size//3),  # правый низ
            (center_x + size//4, center_y),  # правый центр
            (center_x + size//2, center_y - size//3),  # правый
            (center_x + size//3, center_y - size//2),  # правый верх
        ]
        
        pygame.draw.polygon(screen, color, leaf_points)
        pygame.draw.polygon(screen, (200, 0, 0), leaf_points, 2)  # Контур

    def draw_apology_bubble(self, screen):
        """Рисует пузырь с извинениями"""
        if self.apology_timer > 0 and self.current_apology:
            center_x, center_y = self.rect.center
            
            # Пузырь речи
            bubble_width = len(self.current_apology) * 8 + 20
            bubble_height = 25
            bubble_x = center_x - bubble_width // 2
            bubble_y = center_y - self.radius - bubble_height - 10
            
            # Фон пузыря
            bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
            pygame.draw.rect(screen, (255, 255, 255), bubble_rect)
            pygame.draw.rect(screen, (0, 0, 0), bubble_rect, 2)
            
            # Хвостик пузыря
            tail_points = [
                (center_x - 5, bubble_y + bubble_height),
                (center_x + 5, bubble_y + bubble_height),
                (center_x, center_y - self.radius)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), tail_points)
            pygame.draw.polygon(screen, (0, 0, 0), tail_points, 2)
            
            # Текст извинения
            font = pygame.font.Font(None, 20)
            text_surface = font.render(self.current_apology, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(bubble_x + bubble_width // 2, bubble_y + bubble_height // 2))
            screen.blit(text_surface, text_rect)

    def draw_politeness_aura(self, screen):
        """Рисует ауру вежливости вокруг Канады"""
        center_x, center_y = self.rect.center
        
        # Мягкое свечение
        aura_radius = self.radius + 10 + 5 * math.sin(pygame.time.get_ticks() * 0.003)
        aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
        aura_color = (200, 220, 255, 30)  # Мягкий голубоватый
        pygame.draw.circle(aura_surface, aura_color, (aura_radius, aura_radius), aura_radius)
        screen.blit(aura_surface, (center_x - aura_radius, center_y - aura_radius))

    def draw(self, screen):
        # Рисуем ауру вежливости
        self.draw_politeness_aura(screen)
        
        # Рисуем канадский флаг как тело шарика
        center_x, center_y = self.rect.center
        
        # Белый фон
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius)
        
        # Красные полосы по бокам
        left_stripe_rect = pygame.Rect(center_x - self.radius, center_y - self.radius, 
                                      self.radius // 2, self.radius * 2)
        right_stripe_rect = pygame.Rect(center_x + self.radius // 2, center_y - self.radius, 
                                       self.radius // 2, self.radius * 2)
        
        pygame.draw.rect(screen, (255, 0, 0), left_stripe_rect)
        pygame.draw.rect(screen, (255, 0, 0), right_stripe_rect)
        
        # Обрезаем по кругу
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius)
        
        # Перерисовываем с правильной обрезкой
        # Левая красная полоса
        for angle in range(135, 225, 5):
            x = center_x + self.radius * math.cos(math.radians(angle))
            y = center_y + self.radius * math.sin(math.radians(angle))
            pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (x, y), 3)
        
        # Правая красная полоса
        for angle in range(315, 405, 5):
            if angle >= 360:
                angle -= 360
            x = center_x + self.radius * math.cos(math.radians(angle))
            y = center_y + self.radius * math.sin(math.radians(angle))
            pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (x, y), 3)
        
        # Белый центр
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius // 2)
        
        # Кленовый лист в центре
        self.draw_maple_leaf(screen, center_x, center_y, self.radius // 3, (255, 0, 0))
        
        # Контур шарика
        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), self.radius, 3)
        
        # Пузырь с извинениями
        self.draw_apology_bubble(screen)
        
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
        # Канада не становится сильнее от атак, остается вежливой
        self.politeness_level += 10
        self.apologize()  # Извиняется даже за успешную атаку