# balls/usa_ball.py
from .base_fighter import FightingBall
import pygame
import math
import random

class USABall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255), 
                         name="USA", weapon_type="revolver")
        
        self.stats = {'damage': 8, 'range': 250, 'speed': 4, 'radius': self.radius}
        
        # Параметры револьвера
        self.bullets = 6  # Количество пуль в барабане
        self.max_bullets = 6
        self.reload_timer = 0
        self.reload_time = 120  # 2 секунды перезарядка
        self.shoot_cooldown = 0
        self.shoot_cooldown_time = 10  # 0.16 секунды между выстрелами
        
        # Летящие пули
        self.flying_bullets = []
        
        # Эффекты выстрела
        self.muzzle_flash_timer = 0
        self.shell_casings = []  # Гильзы

    def shoot(self, target):
        """Стреляет из револьвера"""
        if self.bullets > 0 and self.shoot_cooldown <= 0 and self.reload_timer <= 0:
            # Направление к цели
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Создаем пулю
                bullet_speed = 15
                bullet = {
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vx': (dx / distance) * bullet_speed,
                    'vy': (dy / distance) * bullet_speed,
                    'lifetime': 180  # 3 секунды полета
                }
                self.flying_bullets.append(bullet)
                
                self.bullets -= 1
                self.shoot_cooldown = self.shoot_cooldown_time
                self.muzzle_flash_timer = 8  # Эффект вспышки выстрела
                
                # Добавляем гильзу
                casing = {
                    'x': self.rect.centerx + random.uniform(-5, 5),
                    'y': self.rect.centery + random.uniform(-5, 5),
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-4, -1),
                    'rotation': random.uniform(0, 360),
                    'lifetime': 180
                }
                self.shell_casings.append(casing)
                
                # Если патроны закончились, начинаем перезарядку
                if self.bullets <= 0:
                    self.reload_timer = self.reload_time
                
                return True
        return False

    def update_bullets(self, target):
        """Обновляет полет пуль и проверяет попадания"""
        for bullet in self.flying_bullets[:]:
            # Обновляем позицию
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['lifetime'] -= 1
            
            # Проверка попадания в цель
            bullet_rect = pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6)
            if bullet_rect.colliderect(target.rect):
                target.take_damage(self.stats['damage'])
                self.flying_bullets.remove(bullet)
                continue
            
            # Проверка на выход за границы или время жизни
            from config import ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT
            if (bullet['x'] < ARENA_X or bullet['x'] > ARENA_X + ARENA_WIDTH or
                bullet['y'] < ARENA_Y or bullet['y'] > ARENA_Y + ARENA_HEIGHT or
                bullet['lifetime'] <= 0):
                self.flying_bullets.remove(bullet)

    def update_casings(self):
        """Обновляет гильзы"""
        for casing in self.shell_casings[:]:
            casing['x'] += casing['vx']
            casing['y'] += casing['vy']
            casing['vy'] += 0.2  # Гравитация
            casing['rotation'] += casing['vx'] * 5
            casing['lifetime'] -= 1
            
            if casing['lifetime'] <= 0:
                self.shell_casings.remove(casing)

    def update(self, other_ball=None):
        # Обновляем кулдауны
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.bullets = self.max_bullets  # Перезарядились
        
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= 1
        
        # Автоматическая стрельба
        if other_ball and self.bullets > 0 and self.shoot_cooldown <= 0 and self.reload_timer <= 0:
            distance = math.sqrt((other_ball.rect.centerx - self.rect.centerx)**2 + 
                               (other_ball.rect.centery - self.rect.centery)**2)
            if distance < 350:  # В пределах досягаемости
                self.shoot(other_ball)
        
        # Обновляем пули
        if other_ball:
            self.update_bullets(other_ball)
        
        # Обновляем гильзы
        self.update_casings()
        
        # Базовое обновление
        super().update(other_ball)

    def draw_revolver(self, screen, x, y):
        """Рисует револьвер"""
        # Рукоять
        handle_points = [
            (x - 3, y + 10),
            (x + 3, y + 10),
            (x + 5, y + 5),
            (x + 5, y - 2),
            (x - 5, y - 2),
            (x - 5, y + 5)
        ]
        pygame.draw.polygon(screen, (101, 67, 33), handle_points)  # Деревянная рукоять
        pygame.draw.polygon(screen, (60, 40, 20), handle_points, 2)  # Контур
        
        # Барабан
        pygame.draw.circle(screen, (150, 150, 150), (x, y), 8)  # Основной барабан
        pygame.draw.circle(screen, (100, 100, 100), (x, y), 8, 2)  # Контур барабана
        
        # Ствол
        barrel_rect = pygame.Rect(x - 2, y - 12, 4, 12)
        pygame.draw.rect(screen, (120, 120, 120), barrel_rect)
        pygame.draw.rect(screen, (80, 80, 80), barrel_rect, 1)
        
        # Спусковая скоба
        trigger_guard_points = [
            (x - 3, y + 2),
            (x + 3, y + 2),
            (x + 3, y + 6),
            (x - 3, y + 6)
        ]
        pygame.draw.polygon(screen, (120, 120, 120), trigger_guard_points)
        pygame.draw.polygon(screen, (80, 80, 80), trigger_guard_points, 1)
        
        # Индикатор патронов
        for i in range(6):
            angle = i * 60
            bullet_x = x + 6 * math.cos(math.radians(angle))
            bullet_y = y + 6 * math.sin(math.radians(angle))
            
            if i < self.bullets:
                color = (255, 215, 0)  # Золотой для патронов
            else:
                color = (60, 60, 60)   # Темный для пустых
            
            pygame.draw.circle(screen, color, (int(bullet_x), int(bullet_y)), 2)

    def draw_muzzle_flash(self, screen):
        """Рисует вспышку выстрела"""
        if self.muzzle_flash_timer > 0:
            center_x, center_y = self.rect.center
            flash_size = self.muzzle_flash_timer * 3
            
            # Яркая вспышка
            flash_surface = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            flash_color = (255, 255, 100, 180)
            pygame.draw.circle(flash_surface, flash_color, (flash_size, flash_size), flash_size)
            screen.blit(flash_surface, (center_x - flash_size, center_y - flash_size - 15))

    def draw_bullets(self, screen):
        """Рисует летящие пули"""
        for bullet in self.flying_bullets:
            # Пуля с огненным следом
            pygame.draw.circle(screen, (255, 255, 0), (int(bullet['x']), int(bullet['y'])), 3)
            pygame.draw.circle(screen, (255, 100, 0), (int(bullet['x']), int(bullet['y'])), 2)
            
            # След пули
            trail_x = bullet['x'] - bullet['vx'] * 0.5
            trail_y = bullet['y'] - bullet['vy'] * 0.5
            pygame.draw.line(screen, (255, 200, 0), (bullet['x'], bullet['y']), (trail_x, trail_y), 2)

    def draw_casings(self, screen):
        """Рисует гильзы"""
        for casing in self.shell_casings:
            # Простая гильза
            casing_rect = pygame.Rect(int(casing['x']) - 2, int(casing['y']) - 1, 4, 2)
            pygame.draw.rect(screen, (255, 215, 0), casing_rect)
            pygame.draw.rect(screen, (200, 170, 0), casing_rect, 1)

    def draw_reload_indicator(self, screen):
        """Показывает индикатор перезарядки"""
        if self.reload_timer > 0:
            center_x, center_y = self.rect.center
            progress = 1.0 - (self.reload_timer / self.reload_time)
            
            # Круговая полоса перезарядки
            arc_rect = pygame.Rect(center_x - self.radius - 10, center_y - self.radius - 10, 
                                  (self.radius + 10) * 2, (self.radius + 10) * 2)
            end_angle = progress * 360
            
            # Рисуем дугу перезарядки
            if progress > 0:
                points = [(center_x, center_y)]
                for angle in range(0, int(end_angle), 5):
                    x = center_x + (self.radius + 5) * math.cos(math.radians(angle - 90))
                    y = center_y + (self.radius + 5) * math.sin(math.radians(angle - 90))
                    points.append((x, y))
                
                if len(points) > 2:
                    pygame.draw.polygon(screen, (255, 255, 0, 100), points)

    def draw(self, screen):
        # Рисуем американский флаг как тело шарика
        center_x, center_y = self.rect.center
        
        # Основной круг (белый фон)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius)
        
        # Красные полосы
        stripe_height = self.radius * 2 // 13
        for i in range(0, 13, 2):  # Только нечетные полосы (красные)
            y_start = center_y - self.radius + i * stripe_height
            stripe_rect = pygame.Rect(center_x - self.radius, y_start, self.radius * 2, stripe_height)
            pygame.draw.rect(screen, (178, 34, 52), stripe_rect)
        
        # Обрезаем по кругу
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius, 0)
        
        # Синий квадрат с звездами (упрощенно)
        canton_size = self.radius // 2
        canton_rect = pygame.Rect(center_x - self.radius, center_y - self.radius, canton_size, canton_size)
        pygame.draw.rect(screen, (60, 59, 110), canton_rect)
        
        # Упрощенные звезды (белые точки)
        for i in range(3):
            for j in range(3):
                star_x = center_x - self.radius + (canton_size // 4) * (i + 1)
                star_y = center_y - self.radius + (canton_size // 4) * (j + 1)
                pygame.draw.circle(screen, (255, 255, 255), (star_x, star_y), 2)
        
        # Контур шарика
        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), self.radius, 3)
        
        # Рисуем револьвер
        self.draw_revolver(screen, center_x + 15, center_y - 10)
        
        # Эффекты
        self.draw_muzzle_flash(screen)
        self.draw_bullets(screen)
        self.draw_casings(screen)
        self.draw_reload_indicator(screen)
        
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
        # Увеличиваем урон и скорость стрельбы
        self.stats['damage'] += 1.0
        self.shoot_cooldown_time = max(5, self.shoot_cooldown_time - 1)  # Быстрее стреляет