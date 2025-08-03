# balls/france_ball.py
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
        self.baguette_length = 60
        self.baguette_width = 8
        
        # Особенность: защита от пуль и сильный отброс
        self.deflect_cooldown = 0
        self.deflect_cooldown_max = 30  # 0.5 секунды между блоками
        self.last_deflect_time = 0
        
        # Эффекты блокировки
        self.block_effect_timer = 0
        self.deflected_bullets = []  # Отраженные пули

    def check_bullet_deflection(self, enemy_bullets):
        """Проверяет и отражает пули противника"""
        if self.deflect_cooldown > 0:
            return False
        
        baguette_rect = self.get_baguette_rect()
        deflected_any = False
        
        for bullet in enemy_bullets[:]:
            bullet_rect = pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6)
            
            if baguette_rect.colliderect(bullet_rect):
                # Отражаем пулю
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
        # Меняем направление пули
        bullet['vx'] = -bullet['vx'] * 1.2  # Отражаем быстрее
        bullet['vy'] = -bullet['vy'] * 1.2
        bullet['lifetime'] = 120  # Новое время жизни
        
        # Добавляем в список отраженных пуль
        self.deflected_bullets.append(bullet)

    def get_baguette_rect(self):
        """Возвращает прямоугольник багета для блокировки"""
        center_x, center_y = self.rect.center
        
        # Направление багета (всегда в сторону движения или к противнику)
        angle = math.atan2(self.vy, self.vx) if abs(self.vx) > 1 or abs(self.vy) > 1 else 0
        
        start_x = center_x + self.radius * math.cos(angle)
        start_y = center_y + self.radius * math.sin(angle)
        end_x = center_x + (self.radius + self.baguette_length) * math.cos(angle)
        end_y = center_y + (self.radius + self.baguette_length) * math.sin(angle)
        
        min_x = min(start_x, end_x) - self.baguette_width // 2
        max_x = max(start_x, end_x) + self.baguette_width // 2
        min_y = min(start_y, end_y) - self.baguette_width // 2
        max_y = max(start_y, end_y) + self.baguette_width // 2
        
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def update(self, other_ball=None):
        # Обновляем кулдауны
        if self.deflect_cooldown > 0:
            self.deflect_cooldown -= 1
        
        if self.block_effect_timer > 0:
            self.block_effect_timer -= 1
        
        # Проверяем блокировку пуль противника
        if other_ball and hasattr(other_ball, 'flying_bullets'):
            self.check_bullet_deflection(other_ball.flying_bullets)
        
        # Обновляем отраженные пули
        for bullet in self.deflected_bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['lifetime'] -= 1
            
            # Проверяем попадание в противника
            if other_ball:
                bullet_rect = pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6)
                if bullet_rect.colliderect(other_ball.rect):
                    other_ball.take_damage(self.stats['damage'])
                    self.deflected_bullets.remove(bullet)
                    continue
            
            # Удаляем пулю если время вышло
            if bullet['lifetime'] <= 0:
                self.deflected_bullets.remove(bullet)
        
        # Базовое обновление
        super().update(other_ball)

    def attack(self, target):
        """Переопределяем атаку для сильного отброса"""
        if not self.can_attack():
            return False

        target.last_attacker_pos = self.rect.center
        success = target.take_damage(self.stats['damage'])
        if success:
            self.attack_cooldown = self.attack_cooldown_duration
            
            # СИЛЬНЫЙ отброс багетом
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                knockback_force = 12  # Очень сильный отброс
                target.vx += (dx / distance) * knockback_force
                target.vy += (dy / distance) * knockback_force - 3
            
            self.on_successful_attack(target)
        return success

    def draw_baguette(self, screen):
        """Рисует багет"""
        center_x, center_y = self.rect.center
        
        # Направление багета
        angle = math.atan2(self.vy, self.vx) if abs(self.vx) > 1 or abs(self.vy) > 1 else 0
        
        start_x = center_x + self.radius * math.cos(angle)
        start_y = center_y + self.radius * math.sin(angle)
        end_x = center_x + (self.radius + self.baguette_length) * math.cos(angle)
        end_y = center_y + (self.radius + self.baguette_length) * math.sin(angle)
        
        # Основной багет (золотисто-коричневый)
        pygame.draw.line(screen, (210, 180, 140), (start_x, start_y), (end_x, end_y), self.baguette_width)
        pygame.draw.line(screen, (160, 130, 90), (start_x, start_y), (end_x, end_y), 2)  # Контур
        
        # Насечки на багете
        for i in range(3):
            progress = 0.2 + i * 0.3
            notch_x = start_x + (end_x - start_x) * progress
            notch_y = start_y + (end_y - start_y) * progress
            
            # Перпендикулярная линия для насечки
            perp_angle = angle + math.pi / 2
            notch_length = self.baguette_width // 3
            
            notch_start_x = notch_x + notch_length * math.cos(perp_angle)
            notch_start_y = notch_y + notch_length * math.sin(perp_angle)
            notch_end_x = notch_x - notch_length * math.cos(perp_angle)
            notch_end_y = notch_y - notch_length * math.sin(perp_angle)
            
            pygame.draw.line(screen, (140, 100, 60), (notch_start_x, notch_start_y), 
                           (notch_end_x, notch_end_y), 2)
        
        # Эффект блокировки
        if self.block_effect_timer > 0:
            # Искры от блокировки
            for i in range(5):
                spark_x = start_x + random.uniform(0, end_x - start_x)
                spark_y = start_y + random.uniform(0, end_y - start_y)
                
                spark_color = random.choice([(255, 255, 100), (255, 200, 0), (255, 255, 255)])
                pygame.draw.circle(screen, spark_color, (int(spark_x), int(spark_y)), 
                                 random.randint(2, 4))

    def draw_deflected_bullets(self, screen):
        """Рисует отраженные пули"""
        for bullet in self.deflected_bullets:
            # Отраженная пуля с синим оттенком
            pygame.draw.circle(screen, (100, 150, 255), (int(bullet['x']), int(bullet['y'])), 3)
            pygame.draw.circle(screen, (50, 100, 200), (int(bullet['x']), int(bullet['y'])), 2)

    def draw(self, screen):
        # Рисуем французский флаг как тело шарика
        center_x, center_y = self.rect.center
        
        # Разделяем на три вертикальные полосы
        third_width = self.radius * 2 // 3
        
        # Синяя полоса (левая)
        blue_rect = pygame.Rect(center_x - self.radius, center_y - self.radius, 
                               third_width, self.radius * 2)
        pygame.draw.rect(screen, (0, 85, 164), blue_rect)
        
        # Белая полоса (средняя)
        white_rect = pygame.Rect(center_x - self.radius + third_width, center_y - self.radius, 
                                third_width, self.radius * 2)
        pygame.draw.rect(screen, (255, 255, 255), white_rect)
        
        # Красная полоса (правая)
        red_rect = pygame.Rect(center_x - self.radius + 2 * third_width, center_y - self.radius, 
                              self.radius * 2 - 2 * third_width, self.radius * 2)
        pygame.draw.rect(screen, (239, 65, 53), red_rect)
        
        # Обрезаем по кругу
        mask_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (self.radius, self.radius), self.radius)
        
        # Применяем круглую маску
        flag_surface = screen.subsurface(pygame.Rect(center_x - self.radius, center_y - self.radius, 
                                                    self.radius * 2, self.radius * 2)).copy()
        flag_surface.set_clip(pygame.Rect(0, 0, self.radius * 2, self.radius * 2))
        
        # Перерисовываем с круглой обрезкой
        pygame.draw.circle(screen, (0, 85, 164), (center_x - self.radius//3, center_y), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.radius)
        pygame.draw.circle(screen, (239, 65, 53), (center_x + self.radius//3, center_y), self.radius)
        
        # Финальная круглая обрезка
        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), self.radius, 3)
        
        # Рисуем багет
        self.draw_baguette(screen)
        
        # Рисуем отраженные пули
        self.draw_deflected_bullets(screen)
        
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
        # Увеличиваем силу багета
        self.stats['damage'] += 2.0
        self.baguette_length += 5  # Багет растет
        self.baguette_width = min(15, self.baguette_width + 1)