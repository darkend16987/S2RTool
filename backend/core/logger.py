"""
Logging Configuration for S2RTool Backend
Provides production-ready logging with proper levels and formatting
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os

# ============== CONFIGURATION ==============
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.environ.get("LOG_TO_FILE", "True").lower() == "true"
LOG_DIR = Path(__file__).parent.parent / "logs"

# Create logs directory if it doesn't exist
if LOG_TO_FILE:
    LOG_DIR.mkdir(exist_ok=True)

# ============== LOG FORMAT ==============
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============== COLOR CODES (for console) ==============
class LogColors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

# ============== COLORED FORMATTER ==============
class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to console output"""

    COLORS = {
        logging.DEBUG: LogColors.CYAN,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.MAGENTA,
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if record.levelno in self.COLORS:
            levelname_color = f"{self.COLORS[record.levelno]}{levelname}{LogColors.RESET}"
            record.levelname = levelname_color

        return super().format(record)

# ============== SETUP LOGGER ==============
def setup_logger(name: str, level: str = None) -> logging.Logger:
    """
    Create and configure a logger

    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # ========== CONSOLE HANDLER ==========
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Use colored formatter for console
    console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # ========== FILE HANDLER ==========
    if LOG_TO_FILE:
        log_file = LOG_DIR / "app.log"

        # Rotating file handler (max 10MB, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Use standard formatter for files (no colors)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# ============== DEFAULT LOGGER ==============
# Create default logger for direct import
logger = setup_logger("s2rtool")

# ============== HELPER FUNCTIONS ==============
def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return setup_logger(name)

# ============== USAGE EXAMPLES ==============
if __name__ == "__main__":
    # Demo logging
    test_logger = get_logger("test")

    test_logger.debug("🔍 Debug message - detailed information")
    test_logger.info("✅ Info message - general information")
    test_logger.warning("⚠️  Warning message - something to watch")
    test_logger.error("❌ Error message - something went wrong")
    test_logger.critical("🔥 Critical message - system failure")

    print("\n" + "="*60)
    print("Logging configured successfully!")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Log to File: {LOG_TO_FILE}")
    if LOG_TO_FILE:
        print(f"Log Directory: {LOG_DIR}")
    print("="*60)
