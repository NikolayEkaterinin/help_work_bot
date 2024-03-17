import os
import django
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import telebot
from telegram_bot.models import CustomUser, Image

from telegram_bot.views import process_29_network

from send_mail.email_templates import EmailTemplates
from send_mail.models import Item

email_templates = EmailTemplates()
descriptions = {}


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


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        # Получаем информацию о пользователе из объекта сообщения
        user_id = message.from_user.id

        # Пытаемся получить пользователя из базы данных
        user, created = CustomUser.objects.get_or_create(
            telegram_id=user_id,
            defaults={
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'access': 1
            }
        )

        # Проверяем, заблокирован ли пользователь
        if user.access == 1:
            # Пользователь заблокирован, отправляем сообщение с отказом в доступе
            bot.send_message(user_id, f'''Вам запрещен доступ к боту. Необходимо обратиться к вашему старшему инженеру для
            получения доступа. Обязательно необходимо предоставить Ваш ID.''')
            bot.send_message(user_id, f'Ваш ID {user_id}')
            return

        # После успешной авторизации отправляем клавиатуру с папками и файлами
        send_keyboard(message)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.from_user.id,
                         "Произошла ошибка при выполнении операции. Пожалуйста, попробуйте еще раз.")


def send_keyboard(message):
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
        keyboard.add('Обращение по ФР')

    # Добавляем кнопку "Назад", если текущий путь не является базовым каталогом
    if current_path != base_folder:
        keyboard.add('Назад')

    for folder in folders:
        keyboard.add(folder)

    for file in files:
        keyboard.add(file)

    # Отправляем клавиатуру с содержимым папки
    bot.send_message(message.from_user.id, "Выберите папку или файл:",
                     reply_markup=keyboard)


# Обработчик кнопки "Обращение по ФР"
@bot.message_handler(func=lambda message: message.text == 'Обращение по ФР')
def handle_fr_inquiry(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_atol = telebot.types.InlineKeyboardButton(text="АТОЛ", callback_data="atol")
    button_shtrih = telebot.types.InlineKeyboardButton(text="ШТРИХ", callback_data="shtrih")
    keyboard.row(button_atol, button_shtrih)
    bot.send_message(message.chat.id, "Добрый день! Выберите производителя ФР:", reply_markup=keyboard)


# Обработчик выбора производителя ФР
@bot.callback_query_handler(func=lambda call: call.data in ["atol", "shtrih"])
def handle_fr_vendor_selection(call):
    recipient_email = ""
    if call.data == "atol":
        handle_fr_vendor_selection(call)
        recipient_email = "eh37@ya.ru"
    elif call.data == "shtrih":
        handle_fr_vendor_selection(call)
        recipient_email = "n.ekaterinin@souyz76.ru"

# Обработчик выбора производителя ФР "АТОЛ"
@bot.callback_query_handler(func=lambda call: call.data in ["atol", "shtrih"])
def handle_fr_vendor_selection(call):
    if call.data == "atol":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Скрипт для смены заводского номера", callback_data="atol_serial_script")
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("Получение лицензий", callback_data="atol_licenses")
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("Скрипт для получения UIN", callback_data="atol_uin_script")
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("Данная модель не поддерживается", callback_data="atol_not_supported")
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("Мигратор на 5 платформу", callback_data="atol_platform_migrator")
        )
        bot.send_message(call.message.chat.id, "Выберите тему обращения:", reply_markup=keyboard)
    elif call.data == "shtrih":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("Смена заводского номера", callback_data="shtrih_serial_change")
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("Получение лицензий", callback_data="shtrih_licenses")
        )
        bot.send_message(call.message.chat.id, "Выберите тему для обращения:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "atol_serial_script")

def handle_email_button(call):
    # Запрашиваем модель и номера ЗН ККТ у пользователя
    bot.send_message(call.message.chat.id, "Введите модель ФР:")
    bot.register_next_step_handler(call.message, ask_model)

def ask_model(message):
    model = message.text
    bot.send_message(message.chat.id, "Введите номер ЗН ККТ в ремонте:")
    bot.register_next_step_handler(message, ask_repair_sn, model)

def ask_repair_sn(message, model):
    repair_sn = message.text
    bot.send_message(message.chat.id, "Введите номер ЗН ККТ подменная:")
    bot.register_next_step_handler(message, ask_substitute_sn, model, repair_sn)

def ask_substitute_sn(message, model, repair_sn):
    substitute_sn = message.text

    # Получаем текст письма
    template_key = "atol_serial_script"
    email_text_template = email_templates.get_template(template_key)

    # Заменяем заполнители в тексте письма на введенные пользователем данные
    email_text = email_text_template.replace("model", model)
    email_text = email_text.replace("repair_sn", repair_sn)
    email_text = email_text.replace("substitute_sn", substitute_sn)
    print(email_text)
    # Определяем следующий доступный номер ticket
    last_item = Item.objects.last()
    if last_item:
        next_ticket = last_item.ticket + 1
    else:
        next_ticket = 1

    # Получаем пользователя Telegram
    telegram_user_id = message.from_user.id

    # Ищем соответствующего пользователя в базе данных
    custom_user, created = CustomUser.objects.get_or_create(
        telegram_id=telegram_user_id)

    # Создаем экземпляр модели Item и заполняем его данными из пользовательского ввода
    item = Item(
        ticket=next_ticket,
        id_user=custom_user,
        description=email_text,  # Используем текст письма с замененными данными
        email="vendor@example.com",
        send_message=False,
    )

    # Сохраняем экземпляр модели в базе данных
    item.save()

    # Запрашиваем фото тестового прогона
    bot.send_message(message.chat.id, "Пришлите фото тестового прогона:")
    bot.register_next_step_handler(message, ask_test_run_photo)

def ask_test_run_photo(message):
    # Проверяем, что сообщение содержит фото
    if message.photo:
        bot.send_message(message.chat.id, "Спасибо! Фото получено.")

        # Обновляем экземпляр модели Item, добавляя фото тестового прогона
        item = Item.objects.last()
        if item:
            item.image = message.photo[-1].file_id
            item.save()
        else:
            bot.send_message(message.chat.id, "Ошибка сохранения данных.")
    else:
        bot.send_message(message.chat.id,
                         "Пожалуйста, пришлите фото тестового прогона.")

def process_29_network_handler(message):

    # Получаем SAP магазина от пользователя
    sap = message.text
    chat_id = message.chat.id

    # Вызываем функцию process_29_network с полученным SAP
    response = process_29_network(sap, bot, chat_id)

    # Отправляем результат обработки пользователю
    bot.send_message(message.chat.id, response)

# Обработчик кнопки "Инфо"
@bot.message_handler(
    func=lambda message: message.text == 'Инфо. Актуальные образы')
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
            bot.send_message(message.from_user.id,
                             "В таблице images нет данных для отображения.")

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.from_user.id,
                         "Произошла ошибка при выполнении операции. Пожалуйста, попробуйте еще раз.")


# Обработчик кнопок с папками и файлами
@bot.message_handler(func=lambda message: True)
def handle_folder_or_file(message):
    global current_path

    try:
        # Получаем пользователя по id
        user = CustomUser.objects.get(telegram_id=message.from_user.id)
        # Проверяем, заблокирован ли пользователь
        if user.access == 1:
            # Пользователь заблокирован, отправляем сообщение с отказом в доступе
            bot.send_message(message.from_user.id, "Вам запрещен доступ к боту.")
            return

        chosen_item = message.text
        chosen_item_path = os.path.join(current_path, chosen_item)

        if chosen_item == 'Назад':
            # Если выбрана кнопка "Назад", обновляем текущий путь на родительскую папку
            current_path, _ = os.path.split(current_path)
            send_keyboard(message)  # Отправляем клавиатуру с содержимым папки
        elif os.path.isdir(chosen_item_path):
            # Проверяем, если выбрана папка, но она выше базовой папки
            if not chosen_item_path.startswith(base_folder):
                bot.send_message(message.from_user.id, "Вы достигли верхней директории.")
                return

            # Если выбрана папка, обновляем текущий путь и отправляем клавиатуру с содержимым папки
            current_path = chosen_item_path
            send_keyboard(message)
        else:
            # Если выбран файл, отправляем его пользователю
            bot.send_document(message.from_user.id, open(chosen_item_path, 'rb'))

    except Exception as e:
        # Записываем ошибку в лог и уведомляем пользователя о неполадке
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.from_user.id, "Произошла ошибка при выполнении операции. Пожалуйста, попробуйте еще раз.")


# Обработчик кнопки "Инфо"
@bot.message_handler(
    func=lambda message: message.text == 'Инфо. Актуальные образы')
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
            bot.send_message(message.from_user.id,
                             "В таблице images нет данных для отображения.")

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        bot.send_message(message.from_user.id,
                         "Произошла ошибка при выполнении операции. Пожалуйста, попробуйте еще раз.")


# Запускаем бота
if __name__ == '__main__':
    bot.polling(none_stop=True)