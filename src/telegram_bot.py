from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler
from command.navigate_command import NavigateCommand, SOURCE, DESTINATION, NAVIGATION
from command.start_command import StartCommand
from command.help_command import HelpCommand
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        self.db_polito_paths = DatabasePostgreSQLPolitoPaths()
        
        # Initialize all commands
        self.navigate_command = NavigateCommand(self.db_polito_paths)
        self.start_command = StartCommand()
        self.help_command = HelpCommand()
        
        self._register_handlers()

    def _register_handlers(self):
        # Regular command handlers
        self.app.add_handler(CommandHandler("start", self.start_command.command_start))
        self.app.add_handler(CommandHandler("help", self.help_command.command_start))
        
        navigate_command_handler = ConversationHandler(
            entry_points=[CommandHandler("navigate", self.navigate_command.command_start)],
            states={
                SOURCE: [CallbackQueryHandler(self.navigate_command.handle_question)],
                DESTINATION: [CallbackQueryHandler(self.navigate_command.handle_question)],
                NAVIGATION: [CallbackQueryHandler(self.navigate_command.handle_question)],
            },
            fallbacks=[CallbackQueryHandler(self.navigate_command.command_cancel)],
        )
        
        self.app.add_handler(navigate_command_handler)

    def run(self):
        try:
            self.app.run_polling()
        except Exception as e:
            raise e