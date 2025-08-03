# balls/sword_ball.py
from .base_fighter import FightingBall

class SwordBall(FightingBall):
    def __init__(self, x, y):
        super().__init__(x=x, y=y, radius=40, color=(200, 50, 200), 
                         name="Sword Master", weapon_type="sword")
        
        self.stats = {'damage': 4, 'range': 100, 'speed': 4, 'radius': self.radius}
        
        # Параметры меча - увеличенные в 2 раза
        self.weapon_length = 80
        self.weapon_width = 15
        
        # Улучшенная физика для мечника
        self.bounce_energy = 1.15
        self.weapon_rotation_speed = 5

    def on_successful_attack(self, target):
        # Меч становится сильнее с каждым ударом
        self.stats['damage'] += 2.5
        self.weapon_length += 8  # Растет в длину быстрее
        self.weapon_width = min(50, self.weapon_width + 0.8)  # И в ширину
        
        # Дополнительный импульс после удара
        self.vx += 2 if self.rect.centerx > target.rect.centerx else -2
        self.vy -= 1