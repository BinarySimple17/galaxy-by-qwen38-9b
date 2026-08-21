# Сессия 1: Каркас игры + Игрок 🚀

## 📅 Дата начала: [вставить дату]

---

## 🎯 Цель сессии
Создать базовый игровой цикл и реализовать управление кораблём игрока (движение по экрану).

---

## ✅ Результат после сессии
Запускается игра — на экране виден треугольный корабль, управляемый клавишами WASD или стрелками. Корабль не выходит за границы экрана. В левом верхнем углу отображается название игры.

---

## 🛠 Задачи

### 1. Создать файл `main.py` (~5 мин)

```python
"""main.py — Точка входа в игру."""
import pygame
import sys
from typing import List, Optional

# Инициализация pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Shooter")
CLOCK = pygame.time.Clock()
FPS = 60

# Цвета
COLORS = {
    "BLACK": (10, 10, 25),
    "WHITE": (255, 255, 255),
    "RED": (239, 84, 80),
    "BLUE": (78, 191, 255),
    "YELLOW": (253, 216, 53),
    "GREEN": (61, 183, 134),
}

# Загрузка спрайта игрока
def load_sprite(path: str) -> pygame.Surface | None:
    try:
        return pygame.image.load(path).convert_alpha()
    except FileNotFoundError:
        print(f"⚠️ Спрайт не найден: {path}")
        print("   Создайте спрайт или используйте fallback.")
        # Fallback — рисуем треугольник программно
        size = 50
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        points = [(25, 0), (50, size - 10), (0, size - 10)]
        pygame.draw.polygon(surface, COLORS["GREEN"], points, width=3)
        return surface


# Класс игрока
class Player(pygame.sprite.Sprite):
    """Корабль игрока."""

    def __init__(self) -> None:
        super().__init__()
        # Загружаем спрайт или рисуем fallback
        self.image = load_sprite("game/sprites/spaceship.png")
        if self.image is None:
            size = 50
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [(25, 0), (50, size - 10), (0, size - 10)]
            pygame.draw.polygon(surface, COLORS["GREEN"], points, width=3)
            self.image = surface

        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))

    def update(self) -> None:
        """Обновление позиции игрока по клавиатуре."""
        speed = 5
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


# Основной класс игры
class Game:
    """Основной игровой цикл."""

    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.all_sprites: List[pygame.sprite.Sprite] = []
        self.player = Player()
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.victory = False

    def draw(self) -> None:
        """Отрисовка кадра."""
        SCREEN.fill(COLORS["BLACK"])
        # Отрисовка игрока
        self.player.image.set_alpha(200 if pygame.time.get_ticks() % 300 < 150 else 255)
        SCREEN.blit(self.player.image, self.player.rect)

        # UI: название, очки, уровень
        title = self.font.render("Galaxy Shooter", True, COLORS["WHITE"])
        SCREEN.blit(title, (10, 10))

        score_text = self.small_font.render(f"Score: {self.score}", True, COLORS["YELLOW"])
        SCREEN.blit(score_text, (10, 50))

        level_text = self.small_font.render(f"Level: {self.level}", True, COLORS["WHITE"])
        SCREEN.blit(level_text, (WIDTH // 2 + 60, 10))

        lives_text = self.small_font.render(
            f"Hearts: {'❤' * self.lives}", True, COLORS["RED"]
        )
        SCREEN.blit(lives_text, (10, HEIGHT - 30))

    def run(self) -> None:
        """Основной игровой цикл."""
        running = True
        while running:
            CLOCK.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif (
                    event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE
                ):
                    running = False
                # Рестарт после Game Over / Victory
                elif self.game_over or self.victory:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.reset()

            # Обновление игрока только если игра не окончена
            if not (self.game_over or self.victory):
                self.player.update()

            self.draw()
            pygame.display.flip()

        self.cleanup()

    def reset(self) -> None:
        """Сброс игры."""
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.victory = False
        self.player.rect.center = (WIDTH // 2, HEIGHT - 60)

    def cleanup(self) -> None:
        pygame.quit()
        sys.exit()


def main() -> None:
    """Точка входа."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
```

### 2. Создать папку `game/sprites/` и положить туда спрайт (~3 мин)
> Если у вас уже есть файл `spaceship.png` в папке `game/sprites/`, можно пропустить этот шаг.

---

## 🧪 Как протестировать

```bash
python main.py
```

**Ожидаемый результат:**
- Запускается окно 800×600 с чёрным фоном
- В левом верхнем углу надпись "Galaxy Shooter"
- По центру внизу — треугольный зелёный корабль
- При нажатии `W`/стрелка вверх — корабль летит вверх, и т.д.
- Корабль не выходит за границы экрана

---

## 🐛 Возможные проблемы

| Проблема | Решение |
|----------|---------|
| "pygame not installed" | `pip install pygame` |
| Спрайт не загружается (FileNotFoundError) | Создать спрайт вручную или использовать fallback-треугольник |
| Корабль застревает в углу | Проверьте границы экрана в методе `update()` |

---

## ✅ Чеклист завершения сессии

- [ ] Игра запускается командой `python main.py`
- [ ] Видно название игры в левом верхнем углу
- [ ] Корабль отрисовывается и двигается по всем 4 сторонам
- [ ] Корабль не выходит за границы экрана
- [ ] Живой пример работает без ошибок

---

## 🚀 Переходим к следующей сессии → Сессия 2: Стрельба + пули
