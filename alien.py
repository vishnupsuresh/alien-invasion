from pathlib import Path

import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """A single alien in the fleet."""

    def __init__(self, ai_game):
        """Create the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Path(__file__) makes the image load work from any working directory.
        image_path = Path(__file__).parent / "images" / "alien.bmp"
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

        # Start near the top left. The fleet builder repositions each alien.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the exact horizontal position as a float, as in Ship.
        self.x = float(self.rect.x)

        # Health and XP reward scale with the player's current level.
        player_level = ai_game.stats.xp_system.level
        self.health = self.settings.base_alien_health * (
            self.settings.alien_health_scale ** (player_level - 1))
        self.xp_drop = self.settings.base_xp_drop * (
            self.settings.xp_scale ** (player_level - 1))

    def check_edges(self):
        """Return True if the alien is touching a screen edge."""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self):
        """Move the alien left or right."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x

    def take_damage(self, damage):
        """Reduce health. Return True if the alien is dead."""
        self.health -= damage
        return self.health <= 0
