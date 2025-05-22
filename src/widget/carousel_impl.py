from typing import Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from widget.carousel_ABC import CarouselABC



class CarouselImpl(CarouselABC):
    def __init__(self):
        super().__init__()

    def get_markup(self, callback_data:str, options: list[list[Any,Any]], max_cols: int = 2, max_rows: int = 3) -> InlineKeyboardMarkup:
        """
        Returns the InlineKeyboardMarkup object for the carousel widget.
        """
        max_items = max_cols * max_rows
        tot_pages = (len(options) + max_items - 1) // max_items
        start_idx = self._curr_page * max_items
        end_idx = start_idx + max_items
        sliced_options = options[start_idx:end_idx]

        items = []

        if (isinstance(options, list) and all(isinstance(item, list) and len(item) == 2 and isinstance(item[0], int) and isinstance(item[1], str) for item in options)):
            for i in range(0, len(sliced_options), max_cols):
                row = [
                    InlineKeyboardButton(option[1], callback_data=f'{callback_data}:{option[0]}:{option[1]}')
                    for option in sliced_options[i:i + max_cols]
                ]
                items.append(row)
        

        # Add navigation buttons
        if self._curr_page < tot_pages - 1:
            items.append([InlineKeyboardButton(text='Next ➡️', callback_data=f'{callback_data}:next')])
        if self._curr_page > 0:
            items.append([InlineKeyboardButton(text='⬅️ Previous', callback_data=f'{callback_data}:prev')])
            
        items.append([InlineKeyboardButton(text='Cancel', callback_data=f'cancel')])

        return InlineKeyboardMarkup(items)
