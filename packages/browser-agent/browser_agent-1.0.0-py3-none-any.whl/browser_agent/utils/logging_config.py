"""Professional logging configuration for Browser Agent"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ..config.paths import path_manager
from ..config.constants import LOGGING_CONFIG, APP_NAME


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        
        return super().format(record)


class BrowserAgentLogger:
    """Professional logging system for Browser Agent"""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self._configured = False
    
    def configure(self, 
                  log_level: str = "INFO",
                  log_to_file: bool = True,
                  log_to_console: bool = True,
                  max_file_size: int = 10 * 1024 * 1024,  # 10MB
                  backup_count: int = 5,
                  format_string: Optional[str] = None) -> None:
        """Configure the logging system"""
        
        if self._configured:
            return
        
        # Set default format
        if format_string is None:
            format_string = LOGGING_CONFIG["format"]
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            
            # Use colored formatter for console
            console_formatter = ColoredFormatter(
                fmt=format_string,
                datefmt=LOGGING_CONFIG["date_format"]
            )
            console_handler.setFormatter(console_formatter)
            
            root_logger.addHandler(console_handler)
            self.handlers['console'] = console_handler
        
        # File handler
        if log_to_file:
            # Ensure log directory exists
            path_manager.user_log_dir.mkdir(parents=True, exist_ok=True)
            
            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=path_manager.log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, log_level.upper()))
            
            # Use standard formatter for file
            file_formatter = logging.Formatter(
                fmt=format_string,
                datefmt=LOGGING_CONFIG["date_format"]
            )
            file_handler.setFormatter(file_formatter)
            
            root_logger.addHandler(file_handler)
            self.handlers['file'] = file_handler
        
        # Create application logger
        app_logger = self.get_logger(APP_NAME)
        app_logger.info(f"Logging system configured - Level: {log_level}")
        app_logger.info(f"Log file: {path_manager.log_file if log_to_file else 'Disabled'}")
        
        self._configured = True
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def set_level(self, level: str) -> None:
        """Set logging level for all handlers"""
        log_level = getattr(logging, level.upper())
        
        # Update root logger
        logging.getLogger().setLevel(log_level)
        
        # Update all handlers
        for handler in self.handlers.values():
            handler.setLevel(log_level)
        
        logger = self.get_logger(APP_NAME)
        logger.info(f"Logging level changed to {level}")
    
    def add_file_handler(self, 
                        filename: str,
                        level: str = "INFO",
                        max_size: int = 10 * 1024 * 1024,
                        backup_count: int = 5) -> None:
        """Add an additional file handler"""
        
        file_path = path_manager.user_log_dir / filename
        
        handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, level.upper()))
        
        formatter = logging.Formatter(
            fmt=LOGGING_CONFIG["format"],
            datefmt=LOGGING_CONFIG["date_format"]
        )
        handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(handler)
        self.handlers[filename] = handler
    
    def remove_handler(self, name: str) -> None:
        """Remove a handler by name"""
        if name in self.handlers:
            handler = self.handlers[name]
            logging.getLogger().removeHandler(handler)
            handler.close()
            del self.handlers[name]
    
    def log_system_info(self) -> None:
        """Log system information for debugging"""
        logger = self.get_logger(f"{APP_NAME}.system")
        
        # Get system info from path manager
        system_info = path_manager.get_system_info()
        
        logger.info("=== System Information ===")
        for key, value in system_info.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 30)
    
    def log_startup(self) -> None:
        """Log application startup information"""
        logger = self.get_logger(APP_NAME)
        
        logger.info("=" * 50)
        logger.info(f"{APP_NAME} Starting Up")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 50)
        
        # Log system info
        self.log_system_info()
    
    def log_shutdown(self) -> None:
        """Log application shutdown"""
        logger = self.get_logger(APP_NAME)
        
        logger.info("=" * 50)
        logger.info(f"{APP_NAME} Shutting Down")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 50)
        
        # Flush all handlers
        for handler in self.handlers.values():
            handler.flush()
    
    def create_task_logger(self, task_id: str) -> logging.Logger:
        """Create a logger for a specific task"""
        logger_name = f"{APP_NAME}.task.{task_id}"
        logger = self.get_logger(logger_name)
        
        # Add task-specific file handler
        task_log_file = f"task_{task_id}.log"
        self.add_file_handler(
            filename=task_log_file,
            level="DEBUG",
            max_size=5 * 1024 * 1024,  # 5MB
            backup_count=2
        )
        
        return logger
    
    def cleanup_old_logs(self, max_age_days: int = 30) -> None:
        """Clean up old log files"""
        import time
        
        log_dir = path_manager.user_log_dir
        if not log_dir.exists():
            return
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        logger = self.get_logger(f"{APP_NAME}.cleanup")
        cleaned_count = 0
        
        for log_file in log_dir.glob("*.log*"):
            if log_file.is_file():
                file_age = current_time - log_file.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        log_file.unlink()
                        cleaned_count += 1
                    except OSError as e:
                        logger.warning(f"Failed to delete old log file {log_file}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old log files")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        log_dir = path_manager.user_log_dir
        
        stats = {
            "log_directory": str(log_dir),
            "main_log_file": str(path_manager.log_file),
            "log_files_count": 0,
            "total_log_size": 0,
            "handlers_count": len(self.handlers),
            "loggers_count": len(self.loggers),
        }
        
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log*"))
            stats["log_files_count"] = len(log_files)
            stats["total_log_size"] = sum(f.stat().st_size for f in log_files if f.is_file())
        
        return stats


# Global logger instance
logger_manager = BrowserAgentLogger()


def setup_logging(log_level: str = "INFO", 
                 log_to_file: bool = True,
                 log_to_console: bool = True) -> None:
    """Setup logging with default configuration"""
    logger_manager.configure(
        log_level=log_level,
        log_to_file=log_to_file,
        log_to_console=log_to_console
    )
    
    # Log startup info
    logger_manager.log_startup()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logger_manager.get_logger(name)


def shutdown_logging() -> None:
    """Shutdown logging system"""
    logger_manager.log_shutdown()