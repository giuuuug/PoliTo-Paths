from telegram import InlineKeyboardMarkup
from abc import ABC, abstractmethod

class CarouselABC(ABC):
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
        
    def reset(self) -> None:
        """
        Resets the current page to the first page.
        """
        self._curr_page = 0 

    @abstractmethod
    def get_markup(self, options, max_cols: int = 2, max_rows: int = 3) -> InlineKeyboardMarkup:
        """
        Abstract method to generate the carousel body (keyboard markup).
        Must be implemented by subclasses.
        """
        pass

    def set_curr_page_from_answer(self, srt: str):
        direction = srt.split(":", 1)[1]
        if direction == "prev":
            self._curr_page -= 1
        elif direction == "next":
            self._curr_page += 1



