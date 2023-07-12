import os
import asyncio
import sqlite3
from aiogram import Bot, types, Dispatcher
from token_data import TELEGRAM_TOKEN

# Устанавливаем соединение с базой данных SQLite
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

# Создаем таблицу пользователей, если она не существует
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    blok INTEGER DEFAULT 0
                )''')
conn.commit()

# Здесь должен быть ваш остальной код...

# Здесь нужно указать токен вашего бота
bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Путь к папке, которую бот будет просматривать
base_folder = 'instr'

# Переменная для хранения выбранного пути
current_path = base_folder

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    # Сохраняем информацию о пользователе в базе данных
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    cursor.execute("INSERT OR IGNORE INTO users (id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
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
        await message.answer("Вам запрещен доступ к боту.")
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

    # Добавляем кнопку "Назад", если текущий путь не является базовым каталогом
    if current_path != base_folder:
        keyboard.add(types.KeyboardButton('Назад'))

    for folder in folders:
        keyboard.add(types.KeyboardButton(folder))

    for file in files:
        keyboard.add(types.KeyboardButton(file))

    if current_path == base_folder:
        keyboard.add(types.KeyboardButton('01_Инфо'))

    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(f"Выберите папку или файл:", reply_markup=keyboard)

# Обработчик нажатия кнопок с папками и файлами
@dp.message_handler()
async def handle_folder_or_file(message: types.Message):
    global current_path

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
        current_path = os.path.dirname(current_path)
        await handle_start(message)
    elif os.path.isfile(chosen_item_path):
        file_size = os.path.getsize(chosen_item_path)
        if file_size > 50 * 1024 * 1024:  # Проверяем, если размер файла больше 50 МБ (в байтах)
            await message.answer("Файлы размером более 50 МБ нельзя скачивать. Для скачивания файлов большого объема,"
                                 "подключитесь к FTP в соответствующий раздел")
        else:
            # Если выбран файл, и его размер допустим, отправляем его пользователю
            with open(chosen_item_path, 'rb') as f:
                await message.answer_document(f)
    elif os.path.isdir(chosen_item_path):
        # Если выбрана папка, обновляем текущий путь и отправляем список файлов и папок
        current_path = chosen_item_path
        await handle_start(message)

    # Сохраняем изменения в базе данных
    conn.commit()


# Запускаем бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    try:
        loop.run_forever()
    finally:
        # Закрываем соединение с базой данных при остановке бота
        conn.close()
