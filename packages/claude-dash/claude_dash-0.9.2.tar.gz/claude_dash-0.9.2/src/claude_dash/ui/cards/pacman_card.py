"""
PacMan game card - a fun replacement for the Gemini card
"""
import random
from typing import List, Tuple, Optional, Dict, Any
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QKeyEvent, QFont
from .base_card import BaseProviderCard


class PacManGame(QWidget):
    """The actual PacMan game widget"""
    
    score_changed = pyqtSignal(int)
    game_over = pyqtSignal()
    
    # Game constants
    CELL_SIZE = 11
    MAZE_WIDTH = 28
    MAZE_HEIGHT = 9
    
    # Directions
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)  # Only get focus when clicked
        self.setMinimumHeight(self.MAZE_HEIGHT * self.CELL_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Game state
        self.demo_mode = True
        self.game_active = False
        self.score = 0
        self.lives = 3
        self.demo_move_counter = 0
        self.power_mode = False
        self.power_timer = 0
        
        # Initialize maze (1 = wall, 0 = dot, 2 = power pellet, 3 = empty)
        self.init_maze()
        
        # Player position and direction
        self.pacman_x = 14
        self.pacman_y = 4
        self.pacman_dir = self.RIGHT
        self.next_dir = self.RIGHT
        self.mouth_open = True
        
        # Ghost positions and targets - 3 ghosts starting in random corners
        corners = [
            (1, 1),  # Top-left
            (self.MAZE_WIDTH - 2, 1),  # Top-right
            (1, self.MAZE_HEIGHT - 2),  # Bottom-left
            (self.MAZE_WIDTH - 2, self.MAZE_HEIGHT - 2)  # Bottom-right
        ]
        random.shuffle(corners)  # Randomize corner selection
        
        self.ghosts = [
            {"x": corners[0][0], "y": corners[0][1], "color": QColor("#ff0000"), "dir": self.RIGHT, "name": "Blinky", "move_counter": 0, "eaten": False, "respawn_timer": 0},
            {"x": corners[1][0], "y": corners[1][1], "color": QColor("#ffb7ff"), "dir": self.LEFT, "name": "Pinky", "move_counter": 0, "eaten": False, "respawn_timer": 0},
            {"x": corners[2][0], "y": corners[2][1], "color": QColor("#00ffff"), "dir": self.DOWN, "name": "Inky", "move_counter": 0, "eaten": False, "respawn_timer": 0},
        ]
        
        # Theme colors
        self.wall_color = QColor("#0000ff")
        self.dot_color = QColor("#ffffff")
        self.pacman_color = QColor("#ffff00")
        
        # Timers
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(150)  # Slower for demo mode
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(200)
        
    def init_maze(self):
        """Initialize the maze layout"""
        # Create a simple maze - 1=wall, 0=dot, 2=power pellet, 3=empty
        self.maze = []
        
        # Create maze without thick outer walls
        for i in range(self.MAZE_HEIGHT):
            row = []
            for j in range(self.MAZE_WIDTH):
                # Add some internal walls
                if (i == 3 or i == 5) and j % 6 == 3:
                    row.append(1)
                # Power pellets in corners
                elif (i == 0 and j == 0) or (i == 0 and j == self.MAZE_WIDTH - 1) or \
                     (i == self.MAZE_HEIGHT - 1 and j == 0) or (i == self.MAZE_HEIGHT - 1 and j == self.MAZE_WIDTH - 1):
                    row.append(2)
                # Center area for ghost house
                elif 3 <= i <= 4 and 10 <= j <= 15:
                    if i == 3 and j in [10, 15]:
                        row.append(1)
                    elif i == 4 and (j == 10 or j == 15):
                        row.append(1)
                    else:
                        row.append(3)  # Empty
                else:
                    row.append(0)  # Dot
            self.maze.append(row)
        
        # Count total dots for completion
        self.total_dots = sum(row.count(0) + row.count(2) for row in self.maze)
        
    def start_game(self):
        """Start the actual game"""
        self.demo_mode = False
        self.game_active = True
        self.score = 0
        self.lives = 3
        self.power_mode = False
        self.power_timer = 0
        self.score_changed.emit(self.score)
        
        # Reset positions
        self.pacman_x = 14
        self.pacman_y = 4
        self.pacman_dir = self.RIGHT
        
        # Reset maze
        self.init_maze()
        
        # Reset ghost positions to random corners
        corners = [
            (1, 1),  # Top-left
            (self.MAZE_WIDTH - 2, 1),  # Top-right
            (1, self.MAZE_HEIGHT - 2),  # Bottom-left
            (self.MAZE_WIDTH - 2, self.MAZE_HEIGHT - 2)  # Bottom-right
        ]
        random.shuffle(corners)
        
        for i, ghost in enumerate(self.ghosts):
            if i < len(corners):
                ghost["x"] = corners[i][0]
                ghost["y"] = corners[i][1]
                ghost["move_counter"] = 0
                ghost["eaten"] = False
                ghost["respawn_timer"] = 0
        
        # Speed up for actual gameplay
        self.game_timer.setInterval(100)
        
        self.setFocus()
        self.update()
        
    def stop_game(self):
        """Stop the game and return to demo mode"""
        self.demo_mode = True
        self.game_active = False
        self.game_timer.setInterval(150)  # Slow down for demo
        self.update()
        
    def mousePressEvent(self, event):
        """Toggle game on click"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.demo_mode:
                self.start_game()
            else:
                self.stop_game()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input"""
        key = event.key()
        
        # Don't handle G or T keys - let main window handle them
        if key in (Qt.Key.Key_G, Qt.Key.Key_T):
            event.ignore()  # Let it propagate to parent
            return
        
        # Space bar toggles game
        if key == Qt.Key.Key_Space:
            if self.demo_mode:
                self.start_game()
            else:
                self.stop_game()
            return
            
        # Arrow keys only work during gameplay
        if not self.game_active or self.demo_mode:
            return
            
        if key == Qt.Key.Key_Up:
            self.next_dir = self.UP
        elif key == Qt.Key.Key_Down:
            self.next_dir = self.DOWN
        elif key == Qt.Key.Key_Left:
            self.next_dir = self.LEFT
        elif key == Qt.Key.Key_Right:
            self.next_dir = self.RIGHT
            
    def can_move(self, x: int, y: int, direction: Tuple[int, int]) -> bool:
        """Check if movement in direction is valid"""
        new_x = x + direction[0]
        new_y = y + direction[1]
        
        # Wrap around horizontally
        if new_x < 0:
            new_x = self.MAZE_WIDTH - 1
        elif new_x >= self.MAZE_WIDTH:
            new_x = 0
            
        # Wrap around vertically too (since no outer walls)
        if new_y < 0:
            new_y = self.MAZE_HEIGHT - 1
        elif new_y >= self.MAZE_HEIGHT:
            new_y = 0
            
        # Check for walls
        return self.maze[new_y][new_x] != 1
        
    def update_game(self):
        """Main game update loop"""
        if self.demo_mode:
            self.update_demo()
        elif self.game_active:
            self.update_gameplay()
            
    def update_demo(self):
        """Update demo mode - PacMan moves randomly"""
        self.demo_move_counter += 1
        
        # Change direction occasionally
        if self.demo_move_counter % 10 == 0 or not self.can_move(self.pacman_x, self.pacman_y, self.pacman_dir):
            # Pick a random valid direction
            directions = [self.UP, self.DOWN, self.LEFT, self.RIGHT]
            random.shuffle(directions)
            for d in directions:
                if self.can_move(self.pacman_x, self.pacman_y, d):
                    self.pacman_dir = d
                    break
                    
        # Move PacMan
        if self.can_move(self.pacman_x, self.pacman_y, self.pacman_dir):
            self.pacman_x += self.pacman_dir[0]
            self.pacman_y += self.pacman_dir[1]
            
            # Wrap around horizontally
            if self.pacman_x < 0:
                self.pacman_x = self.MAZE_WIDTH - 1
            elif self.pacman_x >= self.MAZE_WIDTH:
                self.pacman_x = 0
                
            # Wrap around vertically
            if self.pacman_y < 0:
                self.pacman_y = self.MAZE_HEIGHT - 1
            elif self.pacman_y >= self.MAZE_HEIGHT:
                self.pacman_y = 0
                
        # Move ghosts randomly (slower)
        for ghost in self.ghosts:
            ghost["move_counter"] = ghost.get("move_counter", 0) + 1
            
            # Ghosts move every other update (half speed)
            if ghost["move_counter"] % 2 == 0:
                if random.random() < 0.3:  # 30% chance to change direction
                    directions = [self.UP, self.DOWN, self.LEFT, self.RIGHT]
                    random.shuffle(directions)
                    for d in directions:
                        if self.can_move(ghost["x"], ghost["y"], d):
                            ghost["dir"] = d
                            break
                            
                if self.can_move(ghost["x"], ghost["y"], ghost["dir"]):
                    ghost["x"] += ghost["dir"][0]
                    ghost["y"] += ghost["dir"][1]
                    
                    # Wrap around horizontally
                    if ghost["x"] < 0:
                        ghost["x"] = self.MAZE_WIDTH - 1
                    elif ghost["x"] >= self.MAZE_WIDTH:
                        ghost["x"] = 0
                        
                    # Wrap around vertically
                    if ghost["y"] < 0:
                        ghost["y"] = self.MAZE_HEIGHT - 1
                    elif ghost["y"] >= self.MAZE_HEIGHT:
                        ghost["y"] = 0
                    
        self.update()
        
    def update_gameplay(self):
        """Update actual gameplay"""
        # Try to change direction if requested
        if self.can_move(self.pacman_x, self.pacman_y, self.next_dir):
            self.pacman_dir = self.next_dir
            
        # Move PacMan
        if self.can_move(self.pacman_x, self.pacman_y, self.pacman_dir):
            self.pacman_x += self.pacman_dir[0]
            self.pacman_y += self.pacman_dir[1]
            
            # Wrap around horizontally
            if self.pacman_x < 0:
                self.pacman_x = self.MAZE_WIDTH - 1
            elif self.pacman_x >= self.MAZE_WIDTH:
                self.pacman_x = 0
                
            # Wrap around vertically
            if self.pacman_y < 0:
                self.pacman_y = self.MAZE_HEIGHT - 1
            elif self.pacman_y >= self.MAZE_HEIGHT:
                self.pacman_y = 0
                
            # Collect dots
            if self.maze[self.pacman_y][self.pacman_x] == 0:  # Regular dot
                self.maze[self.pacman_y][self.pacman_x] = 3
                self.score += 10
                self.score_changed.emit(self.score)
            elif self.maze[self.pacman_y][self.pacman_x] == 2:  # Power pellet
                self.maze[self.pacman_y][self.pacman_x] = 3
                self.score += 50
                self.score_changed.emit(self.score)
                # Activate power mode
                self.power_mode = True
                self.power_timer = 80  # About 8 seconds at 100ms update rate
                # Reset eaten status for all ghosts
                for ghost in self.ghosts:
                    ghost["eaten"] = False
                
        # Move ghosts with simple AI (slower)
        for ghost in self.ghosts:
            ghost["move_counter"] = ghost.get("move_counter", 0) + 1
            
            # Handle eaten ghost respawn
            if ghost["eaten"]:
                ghost["respawn_timer"] -= 1
                if ghost["respawn_timer"] <= 0:
                    ghost["eaten"] = False
                    # Respawn at a random corner
                    corners = [(1, 1), (self.MAZE_WIDTH - 2, 1), 
                              (1, self.MAZE_HEIGHT - 2), (self.MAZE_WIDTH - 2, self.MAZE_HEIGHT - 2)]
                    corner = random.choice(corners)
                    ghost["x"] = corner[0]
                    ghost["y"] = corner[1]
                continue
                
            # Ghosts move every other update (half speed)
            if ghost["move_counter"] % 2 == 0:
                # Different behavior based on power mode
                if self.power_mode:
                    # Run away from PacMan when vulnerable
                    if random.random() < 0.8:  # 80% chance to flee
                        dx = self.pacman_x - ghost["x"]
                        dy = self.pacman_y - ghost["y"]
                        
                        # Move in opposite direction
                        if abs(dx) > abs(dy):
                            ghost["dir"] = self.LEFT if dx > 0 else self.RIGHT
                        else:
                            ghost["dir"] = self.UP if dy > 0 else self.DOWN
                else:
                    # Normal chase behavior
                    if random.random() < 0.7:  # 70% chance to chase
                        dx = self.pacman_x - ghost["x"]
                        dy = self.pacman_y - ghost["y"]
                        
                        if abs(dx) > abs(dy):
                            ghost["dir"] = self.RIGHT if dx > 0 else self.LEFT
                        else:
                            ghost["dir"] = self.DOWN if dy > 0 else self.UP
                        
                # Try to move
                if self.can_move(ghost["x"], ghost["y"], ghost["dir"]):
                    ghost["x"] += ghost["dir"][0]
                    ghost["y"] += ghost["dir"][1]
                    
                    # Wrap around horizontally
                    if ghost["x"] < 0:
                        ghost["x"] = self.MAZE_WIDTH - 1
                    elif ghost["x"] >= self.MAZE_WIDTH:
                        ghost["x"] = 0
                        
                    # Wrap around vertically
                    if ghost["y"] < 0:
                        ghost["y"] = self.MAZE_HEIGHT - 1
                    elif ghost["y"] >= self.MAZE_HEIGHT:
                        ghost["y"] = 0
                else:
                    # Pick a random direction if stuck
                    directions = [self.UP, self.DOWN, self.LEFT, self.RIGHT]
                    random.shuffle(directions)
                    for d in directions:
                        if self.can_move(ghost["x"], ghost["y"], d):
                            ghost["dir"] = d
                            break
                        
        # Update power mode timer
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False
        
        # Check collision with ghosts
        for ghost in self.ghosts:
            if ghost["x"] == self.pacman_x and ghost["y"] == self.pacman_y and not ghost["eaten"]:
                if self.power_mode:
                    # Eat the ghost!
                    ghost["eaten"] = True
                    ghost["respawn_timer"] = 50  # 5 seconds at 100ms update rate
                    self.score += 200
                    self.score_changed.emit(self.score)
                else:
                    # Normal collision - lose a life
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_active = False
                        self.game_over.emit()
                        self.stop_game()
                    else:
                        # Reset positions
                        self.pacman_x = 14
                        self.pacman_y = 4
                        # Put ghost in a random corner
                        corners = [(1, 1), (self.MAZE_WIDTH - 2, 1), 
                                   (1, self.MAZE_HEIGHT - 2), (self.MAZE_WIDTH - 2, self.MAZE_HEIGHT - 2)]
                        corner = random.choice(corners)
                        ghost["x"] = corner[0]
                        ghost["y"] = corner[1]
                        ghost["move_counter"] = 0
                    
        # Check win condition
        dots_left = sum(row.count(0) + row.count(2) for row in self.maze)
        if dots_left == 0:
            self.score += 1000  # Bonus for completing level
            self.score_changed.emit(self.score)
            self.init_maze()  # Reset maze
            
        self.update()
        
    def animate(self):
        """Handle animations"""
        self.mouth_open = not self.mouth_open
        self.update()
        
    def paintEvent(self, event):
        """Paint the game"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate drawing area with minimal padding
        padding = 0  # No padding since we have card margins
        width = self.width()
        height = self.height()
        cell_width = width // self.MAZE_WIDTH
        cell_height = height // self.MAZE_HEIGHT
        cell_size = min(cell_width, cell_height)
        
        # Center the maze with padding
        offset_x = padding + (width - self.MAZE_WIDTH * cell_size) // 2
        offset_y = padding + (height - self.MAZE_HEIGHT * cell_size) // 2
        
        # Don't draw background - let card background show through
        
        # Draw maze
        for y in range(self.MAZE_HEIGHT):
            for x in range(self.MAZE_WIDTH):
                cell_x = offset_x + x * cell_size
                cell_y = offset_y + y * cell_size
                
                if self.maze[y][x] == 1:  # Wall
                    painter.fillRect(cell_x, cell_y, cell_size, cell_size, self.wall_color)
                elif self.maze[y][x] == 0:  # Dot
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(self.dot_color)
                    dot_size = cell_size // 4
                    painter.drawEllipse(
                        cell_x + cell_size // 2 - dot_size // 2,
                        cell_y + cell_size // 2 - dot_size // 2,
                        dot_size, dot_size
                    )
                elif self.maze[y][x] == 2:  # Power pellet
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(self.dot_color)
                    pellet_size = cell_size // 2
                    painter.drawEllipse(
                        cell_x + cell_size // 2 - pellet_size // 2,
                        cell_y + cell_size // 2 - pellet_size // 2,
                        pellet_size, pellet_size
                    )
                    
        # Draw ghosts
        for ghost in self.ghosts:
            if ghost["eaten"] and not self.power_mode:
                continue  # Don't draw eaten ghosts after power mode ends
                
            ghost_x = offset_x + ghost["x"] * cell_size
            ghost_y = offset_y + ghost["y"] * cell_size
            
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Different appearance in power mode
            if self.power_mode and not ghost["eaten"]:
                # Vulnerable ghost - blue color, flashing when time is running out
                if self.power_timer < 20 and self.power_timer % 4 < 2:
                    painter.setBrush(QColor("#ffffff"))  # Flash white
                else:
                    painter.setBrush(QColor("#0000ff"))  # Blue
            else:
                painter.setBrush(ghost["color"])
            
            # Ghost body (rounded rectangle)
            painter.drawEllipse(ghost_x + 1, ghost_y + 1, cell_size - 2, cell_size - 2)
            
            # Ghost eyes
            painter.setBrush(QColor("#ffffff"))
            eye_size = cell_size // 5
            painter.drawEllipse(ghost_x + cell_size // 4 - eye_size // 2, ghost_y + cell_size // 3, eye_size, eye_size)
            painter.drawEllipse(ghost_x + 3 * cell_size // 4 - eye_size // 2, ghost_y + cell_size // 3, eye_size, eye_size)
            
            # Pupils - scared expression in power mode
            if self.power_mode and not ghost["eaten"]:
                painter.setBrush(QColor("#ffffff"))
                pupil_size = eye_size // 3
            else:
                painter.setBrush(QColor("#0000ff"))
                pupil_size = eye_size // 2
            painter.drawEllipse(ghost_x + cell_size // 4 - pupil_size // 2, ghost_y + cell_size // 3 + pupil_size // 2, pupil_size, pupil_size)
            painter.drawEllipse(ghost_x + 3 * cell_size // 4 - pupil_size // 2, ghost_y + cell_size // 3 + pupil_size // 2, pupil_size, pupil_size)
            
        # Draw PacMan
        pac_x = offset_x + self.pacman_x * cell_size
        pac_y = offset_y + self.pacman_y * cell_size
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.pacman_color)
        
        if self.mouth_open and (self.game_active or self.demo_mode):
            # Draw PacMan with mouth open
            start_angle = 0
            span_angle = 300
            
            # Adjust angle based on direction
            if self.pacman_dir == self.RIGHT:
                start_angle = 30
            elif self.pacman_dir == self.LEFT:
                start_angle = 210
            elif self.pacman_dir == self.UP:
                start_angle = 120
            elif self.pacman_dir == self.DOWN:
                start_angle = 300
                
            painter.drawPie(pac_x + 1, pac_y + 1, cell_size - 2, cell_size - 2, start_angle * 16, span_angle * 16)
        else:
            # Draw closed circle
            painter.drawEllipse(pac_x + 1, pac_y + 1, cell_size - 2, cell_size - 2)
            
        # Draw overlay text
        font = QFont()
        
        if self.demo_mode:
            # Demo mode - show click to play without background
            painter.setPen(QPen(QColor(255, 255, 255)))
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            # Add text shadow for readability
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawText(6, 16, "Click or Space")
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(5, 15, "Click or Space")
        else:
            # Game mode - show score and controls without backgrounds
            font.setPointSize(9)
            font.setBold(True)
            painter.setFont(font)
            # Score with shadow
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawText(6, 14, f"Score: {self.score}")
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(5, 13, f"Score: {self.score}")
            
            # Controls hint at bottom
            full_height = self.height()
            font.setPointSize(8)
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawText(6, full_height - 6, "Arrows • Space/Click to Stop")
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(5, full_height - 7, "Arrows • Space/Click to Stop")
            
    def update_theme_colors(self, is_dark: bool):
        """Update colors based on theme"""
        if is_dark:
            self.wall_color = QColor("#0040ff")
            self.dot_color = QColor("#ffffff")
            self.pacman_color = QColor("#ffff00")
        else:
            self.wall_color = QColor("#4080ff")
            self.dot_color = QColor("#404040")
            self.pacman_color = QColor("#ffa500")
            
            # Lighter ghost colors for light theme
            self.ghosts[0]["color"] = QColor("#ff4444")  # Lighter red
            self.ghosts[1]["color"] = QColor("#ffaaff")  # Lighter pink
            self.ghosts[2]["color"] = QColor("#44dddd")  # Lighter cyan


class PacManCard(BaseProviderCard):
    """PacMan game card"""
    
    def __init__(self):
        super().__init__(
            provider_name="pacman",
            display_name="PacMan",
            color="#ffff00",  # Yellow
            size=(220, 104),  # Half-height
            show_status=False  # No status label
        )
        self.auto_update = False  # Don't poll for updates
        
    def setup_content(self):
        """Setup PacMan game content"""
        # Remove the default title completely
        self.layout.takeAt(0)  # Remove default title layout
        
        # Game widget fills entire card with padding
        self.game = PacManGame()
        self.game.score_changed.connect(self.update_score)
        self.game.game_over.connect(self.on_game_over)
        self.layout.addWidget(self.game)
        
        # Add small margins to avoid border overlap
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
    def update_score(self, score: int):
        """Update score display"""
        # Score is shown in the game itself now
        pass
        
    def on_game_over(self):
        """Handle game over"""
        # Game handles its own state
        pass
        
    def update_display(self, data: Dict[str, Any]):
        """PacMan doesn't need data updates"""
        pass
        
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """PacMan doesn't fetch any data"""
        return None
        
    def mousePressEvent(self, event):
        """Override to prevent base card click handling"""
        # Let the game handle clicks
        pass
        
    def update_theme_colors(self, is_dark: bool):
        """Update game colors based on theme"""
        self.game.update_theme_colors(is_dark)
        self.game.update()
        
    def scale_content_fonts(self, scale: float):
        """Scale fonts"""
        # PacMan game doesn't have any UI elements with fonts
        # The game itself handles font scaling in its paintEvent
        pass