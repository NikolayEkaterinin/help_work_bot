import os
import django
import sqlite3
from django.db import transaction
from helpmanbot import settings

# Установка настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpmanbot.settings')
django.setup()

# Импорт моделей должен происходить после инициализации Django
from telegram_bot.models import CustomUser, IPAddresses, Image

# Перенос данных из базы данных user.db
old_conn_users = sqlite3.connect('user.db')
old_cursor_users = old_conn_users.cursor()
old_cursor_users.execute('SELECT id, username, first_name, last_name, blok FROM users')
old_data_users = old_cursor_users.fetchall()
old_conn_users.close()

# Перенос данных в новую базу данных для модели CustomUser
with transaction.atomic():
    for row in old_data_users:
        telegram_id, username, first_name, last_name, blok = row
        CustomUser.objects.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            access=(blok == 1)
        )

# Перенос данных из базы данных ip_addresses.db
old_conn_ip = sqlite3.connect('ip_addresses.db')
old_cursor_ip = old_conn_ip.cursor()
old_cursor_ip.execute('SELECT sap, name, ip_mag, subnet_ip FROM ip_addresses')

old_data_ip = old_cursor_ip.fetchall()
old_conn_ip.close()

# Перенос данных в новую базу данных для модели IPAddresses
with transaction.atomic():
    for row in old_data_ip:
        sap, name, ip_mag, subnet_mag = row
        IPAddresses.objects.create(
            sap=sap,
            name=name,
            ip_mag=ip_mag,
            subnet_mag=subnet_mag,
        )

