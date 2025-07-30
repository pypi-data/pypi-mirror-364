import logging
import os
import sys
from datetime import datetime
from typing import Optional
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT
    }
    
    def format(self, record):
        # Get the color for the log level
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        
        # Format the message
        formatted_message = super().format(record)
        
        # Add color only for console output
        if hasattr(record, 'no_color') and record.no_color:
            return formatted_message
        
        return f"{log_color}{formatted_message}{Style.RESET_ALL}"


class BrowserAgentLogger:
    """Enhanced logger for browser agent with structured logging"""
    
    def __init__(self, name: str, level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler without colors
        if log_file:
            self._setup_file_handler(log_file)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def _setup_file_handler(self, log_file: str):
        """Setup file handler for logging"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Add timestamp to log file name
        base_name, ext = os.path.splitext(log_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_file = f"{base_name}_{timestamp}{ext}"
        
        file_handler = logging.FileHandler(timestamped_file)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Logging to file: {timestamped_file}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        self._log_with_context(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        self._log_with_context(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context"""
        self._log_with_context(logging.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional context"""
        self._log_with_context(logging.CRITICAL, message, kwargs)
    
    def _log_with_context(self, level: int, message: str, context: dict):
        """Log message with additional context"""
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            full_message = f"{message} | {context_str}"
        else:
            full_message = message
        
        self.logger.log(level, full_message)
    
    def log_step_start(self, step_number: int, action: str, target: str = None):
        """Log the start of an automation step"""
        target_info = f" -> {target}" if target else ""
        self.info(f"[STEP {step_number}] Starting: {action}{target_info}")
    
    def log_step_success(self, step_number: int, action: str, details: dict = None):
        """Log successful completion of an automation step"""
        details_str = f" | {details}" if details else ""
        self.info(f"[STEP {step_number}] ✓ Success: {action}{details_str}")
    
    def log_step_failure(self, step_number: int, action: str, error: str):
        """Log failure of an automation step"""
        self.error(f"[STEP {step_number}] ✗ Failed: {action} | Error: {error}")
    
    def log_browser_action(self, action: str, **kwargs):
        """Log browser-specific actions"""
        self.debug(f"[BROWSER] {action}", **kwargs)
    
    def log_ai_interaction(self, prompt_length: int, response_length: int, model: str):
        """Log AI API interactions"""
        self.debug(
            f"[AI] Model: {model}",
            prompt_chars=prompt_length,
            response_chars=response_length
        )
    
    def log_performance(self, operation: str, duration: float, **metrics):
        """Log performance metrics"""
        self.info(
            f"[PERF] {operation} completed in {duration:.2f}s",
            **metrics
        )


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> BrowserAgentLogger:
    """Setup and return a configured logger"""
    return BrowserAgentLogger("browser_agent", level, log_file)


class ErrorHandler:
    """Centralized error handling for the browser agent"""
    
    def __init__(self, logger: BrowserAgentLogger):
        self.logger = logger
        self.error_count = 0
        self.error_history = []
    
    def handle_step_error(self, step_number: int, action: str, error: Exception, 
                         context: dict = None) -> dict:
        """Handle errors that occur during step execution"""
        self.error_count += 1
        
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'step_number': step_number,
            'action': action,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.error_history.append(error_info)
        self.logger.log_step_failure(step_number, action, str(error))
        
        # Determine if error is recoverable
        recoverable_errors = [
            'TimeoutException',
            'NoSuchElementException',
            'ElementNotInteractableException',
            'StaleElementReferenceException'
        ]
        
        is_recoverable = type(error).__name__ in recoverable_errors
        
        return {
            'error_info': error_info,
            'is_recoverable': is_recoverable,
            'suggested_action': self._suggest_recovery_action(error)
        }
    
    def handle_browser_error(self, error: Exception, browser_name: str) -> dict:
        """Handle browser-specific errors"""
        self.logger.error(
            f"Browser error in {browser_name}",
            error_type=type(error).__name__,
            error_message=str(error)
        )
        
        # Common browser error recovery suggestions
        recovery_suggestions = {
            'WebDriverException': 'Try restarting the browser',
            'SessionNotCreatedException': 'Check driver compatibility',
            'InvalidSessionIdException': 'Browser session expired, restart required',
            'NoSuchWindowException': 'Browser window was closed',
            'ConnectionRefusedError': 'Browser service not running'
        }
        
        suggestion = recovery_suggestions.get(type(error).__name__, 'Unknown error')
        
        return {
            'error_type': type(error).__name__,
            'suggestion': suggestion,
            'browser': browser_name
        }
    
    def handle_ai_error(self, error: Exception, prompt: str = None) -> dict:
        """Handle AI/API related errors"""
        self.logger.error(
            "AI processing error",
            error_type=type(error).__name__,
            error_message=str(error),
            prompt_length=len(prompt) if prompt else 0
        )
        
        # AI error recovery suggestions
        ai_recovery = {
            'RateLimitError': 'Wait before retrying, reduce request frequency',
            'InvalidRequestError': 'Check prompt format and parameters',
            'AuthenticationError': 'Verify API key configuration',
            'TimeoutError': 'Retry with shorter prompt or increase timeout',
            'JSONDecodeError': 'AI response format error, retry with clearer instructions'
        }
        
        suggestion = ai_recovery.get(type(error).__name__, 'Check AI service status')
        
        return {
            'error_type': type(error).__name__,
            'suggestion': suggestion,
            'prompt_provided': prompt is not None
        }
    
    def _suggest_recovery_action(self, error: Exception) -> str:
        """Suggest recovery actions based on error type"""
        error_type = type(error).__name__
        
        recovery_actions = {
            'TimeoutException': 'Increase wait time or check element selector',
            'NoSuchElementException': 'Verify element selector or wait for page load',
            'ElementNotInteractableException': 'Scroll to element or wait for it to be clickable',
            'StaleElementReferenceException': 'Re-find the element before interacting',
            'InvalidSelectorException': 'Check selector syntax',
            'ElementClickInterceptedException': 'Remove overlaying elements or scroll'
        }
        
        return recovery_actions.get(error_type, 'Manual intervention may be required')
    
    def get_error_summary(self) -> dict:
        """Get summary of all errors encountered"""
        if not self.error_history:
            return {'total_errors': 0, 'summary': 'No errors encountered'}
        
        error_types = {}
        for error in self.error_history:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': self.error_count,
            'error_types': error_types,
            'recent_errors': self.error_history[-5:],  # Last 5 errors
            'most_common': max(error_types.items(), key=lambda x: x[1]) if error_types else None
        }