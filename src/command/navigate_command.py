from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from widget.carousel import CarouselWidget
from database.database_postgreSQL_pgrouting_sample import DatabasePostgreSQLPgRoutingSample
from utils.log import Log
from enum import Enum
from command.command_handler import CommandHandler

class SampleCommandState(Enum):
    SAMPLE_COMMAND_STATE_1_Q = 0
    SAMPLE_COMMAND_STATE_2_Q = 1
    SAMPLE_COMMAND_STATE_NUM = 2

# Define states for the conversation
QUESTION_1, QUESTION_2 = range(2)

class NavigateCommand(CommandHandler):
    def __init__(self, database: DatabasePostgreSQLPgRoutingSample = None):
        super().__init__(log=Log(self.__class__.__name__), database=database)
        self.carousel = CarouselWidget()
        self.questions = []
        self.answers = []
        self.state = SampleCommandState.SAMPLE_COMMAND_STATE_1_Q.value
        
    async def _set_questions(self, update: Update):
        try:
            query = "SELECT name FROM departments"
            with self.database as db:
                results = db.execute_query(query)

            # Process results to ensure they are a list of strings
            if not isinstance(results, list):
                raise ValueError("Query results must be a list.")

            processed_results = [row[0] if isinstance(row, (list, tuple)) else row for row in results]
            if not all(isinstance(item, str) for item in processed_results):
                raise ValueError("Query results must be a list of strings.")

            processed_results = [{str(i + 1): row} for i, row in enumerate(processed_results)]
            self.questions.append({'text': "Where are you now?", 'options': processed_results})
            self.questions.append({'text': "Which is your destination?", 'options': processed_results})


        except ValueError as ve:
            self.log.error(f"Validation error while setting questions: {ve}")
            await update.message.reply_text(
                "An error occurred while processing the data. Please try again later."
            )
        except AttributeError as ae:
            self.log.error(f"Database connection error: {ae}")
            await update.message.reply_text(
                "An error occurred with the database connection. Please contact support."
            )
        except Exception as e:
            self.log.error(f"Unexpected error in '_set_questions': {e}")
            await update.message.reply_text(
                "An unexpected error occurred. Please try again later."
            )

    async def _send_question(self, update_or_query, context):
        question = self.questions[self.state]
        btn_grid = self.carousel.get_grid(options=[list(opt.values())[0] for opt in question["options"]])

        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text(question["text"], reply_markup=btn_grid)
        else:
            await update_or_query.edit_message_text(question["text"], reply_markup=btn_grid)
    
    async def command_start(self, update, context):
        # Reset state and clear previous answers
        self.state = SampleCommandState.SAMPLE_COMMAND_STATE_1_Q.value
        self.answers = []
        self.questions = []  # Clear previous questions too
        
        await self._set_questions(update)
        await self._send_question(update, context)
        return QUESTION_1  # Start with the first question
    
    async def handle_question(self, update, context):
        clb_query = update.callback_query
        await clb_query.answer()
        user_answer = clb_query.data
        
        if user_answer.startswith("navigate:"):
            self.carousel.set_curr_page_from_navigation(user_answer)
            await self._send_question(clb_query, context)
            return self.state  # Stay in the same state
        
        self.answers.append(user_answer)
        
        # Show the next question
        self.state += 1
        self.carousel.set_curr_page(0)
        if self.state < SampleCommandState.SAMPLE_COMMAND_STATE_NUM.value:
            await self._send_question(clb_query, context)
            return QUESTION_2  # Move to the second question
        else:
            await self._compute_shortest_path(clb_query, context)
            return ConversationHandler.END  # End the conversation
    
    async def _compute_shortest_path(self, clb_query, context: ContextTypes.DEFAULT_TYPE):
        await clb_query.edit_message_text(f"Calculating shortest path from {self.answers[0].upper()} to {self.answers[1].upper()}")
        self.log.info(f"Calculating shortest path from {self.answers[0].upper()} to {self.answers[1].upper()}")
        try:
            source_point_as_num = next(
                (key for opt in self.questions[0]["options"] for key, value in opt.items() if value == self.answers[0]),
                None
            )
            destination_point_as_num = next(
                (key for opt in self.questions[1]["options"] for key, value in opt.items() if value == self.answers[1]),
                None
            )
            
            self.log.info(f"Source point as number: {source_point_as_num} Destination point as number: {destination_point_as_num}")

            # Query the database for the shortest path
            query = f"SELECT * FROM get_navigation_instructions({source_point_as_num}, {destination_point_as_num});"
            with self.database as db:
                results = db.execute_query(query)
                        
            # Convert the results into a map structure 
            map_structure = [
                {
                    "step": row[0],
                    "instruction": row[1],
                    "cost": row[2],
                    "geometry": row[3]
                }
                for row in results
            ]

            # Log the map structure for debugging purposes
            self.log.info(f"Map structure: {map_structure}")

            # Format the results for the user
            if map_structure:
                for step in map_structure:
                    await context.bot.send_message(
                        chat_id=clb_query.from_user.id,
                        text=f"Step {step['step']}: {step['instruction']} for {round(step['cost'], 1)}m"
                    )
            else:
                await context.bot.send_message(
                    chat_id=clb_query.from_user.id,
                    text="No path found between the selected points."
                )
        except Exception as e:
            self.log.error(f"Error in '_compute_shortest_path': {e}")
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text="An error occurred while calculating the shortest path."
            )
            return

    async def command_cancel(self, update, context):
        await update.message.reply_text("Command canceled.")
        return ConversationHandler.END
