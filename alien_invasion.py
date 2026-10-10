import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from xp_system import XPSystem


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game and create its resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Stats must exist before the scoreboard, ship, and aliens, since they read from it.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # game_active: a game is running. game_over: the player lost and can replay.
        # Both are False on the first screen, which shows only Play.
        self.game_active = False
        self.game_over = False

        # Play starts a new session with XP reset. Replay starts a new game and keeps XP.
        self.play_button = Button(self, "Play")
        self.replay_button = Button(self, "Replay", y_offset=70)

    def run_game(self):
        """Run the main loop: handle input, update state, draw, and cap the frame rate."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Handle keyboard and mouse input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._check_buttons(pygame.mouse.get_pos())

    def _check_buttons(self, mouse_pos):
        """Start a game when Play or Replay is clicked."""
        if self.game_active:
            return

        if self.play_button.rect.collidepoint(mouse_pos):
            self._start_new_game(reset_xp=True)
        elif self.game_over and self.replay_button.rect.collidepoint(mouse_pos):
            self._start_new_game(reset_xp=False)

    def _check_keydown_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Fire a bullet if the on-screen limit allows it."""
        if self.game_active and len(self.bullets) < self.settings.bullets_allowed:
            self.bullets.add(Bullet(self))

    def _update_bullets(self):
        """Move bullets, remove the ones that left the screen, and check for hits."""
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Apply bullet damage. Each bullet is used up on the first alien it hits."""
        # dokill1=True removes each bullet that hits. Aliens stay (dokill2=False)
        # so they can take more than one hit before dying.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, False)

        for hit_aliens in collisions.values():
            for alien in hit_aliens:
                if alien.take_damage(self.ship.damage):
                    self._on_alien_killed(alien)

        self.sb.prep_score()
        self.sb.check_high_score()

        # Clearing the fleet starts the next wave: new fleet, faster speeds, higher wave number.
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _on_alien_killed(self, alien):
        """Award score and XP for a killed alien."""
        self.aliens.remove(alien)
        self.stats.score += self.settings.alien_points
        self.stats.xp_system.add_xp(alien.xp_drop)

    def _ship_hit(self):
        """Lose a life, or end the game if none are left."""
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            self.bullets.empty()
            self.aliens.empty()

            self._create_fleet()
            self.ship.center_ship()

            # Pause so the player can see what happened before the fleet resumes.
            sleep(0.5)
        else:
            self.game_active = False
            self.game_over = True
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """Move the fleet and check for collisions with the ship or the bottom edge."""
        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Treat an alien reaching the bottom as a ship hit."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break

    def _create_fleet(self):
        """Fill the top of the screen with a grid of aliens."""
        # Build one alien to measure the spacing. Spacing is one alien width horizontally
        # and one alien height vertically between each pair.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Row finished: return to the left edge and move down one row.
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Place one alien at the given position."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Reverse the fleet if any alien reaches a screen edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the whole fleet one step and reverse its direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Draw the frame and show it."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        self.sb.show_score()

        # Draw menu buttons only when no game is running.
        if not self.game_active:
            self.play_button.draw_button()
            if self.game_over:
                self.replay_button.draw_button()

        pygame.display.flip()

    def _start_new_game(self, reset_xp=True):
        """Reset the game state and begin a new game."""
        self.settings.initialize_dynamic_settings()

        # Replacing the XP system resets level, and therefore damage, in one step.
        if reset_xp:
            self.stats.xp_system = XPSystem()

        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        self.game_active = True
        self.game_over = False
        self.bullets.empty()
        self.aliens.empty()
        self._create_fleet()
        self.ship.center_ship()
        pygame.mouse.set_visible(False)


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
