import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import io
load_dotenv()

SENDER_EMAIL = os.getenv('sender_email')
SENDER_PASSWORD = os.getenv('sender_password')

sender_email = SENDER_EMAIL
sender_password = SENDER_PASSWORD


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
        with smtplib.SMTP_SSL("SMTP.yandex.ru", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        print("Письмо успешно отправлено!")
    except Exception as e:
        print("Ошибка при отправке письма: " + str(e))
