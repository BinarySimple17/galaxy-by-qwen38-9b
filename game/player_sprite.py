"""game/player_sprite.py — Игрок (корабль игрока)."""

import pygame
from typing import Optional

from .config import WIDTH, HEIGHT, COLORS, PLAYER_SPEED, PLAYER_COOLDOWN_MS
from .entities import Entity


class Player(pygame.sprite.Sprite):
    """Корабль игрока. Управляется WASD / стрелками."""

    def __init__(self) -> None:
        super().__init__()
        self._load_image()
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))

        # Cooldown для стрельбы (время в миллисекундах)
        self.cooldown: Optional[float] = None
        self.last_shot_time: float = 0.0

    def _load_image(self) -> None:
        """Load sprite or create fallback triangle."""
        try:
            self.image = pygame.image.load("game/sprites/spaceship.png").convert_alpha()
        except FileNotFoundError:
            print("⚠️  Spaceship sprite not found. Using triangular fallback.")
            size = 50
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [(25, 0), (50, size - 10), (0, size - 10)]
            pygame.draw.polygon(surface, COLORS["GREEN"], points, width=3)
            self.image = surface

    def shoot(self) -> bool:
        """Попробовать выстрелить. Возвращает True если выстрел сработал."""
        now = pygame.time.get_ticks()
        if self.cooldown is None or now - self.last_shot_time >= PLAYER_COOLDOWN_MS:
            self.cooldown = now + PLAYER_COOLDOWN_MS
            return True
        return False

    def update(self) -> None:
        """Обновить позицию игрока."""
        speed = PLAYER_SPEED
        if pygame.key.get_pressed():
            keys = pygame.key.get_pressed()
            dx = dy = 0.0

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += speed
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += speed

            self.rect.x += dx
            self.rect.y += dy

        # Ограничение границами экрана
        self.rect.right = min(self.rect.right, WIDTH)
        self.rect.left = max(self.rect.left, 0)
        self.rect.bottom = min(self.rect.bottom, HEIGHT)
        self.rect.top = max(self.rect.top, 50)
