import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from aiogram.types import Message

load_dotenv()

SENDER_EMAIL = os.getenv('sender_email')
SENDER_PASSWORD = os.getenv('sender_password')


async def send_email(sender_email, sender_password, recipient_email, subject, body):
    # Создаем объект MIMEMultipart
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Добавляем тело письма
    message.attach(MIMEText(body, "plain"))

    try:
        # Устанавливаем соединение с SMTP-сервером и отправляем письмо
        with smtplib.SMTP("smtp.mail.ru", 25) as server:
            server.starttls()  # Начинаем шифрованное TLS-соединение
            server.login(sender_email, sender_password)  # Входим в учетную запись отправителя
            server.send_message(message)  # Отправляем письмо
        print("Письмо успешно отправлено!")
    except Exception as e:
        print("Ошибка при отправке письма: " + str(e))

# Пример использования
sender_email = SENDER_EMAIL
sender_password = SENDER_PASSWORD
recipient_email = "n.ekaterinin@soyuz76.ru"
subject = "Тестовое письмо"
body = "Тестовое письмо"

send_email(sender_email, sender_password, recipient_email, subject, body)