from telegram_bot import TelegramBot

if __name__ == '__main__':
    with open("telegram.token", "r") as file:
        token = file.read().strip()
    bot = TelegramBot(token=token)
    bot.run()