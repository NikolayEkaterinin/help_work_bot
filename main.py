import os
import asyncio
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, types, Dispatcher
from token_data import TELEGRAM_TOKEN
from subnet_29 import process_sap_request
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Устанавливаем соединение с базой данных SQLite
conn = sqlite3.connect('user.db')
cursor = conn.cursor()


# Создаем таблицу пользователей, если она не существует
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    blok INTEGER DEFAULT 0,
                    ip_address TEXT
                )''')
conn.commit()
storage = MemoryStorage()

# Здесь нужно указать токен вашего бота
bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Путь к папке, которую бот будет просматривать
base_folder = 'Instr'

# Переменная для хранения выбранного пути
current_path = base_folder

# Настройка логирования
log_file = 'bot.log'
max_log_size = 5 * 1024 * 1024  # 5 МБ
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
file_handler = RotatingFileHandler(filename=log_file, mode='a', maxBytes=max_log_size, backupCount=1)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
logging.getLogger().addHandler(file_handler)


@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    # Сохраняем информацию о пользователе в базе данных
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    cursor.execute("INSERT OR IGNORE INTO users (id, username, first_name, last_name, blok) VALUES (?, ?, ?, ?, 1)",
                   (user_id, username, first_name, last_name))
    conn.commit()

    # Получаем имя пользователя для приветствия
    if first_name is not None:
        name = first_name
    elif username is not None:
        name = username
    else:
        name = "User"

    # Проверяем, заблокирован ли пользователь
    cursor.execute("SELECT blok FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    if result is not None and result[0] == 1:
        # Пользователь заблокирован, отправляем сообщение с отказом в доступе
        await message.answer(f'''Вам запрещен доступ к боту. Необходимо обратиться к вашему старшему инженеру для
        получения доступа. Обязательно необходимо предоставить Ваш ID.''')
        await message.answer(f'Ваш ID {user_id}')
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
    keyboard = types.ReplyKeyboardMarkup(row_width=1)

    # Добавляем кнопку "Инфо" в самом верху, только если текущий путь - базовый каталог
    if current_path == base_folder:
        keyboard.add(types.KeyboardButton('Инфо. Актуальные образы'))
        keyboard.add(types.KeyboardButton('29 сеть'))

    # Добавляем кнопку "Назад", если текущий путь не является базовым каталогом
    if current_path != base_folder:
        keyboard.add(types.KeyboardButton('Назад'))

    for folder in folders:
        keyboard.add(types.KeyboardButton(folder))

    for file in files:
        keyboard.add(types.KeyboardButton(file))

    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(f"Выберите папку или файл:", reply_markup=keyboard)


# Создайте состояние для ожидания SAP
class WaitForSAPState(StatesGroup):
    waiting_for_sap = State()

class Sap_states(StatesGroup):
    sap = State()
@dp.message_handler(lambda message: message.text == '29 сеть')
async def handle_sap_input(message: types.Message, state: FSMContext):
    await message.answer("Введите SAP, для расчета сети")
    await Sap_states.sap.set()
    await state.update_data(prev_message_text=message.text)

@dp.message_handler(state=Sap_states.sap)
async def process_sap_state(message: types.Message, state: FSMContext):
    data = await state.get_data()
    prev_message_text = data.get('prev_message_text')
    sap = message.text.upper()

    await process_sap_request(message, sap)
    await state.finish()


# Обработчик кнопки "Инфо"
@dp.message_handler(lambda message: message.text == 'Инфо. Актуальные образы')
async def handle_info(message: types.Message):
    try:
        user_id = message.from_user.id

        # Получаем данные из таблицы "images"
        # Получаем все строки из таблицы "images"
        cursor.execute("SELECT * FROM images")
        rows = cursor.fetchall()

        if rows:

            for row in rows:
                info_message = f"Актуальные образы {row[0]} :\n"
                info_message += f"\n"
                info_message += f"\n"
                info_message += f"BO: {row[1]}\n"
                info_message += f"\n"
                info_message += f"POS все кроме HP и NCR XR4: {row[2]}\n"
                info_message += f"\n"
                info_message += f"POS HP и NCR XR4: {row[3]}\n"
                info_message += f"\n"
                info_message += f"КСО: {row[4]}\n"
                info_message += f"\n"
                info_message += f"PC: {row[5]}\n"
                await message.answer(info_message)
        else:
            await message.answer("В таблице images нет данных для отображения.")

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        await message.answer("Произошла ошибка при выполнении операции. Пожалуйста, попробуйте еще раз.")


# Обработчик нажатия кнопок с папками и файлами
@dp.message_handler()
async def handle_folder_or_file(message: types.Message):
    global current_path

    try:
        # Проверяем, заблокирован ли пользователь
        cursor.execute("SELECT blok FROM users WHERE id = ?", (message.from_user.id,))
        result = cursor.fetchone()
        if result is not None and result[0] == 1:
            # Пользователь заблокирован, отправляем сообщение с отказом в доступе
            await message.answer("Вам запрещен доступ к боту.")
            return

        chosen_item = message.text
        chosen_item_path = os.path.join(current_path, chosen_item)

        if chosen_item == 'Назад':
            # Если выбрана кнопка "Назад", обновляем текущий путь на родительскую папку
            parent_path = os.path.dirname(current_path)
            if parent_path.startswith(base_folder):
                current_path = parent_path
            else:
                await message.answer("Вы достигли верхней директории.")
                return
            await handle_start(message)
        elif chosen_item == 'Инфо. Актуальные образы':
            current_folder = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_folder, 'help.txt')
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                await message.answer(content)
            else:
                await message.answer("Файл 'help.txt' не найден.")
        elif os.path.isfile(chosen_item_path):
            file_size = os.path.getsize(chosen_item_path)
            # Проверяем, если размер файла больше 50 МБ (в байтах)
            if file_size > 50 * 1024 * 1024:
                await message.answer("Файлы размером более 50 МБ нельзя скачивать."
                                     "Для скачивания файлов большого объема,"
                                     "подключитесь к FTP в соответствующий раздел")
                logging.info(f"Запрос файла объемом более 50 МБ {current_path}, файл {chosen_item}"
                             f" запросил пользователь ID {message.from_user.id}")
            else:
                # Если выбран файл, и его размер допустим, отправляем его пользователю
                with open(chosen_item_path, 'rb') as f:
                    await message.answer_document(f)
        elif os.path.isdir(chosen_item_path):
            # Проверяем, если выбрана папка, но она выше базовой папки
            if not chosen_item_path.startswith(base_folder):
                await message.answer("Вы достигли верхней директории.")
                return

            # Если выбрана папка, обновляем текущий путь и отправляем список файлов и папок
            current_path = chosen_item_path
            await handle_start(message)

        # Сохраняем изменения в базе данных
        conn.commit()

    except Exception as e:
        # Записываем ошибку в лог и уведомляем пользователя о неполадке
        logging.error(f"Произошла ошибка: {e}")
        await message.answer("Произошла ошибка при выполнении операции. Пожалуйста, попробуйте еще раз.")





# Запускаем бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем.")
    except Exception as e:
        logging.error(f"Бот остановлен из-за неожиданной ошибки: {e}")
    finally:
        # Закрываем соединение с базой данных при остановке бота
        conn.close()
