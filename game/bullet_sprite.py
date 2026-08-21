"""game/bullet_sprite.py — Пуля."""

import pygame
import random
import math
from typing import Optional

from .config import WIDTH, COLORS


class Bullet(pygame.sprite.Sprite):
    """Пуля — жёлтая полоса, летящая вверх с отскоком."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        self._load_image()
        # Центрируем пулю относительно точки выстрела
        self.rect = self.image.get_rect(center=(x + 3, y - 7))

        # Скорость пули (вверх с небольшим уклоном влево)
        speed = 8.0
        direction = (-1.0, -speed)
        self.velocity = pygame.math.Vector2(direction).normalize() * speed

    def _load_image(self) -> None:
        """Загрузить спрайт пули или создать fallback."""
        try:
            self.image = pygame.image.load("game/sprites/bullet.png").convert_alpha()
        except FileNotFoundError:
            size, height = 6, 14
            surface = pygame.Surface((size, height), pygame.SRCALPHA)
            pygame.draw.rect(surface, (253, 216, 53, 200), (0, 0, size, height))
            # "Головка" пули
            pygame.draw.circle(surface, (253, 216, 53), (size // 2, 2), 3)
            self.image = surface

    @property
    def is_offscreen(self) -> bool:
        """Проверка, улетела ли пуля за экран."""
        return (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.top < 0 or self.rect.bottom < -50)

    def update(self) -> None:
        """Обновить позицию пули."""
        self.rect.center = (self.rect.centerx + self.velocity.x,
                           self.rect.centery + self.velocity.y)

        # Удаляем пулю, если она улетела за экран
        if self.is_offscreen:
            self.kill()

    def bounce(self) -> Optional[pygame.math.Vector2]:
        """Отскок: возвращает новый вектор скорости."""
        new_speed = random.uniform(-6.0, -9.0)
        angle = random.uniform(1.5, 4.0)
        return pygame.math.Vector2(math.cos(angle), math.sin(angle)) * new_speed
