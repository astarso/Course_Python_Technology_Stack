"""
Helicopter University Game - Enhanced version with:
- Level system and difficulty progression
- High score saving (top 5)
- Power-ups (health kits, shields, bonus points)
- Visual effects (particles, blinking on damage)
- Improved UI/UX (menu, high scores screen)
"""

import pygame
import random
import sys
import json
import os
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
from pathlib import Path
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================
@dataclass
class Config:
    """Game configuration constants."""
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600
    CELL_SIZE: int = 50
    FPS: int = 60
    
    # Game objects
    NUM_RIVERS: int = 5
    NUM_TREES: int = 10
    MAX_POWERUPS: int = 3
    
    # Colors
    COLOR_GRASS: Tuple[int, int, int] = (0, 255, 0)
    COLOR_WATER: Tuple[int, int, int] = (0, 0, 255)
    COLOR_TEXT: Tuple[int, int, int] = (0, 0, 0)
    COLOR_BACKGROUND: Tuple[int, int, int] = (255, 255, 255)
    COLOR_GOLD: Tuple[int, int, int] = (255, 215, 0)
    COLOR_RED: Tuple[int, int, int] = (255, 0, 0)
    COLOR_BLUE: Tuple[int, int, int] = (0, 100, 255)
    COLOR_GREEN: Tuple[int, int, int] = (0, 200, 0)
    COLOR_SHIELD: Tuple[int, int, int] = (100, 100, 255)
    
    # Symbols
    SYMBOL_HELICOPTER: str = "🚁"
    SYMBOL_TREE: str = "🌳"
    SYMBOL_RIVER: str = "🌊"
    SYMBOL_GRASS: str = "🟩"
    SYMBOL_HEART: str = "❤️"
    SYMBOL_SHIELD: str = "🛡️"
    SYMBOL_MEDKIT: str = "💊"
    SYMBOL_BONUS: str = "⭐"
    SYMBOL_COIN: str = "🪙"
    
    # Fonts
    FONT_NAME: str = "Segoe UI Emoji"
    FONT_SIZE: int = 30
    
    # Game settings
    INITIAL_LIVES: int = 3
    SCORES_FILE: str = "highscores.json"
    TOP_SCORES_COUNT: int = 5
    
    # Level progression
    SCORE_PER_LEVEL: int = 500
    BASE_MOVE_COST: int = 10
    COLLISION_PENALTY: int = 50
    
    # Visual effects
    BLINK_DURATION: int = 500  # milliseconds
    PARTICLE_LIFETIME: int = 30  # frames


# =============================================================================
# GAME OBJECTS
# =============================================================================
class GameObject:
    """Base class for game objects."""
    
    def __init__(self, x: int, y: int, symbol: str):
        self.x = x
        self.y = y
        self.symbol = symbol
    
    @property
    def position(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def __eq__(self, other):
        if isinstance(other, GameObject):
            return self.position == other.position
        return False
    
    def __hash__(self):
        return hash(self.position)


class Particle:
    """Particle for visual effects."""
    
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], 
                 lifetime: int = Config.PARTICLE_LIFETIME):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
    
    def update(self) -> bool:
        """Update particle. Returns False if particle is dead."""
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen: pygame.Surface, cell_size: int, font: pygame.font.Font) -> None:
        """Draw the particle."""
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = max(5, int(cell_size * (self.lifetime / self.max_lifetime)))
        rect = pygame.Rect(
            self.x * cell_size + (cell_size - size) // 2,
            self.y * cell_size + (cell_size - size) // 2,
            size, size
        )
        pygame.draw.rect(screen, self.color, rect)


class Helicopter(GameObject):
    """Helicopter player object."""
    
    def __init__(self, x: int, y: int):
        super().__init__(x, y, Config.SYMBOL_HELICOPTER)
        self.lives = Config.INITIAL_LIVES
        self.score = 0
        self.level = 1
        self.has_shield = False
        self.shield_duration = 0
        self.blink_timer = 0
        self.is_blinking = False
        self.invincible_timer = 0
    
    def move(self, dx: int, dy: int, max_x: int, max_y: int) -> bool:
        """Move helicopter by delta. Returns True if move is valid."""
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 0 <= new_x < max_x and 0 <= new_y < max_y:
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def lose_life(self) -> bool:
        """Decrease lives by one. Returns True if shield absorbed damage."""
        if self.has_shield and self.shield_duration > 0:
            self.has_shield = False
            self.shield_duration = 0
            self.blink_timer = Config.BLINK_DURATION
            self.is_blinking = True
            return True  # Shield absorbed damage
        
        self.lives -= 1
        self.blink_timer = Config.BLINK_DURATION
        self.is_blinking = True
        self.invincible_timer = 60  # 1 second at 60 FPS
        return False
    
    def activate_shield(self, duration: int = 300) -> None:
        """Activate shield for specified duration (frames)."""
        self.has_shield = True
        self.shield_duration = duration
    
    def add_bonus_points(self, points: int) -> None:
        """Add bonus points to score."""
        self.score += points
    
    def heal(self) -> None:
        """Restore one life."""
        if self.lives < Config.INITIAL_LIVES:
            self.lives += 1
    
    def level_up(self) -> None:
        """Increase level."""
        self.level += 1
    
    def update_effects(self) -> None:
        """Update visual effects timers."""
        if self.is_blinking:
            self.blink_timer -= 16  # ~60 FPS
            if self.blink_timer <= 0:
                self.is_blinking = False
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        if self.has_shield:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.has_shield = False
    
    @property
    def is_alive(self) -> bool:
        return self.lives > 0
    
    @property
    def should_draw(self) -> bool:
        """Check if helicopter should be drawn (for blinking effect)."""
        if not self.is_blinking:
            return True
        # Blink every 100ms
        return (pygame.time.get_ticks() // 100) % 2 == 0
    
    @property
    def is_invincible(self) -> bool:
        return self.invincible_timer > 0


class Obstacle(GameObject):
    """Obstacle object (river or tree)."""
    
    def __init__(self, x: int, y: int, symbol: str, obstacle_type: str):
        super().__init__(x, y, symbol)
        self.obstacle_type = obstacle_type


class PowerUpType(Enum):
    """Types of power-ups."""
    MEDKIT = "medkit"
    SHIELD = "shield"
    BONUS_POINTS = "bonus_points"
    INVINCIBILITY = "invincibility"


class PowerUp(GameObject):
    """Power-up object."""
    
    TYPE_SYMBOLS = {
        PowerUpType.MEDKIT: Config.SYMBOL_MEDKIT,
        PowerUpType.SHIELD: Config.SYMBOL_SHIELD,
        PowerUpType.BONUS_POINTS: Config.SYMBOL_BONUS,
        PowerUpType.INVINCIBILITY: Config.SYMBOL_COIN,
    }
    
    TYPE_COLORS = {
        PowerUpType.MEDKIT: Config.COLOR_GREEN,
        PowerUpType.SHIELD: Config.COLOR_BLUE,
        PowerUpType.BONUS_POINTS: Config.COLOR_GOLD,
        PowerUpType.INVINCIBILITY: Config.COLOR_GOLD,
    }
    
    def __init__(self, x: int, y: int, powerup_type: PowerUpType):
        symbol = self.TYPE_SYMBOLS[powerup_type]
        super().__init__(x, y, symbol)
        self.powerup_type = powerup_type
        self.color = self.TYPE_COLORS[powerup_type]
        self.float_offset = 0
    
    def update(self) -> None:
        """Update animation."""
        self.float_offset = (self.float_offset + 0.1) % (2 * 3.14159)
    
    def get_display_y(self) -> float:
        """Get Y position with floating animation."""
        import math
        return self.y + math.sin(self.float_offset) * 0.2


# =============================================================================
# GAME ENGINE
# =============================================================================
class GameState(Enum):
    """Game state enumeration."""
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"
    HIGH_SCORES = "high_scores"


class HighScoreManager:
    """Manages high scores persistence."""
    
    def __init__(self, filename: str = Config.SCORES_FILE):
        self.filename = filename
        self.scores: List[Dict] = []
        self.load()
    
    def load(self) -> None:
        """Load scores from file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.scores = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load high scores: {e}")
            self.scores = []
    
    def save(self) -> None:
        """Save scores to file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save high scores: {e}")
    
    def add_score(self, score: int, level: int) -> None:
        """Add a new score and maintain top N."""
        entry = {
            "score": score,
            "level": level,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.scores.append(entry)
        # Sort by score descending
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        # Keep only top N
        self.scores = self.scores[:Config.TOP_SCORES_COUNT]
        self.save()
    
    def get_top_scores(self) -> List[Dict]:
        """Get top scores."""
        return self.scores
    
    def is_high_score(self, score: int) -> bool:
        """Check if score qualifies for top list."""
        if len(self.scores) < Config.TOP_SCORES_COUNT:
            return True
        return score > self.scores[-1]["score"]


class Game:
    """Main game class that manages game logic and rendering."""
    
    def __init__(self):
        """Initialize the game."""
        try:
            pygame.init()
            pygame.font.init()
        except pygame.error as e:
            print(f"Error initializing Pygame: {e}")
            sys.exit(1)
        
        self.config = Config()
        self.screen = pygame.display.set_mode(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Helicopter University Game")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts once
        self.font = pygame.font.SysFont(
            self.config.FONT_NAME, 
            self.config.FONT_SIZE
        )
        self.large_font = pygame.font.SysFont(
            self.config.FONT_NAME, 
            self.config.FONT_SIZE * 2
        )
        self.small_font = pygame.font.SysFont(
            self.config.FONT_NAME, 
            self.config.FONT_SIZE // 2
        )
        
        # Game state
        self.state = GameState.MENU
        self.helicopter: Optional[Helicopter] = None
        self.rivers: List[Obstacle] = []
        self.trees: List[Obstacle] = []
        self.powerups: List[PowerUp] = []
        self.particles: List[Particle] = []
        
        # High scores
        self.high_score_manager = HighScoreManager()
        
        # Calculate grid dimensions
        self.grid_width = self.config.WINDOW_WIDTH // self.config.CELL_SIZE
        self.grid_height = self.config.WINDOW_HEIGHT // self.config.CELL_SIZE
        
        # Menu selection
        self.menu_selection = 0
        self.menu_options = ["Start Game", "High Scores", "Quit"]
    
    def generate_obstacles(self, num_rivers: int, num_trees: int) -> None:
        """Generate random obstacles on the grid."""
        positions = set()
        
        # Generate rivers
        for _ in range(num_rivers):
            while True:
                x = random.randint(0, self.grid_width - 1)
                y = random.randint(0, self.grid_height - 1)
                if (x, y) not in positions:
                    positions.add((x, y))
                    self.rivers.append(
                        Obstacle(x, y, self.config.SYMBOL_RIVER, "river")
                    )
                    break
        
        # Generate trees
        for _ in range(num_trees):
            while True:
                x = random.randint(0, self.grid_width - 1)
                y = random.randint(0, self.grid_height - 1)
                if (x, y) not in positions:
                    positions.add((x, y))
                    self.trees.append(
                        Obstacle(x, y, self.config.SYMBOL_TREE, "tree")
                    )
                    break
    
    def spawn_powerup(self) -> None:
        """Spawn a random power-up at a free position."""
        if len(self.powerups) >= self.config.MAX_POWERUPS:
            return
        
        positions = {obs.position for obs in self.rivers + self.trees}
        if self.helicopter:
            positions.add(self.helicopter.position)
        positions.update(p.position for p in self.powerups)
        
        # Find free position
        attempts = 0
        while attempts < 50:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in positions:
                # Random power-up type
                powerup_type = random.choice(list(PowerUpType))
                self.powerups.append(PowerUp(x, y, powerup_type))
                break
            attempts += 1
    
    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.helicopter = Helicopter(
            self.grid_width // 2,
            self.grid_height // 2
        )
        self.rivers = []
        self.trees = []
        self.powerups = []
        self.particles = []
        self.generate_obstacles(
            self.config.NUM_RIVERS,
            self.config.NUM_TREES
        )
        self.state = GameState.PLAYING
        
        # Ensure helicopter doesn't start on an obstacle
        while (self.helicopter.x, self.helicopter.y) in [
            obs.position for obs in self.rivers + self.trees
        ]:
            self.helicopter = Helicopter(
                random.randint(0, self.grid_width - 1),
                random.randint(0, self.grid_height - 1)
            )
    
    def create_collision_particles(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Create particle explosion at position."""
        for _ in range(10):
            self.particles.append(Particle(x, y, color))
    
    def check_powerup_collision(self) -> None:
        """Check if helicopter collected any power-up."""
        if not self.helicopter:
            return
        
        heli_pos = self.helicopter.position
        powerups_to_remove = []
        
        for powerup in self.powerups:
            if heli_pos == powerup.position:
                powerups_to_remove.append(powerup)
                
                # Apply power-up effect
                if powerup.powerup_type == PowerUpType.MEDKIT:
                    self.helicopter.heal()
                    self.create_collision_particles(powerup.x, powerup.y, self.config.COLOR_GREEN)
                elif powerup.powerup_type == PowerUpType.SHIELD:
                    self.helicopter.activate_shield(300)  # 5 seconds
                    self.create_collision_particles(powerup.x, powerup.y, self.config.COLOR_BLUE)
                elif powerup.powerup_type == PowerUpType.BONUS_POINTS:
                    bonus = 100 * self.helicopter.level
                    self.helicopter.add_bonus_points(bonus)
                    self.create_collision_particles(powerup.x, powerup.y, self.config.COLOR_GOLD)
                elif powerup.powerup_type == PowerUpType.INVINCIBILITY:
                    self.helicopter.invincible_timer = 180  # 3 seconds
                    self.create_collision_particles(powerup.x, powerup.y, self.config.COLOR_GOLD)
        
        # Remove collected power-ups
        for p in powerups_to_remove:
            self.powerups.remove(p)
    
    def check_level_up(self) -> None:
        """Check if player should level up."""
        if not self.helicopter:
            return
        
        required_score = self.helicopter.level * self.config.SCORE_PER_LEVEL
        if self.helicopter.score >= required_score:
            self.helicopter.level_up()
            # Increase difficulty: add more obstacles
            if self.helicopter.level % 2 == 0:
                extra_rivers = min(2, self.helicopter.level // 2)
                extra_trees = min(3, self.helicopter.level)
                self.generate_obstacles(extra_rivers, extra_trees)
            # Spawn bonus power-up
            self.spawn_powerup()
    
    def draw_object(self, symbol: str, x: int, y: int, 
                    font: Optional[pygame.font.Font] = None) -> None:
        """Draw an object at grid position (x, y)."""
        if font is None:
            font = self.font
        
        text_surface = font.render(symbol, True, self.config.COLOR_TEXT)
        pos = (
            x * self.config.CELL_SIZE + 10,
            y * self.config.CELL_SIZE + 10
        )
        self.screen.blit(text_surface, pos)
    
    def draw_background(self) -> None:
        """Draw the game background with grass cells."""
        self.screen.fill(self.config.COLOR_GRASS)
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = (
                    x * self.config.CELL_SIZE,
                    y * self.config.CELL_SIZE,
                    self.config.CELL_SIZE,
                    self.config.CELL_SIZE
                )
                pygame.draw.rect(
                    self.screen, 
                    self.config.COLOR_GRASS, 
                    rect
                )
                self.draw_object(self.config.SYMBOL_GRASS, x, y)
    
    def draw_rivers(self) -> None:
        """Draw all river obstacles."""
        for river in self.rivers:
            rect = (
                river.x * self.config.CELL_SIZE,
                river.y * self.config.CELL_SIZE,
                self.config.CELL_SIZE,
                self.config.CELL_SIZE
            )
            pygame.draw.rect(
                self.screen,
                self.config.COLOR_WATER,
                rect
            )
            self.draw_object(river.symbol, river.x, river.y)
    
    def draw_trees(self) -> None:
        """Draw all tree obstacles."""
        for tree in self.trees:
            self.draw_object(tree.symbol, tree.x, tree.y)
    
    def draw_helicopter(self) -> None:
        """Draw the helicopter."""
        if self.helicopter:
            self.draw_object(
                self.helicopter.symbol,
                self.helicopter.x,
                self.helicopter.y
            )
    
    def draw_ui(self) -> None:
        """Draw user interface (lives, score, level, shield)."""
        if self.helicopter:
            # Main UI line
            ui_text = f"{self.config.SYMBOL_HEART} {self.helicopter.lives}  |  "
            ui_text += f"Score: {self.helicopter.score}  |  "
            ui_text += f"Lvl: {self.helicopter.level}"
            if self.helicopter.has_shield:
                ui_text += f"  |  {self.config.SYMBOL_SHIELD}"
            self.draw_object(ui_text, 0, 0)
            
            # Draw shield timer bar if active
            if self.helicopter.has_shield:
                bar_width = 100
                bar_height = 10
                fill_ratio = self.helicopter.shield_duration / 300
                pygame.draw.rect(self.screen, self.config.COLOR_BLUE, 
                               (10, 40, bar_width, bar_height))
                pygame.draw.rect(self.screen, self.config.COLOR_GREEN,
                               (10, 40, int(bar_width * fill_ratio), bar_height))
    
    def draw_menu(self) -> None:
        """Draw main menu."""
        self.screen.fill(self.config.COLOR_BACKGROUND)
        
        title = self.large_font.render("HELICOPTER UNIVERSITY", True, self.config.COLOR_RED)
        subtitle = self.font.render("Enhanced Edition", True, self.config.COLOR_TEXT)
        
        self.screen.blit(title, 
                        (self.config.WINDOW_WIDTH // 2 - title.get_width() // 2,
                         self.config.WINDOW_HEIGHT // 3 - 60))
        self.screen.blit(subtitle,
                        (self.config.WINDOW_WIDTH // 2 - subtitle.get_width() // 2,
                         self.config.WINDOW_HEIGHT // 3))
        
        # Menu options
        for i, option in enumerate(self.menu_options):
            color = self.config.COLOR_GOLD if i == self.menu_selection else self.config.COLOR_TEXT
            text = self.font.render(option, True, color)
            prefix = "> " if i == self.menu_selection else "  "
            text_with_prefix = self.font.render(prefix + option, True, color)
            self.screen.blit(text_with_prefix,
                           (self.config.WINDOW_WIDTH // 2 - text.get_width() // 2 - 20,
                            self.config.WINDOW_HEIGHT // 2 + i * 50))
        
        instructions = self.small_font.render("Use UP/DOWN to select, ENTER to confirm", 
                                             True, self.config.COLOR_TEXT)
        self.screen.blit(instructions,
                        (self.config.WINDOW_WIDTH // 2 - instructions.get_width() // 2,
                         self.config.WINDOW_HEIGHT - 50))
    
    def draw_high_scores(self) -> None:
        """Draw high scores screen."""
        self.screen.fill(self.config.COLOR_BACKGROUND)
        
        title = self.large_font.render("HIGH SCORES", True, self.config.COLOR_GOLD)
        self.screen.blit(title,
                        (self.config.WINDOW_WIDTH // 2 - title.get_width() // 2,
                         self.config.WINDOW_HEIGHT // 6))
        
        scores = self.high_score_manager.get_top_scores()
        if scores:
            for i, entry in enumerate(scores):
                rank = i + 1
                score_text = f"{rank}. {entry['score']} pts (Lvl {entry['level']}) - {entry['date']}"
                color = self.config.COLOR_GOLD if rank == 1 else self.config.COLOR_TEXT
                text = self.font.render(score_text, True, color)
                self.screen.blit(text,
                               (self.config.WINDOW_WIDTH // 2 - text.get_width() // 2,
                                self.config.WINDOW_HEIGHT // 3 + i * 40))
        else:
            no_scores = self.font.render("No scores yet!", True, self.config.COLOR_TEXT)
            self.screen.blit(no_scores,
                           (self.config.WINDOW_WIDTH // 2 - no_scores.get_width() // 2,
                            self.config.WINDOW_HEIGHT // 2))
        
        back_text = self.small_font.render("Press any key to return to menu", 
                                          True, self.config.COLOR_TEXT)
        self.screen.blit(back_text,
                        (self.config.WINDOW_WIDTH // 2 - back_text.get_width() // 2,
                         self.config.WINDOW_HEIGHT - 50))
    
    def draw_powerups(self) -> None:
        """Draw all power-ups with floating animation."""
        import math
        for powerup in self.powerups:
            powerup.update()
            display_y = powerup.y + math.sin(powerup.float_offset) * 0.2
            rect = (
                powerup.x * self.config.CELL_SIZE,
                int(display_y) * self.config.CELL_SIZE,
                self.config.CELL_SIZE,
                self.config.CELL_SIZE
            )
            pygame.draw.rect(self.screen, powerup.color, rect, 2)
            self.draw_object(powerup.symbol, powerup.x, int(display_y))
    
    def draw_particles(self) -> None:
        """Draw and update all particles."""
        alive_particles = []
        for particle in self.particles:
            if particle.update():
                particle.draw(self.screen, self.config.CELL_SIZE, self.font)
                alive_particles.append(particle)
        self.particles = alive_particles
    
    def draw_game_over(self) -> None:
        """Draw game over screen."""
        overlay = pygame.Surface(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        )
        overlay.set_alpha(200)
        overlay.fill(self.config.COLOR_BACKGROUND)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(
            f"Final Score: {self.helicopter.score}", 
            True, 
            self.config.COLOR_TEXT
        )
        level_text = self.font.render(
            f"Level Reached: {self.helicopter.level}",
            True,
            self.config.COLOR_TEXT
        )
        
        # Check if it's a high score
        is_high_score = self.high_score_manager.is_high_score(self.helicopter.score)
        if is_high_score:
            high_score_text = self.font.render("NEW HIGH SCORE!", True, self.config.COLOR_GOLD)
            self.screen.blit(high_score_text,
                           (self.config.WINDOW_WIDTH // 2 - high_score_text.get_width() // 2,
                            self.config.WINDOW_HEIGHT // 2 - 100))
        
        restart_text = self.font.render(
            "Press R to Restart or Q to Quit", 
            True, 
            self.config.COLOR_TEXT
        )
        
        self.screen.blit(
            game_over_text,
            (self.config.WINDOW_WIDTH // 2 - game_over_text.get_width() // 2,
             self.config.WINDOW_HEIGHT // 2 - 60)
        )
        self.screen.blit(
            score_text,
            (self.config.WINDOW_WIDTH // 2 - score_text.get_width() // 2,
             self.config.WINDOW_HEIGHT // 2)
        )
        self.screen.blit(
            level_text,
            (self.config.WINDOW_WIDTH // 2 - level_text.get_width() // 2,
             self.config.WINDOW_HEIGHT // 2 + 30)
        )
        self.screen.blit(
            restart_text,
            (self.config.WINDOW_WIDTH // 2 - restart_text.get_width() // 2,
             self.config.WINDOW_HEIGHT // 2 + 70)
        )
    
    def draw_pause(self) -> None:
        """Draw pause screen."""
        overlay = pygame.Surface(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        )
        overlay.set_alpha(150)
        overlay.fill(self.config.COLOR_BACKGROUND)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.large_font.render("PAUSED", True, (0, 0, 255))
        self.screen.blit(
            pause_text,
            (self.config.WINDOW_WIDTH // 2 - pause_text.get_width() // 2,
             self.config.WINDOW_HEIGHT // 2)
        )
    
    def check_collision(self) -> bool:
        """Check if helicopter collided with any obstacle."""
        if not self.helicopter or self.helicopter.is_invincible:
            return False
        
        heli_pos = self.helicopter.position
        
        for obstacle in self.rivers + self.trees:
            if heli_pos == obstacle.position:
                return True
        return False
    
    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:  # Start Game
                            self.reset_game()
                        elif self.menu_selection == 1:  # High Scores
                            self.state = GameState.HIGH_SCORES
                        elif self.menu_selection == 2:  # Quit
                            return False
                
                elif self.state == GameState.HIGH_SCORES:
                    self.state = GameState.MENU
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_UP:
                        self.helicopter.move(0, -1, self.grid_width, self.grid_height)
                    elif event.key == pygame.K_DOWN:
                        self.helicopter.move(0, 1, self.grid_width, self.grid_height)
                    elif event.key == pygame.K_LEFT:
                        self.helicopter.move(-1, 0, self.grid_width, self.grid_height)
                    elif event.key == pygame.K_RIGHT:
                        self.helicopter.move(1, 0, self.grid_width, self.grid_height)
                    elif event.key == pygame.K_p:
                        self.state = GameState.PAUSED
                    
                    # Check collision after movement
                    if self.check_collision():
                        print("Collision!")
                        shield_absorbed = self.helicopter.lose_life()
                        if not shield_absorbed:
                            self.helicopter.score = max(0, self.helicopter.score - self.config.COLLISION_PENALTY)
                            self.create_collision_particles(
                                self.helicopter.x, self.helicopter.y, self.config.COLOR_RED
                            )
                        
                        if not self.helicopter.is_alive:
                            # Save high score
                            self.high_score_manager.add_score(
                                self.helicopter.score, 
                                self.helicopter.level
                            )
                            self.state = GameState.GAME_OVER
                        else:
                            # Reposition helicopter away from obstacle
                            self.helicopter.x = self.grid_width // 2
                            self.helicopter.y = self.grid_height // 2
                    
                    # Add score for each move
                    self.helicopter.score += self.config.BASE_MOVE_COST
                    
                    # Check for power-up collection
                    self.check_powerup_collision()
                    
                    # Check for level up
                    self.check_level_up()
                    
                    # Randomly spawn power-ups
                    if random.random() < 0.005:  # 0.5% chance per frame
                        self.spawn_powerup()
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_q:
                        return False
        
        return True
    
    def update(self) -> None:
        """Update game state (called every frame)."""
        if self.state == GameState.PLAYING and self.helicopter:
            self.helicopter.update_effects()
    
    def render(self) -> None:
        """Render the current game state."""
        if self.state == GameState.MENU:
            self.draw_menu()
        
        elif self.state == GameState.HIGH_SCORES:
            self.draw_high_scores()
        
        elif self.state == GameState.PLAYING:
            self.draw_background()
            self.draw_rivers()
            self.draw_trees()
            self.draw_powerups()
            if self.helicopter and self.helicopter.should_draw:
                self.draw_helicopter()
            self.draw_ui()
            self.draw_particles()
        
        elif self.state == GameState.GAME_OVER:
            self.draw_background()
            self.draw_rivers()
            self.draw_trees()
            self.draw_helicopter()
            self.draw_ui()
            self.draw_game_over()
        
        elif self.state == GameState.PAUSED:
            self.draw_background()
            self.draw_rivers()
            self.draw_trees()
            self.draw_helicopter()
            self.draw_ui()
            self.draw_pause()
        
        pygame.display.update()
    
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            self.clock.tick(self.config.FPS)
            running = self.handle_events()
            self.update()
            self.render()
        
        if self.helicopter:
            print(f"Game Over! Final Score: {self.helicopter.score}, Level: {self.helicopter.level}")
    
    def cleanup(self) -> None:
        """Clean up pygame resources."""
        pygame.quit()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main():
    """Main entry point for the game."""
    try:
        game = Game()
        game.run()
    finally:
        game.cleanup()


if __name__ == "__main__":
    main()
