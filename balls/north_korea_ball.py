# balls/north_korea_ball.py
from .base_fighter import FightingBall
import pygame
import math
import random

class NorthKoreaBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255), 
                         name="North Korea", weapon_type="missile")
        
        self.stats = {'damage': 15, 'range': 300, 'speed': 2, 'radius': self.radius}
        
        # Параметры ракеты
        self.missile_cooldown = 0
        self.missile_cooldown_max = 300  # 5 секунд между ракетами
        self.missile_damage = 15
        self.explosion_radius = 60
        
        # Летящие ракеты
        self.missiles = []
        
        # Эффекты взрывов
        self.explosions = []
        
        # Угрожающее поведение
        self.threat_level = 0
        self.warning_timer = 0

    def launch_missile(self, target):
        """Запускает ракету в цель"""
        if self.missile_cooldown <= 0:
            # Направление к цели с некоторой неточностью
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Добавляем случайную неточность
                accuracy = 0.8 + random.uniform(-0.2, 0.2)
                
                missile_speed = 6
                missile = {
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vx': (dx / distance) * missile_speed * accuracy,
                    'vy': (dy / distance) * missile_speed * accuracy,
                    'target_x': target.rect.centerx,
                    'target_y': target.rect.centery,
                    'lifetime': 600,  # 10 секунд полета
                    'trail': [],  # След ракеты
                    'rotation': math.degrees(math.atan2(dy, dx))
                }
                self.missiles.append(missile)
                self.missile_cooldown = self.missile_cooldown_max
                
                # Угрожающее предупреждение
                self.threat_level = min(5, self.threat_level + 1)
                self.warning_timer = 180  # 3 секунды предупреждения
                
                return True
        return False

    def update_missiles(self, target):
        """Обновляет полет ракет и взрывы"""
        for missile in self.missiles[:]:
            # Обновляем позицию
            missile['x'] += missile['vx']
            missile['y'] += missile['vy']
            missile['lifetime'] -= 1
            
            # Добавляем в след
            missile['trail'].append((missile['x'], missile['y']))
            if len(missile['trail']) > 10:
                missile['trail'].pop(0)
            
            # Проверяем попадание в область цели или землю
            target_distance = math.sqrt((missile['x'] - target.rect.centerx)**2 + 
                                      (missile['y'] - target.rect.centery)**2)
            
            # Взрыв при приближении к цели или окончании времени
            if target_distance < 30 or missile['lifetime'] <= 0:
                self.create_explosion(missile['x'], missile['y'], target)
                self.missiles.remove(missile)
                continue
            
            # Проверка на выход за границы арены - тоже взрыв
            from config import ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT
            if (missile['x'] < ARENA_X or missile['x'] > ARENA_X + ARENA_WIDTH or
                missile['y'] < ARENA_Y or missile['y'] > ARENA_Y + ARENA_HEIGHT):
                self.create_explosion(missile['x'], missile['y'], target)
                self.missiles.remove(missile)

    def create_explosion(self, x, y, target):
        """Создает взрыв ракеты"""
        explosion = {
            'x': x,
            'y': y,
            'radius': 0,
            'max_radius': self.explosion_radius,
            'timer': 30,  # 0.5 секунды взрыва
            'sparks': []
        }
        
        # Создаем искры взрыва
        for i in range(15):
            spark = {
                'x': x,
                'y': y,
                'vx': random.uniform(-8, 8),
                'vy': random.uniform(-8, 8),
                'lifetime': random.randint(20, 40),
                'color': random.choice([(255, 100, 0), (255, 200, 0), (255, 255, 100)])
            }
            explosion['sparks'].append(spark)
        
        self.explosions.append(explosion)
        
        # Проверяем урон цели
        distance_to_target = math.sqrt((x - target.rect.centerx)**2 + (y - target.rect.centery)**2)
        if distance_to_target <= self.explosion_radius:
            # Урон зависит от расстояния до центра взрыва
            damage_ratio = 1.0 - (distance_to_target / self.explosion_radius)
            actual_damage = self.missile_damage * damage_ratio
            target.take_damage(actual_damage)
            
            # Сильный отброс от взрыва
            if distance_to_target > 0:
                knockback_force = 15 * damage_ratio
                dx = target.rect.centerx - x
                dy = target.rect.centery - y
                target.vx += (dx / distance_to_target) * knockback_force
                target.vy += (dy / distance_to_target) * knockback_force - 3

    def update_explosions(self):
        """Обновляет эффекты взрывов"""
        for explosion in self.explosions[:]:
            explosion['timer'] -= 1
            explosion['radius'] = min(explosion['max_radius'], 
                                    explosion['max_radius'] * (1 - explosion['timer'] / 30))
            
            # Обновляем искры
            for spark in explosion['sparks'][:]:
                spark['x'] += spark['vx']
                spark['y'] += spark['vy']
                spark['vy'] += 0.3  # Гравитация
                spark['vx'] *= 0.98  # Замедление
                spark['lifetime'] -= 1
                
                if spark['lifetime'] <= 0:
                    explosion['sparks'].remove(spark)
            
            if explosion['timer'] <= 0:
                self.explosions.remove(explosion)

    def update(self, other_ball=None):
        # Обновляем кулдаун ракеты
        if self.missile_cooldown > 0:
            self.missile_cooldown -= 1
        
        # Обновляем таймер предупреждения
        if self.warning_timer > 0:
            self.warning_timer -= 1
        
        # Автоматический запуск ракет
        if other_ball and self.missile_cooldown <= 0:
            distance = math.sqrt((other_ball.rect.centerx - self.rect.centerx)**2 + 
                               (other_ball.rect.centery - self.rect.centery)**2)
            if distance > 100:  # Не запускаем если слишком близко
                self.launch_missile(other_ball)
        
        # Обновляем ракеты и взрывы
        if other_ball:
            self.update_missiles(other_ball)
        self.update_explosions()
        
        # Базовое обновление
        super().update(other_ball)

    def draw_missile(self, screen, missile):
        """Рисует ракету"""
        x, y = missile['x'], missile['y']
        rotation = missile['rotation']
        
        # Тело ракеты
        missile_length = 25
        missile_width = 6
        
        # Вычисляем точки ракеты
        cos_r = math.cos(math.radians(rotation))
        sin_r = math.sin(math.radians(rotation))
        
        # Основные точки ракеты
        nose_x = x + missile_length * cos_r
        nose_y = y + missile_length * sin_r
        
        tail_x = x - missile_length * cos_r
        tail_y = y - missile_length * sin_r
        
        # Боковые точки
        side1_x = x + missile_width * math.cos(math.radians(rotation + 90))
        side1_y = y + missile_width * math.sin(math.radians(rotation + 90))
        side2_x = x - missile_width * math.cos(math.radians(rotation + 90))
        side2_y = y - missile_width * math.sin(math.radians(rotation + 90))
        
        # Рисуем тело ракеты
        missile_points = [
            (nose_x, nose_y),
            (side1_x, side1_y),
            (tail_x, tail_y),
            (side2_x, side2_y)
        ]
        
        pygame.draw.polygon(screen, (100, 100, 100), missile_points)  # Корпус
        pygame.draw.polygon(screen, (60, 60, 60), missile_points, 2)   # Контур
        
        # Красная боеголовка
        nose_points = [
            (nose_x, nose_y),
            (nose_x - 10 * cos_r + 3 * math.cos(math.radians(rotation + 90)),
             nose_y - 10 * sin_r + 3 * math.sin(math.radians(rotation + 90))),
            (nose_x - 10 * cos_r - 3 * math.cos(math.radians(rotation + 90)),
             nose_y - 10 * sin_r - 3 * math.sin(math.radians(rotation + 90)))
        ]
        pygame.draw.polygon(screen, (200, 0, 0), nose_points)
        
        # Огонь из двигателя
        flame_length = 15
        flame_x = tail_x - flame_length * cos_r
        flame_y = tail_y - flame_length * sin_r
        
        flame_points = [
            (tail_x, tail_y),
            (flame_x + 5 * math.cos(math.radians(rotation + 90)),
             flame_y + 5 * math.sin(math.radians(rotation + 90))),
            (flame_x, flame_y),
            (flame_x - 5 * math.cos(math.radians(rotation + 90)),
             flame_y - 5 * math.sin(math.radians(rotation + 90)))
        ]
        pygame.draw.polygon(screen, (255, 100, 0), flame_points)
        
        # След ракеты
        if len(missile['trail']) > 1:
            for i in range(len(missile['trail']) - 1):
                alpha = int(255 * (i + 1) / len(missile['trail']) * 0.5)
                trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (255, 200, 0, alpha), (2, 2), 2)
                screen.blit(trail_surface, (missile['trail'][i][0] - 2, missile['trail'][i][1] - 2))

    def draw_explosion(self, screen, explosion):
        """Рисует взрыв"""
        x, y = explosion['x'], explosion['y']
        radius = explosion['radius']
        
        # Главный взрыв
        if radius > 0:
            # Несколько кругов разного цвета для эффекта
            colors = [(255, 255, 255), (255, 200, 0), (255, 100, 0), (200, 0, 0)]
            radiuses = [radius, radius * 0.8, radius * 0.6, radius * 0.4]
            
            for color, exp_radius in zip(colors, radiuses):
                if exp_radius > 0:
                    explosion_surface = pygame.Surface((exp_radius * 2, exp_radius * 2), pygame.SRCALPHA)
                    alpha = int(200 * (explosion['timer'] / 30))
                    color_with_alpha = (*color, alpha)
                    pygame.draw.circle(explosion_surface, color_with_alpha, 
                                     (exp_radius, exp_radius), exp_radius)
                    screen.blit(explosion_surface, (x - exp_radius, y - exp_radius))
        
        # Искры
        for spark in explosion['sparks']:
            alpha = int(255 * (spark['lifetime'] / 40))
            spark_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            color_with_alpha = (*spark['color'], alpha)
            pygame.draw.circle(spark_surface, color_with_alpha, (3, 3), 3)
            screen.blit(spark_surface, (spark['x'] - 3, spark['y'] - 3))

    def draw_warning_indicator(self, screen):
        """Рисует индикатор готовности ракеты"""
        if self.missile_cooldown <= 60:  # Мигает последнюю секунду
            center_x, center_y = self.rect.center
            
            if (self.missile_cooldown // 10) % 2:
                warning_color = (255, 0, 0, 150)
                warning_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
                pygame.draw.circle(warning_surface, warning_color, 
                                 (self.radius * 1.5, self.radius * 1.5), self.radius + 10, 4)
                screen.blit(warning_surface, 
                          (center_x - self.radius * 1.5, center_y - self.radius * 1.5))
                
                # Текст предупреждения
                font = pygame.font.Font(None, 24)
                warning_text = "MISSILE READY"
                text_surface = font.render(warning_text, True, (255, 0, 0))
                text_rect = text_surface.get_rect(center=(center_x, center_y - self.radius - 20))
                screen.blit(text_surface, text_rect)

    def draw_flag_pattern(self, screen):
        """Рисует флаг Северной Кореи"""
        center_x, center_y = self.rect.center
        
        # Синие полосы (верх и низ)
        blue_height = self.radius // 3
        
        # Верхняя синяя полоса
        for angle in range(0, 360, 5):
            x = center_x + self.radius * math.cos(math.radians(angle))
            y = center_y + self.radius * math.sin(math.radians(angle))
            
            if y < center_y - blue_height:
                pygame.draw.line(screen, (0, 61, 165), (center_x, center_y), (x, y), 2)
        
        # Нижняя синяя полоса
        for angle in range(0, 360, 5):
            x = center_x + self.radius * math.cos(math.radians(angle))
            y = center_y + self.radius * math.sin(math.radians(angle))
            
            if y > center_y + blue_height:
                pygame.draw.line(screen, (0, 61, 165), (center_x, center_y), (x, y), 2)
        
        # Красная полоса (центр)
        pygame.draw.circle(screen, (237, 28, 36), (center_x, center_y), blue_height + 5)
        
        # Белые тонкие полосы
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius - 5, 2)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), blue_height + 10, 2)
        
        # Звезда в красном круге (упрощенно)
        star_size = self.radius // 4
        self.draw_star(screen, center_x - self.radius//2, center_y, star_size, (255, 255, 255))

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
        pygame.draw.polygon(screen, (200, 200, 200), points, 1)

    def draw(self, screen):
        # Рисуем флаг Северной Кореи как тело шарика
        center_x, center_y = self.rect.center
        
        # Основной фон (белый)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius)
        
        # Синие полосы (верх и низ)
        pygame.draw.circle(screen, (0, 61, 165), (center_x, center_y), self.radius)
        
        # Белые полосы
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius - 8)
        
        # Красная центральная полоса
        pygame.draw.circle(screen, (237, 28, 36), (center_x, center_y), self.radius - 16)
        
        # Белая полоса в центре красной
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius - 24)
        
        # Финальная красная полоса
        pygame.draw.circle(screen, (237, 28, 36), (center_x, center_y), self.radius - 32)
        
        # Белый круг со звездой
        star_circle_radius = self.radius // 3
        pygame.draw.circle(screen, (255, 255, 255), (center_x - self.radius//2, center_y), star_circle_radius)
        
        # Красная звезда
        star_size = star_circle_radius - 5
        self.draw_star(screen, center_x - self.radius//2, center_y, star_size, (237, 28, 36))
        
        # Контур шарика
        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), self.radius, 3)
        
        # Рисуем ракеты
        for missile in self.missiles:
            self.draw_missile(screen, missile)
        
        # Рисуем взрывы
        for explosion in self.explosions:
            self.draw_explosion(screen, explosion)
        
        # Индикатор готовности ракеты
        self.draw_warning_indicator(screen)
        
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
        # Увеличиваем мощность ракет
        self.missile_damage += 2
        self.explosion_radius = min(100, self.explosion_radius + 5)
        self.missile_cooldown_max = max(180, self.missile_cooldown_max - 15)  # Быстрее запускает