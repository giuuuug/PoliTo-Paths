from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from widget.carousel import CarouselWidget
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths
from utils.log import Log
from enum import Enum
from command.command_handler import CommandHandler
import geopandas as gpd
from shapely.wkb import loads
from shapely import wkt
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt
import io
import psycopg2
import tempfile
from PIL import Image

class NavigateCommandState(Enum):
    NAVIGATE_COMMAND_STATE_1_Q = 0
    NAVIGATE_COMMAND_STATE_2_Q = 1
    NAVIGATE_COMMAND_STATE_NUM = 2

# Define states for the conversation
QUESTION_1, QUESTION_2 = range(2)

class NavigateCommand(CommandHandler):
    def __init__(self, database: DatabasePostgreSQLPolitoPaths = None):
        super().__init__(log=Log(self.__class__.__name__), database=database)
        self.carousel = CarouselWidget()
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

    async def _send_question(self, update_or_query, context):
        user_id = update_or_query.effective_user.id if isinstance(update_or_query, Update) else update_or_query.from_user.id
        user_data = self._get_user_data(user_id)
        
        question = user_data['questions'][user_data['state']]
        btn_grid = self.carousel.get_grid(options=[list(opt.values())[0] for opt in question["options"]])

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
        await self._send_question(update, context)
        return QUESTION_1
    
    async def handle_question(self, update, context):
        clb_query = update.callback_query
        user_id = clb_query.from_user.id
        
        # Get user state
        user_data = self._get_user_data(user_id)
        
        await clb_query.answer()
        user_answer = clb_query.data
        
        if user_answer.startswith("navigate:"):
            self.carousel.set_curr_page_from_navigation(user_answer)
            await self._send_question(clb_query, context)
            return user_data['state']
        
        user_data['answers'].append(user_answer)
        
        user_data['state'] += 1
        self.carousel.set_curr_page(0)
        if user_data['state'] < NavigateCommandState.NAVIGATE_COMMAND_STATE_NUM.value:
            await self._send_question(clb_query, context)
            return QUESTION_2
        else:
            await self._compute_shortest_path(clb_query, context)
            # Clear user data after navigation is complete
            self._clear_user_data(user_id)
            return ConversationHandler.END

    async def _compute_shortest_path(self, clb_query, context: ContextTypes.DEFAULT_TYPE):
        user_id = clb_query.from_user.id
        user_data = self._get_user_data(user_id)
        
        try:
            await clb_query.edit_message_text(f"🔍 Finding the best path from {user_data['answers'][0].upper()} to {user_data['answers'][1].upper()}")
            self.log.info(f"Calculating shortest path from {user_data['answers'][0].upper()} to {user_data['answers'][1].upper()}")
            
            source_point_as_num = next(
                (key for opt in user_data['questions'][0]["options"] for key, value in opt.items() if value == user_data['answers'][0]),
                None
            )
            destination_point_as_num = next(
                (key for opt in user_data['questions'][1]["options"] for key, value in opt.items() if value == user_data['answers'][1]),
                None
            )
            
            self.log.info(f"Source point as number: {source_point_as_num} Destination point as number: {destination_point_as_num}")

            # Special case for path from point 65 (classroom 6i) to point 74 (classroom 5i)
            if source_point_as_num == '65' and destination_point_as_num == '74':
                version_no_bg = True
                
                photo = 'img/istr_no_bg/map_no_bg.jpg' if version_no_bg else 'img/istr_w_bg/map_w_bg.jpg'
                await context.bot.send_photo(
                    chat_id=clb_query.message.chat_id,
                    photo=photo,
                    caption="🎯 *Navigation Instructions*\nFollow these steps to reach your destination:\n",
                    parse_mode='Markdown'
                )

                # Message 1
                photo = 'img/istr_no_bg/istr_1_no_bg.jpg' if version_no_bg else 'img/istr_w_bg/istr_1_w_bg.jpg'
                await context.bot.send_photo(
                    chat_id=clb_query.message.chat_id,
                    photo=photo,
                    caption="*Step 1* \nStart walking straight ahead for 10 meters along the corridor",
                    parse_mode='Markdown'
                )
                
                # Message 2
                photo = 'img/istr_no_bg/istr_2_no_bg.jpg' if version_no_bg else 'img/istr_w_bg/istr_2_w_bg.jpg'
                await context.bot.send_photo(
                    chat_id=clb_query.message.chat_id,
                    photo=photo,
                    caption="*Step 2* \nAt the intersection, make a left turn",
                    parse_mode='Markdown'
                )
                
                # Message 3
                photo = 'img/istr_no_bg/istr_3_no_bg.jpg' if version_no_bg else 'img/istr_w_bg/istr_3_w_bg.jpg'
                await context.bot.send_photo(
                    chat_id=clb_query.message.chat_id,
                    photo=photo,
                    caption="*Step 3* \nContinue straight for 43 meters",
                    parse_mode='Markdown'
                )
                
                # Message 4
                photo = 'img/istr_no_bg/istr_4_no_bg.jpg' if version_no_bg else 'img/istr_w_bg/istr_4_w_bg.jpg'
                await context.bot.send_photo(
                    chat_id=clb_query.message.chat_id,
                    photo=photo,
                    caption="*Step 4* \nWhen you reach the next intersection, turn left",
                    parse_mode='Markdown'
                )
                
                # Message 5
                photo = 'img/istr_no_bg/istr_5_no_bg.jpg' if version_no_bg else 'img/istr_w_bg/istr_5_w_bg.jpg'
                await context.bot.send_photo(
                    chat_id=clb_query.message.chat_id,
                    photo=photo,
                    caption="*Step 5* \nProceed straight ahead for 7 meters",
                    parse_mode='Markdown'
                )
                
                # Message 6
                await context.bot.send_message(
                    chat_id=clb_query.message.chat_id,
                    text="🎉 *You've arrived!*\nYour destination (classroom 5i) is on your left side.\n\nHave a great day! 🌟",
                    parse_mode='Markdown'
                )
                return ConversationHandler.END
            
            # Regular path computation for all other cases
            # Ensure database connection is active and execute query
            self.database.connect()
            try:
                source_point = int(source_point_as_num)
                dest_point = int(destination_point_as_num)
                params = (source_point, dest_point)
                navigation_steps = self.database.execute_query("""
                    SELECT 
                        step_number,
                        direction,
                        distance_meters,
                        next_turn,
                        landmark_name
                    FROM compute_navigation_instructions(%s, %s)
                """, params)
            finally:
                self.database.close()

            if not navigation_steps:
                await context.bot.send_message(
                    chat_id=clb_query.message.chat_id,
                    text="Sorry, couldn't find a path between these points."
                )
                return

            # Calcola la distanza totale
            total_distance = sum(step[2] for step in navigation_steps if step[2] is not None)
           
            # Invia solo il messaggio testuale
            await context.bot.send_message(
                chat_id=clb_query.message.chat_id,
                text=f"Route found! Total distance: {total_distance:.1f} meters\nFollowing the navigation steps..."
            )
            
            # Invia ogni passo della navigazione
            for i, step in enumerate(navigation_steps):
                direction = step[1]  # direction
                distance = step[2]   # distance_meters
                next_turn = step[3]  # next_turn
                landmark = step[4]   # landmark_name
                
                # Costruisci il messaggio di navigazione
                message = []
                if i == 0:
                    message.append("🚶 Starting point")
                
                # Aggiungi l'indicazione sulla direzione
                if direction:
                    message.append(f"➡️ {direction}")
                
                # Aggiungi la distanza fino al prossimo punto
                if distance:
                    message.append(f"📏 Continue for {distance:.1f} meters")
                
                # Aggiungi informazioni sui punti di riferimento
                if landmark:
                    message.append(f"🏢 You will pass by: {landmark}")
                
                # Aggiungi informazione sulla prossima svolta
                if next_turn:
                    message.append(f"⚠️ Get ready to: {next_turn}")
                
                if i == len(navigation_steps) - 1:
                    message.append("🎯 You have reached your destination!")
                
                # Invia il messaggio con l'eventuale immagine associata
                image_path = self._get_direction_image(direction)
                if image_path:
                    photo = self._resize_image(image_path)
                    await context.bot.send_photo(
                        chat_id=clb_query.message.chat_id,
                        photo=photo,
                        caption="\n".join(message)
                    )
                else:
                    await context.bot.send_message(
                        chat_id=clb_query.message.chat_id,
                        text="\n".join(message)
                    )
        except Exception as e:
            self.log.error(f"Error in _compute_shortest_path: {e}")
            await context.bot.send_message(
                chat_id=clb_query.message.chat_id,
                text="Sorry, an error occurred while calculating the path. Please try again."
            )

    def _get_direction_image(self, direction: str) -> str:
        """Restituisce il percorso dell'immagine associata alla direzione."""
        direction_images = {
            'Turn right': 'img/turn-right.png',
            'Turn left': 'img/turn-left.png',
            'Continue straight': 'img/ahead-only.png'
        }
        return direction_images.get(direction)

    async def command_cancel(self, update, context):
        """Handle command cancellation and clear user state"""
        user_id = update.effective_user.id
        self._clear_user_data(user_id)
        await update.message.reply_text("Navigation canceled.")
        return ConversationHandler.END

