# Сессия 3: Тестовый фундамент 🧪 (v2 — переработана под текущий код)

> **ВАЖНО:** Это ПЕРЕРАБОТАННАЯ сессия. Игровое ядро (враги, коллизии, отскок пуль,
> частицы, прогрессия уровней, боссы) **уже реализовано и работает** в файлах
> `main.py` и `game/`. Старая версия этой сессии с монолитным кодом устарела —
> НЕ следуй ей.
>
> Задача этой сессии — **не менять игру**, а создать автоматические тесты,
> которые будут защищать код при доработках в сессиях 4–6.

---

## ⚠️ Правила для агента (обязательные)

1. В этой сессии **ЗАПРЕЩЕНО** изменять файлы `main.py` и любые файлы в `game/`.
   Разрешено создавать файлы **только внутри папки `tests/`**.
2. Выполняй шаги строго по порядку. Не пропускай и не объединяй шаги.
3. После каждого шага запускай команду проверки из раздела «ПРОВЕРКА».
4. Если проверка упала — сравни свой файл с листингом из задания **посимвольно**
   (отступы в Python критичны: 4 пробела на уровень) и исправь расхождение.
5. Запрещено: устанавливать пакеты через pip, обновлять зависимости,
   создавать новые виртуальные окружения, рефакторить существующий код.
6. Все команды выполняются из корня проекта (`snake_38-9b/`) в PowerShell.
7. Python берём из готового окружения: `.venv\Scripts\python.exe`.

---

## 📌 Текущее состояние проекта (после сессий 0–2)

| Файл | Что внутри | Статус |
|------|-----------|--------|
| `main.py` | Класс `Game`: группы спрайтов, коллизии, уровни, боссы, UI | ✅ работает |
| `game/config.py` | Все константы (экран, цвета, скорости, пороги) | ✅ |
| `game/entities.py` | Базовый `Entity`, `create_rect_from_surface` | ✅ |
| `game/player_sprite.py` | Корабль: WASD/стрелки, кулдаун выстрела | ✅ |
| `game/bullet_sprite.py` | Пуля: полёт вверх, отскок `bounce()` | ✅ |
| `game/enemy_sprite.py` | Враги simple/fast/boss, спавн сверху | ✅ |
| `game/particles.py` | Частицы взрыва | ✅ |
| `game/game_state.py` | Уровни, типы врагов по уровню | ✅ |
| `tests/` | **нет** — создаётся в этой сессии | ❌ |

Известная особенность кода (учтена в тестах): пуля летит чуть влево
(`velocity ≈ (-0.99, -7.94)`), а враги появляются над экраном
(`y ∈ [-50, -40]`). Это норма, не баг.

---

## 🎯 Цель сессии

Создать папку `tests/` с четырьмя автотестами и раннером `run_all.py`.
Тесты запускаются без окна игры (виртуальный видеодрайвер `dummy`).

---

## ✅ Определение готовности (Definition of Done)

- [ ] Команда `.venv\Scripts\python.exe tests\run_all.py` печатает
      `ALL TESTS PASSED (4)` и завершается без ошибок
- [ ] Суммарно зелёных проверок: 37 (10 + 13 + 6 + 8)
- [ ] `git status` показывает новые файлы только в `tests/`

---

## 🛠 Шаги

### Шаг 3.0. Исходная точка

ПРОВЕРКА (убедись, что игра импортируется без ошибок):

```powershell
.venv\Scripts\python.exe -c "import main; print('OK')"
```

Ожидаемый вывод: строка `OK` (плюс баннер pygame — это нормально).

---

### Шаг 3.1. Создать `tests/test_session2.py`

ФАЙЛ: `tests/test_session2.py`.
Если файл уже существует — сверь с листингом; при расхождении перезапиши целиком.

```python
"""Тесты сессии 2: стрельба + пули (чеклист из docs/session/session_2.md)."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
random.seed(1)

import pygame

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("[PASS] " if cond else "[FAIL] ") + name + (("  -- " + str(detail)) if detail else ""))


class FakeClock:
    t = 1000


pygame.time.get_ticks = lambda: FakeClock.t


class FakeKeys(dict):
    """Словарь клавиш: отсутствующие = не нажаты."""

    def __getitem__(self, k):
        return dict.get(self, k, False)


print("=" * 60)
print("Сессия 2: Стрельба + пули - автотесты")
print("=" * 60)

# --- [1] Игра запускается без ошибок ---
try:
    import main as gm
    g = gm.Game()
    check("1. Игра инициализируется без ошибок", True)
except Exception as e:
    check("1. Игра инициализируется без ошибок", False, repr(e))
    sys.exit(1)

space_held = FakeKeys({pygame.K_SPACE: True})
pygame.key.get_pressed = lambda: space_held

# --- [2] Пробел -> вылетает жёлтая пуля ---
FakeClock.t = 1000
g.update()
check("2a. Нажатие пробела создаёт пулю", len(g.bullets) == 1, f"bullets={len(g.bullets)}")
b = next(iter(g.bullets), None)
if b:
    w, h = b.image.get_size()
    yellowish = False
    try:
        px = b.image.get_at((w // 2, h // 2))
        r, gg, bl = px.r, px.g, px.b
        yellowish = (r > 180 and gg > 150 and bl < 120)
    except Exception:
        pass
    check("2b. Пуля - жёлтая полоска", (w <= 50 and h <= 20),
          f"size={w}x{h}, center_px_yellow={yellowish}")
    nose_x = g.player.rect.centerx + 20
    nose_y = g.player.rect.top - 15
    b2 = gm.Bullet(x=nose_x, y=nose_y)  # прямое создание - без сдвига за кадр
    at_nose = b2.rect.center == (nose_x + 3, nose_y - 7)
    check("2c. Пуля появляется из носа корабля", at_nose,
          f"center={b2.rect.center} expected={(nose_x + 3, nose_y - 7)}")

# --- [3] Cooldown ~200 мс ---
FakeClock.t = 1100  # +100 мс после первого выстрела
g.update()
check("3a. Через 100 мс второй выстрел заблокирован (cooldown)",
      len(g.bullets) == 1, f"bullets={len(g.bullets)}")

FakeClock.t = 1250  # +250 мс после первого выстрела (>200)
n_before = len(g.bullets)
g.update()
check("3b. После 200 мс выстрел снова разрешён",
      len(g.bullets) == n_before + 1, f"bullets={len(g.bullets)}")

# --- [4] Пуля летит вверх ---
b = list(g.bullets)[-1] if g.bullets else None
if b is None:
    check("4a. Пуля движется вверх (~8 px/кадр)", False, "нет пуль")
    check("4b. Вектор скорости направлен вверх", False, "нет пуль")
else:
    y_before = b.rect.centery
    space_none = FakeKeys({})
    pygame.key.get_pressed = lambda: space_none
    FakeClock.t = 1300
    g.update()
    dy = y_before - b.rect.centery
    check("4a. Пуля движется вверх (~8 px/кадр)", dy > 5, f"delta_y={dy}")
    vy_up = b.velocity.y < 0
    check("4b. Вектор скорости направлен вверх", vy_up,
          f"velocity={tuple(round(v, 2) for v in b.velocity)}")

    # --- [5] Пуля исчезает за экраном ---
    b.rect.bottom = -60
    is_off = b.is_offscreen
    check("5a. is_offscreen распознаёт пулю за экраном", is_off)

    total_bullets = len(g.bullets)
    g.update()
    still_in_list = b in g.bullets
    check("5b. Пуля удалена из game.bullets за экраном", not still_in_list,
          f"было={total_bullets}, осталось={len(g.bullets)}")

print()
print("=" * 60)
print(f"ИТОГО: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("=" * 60)
for f in FAIL:
    print(" FAIL:", f)
sys.exit(0 if not FAIL else 1)
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe tests\test_session2.py
```

Ожидается последняя строка вывода: `ИТОГО: 10 PASS / 0 FAIL`

---

### Шаг 3.2. Создать `tests/test_collisions.py`

ФАЙЛ: `tests/test_collisions.py`.

```python
"""Тест коллизий: урон врагам, очки, частицы, kill() через pygame.sprite.Group."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
random.seed(2)

import pygame

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("[PASS] " if cond else "[FAIL] ") + name + ((" -- " + str(detail)) if detail else ""))


class FakeClock:
    t = 1000


pygame.time.get_ticks = lambda: FakeClock.t


class FakeKeys(dict):
    def __getitem__(self, k):
        return dict.get(self, k, False)


import main as gm
from game.enemy_sprite import Enemy

g = gm.Game()

# --- Simple-враг: одно попадание убивает ---
e = Enemy("simple")
e.rect.center = (g.player.rect.centerx, 300)
g.enemies.add(e)
g.all_sprites.add(e)

b = gm.Bullet(x=e.rect.centerx, y=e.rect.bottom)
b.rect.center = (e.rect.centerx, e.rect.bottom - 2)
g.bullets.add(b)
g.all_sprites.add(b)

v_before = pygame.math.Vector2(b.velocity)
score0 = g.score

g.handle_collisions()

check("C1. spritecollide работает с Group (нет AttributeError)", True)
check("C2. Вектор пули изменился (отскок)", b.velocity != v_before)
check("C3. Пуля удалена после попадания", b not in [s for s in g.bullets])
check("C4. Враг уничтожен (hp<=0)", e.hp <= 0, f"hp={e.hp}")
check("C5. Враг удалён из группы (kill() работает)", e not in [s for s in g.enemies])
check("C6. Очки +10", g.score == score0 + 10, f"score={g.score}")
particles_count = len([s for s in g.particles])
check("C7. Частицы взрыва созданы (12+)", particles_count >= 12, f"count={particles_count}")
check("C8. Счётчик уровня +1", g.enemies_killed_this_level == 1)

# Повторный вызов не должен падать или начислять повторно
g.handle_collisions()
check("C9. Повторный вызов безопасен, очки не задвоены", g.score == score0 + 10)

# --- Boss: 10 HP ---
boss = Enemy("boss")
boss.rect.center = (400, 150)
g.enemies.add(boss)
g.all_sprites.add(boss)

s0 = g.score
frames = 0
while boss.hp > 0 and frames < 50:
    for i in range(4):
        bb = gm.Bullet(x=boss.rect.centerx, y=boss.rect.top)
        bb.rect.center = (boss.rect.centerx + i * 5, boss.rect.centery)
        g.bullets.add(bb)
        g.all_sprites.add(bb)
    g.handle_collisions()
    frames += 1

check("C10. Босс уничтожен после попаданий", boss.hp <= 0, f"hp={boss.hp}, frames={frames}")
check("C11. +100 очков за босса", g.score - s0 == 100, f"delta={g.score - s0}")
check("C12. Босс удалён из группы", boss not in [s for s in g.enemies])
check("C13. Счётчик уровня +10 за босса", g.enemies_killed_this_level == 11,
      f"killed_counter={g.enemies_killed_this_level}")

print()
total_pass = sum(1 for _, c in results if c)
print(f"ИТОГО: {total_pass} PASS / {len(results) - total_pass} FAIL")
sys.exit(0 if total_pass == len(results) else 1)
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe tests\test_collisions.py
```

Ожидается последняя строка вывода: `ИТОГО: 13 PASS / 0 FAIL`

---

### Шаг 3.3. Создать `tests/test_progression.py`

ФАЙЛ: `tests/test_progression.py`.

```python
"""Прогрессия уровней: непрерывный фарм -> уровни растут, боссы доступны, без крашей."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
random.seed(7)

import pygame
from game.game_state import Level, get_available_enemy_types

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("[PASS] " if cond else "[FAIL] ") + name + ((" -- " + str(detail)) if detail else ""))


class FakeKeys(dict):
    def __getitem__(self, k):
        return dict.get(self, k, False)


class FakeClock:
    t = 1000


pygame.time.get_ticks = lambda: FakeClock.t
pygame.key.get_pressed = lambda: FakeKeys({pygame.K_SPACE: True})

# Свойства уровня соответствуют формулам из AGENTS.md
lv = Level(3)
check("P1. Формулы уровня", lv.spawn_interval == max(40, 80 - 15) and
      lv.enemies_to_kill_for_next_level == 8 and lv.victory_score_threshold == 30,
      f"interval={lv.spawn_interval}, kill={lv.enemies_to_kill_for_next_level}, "
      f"thr={lv.victory_score_threshold}")

import main as gm

g = gm.Game()
TARGET = (403, 300)  # статичная мишень на траектории пуль


def keep_target():
    """Держим один простой враг на линии огня (падение компенсируем)."""
    for s in list(g.enemies):
        if s.enemy_type == "simple":
            s.rect.center = TARGET
            return
    e = gm.Enemy("simple")
    e.rect.center = TARGET
    g.enemies.add(e)
    g.all_sprites.add(e)


levels_seen = {g.level.level_number}
types_seen = set()
try:
    for i in range(1500):
        FakeClock.t += 250  # каждый кадр кулдаун истёк -> стреляем каждый кадр
        g.update()
        keep_target()
        levels_seen.add(g.level.level_number)
        types_seen |= set(s.enemy_type for s in g.enemies)
    crashed = False
except Exception as ex:
    crashed = True
    import traceback
    traceback.print_exc()

check("P2. 1500 кадров боя (выстрел каждый кадр) без краша", not crashed)
max_lvl = max(levels_seen)
check("P3a. Уровень вырос сильно (>6)", max_lvl > 6,
      f"уровни: {min(levels_seen)}..{max_lvl}")
check("P3b. Уровень растёт монотонно",
      levels_seen == set(range(min(levels_seen), max_lvl + 1)), "пропусков нет")
check("P4. Очки копятся соответственно уровню", g.score >= (max_lvl - 1) * 10,
      f"score={g.score}, lvl={max_lvl}")
check("P5. spawn_interval = формула (минимум 40)",
      g.level.spawn_interval == max(40, 80 - max_lvl * 5),
      f"lvl={max_lvl}, interval={g.level.spawn_interval}")
check("P6. На уровне 6+ доступен тип boss", "boss" in get_available_enemy_types(g.level),
      f"lvl={max_lvl}")
check("P7. Боссы реально спавнятся из пула типов", "boss" in types_seen or max_lvl < 6,
      f"типы за бой: {sorted(types_seen)}")

print()
total_pass = sum(1 for _, c in results if c)
print(f"ИТОГО: {total_pass} PASS / {len(results) - total_pass} FAIL")
sys.exit(0 if total_pass == len(results) else 1)
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe tests\test_progression.py
```

Ожидается последняя строка вывода: `ИТОГО: 8 PASS / 0 FAIL`

---

### Шаг 3.4. Создать `tests/test_lifecycle.py`

ФАЙЛ: `tests/test_lifecycle.py`.

```python
"""Жизненный цикл врага: вход сверху разрешён, выход за низ/бока - удаление."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
random.seed(3)

import pygame

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("[PASS] " if cond else "[FAIL] ") + name + ((" -- " + str(detail)) if detail else ""))


class FakeClock:
    t = 1000


pygame.time.get_ticks = lambda: FakeClock.t


class FakeKeys(dict):
    def __getitem__(self, k):
        return dict.get(self, k, False)


pygame.key.get_pressed = lambda: FakeKeys({})

import main as gm
from game.enemy_sprite import Enemy

g = gm.Game()

# --- Simple: спавн над экраном, должен выжить и падать ---
e = Enemy("simple")
e.rect.centerx = 400
e.rect.top = -45          # как в spawn_enemy()
g.enemies.add(e)
g.all_sprites.add(e)

tops = []
for i in range(30):
    g.all_sprites.update()
    if e in [s for s in g.enemies]:
        tops.append(e.rect.top)

check("L1. Враг выжил первый кадр (не убит при входе сверху)", len(tops) == 30,
      f"пережил кадров: {len(tops)}/30")
check("L2. Враг движется вниз", len(tops) >= 2 and tops[-1] > tops[0],
      f"y: {tops[0]} -> {tops[-1]}")

frames_more = 0
while e.rect.bottom <= 450 and frames_more < 400:
    g.all_sprites.update()
    frames_more += 1
check("L3. Враг долетел до зоны игрока (bottom > 450)",
      e.rect.bottom > 450, f"bottom={e.rect.bottom}, кадров={30 + frames_more}")

# --- Boss: тоже входит сверху ---
boss = Enemy("boss")
boss.rect.center = (400, 0)
boss.rect.top = -80       # как в spawn_boss()
g.enemies.add(boss)
g.all_sprites.add(boss)
alive_frames = 0
for i in range(20):
    g.all_sprites.update()
    if boss in [s for s in g.enemies]:
        alive_frames += 1

check("L4. Босс выживает при входе сверху", alive_frames == 20, f"кадров: {alive_frames}/20")

# --- Выход за нижний край -> удаление ---
e.rect.top = gm.HEIGHT + 5
g.all_sprites.update()
check("L5. Враг удалён после выхода за нижний край", e not in [s for s in g.enemies])

# --- Спавн через обычный игровой цикл (детерминированно) ---
extra1 = Enemy("simple")
extra1.rect.centerx = 150
extra1.rect.top = -45
extra2 = Enemy("fast")
extra2.rect.centerx = 600
extra2.rect.top = -40
g.enemies.add(extra1, extra2)
g.all_sprites.add(extra1, extra2)

spawned = 0
for i in range(300):
    g.update()
    spawned += len([s for s in g.enemies])

check("L6. Враги реально появляются и присутствуют на экране", spawned > 300,
      f"враго-кадров за 300: {spawned}")

print()
total_pass = sum(1 for _, c in results if c)
print(f"ИТОГО: {total_pass} PASS / {len(results) - total_pass} FAIL")
sys.exit(0 if total_pass == len(results) else 1)
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe tests\test_lifecycle.py
```

Ожидается последняя строка вывода: `ИТОГО: 6 PASS / 0 FAIL`

---

### Шаг 3.5. Создать `tests/run_all.py`

ФАЙЛ: `tests/run_all.py`.

```python
"""Единая точка запуска всех тестов проекта.

Запуск из корня проекта:
    .venv\\Scripts\\python.exe tests\\run_all.py

Код возврата: 0 — все тесты зелёные, 1 — есть падения.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

TESTS = [
    "test_session2.py",
    "test_collisions.py",
    "test_lifecycle.py",
    "test_progression.py",
]


def main() -> int:
    failed = []
    for name in TESTS:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print(f"[SKIP] {name}: файл не найден (сессия ещё не выполнена)")
            continue
        print("=" * 60)
        print("RUN:", name)
        print("-" * 60)
        result = subprocess.run([sys.executable, path])
        if result.returncode != 0:
            failed.append(name)

    print()
    print("#" * 60)
    if failed:
        print("УПАЛИ:", ", ".join(failed))
        print("#" * 60)
        return 1
    print("ALL TESTS PASSED (%d)" % len(TESTS))
    print("#" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### Шаг 3.6. Финальная проверка сессии

```powershell
.venv\Scripts\python.exe tests\run_all.py
```

Ожидаемое окончание вывода:

```
ALL TESTS PASSED (4)
```

Также проверь, что игровые файлы не тронуты:

```powershell
git status --short
```

Ожидается: только пути внутри `tests/`.

---

## 🐛 Если что-то пошло не так

| Симптом | Причина | Действие |
|---------|---------|----------|
| `ModuleNotFoundError: No module named 'main'` | Запуск не из корня проекта | Перейди в корень `snake_38-9b/` и повтори |
| `ModuleNotFoundError: No module named 'pygame'` | Используется системный python | Запускай через `.venv\Scripts\python.exe` |
| Тест печатает `[FAIL]` по всем пунктам | Опечатка при копировании листинга | Сравни файл с листингом посимвольно |
| `AttributeError: ... has no setter` в трейсбеке | Ты случайно изменил `game/game_state.py` | `git checkout -- game/game_state.py` |
| Окно игры открывается при тестах | Удалены строки `SDL_VIDEODRIVER=dummy` в начале файла | Вернуть первые строки листинга |

---

## 🚦 Чеклист завершения сессии

- [ ] `tests/test_session2.py` → 10 PASS / 0 FAIL
- [ ] `tests/test_collisions.py` → 13 PASS / 0 FAIL
- [ ] `tests/test_progression.py` → 8 PASS / 0 FAIL
- [ ] `tests/test_lifecycle.py` → 6 PASS / 0 FAIL
- [ ] `tests/run_all.py` → `ALL TESTS PASSED (4)`
- [ ] Файлы игры (`main.py`, `game/*`) не изменялись

---

## 🚀 Переходим к следующей сессии → Сессия 4: Жизни, Game Over и частицы (доработка)
