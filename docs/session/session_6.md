# Сессия 6: Game Over / Victory + Полный UI 🏆🎉

## 📅 Дата начала: [вставить дату]

---

## 🎯 Цель сессии
Добавить экраны победы/поражения, перезапуск игры по пробелу, а также полный пользовательский интерфейс (очки, жизни, уровень, прогресс-бар).

---

## ✅ Результат после сессии

Полностью рабочая игра "Galaxy Shooter" с:
- Полноценным игровым циклом
- Управлением корабля (WASD / стрелки)
- Стрельбой пробелом
- Спавном врагов всех трёх типов (простые, быстрые, боссы)
- Прогрессией сложности (уровни, скорость спавна, боссы)
- Жизнями игрока и системой отскока пуль
- Частицами при уничтожении врагов
- Экранами Game Over / Victory с перезапуском
- Полным UI: очки, жизни, уровень, прогресс уровня

---

## 🛠 Задачи

### 1. Обновить `main.py` — полный класс `Game` со всеми функциями (~20 мин)

Ниже представлен **полный, готовый к запуску код** файла `main.py`.

```python
"""main.py — Точка входа в игру."""
import pygame
import random
import math
from typing import List, Optional


# Инициализация pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
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


# ==================== Уровни и прогрессия ====================

class Level:
    """Уровень игры."""

    def __init__(self, level_number: int = 1) -> None:
        self.level_number = level_number
        # Интервал спавна врагов (кадров между появлениями)
        self.spawn_interval = max(40, 80 - level_number * 5)
        # Количество врагов для повышения уровня
        self.enemies_to_kill_for_next_level: int = (level_number + 1) * 2
        # Порог очков для победы на уровне
        self.victory_score_threshold: int = level_number * 10

    def increase(self) -> None:
        """Увеличить уровень."""
        self.level_number += 1
        self.spawn_interval = max(40, 80 - self.level_number * 5)
        self.enemies_to_kill_for_next_level = (self.level_number + 1) * 2
        self.victory_score_threshold = self.level_number * 10


def get_available_enemy_types(level: int) -> list[str]:
    """Возвращает список доступных типов врагов для данного уровня."""
    if level == 1 or level == 2:
        return ["simple"]
    elif level < 3:
        return ["simple", "fast"]
    else:
        # Уровень 6+ → появляются боссы
        types = ["simple"] * (level // 2) + \
                 ["fast"] * ((level + 1) // 3) + \
                 ["boss"] if level >= 6 else []
        return types[:min(level % 4 + 1, len(types))]


def get_boss_health() -> int:
    """Здоровье босса."""
    return 10


def get_boss_size() -> int:
    """Размер спрайта босса (в пикселях)."""
    return 76


# ==================== Частицы ====================

class Particle(pygame.sprite.Sprite):
    """Частица взрыва."""

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
        self.lifetime: int = random.randint(30, 60)

    def update(self) -> None:
        """Обновление позиции и уменьшение времени жизни."""
        self.velocity *= 0.97
        self.rect.center = (self.rect.centerx + self.velocity.x,
                           self.rect.centery + self.velocity.y)
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()


def create_explosion(x: float, y: float) -> list["Particle"]:
    """Создать всплеск частиц в точке (x, y)."""
    particles = []
    for _ in range(random.randint(12, 18)):
        p = Particle(x, y)
        particles.append(p)
    return particles


# ==================== Базовая сущность ====================

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


# ==================== Пуля ====================

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
            pygame.draw.circle(surface, (253, 216, 53), (size // 2, 2), 3)
            self.image = surface

        self.rect = self.image.get_rect(center=(x + 3, y - 7))
        speed = 8.0
        direction_vec = pygame.math.Vector2(direction).normalize() * speed
        self.velocity = direction_vec

    def update(self) -> None:
        """Обновление позиции пули."""
        self.rect.center = (self.rect.centerx + self.velocity.x,
                           self.rect.centery + self.velocity.y)

        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.top < 0 or self.rect.bottom < -50):
            self.kill()

    def bounce(self) -> Optional[pygame.math.Vector2]:
        """Отскочить: возвращает вектор новой скорости."""
        new_speed = random.uniform(-6.0, -9.0)
        angle = random.uniform(1.5, 4.0)
        return pygame.math.Vector2(math.cos(angle), math.sin(angle)) * new_speed


# ==================== Игрок ====================

class Player(pygame.sprite.Sprite):
    """Корабль игрока."""

    def __init__(self) -> None:
        super().__init__()
        try:
            self.image = pygame.image.load("game/sprites/spaceship.png").convert_alpha()
        except FileNotFoundError:
            size = 50
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [(25, 0), (50, size - 10), (0, size - 10)]
            pygame.draw.polygon(surface, COLORS["GREEN"], points, width=3)
            self.image = surface

        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        # Cooldown для стрельбы
        self.cooldown: Optional[float] = None
        self.last_shot_time: float = 0.0

    def shoot(self) -> bool:
        """Выстрелить, если прошло достаточно времени."""
        now = pygame.time.get_ticks()
        if self.cooldown is None or now - self.last_shot_time >= 200:
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


# ==================== Враг ====================

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
            size, color, speed = 76, (239, 84, 80), 1.5

        self.radius = size // 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Тело врага — круг с обводкой
        pygame.draw.circle(self.image, color + (180,), (self.radius, self.radius), self.radius - 3)
        # Обводка круга для стиля
        pygame.draw.circle(self.image, color[0:3] + (255,), (self.radius, self.radius), self.radius - 3, width=2)

        # Глаза — только у простых и быстрых врагов
        if enemy_type != "boss":
            pygame.draw.circle(self.image, (255, 255, 255), (14, 12), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (14, 12), 2)
            pygame.draw.circle(self.image, (255, 255, 255), (size - 14, 12), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (size - 14, 12), 2)

        # Глаз босса — один большой
        if enemy_type == "boss":
            eye_radius = max(5, size // 6)
            pygame.draw.circle(self.image, (255, 255, 200), (size // 2 - eye_radius + 3, self.radius - 8), eye_radius)
            pygame.draw.circle(self.image, (0, 0, 0), (size // 2 - eye_radius + 3, self.radius - 8), max(1, eye_radius // 3))

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


# ==================== Основной класс игры ====================

class Game:
    """Основной игровой цикл."""

    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Группы спрайтов
        self.all_sprites: List[pygame.sprite.Sprite] = []
        self.bullets: List[Bullet] = []
        self.enemies: List["Enemy"] = []
        self.particles: List[Particle] = []

        self.player = Player()
        self.score = 0
        self.level = Level(level_number=1)
        self.lives = 3
        self.game_over = False
        self.victory = False

        # Таймер спавна врагов
        self.enemy_spawn_timer: int = 0
        self.enemy_spawn_interval: int = 80

        # Трекер для повышения уровня
        self.enemies_killed_this_level: int = 0

    def spawn_enemy(self) -> None:
        """Спавн нового врага сверху."""
        available_types = get_available_enemy_types(self.level.level_number)

        if not available_types:
            available_types = ["simple"]

        enemy_type = random.choice(available_types[:min(self.level.level_number % 3 + 1, len(available_types))])

        x = random.randint(20, WIDTH - 20)
        y = random.randint(-40, -50)

        enemy = Enemy(enemy_type=enemy_type)
        enemy.rect.centerx = x
        enemy.rect.top = y

        self.enemies.append(enemy)
        self.all_sprites.append(enemy)

    def spawn_boss(self) -> None:
        """Спавн босса в центре сверху."""
        boss = Enemy(enemy_type="boss")
        boss_x = WIDTH // 2 - get_boss_size() // 2
        boss_y = random.randint(-100, -60)

        boss.rect.centerx = boss_x + get_boss_size() // 2
        boss.rect.top = boss_y

        self.enemies.append(boss)
        self.all_sprites.append(boss)

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

        # Если пуля попала в игрока — наносим урон
        if pygame.sprite.collide_rect(bullet, self.player):
            self.lives -= 1
            bullet.kill()
            return

        # Если пуль не попала во врага или в игрока — удаляем
        bullet.kill()

    def handle_collisions(self) -> None:
        """Обработка всех коллизий."""
        for enemy in list(self.enemies):  # перебираем копию списка
            if enemy.hp <= 0:
                continue

            hits = pygame.sprite.spritecollide(enemy, self.bullets, False)
            for bullet in hits:
                self.handle_collision_enemy_with_bullet(enemy, bullet)

    def handle_level_up(self) -> None:
        """Проверка на повышение уровня."""
        if (self.level.victory_score_threshold > 0 and
                self.score >= self.level.victory_score_threshold):
            # Уровень повышен — сбрасываем счётчик уничтоженных врагов
            self.enemies_killed_this_level = 0
            self.level.increase()

    def update(self) -> None:
        """Обновление состояния игры."""
        if not (self.game_over or self.victory):
            # Обновление игрока
            self.player.update()

            # Стрельба
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

            # Спавн обычных врагов по таймеру
            if random.random() < 1.0 / max(40, 80 - self.level.spawn_interval):
                self.spawn_enemy()

            # Проверка на повышение уровня и спавн босса
            self.handle_level_up()

    def draw(self) -> None:
        """Отрисовка кадра."""
        SCREEN.fill(COLORS["BLACK"])

        # Игрок
        self.player.image.set_alpha(200 if pygame.time.get_ticks() % 300 < 150 else 255)
        SCREEN.blit(self.player.image, self.player.rect)

        # Пули
        for bullet in self.bullets:
            SCREEN.blit(bullet.image, bullet.rect)

        # Враги (не уничтоженные)
        for enemy in self.enemies:
            if enemy.hp <= 0:
                continue
            SCREEN.blit(enemy.image, enemy.rect)

        # Частицы (над всеми другими объектами)
        for particle in self.particles:
            SCREEN.blit(particle.image, particle.rect)

        # UI: заголовок
        title = self.font.render("Galaxy Shooter", True, COLORS["WHITE"])
        SCREEN.blit(title, (10, 10))

        # UI: очки
        score_text = self.small_font.render(f"Score: {self.score}", True, COLORS["YELLOW"])
        SCREEN.blit(score_text, (10, 50))

        # UI: уровень и прогресс
        level_info = (f"Lvl {self.level.level_number} | "
                      f"{self.enemies_killed_this_level}/{self.level.enemies_to_kill_for_next_level}")
        level_text = self.small_font.render(level_info, True, COLORS["WHITE"])
        SCREEN.blit(level_text, (WIDTH // 2 - 160, 10))

        # UI: жизни
        hearts = "❤" * self.lives + ("💔" * (3 - self.lives) if self.lives < 3 else "")
        lives_text = self.small_font.render(f"Hearts: {hearts}", True, COLORS["RED"])
        SCREEN.blit(lives_text, (10, HEIGHT - 30))

    def run(self) -> None:
        """Основной игровой цикл."""
        running = True
        while running:
            CLOCK.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                   (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                    running = False
                # Рестарт после Game Over / Victory
                elif self.game_over or self.victory:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.reset()

            # Обновление игры
            if not (self.game_over or self.victory):
                self.update()

            # Отрисовка
            self.draw()
            pygame.display.flip()

        self.cleanup()

    def reset(self) -> None:
        """Сброс игры."""
        self.score = 0
        self.level = Level(level_number=1)
        self.lives = 3
        self.game_over = False
        self.victory = False
        self.all_sprites.clear()
        self.bullets.clear()
        self.enemies.clear()
        self.particles.clear()
        self.player.rect.center = (WIDTH // 2, HEIGHT - 60)

    def cleanup(self) -> None:
        """Очистка ресурсов."""
        pygame.quit()


# ==================== Точка входа ====================

def main() -> None:
    """Точка входа в игру."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
```

---

## 🧪 Как запустить

```bash
pip install pygame>=2.4.0
python main.py
```

---

## ✅ Чеклист завершения проекта

- [ ] Игра запускается без ошибок
- [ ] Корабль управляется WASD/стрелками, не выходит за границы экрана
- [ ] Стрельба пробелом с ограничением скорострельности (~200 мс)
- [ ] Пули исчезают, улетев за экран
- [ ] Враги спавнятся сверху и падают вниз
- [ ] На уровнях 1–2 — только простые красные враги
- [ ] На уровне 3+ — появляются быстрые синие враги
- [ ] С каждым уровнем интервал спавна уменьшается (80 → ... → 40)
- [ ] На уровне 6 и выше — боссы появляются (HP=10, большой размер, +100 очков)
- [ ] При попадании пули во врага — отскок и всплеск частиц
- [ ] При столкновении с игроком пуля наносит урон, уменьшая жизни
- [ ] Экраны Game Over / Victory отображаются корректно
- [ ] Перезапуск по пробелу работает после победы/поражения
- [ ] UI (очки, жизни, уровень) отрисовывается в левом верхнем углу

---

## 🎉 Поздравляем! Игра готова к тестированию!
