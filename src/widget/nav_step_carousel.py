from typing import Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from widget.carousel import CarouselWidget

class NavStepCarousel(CarouselWidget):
    def __init__(self):
        super().__init__()

    def get(self, steps: list[dict[str, Any]]) -> dict:
        """
        Returns a dict with 'image', 'caption', and 'keyboard' for the current navigation step.
        Each step in steps should be a dict with keys: 'image' (str, path), 'caption' (str).
        """
        total_steps = len(steps)
        # Clamp current page to valid range
        if self._curr_page < 0:
            self._curr_page = 0
        if self._curr_page >= total_steps:
            self._curr_page = total_steps - 1
        step = steps[self._curr_page]
        # Navigation buttons
        buttons = []
        if self._curr_page > 0:
            buttons.append(InlineKeyboardButton(text='⬅️ Previous', callback_data='navigate:prev'))
        if self._curr_page < total_steps - 1:
            buttons.append(InlineKeyboardButton(text='Next ➡️', callback_data='navigate:next'))
        keyboard = InlineKeyboardMarkup([buttons]) if buttons else None
        return {
            'image': step['image'],
            'caption': step['caption'],
            'keyboard': keyboard
        }




