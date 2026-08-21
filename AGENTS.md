# Galaxy Shooter — Instructions for agents

## Commands to run

```bash
python main.py
```

## Project structure

```
game/
  __init__.py       # Empty init file (Python package marker)
  config.py         # All constants: screen size, colors, speeds, spawn rates
  entities.py       # Entity base class + create_rect_from_surface utility
  player_sprite.py  # Player: movement, cooldown shooting
  bullet_sprite.py  # Bullet with bounce physics on enemy collision
  enemy_sprite.py   # Enemy types: simple/fast/boss with hp and bouncing bullets
  particles.py      # Particle effects (explosions)
  game_state.py     # Level progression logic
main.py             # Game class + main() entrypoint
requirements.txt    # pygame, colorsys
```

## Architecture notes

- **Bouncing bullets**: When a bullet hits an enemy with remaining HP, it bounces back toward the player. If it then hits the player, they take damage. This is handled in `main.py:Game.handle_collision_enemy_with_bullet`.
- **Enemy spawn**: Enemies spawn from above (y ∈ [-50, -40]) at random x positions. The spawn interval decreases with level and is capped by `MIN_SPAWN_INTERVAL`.
- **Leveling up**: Triggered when score reaches `level.victory_score_threshold`. The counter `enemies_killed_this_level` resets on each level-up. Available enemy types grow with level number.
- **Boss spawning**: Appears at level 6 (`LEVEL_BOSS_THRESHOLD`).
- **Player death handling**: When lives reach 0, the game transitions to Game Over state; pressing SPACE restarts from scratch (full reset).

## Conventions

- All game constants are defined in `config.py` as module-level variables.
- Entity classes extend `game.entities.Entity`.
- Collision resolution for bullets vs enemies uses `pygame.sprite.spritecollide(enemy, self.bullets, False)`.
