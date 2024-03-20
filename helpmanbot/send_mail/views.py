import mimetypes
import os
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import imaplib
import email
from email.header import decode_header
from .models import Item
import requests
import base64
load_dotenv()

SENDER_EMAIL = os.getenv('sender_email')
SENDER_PASSWORD = os.getenv('sender_password')

sender_email = SENDER_EMAIL
sender_password = SENDER_PASSWORD


# Период проверки наличия ответных писем (1 минута)
CHECK_INTERVAL = 60
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


# Отправка писем
def send_email(recipient_email, subject, description, ticket, attachment=None):
    # Создаем объект MIMEMultipart
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ', '.join(str(email) for email in recipient_email)
    # Используем строку адреса электронной почты
    message["Subject"] = f"{subject} (Ticket: {ticket})"  # Добавляем информацию о теме и номере ticket

    # Добавляем тело письма
    message.attach(MIMEText(description, "plain"))

    # Если указано вложение
    if attachment:
        # Получаем содержимое файла вложения
        attachment_content = attachment.read()
        # Создаем объект MIMEImage из данных изображения
        image_mime = MIMEImage(attachment_content)
        image_mime.add_header('Content-Disposition', 'attachment', filename=attachment.name)
        message.attach(image_mime)

    try:
        # Устанавливаем соединение с SMTP-сервером и отправляем письмо
        with smtplib.SMTP_SSL("SMTP.mail.ru", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        print("Письмо успешно отправлено!")
    except Exception as e:
        print("Ошибка при отправке письма: " + str(e))


# Отправка сообщения в Telegram
def send_message_to_telegram(telegram_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": telegram_id,
        "text": message
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print("Ошибка при отправке сообщения в Telegram:", response.text)


# Отправка файла в Telegram

def send_file_to_telegram(telegram_id, file_path, caption=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    files = {'document': open(file_path, 'rb')}
    data = {'chat_id': telegram_id}
    if caption:
        data['caption'] = caption
    response = requests.post(url, files=files, data=data)
    if response.status_code != 200:
        print("Ошибка при отправке файла в Telegram:", response.text)

# Ожидание ответа письма
def check_emails():
    # Подключение к почтовому серверу
    mail = imaplib.IMAP4_SSL('imap.mail.ru', 993)
    mail.login(SENDER_EMAIL, SENDER_PASSWORD)
    mail.select('inbox')

    # Поиск всех непрочитанных писем
    status, data = mail.search(None, '(UNSEEN)')
    if status == 'OK':
        for num in data[0].split():
            status, raw_email = mail.fetch(num, '(RFC822)')
            if status == 'OK':
                # Обработка содержимого письма
                msg = email.message_from_bytes(raw_email[0][1])
                subject_bytes, _ = decode_header(msg["Subject"])[0]
                if isinstance(subject_bytes, bytes):
                    subject = subject_bytes.decode('latin1')  # или другая подходящая кодировка
                else:
                    subject = subject_bytes

                # Проверка наличия ticket в теме письма
                if 'Ticket' in subject:
                    ticket = subject.split("(Ticket: ")[1][:-1]
                    items = Item.objects.filter(ticket=ticket, send_message=False)
                    if items.exists():
                        item = items.first()

                        # Получение текста ответного письма
                        message_body = None
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                # Ищем текстовую часть письма
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    message_body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            message_body = msg.get_payload(
                                decode=True).decode() if msg.get_content_type() == "text/plain" else None

                        if message_body is not None:
                            # Проверка наличия вложений
                            attachments = msg.get_payload()
                            attachment_paths = []
                            for attachment in attachments:
                                if isinstance(attachment, str):
                                    attachment_paths.append(attachment)
                                    continue
                                if attachment.get_content_maintype() == 'multipart':
                                    continue
                                # Сохранение вложения на диск с правильным именем файла
                                filename = attachment.get_filename()
                                if filename:
                                    # Преобразование имени файла из base64
                                    decoded_filename = decode_header(filename)[0][0]
                                    if isinstance(decoded_filename, bytes):
                                        # Если имя файла представлено в байтовом формате, декодируем его
                                        file_name = decoded_filename.decode()
                                    else:
                                        file_name = decoded_filename

                                    # Получение расширения файла из MIME-типа
                                    file_extension = mimetypes.guess_extension(attachment.get_content_type())

                                    # Генерация уникального имени файла
                                    unique_filename = f"{uuid.uuid4().hex}{file_extension}"

                                    # Путь для сохранения файла
                                    file_path = f"./email_photo/save_from_item/{unique_filename}"

                                    # Сохранение вложения на диск
                                    with open(file_path, 'wb') as f:
                                        f.write(attachment.get_payload(decode=True))

                                    attachment_paths.append(file_path)

                            telegram_id = item.id_user.telegram_id

                            # Подготовка сообщения для отправки пользователю с текстом ответного письма и вложениями
                            message_text = f"Получен ответ на Ваше обращение. Текст: {message_body}"
                            print(message_text)
                            if attachment_paths:
                                for file_path in attachment_paths:
                                    # Отправка файла в Telegram
                                    send_file_to_telegram(telegram_id,
                                                          file_path,
                                                          message_text)
                            else:
                                # Если нет вложений, просто отправляем текст
                                send_message_to_telegram(telegram_id,
                                                         message_text)

                            # Пометка письма как отправленного
                            item.send_message = True
                            item.save()

    # Закрытие соединения с почтовым сервером
    mail.close()
    mail.logout()
