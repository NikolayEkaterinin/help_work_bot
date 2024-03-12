import subprocess
import threading
from time import sleep

def run_django_server():
    subprocess.run(["python", "manage.py", "runserver"])

def run_telegram_bot():
    subprocess.run(["python", "manage.py", "bot"])

if __name__ == "__main__":
    django_thread = threading.Thread(target=run_django_server)
    django_thread.start()
    django_thread.join()  # Дождаться завершения работы Django сервера

    sleep(5)  # Подождать некоторое время перед запуском бота

    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.start()
    bot_thread.join()  # Дождаться завершения работы телеграм-бота
