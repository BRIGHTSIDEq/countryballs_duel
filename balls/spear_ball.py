# balls/spear_ball.py  
from .base_fighter import FightingBall
import math
import random

class SpearBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=40, color=(50, 200, 200), 
                         name="Spear Hunter", weapon_type="spear")
        
        self.stats = {'damage': 6, 'range': 120, 'speed': 4, 'radius': self.radius}
        
        # Параметры копья - увеличенные в 2 раза
        self.weapon_length = 120
        self.weapon_width = 10
        
        # УЛУЧШЕННАЯ физика для копейщика - менее подвержен замедлению
        self.max_speed = 20
        self.weapon_rotation_speed = 7
        
        # ИСПРАВЛЕНИЕ: лучше сохраняет энергию движения
        self.friction = 0.999  # Меньше трения чем у других (было 0.998)
        self.bounce_energy = 1.2  # Больше энергии отскока (было 1.1)
        self.min_speed = 3  # Выше минимальная скорость (было 2)
        
        # Особенность копейщика: периодические рывки для поддержания активности
        self.dash_timer = 0
        self.dash_interval = 240  # Каждые 4 секунды небольшой рывок

    def maintain_activity(self):
        """Поддерживает активность копейщика"""
        self.dash_timer += 1
        
        # Периодический рывок для поддержания движения
        if self.dash_timer >= self.dash_interval:
            self.dash_timer = 0
            # Небольшой импульс в случайном направлении
            
            angle = random.uniform(0, 360)
            force = 4
            self.vx += force * math.cos(math.radians(angle))
            self.vy += force * math.sin(math.radians(angle))
        
        # Дополнительная проверка скорости - если слишком медленно, добавляем энергию
        total_speed = math.sqrt(self.vx**2 + self.vy**2)
        if total_speed < self.min_speed:
            # Усиливаем текущее направление движения или добавляем случайное
            if total_speed > 0.1:
                factor = self.min_speed / total_speed
                self.vx *= factor * 1.2
                self.vy *= factor * 1.2
            else:
                self.vx = random.uniform(-self.min_speed, self.min_speed)
                self.vy = random.uniform(-self.min_speed, self.min_speed)

    def update(self, other_ball=None):
        # Поддерживаем активность копейщика
        self.maintain_activity()
        
        # Базовое обновление
        super().update(other_ball)

    def on_successful_attack(self, target):
        # Копье растет быстрее по длине и урону
        self.stats['damage'] += 2.0
        self.stats['range'] += 10
        self.weapon_length += 15  # Копье растет еще быстрее
        self.weapon_width = min(40, self.weapon_width + 0.6)
        
        # Копейщик получает скорость после удара
        self.max_speed = min(30, self.max_speed + 0.5)
        
        # НОВОЕ: После удара копейщик получает дополнительный импульс
        # Импульс в сторону от цели
        dx = self.rect.centerx - target.rect.centerx
        dy = self.rect.centery - target.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            boost_force = 3
            self.vx += (dx / distance) * boost_force
            self.vy += (dy / distance) * boost_force