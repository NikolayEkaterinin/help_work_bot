import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telegram_bot.apps.TelegramBotConfig")
    from telegram_bot.main import main
    main()