"""
Utilities for testing
"""
import tempfile
import json
from pathlib import Path
from datetime import datetime


def create_test_environment():
    """Create a complete test environment"""
    temp_dir = tempfile.mkdtemp()
    
    # Create Claude data directory
    claude_dir = Path(temp_dir) / '.claude' / 'projects'
    claude_dir.mkdir(parents=True)
    
    # Create config directory
    config_dir = Path(temp_dir) / '.claude-dash'
    config_dir.mkdir(parents=True)
    
    # Create sample config
    config = {
        "claude_code": {
            "subscription_plan": "max20",
            "plans": {
                "max5": {
                    "monthly_cost": 100,
                    "session_token_limit": 88000,
                    "sessions_per_month": 30
                },
                "max20": {
                    "monthly_cost": 200,
                    "session_token_limit": 220000,
                    "sessions_per_month": 120
                }
            }
        },
        "pricing": {
            "models": {
                "claude-opus-4-20250514": {
                    "input": 15.0,
                    "output": 75.0,
                    "cache_creation": 18.75,
                    "cache_read": 1.5
                }
            }
        },
        "ui": {
            "theme": "dark",
            "refresh_interval_seconds": 30
        }
    }
    
    with open(config_dir / 'config.json', 'w') as f:
        json.dump(config, f)
        
    return temp_dir, claude_dir, config_dir


def create_sample_jsonl_data(claude_dir, num_entries=10):
    """Create sample JSONL data for testing"""
    entries = []
    base_time = datetime.utcnow()
    
    for i in range(num_entries):
        timestamp = base_time.replace(minute=i*5)
        entry = {
            'timestamp': timestamp.isoformat() + 'Z',
            'model': 'claude-opus-4-20250514',
            'input_tokens': 100 + i*10,
            'output_tokens': 200 + i*20,
            'cache_creation_tokens': 10,
            'cache_read_tokens': 20
        }
        entries.append(entry)
        
    # Write to file
    with open(claude_dir / 'test_data.jsonl', 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
            
    return entries