# balls/base_fighter.py
import pygame
import os
import math
import random
from config import ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT

class FightingBall:
    def __init__(self, x, y, radius, color, name, weapon_type="sword"):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.color = color
        self.name = name
        self.weapon_type = weapon_type

        # УЛУЧШЕННАЯ ФИЗИКА для TikTok/YouTube Shorts
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-6, 6)
        self.gravity = 0.2
        self.bounce_energy = 1.2  # Уменьшили энергию отскока
        self.friction = 0.998  # Больше трения для более спокойного движения
        self.min_speed = 2
        self.max_speed = 9  # Уменьшили максимальную скорость

        # БЫСТРОЕ вращение шарика
        self.angle = 0
        self.angular_velocity = 0
        self.base_rotation_speed = 5

        # Оружие
        self.weapon_angle = 0
        self.weapon_rotation_speed = 4
        self.weapon_rotation_direction = 1

        # Параметры оружия - УВЕЛИЧЕННЫЕ в 2 раза для лучшей видимости
        self.weapon_length = 100 if weapon_type == "sword" else 120
        self.weapon_width = 16 if weapon_type == "sword" else 12
        self.base_length = self.weapon_length

        self.max_health = 100
        self.health = self.max_health

        # Система неуязвимости и атак
        self.is_invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 25

        self.attack_cooldown = 0
        self.attack_cooldown_duration = 20

        # Характеристики для UI
        self.stats = {'damage': 10, 'range': 1, 'speed': 1, 'radius': self.radius}

        # Для предотвращения прохождения сквозь друг друга
        self.last_pos = (self.rect.centerx, self.rect.centery)

    def take_damage(self, amount):
        if self.is_invulnerable:
            return False

        self.health -= amount
        if self.health < 0:
            self.health = 0

        self.is_invulnerable = True
        self.invulnerable_timer = self.invulnerable_duration
        self.weapon_rotation_direction *= -1

        # БОЛЕЕ ЭФФЕКТНЫЙ отброс
        knockback_force = 6
        if hasattr(self, 'last_attacker_pos'):
            dx = self.rect.centerx - self.last_attacker_pos[0]
            dy = self.rect.centery - self.last_attacker_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                self.vx += (dx / distance) * knockback_force
                self.vy += (dy / distance) * knockback_force - 2

        return True

    def can_attack(self):
        return self.attack_cooldown <= 0 and not self.is_invulnerable

    def attack(self, target):
        if not self.can_attack():
            return False

        target.last_attacker_pos = self.rect.center
        success = target.take_damage(self.stats['damage'])
        if success:
            self.attack_cooldown = self.attack_cooldown_duration
            self.on_successful_attack(target)
        return success

    def on_successful_attack(self, target):
        pass

    def parry(self):
        # УЛУЧШЕННОЕ парирование - более естественный отброс
        center_x = ARENA_X + ARENA_WIDTH / 2
        center_y = ARENA_Y + ARENA_HEIGHT / 2
        dx = self.rect.centerx - center_x
        dy = self.rect.centery - center_y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            bounce_force = 8  # Увеличили силу отброса для парирования
            self.vx += (dx / distance) * bounce_force
            self.vy += (dy / distance) * bounce_force - 3
        
        # Добавляем больше случайности для парирования
        self.vx += random.uniform(-2, 2)
        self.vy += random.uniform(-2, 2)

    def check_collision_with_other(self, other):
        """Проверка и разрешение столкновений между шариками"""
        dx = other.rect.centerx - self.rect.centerx
        dy = other.rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        min_distance = self.radius + other.radius

        if distance < min_distance and distance > 0:
            # Разделяем шарики
            overlap = min_distance - distance
            move_distance = overlap / 2

            # Нормализованный вектор
            nx = dx / distance
            ny = dy / distance

            # Раздвигаем шарики
            self.rect.centerx -= nx * move_distance
            self.rect.centery -= ny * move_distance
            other.rect.centerx += nx * move_distance
            other.rect.centery += ny * move_distance

            # Обмен скоростями с коэффициентом отскока
            bounce_factor = 0.7
            self_vel_n = self.vx * nx + self.vy * ny
            other_vel_n = other.vx * nx + other.vy * ny

            # Новые скорости
            self.vx += (other_vel_n - self_vel_n) * nx * bounce_factor
            self.vy += (other_vel_n - self_vel_n) * ny * bounce_factor
            other.vx += (self_vel_n - other_vel_n) * nx * bounce_factor
            other.vy += (self_vel_n - other_vel_n) * ny * bounce_factor

    def update(self, other_ball=None):
        if self.is_invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # БЫСТРОЕ вращение оружия
        self.weapon_angle += self.weapon_rotation_speed * self.weapon_rotation_direction
        if self.weapon_angle >= 360:
            self.weapon_angle -= 360
        elif self.weapon_angle < 0:
            self.weapon_angle += 360

        # Применяем гравитацию
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction

        # Ограничение максимальной скорости
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > self.max_speed:
            factor = self.max_speed / speed
            self.vx *= factor
            self.vy *= factor

        # Вращение шарика на основе скорости
        total_speed = math.sqrt(self.vx**2 + self.vy**2)
        self.angular_velocity = (total_speed * 2 + self.base_rotation_speed) 
        if self.vx < 0:
            self.angular_velocity = -self.angular_velocity

        self.angle += self.angular_velocity
        if self.angle > 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360

        # Сохраняем предыдущую позицию
        self.last_pos = (self.rect.centerx, self.rect.centery)

        # Движение
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Проверка столкновений с другим шариком
        if other_ball:
            self.check_collision_with_other(other_ball)

        # ИСПРАВЛЕННЫЕ отскоки от стен - предотвращаем вертикальное зацикливание
        if self.rect.left <= ARENA_X:
            self.rect.left = ARENA_X
            self.vx = -self.vx * self.bounce_energy
            self.vx += 2  # Небольшой импульс чтобы не застревать

        if self.rect.right >= ARENA_X + ARENA_WIDTH:
            self.rect.right = ARENA_X + ARENA_WIDTH
            self.vx = -self.vx * self.bounce_energy
            self.vx -= 2  # Небольшой импульс чтобы не застревать

        if self.rect.top <= ARENA_Y:
            self.rect.top = ARENA_Y
            self.vy = -self.vy * self.bounce_energy
            # Предотвращаем вертикальное зацикливание
            if abs(self.vx) < 3:
                self.vx += random.uniform(-4, 4)

        if self.rect.bottom >= ARENA_Y + ARENA_HEIGHT:
            self.rect.bottom = ARENA_Y + ARENA_HEIGHT
            self.vy = -self.vy * self.bounce_energy
            # Предотвращаем вертикальное зацикливание
            if abs(self.vx) < 3:
                self.vx += random.uniform(-4, 4)

        # Поддержание минимальной скорости
        total_speed = math.sqrt(self.vx**2 + self.vy**2)
        if total_speed < self.min_speed:
            factor = self.min_speed / max(total_speed, 0.1)
            self.vx *= factor * 1.1
            self.vy *= factor * 1.1

    def get_weapon_line(self):
        center_x = self.rect.centerx
        center_y = self.rect.centery
        start_x = center_x + self.radius * math.sin(math.radians(self.weapon_angle))
        start_y = center_y - self.radius * math.cos(math.radians(self.weapon_angle))
        end_x = center_x + (self.radius + self.weapon_length) * math.sin(math.radians(self.weapon_angle))
        end_y = center_y - (self.radius + self.weapon_length) * math.cos(math.radians(self.weapon_angle))
        return (start_x, start_y), (end_x, end_y)

    def get_weapon_rect(self):
        start_pos, end_pos = self.get_weapon_line()
        min_x = min(start_pos[0], end_pos[0]) - self.weapon_width // 2
        max_x = max(start_pos[0], end_pos[0]) + self.weapon_width // 2
        min_y = min(start_pos[1], end_pos[1]) - self.weapon_width // 2
        max_y = max(start_pos[1], end_pos[1]) + self.weapon_width // 2
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def draw_pixel_sword(self, screen, start_pos, end_pos):
        """Рисует красивый пиксельный меч с отличной контрастностью"""
        # Основное лезвие с темным контуром
        blade_width = max(4, int(self.weapon_width * 0.8))
        pygame.draw.line(screen, (40, 40, 40), start_pos, end_pos, blade_width + 4)  # Темный контур
        pygame.draw.line(screen, (160, 160, 160), start_pos, end_pos, blade_width)   # Основное лезвие
        
        # Яркий блик на лезвии
        if blade_width > 4:
            highlight_width = max(2, blade_width // 3)
            pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, highlight_width)
        
        # Рукоять
        handle_length = 20
        handle_start_x = self.rect.centerx + (self.radius - handle_length) * math.sin(math.radians(self.weapon_angle))
        handle_start_y = self.rect.centery - (self.radius - handle_length) * math.cos(math.radians(self.weapon_angle))
        handle_end = start_pos
        
        pygame.draw.line(screen, (20, 10, 0), (handle_start_x, handle_start_y), handle_end, blade_width + 6)  # Темный контур
        pygame.draw.line(screen, (101, 67, 33), (handle_start_x, handle_start_y), handle_end, blade_width + 2)  # Рукоять
        
        # Гарда (перекрестие)
        guard_length = 18
        guard_start_x = start_pos[0] - guard_length * math.cos(math.radians(self.weapon_angle))
        guard_start_y = start_pos[1] - guard_length * math.sin(math.radians(self.weapon_angle))
        guard_end_x = start_pos[0] + guard_length * math.cos(math.radians(self.weapon_angle))
        guard_end_y = start_pos[1] + guard_length * math.sin(math.radians(self.weapon_angle))
        
        pygame.draw.line(screen, (30, 30, 30), (guard_start_x, guard_start_y), (guard_end_x, guard_end_y), blade_width + 2)
        pygame.draw.line(screen, (150, 150, 150), (guard_start_x, guard_start_y), (guard_end_x, guard_end_y), blade_width)
        
        # Острие меча
        tip_length = 15
        tip_x = end_pos[0] + tip_length * math.sin(math.radians(self.weapon_angle))
        tip_y = end_pos[1] - tip_length * math.cos(math.radians(self.weapon_angle))
        
        tip_left_x = end_pos[0] + (blade_width//2) * math.cos(math.radians(self.weapon_angle))
        tip_left_y = end_pos[1] + (blade_width//2) * math.sin(math.radians(self.weapon_angle))
        tip_right_x = end_pos[0] - (blade_width//2) * math.cos(math.radians(self.weapon_angle))
        tip_right_y = end_pos[1] - (blade_width//2) * math.sin(math.radians(self.weapon_angle))
        
        pygame.draw.polygon(screen, (40, 40, 40), [(tip_x, tip_y), (tip_left_x, tip_left_y), (tip_right_x, tip_right_y)])
        pygame.draw.polygon(screen, (240, 240, 240), [(tip_x, tip_y), (tip_left_x, tip_left_y), (tip_right_x, tip_right_y)])

    def draw_pixel_spear(self, screen, start_pos, end_pos):
        """Рисует красивое пиксельное копье с отличной контрастностью"""
        # Древко с темным контуром
        shaft_width = max(4, int(self.weapon_width * 0.7))
        pygame.draw.line(screen, (30, 15, 5), start_pos, end_pos, shaft_width + 4)  # Темный контур
        pygame.draw.line(screen, (139, 69, 19), start_pos, end_pos, shaft_width)    # Основное древко
        
        # Полоски на древке для текстуры
        if shaft_width > 4:
            stripe_width = max(2, shaft_width // 3)
            pygame.draw.line(screen, (101, 67, 33), start_pos, end_pos, stripe_width)
        
        # Наконечник копья
        tip_length = 25
        tip_x = end_pos[0] + tip_length * math.sin(math.radians(self.weapon_angle))
        tip_y = end_pos[1] - tip_length * math.cos(math.radians(self.weapon_angle))
        
        # Основной наконечник с контуром
        pygame.draw.line(screen, (40, 40, 40), end_pos, (tip_x, tip_y), shaft_width + 6)  # Темный контур
        pygame.draw.line(screen, (180, 180, 180), end_pos, (tip_x, tip_y), shaft_width + 2)  # Основной наконечник
        
        # Зазубрины наконечника
        barb_length = 12
        barb_left_x = end_pos[0] + barb_length * math.sin(math.radians(self.weapon_angle + 135))
        barb_left_y = end_pos[1] - barb_length * math.cos(math.radians(self.weapon_angle + 135))
        barb_right_x = end_pos[0] + barb_length * math.sin(math.radians(self.weapon_angle - 135))
        barb_right_y = end_pos[1] - barb_length * math.cos(math.radians(self.weapon_angle - 135))
        
        pygame.draw.line(screen, (40, 40, 40), end_pos, (barb_left_x, barb_left_y), shaft_width + 2)
        pygame.draw.line(screen, (160, 160, 160), end_pos, (barb_left_x, barb_left_y), shaft_width)
        pygame.draw.line(screen, (40, 40, 40), end_pos, (barb_right_x, barb_right_y), shaft_width + 2)
        pygame.draw.line(screen, (160, 160, 160), end_pos, (barb_right_x, barb_right_y), shaft_width)
        
        # Острие наконечника
        point_tip_x = tip_x + 10 * math.sin(math.radians(self.weapon_angle))
        point_tip_y = tip_y - 10 * math.cos(math.radians(self.weapon_angle))
        
        pygame.draw.polygon(screen, (40, 40, 40), 
                          [(point_tip_x, point_tip_y), 
                           (tip_x + 4 * math.cos(math.radians(self.weapon_angle)), tip_y + 4 * math.sin(math.radians(self.weapon_angle))),
                           (tip_x - 4 * math.cos(math.radians(self.weapon_angle)), tip_y - 4 * math.sin(math.radians(self.weapon_angle)))])
        pygame.draw.polygon(screen, (240, 240, 240), 
                          [(point_tip_x, point_tip_y), 
                           (tip_x + 3 * math.cos(math.radians(self.weapon_angle)), tip_y + 3 * math.sin(math.radians(self.weapon_angle))),
                           (tip_x - 3 * math.cos(math.radians(self.weapon_angle)), tip_y - 3 * math.sin(math.radians(self.weapon_angle)))])
        
        # Яркий блик на наконечнике
        pygame.draw.line(screen, (255, 255, 255), end_pos, (tip_x, tip_y), 3)

    def draw_weapon(self, screen):
        start_pos, end_pos = self.get_weapon_line()
        
        if self.weapon_type == "sword":
            self.draw_pixel_sword(screen, start_pos, end_pos)
        elif self.weapon_type == "spear":
            self.draw_pixel_spear(screen, start_pos, end_pos)
        # Новые типы оружия будут добавлены в дочерних классах

    def draw(self, screen):
        # Цвет шарика с эффектом неуязвимости
        ball_color = self.color
        if self.is_invulnerable and (self.invulnerable_timer // 3) % 2:
            ball_color = tuple(min(255, c + 80) for c in self.color)

        # Рисуем оружие ПОД шариком
        self.draw_weapon(screen)
        
        # Рисуем шарик с вращением
        pygame.draw.circle(screen, ball_color, self.rect.center, self.radius)
        
        # Добавляем линию для показа вращения
        line_length = self.radius - 5
        line_end_x = self.rect.centerx + line_length * math.cos(math.radians(self.angle))
        line_end_y = self.rect.centery + line_length * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, (255, 255, 255), self.rect.center, (line_end_x, line_end_y), 3)

        # Здоровье на шарике
        if self.health > 0:
            health_text = f"{int(self.health)}"
            font = pygame.font.Font(None, 28)
            text_surface = font.render(health_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.rect.center)
            
            shadow_surface = font.render(health_text, True, (0, 0, 0))
            shadow_rect = text_surface.get_rect(center=(self.rect.center[0] + 2, self.rect.center[1] + 2))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)