import os
import django
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import telebot
from telegram_bot.models import CustomUser, Image

# Загрузка переменных окружения
load_dotenv()

# Инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

# Импорт моделей CustomUser и Image


class Command(BaseCommand):
    help = "Телеграм-бот"

    def handle(self, *args, **options):
        bot.infinity_polling()
    

# Инициализация бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настройка логирования
log_file = 'bot.log'
max_log_size = 5 * 1024 * 1024  # 5 МБ
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
file_handler = RotatingFileHandler(filename=log_file, mode='a',
                                   maxBytes=max_log_size, backupCount=1)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s]: %(message)s'))
logging.getLogger().addHandler(file_handler)

# Путь к папке, которую бот будет просматривать
base_folder = os.path.join(settings.BASE_DIR, 'Instructions')

# Переменная для хранения выбранного пути
current_path = base_folder


@bot.message_handler(commands=['start'])
def handle_start(message):
    # Получаем информацию о пользователе из объекта сообщения
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Создаем или обновляем пользователя в базе данных
    user, created = CustomUser.objects.get_or_create(
        telegram_id=user_id,
        defaults={'username': username, 'first_name': first_name,
                  'last_name': last_name, 'access': 1}
    )

    # Проверяем, заблокирован ли пользователь
    if user.access == 1:
        # Пользователь заблокирован, отправляем сообщение с отказом в доступе
        bot.send_message(user_id, f'''Вам запрещен доступ к боту. Необходимо обратиться к вашему старшему инженеру для
        получения доступа. Обязательно необходимо предоставить Ваш ID.''')
        bot.send_message(user_id, f'Ваш ID {user_id}')
        return

    # Получаем файлы и папки в текущем каталоге
    files = []
    folders = []

    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)

    # Создаем клавиатуру с папками и файлами в качестве кнопок
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)

    # Добавляем кнопку "Инфо" в самом верху, только если текущий путь - базовый каталог
    if current_path == base_folder:
        keyboard.add('Инфо. Актуальные образы')
        keyboard.add('29 сеть')

    # Добавляем кнопку "Назад", если текущий путь не является базовым каталогом
    if current_path != base_folder:
        keyboard.add('Назад')

    for folder in folders:
        keyboard.add(folder)

    for file in files:
        keyboard.add(file)

    # Отправляем приветственное сообщение с клавиатурой
    bot.send_message(user_id, "Выберите папку или файл:", reply_markup=keyboard)


# Обработчик кнопок с папками и файлами
@bot.message_handler(func=lambda message: True)
def handle_folder_or_file(message):
    global current_path

    try:
        # Получаем пользователя по id
        user = CustomUser.objects.get(id=message.from_user.id)
        # Проверяем, заблокирован ли пользователь
        if user.blok == 1:
            # Пользователь заблокирован, отправляем сообщение с отказом в доступе
            bot.send_message(message.from_user.id, "Вам запрещен доступ к боту.")
            return

        chosen_item = message.text
        chosen_item_path = os.path.join(current_path, chosen_item)

        if chosen_item == 'Назад':
            # Если выбрана кнопка "Назад", обновляем текущий путь на родительскую папку
            parent_path = os.path.dirname(current_path)
            if parent_path.startswith(base_folder):
                current_path = parent_path
            else:
                bot.send_message(message.from_user.id, "Вы достигли верхней директории.")
                return
            handle_start(message)
            file_size = os.path.getsize(chosen_item_path)
            # Проверяем, если размер файла больше 50 МБ (в байтах)
            if file_size > 50 * 1024 * 1024:
                bot.send_message(message.from_user.id, "Файлы размером более 50 МБ нельзя скачивать."
                                                        "Для скачивания файлов большого объема,"
                                                        "подключитесь к FTP в соответствующий раздел")
                logging.info(f"Запрос файла объемом более 50 МБ {current_path}, файл {chosen_item}"
                             f" запросил пользователь ID {message.from_user.id}")
            else:
                # Если выбран файл, и его размер допустим, отправляем его пользователю
                with open(chosen_item_path, 'rb') as f:
                    bot.send_document(message.from_user.id, f)
        elif os.path.isdir(chosen_item_path):
            # Проверяем, если выбрана папка, но она выше базовой папки
            if not chosen_item_path.startswith(base_folder):
                bot.send_message(message.from_user.id, "Вы достигли верхней директории.")
                return

            # Если выбрана папка, обновляем текущий путь и отправляем список файлов и папок
            current_path = chosen_item_path
            handle_start(message)

    except Exception as e:
        # Записываем ошибку в лог и уведомляем пользователя о неполадке
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.from_user.id, "Произошла ошибка при выполнении операции. Пожалуйста, попробуйте еще раз.")


# Обработчик кнопки "Инфо"
@bot.message_handler(func=lambda message: message.text == 'Инфо. Актуальные образы')
def handle_info(message):
    try:
        # Получаем все объекты модели Image
        images = Image.objects.all()

        if images.exists():
            info_messages = []
            for image in images:
                info_message = f"Актуальные образы {image.ts} :\n"
                info_message += f"\n"
                info_message += f"\n"
                info_message += f"BO: {image.bo}\n"
                info_message += f"\n"
                info_message += f"POS все кроме HP и NCR XR4: {image.pos}\n"
                info_message += f"\n"
                info_message += f"POS HP и NCR XR4: {image.sco}\n"
                info_message += f"\n"
                info_message += f"КСО: {image.pc}\n"
                info_message += f"\n"
                info_message += f"PC: {image.pc}\n"
                info_messages.append(info_message)

            # Отправляем сообщения с информацией
            for info_message in info_messages:
                bot.send_message(message.from_user.id, info_message)
        else:
            bot.send_message(message.from_user.id, "В таблице images нет данных для отображения.")

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.from_user.id, "Произошла ошибка при выполнении операции. Пожалуйста, попробуйте еще раз.")


# Запускаем бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
