"""
Value Analysis Card - Shows subscription value vs API costs
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
                             QPushButton, QButtonGroup, QFrame, QProgressBar,
                             QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor
from .base_card import BaseProviderCard

logger = logging.getLogger(__name__)


class TabButton(QPushButton):
    """Custom button that looks like a tab"""
    def __init__(self, text: str, active: bool = False):
        super().__init__(text)
        self.setCheckable(True)
        self.setChecked(active)
        self.setFixedHeight(20)  # Increased height to prevent clipping
        self.setMinimumWidth(30)  # Minimum width to prevent too small
        # Don't set fixed width - let it size to content
        self.update_style()
        self.toggled.connect(self.update_style)
        
    def update_style(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2962FF;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 6px;
                    font-size: 9px;
                    font-weight: 600;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #424242;
                    color: #bbb;
                    border: none;
                    border-radius: 8px;
                    padding: 0 6px;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background-color: #525252;
                    color: white;
                }
            """)


class ValueAnalysisCard(BaseProviderCard):
    """Card showing subscription value analysis and efficiency metrics"""
    
    # Signal emitted when time period changes
    period_changed = pyqtSignal(str)
    
    def __init__(self, scale_factor: float = 1.0):
        # Get config first, before calling super().__init__
        from ...core.config_loader import get_config
        self.config = get_config()
        
        # Get default subscription cost from config
        plan = self.config.get_subscription_plan()
        plan_info = self.config.get_plan_info(plan)
        self.default_sub_cost = plan_info.get("monthly_cost", 200)
        
        super().__init__(
            provider_name="value_analysis",
            display_name="Analysis",  # Different short name
            color="#FF6B35",
            scale_factor=scale_factor
        )
        
        # Current data
        self.current_period = "month"  # "last_month", "month", or "30days"
        self.api_cost = 0.0
        self.subscription_cost = self.default_sub_cost
        self.tokens_used = 0
        self.tokens_available = 0
        self.efficiency = 0.0
        self.breakeven_efficiency = 0.0
        
    def get_font_size(self):
        """Match Claude card font sizing"""
        return self.base_font_sizes['small']
        
    def create_compact_header(self, title: str) -> QHBoxLayout:
        """Create header matching Claude card style"""
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        
        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(self.base_font_sizes['title'])
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setMinimumHeight(self.base_font_sizes['title'] + 6)  # Add padding for descenders
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Tab buttons - two options
        # Get current month name
        from datetime import datetime
        now = datetime.now()
        current_month = now.strftime("%b")  # e.g., "Jan"
        
        self.month_button = TabButton(current_month, True)
        self.days30_button = TabButton("-30", False)
        
        # Button group to ensure only one is selected
        self.period_group = QButtonGroup()
        self.period_group.addButton(self.month_button)
        self.period_group.addButton(self.days30_button)
        
        self.month_button.clicked.connect(lambda: self._on_period_changed("month"))
        self.days30_button.clicked.connect(lambda: self._on_period_changed("30days"))
        
        header_layout.addWidget(self.month_button)
        header_layout.addWidget(self.days30_button)
        
        return header_layout
        
    def setup_content(self):
        """Set up the card's content"""
        # Remove the default title and use compact header
        self.layout.takeAt(0)  # Remove default title layout
        
        # Create compact header with tab buttons
        header_layout = self.create_compact_header("Analysis")
        self.layout.insertLayout(0, header_layout)
        
        self.layout.addSpacing(16)  # Slightly reduced to give more room
        
        # Start with main content groups
        from ..theme_manager import ThemeManager
        theme_manager = ThemeManager()
        
        # GROUP 1: Cost Comparison
        # Cost comparison header
        cost_header = QLabel("Cost Comparison:")
        cost_header.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px; line-height: {self.base_font_sizes['small'] + 4}px;")
        cost_header.setFixedHeight(self.base_font_sizes['small'] + 6)
        self.layout.addWidget(cost_header)
        
        # Small spacing within group
        self.layout.addSpacing(2)
        
        # API Cost
        api_layout = QHBoxLayout()
        api_layout.setSpacing(2)
        api_layout.setContentsMargins(0, 0, 0, 0)
        self.api_label = QLabel("Projected API for month:")
        self.api_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small']) + f"; line-height: {self.base_font_sizes['small'] + 4}px;")
        self.api_label.setFixedHeight(self.base_font_sizes['small'] + 6)
        api_layout.addWidget(self.api_label)
        api_layout.addStretch()
        self.api_cost_label = QLabel("$0")
        self.api_cost_label.setStyleSheet(f"color: #4CAF50; font-size: {self.base_font_sizes['small']}px; font-weight: bold;")
        self.api_cost_label.setFixedHeight(self.base_font_sizes['small'] + 6)
        api_layout.addWidget(self.api_cost_label)
        self.layout.addLayout(api_layout)
        
        # Subscription cost
        sub_layout = QHBoxLayout()
        sub_layout.setSpacing(4)
        sub_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_label = QLabel("Subscription:")
        self.sub_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small']) + f"; line-height: {self.base_font_sizes['small'] + 4}px;")
        self.sub_label.setFixedHeight(self.base_font_sizes['small'] + 6)
        sub_layout.addWidget(self.sub_label)
        sub_layout.addStretch()
        self.sub_cost_label = QLabel(f"${self.default_sub_cost}")
        self.sub_cost_label.setStyleSheet(f"color: #ff6b35; font-size: {self.base_font_sizes['small']}px; font-weight: bold;")
        self.sub_cost_label.setFixedHeight(self.base_font_sizes['small'] + 6)
        sub_layout.addWidget(self.sub_cost_label)
        self.layout.addLayout(sub_layout)
        
        # Small spacing
        self.layout.addSpacing(12)
        
        # Spacing between groups
#        self.layout.addSpacing(2)
        
        # GROUP 3: Efficiency
        # Efficiency header with click handler
        self.eff_header = QLabel('<span style="text-decoration: underline; cursor: pointer;">Plan Efficiency</span> (Month through today)')
        self.eff_header.setTextFormat(Qt.TextFormat.RichText)
        self.eff_header.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; line-height: {self.base_font_sizes['small'] + 3}px;")
        self.eff_header.setFixedHeight(self.base_font_sizes['small'] + 6)
        self.eff_header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eff_header.setToolTip("Click for explanation")
        self.eff_header.mousePressEvent = lambda e: self._show_efficiency_explanation()
        self.layout.addWidget(self.eff_header)
        
        # Small spacing
        self.layout.addSpacing(4)
        
        # Efficiency bar (match Model Usage bar style but with text)
        self.efficiency_bar = QProgressBar()
        self.efficiency_bar.setMaximum(100)
        self.efficiency_bar.setMinimumHeight(12)  # Match Claude card
        self.efficiency_bar.setMaximumHeight(12)  # Match Claude card
        self.efficiency_bar.setTextVisible(True)
        self.efficiency_bar.setFormat("%p%")
        self.layout.addWidget(self.efficiency_bar)
        
        # Apply Model Usage bar styling
        self._update_efficiency_bar_styling()
        
        # Small spacing
        self.layout.addSpacing(2)
        
        # Usage label only (percentage is in the progress bar)
        self.usage_label = QLabel("0 / 0")
        self.usage_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small'] - 1))
        self.usage_label.setFixedHeight(self.base_font_sizes['small'] + 5)
        self.layout.addWidget(self.usage_label)
        
        
        # Spacing between groups
        self.layout.addSpacing(12)
        
        # GROUP 4: Break-even
        # Break-even info with click handler
        breakeven_layout = QHBoxLayout()
        breakeven_layout.setContentsMargins(0, 0, 0, 0)
        breakeven_label = QLabel('<span style="text-decoration: underline; cursor: pointer;">Break-even:</span>')
        breakeven_label.setTextFormat(Qt.TextFormat.RichText)
        breakeven_label.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px; line-height: {self.base_font_sizes['small'] + 4}px;")
        breakeven_label.setFixedHeight(self.base_font_sizes['small'] + 6)
        breakeven_label.setToolTip("Click for explanation")
        breakeven_label.setCursor(Qt.CursorShape.PointingHandCursor)
        breakeven_label.mousePressEvent = lambda e: self._show_breakeven_explanation()
        breakeven_layout.addWidget(breakeven_label)
        breakeven_layout.addStretch()
        self.breakeven_value_label = QLabel("0%")
        self.breakeven_value_label.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px;")
        self.breakeven_value_label.setFixedHeight(self.base_font_sizes['small'] + 6)
        breakeven_layout.addWidget(self.breakeven_value_label)
        self.layout.addLayout(breakeven_layout)
        
        # Small spacing
        self.layout.addSpacing(2)
        
        self.tokens_needed_label = QLabel("")
        self.tokens_needed_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small'] - 1))
        self.tokens_needed_label.setFixedHeight(self.base_font_sizes['small'] + 5)
        self.layout.addWidget(self.tokens_needed_label)
        
        # Spacing before recommendation
        self.layout.addSpacing(12)
        
        # GROUP 5: Recommendation
        rec_header = QLabel("Recommendation:")
#        rec_header.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px; line-height: #{self.base_font_sizes['small'] + 4}px;")
        rec_header.setStyleSheet(f"font-size: {self.base_font_sizes['small']}px; line-height: {self.base_font_sizes['small'] + 0}px;")
#        rec_header.setFixedHeight(self.base_font_sizes['small'] + 6)
        rec_header.setFixedHeight(self.base_font_sizes['small'] + 1)
        self.layout.addWidget(rec_header)
        
        # Small spacing
#        self.layout.addSpacing(1)
        
        # Recommendation text
        self.recommendation_label = QLabel("")
        self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #4CAF50;")
        self.recommendation_label.setWordWrap(True)
        self.layout.addWidget(self.recommendation_label)
        
        
    def _on_period_changed(self, period: str):
        """Handle period change"""
        self.current_period = period
        # Update efficiency header with period
        if period == "month":
            self.eff_header.setText('<span style="text-decoration: underline; cursor: pointer;">Plan Efficiency</span> (up to today)')
        else:
            self.eff_header.setText('<span style="text-decoration: underline; cursor: pointer;">Plan Efficiency</span> (Last 30 days)')
        self.period_changed.emit(period)
        
    def update_data(self, data: Dict[str, Any]):
        """Update the card with new data"""
        # Extract data
        self.api_cost = data.get('api_cost', 0.0)
        self.subscription_cost = data.get('subscription_cost', 200.0)
        self.tokens_used = data.get('tokens_used', 0)
        self.tokens_available = data.get('tokens_available', 0)
        self.efficiency = data.get('efficiency', 0.0)
        self.breakeven_efficiency = data.get('breakeven_efficiency', 0.0)
        self.overflow_sessions = data.get('overflow_sessions', [])
        self.total_overflow_tokens = data.get('total_overflow_tokens', 0)
        self.session_blocks = data.get('session_blocks', [])
        
        
        # Update costs
        self.api_cost_label.setText(f"${self.api_cost:.0f}")
        self.sub_cost_label.setText(f"${self.subscription_cost:.0f}")
        
        # Clear status label - recommendation section handles all guidance
        self.status_label.setText("")
        self.status_label.hide()
            
        # Update efficiency (percentage shown in progress bar)
        self.efficiency_bar.setValue(int(self.efficiency))
        
        
        # Update usage label
        if self.tokens_available > 0:
            self.usage_label.setText(f"{self._format_tokens(self.tokens_used)} / {self._format_tokens(self.tokens_available)}")
        else:
            self.usage_label.setText("")
        
        # Update break-even
        self.breakeven_value_label.setText(f"{self.breakeven_efficiency:.0f}%")
        
        # Calculate tokens needed
        if self.tokens_available > 0 and self.efficiency < self.breakeven_efficiency:
            tokens_needed = int((self.breakeven_efficiency / 100) * self.tokens_available) - self.tokens_used
            if tokens_needed > 0:
                self.tokens_needed_label.setText(f"Use {self._format_tokens(tokens_needed)} more tokens to break-even")
            else:
                self.tokens_needed_label.setText("")
        else:
            self.tokens_needed_label.setText("")
            
        # Update recommendation
        self._update_recommendation()
    
    def _format_tokens(self, tokens: int) -> str:
        """Format token count for display"""
        if tokens >= 1_000_000:
            return f"{tokens / 1_000_000:.1f}M"
        elif tokens >= 1_000:
            return f"{tokens / 1_000:.0f}k"
        else:
            return str(tokens)
            
    def _show_efficiency_explanation(self):
        """Show explanation dialog for plan efficiency"""
        QMessageBox.information(
            self,
            "Plan Efficiency",
            "Plan Efficiency shows what percentage of your available tokens you've used.\n\n"
            "For 'Up to today', it only counts tokens from sessions that have already occurred, "
            "not the full month's allocation.\n\n"
            "Higher efficiency means you're getting more value from your subscription."
        )
        
    def _show_breakeven_explanation(self):
        """Show explanation dialog for break-even"""
        QMessageBox.information(
            self,
            "Break-even Efficiency",
            "Break-even efficiency is the percentage of available tokens you need to use "
            "for the subscription to cost the same as paying for API tokens directly.\n\n"
            "If your efficiency is above this percentage, the subscription saves you money. "
            "If below, using the API directly would be cheaper."
        )
        
    def _update_recommendation(self):
        """Update subscription recommendation based on usage patterns"""
        # Get current plan from subscription cost
        current_plan = "unknown"
        
        # Get plan costs from config
        all_plans = self.config.config.get('claude_code', {}).get('plans', {})
        for plan_key, plan_info in all_plans.items():
            if plan_info.get('monthly_cost') == self.subscription_cost:
                current_plan = plan_key
                break
            
        logger.info(f"_update_recommendation: current_plan={current_plan}, efficiency={self.efficiency:.1f}%, "
                   f"breakeven={self.breakeven_efficiency:.1f}%, api_cost=${self.api_cost:.2f}")
            
        # Calculate what efficiency would be needed for each plan to break even
        if self.tokens_used > 0:
            # Get available plans from config
            all_plans = self.config.config.get('claude_code', {}).get('plans', {})
            plans = {}
            for plan_key, plan_info in all_plans.items():
                plans[plan_key] = {
                    "cost": plan_info.get("monthly_cost"),
                    "name": plan_info.get("display_name", plan_info.get("name")),
                    "session_limit": plan_info.get("session_token_limit"),
                    "sessions_per_month": plan_info.get("sessions_per_month", 120)
                }
            
            # Determine the most cost-effective option based on actual session overflows
            # The key insight: overflow happens per session, not monthly total
            
            # Calculate overflow tokens for each plan
            plan_overflow_tokens = {}
            
            # Check each plan's overflow based on session blocks
            if hasattr(self, 'session_blocks') and self.session_blocks:
                for plan_key, plan_info in plans.items():
                    session_limit = plan_info.get('session_limit', 220000)
                    overflow_tokens = 0
                    
                    for block in self.session_blocks:
                        if hasattr(block, 'total_tokens') and block.total_tokens > session_limit:
                            overflow_tokens += block.total_tokens - session_limit
                    
                    plan_overflow_tokens[plan_key] = overflow_tokens
                    if overflow_tokens > 0:
                        logger.info(f"{plan_info['name']} overflow: {len(self.session_blocks)} blocks, {overflow_tokens:,} overflow tokens")
            
            # Calculate API costs for overflow tokens
            # Use the actual user's token cost ratio
            if self.tokens_used > 0:
                cost_per_token = self.api_cost / self.tokens_used
            else:
                cost_per_token = 0.00007128  # Default $71.28/M tokens
            
            # Calculate total costs (subscription + overflow) for each plan
            plan_total_costs = {}
            for plan_key, plan_info in plans.items():
                sub_cost = plan_info.get('cost', 0)
                overflow_cost = plan_overflow_tokens.get(plan_key, 0) * cost_per_token
                plan_total_costs[plan_key] = {
                    'subscription': sub_cost,
                    'overflow': overflow_cost,
                    'total': sub_cost + overflow_cost,
                    'has_overflow': overflow_cost > 0
                }
            
            # Calculate what percentage of sessions overflow for each plan
            plan_overflow_percentages = {}
            if hasattr(self, 'session_blocks') and self.session_blocks:
                total_sessions = len(self.session_blocks)
                for plan_key, plan_info in plans.items():
                    session_limit = plan_info.get('session_limit', 220000)
                    overflow_sessions = sum(1 for block in self.session_blocks 
                                          if hasattr(block, 'total_tokens') and block.total_tokens > session_limit)
                    plan_overflow_percentages[plan_key] = (overflow_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # Find the best option by comparing all costs
            best_option = "api"
            best_cost = self.api_cost
            best_plan_key = None
            
            # Check each plan's total cost
            for plan_key, costs in plan_total_costs.items():
                # Skip Pro + API if more than 50% of sessions would overflow
                if plan_key == "pro" and costs['has_overflow'] and plan_overflow_percentages.get('pro', 0) > 50:
                    logger.info(f"Skipping Pro + API: {plan_overflow_percentages.get('pro', 0):.0f}% of sessions overflow")
                    continue
                    
                # Skip any hybrid if overflow cost is more than 50% of total
                if costs['has_overflow'] and costs['overflow'] > costs['subscription']:
                    logger.info(f"Skipping {plan_key} hybrid: overflow cost (${costs['overflow']:.0f}) > subscription (${costs['subscription']:.0f})")
                    continue
                
                if costs['total'] < best_cost:
                    best_cost = costs['total']
                    best_plan_key = plan_key
                    if costs['has_overflow']:
                        best_option = f"{plan_key}_hybrid"
                    else:
                        best_option = plan_key
            
            logger.info(f"Best option: {best_option} at ${best_cost:.0f}/mo")
                    
            # Make recommendation based on usage patterns
            # First check for extreme efficiency cases
            if self.efficiency >= 95:
                # Near or over limit
                if current_plan == "max20":
                    self.recommendation_label.setText("Max20x + API for overflow")
                    self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #4CAF50; line-height: {self.base_font_sizes['small'] + 3}px;")
                else:
                    self.recommendation_label.setText("Upgrade to Max20x")
                    self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #ff6b35; line-height: {self.base_font_sizes['small'] + 3}px;")
                    
            elif self.efficiency >= 85:
                # Very high usage but within limits
                if current_plan == "max20":
                    self.recommendation_label.setText("Max20x is optimal")
                    self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #4CAF50; line-height: {self.base_font_sizes['small'] + 3}px;")
                else:
                    self.recommendation_label.setText("Consider Max20x")
                    self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #ff6b35; line-height: {self.base_font_sizes['small'] + 3}px;")
                    
            else:
                # Normal usage - recommend based on cost comparison
                if best_option == "api":
                    # API is cheapest
                    savings = self.subscription_cost - self.api_cost
                    if savings > 50:
                        self.recommendation_label.setText(f"API saves at least ${savings:.0f}/mo")
                    else:
                        self.recommendation_label.setText(f"API only (~${self.api_cost:.0f}/mo)")
                    self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #ff6b35; line-height: {self.base_font_sizes['small'] + 3}px;")
                    
                elif "_hybrid" in best_option:
                    # Hybrid recommendation (any plan + API)
                    plan_key = best_option.replace("_hybrid", "")
                    plan_name = plans.get(plan_key, {}).get('name', plan_key)
                    current_cost = self.subscription_cost
                    savings = current_cost - best_cost
                    
                    if savings > 50:
                        self.recommendation_label.setText(f"{plan_name} + API (~${best_cost:.0f}/mo) saves ${savings:.0f}")
                    else:
                        self.recommendation_label.setText(f"{plan_name} + API (~${best_cost:.0f}/mo)")
                    self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #ff6b35; line-height: {self.base_font_sizes['small'] + 3}px;")
                    
                elif best_plan_key and best_plan_key != current_plan and "_hybrid" not in best_option:
                    # Different plan is better (no overflow)
                    best_plan_name = plans[best_plan_key]['name']
                    current_cost = self.subscription_cost
                    savings = current_cost - best_cost
                    
                    if savings > 50:
                        self.recommendation_label.setText(f"{best_plan_name} (~${best_cost:.0f}/mo) saves ${savings:.0f}")
                    else:
                        # Determine if upgrade or downgrade
                        current_plan_cost = plans.get(current_plan, {}).get('cost', self.subscription_cost)
                        best_plan_cost = plans.get(best_plan_key, {}).get('cost', 0)
                        
                        if best_plan_cost > current_plan_cost:
                            self.recommendation_label.setText(f"Upgrade to {best_plan_name} (~${best_plan_cost:.0f}/mo)")
                        else:
                            self.recommendation_label.setText(f"Downgrade to {best_plan_name} (~${best_plan_cost:.0f}/mo)")
                    self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #ff6b35; line-height: {self.base_font_sizes['small'] + 3}px;")
                    
                    
                else:
                    # Current plan is already optimal
                    plan_name = plans.get(current_plan, {}).get('name', 'Current plan')
                    if self.efficiency >= self.breakeven_efficiency:
                        self.recommendation_label.setText(f"{plan_name} is optimal")
                        self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #4CAF50; line-height: {self.base_font_sizes['small'] + 3}px;")
                    else:
                        # Below breakeven but still on best plan for their usage
                        self.recommendation_label.setText(f"{plan_name} is best for your usage")
                        self.recommendation_label.setStyleSheet(f"font-size: {self.base_font_sizes['small'] - 1}px; color: #4CAF50; line-height: {self.base_font_sizes['small'] + 3}px;")
        else:
            # No usage data yet
            self.recommendation_label.setText("Gathering usage data...")
            self.recommendation_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small'] - 1) + f"; line-height: {self.base_font_sizes['small'] + 3}px;")
            
    def _update_efficiency_bar_styling(self):
        """Update efficiency bar styling to match MODEL USAGE bar"""
        # Match Model Usage bar EXACTLY - blue progress on light gray background
        self.efficiency_bar.setStyleSheet(f"""
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
        
    def update_theme(self):
        """Update the card when theme changes"""
        super().update_theme()  # Call parent to update card border
        
        # Get theme manager
        from ..theme_manager import ThemeManager
        theme_manager = ThemeManager()
        
        # Update all secondary text labels
        self.api_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small']) + f"; line-height: {self.base_font_sizes['small'] + 4}px;")
        self.sub_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small']) + f"; line-height: {self.base_font_sizes['small'] + 4}px;")
        self.usage_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small'] - 1))
        self.tokens_needed_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small'] - 1))
        
        # Update recommendation label if it's showing "Gathering usage data..."
        if "Gathering usage data" in self.recommendation_label.text():
            self.recommendation_label.setStyleSheet(theme_manager.get_secondary_text_style(self.base_font_sizes['small'] - 1) + f"; line-height: {self.base_font_sizes['small'] + 3}px;")
