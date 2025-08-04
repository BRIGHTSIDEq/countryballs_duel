# balls/france_ball.py - ОБНОВЛЕННАЯ ВЕРСИЯ
from .base_fighter import FightingBall
import pygame
import math
import random

class FranceBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=45, color=(255, 255, 255),
                         name="France", weapon_type="baguette")

        self.stats = {'damage': 10, 'range': 80, 'speed': 3, 'radius': self.radius}

        # Параметры багета
        self.baguette_length = 70
        self.baguette_width = 10
        self.baguette_angle = 0 # Угол вращения багета

        self.deflect_cooldown = 0
        self.deflect_cooldown_max = 30
        self.block_effect_timer = 0
        self.deflected_bullets = []

    def check_bullet_deflection(self, enemy_bullets):
        """Проверяет и отражает пули противника"""
        if self.deflect_cooldown > 0: return False
        
        baguette_rect = self.get_weapon_rect()
        deflected_any = False
        
        for bullet in enemy_bullets[:]:
            bullet_rect = pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6)
            if baguette_rect.colliderect(bullet_rect):
                self.deflect_bullet(bullet)
                enemy_bullets.remove(bullet)
                deflected_any = True
        
        if deflected_any:
            self.deflect_cooldown = self.deflect_cooldown_max
            self.block_effect_timer = 20
            return True
        return False

    def deflect_bullet(self, bullet):
        """Отражает пулю обратно"""
        bullet['vx'] = -bullet['vx'] * 1.2
        bullet['vy'] = -bullet['vy'] * 1.2
        bullet['lifetime'] = 120
        self.deflected_bullets.append(bullet)

    def get_weapon_rect(self):
        """Возвращает прямоугольник багета для столкновений"""
        center_x, center_y = self.rect.center
        
        # Позиция багета сверху шара
        weapon_center_y = center_y - self.radius - self.baguette_length / 2
        
        # Создаем повернутый прямоугольник
        angle_rad = math.radians(self.baguette_angle)
        
        points = []
        half_w, half_l = self.baguette_width / 2, self.baguette_length / 2
        
        # 4 угла прямоугольника
        corners = [(-half_l, -half_w), (half_l, -half_w), (half_l, half_w), (-half_l, half_w)]
        
        for l, w in corners:
            # Вращаем и смещаем
            x = (l * math.cos(angle_rad) - w * math.sin(angle_rad)) + center_x
            y = (l * math.sin(angle_rad) + w * math.cos(angle_rad)) + (center_y - self.radius - 10) # Смещаем над шаром
            points.append((x,y))

        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


    def update(self, other_ball=None):
        # Багет вращается в направлении движения
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            target_angle = math.degrees(math.atan2(-self.vy, self.vx))
            # Плавное вращение к цели
            angle_diff = (target_angle - self.baguette_angle + 180) % 360 - 180
            self.baguette_angle += angle_diff * 0.2
        
        if self.deflect_cooldown > 0: self.deflect_cooldown -= 1
        if self.block_effect_timer > 0: self.block_effect_timer -= 1
        
        if other_ball and hasattr(other_ball, 'flying_bullets'):
            self.check_bullet_deflection(other_ball.flying_bullets)
        
        for bullet in self.deflected_bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['lifetime'] -= 1
            
            if other_ball and pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6).colliderect(other_ball.rect):
                other_ball.take_damage(self.stats['damage'])
                self.deflected_bullets.remove(bullet)
                continue
            
            if bullet['lifetime'] <= 0: self.deflected_bullets.remove(bullet)
        
        super().update(other_ball)

    def attack(self, target):
        """Атака с сильным отбросом"""
        if not self.can_attack(): return False

        target.last_attacker_pos = self.rect.center
        success = target.take_damage(self.stats['damage'])
        if success:
            self.attack_cooldown = self.attack_cooldown_duration
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                knockback_force = 12
                target.vx += (dx / distance) * knockback_force
                target.vy += (dy / distance) * knockback_force - 3
            self.on_successful_attack(target)
        return success

    def draw_flag_pattern(self, screen):
        """Рисует правильный флаг Франции с помощью маски"""
        center_x, center_y = self.rect.center
        radius = self.radius

        flag_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        stripe_width = (radius * 2) / 3

        pygame.draw.rect(flag_surface, (0, 85, 164), (0, 0, stripe_width, radius * 2))
        pygame.draw.rect(flag_surface, (255, 255, 255), (stripe_width, 0, stripe_width, radius * 2))
        pygame.draw.rect(flag_surface, (239, 65, 53), (stripe_width * 2, 0, stripe_width, radius * 2))

        mask_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (radius, radius), radius)
        flag_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        screen.blit(flag_surface, (center_x - radius, center_y - radius))

    def draw_detailed_baguette(self, screen):
        """Рисует новый детализированный багет, который вращается"""
        center_x, center_y = self.rect.center
        
        # Багет рисуется на отдельной поверхности для удобства вращения
        baguette_surf = pygame.Surface((self.baguette_length + 20, self.baguette_width + 10), pygame.SRCALPHA)
        b_center_x, b_center_y = (self.baguette_length + 20)//2, (self.baguette_width + 10)//2

        # Основная форма багета
        base_color = (210, 180, 140)
        dark_color = (139, 115, 85)
        baguette_rect = pygame.Rect(b_center_x - self.baguette_length//2, b_center_y - self.baguette_width//2, self.baguette_length, self.baguette_width)
        pygame.draw.rect(baguette_surf, base_color, baguette_rect, border_radius=5)
        pygame.draw.rect(baguette_surf, dark_color, baguette_rect, 1, border_radius=5)
        
        # Насечки
        for i in range(1, 5):
            x = b_center_x - self.baguette_length//2 + (i * self.baguette_length / 5)
            pygame.draw.line(baguette_surf, dark_color, (x-5, b_center_y-5), (x+5, b_center_y+5), 1)

        # Вращаем багет
        rotated_baguette = pygame.transform.rotate(baguette_surf, -self.baguette_angle)
        # Позиционируем над шаром
        new_rect = rotated_baguette.get_rect(center=(center_x, center_y - self.radius - 15))
        screen.blit(rotated_baguette, new_rect)

        # Эффект блокировки
        if self.block_effect_timer > 0:
            for _ in range(5):
                angle = self.baguette_angle + random.uniform(-45, 45)
                rad = math.radians(angle)
                spark_x = new_rect.centerx + random.uniform(-20, 20) * math.cos(rad)
                spark_y = new_rect.centery + random.uniform(-20, 20) * math.sin(rad)
                pygame.draw.circle(screen, random.choice([(255,255,100), (255,255,255)]), (spark_x, spark_y), random.randint(1,4))

    def draw_deflected_bullets(self, screen):
        """Рисует отраженные пули"""
        for bullet in self.deflected_bullets:
            pygame.draw.circle(screen, (100, 150, 255), (int(bullet['x']), int(bullet['y'])), 5)
            pygame.draw.circle(screen, (200, 220, 255), (int(bullet['x']), int(bullet['y'])), 2)

    def draw(self, screen):
        self.draw_flag_pattern(screen)
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, self.radius, 3)
        
        self.draw_detailed_baguette(screen)
        self.draw_deflected_bullets(screen)
        
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
        self.stats['damage'] += 2.0
        self.baguette_length = min(100, self.baguette_length + 5)
        self.baguette_width = min(15, self.baguette_width + 1)