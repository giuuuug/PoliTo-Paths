from typing import Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from widget.carousel import CarouselWidget

class SrcDestCarousel(CarouselWidget):
    def __init__(self):
        super().__init__()

    def get(self, options: list[dict[str, Any]], max_cols: int = 2, max_rows: int = 3) -> InlineKeyboardMarkup:
        """
        Returns the InlineKeyboardMarkup object for the carousel widget.
        """
        max_items = max_cols * max_rows
        tot_pages = (len(options) + max_items - 1) // max_items
        start_idx = self._curr_page * max_items
        end_idx = start_idx + max_items
        sliced_options = options[start_idx:end_idx]

        items = []

        # Dynamically create rows of buttons based on the options
        for i in range(0, len(sliced_options), max_cols):
            row = [
                InlineKeyboardButton(option, callback_data=option)
                for option in sliced_options[i:i + max_cols]
            ]
            items.append(row)

        # Add navigation buttons
        if self._curr_page > 0:
            items.append([InlineKeyboardButton(text='⬅️ Previous', callback_data='navigate:prev')])
        if self._curr_page < tot_pages - 1:
            items.append([InlineKeyboardButton(text='Next ➡️', callback_data='navigate:next')])

        return InlineKeyboardMarkup(items)


        
        
       