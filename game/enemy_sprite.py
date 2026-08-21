"""game/enemy_sprite.py — Враги."""

import pygame
import random
import math
from typing import Optional, List

from .config import (
    WIDTH, HEIGHT, COLORS, ENEMY_SIMPLE_SIZE, ENEMY_FAST_SIZE, ENEMY_BOSS_SIZE,
    ENEMY_SIMPLE_SPEED, ENEMY_FAST_SPEED, ENEMY_BOSS_SPEED
)


class Enemy(pygame.sprite.Sprite):
    """Враг — круглый корабль, падающий сверху."""

    TYPES = ["simple", "fast", "boss"]

    def __init__(self, enemy_type: str = "simple") -> None:
        super().__init__()
        self.enemy_type = enemy_type
        self.max_hp = 1 if enemy_type != "boss" else 10
        self.hp = self.max_hp
        self.score_value = {
            "simple": 10,
            "fast": 20,
            "boss": 100,
        }[enemy_type]

        # Размеры и скорости по типу
        if enemy_type == "simple":
            size, color, speed = ENEMY_SIMPLE_SIZE, COLORS["RED"], ENEMY_SIMPLE_SPEED
        elif enemy_type == "fast":
            size, color, speed = ENEMY_FAST_SIZE, COLORS["BLUE"], ENEMY_FAST_SPEED
        else:  # boss
            size, color, speed = ENEMY_BOSS_SIZE, (239, 84, 80), ENEMY_BOSS_SPEED

        self.radius = size // 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Тело врага — круг с обводкой
        pygame.draw.circle(self.image, color + (180,), (self.radius, self.radius), self.radius - 3)
        # Обводка для стиля
        pygame.draw.circle(
            self.image, tuple(c for c in color[:3]) + (255,),
            (self.radius, self.radius), self.radius - 3, width=2
        )

        # Глаза — только у простых и быстрых врагов
        if enemy_type != "boss":
            pygame.draw.circle(self.image, (255, 255, 255), (14, 12), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (14, 12), 2)
            pygame.draw.circle(self.image, (255, 255, 255), (size - 14, 12), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (size - 14, 12), 2)

        # Глаз босса — один большой в центре
        if enemy_type == "boss":
            eye_radius = max(5, size // 6)
            pygame.draw.circle(
                self.image, (255, 255, 200),
                (size // 2 - eye_radius + 3, self.radius - 8), eye_radius
            )
            pygame.draw.circle(
                self.image, (0, 0, 0),
                (size // 2 - eye_radius + 3, self.radius - 8), max(1, eye_radius // 3)
            )

        self.rect = self.image.get_rect()
        self.velocity = pygame.math.Vector2(0.0, speed)

    def update(self) -> None:
        """Обновить позицию врага."""
        self.rect.y += self.velocity.y

        # Волновое движение для быстрых врагов
        if self.enemy_type == "fast":
            wave_offset = math.sin(pygame.time.get_ticks() / 300.0) * 1.5
            self.rect.x += wave_offset

        # Удаление при полном выходе за экран (низ/бока); вход сверху разрешён
        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.top > HEIGHT):
            self.kill()


def spawn_enemy(x: float = None, y: float = None, enemy_type: str = "simple") -> Enemy:
    """Создать и разместить врага."""
    if x is None:
        x = random.randint(20, WIDTH - 20)
    if y is None:
        y = random.randint(-40, -50)

    enemy = Enemy(enemy_type=enemy_type)
    enemy.rect.centerx = x
    enemy.rect.top = y
    return enemy


def spawn_boss() -> Enemy:
    """Создать босса и разместить в центре сверху."""
    boss = Enemy(enemy_type="boss")
    boss_x = WIDTH // 2 - ENEMY_BOSS_SIZE // 2
    boss_y = random.randint(-100, -60)

    boss.rect.centerx = boss_x + ENEMY_BOSS_SIZE // 2
    boss.rect.top = boss_y

    return boss
