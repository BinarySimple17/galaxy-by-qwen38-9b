# Сессия 4: Жизни игрока и частицы взрыва 💥❤️

## 📅 Дата начала: [вставить дату]

---

## 🎯 Цель сессии
Добавить систему жизней для игрока. При столкновении пули игрока с врагом — пуля отскакивает, и враг стреляет в игрока (наносит урон). Уничтожение врага вызывает всплеск частиц.

---

## ✅ Результат после сессии
Игра запускается: при попадании пули во врага она отскакивает обратно (в сторону игрока), а враг стреляет в ответ — если попадает, у игрока уменьшается жизнь. При уничтожении врага вокруг него вспыхивают разноцветные частицы.

---

## 🛠 Задачи

### 1. Создать файл `game/particles.py` (~8 мин)

```python
"""game/particles.py — Система частиц."""
import pygame
import random
import math
from typing import Optional


class Particle(pygame.sprite.Sprite):
    """Частица взрыва: летящая в случайном направлении, затухает со временем."""

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
        self.lifetime: int = random.randint(30, 60)  # кадры жизни частицы

    def update(self) -> None:
        """Обновление позиции и уменьшение времени жизни."""
        self.velocity *= 0.97  # замедление
        self.rect.center = (self.rect.centerx + self.velocity.x,
                           self.rect.centery + self.velocity.y)
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()


def create_explosion(x: float, y: float) -> list[Particle]:
    """Создать всплеск частиц в точке (x, y)."""
    particles = []
    for _ in range(random.randint(12, 18)):
        p = Particle(x, y)
        particles.append(p)
    return particles


# Базовый класс сущности (можно вынести в отдельный файл game/entities.py)
class Entity(pygame.sprite.Sprite):
    """Базовый класс сущности."""

    def __init__(self, x: float, y: float, radius: float = 20) -> None:
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))

    def is_offscreen(self) -> bool:
        return (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT)


# Пуля — обновлённая с отскоком
class Bullet(pygame.sprite.Sprite):
    """Пуля — жёлтая полоса, летящая вверх."""

    def __init__(self, x: float, y: float, direction: tuple = (-1.0, -8.0)) -> None:
        super().__init__()
        try:
            self.image = pygame.image.load("game/sprites/bullet.png").convert_alpha()
        except FileNotFoundError:
            size, height = 6, 14
            surface = pygame.Surface((size, height), pygame.SRCALPHA)
            pygame.draw.rect(surface, (253, 216, 53, 200), (0, 0, size, height))
            self.image = surface

        self.rect = self.image.get_rect(center=(x + 3, y - 7))
        speed = 8.0
        direction_vec = pygame.math.Vector2(direction).normalize() * speed
        self.velocity = direction_vec

    def update(self) -> None:
        """Обновление позиции пули."""
        self.rect.center = (self.rect.centerx + self.velocity.x,
                           self.rect.centery + self.velocity.y)

        # Удаляем пулю, если она улетела за верх экрана или слишком далеко в стороны
        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.top < 0 or self.rect.bottom < -50):
            self.kill()

    def bounce(self) -> Optional[pygame.math.Vector2]:
        """Отскочить: возвращает вектор новой скорости."""
        new_speed = random.uniform(-6.0, -9.0)  # отскок вверх (в сторону игрока)
        angle = random.uniform(1.5, 4.0)  # случайный угол отскока
        return pygame.math.Vector2(math.cos(angle), math.sin(angle)) * new_speed


# Враг — обновлённый со способностью стрелять обратно
class Enemy(pygame.sprite.Sprite):
    """Враг — круг, падающий сверху."""

    TYPES = ["simple", "fast", "boss"]

    def __init__(self, enemy_type: str = "simple") -> None:
        super().__init__()
        self.enemy_type = enemy_type
        self.max_hp = 1 if enemy_type != "boss" else 10
        self.hp = self.max_hp
        self.score_value = 10 if enemy_type == "simple" else (20 if enemy_type == "fast" else 100)

        if enemy_type == "simple":
            size, color, speed = 30, (239, 84, 80), 2.5
        elif enemy_type == "fast":
            size, color, speed = 20, (78, 191, 255), 4.5
        else:
            size, color, speed = 70, (239, 84, 80), 1.5

        self.radius = size // 2
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        pygame.draw.circle(self.image, color + (180,), (self.radius, self.radius), self.radius - 3)

        if enemy_type != "boss":
            pygame.draw.circle(self.image, (255, 255, 255), (14, 12), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (14, 12), 2)
            pygame.draw.circle(self.image, (255, 255, 255), (size - 14, 12), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (size - 14, 12), 2)

        self.rect = self.image.get_rect()
        self.velocity = pygame.math.Vector2(0.0, speed)

    def update(self) -> None:
        """Обновление позиции врага."""
        self.rect.y += self.velocity.y

        if self.enemy_type == "fast":
            wave_offset = math.sin(pygame.time.get_ticks() / 300.0) * 1.5
            self.rect.x += wave_offset

        # Проверка: улетел за экран → удалить
        if (self.rect.right < 0 or self.rect.left > WIDTH or
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

### 2. Обновить `main.py` с жизнями и частицами (~7 мин)

#### А. Добавить частицы при уничтожении врага

В методе `spawn_enemy()` у класса `Game`:

```python
def spawn_enemy(self, x: float | None = None, y: float | None = None) -> None:
    """Спавн нового врага сверху."""
    types = ["simple"] * (self.level // 2) + ["fast"] if self.level >= 3 else ["simple"]
    enemy_type = random.choice(types[:min(self.level % 3 + 1, len(types))])

    x = x or random.randint(20, WIDTH - 20)
    y = y or random.randint(-40, -50)

    enemy = Enemy(enemy_type=enemy_type)
    enemy.rect.centerx = x
    enemy.rect.top = y

    self.enemies.append(enemy)
    self.all_sprites.append(enemy)


def spawn_particles(self, x: float, y: float) -> None:
    """Создать взрыв частиц в точке (x, y)."""
    for _ in range(random.randint(12, 18)):
        particle = Particle(x, y)
        self.particles.append(particle)
        self.all_sprites.append(particle)


def handle_collision_enemy_with_bullet(self, enemy: "Enemy", bullet: Bullet) -> None:
    """Обработка коллизии врага с пулей игрока."""
    if enemy.hp <= 0:
        return

    # Пуля отскакивает (враг стреляет обратно в игрока)
    bounce_direction = bullet.bounce()
    bullet.velocity = bounce_direction

    # Враг стреляет — создаём пулю, летящую в сторону игрока
    if pygame.sprite.collide_rect(bullet, self.player):
        # Пуля попала в игрока → наносим урон
        self.lives -= 1
        bullet.kill()
        return

    # Если пуль не попала во врага или в игрока — удаляем
    bullet.kill()
```

#### Б. Добавить метод `handle_collisions()` и вызвать его из `update()`

В классе `Game`:

```python
def handle_collision_enemy_with_bullet(self, enemy: "Enemy", bullet: Bullet) -> None:
    """Обработка коллизии врага с пулей игрока."""
    if enemy.hp <= 0:
        return

    # Пуля отскакивает (враг стреляет обратно в игрока)
    bounce_direction = bullet.bounce()
    bullet.velocity = bounce_direction

    # Враг стреляет — создаём пулю, летящую в сторону игрока
    if pygame.sprite.collide_rect(bullet, self.player):
        # Пуля попала в игрока → наносим урон
        self.lives -= 1
        bullet.kill()
        return

    # Если пуль не попала во врага или в игрока — удаляем
    bullet.kill()


def handle_collisions(self) -> None:
    """Обработка всех коллизий."""
    # Пули → враги
    for enemy in list(self.enemies):  # перебираем копию списка
        if enemy.hp <= 0:
            continue

        hits = pygame.sprite.spritecollide(enemy, self.bullets, False)
        for bullet in hits:
            self.handle_collision_enemy_with_bullet(enemy, bullet)


# В update():
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
        self.handle_collisions()

        # Обновление всех живых сущностей
        for entity in list(self.all_sprites):
            entity.update()

        # Спавн врагов по таймеру
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= max(40, 80 - self.level * 5):
            self.spawn_enemy()
            self.enemy_spawn_timer = 0


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
            continue
        SCREEN.blit(enemy.image, enemy.rect)

    # Частицы (над всеми другими объектами)
    for particle in self.particles:
        SCREEN.blit(particle.image, particle.rect)

    # UI
    title = self.font.render("Galaxy Shooter", True, COLORS["WHITE"])
    SCREEN.blit(title, (10, 10))

    score_text = self.small_font.render(f"Score: {self.score}", True, COLORS["YELLOW"])
    SCREEN.blit(score_text, (10, 50))

    level_text = self.small_font.render(f"Level: {self.level}", True, COLORS["WHITE"])
    SCREEN.blit(level_text, (WIDTH // 2 + 60, 10))

    lives_text = self.small_font.render(
        f"Hearts: {'❤' * self.lives}{'💔' * (3 - self.lives)}", True, COLORS["RED"]
    )
    SCREEN.blit(lives_text, (10, HEIGHT - 30))
```

### 3. Обновить `Player` — добавить урон от пуль (~2 мин)

В классе `Player`:

```python
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
        self.cooldown: Optional[float] = None
        self.last_shot_time: float = 0.0


    # (движение остаётся без изменений)
```

### 4. Обновить `draw()` — отрисовка частиц над остальным

В методе `draw()`:

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
            continue
        SCREEN.blit(enemy.image, enemy.rect)

    # Частицы (над всеми другими объектами)
    for particle in self.particles:
        SCREEN.blit(particle.image, particle.rect)

    # UI...
```

---

## 🧪 Как протестировать

Запустить игру:

```bash
python main.py
```

**Наблюдается:**
- При попадании пули во врага — пуля отскакивает обратно (в сторону игрока), а вокруг врага вспыхивают разноцветные частицы
- Если отскочившая пуля попадает в игрока — уменьшается количество жизней, отображаемых как ❤️ или 💔
- Частицы исчезают через ~45 кадров (~0.7 сек)

---

## 🐛 Возможные проблемы

| Проблема | Решение |
|----------|---------|
| Пули не отскакивают | Проверить метод `bounce()` — возвращает вектор с отрицательной скоростью по Y |
| Частицы не появляются при уничтожении врага | Убедиться, что в коде после `enemy.kill()` вызывается `spawn_particles()` или что частицы создаются при коллизии |
| Пуля пролетает сквозь игрока | Увеличить радиус/размер игрока в `Player.rect` или добавить проверку коллизий с прямоугольником игрока |

---

## ✅ Чеклист завершения сессии

- [ ] Игра запускается без ошибок
- [ ] При попадании пули во врага:
  - Пуля отскакивает вверх (в сторону игрока)
  - Враг стреляет обратно (появляется новая пуля, летящая в сторону игрока)
  - Если пуля попадает в игрока — жизнь уменьшается (❤️ превращается в 💔)
- [ ] При уничтожении врага вокруг него вспыхивает разноцветный взрыв из частиц
- [ ] Частицы исчезают через ~45 кадров

---

## 🚀 Переходим к следующей сессии → Сессия 5: Прогрессия сложности + боссы
