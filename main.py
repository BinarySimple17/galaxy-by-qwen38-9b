"""main.py — Точка входа в игру."""

import pygame
import random
from typing import Optional, List

# --- Импорты внутренних модулей ---
from game.config import (
    WIDTH, HEIGHT, FPS, COLORS, PLAYER_SPEED,
    PLAYER_COOLDOWN_MS, ENEMY_SIMPLE_SIZE, ENEMY_FAST_SIZE,
    ENEMY_BOSS_SIZE, ENEMY_SIMPLE_SPEED, ENEMY_FAST_SPEED,
    ENEMY_BOSS_SPEED, STARTING_SPAWN_INTERVAL, MIN_SPAWN_INTERVAL,
    LEVEL_3_THRESHOLD, LEVEL_BOSS_THRESHOLD, LIVES_PER_LEVEL_BASE,
)
from game.entities import Entity, create_rect_from_surface
from game.player_sprite import Player
from game.bullet_sprite import Bullet
from game.enemy_sprite import Enemy, spawn_enemy, spawn_boss
from game.particles import Particle, create_explosion
from game.game_state import Level, increase_level, get_available_enemy_types


# ==================== ОСНОВНОЙ КЛАСС ИГРЫ ====================

class Game:
    """Основной класс игры — игровой цикл и логика."""

    def __init__(self) -> None:
        pygame.init()
        SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Galaxy Shooter")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.screen: pygame.Surface = SCREEN

        # Группы спрайтов
        self.all_sprites: List[pygame.sprite.Sprite] = []
        self.bullets: List[Bullet] = []
        self.enemies: List["Enemy"] = []
        self.particles: List[Particle] = []

        # Игрок
        self.player = Player()
        self.all_sprites.append(self.player)

        # Состояние игры
        self.score: int = 0
        self.level = Level(level_number=1)
        self.lives: int = 3
        self.game_over: bool = False
        self.victory: bool = False

        # Таймер спавна врагов
        self.enemy_spawn_timer: int = 0
        self.enemy_spawn_interval: int = STARTING_SPAWN_INTERVAL

        # Трекер для повышения уровня
        self.enemies_killed_this_level: int = 0

    def spawn_enemy(self) -> None:
        """Спавнить нового врага сверху."""
        available_types = get_available_enemy_types(self.level)
        if not available_types:
            available_types = ["simple"]

        enemy_type = random.choice(available_types[:min(self.level.level_number % 3 + 1, len(available_types))])
        x = random.randint(20, WIDTH - 20)
        y = random.randint(-50, -40)  # враги спавнятся сверху (y от -50 до -40 пикселей выше верха экрана)

        enemy = spawn_enemy(x=x, y=y, enemy_type=enemy_type)
        self.enemies.append(enemy)
        self.all_sprites.append(enemy)

    def spawn_boss(self) -> None:
        """Спавнить босса в центре сверху."""
        boss = spawn_boss()
        self.enemies.append(boss)
        self.all_sprites.append(boss)

    def spawn_particles(self, x: float, y: float) -> None:
        """Создать взрыв частиц."""
        for _ in range(random.randint(12, 18)):
            particle = Particle(x, y)
            self.particles.append(particle)
            self.all_sprites.append(particle)

    def handle_collision_enemy_with_bullet(self, enemy: "Enemy", bullet: Bullet) -> None:
        """Обработать коллизию врага с пулей."""
        if enemy.hp <= 0:
            return

        # Пуля отскакивает — враг стреляет обратно в игрока
        bounce_direction = bullet.bounce()
        bullet.velocity = bounce_direction

        # Если пуль попала в игрока — наносим урон
        if pygame.sprite.collide_rect(bullet, self.player):
            self.lives -= 1
            bullet.kill()
            return

        # Если пуля не попала никуда — удаляем её
        bullet.kill()

    def handle_collisions(self) -> None:
        """Обработать все коллизии между пулями и врагами."""
        for enemy in list(self.enemies):  # перебираем копию списка
            if enemy.hp <= 0:
                continue

            hits = pygame.sprite.spritecollide(enemy, self.bullets, False)
            for bullet in hits:
                self.handle_collision_enemy_with_bullet(enemy, bullet)

    def handle_level_up(self) -> None:
        """Проверить повышение уровня."""
        if (self.level.victory_score_threshold > 0 and
                self.score >= self.level.victory_score_threshold):
            # Уровень повышен — сбрасываем счётчик уничтоженных врагов
            self.enemies_killed_this_level = 0
            increase_level(self.level)

    def reset(self) -> None:
        """Сброс игры."""
        self.score = 0
        self.lives = 3
        self.level = Level(level_number=1)
        self.game_over = False
        self.victory = False
        self.all_sprites.clear()
        self.bullets.clear()
        self.enemies.clear()
        self.particles.clear()
        self.player.rect.center = (WIDTH // 2, HEIGHT - 60)

    def draw(self) -> None:
        """Отрисовка кадра."""
        self.screen.fill(COLORS["BLACK"])

        # Игрок с эффектом мигания
        if pygame.time.get_ticks() % 300 < 150:
            self.player.image.set_alpha(200)
        else:
            self.player.image.set_alpha(255)

        self.screen.blit(self.player.image, self.player.rect)

        # Пули
        for bullet in self.bullets:
            self.screen.blit(bullet.image, bullet.rect)

        # Враги (не уничтоженные)
        for enemy in self.enemies:
            if enemy.hp <= 0:
                continue
            self.screen.blit(enemy.image, enemy.rect)

        # Частицы (над всеми другими объектами)
        for particle in self.particles:
            self.screen.blit(particle.image, particle.rect)

        # UI
        title = self.font.render("Galaxy Shooter", True, COLORS["WHITE"])
        self.screen.blit(title, (10, 10))

        score_text = self.small_font.render(f"Score: {self.score}", True, COLORS["YELLOW"])
        self.screen.blit(score_text, (10, 50))

        level_info = f"Lvl {self.level.level_number} | " \
                     f"{self.enemies_killed_this_level}/{self.level.enemies_to_kill_for_next_level}"
        level_text = self.small_font.render(level_info, True, COLORS["WHITE"])
        self.screen.blit(level_text, (WIDTH // 2 - 160, 10))

        # Жизни: ❤️ — живые, 💔 — потерянные
        hearts_alive = "❤" * self.lives
        hearts_broken = "💔" * max(0, 3 - self.lives)
        lives_text = self.small_font.render(f"Hearts: {hearts_alive}{hearts_broken}", True, COLORS["RED"])
        self.screen.blit(lives_text, (10, HEIGHT - 30))

    def update(self) -> None:
        """Обновить состояние игры за один кадр."""
        if self.game_over or self.victory:
            return

        # Обновление игрока
        self.player.update()

        # Стрельба
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            if self.player.shoot():
                bullet = Bullet(
                    x=self.player.rect.centerx + 20,
                    y=self.player.rect.top - 15
                )
                self.bullets.append(bullet)
                self.all_sprites.append(bullet)

        # Удаление пуль за экраном
        for bullet in list(self.bullets):
            if bullet.is_offscreen:
                bullet.kill()

        # Коллизии
        self.handle_collisions()

        # Обновление всех живых сущностей
        for entity in list(self.all_sprites):
            entity.update()

        # Спавн врагов по таймеру
        if random.random() < 1.0 / max(MIN_SPAWN_INTERVAL, self.level.spawn_interval):
            self.spawn_enemy()

        # Проверка повышения уровня
        self.handle_level_up()

    def run(self) -> None:
        """Основной игровой цикл."""
        running = True

        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                   (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                    running = False
                # Рестарт после Game Over / Victory
                elif self.game_over or self.victory:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.reset()

            # Обновление игры
            self.update()

            # Отрисовка
            self.draw()
            pygame.display.flip()

        pygame.quit()


# ==================== ТОЧКА ВХОДА ====================

def main() -> None:
    """Точка входа в игру."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
