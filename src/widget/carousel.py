from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class CarouselWidget:
    def __init__(self, message: str, items: list[str]):
        self.message = message
        self.items = items
        self.items_per_page = 6
        self.current_page = 0
        self.selected_value = None

    def get_keyboard(self):
        # Calculate the start and end indices for the current page
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        page_items = self.items[start_index:end_index]

        # Create buttons for the current page
        keyboard = []
        for i in range(0, len(page_items), 2):
            row = [
                InlineKeyboardButton(page_items[i], callback_data=f"select:{page_items[i]}"),
            ]
            if i + 1 < len(page_items):
                row.append(InlineKeyboardButton(page_items[i + 1], callback_data=f"select:{page_items[i + 1]}"))
            keyboard.append(row)

        # Add navigation buttons
        nav_buttons = []
        if self.current_page > 0:
            nav_buttons.append(InlineKeyboardButton("Previous", callback_data="navigate:prev"))
        if end_index < len(self.items):
            nav_buttons.append(InlineKeyboardButton("Next", callback_data="navigate:next"))
        if nav_buttons:
            keyboard.append(nav_buttons)

        return InlineKeyboardMarkup(keyboard)