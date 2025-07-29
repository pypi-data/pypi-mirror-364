"""
Logger utility for SYSTEM-SELL
"""

import logging

def setup_logger(verbose: bool = False):
    """Setup and return a logger instance"""
    logger = logging.getLogger("system-sell")
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger
