"""
Enhanced Claude Code card that shows subscription and usage costs
"""
import json
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from PyQt6.QtWidgets import QLabel, QProgressBar, QFrame, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from .base_card import BaseProviderCard
from ...core.config_loader import get_config

logger = logging.getLogger(__name__)


class ModelUsageGraph(QWidget):
    """Horizontal bar showing Opus 4 vs Sonnet 4 usage percentage"""
    
    def __init__(self):
        super().__init__()
        self.opus_percentage = 50.0  # Default to 50/50
        self.setMinimumHeight(12)
        self.setMaximumHeight(12)
        
    def set_data(self, model_breakdown: Dict[str, Any]):
        """Update graph with model usage data"""
        # Calculate percentages from total session usage
        opus_tokens = 0
        sonnet_tokens = 0
        
        for model, stats in model_breakdown.items():
            total_tokens = stats.get('input_tokens', 0) + stats.get('output_tokens', 0)
            if 'opus' in model.lower():
                opus_tokens += total_tokens
            elif 'sonnet' in model.lower():
                sonnet_tokens += total_tokens
                
        total = opus_tokens + sonnet_tokens
        if total > 0:
            self.opus_percentage = (opus_tokens / total) * 100
        else:
            self.opus_percentage = 50.0
            
        self.update()
            
    def paintEvent(self, event):
        """Paint the horizontal percentage bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(230, 230, 230))
        
        # Calculate split point
        width = self.width()
        split_x = int(width * self.opus_percentage / 100)
        
        # Draw Opus portion (blue)
        if split_x > 0:
            painter.fillRect(0, 0, split_x, self.height(), QColor(41, 98, 255))
        
        # Draw Sonnet portion (orange) 
        if split_x < width:
            painter.fillRect(split_x, 0, width - split_x, self.height(), QColor(255, 106, 53))


class ClaudeCodeCard(BaseProviderCard):
    """Claude Code card with subscription and usage display"""
    
    def __init__(self, scale_factor: float = 1.0):
        self.config = get_config()
        self.session_start_time = None
        self.current_tokens = 0
        
        # Get plan info from config
        plan = self.config.get_subscription_plan()
        plan_info = self.config.get_plan_info(plan)
        self.token_limit = plan_info.get("session_token_limit", 220000)
        
        self.recent_token_rates = []  # Track token usage rate
        self.hourly_burn_rate = 0.0  # Tokens per minute based on last hour
        
        # Get plan display name from config
        plan_display = plan_info.get("display_name", plan_info.get("name", "Max20x"))
        
        self.plan_display = plan_display
        super().__init__(
            provider_name="anthropic",
            display_name="Claude Code",
            color="#ff6b35",  # Vibrant orange
            scale_factor=scale_factor
        )
        self.billing_url = "https://console.anthropic.com/settings/billing"
        self.enable_billing_link()
        # Update every 30 seconds
        self.update_interval = 30000
        
        # Theme colors
        self.progress_bar_bg = "#e0e0e0"
        self.progress_bar_text = "#000000"
        
        # Timer to update time remaining
        self.time_update_timer = QTimer()
        self.time_update_timer.timeout.connect(self.update_time_display)
        self.time_update_timer.start(1000)  # Update every second
        
    def get_font_size(self) -> int:
        """Get current font size for dynamic text"""
        # Check if parent window has font scale
        parent = self.window()
        if parent and hasattr(parent, 'font_scale'):
            return int(self.base_font_sizes['small'] * parent.font_scale)
        return self.base_font_sizes['small']
        
    def setup_content(self):
        """Setup Claude Code specific content"""
        
        # Remove the default title and use compact header instead
        self.layout.takeAt(0)  # Remove default title layout
        
        # Create compact header
        header_layout = self.create_compact_header("Claude Code")
        self.header_value_label.setText(self.plan_display)  # Show plan in value font
        self.layout.insertLayout(0, header_layout)

        self.layout.addSpacing(14)  # Add vertical space after headers

        # GROUP 1: Token Group
        # Token progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimumHeight(12)
        self.progress_bar.setMaximumHeight(12)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% of token limit")
        self.layout.addWidget(self.progress_bar)
        
        # Small spacing within token group
        self.layout.addSpacing(3)
        
        # Token count
        self.token_label = QLabel("Tokens: -")
        self.token_label.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px;")
        self.layout.addWidget(self.token_label)
        
        # Spacing between groups
        self.layout.addSpacing(10)
        
        # GROUP 2: Session Time Group
        # Session time label
        self.time_label = QLabel("Session Time")
        self.time_label.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px;")
        self.layout.addWidget(self.time_label)
        
        # Small spacing
        self.layout.addSpacing(3)
        
        # Time progress bar (MATCH MODEL USAGE BAR)
        self.time_progress_bar = QProgressBar()
        self.time_progress_bar.setMaximum(100)
        self.time_progress_bar.setMinimumHeight(12)
        self.time_progress_bar.setMaximumHeight(12)
        self.time_progress_bar.setTextVisible(True)
        self.time_progress_bar.setFormat("%p%")
        # Apply Model Usage bar styling (blue like Opus)
        self.time_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgb(230, 230, 230);
                text-align: center;
                color: #000000;
                font-size: {self.base_font_sizes['small'] - 1}px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: rgb(41, 98, 255);
                border: none;
            }}
        """)
        self.layout.addWidget(self.time_progress_bar)
        
        # Small spacing
        self.layout.addSpacing(3)
        
        # Time remaining
        self.time_remaining_label = QLabel("Time left: -")
        self.time_remaining_label.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px;")
        self.layout.addWidget(self.time_remaining_label)
        
        # Spacing between groups
        self.layout.addSpacing(10)
        
        # GROUP 3: Model Usage Group
        # Model usage label
        self.model_label = QLabel("Model Usage")
        self.model_label.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px;")
        self.layout.addWidget(self.model_label)
        
        # Small spacing
        self.layout.addSpacing(3)
        
        # Model graph
        self.model_graph = ModelUsageGraph()
        self.layout.addWidget(self.model_graph)
        
        # Small spacing
        self.layout.addSpacing(3)
        
        # Model legend
        self.model_legend = QLabel('<span style="color: #2962FF;">&#9632;</span> Opus  <span style="color: #FF6A35;">&#9632;</span> Sonnet')
        self.model_legend.setTextFormat(Qt.TextFormat.RichText)
        self.model_legend.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px;")
        self.layout.addWidget(self.model_legend)
        
        # Spacing between groups
        self.layout.addSpacing(6)
        
        # GROUP 4: Prediction Group
        # Prediction
        self.prediction_label = QLabel("Prediction: -")
        self.prediction_label.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px;")
        self.layout.addWidget(self.prediction_label)
        
        # Small spacing
        self.layout.addSpacing(2)
        
        # New session info
        self.new_session_label = QLabel("")
        self.new_session_label.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px;")
        self.layout.addWidget(self.new_session_label)
        
    def update_display(self, data: Dict[str, Any]):
        """Update the display with usage data"""
        # Extract data
        daily_cost = data.get('daily_cost', 0.0)
        session_cost = data.get('session_cost', 0.0)
        tokens = data.get('tokens', 0)
        is_active = data.get('is_active', False)
        session_start = data.get('session_start')
        initial_rate_data = data.get('initial_rate_data', [])
        model_breakdown = data.get('model_breakdown', {})
        hourly_burn_rate = data.get('hourly_burn_rate', 0.0)
        
        # Debug logging
        # Update display with new data
        # Token limit already set in __init__, no need to refetch
        
        # Update session start time
        if session_start:
            self.session_start_time = session_start
        
        # Update hourly burn rate
        self.hourly_burn_rate = hourly_burn_rate
        
        # Initialize rate data from historical data if provided
        if initial_rate_data and not self.recent_token_rates:
            self.recent_token_rates = initial_rate_data[-10:]  # Keep last 10
        
        # Track token usage rate
        if self.current_tokens > 0 and tokens > self.current_tokens:
            tokens_added = tokens - self.current_tokens
            self.recent_token_rates.append(tokens_added)
            # Keep only last 10 measurements
            if len(self.recent_token_rates) > 10:
                self.recent_token_rates.pop(0)
        
        self.current_tokens = tokens
        
        # Calculate token percentage
        token_percentage = (tokens / self.token_limit * 100) if self.token_limit > 0 else 0
        
        # Update progress bar based on tokens (cap at 100%)
        self.progress_bar.setValue(min(100, int(token_percentage)))
        
        # Update progress bar format based on whether we're over limit
        if token_percentage > 100:
            self.progress_bar.setFormat(f"{int(token_percentage)}% of token limit")
        else:
            self.progress_bar.setFormat("%p% of token limit")
        
        # Color code the progress bar based on token usage
        self._update_progress_bar_color(token_percentage)
        
        # Update tokens
        if is_active and tokens > 0:
            self.token_label.setText(f"Tokens: {tokens:,} of {self.token_limit:,}")
        elif is_active:
            self.token_label.setText("Tokens: 0")
        else:
            self.token_label.setText("Tokens: No active session")
            
        # Update status with last update time
        logger.info(f"Claude card received: is_active={is_active}")
        last_update = data.get('last_update', datetime.now())
        update_time_str = last_update.strftime("%H:%M:%S")
        
        # Format with smaller font for update time
        if is_active:
            status_html = f'Active Session <span style="font-size: {self.base_font_sizes["small"] - 1}px;">• Updated: {update_time_str}</span>'
            self.update_status(status_html, "active", use_html=True)
        else:
            status_html = f'No active session <span style="font-size: {self.base_font_sizes["small"] - 1}px;">• Updated: {update_time_str}</span>'
            self.update_status(status_html, "normal", use_html=True)
        
        # Update time display
        self.update_time_display()
        
        # Update model usage graph
        if model_breakdown:
            self.model_graph.set_data(model_breakdown)
        
    def update_time_display(self):
        """Update time-related displays"""
        # Use UTC time for calculations
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Use the actual session start time from the data
        if not self.session_start_time:
            # No active session - show inactive state
            self.time_label.setText("No Active Session")
            self.time_progress_bar.setValue(0)
            self.time_remaining_label.setText("Session inactive")
            self.prediction_label.setText("")
            self.new_session_label.setText("")
            return
            
        session_start = self.session_start_time
        session_end = session_start + timedelta(hours=5)
        
        # Calculate remaining and elapsed time
        remaining = session_end - now
        elapsed = now - session_start
        
        # Calculate time percentage
        session_duration = timedelta(hours=5)
        time_percentage = (elapsed.total_seconds() / session_duration.total_seconds() * 100)
        time_percentage = min(100, max(0, time_percentage))
        
        # Update time progress bar
        self.time_progress_bar.setValue(int(time_percentage))
        
        # Format time remaining (without seconds)
        if remaining.total_seconds() > 0:
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            self.time_remaining_label.setText(f"Time left: {hours}h {minutes}m")
        else:
            self.time_remaining_label.setText("Time left: Session expired")
        
        # Calculate prediction using hourly burn rate
        if self.hourly_burn_rate > 0 and remaining.total_seconds() > 0:
            # Calculate when we'll hit the limit
            tokens_until_limit = self.token_limit - self.current_tokens
            
            # Time until limit in minutes
            minutes_until_limit = tokens_until_limit / self.hourly_burn_rate
            time_until_limit = timedelta(minutes=minutes_until_limit)
            
            # Log the calculation for debugging
            logger.debug(f"Token prediction: {tokens_until_limit} tokens left / {self.hourly_burn_rate:.1f} tokens/min = {minutes_until_limit:.1f} minutes")
            
            # Calculate the exact time when tokens will run out
            limit_time = now + time_until_limit
            
            # Format time like Claude Monitor (local time)
            # Convert from UTC to local time for display
            from zoneinfo import ZoneInfo
            utc_time = limit_time.replace(tzinfo=ZoneInfo('UTC'))
            local_limit_time = utc_time.astimezone()
            
            # Check if it's today or tomorrow
            local_now = datetime.now()
            if local_limit_time.date() == local_now.date():
                time_str = local_limit_time.strftime("%I:%M %p").lstrip('0')
            elif local_limit_time.date() == (local_now + timedelta(days=1)).date():
                time_str = "tomorrow " + local_limit_time.strftime("%I:%M %p").lstrip('0')
            else:
                time_str = local_limit_time.strftime("%m/%d %I:%M %p").lstrip('0')
            
            # Show when work will stop (sooner of token limit or session end)
            if time_until_limit < remaining:
                # Tokens will run out first
                self.prediction_label.setText(f"Tokens run out: {time_str}")
                self.prediction_label.setStyleSheet(f"color: #ff6b35; font-size: {self.get_font_size()}px; font-weight: bold;")
            else:
                # Session will end first - show session end time
                from zoneinfo import ZoneInfo
                session_end_utc = session_end.replace(tzinfo=ZoneInfo('UTC'))
                session_end_local = session_end_utc.astimezone()
                session_end_str = session_end_local.strftime("%I:%M %p").lstrip('0')
                self.prediction_label.setText(f"Session ends: {session_end_str}")
                self.prediction_label.setStyleSheet(f"color: #0096FF; font-size: {self.get_font_size()}px;")
        else:
            # Still calculating or no data yet
            if self.current_tokens > 0:
                self.prediction_label.setText("Rate: Calculating...")
            else:
                self.prediction_label.setText("Prediction: -")
            self.prediction_label.setStyleSheet(f"font-size: {self.get_font_size()}px;")
            
        # Show when the next session starts (after current session ends)
        # Only show if we have an active session
        if self.session_start_time:
            # Convert session_end (UTC) to local time for display
            from zoneinfo import ZoneInfo
            utc_session_end = session_end.replace(tzinfo=ZoneInfo('UTC'))
            local_session_end = utc_session_end.astimezone()
            new_session_time = local_session_end.strftime("%I:%M %p").lstrip('0')
            # Next session starts immediately when current one ends
            self.new_session_label.setText(f"Next session: {new_session_time}")
        else:
            # No active session
            self.new_session_label.setText("")
        
    def scale_content_fonts(self, scale: float):
        """Scale Claude Code specific fonts"""
        # Scale token label (1pt smaller than secondary)
        self.token_label.setStyleSheet(f"font-size: {int((self.base_font_sizes['secondary'] - 1) * scale)}px;")
        
        # Scale time labels
        self.time_label.setStyleSheet(f"font-size: {int(self.base_font_sizes['small'] * scale)}px; margin-top: 2px;")
        self.time_remaining_label.setStyleSheet(f"font-size: {int(self.base_font_sizes['small'] * scale)}px;")
        self.new_session_label.setStyleSheet(f"font-size: {int(self.base_font_sizes['small'] * scale)}px;")
        self.model_label.setStyleSheet(f"font-size: {int(self.base_font_sizes['small'] * scale)}px; margin-top: 2px;")
        self.model_legend.setStyleSheet(f"font-size: {int((self.base_font_sizes['small'] - 1) * scale)}px;")
        
        # Scale prediction label with special handling for its dynamic styling
        current_style = self.prediction_label.styleSheet()
        if "color: #ff6b35" in current_style:  # Orange warning
            self.prediction_label.setStyleSheet(f"color: #ff6b35; font-size: {int(self.base_font_sizes['small'] * scale)}px; font-weight: bold;")
        elif "color: #28a745" in current_style:  # Green
            self.prediction_label.setStyleSheet(f"color: #28a745; font-size: {int(self.base_font_sizes['small'] * scale)}px;")
        else:  # Default
            self.prediction_label.setStyleSheet(f"font-size: {int(self.base_font_sizes['small'] * scale)}px;")
            
    def update_theme_colors(self, is_dark: bool):
        """Update progress bar colors based on theme"""
        if is_dark:
            # Dark theme - use lighter backgrounds and white text
            self.progress_bar_bg = "#404040"
            self.progress_bar_text = "#ffffff"
        else:
            # Light theme - use darker text on light backgrounds
            self.progress_bar_bg = "#e0e0e0"
            self.progress_bar_text = "#000000"
            
        # Update time progress bar to MATCH MODEL USAGE BAR
        self.time_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgb(230, 230, 230);
                text-align: center;
                color: {self.progress_bar_text};
                font-size: {self.base_font_sizes['small'] - 1}px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: rgb(41, 98, 255);
                border: none;
            }}
        """)
        
        # Re-apply token progress bar color with theme
        if hasattr(self, 'current_tokens'):
            token_percentage = (self.current_tokens / self.token_limit * 100) if self.token_limit > 0 else 0
            self._update_progress_bar_color(token_percentage)
            
    def _update_progress_bar_color(self, token_percentage: float):
        """Update progress bar color based on percentage"""
        if token_percentage >= 90:
            chunk_color = "#dc3545"  # Red
        elif token_percentage >= 75:
            chunk_color = "#ff6b35"  # Orange
        else:
            chunk_color = "#28a745"  # Green
            
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {self.progress_bar_bg};
                text-align: center;
                color: {self.progress_bar_text};
                font-size: {self.base_font_sizes['small'] - 1}px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {chunk_color};
                border: none;
            }}
        """)
