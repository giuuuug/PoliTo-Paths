# logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self):
        # Configurazione radicalmente separata
        self._configure_app_logger()
        self._configure_bot_logger()
        
    def _configure_app_logger(self):
        """Logger per errori applicativi generici"""
        self.app_logger = logging.getLogger('app')
        self.app_logger.setLevel(logging.WARNING)
        self.app_logger.propagate = False
        
        # File handler SOLO per app
        app_file_handler = RotatingFileHandler(
            'app.log',
            maxBytes=10*1024*1024,
            backupCount=1,
            encoding='utf-8'
        )
        app_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - APP::%(levelname)s - %(module)s - %(message)s'
        ))
        app_file_handler.addFilter(lambda record: record.name == 'app')
        
        self.app_logger.addHandler(app_file_handler)

    def _configure_bot_logger(self):
        """Logger specifico per le attività del bot"""
        self.bot_logger = logging.getLogger('bot')
        self.bot_logger.setLevel(logging.INFO)
        self.bot_logger.propagate = False
        
        # File handler SOLO per bot
        bot_file_handler = RotatingFileHandler(
            'bot.log',
            maxBytes=5*1024*1024,
            backupCount=1,
            encoding='utf-8'
        )
        bot_file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] BOT::%(levelname)s - %(message)s'
        ))
        bot_file_handler.addFilter(lambda record: record.name == 'bot')
        
        self.bot_logger.addHandler(bot_file_handler)

    # Metodi espliciti per l'uso esterno
    def log_app_error(self, msg):
        self.app_logger.error(msg)
    
    def log_bot_info(self, msg):
        self.bot_logger.info(msg)
    
    def log_bot_critical(self, msg):
        self.bot_logger.critical(msg)