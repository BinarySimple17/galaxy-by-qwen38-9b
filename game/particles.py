"""game/particles.py — Система частиц (взрывы)."""

import pygame
import random
import math
from typing import List, Tuple

from .config import COLORS


class Particle(pygame.sprite.Sprite):
    """Частица взрыва: летит в случайном направлении, затухает со временем."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.5, 4.0)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * speed

        radius = random.randint(3, 8)
        color = random.choice((COLORS["RED"], COLORS["YELLOW"], COLORS["GREEN"]))

        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, color + (150,), (radius, radius), radius)

        self.image = surface
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime: int = random.randint(30, 60)  # кадров жизни частицы

    def update(self) -> None:
        """Обновить позицию и время жизни."""
        self.velocity *= 0.97  # замедление
        self.rect.center = (self.rect.centerx + self.velocity.x,
                           self.rect.centery + self.velocity.y)
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()


def create_explosion(x: float, y: float, count: int | None = None) -> List["Particle"]:
    """Создать всплеск частиц в точке (x, y)."""
    particles: List[Particle] = []
    if count is None:
        count = random.randint(12, 18)

    for _ in range(count):
        p = Particle(x, y)
        particles.append(p)

    return particles
