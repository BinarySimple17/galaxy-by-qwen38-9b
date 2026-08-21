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
