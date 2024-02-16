import subprocess
import threading


def run_django_server():
    subprocess.run(["python", "manage.py", "runserver"])


def run_telegram_bot():
    subprocess.run(["python", "manage.py", "bot"])


if __name__ == "__main__":
    django_thread = threading.Thread(target=run_django_server)
    bot_thread = threading.Thread(target=run_telegram_bot)

    django_thread.start()
    bot_thread.start()

    django_thread.join()
    bot_thread.join()
    