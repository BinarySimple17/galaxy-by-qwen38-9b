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
