"""game/game_state.py — Уровни и прогрессия сложности."""

from dataclasses import dataclass


@dataclass
class Level:
    """Уровень игры."""

    level_number: int = 1

    @property
    def spawn_interval(self) -> int:
        """Интервал спавна врагов в кадрах. Уменьшается на 5 каждый уровень, минимум 40."""
        return max(40, 80 - self.level_number * 5)

    @property
    def enemies_to_kill_for_next_level(self) -> int:
        """Количество врагов для повышения уровня (X × Y, где X=10, Y=current_level)."""
        return (self.level_number + 1) * 2

    @property
    def victory_score_threshold(self) -> int:
        """Порог очков для победы на уровне."""
        return self.level_number * 10


def increase_level(level: Level) -> None:
    """Увеличить номер уровня и обновить параметры."""
    level.level_number += 1
    # spawn_interval уже вычисляется через свойство, но пересчитаем явно для ясности
    level.spawn_interval = max(40, 80 - level.level_number * 5)
    level.enemies_to_kill_for_next_level = (level.level_number + 1) * 2
    level.victory_score_threshold = level.level_number * 10


def get_available_enemy_types(level: Level) -> list[str]:
    """Возвращает список доступных типов врагов для данного уровня."""
    if level.level_number == 1 or level.level_number == 2:
        return ["simple"]
    elif level.level_number < 3:
        return ["simple", "fast"]
    else:
        # Уровень 6+ — появляются боссы
        types = (["simple"] * (level.level_number // 2) +
                  ["fast"] * ((level.level_number + 1) // 3))
        if level.level_number >= 6:
            types.append("boss")
        return types[:min(level.level_number % 4 + 1, len(types))]


def get_boss_health() -> int:
    """Здоровье босса."""
    return 10
