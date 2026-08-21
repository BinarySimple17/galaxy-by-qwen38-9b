# Сессия 3: Враги и коллизии пуль 🎮

## 📅 Дата начала: [вставить дату]

---

## 🎯 Цель сессии
Добавить врагов в игру. Они спавнятся сверху, падают вниз. Пули игрока уничтожают их — начисляются очки.

---

## ✅ Результат после сессии
Игра запускается: корабль управляется WASD, стрельба пробелом. Сверху появляются красные круги-враги, которые падают вниз. При попадании пули враг исчезает и добавляется +10 к очкам.

---

## 🛠 Задачи

### 1. Создать файл `game/enemy_sprite.py` (~8 мин)

```python
"""game/enemy_sprite.py — Враги."""
import pygame
import random
import math
from typing import Optional


class Enemy(pygame.sprite.Sprite):
    """Враг — круг, падающий сверху."""

    TYPES = ["simple", "fast", "boss"]

    def __init__(self, enemy_type: str = "simple") -> None:
        super().__init__()
        self.enemy_type = enemy_type
        self.max_hp = 1 if enemy_type != "boss" else 10
        self.hp = self.max_hp
        self.score_value = 10 if enemy_type == "simple" else (20 if enemy_type == "fast" else 100)

        # Параметры в зависимости от типа врага
        if enemy_type == "simple":
            size, color, speed = 30, (239, 84, 80), 2.5
        elif enemy_type == "fast":
            size, color, speed = 20, (78, 191, 255), 4.5
        else:  # boss
            size, color, speed = 70, (239, 84, 80), 1.5

        self.radius = size // 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Рисуем тело врага
        pygame.draw.circle(self.image, color + (180,), (self.radius, self.radius), self.radius - 3)

        # "Глаза" — только у простых и быстрых врагов
        if enemy_type != "boss":
            pygame.draw.circle(self.image, (255, 255, 255), (14, 12), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (14, 12), 2)
            pygame.draw.circle(self.image, (255, 255, 255), (self.radius - 14, 12), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (self.radius - 14, 12), 2)

        self.rect = self.image.get_rect()

        # Скорость падения вниз по оси Y
        self.velocity = pygame.math.Vector2(0.0, speed)

    def update(self) -> None:
        """Обновление позиции врага."""
        self.rect.y += self.velocity.y

        # Волновое движение для быстрых врагов (синих)
        if self.enemy_type == "fast":
            wave_offset = math.sin(pygame.time.get_ticks() / 300.0) * 1.5
            self.rect.x += wave_offset

        # Проверка: улетел за экран → удалить
        if (self.rect.right < 0 or self.rect.left > 800 or
                self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()


def get_enemy_image(enemy_type: str = "simple") -> pygame.Surface:
    """Получить изображение врага по типу."""
    if enemy_type == "simple":
        size, color = 30, (239, 84, 80)
    elif enemy_type == "fast":
        size, color = 20, (78, 191, 255)
    else:
        size, color = 70, (239, 84, 80)

    surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.circle(surface, color + (180,), (size, size), size - 3)
    if enemy_type != "boss":
        pygame.draw.circle(surface, (255, 255, 255), (14, 12), 4)
        pygame.draw.circle(surface, (0, 0, 0), (14, 12), 2)
        pygame.draw.circle(surface, (255, 255, 255), (size - 14, 12), 4)
        pygame.draw.circle(surface, (0, 0, 0), (size - 14, 12), 2)

    return surface
```

### 2. Обновить `main.py` с врагами (~7 мин)

Добавляем:
- Класс `Enemy` в импорты
- Метод `spawn_enemy()` у класса `Game` — создание и спавн нового врага
- В цикле `update()` вызываем `enemies.update()`
- Увеличиваем список всех спрайтов на врагов

```python
# В main.py — импорт:
from game.enemy_sprite import Enemy


# В классе Game:

class Game:
    """Основной игровой цикл."""

    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.all_sprites: List[pygame.sprite.Sprite] = []
        self.bullets: List[Bullet] = []
        # ← добавляем группу врагов
        self.enemies: List[Enemy] = []

        self.player = Player()
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.victory = False

        # Таймер спавна врагов
        self.enemy_spawn_timer: int = 0
        self.enemy_spawn_interval: int = 80  # кадров между спавном врага

    def spawn_enemy(self) -> None:
        """Спавн нового врага сверху."""
        # Определяем, какие типы врагов доступны на текущем уровне
        types = ["simple"] * (self.level // 2) + ["fast"] if self.level >= 3 else ["simple"]
        enemy_type = random.choice(types[:min(self.level % 3 + 1, len(types))])

        x = random.randint(20, WIDTH - 20)
        y = random.randint(-40, -50)

        enemy = Enemy(enemy_type=enemy_type)
        enemy.rect.centerx = x
        enemy.rect.top = y

        self.enemies.append(enemy)
        self.all_sprites.append(enemy)

    def update(self) -> None:
        """Обновление состояния игры."""
        if not (self.game_over or self.victory):
            self.player.update()
            self.shoot()

            # Удаляем пули, улетевшие за экран
            for bullet in list(self.bullets):
                if bullet.is_offscreen():
                    bullet.kill()

            # Обновление всех живых сущностей (игрок + пули + враги)
            for entity in list(self.all_sprites):
                entity.update()

            # Спавн врагов по таймеру
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= max(40, 80 - self.level * 5):
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
```

### 3. Обновить метод `draw()` класса `Game` (~2 мин)

Добавить отрисовку врагов:

```python
def draw(self) -> None:
    """Отрисовка кадра."""
    SCREEN.fill(COLORS["BLACK"])

    # Игрок
    self.player.image.set_alpha(200 if pygame.time.get_ticks() % 300 < 150 else 255)
    SCREEN.blit(self.player.image, self.player.rect)

    # Пули
    for bullet in self.bullets:
        SCREEN.blit(bullet.image, bullet.rect)

    # Враги
    for enemy in self.enemies:
        if enemy.hp <= 0:
            continue  # не рисуем уничтоженных
        SCREEN.blit(enemy.image, enemy.rect)

    # UI
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
```

### 4. Добавить обработку коллизий пуль с врагами (~5 мин)

В методе `update()` класса `Game` добавляем проверку: если пуля попала во врага — уменьшаем его здоровье и удаляем пулю.

```python
def handle_bullet_enemy_collisions(self) -> None:
    """Проверка попаданий пуль во врагов."""
    for bullet in list(self.bullets):  # перебираем копию списка
        enemy = pygame.sprite.spritecollide(bullet, self.enemies, False)[0] if \
               pygame.sprite.spritecollideany(bullet, self.enemies) else None

        if enemy is not None and enemy.hp > 0:
            enemy.hp -= 1
            bullet.kill()  # пуля исчезает после попадания

            # Если враг уничтожен — удаляем его и начисляем очки
            if enemy.hp <= 0:
                enemy.kill()
                self.score += enemy.score_value


# В методе update():
def update(self) -> None:
    """Обновление состояния игры."""
    if not (self.game_over or self.victory):
        self.player.update()
        self.shoot()

        # Удаляем пули, улетевшие за экран
        for bullet in list(self.bullets):
            if bullet.is_offscreen():
                bullet.kill()

        # Проверка попаданий пуль во врагов
        self.handle_bullet_enemy_collisions()

        # Обновление всех живых сущностей
        for entity in list(self.all_sprites):
            entity.update()

        # Спавн врагов по таймеру
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= max(40, 80 - self.level * 5):
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
```

---

## 🧪 Как протестировать

Запустить игру:

```bash
python main.py
```

**Наблюдается:**
- Сверху появляются красные круги (простые враги) — каждые ~80 кадров (~1.3 сек при 60 FPS, уменьшается с уровнем)
- Они падают вниз со скоростью ~2.5 пикселей за кадр
- При нажатии пробела пуля попадает во врага → он исчезает, очки увеличиваются на +10

---

## 🐛 Возможные проблемы

| Проблема | Решение |
|----------|---------|
| Враги не появляются | Проверить таймер спавна — `enemy_spawn_interval` может быть слишком большим |
| Пули проходят сквозь врагов | Убедиться, что `handle_bullet_enemy_collisions()` вызывается в `update()` и пули удаляются после попадания (`bullet.kill()`) |
| Враги не падают вниз | Проверить `velocity.y` — должно быть положительным (вниз) |

---

## ✅ Чеклист завершения сессии

- [ ] Игра запускается без ошибок
- [ ] Сверху появляются красные круги-враги
- [ ] Враги падают вниз, исчезают при улете за экран
- [ ] Пули попадают во врагов → враг уничтожается, очки начисляются (+10)
- [ ] Таймер спавна уменьшает интервал с каждым уровнем (минимум 40 кадров)

---

## 🚀 Переходим к следующей сессии → Сессия 4: Жизни игрока + частицы взрыва
