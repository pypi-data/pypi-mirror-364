# Claude Dash

<p align="center">
  <strong>Monitor your Claude usage and subscription value in real-time</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#understanding-the-metrics">Understanding Metrics</a> •
  <a href="#development">Development</a> •
  <a href="#building">Building</a>
</p>

## Overview

Claude Dash is a desktop application that helps Claude users track their usage and understand the value of their subscription. It provides real-time monitoring of your Claude Code sessions, intelligent subscription vs API cost analysis, and actionable recommendations.

**Important**: Claude Dash analyzes your actual usage patterns, not theoretical maximums. The efficiency metrics show how well you're using the sessions you actually start, providing a realistic view of your subscription value.

## Features

### Current Session Monitoring
- **Real-Time Token Tracking**: Live updates of your current Claude session
- **Visual Progress Bars**: Token usage, time remaining, and model breakdown
- **Smart Predictions**: Know when your session will end or tokens run out
- **Burn Rate Analysis**: See your current token usage rate ($/min)

### Value Analysis
- **Subscription vs API Comparison**: Compare your usage costs against direct API pricing
- **Realistic Efficiency Metrics**: Based on sessions you actually use, not 24/7 theoretical usage
- **Smart Recommendations**: Get actionable advice on whether to keep your subscription or switch to API
- **Multiple Time Periods**: Analyze current month and last 30 days

### Technical Features
- **Almost No Configuration**: No API keys needed - reads directly from Claude's local data
- **Opus 4 Pricing Support**: Uses current Claude 4 Opus pricing ($15/$75 per million tokens)
- **Cache Token Handling**: Correctly excludes cache tokens from subscription limit calculations
- **Personalized Analytics**: Break-even calculations use your actual input/output ratio, not generic assumptions
- **Auto-refresh**: Updates every 30 seconds with fresh data
- **Theme Support**: 13 built-in themes including Dark, Light, Solarized, Nord, Dracula, and more
- **UI Scaling**: Adjustable interface size (75%-200%) for different display sizes and preferences

## Installation

### Requirements
- Python 3.8 or higher
- Claude Code installed and used on your system

### Install with uvx (Recommended)

The easiest way to run Claude Dash is with [uvx](https://github.com/astral-sh/uv):

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh  # On macOS/Linux
# Or see https://github.com/astral-sh/uv for other platforms

# Run Claude Dash (once published to PyPI)
uvx claude-dash
```

### Install with pip

```bash
# Once published to PyPI
pip install claude-dash
claude-dash
```

### Install from source

1. **Clone the repository:**
```bash
git clone https://github.com/mhcoen/claude-dash.git
cd claude-dash
```

2. **Install in development mode:**
```bash
pip install -e .
```

4. **Run Claude Dash:**
```bash
python src/main.py
```

## Usage

Claude Dash automatically detects your Claude usage by reading from Claude Code's local data files. Launch the app and it will:

1. **Find your current session** and display real-time progress
2. **Calculate actual costs** for your usage patterns
3. **Compare subscription vs API** costs with accurate Opus 4 pricing
4. **Provide recommendations** based on your actual usage efficiency
5. **Update continuously** with fresh data every 30 seconds

### Main Interface

The app has two main cards:

#### Claude Code Card (Left)
- **Current session tokens** and time progress
- **Model usage breakdown** (Opus vs Sonnet)
- **Burn rate** showing current spending rate
- **Session predictions** for when tokens/time will run out

#### Value Analysis Card (Right)
- **Cost comparison** between subscription and API usage
- **Efficiency metrics** based on your actual session usage
- **Break-even analysis** showing what efficiency you need
- **Recommendations** for subscription vs API usage

### Keyboard Shortcuts
- **T**: Open theme selector
- **↑/↓**: Navigate themes (when selector is open)
- **Enter**: Select theme (when selector is open)
- **ESC**: Cancel theme selection and close selector
- **Ctrl/Cmd +**: Increase UI scale by 25%
- **Ctrl/Cmd -**: Decrease UI scale by 25%
- **Ctrl/Cmd 0**: Reset UI scale to 100%

## Understanding the Metrics

### Efficiency Calculation
**Important**: The efficiency metric shows how much of your *actually started sessions* you're using, not a theoretical 24/7 maximum.

- **What it measures**: (Tokens used) ÷ (Tokens available in sessions you started) × 100
- **Why this matters**: Gives a realistic view of your usage patterns without penalizing you for not coding at 3am
- **Example**: If you start 78 sessions in a month and use 1.3M tokens, your efficiency is based on those 78 sessions (17.2M tokens available), not the theoretical maximum of ~144 sessions if you were coding 24/7

### Cost Analysis
- **API Cost**: Only includes input/output tokens that count against subscription limits
- **Cache Costs**: Shown separately as they don't count against subscription limits
- **Opus 4 Pricing**: Uses current rates ($15/M input, $75/M output)
- **Break-even**: The efficiency level where subscription cost equals API cost
  - Personalized calculation based on your actual input/output token ratio
  - Heavy summarization users (more input) will have lower costs per token
  - Heavy generation users (more output) will have higher costs per token
  - No generic assumptions - uses your real usage data for accuracy

### Recommendations
- **"API saves $X/mo"**: Your usage is low enough that API would be cheaper
- **"Max5x is optimal"**: Your usage fits better with Max5 subscription
- **"Max20x is optimal"**: Your usage justifies the Max20 subscription
- **Cost thresholds**: API < $100, Max5 $100-200, Max20 $200+

**Important**: Subscriptions provide access to claude.ai web interface, which includes features not available via API:
- Web-based chat interface for casual use
- File uploads and document analysis
- Image viewing and analysis capabilities
- Web browsing and research features
- Project organization and conversation history
- No need to manage API keys or billing

These benefits may justify a subscription even if API-only would be cheaper for your coding usage.

### How Recommendations Work

The recommendations aren't just about finding the absolute cheapest option, but about finding the most practical and convenient solution for your usage patterns.

The recommendation system analyzes your actual session patterns to suggest the most practical plan:

1. **Session Analysis**: Examines each of your sessions to see which would exceed plan limits:
   - Pro: 19k tokens per session
   - Max5x: 88k tokens per session
   - Max20x: 220k tokens per session

2. **Hybrid Options**: Considers subscription + API combinations (e.g., "Pro + API")
   - Calculates overflow tokens for sessions exceeding plan limits
   - Adds API costs for those overflow tokens to the base subscription cost

3. **Practical Filters**: Avoids impractical recommendations:
   - **Won't suggest Pro + API** if >50% of your sessions exceed Pro's 19k limit
   - **Won't suggest any hybrid** if API overflow costs more than the subscription itself
   - This prevents constant API charges and unpredictable bills
   - Also considers the **inconvenience** of frequently switching between subscription and API modes

4. **Example**: If you have 80 sessions averaging 17.7k tokens:
   - Pro + API might be mathematically cheapest (~$70/mo)
   - But if 60 sessions exceed 19k tokens, you'd constantly need to switch to API mode
   - System recommends Max5x ($100/mo) for predictable costs and seamless experience
   - No interruptions, no mode switching, no surprise charges

## Configuration

Claude Dash stores configuration in `~/.claude-dash/`. On first run, default configuration files are automatically created from templates in `src/config/defaults/`.

### Setting Your Subscription Plan

**Important**: You must set your Claude subscription plan in the configuration file for accurate analysis. The app defaults to Max20x, but you should update this to match your actual subscription.

To change your subscription plan:
1. Open `~/.claude-dash/config.json`
2. Find the `"subscription_plan"` field under `"claude_code"`
3. Set it to one of: `"pro"`, `"max5"`, or `"max20"`

### Main Configuration (`config.json`)
Contains subscription settings, UI preferences, and analysis parameters:
```json
{
  "claude_code": {
    "subscription_plan": "max20",  // ← Change this to your plan: "pro", "max5", or "max20"
    "plans": {
      "pro": {
        "name": "Pro",
        "monthly_cost": 20,
        "session_token_limit": 19000,
        "session_cost_limit": 18.0,
        "display_name": "Claude Pro",
        "sessions_per_month": 5
      },
      "max5": {
        "name": "Max 5×",
        "monthly_cost": 100,
        "session_token_limit": 88000,
        "session_cost_limit": 35.0,
        "display_name": "Claude Max 5×",
        "sessions_per_month": 30
      },
      "max20": {
        "name": "Max 20×",
        "monthly_cost": 200,
        "session_token_limit": 220000,
        "session_cost_limit": 140.0,
        "display_name": "Claude Max 20×",
        "sessions_per_month": 120
      }
    },
    "session_duration_hours": 5,
    "session_gap_minutes": 5
  },
  "ui": {
    "theme": "dark",
    "refresh_interval_seconds": 30,
    "font_sizes": {
      "tiny": 10,
      "small": 12,
      "medium": 14,
      "large": 16,
      "huge": 20
    }
  },
  "analysis": {
    "cost_thresholds": {
      "api_optimal": 100,
      "max5_optimal": 200
    },
    "quick_start_hours": 24,
    "cache_duration_seconds": 30
  },
  "paths": {
    "claude_data": "~/.claude/projects",
    "logs": "~/.claude-dash/logs"
  },
  "themes": {
    "light": {
      "name": "Light",
      "background": "#f5f5f5",
      "card_background": "white",
      "text_primary": "#000000",
      "text_secondary": "#666666",
      "border": "#e0e0e0",
      "accent": "#ff6b35"
    },
    "dark": {
      "name": "Dark",
      "background": "#1e1e1e",
      "card_background": "#2d2d2d",
      "text_primary": "#ffffff",
      "text_secondary": "#b0b0b0",
      "border": "#404040",
      "accent": "#ff8a65"
    }
  },
  "default_theme": "dark"
}
```

### Pricing Configuration (`pricing.json`)
Contains model pricing - easily update when rates change:
```json
{
  "last_updated": "2025-01-23",
  "currency": "USD",
  "per_million_tokens": true,
  "models": {
    "claude-opus-4-20250514": {
      "name": "Claude 4 Opus",
      "input": 15.0,
      "output": 75.0,
      "cache_creation": 18.75,
      "cache_read": 1.5
    },
    "claude-3.5-sonnet": {
      "name": "Claude 3.5 Sonnet",
      "input": 3.0,
      "output": 15.0,
      "cache_creation": 3.75,
      "cache_read": 0.3
    },
    "claude-sonnet-4-20250514": {
      "name": "Claude 4 Sonnet",
      "input": 3.0,
      "output": 15.0,
      "cache_creation": 3.75,
      "cache_read": 0.3
    },
    "default": {
      "name": "Default",
      "input": 3.0,
      "output": 15.0,
      "cache_creation": 3.75,
      "cache_read": 0.3
    }
  }
}
```

### Updating Configuration
- Edit files directly in `~/.claude-dash/`
- Changes take effect on next app restart
- To reset to defaults, delete the config files and restart the app

## How It Works

Claude Dash reads usage data from Claude Code's local JSONL files in `~/.claude/projects/`:

1. **Session Detection**: Groups usage into 5-hour session blocks
2. **Token Counting**: Tracks input/output tokens (cache tokens shown separately)
3. **Cost Calculation**: Uses real Opus 4 API pricing for comparisons
4. **Efficiency Analysis**: Based on sessions actually started, not theoretical maximum
5. **Smart Updates**: Preserves session data during periodic refreshes

### Data Retention
Claude Code purges logs after ~30 days on a rolling basis. Claude Dash handles this by:
- Loading sufficient historical data for accurate analysis
- Focusing on recent usage patterns for recommendations
- Providing month-to-date and 30-day analysis options

## Development

For development setup and contribution guidelines, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Building

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --name="Claude Dash" --windowed --onefile src/main.py
```

The executable will be created in the `dist/` directory.

## Troubleshooting

### Common Issues

**"No Claude data found"**
- Ensure Claude Code is installed and you've used it recently
- Check that `~/.claude/projects/` contains JSONL files

**"Efficiency shows 0%"**
- This usually means no recent sessions were found
- Try using Claude Code and wait a few minutes for data to appear

**"API cost seems wrong"**
- Verify you're using Opus 4 (pricing assumes current Claude 4 rates)
- Remember cache costs are shown separately and don't count against limits

## Contributing

Contributions welcome! For major changes, please open an issue first.

## Author

**Michael Coen**  
Email: [mhcoen@gmail.com](mailto:mhcoen@gmail.com), [mhcoen@alum.mit.edu](mailto:mhcoen@alum.mit.edu)

## Acknowledgments

Special thanks to [Maciek Dymarczyk](https://github.com/Maciek-roboblog) for his [Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) project. His work was instrumental in understanding how Claude Code measures usage and how to read and parse Claude's log files. This project builds heavily upon his work and would not exist without it.

Development of this work was assisted by Claude Code, Gemini Code Assist, Warp, GPT-o3, and Zen-MCP.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Disclaimer

Claude Dash is an independent project and is not affiliated with or endorsed by Anthropic. It analyzes local Claude Code usage data to provide insights about subscription value.

**NO WARRANTY**: This software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

The usage calculations and recommendations are estimates based on local data analysis and may not reflect actual billing or usage limits. Always verify important metrics with your official Claude account dashboard.
