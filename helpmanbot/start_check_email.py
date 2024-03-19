import os
import django
import requests
import time
from dotenv import load_dotenv
# Установка переменной окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helpmanbot.settings")

# Инициализация Django
django.setup()
from send_mail.views import check_emails

load_dotenv()

# Получение настроек из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Период проверки наличия ответных писем (1 минута)
CHECK_INTERVAL = 10

def main():
    # Запускаем бесконечный цикл проверки почты
    while True:
        check_emails()
        # Ждем определенный период времени (в секундах) перед следующей проверкой
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
