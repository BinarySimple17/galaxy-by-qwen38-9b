# Сессия 6: Победа, рестарт и финальный UI 🏆🎉 (v2 — доработка)

> **ВАЖНО:** Это ПЕРЕРАБОТАННАЯ сессия. Из старой версии НЕ нужно переписывать
> `main.py` целиком — игра уже модульная и рабочая.
>
> Текущие пробелы, которые закрывает сессия:
> 1. Флаг `victory` **никогда не выставляется** — победы в игре нет.
> 2. `reset()` не обнуляет `enemies_killed_this_level` и `enemy_spawn_timer`
>    (после рестарта прогресс уровня показывался неверно).
> 3. Экран есть только у поражения; экран победы отсутствует.

---

## ⚠️ Правила для агента (обязательные)

1. Меняй только файлы, указанные в шагах: `game/config.py`, `main.py`,
   `tests/run_all.py` и новый файл `tests/test_final.py`.
2. Каждый шаг: «НАЙДИ» → точный якорь из текущего кода, «ЗАМЕНИ НА» → блок
   целиком, затем «ПРОВЕРКА». Упало — `git checkout -- <файл>` и шаг заново.
3. Отступы Python — 4 пробела на уровень. Копируй блоки без правок.
4. Файлы `game/game_state.py`, `game/enemy_sprite.py` и остальные модули
   `game/` **не трогать**.
5. Все команды — из корня проекта в PowerShell через `.venv\Scripts\python.exe`.

---

## 📌 Текущее состояние

| Поведение | Где | Статус |
|-----------|-----|--------|
| Game Over при `lives <= 0` + экран | сессия 4 | ✅ |
| HP-бар босса | сессия 5 | ✅ |
| Условие победы (`victory = True`) | нигде | ❌ **нет** |
| Экран VICTORY | `draw()` | ❌ **нет** |
| Полный сброс счётчиков при рестарте | `reset()` | ❌ частично |
| Рестарт по SPACE после конца игры | `run()` | ✅ уже вызывает `reset()` |

---

## 🎯 Цель сессии

1. Константа `VICTORY_LEVEL = 10`: победа наступает, когда номер уровня
   становится больше `VICTORY_LEVEL`.
2. Экран VICTORY по центру (зелёный), рядом GAME OVER (красный).
3. `reset()` сбрасывает ВСЁ: очки, жизни, уровень, флаги, счётчики, группы.

---

## ✅ Определение готовности (Definition of Done)

- [ ] `tests/test_final.py` → `ИТОГО: 9 PASS / 0 FAIL`
- [ ] `tests/run_all.py` → `ALL TESTS PASSED (7)`
- [ ] Изменены только `game/config.py`, `main.py`, `tests/run_all.py`,
      добавлен `tests/test_final.py`

---

## 🛠 Шаги

### Шаг 6.1. Константа победы

ФАЙЛ: `game/config.py`.

НАЙДИ (конец файла):

```python
# --- Параметры победы/поражения ---
LIVES_PER_LEVEL_BASE = 10  # базовый порог очков для победы на уровне
```

ЗАМЕНИ НА:

```python
# --- Параметры победы/поражения ---
LIVES_PER_LEVEL_BASE = 10  # базовый порог очков для победы на уровне
VICTORY_LEVEL = 10         # уровень, после которого наступает победа
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe -c "from game.config import VICTORY_LEVEL; print('VICTORY_LEVEL', VICTORY_LEVEL)"
```

Ожидается вывод: `VICTORY_LEVEL 10`

---

### Шаг 6.2. Импорт константы

ФАЙЛ: `main.py`.

НАЙДИ (блок импорта в начале файла):

```python
from game.config import (
    WIDTH, HEIGHT, FPS, COLORS, PLAYER_SPEED,
    PLAYER_COOLDOWN_MS, ENEMY_SIMPLE_SIZE, ENEMY_FAST_SIZE,
    ENEMY_BOSS_SIZE, ENEMY_SIMPLE_SPEED, ENEMY_FAST_SPEED,
    ENEMY_BOSS_SPEED, STARTING_SPAWN_INTERVAL, MIN_SPAWN_INTERVAL,
    LEVEL_3_THRESHOLD, LEVEL_BOSS_THRESHOLD, LIVES_PER_LEVEL_BASE,
)
```

ЗАМЕНИ НА:

```python
from game.config import (
    WIDTH, HEIGHT, FPS, COLORS, PLAYER_SPEED,
    PLAYER_COOLDOWN_MS, ENEMY_SIMPLE_SIZE, ENEMY_FAST_SIZE,
    ENEMY_BOSS_SIZE, ENEMY_SIMPLE_SPEED, ENEMY_FAST_SPEED,
    ENEMY_BOSS_SPEED, STARTING_SPAWN_INTERVAL, MIN_SPAWN_INTERVAL,
    LEVEL_3_THRESHOLD, LEVEL_BOSS_THRESHOLD, LIVES_PER_LEVEL_BASE,
    VICTORY_LEVEL,
)
```

---

### Шаг 6.3. Условие победы в handle_level_up

ФАЙЛ: `main.py`.

НАЙДИ (метод целиком):

```python
    def handle_level_up(self) -> None:
        """Проверить повышение уровня."""
        if (self.level.victory_score_threshold > 0 and
                self.score >= self.level.victory_score_threshold):
            # Уровень повышен — сбрасываем счётчик уничтоженных врагов
            self.enemies_killed_this_level = 0
            increase_level(self.level)

            # На уровне 6+ каждое повышение уровня приводит босса
            if self.level.level_number >= LEVEL_BOSS_THRESHOLD:
                self.spawn_boss()
```

ЗАМЕНИ НА:

```python
    def handle_level_up(self) -> None:
        """Проверить повышение уровня и условие победы."""
        if (self.level.victory_score_threshold > 0 and
                self.score >= self.level.victory_score_threshold):
            # Уровень повышен — сбрасываем счётчик уничтоженных врагов
            self.enemies_killed_this_level = 0
            increase_level(self.level)

            # Победа: пройден уровень VICTORY_LEVEL
            if self.level.level_number > VICTORY_LEVEL:
                self.victory = True
                return

            # На уровне 6+ каждое повышение уровня приводит босса
            if self.level.level_number >= LEVEL_BOSS_THRESHOLD:
                self.spawn_boss()
```

ПРОВЕРКА (регрессия прогрессии — victory-ветка ещё не должна сработать
на низких уровнях):

```powershell
.venv\Scripts\python.exe tests\test_progression.py
```

Ожидается последняя строка: `ИТОГО: 8 PASS / 0 FAIL`

---

### Шаг 6.4. Два экрана: GAME OVER и VICTORY

ФАЙЛ: `main.py`.

НАЙДИ (в конце метода `draw()`, блок из сессии 4):

```python
        # Экран поражения
        if self.game_over:
            over = self.big_font.render("GAME OVER", True, COLORS["WHITE"])
            hint = self.small_font.render("SPACE — рестарт", True, COLORS["YELLOW"])
            self.screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
```

ЗАМЕНИ НА:

```python
        # Экраны Game Over / Victory
        if self.game_over:
            over = self.big_font.render("GAME OVER", True, COLORS["RED"])
            hint = self.small_font.render("SPACE — рестарт", True, COLORS["WHITE"])
            self.screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        elif self.victory:
            win = self.big_font.render("VICTORY!", True, COLORS["GREEN"])
            hint = self.small_font.render(
                f"Пройден уровень {VICTORY_LEVEL}! SPACE — заново",
                True, COLORS["YELLOW"])
            self.screen.blit(win, win.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
```

---

### Шаг 6.5. Полный сброс в reset()

ФАЙЛ: `main.py`.

НАЙДИ (начало метода `reset()`):

```python
    def reset(self) -> None:
        """Сброс игры."""
        self.score = 0
        self.lives = 3
        self.level = Level(level_number=1)
        self.game_over = False
        self.victory = False
```

ЗАМЕНИ НА:

```python
    def reset(self) -> None:
        """Сброс игры."""
        self.score = 0
        self.lives = 3
        self.level = Level(level_number=1)
        self.game_over = False
        self.victory = False
        self.enemies_killed_this_level = 0
        self.enemy_spawn_timer = 0
```

---

### Шаг 6.6. Финальный интеграционный тест

СОЗДАЙ ФАЙЛ: `tests/test_final.py`.

```python
"""Финал: победа по уровню, заморозка цикла, полный рестарт, экраны."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
random.seed(6)

import pygame


class FakeKeys(dict):
    def __getitem__(self, k):
        return dict.get(self, k, False)


class FakeClock:
    t = 1000


pygame.time.get_ticks = lambda: FakeClock.t
pygame.key.get_pressed = lambda: FakeKeys({pygame.K_SPACE: True})

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("[PASS] " if cond else "[FAIL] ") + name + ((" -- " + str(detail)) if detail else ""))


import main as gm
from game.enemy_sprite import Enemy
from game.config import VICTORY_LEVEL, WIDTH, HEIGHT

g = gm.Game()
TARGET = (403, 300)


def keep_target():
    for s in list(g.enemies):
        if s.enemy_type == "simple":
            s.rect.center = TARGET
            return
    e = Enemy("simple")
    e.rect.center = TARGET
    g.enemies.add(e)
    g.all_sprites.add(e)


# --- Часть 1. Победа ---
frames = 0
try:
    while not g.victory and frames < 6000:
        FakeClock.t += 250          # каждый кадр кулдаун истёк
        g.update()
        keep_target()
        frames += 1
    crashed = False
except Exception:
    import traceback
    traceback.print_exc()
    crashed = True

check("F1. Победа достигается фармом без краша",
      not crashed and g.victory is True,
      f"кадров={frames}, lvl={g.level.level_number}")
check("F2. Уровень победы = VICTORY_LEVEL + 1",
      g.level.level_number == VICTORY_LEVEL + 1,
      f"lvl={g.level.level_number}, VICTORY_LEVEL={VICTORY_LEVEL}")

# --- Цикл замер после победы ---
snap_bullets = tuple(sorted(b.rect.center for b in g.bullets))
snap_counts = (len([s for s in g.all_sprites]), len([s for s in g.enemies]))
for _ in range(20):
    FakeClock.t += 250
    g.update()
check("F3. update() заморожен при victory",
      tuple(sorted(b.rect.center for b in g.bullets)) == snap_bullets and
      (len([s for s in g.all_sprites]), len([s for s in g.enemies])) == snap_counts)

# --- Экран победы рисуется ---
try:
    g.draw()
    check("F4. draw() с экраном победы без ошибок", True)
except Exception as ex:
    check("F4. draw() с экраном победы без ошибок", False, repr(ex))

# --- Часть 2. Рестарт из поражения ---
g.reset()

px = g.player.rect.centerx
py = g.player.rect.top
enemy = Enemy("simple")
enemy.rect.center = (px, py - 10)
g.enemies.add(enemy)
g.all_sprites.add(enemy)
b = gm.Bullet(x=px - 20, y=py + 25)
b.rect.center = (px, py - 5)
g.bullets.add(b)
g.all_sprites.add(b)
g.lives = 1
g.handle_collisions()
check("F5. Поражение воспроизводится после reset()", g.game_over is True,
      f"lives={g.lives}")

# --- Полный сброс ---
g.reset()
check("F6. Флаги сброшены", g.game_over is False and g.victory is False)
check("F7. Счётчики обнулены",
      g.score == 0 and g.lives == 3 and g.level.level_number == 1 and
      g.enemies_killed_this_level == 0 and g.enemy_spawn_timer == 0,
      f"score={g.score}, lives={g.lives}, killed={g.enemies_killed_this_level}, "
      f"timer={g.enemy_spawn_timer}")
check("F8. Группы пусты, игрок на месте",
      len([s for s in g.enemies]) == 0 and len([s for s in g.bullets]) == 0 and
      len([s for s in g.particles]) == 0 and
      g.player in [s for s in g.all_sprites] and
      g.player.rect.center == (WIDTH // 2, HEIGHT - 60))

# --- Игра идёт после рестарта ---
fired = False
try:
    for _ in range(60):
        FakeClock.t += 250
        g.update()
        if len([s for s in g.bullets]) > 0:
            fired = True
    check("F9. После рестарта игра стреляет и живёт", fired)
except Exception as ex:
    check("F9. После рестарта игра стреляет и живёт", False, repr(ex))

print()
total_pass = sum(1 for _, c in results if c)
print(f"ИТОГО: {total_pass} PASS / {len(results) - total_pass} FAIL")
sys.exit(0 if total_pass == len(results) else 1)
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe tests\test_final.py
```

Ожидается последняя строка: `ИТОГО: 9 PASS / 0 FAIL`

---

### Шаг 6.7. Подключить тест к раннеру

ФАЙЛ: `tests/run_all.py`.

НАЙДИ:

```python
TESTS = [
    "test_session2.py",
    "test_collisions.py",
    "test_lifecycle.py",
    "test_progression.py",
    "test_gameover.py",
    "test_boss.py",
]
```

ЗАМЕНИ НА:

```python
TESTS = [
    "test_session2.py",
    "test_collisions.py",
    "test_lifecycle.py",
    "test_progression.py",
    "test_gameover.py",
    "test_boss.py",
    "test_final.py",
]
```

---

### Шаг 6.8. Финальная проверка всего проекта

```powershell
.venv\Scripts\python.exe tests\run_all.py
```

Ожидаемое окончание вывода:

```
ALL TESTS PASSED (7)
```

Ручная проверка (если есть дисплей):

```powershell
.venv\Scripts\python.exe main.py
```

Сценарий: проиграй (потеряй 3 сердца) → `GAME OVER`, `SPACE` → игра заново;
затем фарми до уровня выше 10 → зелёный `VICTORY!`, `SPACE` → снова с 1 уровня.

---

## 🐛 Если что-то пошло не так

| Симптом | Причина | Действие |
|---------|---------|----------|
| F1 `[FAIL]`: победа не наступает за 6000 кадров | Ветка victory стоит ПОСЛЕ spawn_boss без `return`, либо условие `>=` вместо `>` | Сверь метод с листингом 6.3 посимвольно |
| F2 `[FAIL]`: lvl != VICTORY_LEVEL + 1 | Условие `>= VICTORY_LEVEL` | Должно быть строго `> VICTORY_LEVEL` |
| F3 `[FAIL]`: спрайты двигаются после победы | Нарушена первая строка `update()` | Верни: `if self.game_over or self.victory: return` |
| F7 `[FAIL]`: killed/timer не нули | Пропущен шаг 6.5 | Выполни шаг 6.5 |
| F9 `[FAIL]`: нет выстрелов | Сбита кулдаун-логика или пробел не «зажат» в тесте | Не меняй `player_sprite.py`; сверь листинг 6.6 |
| B/P/G/C-тесты упали после шагов | Задеты соседние методы | `git checkout -- main.py`; повтори шаги по одному |

---

## 🚦 Чеклист завершения сессии

- [ ] Победа наступает при переходе на уровень `VICTORY_LEVEL + 1`
- [ ] Экран VICTORY зелёный с подсказкой, GAME OVER красный
- [ ] `reset()` обнуляет все поля состояния и группы
- [ ] `tests/test_final.py` → 9 PASS / 0 FAIL
- [ ] `tests/run_all.py` → `ALL TESTS PASSED (7)`
- [ ] Модули `game/*` не изменялись (кроме `config.py`, шаг 6.1)

---

## 🎉 Проект завершён — итоговое состояние игры

| Возможность | Реализация |
|-------------|------------|
| Корабль WASD/стрелки, границы экрана | `game/player_sprite.py` |
| Стрельба пробелом, кулдаун 200 мс | `Player.shoot` + тесты 3a/3b |
| Отскок пуль, урон игроку от отскочившей пули | `handle_collision_enemy_with_bullet` |
| Враги simple/fast/boss, волны, глаз босса | `game/enemy_sprite.py` |
| Взрывы частиц | `game/particles.py` + тест C7 |
| Прогрессия: уровни, интервал спавна, пулы типов | `game/game_state.py` + P1–P7 |
| Боссы с 10 HP, +100 очков, HP-бар | тест C10–C13, B8–B12 |
| Game Over при 0 жизней + экран | сессия 4 + G1–G5 |
| Victory после уровня 10 + экран | сессия 6 + F1–F4 |
| Рестарт по SPACE с полным сбросом | `reset()` + F5–F9 |
| Регрессионный набор: 74 автопроверки | `tests/run_all.py` |

**Финальная команда проверки:**

```powershell
.venv\Scripts\python.exe tests\run_all.py
```
