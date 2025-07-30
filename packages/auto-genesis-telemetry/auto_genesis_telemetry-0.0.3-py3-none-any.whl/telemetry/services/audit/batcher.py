import asyncio
import json
import time
from typing import List, Callable, Optional
from dataclasses import asdict

from ...types import AuditEvent
from ...utils.logging_util import custom_logger, custom_error_logger


class AuditBatcher:
    """Batches audit events based on size and time thresholds."""
    
    def __init__(self, batch_size_kb: int, batch_timeout_ms: int):
        self.batch_size_kb = batch_size_kb
        self.batch_timeout_ms = batch_timeout_ms
        self.current_batch: List[AuditEvent] = []
        self.current_batch_size = 0
        self.last_batch_time = time.time()
        self.batch_processor: Optional[Callable] = None
        self.batch_task: Optional[asyncio.Task] = None
        self.running = False
        self.lock = asyncio.Lock()
        
    async def start(self, batch_processor_callback: Callable) -> None:
        """Start batching with background processor."""
        try:
            self.batch_processor = batch_processor_callback
            self.running = True
            self.last_batch_time = time.time()
            
            # Start background task for time-based batching
            self.batch_task = asyncio.create_task(self._batch_timer_task())
            
            custom_logger("AuditBatcher started successfully")
            
        except Exception as e:
            custom_error_logger(f"Failed to start AuditBatcher: {e}")
            raise
    
    async def add_event(self, event: AuditEvent) -> None:
        """Add event to current batch, triggering send if thresholds met."""
        if not self.running:
            custom_error_logger("AuditBatcher is not running")
            return
        
        async with self.lock:
            # Calculate event size
            event_dict = asdict(event)
            event_json = json.dumps(event_dict, sort_keys=True)
            event_size_bytes = len(event_json.encode('utf-8'))
            event_size_kb = event_size_bytes / 1024
            
            # Add event to batch
            self.current_batch.append(event)
            self.current_batch_size += event_size_kb
            
            # Check if we should send the batch
            should_send = (
                self.current_batch_size >= self.batch_size_kb or
                len(self.current_batch) >= 100  # Max events per batch
            )
            
            if should_send:
                await self._send_current_batch()
    
    async def _send_current_batch(self) -> None:
        """Send current batch and reset for next batch."""
        if not self.current_batch:
            return
        
        try:
            # Get current batch
            batch_to_send = self.current_batch.copy()
            batch_size = len(batch_to_send)
            
            # Reset current batch
            self.current_batch.clear()
            self.current_batch_size = 0
            self.last_batch_time = time.time()
            
            # Process batch
            if self.batch_processor:
                await self.batch_processor(batch_to_send)
            
            custom_logger(f"Sent batch of {batch_size} audit events")
            
        except Exception as e:
            custom_error_logger(f"Failed to send audit batch: {e}")
            
            # Re-add failed events to current batch (simple retry)
            async with self.lock:
                self.current_batch.extend(batch_to_send)
                # Recalculate size
                self.current_batch_size = sum(
                    len(json.dumps(asdict(event), sort_keys=True).encode('utf-8')) / 1024
                    for event in self.current_batch
                )
            
            raise
    
    async def _batch_timer_task(self) -> None:
        """Background task that sends batches based on time threshold."""
        while self.running:
            try:
                await asyncio.sleep(self.batch_timeout_ms / 1000.0)
                
                async with self.lock:
                    current_time = time.time()
                    time_since_last_batch = (current_time - self.last_batch_time) * 1000
                    
                    if (time_since_last_batch >= self.batch_timeout_ms and 
                        self.current_batch):
                        await self._send_current_batch()
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                custom_error_logger(f"Error in batch timer task: {e}")
                await asyncio.sleep(1)  # Brief delay before continuing
    
    async def flush(self) -> None:
        """Flush any remaining events in the current batch."""
        async with self.lock:
            if self.current_batch:
                await self._send_current_batch()
    
    async def shutdown(self) -> None:
        """Flush remaining events and stop batching."""
        try:
            custom_logger("Shutting down AuditBatcher...")
            
            # Stop accepting new events
            self.running = False
            
            # Cancel background task
            if self.batch_task and not self.batch_task.done():
                self.batch_task.cancel()
                try:
                    await self.batch_task
                except asyncio.CancelledError:
                    pass
            
            # Flush remaining events
            await self.flush()
            
            custom_logger("AuditBatcher shutdown completed")
            
        except Exception as e:
            custom_error_logger(f"Failed to shutdown AuditBatcher: {e}")
            raise