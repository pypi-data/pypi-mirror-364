#!/usr/bin/env python3
"""
Claude Dash - Monitor your Claude usage and subscription value
A focused tool for Claude users to track usage and compare subscription vs API costs
"""
import sys
import os
import signal
import logging
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from .__version__ import __version__

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QPalette, QColor, QKeySequence, QShortcut

# Import Claude-specific components
from .providers.claude_code_reader import ClaudeCodeReader
from .ui.cards.claude_code_card import ClaudeCodeCard
from .ui.cards.simple_card import SimpleCard
from .ui.cards.value_analysis_card import ValueAnalysisCard
from .ui.theme_manager import ThemeManager
# Removed session_helper import - using ClaudeCodeReader instead
from .core.config_loader import get_config

# Configure logging - default to WARNING (quiet)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClaudeDataWorker(QThread):
    """Worker thread to fetch Claude data without blocking UI"""
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, reader: ClaudeCodeReader):
        super().__init__()
        self.reader = reader
        self.running = True
        
    def run(self):
        """Run the data fetching loop"""
        while self.running:
            try:
                data = self.fetch_claude_data()
                if data:
                    self.data_ready.emit(data)
            except Exception as e:
                logger.error(f"Error fetching Claude data: {e}")
                self.error_occurred.emit(str(e))
            
            # Wait 30 seconds before next update
            for _ in range(30):
                if not self.running:
                    break
                self.sleep(1)
    
    def fetch_claude_data(self) -> Dict[str, Any]:
        """Fetch Claude usage data"""
        # Get daily data
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_data = self.reader.get_usage_data(since_date=today_start)
        
        # Get session info
        session_info = self.reader.get_current_session_info()
        session_start = session_info['start_time']
        
        # Get current window tokens
        window_tokens = self.reader.get_5hour_window_tokens()
        
        # Calculate hourly burn rate
        hourly_burn_rate = self.reader.calculate_hourly_burn_rate()
        
        # Check if currently active (convert to UTC for comparison)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        is_active = session_start <= now <= (session_start + timedelta(hours=5))
        
        result = {
            'daily_cost': daily_data['total_cost'],
            'session_cost': daily_data['total_cost'],  # For current session
            'tokens': window_tokens,
            'is_active': is_active,
            'session_start': session_start,
            'model_breakdown': session_info.get('model_breakdown', {}),
            'hourly_burn_rate': hourly_burn_rate,
            'last_update': datetime.now()
        }
        
        logger.info(f"Active session check: session_start={session_start}, now={now}, is_active={is_active}")
        
        return result
    
    def stop(self):
        """Stop the worker thread"""
        self.running = False
        self.wait()


class ClaudeDashWindow(QMainWindow):
    """Main window for Claude Dash"""
    
    def __init__(self):
        super().__init__()
        # Create shared reader instance
        self.reader = ClaudeCodeReader()
        self.data_worker = None
        self.theme_selector_active = False
        self.theme_selector_card = None
        # Create theme manager instance
        self.theme_manager = ThemeManager()
        # UI scale factor - load from config
        config = get_config()
        self.scale_factor = config.config.get('ui_scale', 1.0)
        self.init_ui()
        self.check_data_source_and_launch()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Claude Dash")
        # Base sizes: Cards are 220x210 each, 4px spacing between, 4px margins
        # Width: 4 + 220 + 4 + 220 + 4 = 452
        # Height: 4 + 210 + 4 = 218
        base_width = 452
        base_height = 218
        self.setFixedSize(int(base_width * self.scale_factor), int(base_height * self.scale_factor))

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        margin = int(4 * self.scale_factor)
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(0)
        
        # --- Main Content Area ---
        # This container will hold either the cards or the error message
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.content_container)

        # Cards container (will be added to content_layout later)
        self.cards_widget = QWidget()
        cards_layout = QHBoxLayout(self.cards_widget)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(int(4 * self.scale_factor))
        self.claude_card = ClaudeCodeCard(scale_factor=self.scale_factor)
        self.value_card = ValueAnalysisCard(scale_factor=self.scale_factor)
        self.value_card.period_changed.connect(self.on_period_changed)
        cards_layout.addWidget(self.claude_card)
        cards_layout.addWidget(self.value_card)
        
        # Error label (will be added to content_layout later)
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #ccc; font-size: 13px;")
        
        # Remove the stretch to prevent clipping
        
        # Apply theme
        self.apply_theme()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()

    def check_data_source_and_launch(self):
        """Check for data source and launch worker or show error"""
        claude_dir = self.reader.get_claude_dir()
        
        # Check if directory exists and contains any .jsonl files
        if not claude_dir.exists() or not any(claude_dir.rglob("*.jsonl")):
            self.show_data_error(str(claude_dir))
        else:
            self.show_dashboard()
            self.init_data_worker()

    def show_dashboard(self):
        """Display the main dashboard cards"""
        # Clear content layout and add cards
        self.clear_content_layout()
        self.content_layout.addWidget(self.cards_widget)
        self.cards_widget.show()

    def show_data_error(self, path: str):
        """Display an error message about the missing data source"""
        self.clear_content_layout()
        error_text = (
            f'<h2><b>Could not find Claude Code data.</b></h2>'
            f'<p>This application reads data from the local Claude Code directory:</p>'
            f'<i>{path}</i>'
            f'<p>This directory was not found or is empty. Please ensure Claude Code is installed and has been used at least once.</p>'
        )
        self.error_label.setText(error_text)
        self.content_layout.addWidget(self.error_label)
        self.error_label.show()
        # Update window title to indicate data source missing
        self.setWindowTitle("Claude Dash - Data source missing")

    def clear_content_layout(self):
        """Helper to remove all widgets from the content layout"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().hide()

    def create_placeholder_card(self) -> SimpleCard:
        """Create a placeholder card for the value analysis"""
        card = SimpleCard(
            provider_name="value_analysis",
            display_name="Value Analysis",
            color="#FF6B35"
        )
        
        # Override the default content
        card.cost_label.setText("Coming Soon!")
        card.cost_label.setStyleSheet("color: #999; font-size: 16px;")
        
        if hasattr(card, 'metric_label'):
            card.metric_label.setText("API cost comparison\nSavings analysis\nUsage recommendations")
            card.metric_label.setStyleSheet("color: #999; font-size: 12px;")
            card.metric_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return card
        
    def init_data_worker(self):
        """Initialize and start the data worker thread"""
        if self.data_worker is None:
            self.data_worker = ClaudeDataWorker(self.reader)
            self.data_worker.data_ready.connect(self.on_data_ready)
            self.data_worker.error_occurred.connect(self.on_error)
            self.data_worker.start()

        
    def on_data_ready(self, data: Dict[str, Any]):
        """Handle new data from the worker thread"""
        # Store the latest data
        self.last_claude_data = data
        
        # Update Claude card
        self.claude_card.update_display(data)
        
        # Calculate and update value analysis
        value_data = self.calculate_value_analysis(data)
        self.value_card.update_data(value_data)
        
        # Update last update time
        update_time = data.get('last_update', datetime.now())
        # Update time removed to save space
        
    def on_error(self, error_msg: str):
        """Handle errors from the worker thread"""
        logger.error(f"Data worker error: {error_msg}")
        # Error logging removed from UI
        
    def calculate_value_analysis(self, claude_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate value analysis metrics based on Claude usage data"""
        # Get period from value card
        period = getattr(self.value_card, 'current_period', 'month')
        
        # Get current subscription plan from centralized config
        config = get_config()
        plan = config.get_subscription_plan()
        plan_info = config.get_plan_info(plan)
        
        subscription_cost = plan_info.get("monthly_cost", 200)
        tokens_per_session = plan_info.get("session_token_limit", 220000)
        
        # Get reader and current time
        reader = self.reader
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Get current session tokens for fallback calculations
        current_session_tokens = claude_data.get('tokens', 0)
        
        # Get current burn rate from claude data
        burn_rate_tokens = claude_data.get('hourly_burn_rate', 0.0)
        
        # Debug logging
        logger.info(f"Initial burn rate: {burn_rate_tokens} tokens/min, current session tokens: {current_session_tokens}")
        
        # If burn rate is 0, calculate from recent activity
        if burn_rate_tokens == 0:
            # Try multiple fallback methods
            
            # Method 1: Current session rate
            if current_session_tokens > 0:
                session_start = claude_data.get('session_start')
                if session_start:
                    minutes_elapsed = (now - session_start).total_seconds() / 60
                    if minutes_elapsed > 1:  # At least 1 minute
                        burn_rate_tokens = current_session_tokens / minutes_elapsed
                        logger.info(f"Using session-based burn rate: {burn_rate_tokens:.1f} tokens/min")
            
            # Method 2: Last 2 hours average
            if burn_rate_tokens == 0:
                two_hours_ago = now - timedelta(hours=2)
                recent_data = reader.get_usage_data(since_date=two_hours_ago)
                recent_tokens = recent_data.get('total_tokens', 0)
                if recent_tokens > 0:
                    burn_rate_tokens = recent_tokens / 120  # 120 minutes in 2 hours
                    logger.info(f"Using 2-hour average burn rate: {burn_rate_tokens:.1f} tokens/min")
            
            # Method 3: Today's average
            if burn_rate_tokens == 0:
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                today_data = reader.get_usage_data(since_date=today_start)
                today_tokens = today_data.get('total_tokens', 0)
                minutes_today = (now - today_start).total_seconds() / 60
                if today_tokens > 0 and minutes_today > 0:
                    burn_rate_tokens = today_tokens / minutes_today
                    logger.info(f"Using today's average burn rate: {burn_rate_tokens:.1f} tokens/min")
        
        # Convert tokens/min to dollars/min
        # Need to check which model is being used
        # Get current session to determine model
        current_block = reader._get_current_block()
        if current_block and current_block.models:
            # Use the most recent model
            model = current_block.models[-1]
            pricing = config.get_model_pricing(model)
        else:
            # Default to Opus 4 pricing since that's what user is using
            pricing = config.get_model_pricing('claude-opus-4-20250514')
        
        # Assume 20/80 input/output split for estimation (more output than input typically)
        if burn_rate_tokens > 0:
            input_rate = burn_rate_tokens * 0.2 / 1_000_000 * pricing['input']
            output_rate = burn_rate_tokens * 0.8 / 1_000_000 * pricing['output']
            burn_rate_dollars = input_rate + output_rate
        else:
            burn_rate_dollars = 0.0
            
        logger.info(f"Final burn rate: {burn_rate_tokens:.1f} tokens/min = ${burn_rate_dollars:.4f}/min")
        
        if period == "month":
            # This month - only count tokens available up to current time  
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate hours since month start to load ALL month data
            hours_since_month_start = int((now - month_start).total_seconds() / 3600) + 24  # Add 24h buffer
            
            # Force load all month data
            logger.info(f"Loading {hours_since_month_start} hours of data for month calculation")
            reader._update_session_blocks(force_refresh=True, hours_back=hours_since_month_start)
            all_blocks = reader._session_blocks
            
            # Filter for blocks that started in current month OR are currently active
            month_blocks = [b for b in all_blocks 
                          if (b.start_time >= month_start and b.start_time < now) or b.is_active]
            
            # Calculate tokens from blocks directly
            input_tokens = sum(b.input_tokens for b in month_blocks)
            output_tokens = sum(b.output_tokens for b in month_blocks)
            cache_read = sum(b.cache_read_tokens for b in month_blocks)
            cache_creation = sum(b.cache_creation_tokens for b in month_blocks)
            
            # For subscription limits, only count tokens that count against the limit
            tokens_used = input_tokens + output_tokens
            
            # Also try the reader method as fallback
            month_data = reader.get_usage_data(since_date=month_start)
            reader_tokens = month_data.get('total_tokens', 0)
            
            # Use whichever gives more tokens (to avoid missing data)
            if reader_tokens > tokens_used:
                tokens_used = reader_tokens
                logger.info(f"Using reader method tokens: {reader_tokens:,}")
            
            # Debug logging
            logger.info(f"Month: Found {len(month_blocks)} blocks. Tokens - input: {input_tokens:,}, output: {output_tokens:,}, "
                       f"cache_read: {cache_read:,}, cache_creation: {cache_creation:,}, total used: {tokens_used:,}")
            
            # Log some sample blocks to debug
            if month_blocks:
                logger.info(f"First block: {month_blocks[0].start_time} - tokens: {month_blocks[0].total_tokens:,}")
                logger.info(f"Last block: {month_blocks[-1].start_time} - tokens: {month_blocks[-1].total_tokens:,}")
                
                # Check for any suspiciously large blocks
                for block in month_blocks:
                    if block.total_tokens > 100_000:
                        logger.info(f"Large block found: {block.start_time} with {block.total_tokens:,} tokens")
            
            # Calculate based on actual sessions started, not theoretical 24/7 availability
            # This gives a more realistic efficiency metric
            hours_elapsed = (now - month_start).total_seconds() / 3600
            theoretical_sessions = int(hours_elapsed / 5)
            sessions_completed = len(month_blocks)  # Use actual sessions instead
            
            logger.info(f"Sessions: actual={sessions_completed}, theoretical 24/7={theoretical_sessions}")
            
            # Sanity check: if tokens seem too low for the time period, there might be missing data
            days_elapsed = hours_elapsed / 24
            if days_elapsed > 5 and tokens_used < 50000 * days_elapsed:
                # Less than 50k tokens per day after 5+ days suggests missing data
                logger.warning(f"Suspiciously low tokens ({tokens_used:,}) for {days_elapsed:.1f} days. Checking for missing data...")
                
                # Try to estimate from available data
                if current_session_tokens > 0:
                    # Estimate based on current session extrapolated
                    avg_per_session = current_session_tokens * 2  # Assume halfway through session
                    estimated_tokens = int(avg_per_session * sessions_completed)
                    if estimated_tokens > tokens_used:
                        logger.info(f"Using extrapolated estimate: {estimated_tokens:,} tokens")
                        tokens_used = estimated_tokens
            
            # Trust the actual session blocks as the source of truth
            # The month_blocks list already includes all sessions that have occurred
            tokens_available = tokens_per_session * sessions_completed
            
            logger.info(f"Month calculation - hours_elapsed: {hours_elapsed:.1f}, actual sessions: {sessions_completed}, tokens_available: {tokens_available:,}")
            
            # Calculate API cost with proper Opus 4 pricing
            # Only include input and output tokens for fair comparison with subscription
            # Cache tokens are optional performance optimization, not core usage
            api_cost_actual = (
                (input_tokens / 1_000_000 * 15) +
                (output_tokens / 1_000_000 * 75)
            )
            
            # Project API cost for the full month (only for month period)
            if period == "month":
                # Calculate days in current month
                if month_start.month == 12:
                    next_month = month_start.replace(year=month_start.year + 1, month=1)
                else:
                    next_month = month_start.replace(month=month_start.month + 1)
                days_in_month = (next_month - month_start).days
                days_elapsed = hours_elapsed / 24
                
                # Interpolate to full month
                if days_elapsed > 0:
                    api_cost = api_cost_actual * (days_in_month / days_elapsed)
                else:
                    api_cost = api_cost_actual
            else:
                # For 30-day period, no projection needed
                api_cost = api_cost_actual
            
            # Calculate cache costs separately (for information only)
            cache_cost = (
                (cache_creation / 1_000_000 * 18.75) +
                (cache_read / 1_000_000 * 1.50)
            )
            
            # Log the breakdown
            logger.info(f"API cost breakdown: Input=${input_tokens / 1_000_000 * 15:.2f}, "
                       f"Output=${output_tokens / 1_000_000 * 75:.2f}, "
                       f"Total API cost=${api_cost_actual:.2f} "
                       f"(Projected for month: ${api_cost:.2f}) "
                       f"(Cache costs: ${cache_cost:.2f} - not included in comparison)")
            
            # Calculate efficiency
            efficiency = (tokens_used / tokens_available * 100) if tokens_available > 0 else 0
            
            # Calculate breakeven
            if tokens_available > 0 and tokens_used > 0:
                # Calculate actual input/output ratio from user's data
                actual_input_ratio = input_tokens / tokens_used if tokens_used > 0 else 0.2
                actual_output_ratio = output_tokens / tokens_used if tokens_used > 0 else 0.8
                
                # Use actual ratios for personalized breakeven calculation
                # For Opus: input=$15/M, output=$75/M
                avg_cost_per_token = (actual_input_ratio * 15 + actual_output_ratio * 75) / 1_000_000
                tokens_for_200_dollars = 200 / avg_cost_per_token
                breakeven_efficiency = (tokens_for_200_dollars / tokens_available) * 100
                
                logger.info(f"Actual token ratio - Input: {actual_input_ratio:.1%}, Output: {actual_output_ratio:.1%}, "
                           f"Avg cost: ${avg_cost_per_token * 1_000_000:.2f}/M tokens")
            else:
                breakeven_efficiency = 52.0
                
            logger.info(f"Efficiency: {efficiency:.1f}%, Breakeven: {breakeven_efficiency:.1f}%, "
                       f"API cost: ${api_cost:.2f}, Sub cost: ${subscription_cost:.2f}")
            
            # Calculate max tokens per session based on plan
            if subscription_cost == 100:  # Max5x
                max_tokens_per_session = 88_000
            elif subscription_cost == 200:  # Max20x
                max_tokens_per_session = 220_000
            else:  # Pro
                max_tokens_per_session = 19_000
                
            # Find sessions that would overflow
            overflow_sessions = []
            total_overflow_tokens = 0
            
            # Use appropriate blocks variable based on period
            blocks_to_analyze = month_blocks if period == "month" else thirty_day_blocks
            
            # Log session token usage to verify
            session_tokens = [block.total_tokens for block in blocks_to_analyze]
            if session_tokens:
                max_session = max(session_tokens)
                logger.info(f"Session token analysis: max={max_session:,}, min={min(session_tokens):,}, "
                           f"avg={sum(session_tokens)/len(session_tokens):,.0f}")
                # Log how many sessions exceed each limit
                over_88k = sum(1 for t in session_tokens if t > 88_000)
                over_220k = sum(1 for t in session_tokens if t > 220_000)
                logger.info(f"Sessions over limits: {over_88k} over 88k (Max5x), {over_220k} over 220k (Max20x)")
                
            for block in blocks_to_analyze:
                if block.total_tokens > max_tokens_per_session:
                    overflow = block.total_tokens - max_tokens_per_session
                    overflow_sessions.append({
                        'start_time': block.start_time,
                        'tokens': block.total_tokens,
                        'overflow': overflow
                    })
                    total_overflow_tokens += overflow
                    
            return {
                'api_cost': api_cost,
                'subscription_cost': subscription_cost,
                'tokens_used': tokens_used,
                'tokens_available': tokens_available,
                'efficiency': efficiency,
                'breakeven_efficiency': breakeven_efficiency,
                'session_blocks': blocks_to_analyze,
                'overflow_sessions': overflow_sessions,
                'total_overflow_tokens': total_overflow_tokens
            }
            
        else:  # Last 30 days
            # Get data for last 30 days
            thirty_days_ago = now - timedelta(days=30)
            thirty_day_data = reader.get_usage_data(since_date=thirty_days_ago)
            
            # Force load 30 days of data to get all session blocks
            reader._update_session_blocks(force_refresh=True, hours_back=30 * 24)
            all_blocks = reader._session_blocks
            thirty_day_blocks = [b for b in all_blocks 
                               if b.start_time >= thirty_days_ago or 
                               (b.end_time >= thirty_days_ago and b.start_time < thirty_days_ago)]
            
            # Only count tokens that count against subscription limits
            input_tokens = thirty_day_data.get('total_input_tokens', 0)
            output_tokens = thirty_day_data.get('total_output_tokens', 0)
            cache_read = thirty_day_data.get('total_cache_read_tokens', 0)
            cache_creation = thirty_day_data.get('total_cache_creation_tokens', 0)
            
            # Only input + output count against limits
            tokens_used = input_tokens + output_tokens
            
            # Calculate based on actual sessions, not theoretical 24/7
            theoretical_sessions = int(30 * 24 / 5)  # 144 sessions
            sessions_in_30_days = len(thirty_day_blocks)  # Actual sessions
            tokens_available = tokens_per_session * sessions_in_30_days
            
            logger.info(f"30-day sessions: actual={sessions_in_30_days}, theoretical 24/7={theoretical_sessions}")
            
            # Calculate API cost with proper Opus 4 pricing
            # Only include input and output tokens for fair comparison with subscription
            # Cache tokens are optional performance optimization, not core usage
            api_cost_actual = (
                (input_tokens / 1_000_000 * 15) +
                (output_tokens / 1_000_000 * 75)
            )
            
            # Project API cost for the full month (only for month period)
            if period == "month":
                # Calculate days in current month
                if month_start.month == 12:
                    next_month = month_start.replace(year=month_start.year + 1, month=1)
                else:
                    next_month = month_start.replace(month=month_start.month + 1)
                days_in_month = (next_month - month_start).days
                days_elapsed = hours_elapsed / 24
                
                # Interpolate to full month
                if days_elapsed > 0:
                    api_cost = api_cost_actual * (days_in_month / days_elapsed)
                else:
                    api_cost = api_cost_actual
            else:
                # For 30-day period, no projection needed
                api_cost = api_cost_actual
            
            # Calculate cache costs separately (for information only)
            cache_cost = (
                (cache_creation / 1_000_000 * 18.75) +
                (cache_read / 1_000_000 * 1.50)
            )
            
            # Log the breakdown
            logger.info(f"API cost breakdown: Input=${input_tokens / 1_000_000 * 15:.2f}, "
                       f"Output=${output_tokens / 1_000_000 * 75:.2f}, "
                       f"Total API cost=${api_cost_actual:.2f} "
                       f"(Projected for month: ${api_cost:.2f}) "
                       f"(Cache costs: ${cache_cost:.2f} - not included in comparison)")
            
            # Calculate efficiency
            efficiency = (tokens_used / tokens_available * 100) if tokens_available > 0 else 0
            
            # Calculate breakeven
            if tokens_available > 0 and tokens_used > 0:
                # Calculate actual input/output ratio from user's data
                actual_input_ratio = input_tokens / tokens_used if tokens_used > 0 else 0.2
                actual_output_ratio = output_tokens / tokens_used if tokens_used > 0 else 0.8
                
                # Use actual ratios for personalized breakeven calculation
                # For Opus: input=$15/M, output=$75/M
                avg_cost_per_token = (actual_input_ratio * 15 + actual_output_ratio * 75) / 1_000_000
                tokens_for_200_dollars = 200 / avg_cost_per_token
                breakeven_efficiency = (tokens_for_200_dollars / tokens_available) * 100
                
                logger.info(f"Actual token ratio - Input: {actual_input_ratio:.1%}, Output: {actual_output_ratio:.1%}, "
                           f"Avg cost: ${avg_cost_per_token * 1_000_000:.2f}/M tokens")
            else:
                breakeven_efficiency = 52.0
                
            logger.info(f"Efficiency: {efficiency:.1f}%, Breakeven: {breakeven_efficiency:.1f}%, "
                       f"API cost: ${api_cost:.2f}, Sub cost: ${subscription_cost:.2f}")
            
            # Calculate max tokens per session based on plan
            if subscription_cost == 100:  # Max5x
                max_tokens_per_session = 88_000
            elif subscription_cost == 200:  # Max20x
                max_tokens_per_session = 220_000
            else:  # Pro
                max_tokens_per_session = 19_000
                
            # Find sessions that would overflow
            overflow_sessions = []
            total_overflow_tokens = 0
            
            # Use appropriate blocks variable based on period
            blocks_to_analyze = month_blocks if period == "month" else thirty_day_blocks
            
            # Log session token usage to verify
            session_tokens = [block.total_tokens for block in blocks_to_analyze]
            if session_tokens:
                max_session = max(session_tokens)
                logger.info(f"Session token analysis: max={max_session:,}, min={min(session_tokens):,}, "
                           f"avg={sum(session_tokens)/len(session_tokens):,.0f}")
                # Log how many sessions exceed each limit
                over_88k = sum(1 for t in session_tokens if t > 88_000)
                over_220k = sum(1 for t in session_tokens if t > 220_000)
                logger.info(f"Sessions over limits: {over_88k} over 88k (Max5x), {over_220k} over 220k (Max20x)")
                
            for block in blocks_to_analyze:
                if block.total_tokens > max_tokens_per_session:
                    overflow = block.total_tokens - max_tokens_per_session
                    overflow_sessions.append({
                        'start_time': block.start_time,
                        'tokens': block.total_tokens,
                        'overflow': overflow
                    })
                    total_overflow_tokens += overflow
                    
            return {
                'api_cost': api_cost,
                'subscription_cost': subscription_cost,
                'tokens_used': tokens_used,
                'tokens_available': tokens_available,
                'efficiency': efficiency,
                'breakeven_efficiency': breakeven_efficiency,
                'session_blocks': blocks_to_analyze,
                'overflow_sessions': overflow_sessions,
                'total_overflow_tokens': total_overflow_tokens
            }
    
    def on_period_changed(self, period: str):
        """Handle period change from value analysis card"""
        # Get latest Claude data from worker
        if hasattr(self, 'last_claude_data'):
            # Recalculate and update the value analysis
            value_data = self.calculate_value_analysis(self.last_claude_data)
            self.value_card.update_data(value_data)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Theme selector shortcut
        theme_selector_shortcut = QShortcut(QKeySequence("T"), self)
        theme_selector_shortcut.activated.connect(self.show_theme_selector)
        
        # Scale shortcuts
        scale_up_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        scale_up_shortcut.activated.connect(self.scale_up)
        
        scale_down_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        scale_down_shortcut.activated.connect(self.scale_down)
        
        # Reset scale
        scale_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        scale_reset_shortcut.activated.connect(self.scale_reset)
        
    def apply_theme(self):
        """Apply the current theme to the application"""
        # Apply palette
        self.setPalette(self.theme_manager.get_palette())
        
        # Apply main window style
        self.setStyleSheet(self.theme_manager.get_main_window_style())
        
        # Update cards with new theme
        self.claude_card.update_theme()
        self.value_card.update_theme()
        
    def show_theme_selector(self):
        """Show theme selector overlay"""
        if self.theme_selector_active:
            return
            
        from .ui.cards.theme_selector_card import ThemeSelectorCard
        
        # Get all available themes from theme manager
        available_themes = self.theme_manager.get_available_themes()
        current_theme = self.theme_manager.current_theme
        
        # Create theme selector
        self.theme_selector_card = ThemeSelectorCard(available_themes, current_theme)
        self.theme_selector_card.theme_selected.connect(self.on_theme_preview)
        self.theme_selector_card.close_requested.connect(self.hide_theme_selector)
        
        # Position it at the bottom of the Claude card
        self.theme_selector_card.move(self.claude_card.x(), 
                                     self.claude_card.y() + self.claude_card.height - self.theme_selector_card.height)
        self.theme_selector_card.setParent(self.centralWidget())
        self.theme_selector_card.show()
        self.theme_selector_card.raise_()
        self.theme_selector_card.theme_list.setFocus()
        self.theme_selector_active = True
        
    def on_theme_preview(self, theme_name: str):
        """Handle theme preview (just apply theme without closing selector)"""
        # Apply the selected theme
        if self.theme_manager.set_theme(theme_name):
            self.apply_theme()
        # Don't hide the selector - let the user continue browsing
        
    def hide_theme_selector(self):
        """Hide theme selector overlay"""
        if not self.theme_selector_active:
            return
            
        if self.theme_selector_card:
            self.theme_selector_card.hide()
            self.theme_selector_card.deleteLater()
            self.theme_selector_card = None
            
        self.theme_selector_active = False
        
    def mousePressEvent(self, event):
        """Handle mouse clicks on the main window"""
        # Hide theme selector if clicking outside of it
        if self.theme_selector_active and self.theme_selector_card:
            theme_rect = self.theme_selector_card.geometry()
            if not theme_rect.contains(event.pos()):
                self.hide_theme_selector()
        super().mousePressEvent(event)
        
    def scale_up(self):
        """Increase UI scale by 25%"""
        self.scale_factor = min(2.0, self.scale_factor + 0.25)
        self.restart_with_scale()
        
    def scale_down(self):
        """Decrease UI scale by 25%"""
        self.scale_factor = max(0.75, self.scale_factor - 0.25)
        self.restart_with_scale()
        
    def scale_reset(self):
        """Reset UI scale to 100%"""
        self.scale_factor = 1.0
        self.restart_with_scale()
        
    def restart_with_scale(self):
        """Save scale preference and restart the app"""
        # Save scale to config
        config = get_config()
        config.config['ui_scale'] = self.scale_factor
        config.save_config()
        
        # Update both cards to show the scale change message
        scale_msg = f"Scale set to {int(self.scale_factor * 100)}%. Please restart app."
        if hasattr(self, 'claude_card') and self.claude_card and hasattr(self.claude_card, 'update_status'):
            self.claude_card.update_status(scale_msg, "warning")
        if hasattr(self, 'value_card') and self.value_card and hasattr(self.value_card, 'update_status'):
            self.value_card.update_status(scale_msg, "warning")
        
    def keyPressEvent(self, event):
        """Handle key presses"""
        # If theme selector is active and ESC is pressed, it will handle it
        if event.key() == Qt.Key.Key_Escape and self.theme_selector_active:
            event.ignore()  # Let theme selector handle it
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.data_worker:
            self.data_worker.stop()
        event.accept()


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog='claude-dash',
        description='Claude Dash - Monitor your Claude usage and subscription value'
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'Claude Dash {__version__}'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging (most verbose)'
    )
    parser.add_argument(
        '--verbose', '-V',
        action='store_true',
        help='Enable info logging (show operational messages)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress all output except errors'
    )
    
    args = parser.parse_args()
    
    # Configure logging based on flags
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    # Otherwise stays at WARNING level (default)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Claude Dash")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = ClaudeDashWindow()
    window.show()
    window.raise_()
    window.activateWindow()
    
    # Center the window on screen
    screen = app.primaryScreen()
    if screen:
        screen_geometry = screen.availableGeometry()
        window.move(
            (screen_geometry.width() - window.width()) // 2,
            (screen_geometry.height() - window.height()) // 2
        )
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()