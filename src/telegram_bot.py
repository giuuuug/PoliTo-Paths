from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler
from command.navigate_command import NavigateCommand, NavigationStepState
from command.start_command import StartCommand
from command.help_command import HelpCommand
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths

QUESTION_1, QUESTION_2 = range(2)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        self.db_polito_paths = DatabasePostgreSQLPolitoPaths()
        
        # Initialize all commands
        self.navigate_command = NavigateCommand(self.db_polito_paths)
        self.start_command = StartCommand()
        self.help_command = HelpCommand()
        
        # Clear all navigation sessions on startup
        self.navigate_command.clear_all_sessions()
        
        self._register_handlers()

    def _register_handlers(self):
        # Regular command handlers
        self.app.add_handler(CommandHandler("start", self.start_command.command_start))
        self.app.add_handler(CommandHandler("help", self.help_command.command_start))
        
        navigate_command_handler = ConversationHandler(
            entry_points=[CommandHandler("navigate", self.navigate_command.command_start)],
            states={
                QUESTION_1: [CallbackQueryHandler(self.navigate_command.handle_question)],
                QUESTION_2: [CallbackQueryHandler(self.navigate_command.handle_question)],
                NavigationStepState.NAV_STEP.value: [CallbackQueryHandler(self.navigate_command.handle_navigation_callback, pattern=r"^navigate:(next|prev)$")],
            },
            fallbacks=[CommandHandler("cancel", self.navigate_command.command_cancel)],
        )
        
        self.app.add_handler(navigate_command_handler)

    def run(self):
        try:
            self.app.run_polling()
        except Exception as e:
            raise