import os
import asyncio
from aiogram import Bot, types, Dispatcher
from token_data import TELEGRAM_TOKEN

# Здесь нужно указать токен вашего бота
bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Путь к папке, которую бот будет просматривать
base_folder = 'd:\ПНР'

# Переменная для хранения выбранного пути
current_path = base_folder

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    # Получаем список файлов и папок в указанной директории
    files = []
    folders = []

    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)

    # Создаем клавиатуру с папками и файлами в виде кнопок
    keyboard = types.ReplyKeyboardMarkup(row_width=1)

    # Добавляем кнопку "назад", если текущий путь не совпадает с базовой папкой
    if current_path != base_folder:
        keyboard.add(types.KeyboardButton('Назад'))

    for folder in folders:
        keyboard.add(types.KeyboardButton(folder))

    for file in files:
        keyboard.add(types.KeyboardButton(file))

    if current_path == base_folder:
        keyboard.add(types.KeyboardButton('01_Инфо'))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer('Выберите папку или файл:', reply_markup=keyboard)

# Обработчик нажатия кнопок с папками и файлами
@dp.message_handler()
async def handle_folder_or_file(message: types.Message):
    global current_path
    chosen_item = message.text
    chosen_item_path = os.path.join(current_path, chosen_item)

    if chosen_item == 'Назад':
        # Если выбрана кнопка "назад", обновляем текущий путь на родительскую папку
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


# Запускаем бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()
