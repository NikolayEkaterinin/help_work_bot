from django.db import models


# Модель пользователя
class CustomUser(models.Model):
    telegram_id = models.IntegerField(
        verbose_name='Telegram ID',
    )
    username = models.TextField(
        verbose_name='Username',
        max_length=150,
        null=True,  # Разрешаем нулевые значения
    )
    first_name = models.TextField(
        verbose_name='First Name',
        max_length=150,
        null=True,  # Разрешаем нулевые значения
    )
    last_name = models.TextField(
        verbose_name='Last Name',
        max_length=150,
        null=True,  # Разрешаем нулевые значения
    )
    access = models.BooleanField(
        default=False,
        verbose_name='Доступ к боту',
    )


# Модель IP адресной системы
class IPAddresses(models.Model):
    sap = models.TextField(
        max_length=10,
        verbose_name='SAP объекта',
    )
    name = models.TextField(
        max_length=20,
        verbose_name='Наименование объекта',
    )
    ip_mag = models.TextField(
        verbose_name='IP адрес',
    )
    subnet_mag = models.TextField(
        verbose_name='Подсеть',
    )


# Модель образа
class Image(models.Model):
    ts = models.TextField(
        verbose_name='Торговая сеть',
        max_length=150,
    )
    bo = models.TextField(
        verbose_name='Образ сервера',
        max_length=150,
    )
    pos = models.TextField(
        verbose_name='Образ кассы',
        max_length=150,
    )
    sco = models.TextField(
        verbose_name='Образ КСО',
        max_length=150,
    )
    pc = models.TextField(
        verbose_name='Образ PC',
        max_length=150,
    )
