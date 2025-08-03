# balls/axe_ball.py
from .base_fighter import FightingBall
import math
import random

class AxeBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(150, 75, 0), 
                         name="Axe Berserker", weapon_type="axe")
        
        self.stats = {'damage': 8, 'range': 90, 'speed': 2, 'radius': self.radius}
        
        # Параметры топора
        self.weapon_length = 70
        self.weapon_width = 20
        
        # ОСОБЕННОСТЬ: Рывок каждые 5 секунд
        self.dash_cooldown = 0
        self.dash_cooldown_max = 300  # 5 секунд при 60 FPS
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_duration = 45  # 0.75 секунды рывка
        self.dash_target = None
        self.dash_trail = []  # Для эффекта следа
        
        # Улучшенная физика для берсерка
        self.max_speed = 14
        self.weapon_rotation_speed = 7
        self.base_rotation_speed = 12  # Быстрее вращается

    def start_dash(self, target):
        """Начинает рывок к противнику"""
        if self.dash_cooldown <= 0 and not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown = self.dash_cooldown_max
            self.dash_target = target
            self.dash_trail = []  # Очищаем след
            
            # Сильный импульс к цели
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                dash_force = 15
                self.vx = (dx / distance) * dash_force
                self.vy = (dy / distance) * dash_force
            
            return True
        return False

    def update(self, other_ball=None):
        # Обновляем кулдаун рывка
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        
        # Логика рывка
        if self.is_dashing:
            self.dash_timer -= 1
            
            # Добавляем позицию в след
            self.dash_trail.append((self.rect.centerx, self.rect.centery))
            # Ограничиваем длину следа
            if len(self.dash_trail) > 8:
                self.dash_trail.pop(0)
            
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.dash_trail = []  # Очищаем след после окончания дэша
                # После рывка немного замедляем
                self.vx *= 0.7
                self.vy *= 0.7
        else:
            # Постепенно очищаем след если не в дэше
            if self.dash_trail:
                self.dash_trail.pop(0)
        
        # Автоматический рывок когда кулдаун готов
        if other_ball and self.dash_cooldown <= 0 and not self.is_dashing:
            # Проверяем расстояние до противника
            dx = other_ball.rect.centerx - self.rect.centerx
            dy = other_ball.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Рывок если противник не слишком близко и не слишком далеко
            if 150 < distance < 400:
                self.start_dash(other_ball)
        
        # Базовое обновление
        super().update(other_ball)

    def take_damage(self, amount):
        # Во время рывка неуязвим!
        if self.is_dashing:
            return False
        
        return super().take_damage(amount)

    def on_successful_attack(self, target):
        # Топор наносит больше урона и становится больше
        self.stats['damage'] += 1.0
        self.weapon_length += 6
        self.weapon_width = min(60, self.weapon_width + 1.2)
        
        # Восстанавливает немного здоровья после удара (берсерк)
        self.health = min(self.max_health, self.health + 1)

    def draw_pixel_axe(self, screen, start_pos, end_pos):
        """Рисует красивый пиксельный двуручный топор с контрастными цветами"""
        import pygame
        
        # Вычисляем угол для правильного позиционирования лезвий
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        handle_angle = math.atan2(dy, dx)
        
        # Рукоять топора (деревянная с обмоткой)
        handle_width = max(8, int(self.weapon_width * 0.4))
        
        # Основа рукояти (темный контур)
        pygame.draw.line(screen, (20, 10, 5), start_pos, end_pos, handle_width + 4)
        # Деревянная рукоять
        pygame.draw.line(screen, (139, 90, 43), start_pos, end_pos, handle_width)
        # Светлые полоски для текстуры
        pygame.draw.line(screen, (180, 140, 70), start_pos, end_pos, max(2, handle_width // 3))
        
        # Обмотка на рукояти (несколько участков)
        handle_length = math.sqrt(dx*dx + dy*dy)
        for i in range(3):
            wrap_start = 0.2 + i * 0.25
            wrap_end = wrap_start + 0.15
            
            wrap_start_pos = (
                start_pos[0] + dx * wrap_start,
                start_pos[1] + dy * wrap_start
            )
            wrap_end_pos = (
                start_pos[0] + dx * wrap_end,
                start_pos[1] + dy * wrap_end
            )
            pygame.draw.line(screen, (60, 40, 20), wrap_start_pos, wrap_end_pos, handle_width + 2)
            pygame.draw.line(screen, (90, 60, 30), wrap_start_pos, wrap_end_pos, handle_width)
        
        # Головка топора
        head_size = max(30, int(self.weapon_width * 1.8))
        head_x = end_pos[0]
        head_y = end_pos[1]
        
        # Перпендикулярный вектор для лезвий
        perp_x = -math.sin(handle_angle)
        perp_y = math.cos(handle_angle)
        
        # Центральная часть головки (металлическое крепление)
        center_width = head_size // 3
        center_length = head_size // 2
        
        center_start = (
            head_x - perp_x * center_width,
            head_y - perp_y * center_width
        )
        center_end = (
            head_x + perp_x * center_width,
            head_y + perp_y * center_width
        )
        
        # Рисуем центральную часть
        pygame.draw.line(screen, (40, 40, 40), center_start, center_end, center_length + 4)  # Контур
        pygame.draw.line(screen, (120, 120, 130), center_start, center_end, center_length)   # Металл
        pygame.draw.line(screen, (160, 160, 170), center_start, center_end, center_length // 2)  # Блик
        
        # Левое лезвие
        blade_length = head_size * 1.2
        left_blade_tip = (
            head_x - perp_x * blade_length,
            head_y - perp_y * blade_length
        )
        
        left_blade_points = [
            left_blade_tip,
            (head_x - perp_x * center_width - math.cos(handle_angle) * center_length//2,
             head_y - perp_y * center_width - math.sin(handle_angle) * center_length//2),
            (head_x - perp_x * center_width + math.cos(handle_angle) * center_length//2,
             head_y - perp_y * center_width + math.sin(handle_angle) * center_length//2)
        ]
        
        # Правое лезвие
        right_blade_tip = (
            head_x + perp_x * blade_length,
            head_y + perp_y * blade_length
        )
        
        right_blade_points = [
            right_blade_tip,
            (head_x + perp_x * center_width - math.cos(handle_angle) * center_length//2,
             head_y + perp_y * center_width - math.sin(handle_angle) * center_length//2),
            (head_x + perp_x * center_width + math.cos(handle_angle) * center_length//2,
             head_y + perp_y * center_width + math.sin(handle_angle) * center_length//2)
        ]
        
        # Рисуем лезвия с контуром
        for blade_points in [left_blade_points, right_blade_points]:
            # Темный контур
            pygame.draw.polygon(screen, (30, 30, 30), blade_points)
            
            # Основное лезвие (светло-серый металл)
            inner_points = []
            for i, point in enumerate(blade_points):
                if i == 0:  # Кончик лезвия
                    inner_points.append((point[0] * 0.9 + blade_points[1][0] * 0.05 + blade_points[2][0] * 0.05,
                                       point[1] * 0.9 + blade_points[1][1] * 0.05 + blade_points[2][1] * 0.05))
                else:
                    inner_points.append((point[0] * 0.95 + blade_points[0][0] * 0.05,
                                       point[1] * 0.95 + blade_points[0][1] * 0.05))
            
            pygame.draw.polygon(screen, (200, 200, 210), inner_points)
            
            # Острое лезвие (яркий блик)
            edge_points = [
                blade_points[0],  # Кончик
                ((blade_points[1][0] + blade_points[2][0]) * 0.5,
                 (blade_points[1][1] + blade_points[2][1]) * 0.5)
            ]
            pygame.draw.line(screen, (240, 240, 250), edge_points[0], edge_points[1], 3)
            
            # Дополнительный блик по краю
            for i in range(len(blade_points) - 1):
                mid_point = (
                    (blade_points[i][0] + blade_points[i+1][0]) * 0.5,
                    (blade_points[i][1] + blade_points[i+1][1]) * 0.5
                )
                inner_point = (
                    mid_point[0] * 0.8 + head_x * 0.2,
                    mid_point[1] * 0.8 + head_y * 0.2
                )
                pygame.draw.line(screen, (220, 220, 230), mid_point, inner_point, 2)

    def draw_weapon(self, screen):
        start_pos, end_pos = self.get_weapon_line()
        self.draw_pixel_axe(screen, start_pos, end_pos)

    def draw(self, screen):
        import pygame
        
        # Эффект следа от рывка
        if self.dash_trail:
            for i, pos in enumerate(self.dash_trail):
                alpha = int(255 * (i + 1) / len(self.dash_trail) * 0.6)
                radius = int(self.radius * (0.3 + 0.7 * (i + 1) / len(self.dash_trail)))
                
                # Создаем поверхность для полупрозрачного эффекта
                trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                trail_color = (255, 150, 50, alpha)
                pygame.draw.circle(trail_surface, trail_color, (radius, radius), radius)
                screen.blit(trail_surface, (pos[0] - radius, pos[1] - radius))
        
        # Эффект рывка
        if self.is_dashing:
            # Яркое свечение во время рывка
            glow_radius = self.radius + 15
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            # Пульсирующее свечение
            pulse = 0.7 + 0.3 * math.sin(self.dash_timer * 0.3)
            glow_alpha = int(120 * pulse)
            glow_color = (255, 100, 0, glow_alpha)
            
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.rect.centerx - glow_radius, self.rect.centery - glow_radius))
        
        # Индикатор готовности рывка
        if self.dash_cooldown <= 60 and not self.is_dashing:  # Мигает последнюю секунду
            if (self.dash_cooldown // 10) % 2:
                ready_color = (255, 255, 0, 150)
                ready_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
                pygame.draw.circle(ready_surface, ready_color, 
                                 (self.radius * 1.5, self.radius * 1.5), self.radius + 5, 4)
                screen.blit(ready_surface, 
                          (self.rect.centerx - self.radius * 1.5, self.rect.centery - self.radius * 1.5))
        
        # Базовое рисование
        super().draw(screen)