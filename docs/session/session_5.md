# Сессия 5: Прогрессия и боссы ⬆️👹 (v2 — доработка)

> **ВАЖНО:** Это ПЕРЕРАБОТАННАЯ сессия. Вся механика прогрессии **уже
> реализована и покрыта тестами** `tests/test_progression.py` (P1–P7):
> - повышение уровня по порогу очков (`handle_level_up`);
> - интервал спавна = `max(40, 80 - level*5)` (свойство `Level.spawn_interval`);
> - босс спавнится при переходе на уровень ≥ `LEVEL_BOSS_THRESHOLD`;
> - тип `"boss"` гарантированно есть в пуле типов с уровня 6.
>
> Логику в этой сессии **не меняем**. Добавляем только:
> 1. HP-бар босса в интерфейсе;
> 2. отдельные юнит-тесты боссовой логики.

---

## ⚠️ Правила для агента (обязательные)

1. Меняй только файлы, указанные в шагах: `main.py`, `tests/run_all.py`
   и новый файл `tests/test_boss.py`.
2. Файлы `game/game_state.py` и `game/enemy_sprite.py` **не трогать** —
   их логика уже готова и проверена.
3. Каждый шаг: «НАЙДИ» → точный якорь, «ЗАМЕНИ НА» → блок целиком,
   затем «ПРОВЕРКА». Упало — `git checkout -- main.py` и шаг заново.
4. Отступы — 4 пробела на уровень. Копируй блоки без изменений.
5. Все команды — из корня проекта в PowerShell через `.venv\Scripts\python.exe`.

---

## 📌 Текущее состояние

| Элемент | Где живёт | Статус |
|---------|-----------|--------|
| Формулы уровня | `game/game_state.py::Level` (свойства) | ✅ тест P1 |
| Повышение уровня по очкам | `main.py::handle_level_up` | ✅ тест P2–P4 |
| Спавн босса при переходе порога | `main.py::handle_level_up` | ✅ тест P7 |
| Пул типов врагов по уровню | `game/game_state.py::get_available_enemy_types` | ✅ тест P6 |
| HP-бар босса в UI | `draw()` | ❌ **нет** |
| Юнит-тесты боссовой логики | `tests/` | ❌ **нет** |

---

## ✅ Определение готовности (Definition of Done)

- [ ] `tests/test_boss.py` → `ИТОГО: 11 PASS / 0 FAIL`
- [ ] `tests/run_all.py` → `ALL TESTS PASSED (6)`
- [ ] Изменены только `main.py` (блок HP-бара), `tests/run_all.py`, добавлен `tests/test_boss.py`

---

## 🛠 Шаги

### Шаг 5.1. HP-бар босса в draw()

ФАЙЛ: `main.py`.

НАЙДИ (конец метода `draw()`, две строки вывода жизней):

```python
        lives_text = self.small_font.render(f"Hearts: {hearts_alive}{hearts_broken}", True, COLORS["RED"])
        self.screen.blit(lives_text, (10, HEIGHT - 30))
```

ЗАМЕНИ НА:

```python
        lives_text = self.small_font.render(f"Hearts: {hearts_alive}{hearts_broken}", True, COLORS["RED"])
        self.screen.blit(lives_text, (10, HEIGHT - 30))

        # HP-бар босса (правый нижний угол)
        bosses_alive = [e for e in self.enemies if e.enemy_type == "boss" and e.hp > 0]
        if bosses_alive:
            boss = bosses_alive[0]
            bar_w = int((boss.hp / boss.max_hp) * 180)
            pygame.draw.rect(self.screen, COLORS["RED"],
                             (WIDTH - 220, HEIGHT - 28, 184, 12), 1)
            pygame.draw.rect(self.screen, COLORS["GREEN"],
                             (WIDTH - 218, HEIGHT - 26, max(0, bar_w), 8))
            label = self.small_font.render(
                f"BOSS {boss.hp}/{boss.max_hp}", True, COLORS["WHITE"])
            self.screen.blit(label, (WIDTH - 220, HEIGHT - 50))
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe -c "import os; os.environ['SDL_VIDEODRIVER']='dummy'; import main; g=main.Game(); g.draw(); print('draw OK')"
```

Ожидается вывод: `draw OK`

---

### Шаг 5.2. Юнит-тесты боссов и прогрессии

СОЗДАЙ ФАЙЛ: `tests/test_boss.py`.

```python
"""Юнит-тесты прогрессии и боссов: пулы типов, формулы, спавн, HP-бар."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
random.seed(5)

import pygame


class FakeKeys(dict):
    def __getitem__(self, k):
        return dict.get(self, k, False)


pygame.time.get_ticks = lambda: 1000
pygame.key.get_pressed = lambda: FakeKeys({})

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("[PASS] " if cond else "[FAIL] ") + name + ((" -- " + str(detail)) if detail else ""))


from game.config import LEVEL_BOSS_THRESHOLD, WIDTH, MIN_SPAWN_INTERVAL
from game.game_state import Level, increase_level, get_available_enemy_types
from game.enemy_sprite import Enemy, spawn_boss
import main as gm

# --- Пулы типов ---
p1 = get_available_enemy_types(Level(1))
p2 = get_available_enemy_types(Level(2))
p3 = get_available_enemy_types(Level(3))
p6 = get_available_enemy_types(Level(6))
p9 = get_available_enemy_types(Level(9))

check("B1. Уровень 1: только simple", p1 == ["simple"], f"{p1}")
check("B2. Уровень 2: только simple", p2 == ["simple"], f"{p2}")
check("B3. Уровень 3: fast доступен, boss ещё нет",
      "fast" in p3 and "boss" not in p3, f"{p3}")
check("B4. Уровни 6 и 9: boss всегда в пуле",
      "boss" in p6 and "boss" in p9,
      f"{sorted(set(p6))} / {sorted(set(p9))}")

all_valid = all(set(get_available_enemy_types(Level(n))) <= {"simple", "fast", "boss"}
                for n in range(1, 13))
check("B5. В пулах нет неизвестных типов", all_valid)


# --- Формулы Level ---
lv = Level(1)
increase_level(lv)
check("B6a. increase_level: номер +1", lv.level_number == 2, f"lvl={lv.level_number}")
check("B6b. increase_level: свойства пересчитались",
      lv.spawn_interval == max(MIN_SPAWN_INTERVAL, 80 - lv.level_number * 5) and
      lv.enemies_to_kill_for_next_level == 6 and lv.victory_score_threshold == 20,
      f"int={lv.spawn_interval}, kill={lv.enemies_to_kill_for_next_level}, "
      f"thr={lv.victory_score_threshold}")
check("B7. Интервал упирается в минимум",
      Level(20).spawn_interval == MIN_SPAWN_INTERVAL,
      f"int={Level(20).spawn_interval}")

# --- Босс как сущность ---
boss = Enemy("boss")
check("B8. Характеристики босса",
      boss.max_hp == 10 and boss.score_value == 100 and boss.rect.width == 76,
      f"hp={boss.max_hp}, pts={boss.score_value}, w={boss.rect.width}")

sb = spawn_boss()
check("B9. spawn_boss геометрия",
      sb.rect.top < 0 and 0 <= sb.rect.centerx <= WIDTH,
      f"top={sb.rect.top}, cx={sb.rect.centerx}")

# --- Спавн босса при переходе порога уровня 6 ---
g = gm.Game()
g.level = Level(LEVEL_BOSS_THRESHOLD - 1)     # уровень 5
g.score = g.level.victory_score_threshold     # мгновенно достигнут порог
g.handle_level_up()
bosses_now = sum(1 for e in g.enemies if e.enemy_type == "boss")
check("B10. Переход 5->6 приводит босса",
      g.level.level_number == 6 and bosses_now >= 1,
      f"lvl={g.level.level_number}, боссов={bosses_now}")

# --- Отрисовка с живым боссом не падает (HP-бар) ---
try:
    g.draw()
    check("B11. draw() с боссом и HP-баром без ошибок", True)
except Exception as ex:
    check("B11. draw() с боссом и HP-баром без ошибок", False, repr(ex))

print()
total_pass = sum(1 for _, c in results if c)
print(f"ИТОГО: {total_pass} PASS / {len(results) - total_pass} FAIL")
sys.exit(0 if total_pass == len(results) else 1)
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe tests\test_boss.py
```

Ожидается последняя строка: `ИТОГО: 11 PASS / 0 FAIL`

---

### Шаг 5.3. Подключить тест к раннеру

ФАЙЛ: `tests/run_all.py`.

НАЙДИ:

```python
TESTS = [
    "test_session2.py",
    "test_collisions.py",
    "test_lifecycle.py",
    "test_progression.py",
    "test_gameover.py",
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
]
```

---

### Шаг 5.4. Финальная проверка сессии

```powershell
.venv\Scripts\python.exe tests\run_all.py
```

Ожидаемое окончание вывода:

```
ALL TESTS PASSED (6)
```

Ручная проверка (опционально): запусти игру, прокачайся до 6 уровня —
справа внизу у босса должна появиться зелёная полоска здоровья `BOSS 10/10`,
которая уменьшается от попаданий.

---

## 🐛 Если что-то пошло не так

| Симптом | Причина | Действие |
|---------|---------|----------|
| B10 `[FAIL]`: боссов=0 | Затронут `handle_level_up` или `spawn_boss` | Сверь `main.py::handle_level_up` с состоянием до правки; ничего в нём менять этой сессией не нужно |
| B10 `[FAIL]`: lvl != 6 | Использован литерал вместо `LEVEL_BOSS_THRESHOLD` | Импортируй константу из `game.config` как в листинге |
| B11 `[FAIL]` c `NameError`/`AttributeError` | Сломан блок HP-бара (отступы, имя `max_hp`) | Сверь блок шага 5.1 посимвольно; атрибут называется `max_hp` |
| Полоса не видна в игре | Босс ещё мёртв или его нет на экране | Бар рисуется только при живом боссе (`hp > 0`) |
| Любой C/P/G-тест упал после 5.1 | Задеты соседние строки draw() | `git checkout -- main.py`, повтори 5.1 |

---

## 🚦 Чеклист завершения сессии

- [ ] HP-бар босса рисуется в правом нижнем углу, ширина пропорциональна `hp/max_hp`
- [ ] `tests/test_boss.py` → 11 PASS / 0 FAIL
- [ ] `tests/run_all.py` → `ALL TESTS PASSED (6)`
- [ ] Файлы `game/*` не изменялись

---

## 🚀 Переходим к следующей сессии → Сессия 6: Победа, рестарт и финальный UI
