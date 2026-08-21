# Сессия 2: Стрельба и пули 🎯

## 📅 Дата начала: [вставить дату]

---

## 🎯 Цель сессии
Реализовать стрельбу игрока. Игрок может стрелять пробелом, пули летят вверх и исчезают за пределами экрана.

---

## ✅ Результат после сессии
Игра запускается: корабль управляется WASD/стрелками, по нажатию `Пробела` из него вылетает жёлтая пуля, которая летит вверх и исчезает, улетев за верхнюю границу экрана.

---

## 🛠 Задачи

### 1. Обновить файл `main.py` (~10 мин)

Добавляем:
- Класс `Bullet` — пуля со спрайтом
- Свойство `cooldown` в игроке для ограничения скорострельности
- Метод `shoot()` у класса `Game`
- Обработку коллизий между пулями и экраном (удаление улетевших пуль)

### 2. Создать файл `game/bullet_sprite.py` (~5 мин)

```python
"""game/bullet_sprite.py — Пуля."""
import pygame
import math
from typing import Optional


class Bullet(pygame.sprite.Sprite):
    """Пуля — жёлтая полоса, летящая вверх."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        # Загружаем спрайт пули или рисуем fallback
        try:
            self.image = pygame.image.load("game/sprites/bullet.png").convert_alpha()
        except FileNotFoundError:
            size, height = 6, 14
            surface = pygame.Surface((size, height), pygame.SRCALPHA)
            pygame.draw.rect(surface, (253, 216, 53, 200), (0, 0, size, height))
            # "головка" пули
            pygame.draw.circle(surface, (253, 216, 53), (size // 2, 2), 3)
            self.image = surface

        # Центрируем относительно точки выстрела
        self.rect = self.image.get_rect(center=(x + 3, y - 7))

        # Скорость пули: вверх по оси Y
        speed = 8.0
        direction = (-1.0, -speed)  # небольшой уклон влево для эффекта
        self.velocity = pygame.math.Vector2(direction).normalize() * speed

    def update(self) -> None:
        """Обновление позиции пули."""
        self.rect.center = (self.rect.centerx + self.velocity.x,
                           self.rect.centery + self.velocity.y)

        # Удаляем пулю, если она улетела за верх экрана или слишком далеко влево/вправо
        if (self.rect.right < 0 or self.rect.left > 800 or
                self.rect.top < 0 or self.rect.bottom < -50):
            self.kill()


def get_bullet_image() -> pygame.Surface:
    """Получить изображение пули (загрузка или fallback)."""
    try:
        return pygame.image.load("game/sprites/bullet.png").convert_alpha()
    except FileNotFoundError:
        size, height = 6, 14
        surface = pygame.Surface((size, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (253, 216, 53, 200), (0, 0, size, height))
        pygame.draw.circle(surface, (253, 216, 53), (size // 2, 2), 3)
        return surface
```

### 3. Обновить `main.py` с добавленными возможностями (~8 мин)

Изменить класс `Player`: добавить `cooldown` и метод `shoot()`.

Изменить класс `Game`: добавить `bullets` как группу спрайтов, реализовать стрельбу и удаление улетевших пуль.

```python
# В main.py — изменения в классе Player:

class Player(pygame.sprite.Sprite):
    """Корабль игрока."""

    def __init__(self) -> None:
        super().__init__()
        self.image = load_sprite("game/sprites/spaceship.png")
        if self.image is None:
            size = 50
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [(25, 0), (50, size - 10), (0, size - 10)]
            pygame.draw.polygon(surface, COLORS["GREEN"], points, width=3)
            self.image = surface

        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        # Добавляем
        self.cooldown: Optional[float] = None      # таймер перезарядки
        self.last_shot_time: float = 0.0           # время последнего выстрела

    def shoot(self) -> bool:
        """Выстрелить, если прошло достаточно времени. Возвращает True при успешном выстреле."""
        now = pygame.time.get_ticks()
        if self.cooldown is None or now - self.last_shot_time >= 200:  # ~200ms между выстрелами
            self.cooldown = now + 200
            return True
        return False

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


# В main.py — изменения в классе Game:

class Game:
    """Основной игровой цикл."""

    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.all_sprites: List[pygame.sprite.Sprite] = []
        self.bullets: List[Bullet] = []            # ← добавляем группу пуль
        self.player = Player()
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.victory = False

    def shoot(self) -> None:
        """Выстрел игрока."""
        if pygame.key.get_pressed()[pygame.K_SPACE] and not self.player.cooldown:
            bullet = Bullet(
                self.player.rect.centerx + 20,
                self.player.rect.top - 15
            )
            # Добавляем пулю в список и группу всех спрайтов
            self.bullets.append(bullet)
            self.all_sprites.add(bullet)

    def update(self) -> None:
        """Обновление состояния игры."""
        if not (self.game_over or self.victory):
            self.player.update()
            self.shoot()  # ← вызываем стрельбу

            # Удаляем пули, улетевшие за экран
            for bullet in list(self.bullets):
                if bullet.is_offscreen():
                    bullet.kill()

            # Обновление всех живых сущностей
            for entity in list(self.all_sprites):
                entity.update()
```

### 4. Добавить удаление улетевших пуль (~2 мин)

В методе `update()` класса `Game`:

```python
def update(self) -> None:
    if not (self.game_over or self.victory):
        self.player.update()
        self.shoot()

        # Удаляем пули, улетевшие за экран
        for bullet in list(self.bullets):
            if bullet.is_offscreen():
                bullet.kill()

        # Обновление всех живых сущностей
        for entity in list(self.all_sprites):
            entity.update()
```

---

## 🧪 Как протестировать

Запустить игру:

```bash
python main.py
```

**Нажать `Пробел`** → должна вылететь жёлтая пуля из носа корабля, лететь вверх и исчезнуть.

**Увеличьте скорость:** нажимайте пробел быстро — пули должны появляться с задержкой ~200мс.

---

## 🐛 Возможные проблемы

| Проблема | Решение |
|----------|---------|
| Пули не удаляются | Добавить проверку `is_offscreen()` или просто проверять координаты |
| Слишком быстрая стрельба | Увеличить значение `cooldown` в классе `Player` (сейчас 200 мс) |
| Пуля застревает на экране | Проверить, что скорость пули достаточно большая — увеличить множитель скорости |

---

## ✅ Чеклист завершения сессии

- [ ] Игра запускается без ошибок
- [ ] При нажатии пробела из корабля вылетает жёлтая полоса (пуля)
- [ ] Пуля летит вверх и исчезает, улетев за верх экрана
- [ ] Между выстрелами есть задержка (~200 мс) — двойное нажатие не даёт две пули одновременно

---

## 🚀 Переходим к следующей сессии → Сессия 3: Враги + коллизии
