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

    def _reset_user_state(self, context):
        context.user_data.clear()
        context.user_data['question_state'] = SOURCE
        context.user_data['sel_source'] = '6i'
        context.user_data['sel_destination'] = '5i'
        context.user_data['navigation_step_state'] = NAV_STEP_STATE_1
        context.user_data['source_carousel'] = CarouselImpl()
        context.user_data['destination_carousel'] = CarouselImpl()
        context.user_data['navigation_carousel'] = CarouselImpl()

    async def _send_message(self, update_or_query, context):
        question_state = context.user_data.get('question_state', SOURCE)
        caption = ""
        
        if question_state == SOURCE:
            question = "\U0001F4CD Select your starting point\n\nWhere are you currently located?"
            options = context.user_data['source_carousel'].get_markup(SOURCE_CLBK_DATA, context.user_data['rooms'])
        elif question_state == DESTINATION:
            question = "\U0001F4CD Select your destination\n\nWhere do you want to go?"
            options = context.user_data['destination_carousel'].get_markup(DESTINATION_CLBK_DATA, context.user_data['rooms'])
        elif question_state == NAVIGATION:
            nav_state = context.user_data['navigation_step_state']
            caption = context.user_data['navigation_steps'][nav_state][1]
            options = context.user_data['navigation_carousel'].get_markup(NAVIGATION_CLBK_DATA, context.user_data['navigation_steps'], max_cols=1, max_rows=1)

        if isinstance(update_or_query, Update):
            if question_state == NAVIGATION:
                with open(context.user_data['navigation_steps'][context.user_data['navigation_step_state']][0], 'rb') as img:
                    await update_or_query.message.reply_photo(photo=img, caption=caption, parse_mode='Markdown', reply_markup=options)
            else:
                await update_or_query.message.reply_text(question, reply_markup=options)
        else:
            if question_state == NAVIGATION:
                with open(context.user_data['navigation_steps'][context.user_data['navigation_step_state']][0], 'rb') as img:
                    await update_or_query.edit_message_media(media=InputMediaPhoto(media=img, caption=caption, parse_mode='Markdown'), reply_markup=options)
            else:
                await update_or_query.edit_message_text(question, reply_markup=options)

    async def command_start(self, update, context):
        query = "SELECT ogc_fid, room_names FROM xs01_p ORDER BY room_names"
        with self.database as db:
            results = db.execute_query(query)

        rooms = [
            [int(row[0]), row[1].strip().upper()]
            for row in results
            if row and row[0] is not None and row[1] is not None
        ]

        self._reset_user_state(context)
        context.user_data['rooms'] = rooms
        context.user_data['navigation_steps'] = [
            ['img/istr_no_bg/map_no_bg.jpg', f"\U0001F3AF *Navigation Instructions*\n- Source: {context.user_data['sel_source']}\n- Destination: {context.user_data['sel_destination']}"],
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
        question_state = context.user_data.get('question_state', SOURCE)

        if user_answer.startswith((f'{SOURCE_CLBK_DATA}:next', f'{SOURCE_CLBK_DATA}:prev')):
            context.user_data['source_carousel'].set_curr_page_from_answer(user_answer)
            await self._send_message(clb_query, context)
            return question_state

        elif user_answer.startswith((f'{DESTINATION_CLBK_DATA}:next', f'{DESTINATION_CLBK_DATA}:prev')):
            context.user_data['destination_carousel'].set_curr_page_from_answer(user_answer)
            await self._send_message(clb_query, context)
            return question_state

        elif user_answer.startswith((f'{NAVIGATION_CLBK_DATA}:next', f'{NAVIGATION_CLBK_DATA}:prev')):
            if user_answer.endswith('next'):
                context.user_data['navigation_step_state'] += 1
            elif user_answer.endswith('prev'):
                context.user_data['navigation_step_state'] -= 1
            context.user_data['navigation_carousel'].set_curr_page_from_answer(user_answer)
            await self._send_message(clb_query, context)
            return question_state

        elif user_answer == 'cancel':
            return await self.command_cancel(clb_query, context)

        else:
            if question_state == SOURCE:
                context.user_data['sel_source'] = user_answer.split()[1]
                context.user_data['question_state'] = DESTINATION
                await self._send_message(clb_query, context)
                return DESTINATION

            elif question_state == DESTINATION:
                context.user_data['sel_destination'] = user_answer.split()[1]
                if context.user_data['sel_source'] != '6I' or context.user_data['sel_destination'] != '5I':
                    self.log.info("Invalid source and destination")
                    await clb_query.edit_message_text("This demo is only available for:\n- 6i (Source)\n- 5i (Destination). Please start again.")
                    return ConversationHandler.END
                context.user_data['question_state'] = NAVIGATION
                await self._send_message(clb_query, context)
                return NAVIGATION
            else:
                self.log.error("Invalid question state")
                await clb_query.edit_message_text("An error occurred. Please try again.")
                return ConversationHandler.END

    async def command_cancel(self, update_or_query, context):
        try:
            if isinstance(update_or_query, Update):
                await update_or_query.message.reply_text("Operation cancelled. Please start again.")
            else:
                await update_or_query.edit_message_text("Operation cancelled. Please start again.")
        except Exception:
            chat_id = update_or_query.message.chat_id if hasattr(update_or_query, "message") else None
            if chat_id:
                await context.bot.send_message(chat_id=chat_id, text="Operation cancelled. Please start again.")

        self._reset_user_state(context)
        return ConversationHandler.END
