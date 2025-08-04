# balls/usa_ball.py - ОБНОВЛЕННАЯ ВЕРСИЯ (ВИЗУАЛ)
from .base_fighter import FightingBall
import pygame
import math
import random

class USABall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255),
                         name="USA", weapon_type="revolver")

        self.stats = {'damage': 8, 'range': 250, 'speed': 4, 'radius': self.radius}

        self.bullets = 6
        self.max_bullets = 6
        self.reload_timer = 0
        self.reload_time = 120
        self.shoot_cooldown = 0
        self.shoot_cooldown_time = 10

        self.flying_bullets = []
        self.muzzle_flash_timer = 0
        self.shell_casings = []

    def shoot(self, target):
        """Стреляет из револьвера"""
        if self.bullets > 0 and self.shoot_cooldown <= 0 and self.reload_timer <= 0:
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance > 0:
                bullet_speed = 15
                bullet = {
                    'x': self.rect.centerx, 'y': self.rect.centery,
                    'vx': (dx / distance) * bullet_speed, 'vy': (dy / distance) * bullet_speed,
                    'lifetime': 180
                }
                self.flying_bullets.append(bullet)

                self.bullets -= 1
                self.shoot_cooldown = self.shoot_cooldown_time
                self.muzzle_flash_timer = 8

                casing = {
                    'x': self.rect.centerx + random.uniform(-5, 5), 'y': self.rect.centery + random.uniform(-5, 5),
                    'vx': random.uniform(-2, 2), 'vy': random.uniform(-4, -1),
                    'rotation': random.uniform(0, 360), 'lifetime': 180
                }
                self.shell_casings.append(casing)

                if self.bullets <= 0:
                    self.reload_timer = self.reload_time
                return True
        return False

    def update_bullets(self, target):
        """Обновляет полет пуль и проверяет попадания"""
        for bullet in self.flying_bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['lifetime'] -= 1

            bullet_rect = pygame.Rect(bullet['x'] - 4, bullet['y'] - 4, 8, 8)
            if bullet_rect.colliderect(target.rect):
                target.take_damage(self.stats['damage'])
                if bullet in self.flying_bullets:
                    self.flying_bullets.remove(bullet)
                continue
            
            if bullet['lifetime'] <= 0:
                if bullet in self.flying_bullets:
                    self.flying_bullets.remove(bullet)

    def update_casings(self):
        """Обновляет гильзы"""
        for casing in self.shell_casings[:]:
            casing['x'] += casing['vx']
            casing['y'] += casing['vy']
            casing['vy'] += 0.2
            casing['rotation'] += casing['vx'] * 5
            casing['lifetime'] -= 1
            if casing['lifetime'] <= 0:
                self.shell_casings.remove(casing)

    def update(self, other_ball=None):
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.muzzle_flash_timer > 0: self.muzzle_flash_timer -= 1

        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.bullets = self.max_bullets

        if other_ball and self.bullets > 0 and self.shoot_cooldown <= 0 and self.reload_timer <= 0:
            distance = math.hypot(other_ball.rect.centerx - self.rect.centerx, other_ball.rect.centery - self.rect.centery)
            if distance < 350:
                self.shoot(other_ball)

        if other_ball: self.update_bullets(other_ball)
        self.update_casings()
        super().update(other_ball)

    def draw_flag_pattern(self, screen):
        """Рисует правильный флаг США с помощью маски"""
        center_x, center_y = self.rect.center
        radius = self.radius
        
        flag_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        stripe_height = (radius * 2) / 13
        for i in range(13):
            color = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
            pygame.draw.rect(flag_surface, color, (0, i * stripe_height, radius * 2, stripe_height))

        canton_width = radius * 1.0
        canton_height = stripe_height * 7
        pygame.draw.rect(flag_surface, (60, 59, 110), (0, 0, canton_width, canton_height))
        
        star_rows = 9
        star_cols = 11
        for row in range(star_rows):
            for col in range(row % 2, star_cols, 2):
                star_x = canton_width * col / star_cols + 5
                star_y = canton_height * row / star_rows + 4
                if star_x < canton_width - 5 and star_y < canton_height - 5:
                    pygame.draw.circle(flag_surface, (255, 255, 255), (star_x, star_y), 2)

        mask_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (radius, radius), radius)
        flag_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        screen.blit(flag_surface, (center_x - radius, center_y - radius))

    def draw_revolver(self, screen):
        """Рисует БОЛЬШОЙ револьвер, который шар 'держит' в руках"""
        center_x, center_y = self.rect.center
        
        mouse_pos = pygame.mouse.get_pos()
        angle = math.degrees(math.atan2(mouse_pos[1] - center_y, mouse_pos[0] - center_x))
        
        # ИЗМЕНЕНИЕ: Смещение увеличено с 15 до 35, чтобы вынести револьвер за пределы шара
        revolver_offset = 35
        revolver_offset_x = revolver_offset * math.cos(math.radians(angle))
        revolver_offset_y = revolver_offset * math.sin(math.radians(angle))
        gun_x, gun_y = center_x + revolver_offset_x, center_y + revolver_offset_y

        # ИЗМЕНЕНИЕ: Поверхность и все элементы револьвера увеличены
        gun_surface = pygame.Surface((90, 60), pygame.SRCALPHA)
        gs_center_x, gs_center_y = 35, 30
        
        # Ствол
        pygame.draw.rect(gun_surface, (80, 80, 80), (gs_center_x, gs_center_y - 5, 40, 10))
        # Рукоять
        handle_poly = [(gs_center_x - 10, gs_center_y), (gs_center_x - 20, gs_center_y + 25), (gs_center_x + 5, gs_center_y + 25), (gs_center_x + 10, gs_center_y + 10)]
        pygame.draw.polygon(gun_surface, (139, 69, 19), handle_poly)
        pygame.draw.polygon(gun_surface, (80, 50, 20), handle_poly, 2)
        # Барабан
        pygame.draw.circle(gun_surface, (140, 140, 140), (gs_center_x, gs_center_y), 12)
        pygame.draw.circle(gun_surface, (80, 80, 80), (gs_center_x, gs_center_y), 12, 2)
        # Индикатор патронов
        for i in range(self.max_bullets):
            bullet_angle = (360 / self.max_bullets) * i
            bx = gs_center_x + 9 * math.cos(math.radians(bullet_angle))
            by = gs_center_y + 9 * math.sin(math.radians(bullet_angle))
            color = (255, 215, 0) if i < self.bullets else (50, 50, 50)
            pygame.draw.circle(gun_surface, color, (bx, by), 3)
            
        rotated_gun = pygame.transform.rotate(gun_surface, -angle)
        new_rect = rotated_gun.get_rect(center=(gun_x, gun_y))
        screen.blit(rotated_gun, new_rect)

    def draw_muzzle_flash(self, screen):
        """Рисует вспышку выстрела"""
        if self.muzzle_flash_timer > 0:
            center_x, center_y = self.rect.center
            mouse_pos = pygame.mouse.get_pos()
            angle = math.atan2(mouse_pos[1] - center_y, mouse_pos[0] - center_x)
            
            # Смещаем вспышку к концу ствола
            flash_start_offset = self.radius + 40
            flash_size = self.muzzle_flash_timer * 4
            start_pos_x = center_x + flash_start_offset * math.cos(angle)
            start_pos_y = center_y + flash_start_offset * math.sin(angle)
            
            points = []
            for i in range(5):
                a = angle + random.uniform(-0.5, 0.5)
                r = flash_size * (1 - (self.muzzle_flash_timer / 8))
                points.append((start_pos_x + r * math.cos(a), start_pos_y + r * math.sin(a)))
            
            if len(points) > 2:
                 pygame.draw.polygon(screen, (255, 255, 100), points)

    def draw_bullets(self, screen):
        """Рисует пули"""
        for bullet in self.flying_bullets:
            pygame.draw.circle(screen, (255, 255, 0), (int(bullet['x']), int(bullet['y'])), 5)
            pygame.draw.circle(screen, (255, 150, 0), (int(bullet['x']), int(bullet['y'])), 3)
            trail_x = bullet['x'] - bullet['vx']
            trail_y = bullet['y'] - bullet['vy']
            pygame.draw.line(screen, (255, 200, 0, 150), (bullet['x'], bullet['y']), (trail_x, trail_y), 3)

    def draw_casings(self, screen):
        """Рисует гильзы"""
        for casing in self.shell_casings:
            pygame.draw.rect(screen, (255, 215, 0), (int(casing['x']), int(casing['y']), 5, 3))

    def draw_reload_indicator(self, screen):
        """Рисует индикатор перезарядки"""
        if self.reload_timer > 0:
            center_x, center_y = self.rect.center
            progress = 1.0 - (self.reload_timer / self.reload_time)
            radius = self.radius + 5 
            rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)
            pygame.draw.arc(screen, (255, 255, 0), rect, math.pi/2, math.pi/2 + progress * 2 * math.pi, 3)

    def draw(self, screen):
        self.draw_flag_pattern(screen)
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.radius, 3)
        self.draw_revolver(screen)
        self.draw_muzzle_flash(screen)
        self.draw_bullets(screen)
        self.draw_casings(screen)
        self.draw_reload_indicator(screen)
        
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
        self.shoot_cooldown_time = max(5, self.shoot_cooldown_time - 1)