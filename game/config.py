"""game/config.py — Конфигурация и константы игры."""

# --- Размеры экрана ---
WIDTH = 800
HEIGHT = 600

# --- FPS ---
FPS = 60

# --- Цвета (RGB) ---
COLORS = {
    "BLACK": (10, 10, 25),
    "WHITE": (255, 255, 255),
    "RED": (239, 84, 80),
    "BLUE": (78, 191, 255),
    "YELLOW": (253, 216, 53),
    "GREEN": (61, 183, 134),
}

# --- Параметры игрока ---
PLAYER_SPEED = 5.0
PLAYER_COOLDOWN_MS = 200  # мс между выстрелами (~200 мс)

# --- Параметры врагов ---
ENEMY_SIMPLE = "simple"
ENEMY_FAST = "fast"
ENEMY_BOSS = "boss"
ENEMY_SIMPLE_SIZE = 30
ENEMY_FAST_SIZE = 20
ENEMY_BOSS_SIZE = 76
ENEMY_SIMPLE_SPEED = 2.5
ENEMY_FAST_SPEED = 4.5
ENEMY_BOSS_SPEED = 1.5

# --- Параметры уровня ---
STARTING_SPAWN_INTERVAL = 80  # кадров между спавнами
MIN_SPAWN_INTERVAL = 40  # минимальный интервал
LEVEL_3_THRESHOLD = 3  # уровень, когда появляются быстрые враги
LEVEL_BOSS_THRESHOLD = 6  # уровень, когда появляются боссы

# --- Параметры победы/поражения ---
LIVES_PER_LEVEL_BASE = 10  # базовый порог очков для победы на уровне
