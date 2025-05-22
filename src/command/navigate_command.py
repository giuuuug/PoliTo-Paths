# navigate_command.py
from telegram import InputMediaPhoto, Update
from telegram.ext import ContextTypes, ConversationHandler
from widget.carousel_impl import CarouselImpl
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths
from utils.log import Log
from enum import Enum
from command.command_handler import CommandHandler

SOURCE, DESTINATION, NAVIGATION, FINISH = range(4)
NAV_STEP_STATE_1, NAV_STEP_STATE_2, NAV_STEP_STATE_3, NAV_STEP_STATE_4, NAV_STEP_STATE_5, NAV_STEP_NUM = range(6)

SOURCE_CLBK_DATA: str = "source"
DESTINATION_CLBK_DATA: str = "destination"
NAVIGATION_CLBK_DATA: str = "navigation"

class NavigateCommand(CommandHandler):
    def __init__(self, database: DatabasePostgreSQLPolitoPaths = None):
        super().__init__(log=Log(self.__class__.__name__), database=database)

    def _reset_user_state(self, context, user_id=None):
        # Se non viene fornito un user_id, non fare nulla
        if user_id is None and not hasattr(context, 'user_id_key'):
            return
            
        # Usa l'ID utente come chiave per memorizzare i dati
        user_id_key = user_id if user_id else context.user_id_key
        
        # Inizializza il dizionario per questo utente se non esiste
        if user_id_key not in context.user_data:
            context.user_data[user_id_key] = {}
            
        # Resetta lo stato dell'utente
        context.user_data[user_id_key] = {
            'question_state': SOURCE,
            'sel_source': '6i',
            'sel_destination': '5i',
            'navigation_step_state': NAV_STEP_STATE_1,
            'source_carousel': CarouselImpl(),
            'destination_carousel': CarouselImpl(),
            'navigation_carousel': CarouselImpl()
        }

    async def _send_message(self, update_or_query, context):
        # Ottieni l'ID utente dall'update o dalla query
        if isinstance(update_or_query, Update):
            user_id = update_or_query.effective_user.id
        else:  # CallbackQuery
            user_id = update_or_query.from_user.id
            
        # Memorizza l'ID utente nel context per uso futuro
        context.user_id_key = user_id
        
        # Assicurati che i dati dell'utente esistano
        if user_id not in context.user_data or not context.user_data[user_id]:
            self._reset_user_state(context, user_id)
            
        # Ottieni i dati specifici dell'utente
        user_data = context.user_data[user_id]
        question_state = user_data.get('question_state', SOURCE)
        caption = ""
        
        if question_state == SOURCE:
            question = "\U0001F4CD Select your starting point\n\nWhere are you currently located?"
            options = user_data['source_carousel'].get_markup(SOURCE_CLBK_DATA, user_data['rooms'])
        elif question_state == DESTINATION:
            question = "\U0001F4CD Select your destination\n\nWhere do you want to go?"
            options = user_data['destination_carousel'].get_markup(DESTINATION_CLBK_DATA, user_data['rooms'])
        elif question_state == NAVIGATION:
            nav_state = user_data['navigation_step_state']
            caption = user_data['navigation_steps'][nav_state][1]
            options = user_data['navigation_carousel'].get_markup(NAVIGATION_CLBK_DATA, user_data['navigation_steps'], max_cols=1, max_rows=1)

        if isinstance(update_or_query, Update):
            if question_state == NAVIGATION:
                with open(user_data['navigation_steps'][user_data['navigation_step_state']][0], 'rb') as img:
                    await update_or_query.message.reply_photo(photo=img, caption=caption, parse_mode='Markdown', reply_markup=options)
            else:
                await update_or_query.message.reply_text(question, reply_markup=options)
        else:
            if question_state == NAVIGATION:
                with open(user_data['navigation_steps'][user_data['navigation_step_state']][0], 'rb') as img:
                    await update_or_query.edit_message_media(media=InputMediaPhoto(media=img, caption=caption, parse_mode='Markdown'), reply_markup=options)
            else:
                await update_or_query.edit_message_text(question, reply_markup=options)

    async def command_start(self, update, context):
        # Ottieni l'ID utente
        user_id = update.effective_user.id
        context.user_id_key = user_id
        
        # Esegui la query per ottenere le stanze
        query = "SELECT ogc_fid, room_names FROM xs01_p ORDER BY room_names"
        with self.database as db:
            results = db.execute_query(query)

        rooms = [
            [int(row[0]), row[1].strip().upper()]
            for row in results
            if row and row[0] is not None and row[1] is not None
        ]

        # Resetta lo stato dell'utente
        self._reset_user_state(context, user_id)
        
        # Ottieni i dati specifici dell'utente
        user_data = context.user_data[user_id]
        
        # Aggiorna i dati dell'utente
        user_data['rooms'] = rooms
        user_data['navigation_steps'] = [
            ['img/istr_no_bg/map_no_bg.jpg', f"\U0001F3AF *Navigation Instructions*\n- Source: {user_data['sel_source']}\n- Destination: {user_data['sel_destination']}"],
            ['img/istr_no_bg/istr_1_no_bg.jpg', "*Step 1* \nStart walking straight ahead for 10 meters along the corridor"],
            ['img/istr_no_bg/istr_3_no_bg.jpg', "*Step 2* \nContinue straight for 43 meters"],
            ['img/istr_no_bg/istr_5_no_bg.jpg', "*Step 3* \nProceed straight ahead for 7 meters"],
            ['img/istr_no_bg/istr_5_no_bg.jpg', "\U0001F389 *You've arrived!*\nYour destination is on your left side.\n\nHave a great day! \U0001F31F"],
        ]

        await self._send_message(update, context)
        return SOURCE

    async def handle_question(self, update, context):
        clb_query = update.callback_query
        await clb_query.answer()
        user_answer = clb_query.data
        
        # Ottieni l'ID utente
        user_id = clb_query.from_user.id
        context.user_id_key = user_id
        
        # Assicurati che i dati dell'utente esistano
        if user_id not in context.user_data or not context.user_data[user_id]:
            self._reset_user_state(context, user_id)
            
        # Ottieni i dati specifici dell'utente
        user_data = context.user_data[user_id]
        question_state = user_data.get('question_state', SOURCE)

        if user_answer.startswith((f'{SOURCE_CLBK_DATA}:next', f'{SOURCE_CLBK_DATA}:prev')):
            user_data['source_carousel'].set_curr_page_from_answer(user_answer)
            await self._send_message(clb_query, context)
            return question_state

        elif user_answer.startswith((f'{DESTINATION_CLBK_DATA}:next', f'{DESTINATION_CLBK_DATA}:prev')):
            user_data['destination_carousel'].set_curr_page_from_answer(user_answer)
            await self._send_message(clb_query, context)
            return question_state

        elif user_answer.startswith((f'{NAVIGATION_CLBK_DATA}:next', f'{NAVIGATION_CLBK_DATA}:prev')):
            if user_answer.endswith('next'):
                user_data['navigation_step_state'] += 1
            elif user_answer.endswith('prev'):
                user_data['navigation_step_state'] -= 1
            user_data['navigation_carousel'].set_curr_page_from_answer(user_answer)
            await self._send_message(clb_query, context)
            return question_state

        elif user_answer == 'cancel':
            return await self.command_cancel(clb_query, context)

        else:
            if question_state == SOURCE:
                user_data['sel_source'] = user_answer.split()[1]
                user_data['question_state'] = DESTINATION
                await self._send_message(clb_query, context)
                return DESTINATION

            elif question_state == DESTINATION:
                user_data['sel_destination'] = user_answer.split()[1]
                if user_data['sel_source'] != '6I' or user_data['sel_destination'] != '5I':
                    self.log.info("Invalid source and destination")
                    await clb_query.edit_message_text("An error occurred.\nThis demo is only available for:\n- 6i (Source)\n- 5i (Destination). \n\nPlease rerun the /navigate command.")
                    return ConversationHandler.END
                user_data['question_state'] = NAVIGATION
                await self._send_message(clb_query, context)
                return NAVIGATION
            else:
                self.log.error("Invalid question state")
                await clb_query.edit_message_text("An error occurred. Please try again.")
                return ConversationHandler.END

    async def command_cancel(self, update_or_query, context):
        # Ottieni l'ID utente
        if isinstance(update_or_query, Update):
            user_id = update_or_query.effective_user.id
        else:  # CallbackQuery
            user_id = update_or_query.from_user.id
            
        # Memorizza l'ID utente nel context per uso futuro
        context.user_id_key = user_id
        
        try:
            if isinstance(update_or_query, Update):
                await update_or_query.message.reply_text("Operation cancelled. Please rerun the /navigate command again.")
            else:
                await update_or_query.edit_message_text("Operation cancelled. Please rerun the /navigate command again.")
        except Exception:
            chat_id = update_or_query.message.chat_id if hasattr(update_or_query, "message") else None
            if chat_id:
                await context.bot.send_message(chat_id=chat_id, text="Operation cancelled. Please rerun the /navigate command again.")

        # Resetta lo stato dell'utente specifico
        self._reset_user_state(context, user_id)
        return ConversationHandler.END
