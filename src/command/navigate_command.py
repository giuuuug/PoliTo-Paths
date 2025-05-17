from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler
from widget.src_dest_carousel import SrcDestCarousel
from widget.nav_step_carousel import NavStepCarousel
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths
from utils.log import Log
from enum import Enum
from command.command_handler import CommandHandler

class NavigateCommandState(Enum):
    NAVIGATE_COMMAND_STATE_1_Q = 0
    NAVIGATE_COMMAND_STATE_2_Q = 1
    NAVIGATE_COMMAND_STATE_NUM = 2

class NavigationStepState(Enum):
    NAV_STEP = 100

QUESTION_1, QUESTION_2 = range(2)

class NavigateCommand(CommandHandler):
    def __init__(self, database: DatabasePostgreSQLPolitoPaths = None):
        super().__init__(log=Log(self.__class__.__name__), database=database)
        self.src_dest_carousel = SrcDestCarousel()
        self.nav_step_carousel = NavStepCarousel()
        # Dictionary to store user-specific data
        self.user_states = {}

    def _get_user_data(self, user_id: int):
        """Get or create user-specific data"""
        if user_id not in self.user_states:
            self.user_states[user_id] = {
                'state': NavigateCommandState.NAVIGATE_COMMAND_STATE_1_Q.value,
                'answers': [],
                'questions': [],
                'navigation_instructions': [],
                'current_step': 0
            }
        return self.user_states[user_id]

    def _clear_user_data(self, user_id: int):
        """Clear user data when navigation is complete or canceled"""
        if user_id in self.user_states:
            del self.user_states[user_id]

    def clear_all_sessions(self):
        """Clear all user navigation sessions."""
        self.user_states.clear()
        
    async def _set_questions(self, update: Update):
        user_id = update.effective_user.id
        user_data = self._get_user_data(user_id)
        
        try:
            query = "SELECT id_0, room_names FROM xs01_p ORDER BY room_names"
            with self.database as db:
                results = db.execute_query(query)

            filtered_results = [
                {str(row[0]): row[1]}
                for row in results
                if row and row[0] is not None and row[1] is not None
            ]

            if not all(isinstance(list(opt.values())[0], str) for opt in filtered_results):
                raise ValueError(f"Query results must be a list of strings, got types: {[type(list(opt.values())[0]) for opt in filtered_results]}")

            self.log.info(f"Processed results: {filtered_results}")
            user_data['questions'] = [
                {'text': "📍 Select your starting point\nWhere are you currently located?", 'options': filtered_results},
                {'text': "📍 Select your destination\nWhere do you want to go?", 'options': filtered_results}
            ]

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

    async def _send_src_dest_question(self, update_or_query, context):
        user_id = update_or_query.effective_user.id if isinstance(update_or_query, Update) else update_or_query.from_user.id
        user_data = self._get_user_data(user_id)
        
        question = user_data['questions'][user_data['state']]
        btn_grid = self.src_dest_carousel.get(options=[list(opt.values())[0] for opt in question["options"]])

        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text(question["text"], reply_markup=btn_grid)
        else:
            await update_or_query.edit_message_text(question["text"], reply_markup=btn_grid)
            
    
    async def command_start(self, update, context):
        user_id = update.effective_user.id
        
        # Check if user is already in a navigation session
        if user_id in self.user_states:
            await update.message.reply_text(
                "You already have an active navigation session. Please complete it or use /cancel to start a new one."
            )
            return ConversationHandler.END
        
        # Initialize user state
        user_data = self._get_user_data(user_id)
        user_data['state'] = NavigateCommandState.NAVIGATE_COMMAND_STATE_1_Q.value
        user_data['answers'] = []
        user_data['questions'] = []
        
        await self._set_questions(update)
        await self._send_src_dest_question(update, context)
        return QUESTION_1
    
    async def handle_question(self, update, context):
        clb_query = update.callback_query
        user_id = clb_query.from_user.id
        
        # Get user state
        user_data = self._get_user_data(user_id)
        
        await clb_query.answer()
        user_answer = clb_query.data
        
        if user_answer.startswith("navigate:"):
            self.src_dest_carousel.set_curr_page_from_navigation(user_answer)
            await self._send_src_dest_question(clb_query, context)
            return user_data['state']
        
        user_data['answers'].append(user_answer)
        
        user_data['state'] += 1
        self.src_dest_carousel.set_curr_page(0)
        if user_data['state'] < NavigateCommandState.NAVIGATE_COMMAND_STATE_NUM.value:
            await self._send_src_dest_question(clb_query, context)
            return QUESTION_2
        else:
            # Compute path and transition to navigation state
            return await self._compute_shortest_path(clb_query, context)

    async def handle_navigation_callback(self, update, context):
        clb_query = update.callback_query
        user_id = clb_query.from_user.id
        
        # Get user state
        user_data = self._get_user_data(user_id)
        
        await clb_query.answer()
        user_answer = clb_query.data
        
        self.log.info(f"User {user_id} clicked navigation button: {user_answer}")
        
        if not user_answer.startswith("navigate:"):
            await clb_query.edit_message_text("Navigation session expired. Please start again.")
            return ConversationHandler.END
            
        self.nav_step_carousel.set_curr_page_from_navigation(user_answer)    
        step_idx = self.nav_step_carousel.get_curr_page()
        total_steps = len(user_data['navigation_instructions'])
        
        # Ensure step_idx stays within bounds
        if step_idx < 0:
            step_idx = 0
            self.nav_step_carousel.set_curr_page(0)
        if step_idx >= total_steps:
            step_idx = total_steps - 1
            self.nav_step_carousel.set_curr_page(total_steps - 1)

        # Update user state to ensure we stay in navigation mode
        user_data['state'] = NavigationStepState.NAV_STEP.value
        user_data['current_step'] = step_idx
        
        # Update the current step
        await self._show_navigation_step(clb_query.message.chat_id, context, user_id, step_idx)
        
        # End conversation if we're at the last step
        if step_idx == total_steps - 1:
            self._clear_user_data(user_id)
            return ConversationHandler.END
            
        return NavigationStepState.NAV_STEP.value

    async def _show_navigation_step(self, chat_id, context, user_id, step_idx):
        user_data = self._get_user_data(user_id)
        steps = user_data['navigation_instructions']
        self.nav_step_carousel.set_curr_page(step_idx)
        nav = self.nav_step_carousel.get(steps)

        # If this is a navigation update (not the first step), delete the previous message
        if hasattr(context, 'callback_query') and context.callback_query:
            try:
                await context.callback_query.message.delete()
            except Exception as e:
                self.log.error(f"Could not delete previous message: {e}")

        # Send new navigation message
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=nav['image'],
            caption=nav['caption'],
            parse_mode='Markdown',
            reply_markup=nav['keyboard']
        )
        user_data['current_step'] = step_idx

    async def _compute_shortest_path(self, clb_query, context: ContextTypes.DEFAULT_TYPE):
        user_id = clb_query.from_user.id
        user_data = self._get_user_data(user_id)
        source_point_as_num = next(
            (key for opt in user_data['questions'][0]["options"] for key, value in opt.items() if value == user_data['answers'][0]),
            None
        )
        destination_point_as_num = next(
            (key for opt in user_data['questions'][1]["options"] for key, value in opt.items() if value == user_data['answers'][1]),
            None
        )
        # Special case for path from point 65 (classroom 6i) to point 74 (classroom 5i)
        #if source_point_as_num == '65' and destination_point_as_num == '74':
        user_data['navigation_instructions'] = [
            {'image': 'img/istr_no_bg/map_no_bg.jpg', 'caption': "🎯 *Navigation Instructions*\nFollow these steps to reach your destination:\n"},
            {'image': 'img/istr_no_bg/istr_1_no_bg.jpg', 'caption': "*Step 1* \nStart walking straight ahead for 10 meters along the corridor"},
            {'image': 'img/istr_no_bg/istr_3_no_bg.jpg', 'caption': "*Step 2* \nContinue straight for 43 meters"},
            {'image': 'img/istr_no_bg/istr_5_no_bg.jpg', 'caption': "*Step 3* \nProceed straight ahead for 7 meters"},
            {'image': 'img/istr_no_bg/istr_5_no_bg.jpg', 'caption': "🎉 *You've arrived!*\nYour destination (classroom 5i) is on your left side.\n\nHave a great day! 🌟"}
        ]
        user_data['current_step'] = 0
        user_data['state'] = NavigationStepState.NAV_STEP.value
        await self._show_navigation_step(clb_query.message.chat_id, context, user_id, 0)
        return NavigationStepState.NAV_STEP.value
            
    async def command_cancel(self, update, context):
        """Handle command cancellation and clear user state"""
        user_id = update.effective_user.id
        self._clear_user_data(user_id)
        await update.message.reply_text("Navigation canceled.")
        return ConversationHandler.END

