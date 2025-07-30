"""
Claude Code usage reader for Anthropic usage data
Reads JSONL files from ~/.claude/projects/ to get Claude usage
"""
import os
import json
import glob
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Callable
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..core.config_loader import get_config

logger = logging.getLogger(__name__)


# SessionBlock class to match Claude Monitor's structure
class SessionBlock:
    """Session block data structure matching Claude Monitor"""
    def __init__(self, start_time: datetime, end_time: datetime, block_id: str):
        self.id = block_id
        self.start_time = start_time
        self.end_time = end_time
        self.actual_end_time = None
        self.is_active = False
        self.is_gap = False
        
        # Token counts
        self.input_tokens = 0
        self.output_tokens = 0
        self.cache_creation_tokens = 0
        self.cache_read_tokens = 0
        self.total_tokens = 0  # Total tokens that count toward limits (TBD)
        
        # Aggregated data
        self.cost_usd = 0.0
        self.entries = []
        self.models = []
        self.per_model_stats = {}
        self.sent_messages_count = 0
        
    @property
    def duration_minutes(self) -> float:
        """Get duration of block in minutes"""
        if self.is_active:
            end = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            end = self.actual_end_time or self.end_time
        return (end - self.start_time).total_seconds() / 60.0


class ClaudeCodeReader:
    """Reads Claude Code usage from JSONL files"""
    
    def __init__(self):
        # Load configuration
        self.config = get_config()
        
        # Use configured claude directory
        self.claude_dir = self.config.get_claude_data_path()
        
        # Get session duration from config
        claude_config = self.config.config.get('claude_code', {})
        self.session_duration_hours = claude_config.get('session_duration_hours', 5)
        
        self._executor = ThreadPoolExecutor(max_workers=1)
        
        # Cache for session blocks
        self._session_blocks = []
        self._blocks_last_updated = None
        
        # Load timing settings from config
        analysis_config = self.config.get_analysis_config()
        self._blocks_cache_duration = timedelta(seconds=analysis_config.get("cache_duration_seconds", 30))
        self._quick_start_hours = 24
        self._full_data_loaded = False
        
    def get_claude_dir(self) -> Path:
        """Return the path to the Claude projects directory."""
        return self.claude_dir
        
    def _round_to_hour(self, timestamp: datetime) -> datetime:
        """Round timestamp to the nearest full hour (for session start)"""
        return timestamp.replace(minute=0, second=0, microsecond=0)
    
    def _load_usage_entries(self, hours_back: Optional[int] = None) -> List[Dict]:
        """Load and deduplicate JSONL entries"""
        entries = []
        seen_hashes: Set[str] = set()
        
        cutoff_time = None
        if hours_back:
            cutoff_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours_back)
        
        # Find all JSONL files
        jsonl_files = list(self.claude_dir.rglob("*.jsonl"))
        logger.info(f"Loading entries from {len(jsonl_files)} JSONL files (hours_back={hours_back})")
        
        files_read = 0
        for file_path in jsonl_files:
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue
                            
                        try:
                            entry = json.loads(line)
                            
                            # Create deduplication hash
                            message = entry.get('message', {})
                            message_id = entry.get('message_id') or message.get('id')
                            request_id = entry.get('requestId') or entry.get('request_id')
                            
                            if message_id and request_id:
                                unique_hash = f"{message_id}:{request_id}"
                                if unique_hash in seen_hashes:
                                    continue
                                seen_hashes.add(unique_hash)
                            
                            # Parse timestamp
                            timestamp_str = entry.get('timestamp')
                            if not timestamp_str:
                                continue
                            
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if timestamp.tzinfo:
                                timestamp = timestamp.replace(tzinfo=None)
                            
                            # Apply time filter
                            if cutoff_time and timestamp < cutoff_time:
                                continue
                            
                            # Check if entry has usage data
                            usage = message.get('usage', {})
                            if not usage:
                                continue
                            
                            # Must have some tokens
                            if not any([
                                usage.get('input_tokens', 0) > 0,
                                usage.get('output_tokens', 0) > 0,
                                usage.get('cache_creation_input_tokens', 0) > 0,
                                usage.get('cache_read_input_tokens', 0) > 0
                            ]):
                                continue
                            
                            # Store processed entry
                            entries.append({
                                'timestamp': timestamp,
                                'model': message.get('model', 'unknown'),
                                'usage': usage,
                                'message_id': message_id,
                                'request_id': request_id,
                                'raw': entry
                            })
                            
                        except:
                            continue
                
                files_read += 1
                            
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
        
        # Sort by timestamp
        entries.sort(key=lambda e: e['timestamp'])
        
        logger.info(f"Successfully read {files_read} files, found {len(entries)} entries with usage data")
        
        return entries
    
    def _create_session_blocks(self, entries: List[Dict]) -> List[SessionBlock]:
        """Transform entries into session blocks"""
        if not entries:
            return []
        
        blocks = []
        current_block = None
        session_duration = timedelta(hours=self.session_duration_hours)
        
        for entry in entries:
            timestamp = entry['timestamp']
            
            # Check if we need a new block
            if current_block is None or timestamp >= current_block.end_time:
                # Create new block
                start_time = self._round_to_hour(timestamp)
                end_time = start_time + session_duration
                block_id = start_time.isoformat()
                
                current_block = SessionBlock(start_time, end_time, block_id)
                blocks.append(current_block)
            
            # Add entry to current block
            self._add_entry_to_block(current_block, entry)
        
        # Finalize blocks
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for block in blocks:
            if block.entries:
                block.actual_end_time = block.entries[-1]['timestamp']
                block.sent_messages_count = len(block.entries)
                
                # Mark as active if still ongoing
                if block.end_time > now:
                    block.is_active = True
        
        return blocks
    
    def _add_entry_to_block(self, block: SessionBlock, entry: Dict) -> None:
        """Add entry to block and aggregate data"""
        usage = entry['usage']
        model = entry['model']
        
        # Store entry for burn rate calculation (only once)
        block.entries.append(entry)
        
        # Update token counts
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        cache_creation_tokens = usage.get('cache_creation_input_tokens', 0)
        cache_read_tokens = usage.get('cache_read_input_tokens', 0)
        
        block.input_tokens += input_tokens
        block.output_tokens += output_tokens
        block.cache_creation_tokens += cache_creation_tokens
        block.cache_read_tokens += cache_read_tokens
        # Update total tokens - only input + output count toward limits
        block.total_tokens = block.input_tokens + block.output_tokens
        
        # Calculate cost using config pricing
        pricing = self.config.get_model_pricing(model)
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        cache_creation_cost = (cache_creation_tokens / 1_000_000) * pricing['cache_creation']
        cache_read_cost = (cache_read_tokens / 1_000_000) * pricing['cache_read']
        item_cost = input_cost + output_cost + cache_creation_cost + cache_read_cost
        
        block.cost_usd += item_cost
        
        # Track models
        if model not in block.models:
            block.models.append(model)
        
        # Update per-model stats
        if model not in block.per_model_stats:
            block.per_model_stats[model] = {
                'input_tokens': 0,
                'output_tokens': 0,
                'cache_creation_tokens': 0,
                'cache_read_tokens': 0,
                'cost_usd': 0.0,
                'entries_count': 0
            }
        
        stats = block.per_model_stats[model]
        stats['input_tokens'] += input_tokens
        stats['output_tokens'] += output_tokens
        stats['cache_creation_tokens'] += cache_creation_tokens
        stats['cache_read_tokens'] += cache_read_tokens
        stats['cost_usd'] += item_cost
        stats['entries_count'] += 1
    
    def _update_session_blocks(self, force_refresh: bool = False, hours_back: Optional[int] = None) -> None:
        """Update session blocks cache if needed
        
        Args:
            force_refresh: Force refresh even if cache is valid
            hours_back: Override hours to load (None = use default behavior)
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Check if cache is still valid
        if not force_refresh and self._blocks_last_updated and hours_back is None:
            if now - self._blocks_last_updated < self._blocks_cache_duration:
                return
        
        # Determine how much data to load
        if hours_back is not None:
            # Explicit hours requested (e.g., for month calculation)
            entries = self._load_usage_entries(hours_back=hours_back)
            logger.info(f"Loading {hours_back} hours of data for session blocks")
            # Create fresh blocks for explicit requests
            self._session_blocks = self._create_session_blocks(entries)
        elif not self._full_data_loaded:
            # First load - quick start with 24 hours
            entries = self._load_usage_entries(hours_back=self._quick_start_hours)
            self._full_data_loaded = True
            # Create initial blocks
            self._session_blocks = self._create_session_blocks(entries)
        else:
            # For updates, preserve existing blocks and only update with new data
            # Keep at least 24 hours of data to ensure current session is complete
            cutoff_time = now - timedelta(hours=24)
            
            # Remove blocks older than 24 hours (except active ones)
            self._session_blocks = [b for b in self._session_blocks 
                                  if b.end_time >= cutoff_time or b.is_active]
            
            # Load only recent entries to check for updates
            recent_entries = self._load_usage_entries(hours_back=1)
            
            if recent_entries:
                # Find the latest timestamp we already have
                latest_existing = max((e['timestamp'] for b in self._session_blocks 
                                     for e in b.entries), default=None)
                
                # Only process truly new entries
                new_entries = [e for e in recent_entries 
                             if latest_existing is None or e['timestamp'] > latest_existing]
                
                if new_entries:
                    # Add new entries to existing blocks or create new ones
                    self._merge_new_entries(new_entries)
                    logger.debug(f"Added {len(new_entries)} new entries to session blocks")
        
        self._blocks_last_updated = now
        
        # Log update summary
        total_entries = sum(len(b.entries) for b in self._session_blocks)
        logger.info(f"Updated session blocks: {len(self._session_blocks)} blocks, "
                    f"{total_entries} total entries")
        
        # Log total tokens for debugging
        total_tokens = sum(b.total_tokens for b in self._session_blocks)
        logger.info(f"Total tokens across all blocks: {total_tokens:,}")
    
    def _merge_new_entries(self, new_entries: List[Dict]) -> None:
        """Merge new entries into existing session blocks"""
        SESSION_GAP_MINUTES = 5
        
        for entry in new_entries:
            timestamp = entry['timestamp']
            
            # Find the appropriate block for this entry
            added = False
            for block in self._session_blocks:
                # Check if entry belongs to this block
                if (block.start_time <= timestamp <= block.end_time or
                    (block.is_active and timestamp >= block.start_time and 
                     timestamp <= block.start_time + timedelta(hours=5))):
                    # Add to existing block
                    self._add_entry_to_block(block, entry)
                    
                    # Update block end time if needed
                    if timestamp > block.end_time:
                        block.end_time = timestamp
                        # duration_minutes is a property, not an attribute - no need to set it
                    
                    added = True
                    break
            
            # If not added to existing block, check if we need a new block
            if not added:
                # Check if this is close enough to extend an existing block
                for block in self._session_blocks:
                    time_since_last = (timestamp - block.end_time).total_seconds() / 60
                    if 0 < time_since_last <= SESSION_GAP_MINUTES:
                        # Extend existing block
                        self._add_entry_to_block(block, entry)
                        block.end_time = timestamp
                        # duration_minutes is a property, not an attribute - no need to set it
                        added = True
                        break
                
                # If still not added, create a new block
                if not added:
                    # Create a new block with proper constructor arguments
                    block_id = timestamp.isoformat()
                    new_block = SessionBlock(
                        start_time=timestamp,
                        end_time=timestamp + timedelta(hours=self.session_duration_hours),
                        block_id=block_id
                    )
                    self._add_entry_to_block(new_block, entry)
                    self._session_blocks.append(new_block)
                    
                    # Sort blocks by start time
                    self._session_blocks.sort(key=lambda b: b.start_time)
        
        # Update active status for the last block
        if self._session_blocks:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            last_block = self._session_blocks[-1]
            # A block is active if it's within the 5-hour window and had recent activity
            if (now - last_block.start_time).total_seconds() < 5 * 3600:
                time_since_last_entry = (now - last_block.end_time).total_seconds() / 60
                if time_since_last_entry < 10:  # Activity within last 10 minutes
                    last_block.is_active = True
                else:
                    last_block.is_active = False
    
    def get_token_rate_history(self, session_start: datetime, interval_minutes: int = 5) -> List[int]:
        """
        Calculate token usage rates from session history.
        Returns a list of token counts added in each interval.
        """
        # This is now calculated from blocks
        return []

    def _get_current_block(self) -> Optional[SessionBlock]:
        """Get the current active session block"""
        self._update_session_blocks()
        
        for block in self._session_blocks:
            if block.is_active:
                return block
        
        # If no active block, return the most recent one
        if self._session_blocks:
            return self._session_blocks[-1]
        
        return None
    
    def calculate_hourly_burn_rate(self) -> float:
        """
        Calculate burn rate based on recent activity.
        Returns tokens per minute.
        """
        logger.info("Calculating hourly burn rate...")
        
        # Update blocks to get recent data
        self._update_session_blocks()
        
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        one_hour_ago = now - timedelta(hours=1)
        
        # Count tokens from ALL blocks in the last hour, not just active ones
        hourly_input = 0
        hourly_output = 0
        entries_in_hour = 0
        earliest_entry = None
        latest_entry = None
        
        # Check all recent blocks
        for block in self._session_blocks:
            # Skip blocks that ended more than an hour ago
            if block.end_time < one_hour_ago and not block.is_active:
                continue
                
            for entry in block.entries:
                if entry['timestamp'] >= one_hour_ago:
                    usage = entry['usage']
                    hourly_input += usage.get('input_tokens', 0)
                    hourly_output += usage.get('output_tokens', 0)
                    entries_in_hour += 1
                    
                    # Track time range
                    if earliest_entry is None or entry['timestamp'] < earliest_entry:
                        earliest_entry = entry['timestamp']
                    if latest_entry is None or entry['timestamp'] > latest_entry:
                        latest_entry = entry['timestamp']
        
        hourly_tokens = hourly_input + hourly_output
        
        # If no entries in the last hour, try last 2 hours
        if entries_in_hour == 0:
            logger.info("No entries in last hour, checking last 2 hours...")
            two_hours_ago = now - timedelta(hours=2)
            
            for block in self._session_blocks:
                if block.end_time < two_hours_ago and not block.is_active:
                    continue
                    
                for entry in block.entries:
                    if entry['timestamp'] >= two_hours_ago:
                        usage = entry['usage']
                        hourly_input += usage.get('input_tokens', 0)
                        hourly_output += usage.get('output_tokens', 0)
                        entries_in_hour += 1
                        
                        if earliest_entry is None or entry['timestamp'] < earliest_entry:
                            earliest_entry = entry['timestamp']
                        if latest_entry is None or entry['timestamp'] > latest_entry:
                            latest_entry = entry['timestamp']
            
            hourly_tokens = hourly_input + hourly_output
        
        # If still no entries, return 0
        if entries_in_hour == 0 or earliest_entry is None or latest_entry is None:
            logger.info("No recent entries for burn rate calculation")
            return 0.0
        
        # Calculate actual time span of entries
        time_span_minutes = (latest_entry - earliest_entry).total_seconds() / 60.0
        
        # Need at least 5 minutes of data
        if time_span_minutes < 5:
            # If we have some tokens but less than 5 minutes, extrapolate
            if hourly_tokens > 0 and time_span_minutes > 1:
                tokens_per_minute = hourly_tokens / time_span_minutes
                logger.info(f"Extrapolating burn rate from {time_span_minutes:.1f} minutes: {tokens_per_minute:.1f} tokens/min")
                return tokens_per_minute
            else:
                logger.info(f"Not enough time span for burn rate: only {time_span_minutes:.1f} minutes")
                return 0.0
        
        tokens_per_minute = hourly_tokens / time_span_minutes
        
        logger.info(f"Hourly burn rate: {hourly_tokens} tokens over {time_span_minutes:.1f} min = {tokens_per_minute:.1f} tokens/min")
        
        return tokens_per_minute
    
    
    def get_5hour_window_tokens(self) -> int:
        """Get tokens for the current 5-hour window (matches Claude's billing window)"""
        # Get current block
        current_block = self._get_current_block()
        if not current_block:
            return 0
        
        # Return ALL tokens (including cache) as that's what counts toward the limit
        return current_block.total_tokens
    
    def get_live_output_tokens(self) -> int:
        """Get output tokens for the last 60 minutes (matches Claude UI)"""
        # Get current block
        current_block = self._get_current_block()
        if not current_block or not current_block.is_active:
            return 0
        
        # For simplicity, return output tokens from current block
        # (Claude UI likely shows a rolling 60-minute window, but block-based is simpler)
        return current_block.output_tokens
    
    def get_usage_data(self, since_date: Optional[datetime] = None) -> Dict:
        """Get Claude usage data from session blocks"""
        # Update blocks
        self._update_session_blocks()
        
        # Filter blocks by date if needed
        blocks = self._session_blocks
        if since_date:
            blocks = [b for b in blocks if b.end_time >= since_date or b.is_active]
        
        # Aggregate data from blocks
        total_cost = 0.0
        total_input_tokens = 0
        total_output_tokens = 0
        total_cache_read_tokens = 0
        total_cache_creation_tokens = 0
        model_breakdown = {}
        session_count = len(blocks)
        entries_processed = 0
        
        for block in blocks:
            # Add block totals
            total_cost += block.cost_usd
            total_input_tokens += block.input_tokens
            total_output_tokens += block.output_tokens
            total_cache_read_tokens += block.cache_read_tokens
            total_cache_creation_tokens += block.cache_creation_tokens
            entries_processed += len(block.entries)
            
            # Merge model breakdown
            for model, stats in block.per_model_stats.items():
                if model not in model_breakdown:
                    model_breakdown[model] = {
                        "cost": 0.0,
                        "input_tokens": 0,
                        "cache_creation_tokens": 0,
                        "cache_read_tokens": 0,
                        "output_tokens": 0,
                        "requests": 0
                    }
                
                model_breakdown[model]["cost"] += stats['cost_usd']
                model_breakdown[model]["input_tokens"] += stats['input_tokens']
                model_breakdown[model]["cache_creation_tokens"] += stats['cache_creation_tokens']
                model_breakdown[model]["cache_read_tokens"] += stats['cache_read_tokens']
                model_breakdown[model]["output_tokens"] += stats['output_tokens']
                model_breakdown[model]["requests"] += stats['entries_count']
        
        # Return aggregated data
        return {
            "total_cost": total_cost,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cache_read_tokens": total_cache_read_tokens,
            "total_cache_creation_tokens": total_cache_creation_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,  # Non-cache tokens only
            "total_tokens_with_cache": total_input_tokens + total_output_tokens + total_cache_read_tokens + total_cache_creation_tokens,
            "model_breakdown": model_breakdown,
            "session_count": session_count,
            "file_count": len(blocks),  # Number of blocks
            "since_date": since_date.isoformat() if since_date else "all"
        }
    
    async def get_usage_data_async(self, since_date: Optional[datetime] = None, 
                                   progress_callback: Optional[Callable[[str], None]] = None) -> Dict:
        """Async version of get_usage_data that runs in a background thread"""
        loop = asyncio.get_event_loop()
        
        # Create a wrapper that includes progress updates
        def _get_data_with_progress():
            if progress_callback:
                progress_callback("Reading Claude Code usage...")
            result = self.get_usage_data(since_date)
            if progress_callback:
                progress_callback(f"Processed {result['file_count']} files")
            return result
        
        # Run the synchronous method in a thread pool
        return await loop.run_in_executor(self._executor, _get_data_with_progress)
    
    def get_current_session_info(self) -> Dict:
        """Get information about the current session including start time and model breakdown"""
        # Get current block
        current_block = self._get_current_block()
        if not current_block:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            return {
                'start_time': self._round_to_hour(now),
                'rate_history': [],
                'model_breakdown': {}
            }
        
        return {
            'start_time': current_block.start_time,
            'rate_history': [],  # Not used anymore
            'model_breakdown': current_block.per_model_stats
        }
    
    def __del__(self):
        """Clean up the thread pool executor"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)