"""game/entities.py — Базовый класс сущности и утилиты."""

import pygame

from .config import WIDTH, HEIGHT


class Entity:
    """Базовая сущность для всех игровых объектов."""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = x
        self.y = y
        self.image: pygame.Surface | None = None
        self.rect: pygame.Rect | None = None

    @property
    def is_offscreen(self) -> bool:
        """Проверка, находится ли сущность за пределами экрана."""
        if getattr(self, "rect", None) is None:
            return False
        return (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT)

    def update(self) -> None:
        """Базовый метод обновления. Переопределять в подклассах."""
        pass


def create_rect_from_surface(surface: pygame.Surface | None,
                            center_x: float = 0.0,
                            center_y: float = 0.0) -> pygame.Rect:
    """Создать Rect из поверхности, центрируя её в точке (center_x, center_y)."""
    if surface is not None:
        return surface.get_rect(center=(center_x, center_y))
    raise ValueError("Surface must be set before creating rect.")
