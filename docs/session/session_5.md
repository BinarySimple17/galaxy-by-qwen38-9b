# Сессия 5: Прогрессия сложности и боссы ⬆️👹

## 📅 Дата начала: [вставить дату]

---

## 🎯 Цель сессии
Реализовать систему уровней (прогрессию сложности):
- После уничтожения N врагов — повышение уровня (+1)
- С каждым уровнем уменьшается интервал спавна врагов (минимум 40 кадров)
- Уровень 3+ → появляются быстрые синие враги
- Уровень 6+ → появляются боссы

---

## ✅ Результат после сессии
Игра запускается: при уничтожении достаточного количества врагов уровень повышается, скорость спавна увеличивается, появляются более опасные типы врагов. На уровне 6 и выше — боссы (крупные красные круги с большим глазом, HP=10).

---

## 🛠 Задачи

### 1. Создать файл `game/game_state.py` (~5 мин)

```python
"""game/game_state.py — Уровни и прогрессия сложности."""


class Level:
    """Уровень игры."""

    def __init__(self, level_number: int = 1) -> None:
        self.level_number = level_number

        # Интервал спавна врагов (кадров между появлениями)
        # Стартовый интервал: 80 кадров (~1.3 сек при 60 FPS)
        # Каждый уровень уменьшает интервал на 5 кадров, минимум 40
        self.spawn_interval = max(40, 80 - level_number * 5)

        # Количество врагов, которое нужно уничтожить для повышения уровня
        # Уровень Y → нужно уничтожить X × Y врагов
        self.enemies_to_kill_for_next_level: int = (level_number + 1) * 2

        # Порог очков для победы на уровне (X × Y, где X=10, Y=current_level)
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
```

### 2. Обновить `main.py` с поддержкой уровней (~6 мин)

#### А. В импорте добавить `Level`:

```python
from game.game_state import Level, get_available_enemy_types
```

#### Б. В классе `Game` — инициализация уровня:

```python
class Game:
    """Основной игровой цикл."""

    def __init__(self) -> None:
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.all_sprites: List[pygame.sprite.Sprite] = []
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []

        # Спрайты — теперь сущности уровня
        self.player = Player()
        self.score = 0
        self.level = Level(level_number=1)   # ← создаём уровень

        self.lives = 3
        self.game_over = False
        self.victory = False

        self.enemy_spawn_timer: int = 0
        self.enemy_spawn_interval: int = 80

        # Трекер для повышения уровня
        self.enemies_killed_this_level: int = 0
```

#### В. Обновить метод `spawn_enemy()` — выбирать врага с учётом уровня:

```python
def spawn_enemy(self) -> None:
    """Спавн нового врага сверху."""
    # Выбираем доступные типы для текущего уровня
    available_types = get_available_enemy_types(self.level.level_number)

    if not available_types:
        available_types = ["simple"]  # fallback, если нет доступных типов

    enemy_type = random.choice(available_types[:min(self.level.level_number % 3 + 1, len(available_types))])

    x = random.randint(20, WIDTH - 20)
    y = random.randint(-40, -50)

    enemy = Enemy(enemy_type=enemy_type)
    enemy.rect.centerx = x
    enemy.rect.top = y

    self.enemies.append(enemy)
    self.all_sprites.append(enemy)


def spawn_enemy_at_boss_position(self) -> None:
    """Спавн босса в центре сверху."""
    boss_x = WIDTH // 2 - get_boss_size() // 2
    boss_y = random.randint(-100, -60)

    boss = Enemy(enemy_type="boss")
    boss.rect.centerx = boss_x + get_boss_size() // 2
    boss.rect.top = boss_y

    self.enemies.append(boss)
    self.all_sprites.append(boss)


def handle_level_up(self) -> None:
    """Проверка на повышение уровня."""
    if self.level.victory_score_threshold > 0 and self.score >= self.level.victory_score_threshold:
        # Уровень повышен — сбрасываем счётчик уничтоженных врагов
        self.enemies_killed_this_level = 0
        self.level.increase()

        # Визуальный эффект повышения уровня (например, мигающий текст)
        return True

    return False
```

#### Г. Обновить метод `update()` — повышение уровня:

```python
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
        if random.random() < 1.0 / max(40, 80 - self.level.spawn_interval):
            self.spawn_enemy()
```

#### Д. Добавить обработку боссов — спавн босса при повышении уровня:

```python
def spawn_boss(self) -> None:
    """Спавн босса."""
    boss = Enemy(enemy_type="boss")
    boss.rect.centerx = WIDTH // 2 - 38  # центрируем
    boss.rect.top = random.randint(-100, -60)

    self.enemies.append(boss)
    self.all_sprites.append(boss)


def handle_level_up(self) -> None:
    """Проверка на повышение уровня и спавн босса."""
    if (self.level.victory_score_threshold > 0 and
            self.score >= self.level.victory_score_threshold):

        # Уровень повышен — сбрасываем счётчик уничтоженных врагов
        self.enemies_killed_this_level = 0
        self.level.increase()

        # Если уровень 6 или выше — спавним босса
        if self.level.level_number >= 6:
            self.spawn_boss()


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

        # Спавн обычных врагов по таймеру
        if random.random() < 1.0 / max(40, 80 - self.level.spawn_interval):
            self.spawn_enemy()

        # Проверка на повышение уровня
        self.handle_level_up()
```

### 3. Обновить `handle_collisions()` — уничтожение врага и начисление очков:

```python
def handle_bullet_enemy_collisions(self) -> None:
    """Проверка попаданий пуль во врагов."""
    for enemy in list(self.enemies):  # перебираем копию списка
        if enemy.hp <= 0:
            continue

        hits = pygame.sprite.spritecollide(enemy, self.bullets, False)
        for bullet in hits:
            self.handle_collision_enemy_with_bullet(enemy, bullet)


def handle_collision_enemy_with_bullet(self, enemy: "Enemy", bullet: Bullet) -> None:
    """Обработка коллизии врага с пулей игрока."""
    if enemy.hp <= 0:
        return

    # Пуля отскакивает (враг стреляет обратно в игрока)
    bounce_direction = bullet.bounce()
    bullet.velocity = bounce_direction

    # Если пуля попала в игрока — наносим урон, иначе уничтожаем врага
    if pygame.sprite.collide_rect(bullet, self.player):
        self.lives -= 1
        bullet.kill()
        return

    # Враг уничтожен
    enemy.hp = 0
    bullet.kill()

    # Начисляем очки
    self.score += enemy.score_value

    # Увеличиваем счётчик уничтоженных врагов
    if enemy.enemy_type == "boss":
        self.enemies_killed_this_level += 10
    else:
        self.enemies_killed_this_level += 1


def handle_collisions(self) -> None:
    """Обработка всех коллизий."""
    # Пули → враги
    for enemy in list(self.enemies):
        if enemy.hp <= 0:
            continue

        hits = pygame.sprite.spritecollide(enemy, self.bullets, False)
        for bullet in hits:
            self.handle_collision_enemy_with_bullet(enemy, bullet)
```

### 4. Обновить `draw()` — отображение уровня и прогресса (~2 мин):

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

    # UI
    title = self.font.render("Galaxy Shooter", True, COLORS["WHITE"])
    SCREEN.blit(title, (10, 10))

    score_text = self.small_font.render(f"Score: {self.score}", True, COLORS["YELLOW"])
    SCREEN.blit(score_text, (10, 50))

    level_text = self.small_font.render(
        f"Level: {self.level.level_number} | "
        f"Enemies killed this level: {self.enemies_killed_this_level}/{self.level.enemies_to_kill_for_next_level}",
        True, COLORS["WHITE"]
    )
    SCREEN.blit(level_text, (WIDTH // 2 - 180, 10))

    lives_text = self.small_font.render(
        f"Hearts: {'❤' * self.lives}{'💔' * (3 - self.lives)}", True, COLORS["RED"]
    )
    SCREEN.blit(lives_text, (10, HEIGHT - 30))

    # Индикатор прогресса босса (если есть)
    if any(e.enemy_type == "boss" for e in self.enemies):
        boss = [e for e in self.enemies if e.enemy_type == "boss"][0]
        boss_health_bar = pygame.Surface((20, 6), pygame.SRCALPHA)
        boss_max_hp = get_boss_health()
        boss_current_hp = boss.hp
        bar_width = int((boss_current_hp / boss_max_hp) * 180)
        pygame.draw.rect(boss_health_bar, COLORS["GREEN"], (0, 0, bar_width, 6))
        SCREEN.blit(boss_health_bar, (WIDTH - 225, HEIGHT - 30))


# В init():
self.level = Level(level_number=1)
```

---

## 🧪 Как протестировать

Запустить игру:

```bash
python main.py
```

**Наблюдается:**
- На уровне 1–2 — только простые красные враги (HP=1, скорость 2.5), +10 очков за каждого
- На уровне 3+ появляются быстрые синие враги (маленькие, волновое движение)
- С каждым уровнем интервал спавна уменьшается: 80 → 75 → 70 → ... → 40 кадров
- При достижении порога очков на уровне — уровень повышается, счётчик уничтоженных врагов сбрасывается
- На уровне 6 и выше — появляются боссы (крупные красные круги с глазом, HP=10, медленно падают), +100 очков за каждого

---

## 🐛 Возможные проблемы

| Проблема | Решение |
|----------|---------|
| Босс не появляется | Проверить условие `level.level_number >= 6` в методе `handle_level_up()` |
| Уровень не повышается | Убедиться, что порог очков достигнут и счётчик уничтоженных врагов соответствует порогу |
| Интервал спавна не уменьшается | Проверить формулу в `Level.increase()`: `spawn_interval = max(40, 80 - level * 5)` |

---

## ✅ Чеклист завершения сессии

- [ ] Игра запускается без ошибок
- [ ] На уровне 1–2 — только простые враги
- [ ] На уровне 3+ появляются быстрые синие враги
- [ ] Интервал спавна уменьшается с каждым уровнем (80 → 75 → ... → 40)
- [ ] При достижении порога очков уровень повышается
- [ ] На уровне 6 и выше — появляются боссы (HP=10, большой размер)

---

## 🚀 Переходим к последней сессии → Сессия 6: Game Over / Victory + UI
