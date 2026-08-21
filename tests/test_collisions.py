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
