from xp_system import XPSystem


class GameStats:
    """Track statistics for Alien Invasion.

    Some values reset every game (score, ships, wave). Others persist
    across games (high score, XP).
    """

    def __init__(self, ai_game):
        self.settings = ai_game.settings

        # High score is never reset.
        self.high_score = 0

        # Created before reset_stats(), which reads xp_system.level.
        self.xp_system = XPSystem()
        self.reset_stats()

    def reset_stats(self):
        """Reset the values that change within a single game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        # "level" is the wave counter shown on the scoreboard. It starts at the
        # player's XP level and goes up by one each time a fleet is cleared.
        self.level = self.xp_system.level
