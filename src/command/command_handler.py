from abc import ABC, abstractmethod
from telegram.ext import ContextTypes, CallbackContext
from telegram import Update
from utils.log import Log

class CommandHandler(ABC):
    def __init__(self, log, database = None,):
        self.database = database
        self.log = Log(self.__class__.__name__)
    
    @abstractmethod
    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle a command from the user.
        
        Args:
            update: The update object containing information about the command.
            context: The context object containing additional information.
        """
        pass
    
    @abstractmethod
    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle a command from the user.
        
        Args:
            update: The update object containing information about the command.
            context: The context object containing additional information.
        """
        pass
    
    @abstractmethod
    async def command_cancel(self, update: Update, context: CallbackContext):
        """
        Handle the cancellation of a command.
        
        Args:
            update: The update object containing information about the command.
            context: The context object containing additional information.
        """
        pass