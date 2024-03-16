import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiogram.types import Message

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
sender_email = "n.ekaterinin@soyuz76.ru"
sender_password = "hQh3bsNzmNZGrJfxiG3P"
recipient_email = "n.ekaterinin@soyuz76.ru"
subject = "Тестовое письмо"
body = "Тестовое письмо"

send_email(sender_email, sender_password, recipient_email, subject, body)