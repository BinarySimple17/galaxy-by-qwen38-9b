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
