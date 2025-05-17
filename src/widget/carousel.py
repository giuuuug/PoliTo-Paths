from typing import Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from abc import ABC, abstractmethod

class CarouselWidget(ABC):
    def __init__(self):
        self._curr_page = 0 

    def get_curr_page(self) -> int:
        """
        Getter method to retrieve the current page.
        """
        return self._curr_page

    def set_curr_page(self, page: int) -> None:
        """
        Setter method to update the current page.
        """
        if page < 0:
            raise ValueError("Page number cannot be negative.")
        self._curr_page = page

    @abstractmethod
    def get(self, options: list[dict[str, Any]], max_cols: int = 2, max_rows: int = 3) -> InlineKeyboardMarkup:
        """
        Abstract method to generate the carousel body (keyboard markup).
        Must be implemented by subclasses.
        """
        pass

    def set_curr_page_from_navigation(self, srt: str):
        direction = srt.split(":", 1)[1]
        if direction == "prev":
            self._curr_page -= 1
        elif direction == "next":
            self._curr_page += 1



