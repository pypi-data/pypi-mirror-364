import asyncio
import schedule
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    id: str
    name: str
    prompt: str
    browser: str
    schedule_type: str  # 'once', 'daily', 'weekly', 'monthly', 'interval'
    schedule_time: str  # Time specification
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None
    enabled: bool = True
    result: Optional[Dict] = None
    error: Optional[str] = None


class TaskScheduler:
    """Scheduler for automating browser tasks at specified times"""
    
    def __init__(self, agent=None):
        self.agent = agent
        self.tasks = {}
        self.running_tasks = {}
        self.scheduler_thread = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Setup schedule
        self.schedule = schedule
    
    def add_task(self, task: ScheduledTask) -> bool:
        """Add a new scheduled task"""
        try:
            if task.id in self.tasks:
                self.logger.warning(f"Task {task.id} already exists, replacing")
            
            # Set created_at if not set
            if not task.created_at:
                task.created_at = datetime.now()
            
            # Calculate next run time
            task.next_run = self._calculate_next_run(task)
            
            # Schedule the task
            self._schedule_task(task)
            
            self.tasks[task.id] = task
            self.logger.info(f"Task {task.id} scheduled for {task.next_run}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add task {task.id}: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        if task_id in self.tasks:
            # Cancel the schedule
            self.schedule.clear(task_id)
            
            # Remove from tasks
            del self.tasks[task_id]
            
            # Cancel if currently running
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                del self.running_tasks[task_id]
            
            self.logger.info(f"Task {task_id} removed")
            return True
        
        return False
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a task"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            return True
        return False
    
    def start_scheduler(self):
        """Start the task scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.logger.info("Task scheduler started")
    
    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.running = False
        
        # Cancel all running tasks
        for task_future in self.running_tasks.values():
            task_future.cancel()
        
        self.running_tasks.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Task scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self.schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(5)
    
    def _schedule_task(self, task: ScheduledTask):
        """Schedule a task with the schedule library"""
        def run_task():
            if task.enabled and (not task.max_runs or task.run_count < task.max_runs):
                asyncio.create_task(self._execute_task(task))
        
        if task.schedule_type == "once":
            # Parse time for one-time execution
            run_time = datetime.strptime(task.schedule_time, "%Y-%m-%d %H:%M:%S")
            if run_time > datetime.now():
                delay = (run_time - datetime.now()).total_seconds()
                threading.Timer(delay, run_task).start()
        
        elif task.schedule_type == "daily":
            self.schedule.every().day.at(task.schedule_time).do(run_task).tag(task.id)
        
        elif task.schedule_type == "weekly":
            # Format: "monday:14:30" or "14:30" for every week
            if ":" in task.schedule_time and len(task.schedule_time.split(":")) == 3:
                day, hour, minute = task.schedule_time.split(":")
                getattr(self.schedule.every(), day.lower()).at(f"{hour}:{minute}").do(run_task).tag(task.id)
            else:
                self.schedule.every().week.at(task.schedule_time).do(run_task).tag(task.id)
        
        elif task.schedule_type == "interval":
            # Format: "30s", "5m", "2h"
            interval_str = task.schedule_time
            if interval_str.endswith('s'):
                seconds = int(interval_str[:-1])
                self.schedule.every(seconds).seconds.do(run_task).tag(task.id)
            elif interval_str.endswith('m'):
                minutes = int(interval_str[:-1])
                self.schedule.every(minutes).minutes.do(run_task).tag(task.id)
            elif interval_str.endswith('h'):
                hours = int(interval_str[:-1])
                self.schedule.every(hours).hours.do(run_task).tag(task.id)
    
    async def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        if not self.agent:
            self.logger.error(f"No agent available to execute task {task.id}")
            return
        
        try:
            task.status = TaskStatus.RUNNING
            task.last_run = datetime.now()
            task.run_count += 1
            
            self.logger.info(f"Executing scheduled task: {task.name}")
            
            # Execute the task using the agent
            result = await self.agent.execute_task(task.prompt, task.browser)
            
            # Update task with result
            task.result = result.__dict__ if hasattr(result, '__dict__') else result
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            
            if not result.success:
                task.error = result.error_message
            
            self.logger.info(f"Task {task.name} completed with status: {task.status.value}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.logger.error(f"Task {task.name} failed: {e}")
        
        finally:
            # Remove from running tasks
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            
            # Calculate next run if recurring
            if task.schedule_type != "once":
                task.next_run = self._calculate_next_run(task)
    
    def _calculate_next_run(self, task: ScheduledTask) -> Optional[datetime]:
        """Calculate the next run time for a task"""
        now = datetime.now()
        
        if task.schedule_type == "once":
            run_time = datetime.strptime(task.schedule_time, "%Y-%m-%d %H:%M:%S")
            return run_time if run_time > now else None
        
        elif task.schedule_type == "daily":
            time_parts = task.schedule_time.split(":")
            hour, minute = int(time_parts[0]), int(time_parts[1])
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        
        elif task.schedule_type == "weekly":
            # Simplified calculation for weekly tasks
            return now + timedelta(weeks=1)
        
        elif task.schedule_type == "interval":
            interval_str = task.schedule_time
            if interval_str.endswith('s'):
                delta = timedelta(seconds=int(interval_str[:-1]))
            elif interval_str.endswith('m'):
                delta = timedelta(minutes=int(interval_str[:-1]))
            elif interval_str.endswith('h'):
                delta = timedelta(hours=int(interval_str[:-1]))
            else:
                delta = timedelta(hours=1)  # Default
            
            return now + delta
        
        return None
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            'id': task.id,
            'name': task.name,
            'status': task.status.value,
            'enabled': task.enabled,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'last_run': task.last_run.isoformat() if task.last_run else None,
            'next_run': task.next_run.isoformat() if task.next_run else None,
            'run_count': task.run_count,
            'max_runs': task.max_runs,
            'result': task.result,
            'error': task.error
        }
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all scheduled tasks"""
        return [self.get_task_status(task_id) for task_id in self.tasks]
    
    def get_running_tasks(self) -> List[str]:
        """Get list of currently running task IDs"""
        return list(self.running_tasks.keys())


class RealTimeMonitor:
    """Monitor for real-time task execution and system events"""
    
    def __init__(self, agent=None):
        self.agent = agent
        self.callbacks = {}
        self.monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
    
    def add_callback(self, event_type: str, callback: Callable):
        """Add a callback for specific events"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
    
    def remove_callback(self, event_type: str, callback: Callable):
        """Remove a callback"""
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type].remove(callback)
            except ValueError:
                pass
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.logger.info("Real-time monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Real-time monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Monitor system events, browser status, etc.
                self._check_browser_status()
                self._check_system_resources()
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(10)
    
    def _check_browser_status(self):
        """Check browser status and emit events"""
        if self.agent and hasattr(self.agent, 'browser_manager'):
            # Check if browser is still responsive
            try:
                if self.agent.browser_manager.active_driver:
                    # Try to get current URL as a health check
                    current_url = self.agent.browser_manager.active_driver.current_url
                    self._emit_event('browser_healthy', {'url': current_url})
            except Exception as e:
                self._emit_event('browser_error', {'error': str(e)})
    
    def _check_system_resources(self):
        """Check system resources and emit warnings if needed"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 90:
                self._emit_event('high_cpu_usage', {'cpu_percent': cpu_percent})
            
            if memory_percent > 90:
                self._emit_event('high_memory_usage', {'memory_percent': memory_percent})
                
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
    
    def _emit_event(self, event_type: str, data: Dict[str, Any] = None):
        """Emit an event to registered callbacks"""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(event_type, data or {})
                except Exception as e:
                    self.logger.error(f"Error in callback for {event_type}: {e}")
    
    def trigger_manual_event(self, event_type: str, data: Dict[str, Any] = None):
        """Manually trigger an event"""
        self._emit_event(event_type, data)