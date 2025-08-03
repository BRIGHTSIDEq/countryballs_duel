# balls/bow_ball.py
from .base_fighter import FightingBall
import math
import random

class Arrow:
    def __init__(self, start_x, start_y, target_x, target_y, speed=8):
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        
        # Направление к цели
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
        else:
            self.vx = speed
            self.vy = 0
            
        self.angle = math.degrees(math.atan2(dy, dx))
        self.length = 25
        self.active = True
        self.damage = 5
        
        # Для отслеживания столкновений
        self.hit_targets = set()

    def update(self):
        if not self.active:
            return
            
        self.x += self.vx
        self.y += self.vy
        
        # Стрела исчезает если улетела слишком далеко
        distance_traveled = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2)
        if distance_traveled > 600:
            self.active = False

    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        import pygame
        return pygame.Rect(self.x - 5, self.y - 5, 10, 10)

    def draw(self, screen):
        if not self.active:
            return
            
        import pygame
        
        # Рисуем стрелу
        end_x = self.x + self.length * math.cos(math.radians(self.angle))
        end_y = self.y + self.length * math.sin(math.radians(self.angle))
        
        # Древко стрелы
        pygame.draw.line(screen, (101, 67, 33), (self.x, self.y), (end_x, end_y), 4)
        pygame.draw.line(screen, (139, 90, 43), (self.x, self.y), (end_x, end_y), 2)
        
        # Наконечник
        tip_length = 8
        tip_x = end_x + tip_length * math.cos(math.radians(self.angle))
        tip_y = end_y + tip_length * math.sin(math.radians(self.angle))
        
        pygame.draw.line(screen, (40, 40, 40), (end_x, end_y), (tip_x, tip_y), 6)
        pygame.draw.line(screen, (180, 180, 180), (end_x, end_y), (tip_x, tip_y), 4)
        
        # Оперение
        feather_length = 6
        feather_x = self.x - feather_length * math.cos(math.radians(self.angle))
        feather_y = self.y - feather_length * math.sin(math.radians(self.angle))
        
        # Два пера
        feather_offset = 15
        feather1_x = feather_x + feather_length * math.cos(math.radians(self.angle + feather_offset))
        feather1_y = feather_y + feather_length * math.sin(math.radians(self.angle + feather_offset))
        feather2_x = feather_x + feather_length * math.cos(math.radians(self.angle - feather_offset))
        feather2_y = feather_y + feather_length * math.sin(math.radians(self.angle - feather_offset))
        
        pygame.draw.line(screen, (255, 100, 100), (self.x, self.y), (feather1_x, feather1_y), 3)
        pygame.draw.line(screen, (255, 100, 100), (self.x, self.y), (feather2_x, feather2_y), 3)


class BowBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=35, color=(34, 139, 34), 
                         name="Archer Lord", weapon_type="bow")
        
        self.stats = {'damage': 5, 'range': 200, 'speed': 7, 'radius': self.radius}
        
        # Параметры лука
        self.weapon_length = 60
        self.weapon_width = 8
        
        # ОСОБЕННОСТЬ: Стрелы
        self.arrows = []
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 50# 1 секунда при 60 FPS
        self.arrows_per_shot = 1  # Начинаем с одной стрелы
        self.total_shots = 0
        
        # Лучник более подвижный но хрупкий
        self.max_speed = 22
        self.weapon_rotation_speed = 3
        self.bounce_energy = 1.3
        
        # Уменьшенное здоровье
        self.max_health = 100
        self.health = self.max_health

    def can_shoot(self):
        return self.shoot_cooldown <= 0

    def shoot_arrows(self, target):
        """Выстреливает стрелы в сторону цели"""
        if not self.can_shoot():
            return False
            
        self.shoot_cooldown = self.shoot_cooldown_max
        self.total_shots += 1
        
        # Позиция стрельбы (конец лука)
        shoot_x = self.rect.centerx + (self.radius + self.weapon_length * 0.8) * math.sin(math.radians(self.weapon_angle))
        shoot_y = self.rect.centery - (self.radius + self.weapon_length * 0.8) * math.cos(math.radians(self.weapon_angle))
        
        # Стреляем несколько стрел
        for i in range(self.arrows_per_shot):
            # Небольшой разброс для множественных стрел
            spread_angle = 0
            if self.arrows_per_shot > 1:
                spread_angle = (i - (self.arrows_per_shot - 1) / 2) * 15
            
            target_x = target.rect.centerx + spread_angle * 2
            target_y = target.rect.centery + spread_angle * 2
            
            arrow = Arrow(shoot_x, shoot_y, target_x, target_y)
            self.arrows.append(arrow)
        
        # После каждого выстрела количество стрел увеличивается
        self.arrows_per_shot += 1
        
        return True

    def update_arrows(self, other_ball):
        """Обновляет все стрелы"""
        for arrow in self.arrows[:]:  # Копия списка для безопасного удаления
            if not arrow.active:
                self.arrows.remove(arrow)
                continue
                
            arrow.update()
            
            # Проверка столкновения с противником
            if (other_ball not in arrow.hit_targets and 
                arrow.get_rect().colliderect(other_ball.rect)):
                
                # Стрела попала
                arrow.hit_targets.add(other_ball)
                other_ball.last_attacker_pos = (arrow.x, arrow.y)
                other_ball.take_damage(arrow.damage)
                arrow.active = False

    def update(self, other_ball=None):
        # Обновляем кулдаун стрельбы
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Автоматическая стрельба
        if other_ball and self.can_shoot():
            self.shoot_arrows(other_ball)
        
        # Обновляем стрелы
        if other_ball:
            self.update_arrows(other_ball)
        
        # Базовое обновление
        super().update(other_ball)

    def on_successful_attack(self, target):
        # Лучник не атакует оружием напрямую, только стрелами
        pass

    def check_arrow_weapon_collision(self, weapon_rect):
        """Проверяет столкновение стрел с оружием противника (парирование)"""
        for arrow in self.arrows[:]:
            if arrow.active and arrow.get_rect().colliderect(weapon_rect):
                arrow.active = False
                return True
        return False

    def draw_pixel_bow(self, screen, start_pos, end_pos):
        """Рисует красивый пиксельный лук"""
        import pygame
        
        # Рукоять лука (центральная часть)
        handle_length = self.weapon_length * 0.3
        handle_start_x = self.rect.centerx + (self.radius + handle_length/2) * math.sin(math.radians(self.weapon_angle))
        handle_start_y = self.rect.centery - (self.radius + handle_length/2) * math.cos(math.radians(self.weapon_angle))
        handle_end_x = self.rect.centerx + (self.radius + handle_length*1.5) * math.sin(math.radians(self.weapon_angle))
        handle_end_y = self.rect.centery - (self.radius + handle_length*1.5) * math.cos(math.radians(self.weapon_angle))
        
        # Рукоять
        pygame.draw.line(screen, (60, 30, 0), (handle_start_x, handle_start_y), (handle_end_x, handle_end_y), 8)
        pygame.draw.line(screen, (101, 67, 33), (handle_start_x, handle_start_y), (handle_end_x, handle_end_y), 6)
        
        # Плечи лука (изогнутые части)
        bow_width = 25
        
        # Верхнее плечо
        upper_start_x = handle_end_x
        upper_start_y = handle_end_y
        upper_end_x = end_pos[0] + bow_width * math.cos(math.radians(self.weapon_angle))
        upper_end_y = end_pos[1] + bow_width * math.sin(math.radians(self.weapon_angle))
        
        # Нижнее плечо
        lower_start_x = handle_start_x
        lower_start_y = handle_start_y
        lower_end_x = start_pos[0] + bow_width * math.cos(math.radians(self.weapon_angle))
        lower_end_y = start_pos[1] + bow_width * math.sin(math.radians(self.weapon_angle))
        
        # Рисуем плечи лука
        pygame.draw.line(screen, (40, 25, 5), (upper_start_x, upper_start_y), (upper_end_x, upper_end_y), 6)
        pygame.draw.line(screen, (139, 90, 43), (upper_start_x, upper_start_y), (upper_end_x, upper_end_y), 4)
        
        pygame.draw.line(screen, (40, 25, 5), (lower_start_x, lower_start_y), (lower_end_x, lower_end_y), 6)
        pygame.draw.line(screen, (139, 90, 43), (lower_start_x, lower_start_y), (lower_end_x, lower_end_y), 4)
        
        # Тетива лука
        pygame.draw.line(screen, (200, 200, 200), (upper_end_x, upper_end_y), (lower_end_x, lower_end_y), 2)
        
        # Наконечники лука
        for end_x, end_y in [(upper_end_x, upper_end_y), (lower_end_x, lower_end_y)]:
            pygame.draw.circle(screen, (60, 60, 60), (int(end_x), int(end_y)), 4)
            pygame.draw.circle(screen, (120, 120, 120), (int(end_x), int(end_y)), 3)

    def draw_weapon(self, screen):
        start_pos, end_pos = self.get_weapon_line()
        self.draw_pixel_bow(screen, start_pos, end_pos)

    def draw(self, screen):
        import pygame
        
        # Рисуем все стрелы
        for arrow in self.arrows:
            arrow.draw(screen)
        
        # Индикатор готовности к стрельбе
        if self.shoot_cooldown <= 15:  # Мигает перед выстрелом
            if (self.shoot_cooldown // 5) % 2:
                ready_color = (0, 255, 0, 120)
                ready_surface = pygame.Surface((self.radius * 2.5, self.radius * 2.5), pygame.SRCALPHA)
                pygame.draw.circle(ready_surface, ready_color, 
                                 (int(self.radius * 1.25), int(self.radius * 1.25)), self.radius + 8, 2)
                screen.blit(ready_surface, 
                          (self.rect.centerx - self.radius * 1.25, self.rect.centery - self.radius * 1.25))
        
        # Показываем количество стрел в следующем залпе
        if self.arrows_per_shot > 1:
            arrows_text = f"x{self.arrows_per_shot}"
            font = pygame.font.Font(None, 20)
            text_surface = font.render(arrows_text, True, (255, 255, 0))
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - self.radius - 20))
            
            # Тень
            shadow_surface = font.render(arrows_text, True, (0, 0, 0))
            shadow_rect = text_surface.get_rect(center=(self.rect.centerx + 1, self.rect.centery - self.radius - 19))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)
        
        # Базовое рисование
        super().draw(screen)