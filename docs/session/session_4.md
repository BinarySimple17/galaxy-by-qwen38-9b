# Сессия 4: Жизни, Game Over и частицы 💥❤️ (v2 — доработка)

> **ВАЖНО:** Это ПЕРЕРАБОТАННАЯ сессия. Большая часть механик из старой версии
> **уже реализована и покрыта тестами**:
> - отскок пули от врага и урон игроку (`main.py`, метод `handle_collision_enemy_with_bullet`);
> - частицы взрыва при уничтожении врага (`spawn_particles`, проверяется тестом C7);
> - жизни `❤/💔` в UI (проверяются отрисовкой).
>
> Чего **не хватает**: флаг `game_over` никогда не устанавливается — при нуле
> жизней игра продолжает работать молча, без экрана поражения.
>
> Задача сессии: добавить завершение игры по жизням + экран GAME OVER.

---

## ⚠️ Правила для агента (обязательные)

1. Меняй только файлы, указанные в шагах: `main.py`, `tests/run_all.py`
   и новый файл `tests/test_gameover.py`.
2. Каждый шаг: найди точный якорь (раздел «НАЙДИ»), замени блоком из
   «ЗАМЕНИ НА». Ничего сверх указанного не меняй.
3. Отступы Python — 4 пробела на уровень. Копируй блоки целиком.
4. После каждого шага выполняй «ПРОВЕРКУ». Упало — верни файл назад
   (`git checkout -- main.py`) и повтори шаг заново.
5. Запрещено: менять константы, рефакторить методы, трогать `game/*`.
6. Все команды — из корня проекта в PowerShell.

---

## 📌 Текущее состояние

| Поведение | Где | Статус |
|-----------|-----|--------|
| Пуля отскакивает от врага | `handle_collision_enemy_with_bullet` | ✅ есть |
| Отскочившая пуля бьёт игрока (`lives -= 1`) | там же | ✅ есть |
| Взрыв частиц при убийстве врага | `spawn_particles` | ✅ есть |
| `game_over = True` при `lives <= 0` | нигде | ❌ **нет** |
| Экран GAME OVER | `draw()` | ❌ **нет** |

---

## 🎯 Цель сессии

1. При `lives <= 0` выставлять `self.game_over = True`.
2. `update()` уже останавливается при `game_over` (первая строка метода) —
   после шага 4.2 игра честно замирает.
3. В `draw()` появляется экран поражения с подсказкой про SPACE.

---

## ✅ Определение готовности (Definition of Done)

- [ ] `tests/test_gameover.py` → `ИТОГО: 5 PASS / 0 FAIL`
- [ ] `tests/run_all.py` → `ALL TESTS PASSED (5)`
- [ ] Изменены только `main.py`, `tests/run_all.py`, добавлен `tests/test_gameover.py`

---

## 🛠 Шаги

### Шаг 4.1. Крупный шрифт для экранов

ФАЙЛ: `main.py`.

НАЙДИ (метод `__init__`, начало класса `Game`):

```python
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
```

ЗАМЕНИ НА:

```python
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 72)
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe -c "import os; os.environ['SDL_VIDEODRIVER']='dummy'; import main; g=main.Game(); print('big_font OK' if hasattr(g,'big_font') else 'NO big_font')"
```

Ожидается вывод: `big_font OK`

---

### Шаг 4.2. Флаг game_over при нуле жизней

ФАЙЛ: `main.py`.

НАЙДИ (в методе `handle_collision_enemy_with_bullet`):

```python
        # Если пуля попала в игрока — наносим урон
        if pygame.sprite.collide_rect(bullet, self.player):
            self.lives -= 1
            bullet.kill()
            return
```

ЗАМЕНИ НА:

```python
        # Если пуля попала в игрока — наносим урон
        if pygame.sprite.collide_rect(bullet, self.player):
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            bullet.kill()
            return
```

ПРОВЕРКА (регрессия коллизий):

```powershell
.venv\Scripts\python.exe tests\test_collisions.py
```

Ожидается последняя строка: `ИТОГО: 13 PASS / 0 FAIL`

---

### Шаг 4.3. Экран GAME OVER

ФАЙЛ: `main.py`.

НАЙДИ (конец метода `draw()`):

```python
        # Жизни: ❤️ — живые, 💔 — потерянные
        hearts_alive = "❤" * self.lives
        hearts_broken = "💔" * max(0, 3 - self.lives)
        lives_text = self.small_font.render(f"Hearts: {hearts_alive}{hearts_broken}", True, COLORS["RED"])
        self.screen.blit(lives_text, (10, HEIGHT - 30))
```

ЗАМЕНИ НА:

```python
        # Жизни: ❤️ — живые, 💔 — потерянные
        hearts_alive = "❤" * self.lives
        hearts_broken = "💔" * max(0, 3 - self.lives)
        lives_text = self.small_font.render(f"Hearts: {hearts_alive}{hearts_broken}", True, COLORS["RED"])
        self.screen.blit(lives_text, (10, HEIGHT - 30))

        # Экран поражения
        if self.game_over:
            over = self.big_font.render("GAME OVER", True, COLORS["WHITE"])
            hint = self.small_font.render("SPACE — рестарт", True, COLORS["YELLOW"])
            self.screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
```

ПРОВЕРКА (отрисовка не падает):

```powershell
.venv\Scripts\python.exe -c "import os; os.environ['SDL_VIDEODRIVER']='dummy'; import main; g=main.Game(); g.game_over=True; g.draw(); print('draw OK')"
```

Ожидается вывод: `draw OK`

---

### Шаг 4.4. Тест завершения игры

СОЗДАЙ ФАЙЛ: `tests/test_gameover.py`.

```python
"""Тест: жизнь до нуля -> game_over=True, игровой цикл замирает."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
random.seed(4)

import pygame


class FakeClock:
    t = 1000


pygame.time.get_ticks = lambda: FakeClock.t


class FakeKeys(dict):
    def __getitem__(self, k):
        return dict.get(self, k, False)


results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("[PASS] " if cond else "[FAIL] ") + name + ((" -- " + str(detail)) if detail else ""))


import main as gm
from game.enemy_sprite import Enemy

g = gm.Game()

# Враг нависает над верхней кромкой игрока; пуля кладём в пересечение обоих.
px = g.player.rect.centerx          # ~400
py = g.player.rect.top              # ~515

enemy = Enemy("simple")
enemy.rect.center = (px, py - 10)   # низ врага перекрывает верх игрока
g.enemies.add(enemy)
g.all_sprites.add(enemy)

b = gm.Bullet(x=px - 20, y=py + 25)   # создаём как в стрельбе...
b.rect.center = (px, py - 5)          # ...и кладём точно в зону врага+игрока
g.bullets.add(b)
g.all_sprites.add(b)

g.lives = 1                            # одна жизнь до удара
g.handle_collisions()

check("G1. Жизнь списана до нуля", g.lives == 0, f"lives={g.lives}")
check("G2. game_over = True", g.game_over is True)
check("G3. Враг не пострадал (урон ушёл игроку)", enemy.hp == 1, f"hp={enemy.hp}")

# Игровой цикл должен замереть: пробел зажат, но новые пули не появляются
pygame.key.get_pressed = lambda: FakeKeys({pygame.K_SPACE: True})
for _ in range(5):
    FakeClock.t += 250
    g.update()
check("G4. update() заморожен при game_over (пуль нет)",
      len([s for s in g.bullets]) == 0,
      f"bullets={len([s for s in g.bullets])}")
check("G5. Очки не меняются после смерти", g.score == 0, f"score={g.score}")

print()
total_pass = sum(1 for _, c in results if c)
print(f"ИТОГО: {total_pass} PASS / {len(results) - total_pass} FAIL")
sys.exit(0 if total_pass == len(results) else 1)
```

ПРОВЕРКА:

```powershell
.venv\Scripts\python.exe tests\test_gameover.py
```

Ожидается последняя строка: `ИТОГО: 5 PASS / 0 FAIL`

---

### Шаг 4.5. Подключить тест к раннеру

ФАЙЛ: `tests/run_all.py`.

НАЙДИ:

```python
TESTS = [
    "test_session2.py",
    "test_collisions.py",
    "test_lifecycle.py",
    "test_progression.py",
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
]
```

---

### Шаг 4.6. Финальная проверка сессии

```powershell
.venv\Scripts\python.exe tests\run_all.py
```

Ожидаемое окончание вывода:

```
ALL TESTS PASSED (5)
```

Ручная проверка (опционально, если есть дисплей):

```powershell
.venv\Scripts\python.exe main.py
```

Подставься под отскочившие пули, пока сердца не закончатся → по центру
должно появиться `GAME OVER`, игра замирает, `SPACE` перезапускает.

---

## 🐛 Если что-то пошло не так

| Симптом | Причина | Действие |
|---------|---------|----------|
| G2 `[FAIL]`: `game_over` остался False | Шаг 4.2 не применён или ветка стоит не в том месте | Сверь блок с листингом шага 4.2 посимвольно |
| G3 `[FAIL]`: у врага hp=0 | Пуля легла мимо зоны игрока | Сверь координаты в листинге 4.4 (`py - 10`, `py - 5`) |
| G4 `[FAIL]`: пули продолжают появляться | `update()` больше не начинается с проверки флага | Верни первую строку `update()`: `if self.game_over or self.victory: return` |
| После 4.2 падает C-тест | Затронут другой блок обработчика | `git checkout -- main.py`, повтори шаги 4.1–4.3 |
| `NameError: big_font` | Пропущен шаг 4.1 | Выполни шаг 4.1 |

---

## 🚦 Чеклист завершения сессии

- [ ] `game_over` выставляется ровно при `lives <= 0`
- [ ] Экран GAME OVER рисуется по центру, подсказка про SPACE видна
- [ ] `tests/test_gameover.py` → 5 PASS / 0 FAIL
- [ ] `tests/run_all.py` → `ALL TESTS PASSED (5)`
- [ ] Ни один файл в `game/` не изменён

---

## 🚀 Переходим к следующей сессии → Сессия 5: Прогрессия и боссы (доработка)
