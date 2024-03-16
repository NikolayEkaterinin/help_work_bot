from django.db import models
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator)

from telegram_bot.models import CustomUser


class Item(models.Model):
    ticket = models.IntegerField(
        verbose_name='тикет обращения',
        blank=False,

    )
    id_user = models.ForeignKey(
        CustomUser,
        verbose_name='Автор обращения',
        on_delete=models.CASCADE,
        related_name='user_item',
        blank=False,
    )
    description = models.TextField(
        verbose_name='Описание обращения',
        blank=False,
    )
    email = models.EmailField(
        verbose_name='email вендера',
        blank=False,
    )
    image = models.ImageField(
        verbose_name='Прикладываемое фото',
        upload_to="email_photo/",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'bmp']),
                    MaxValueValidator(
                        5242880,
                        message='Размер не может превышать 50 МБ')],
        null=True,
        blank=True,
    )
    send_message = models.BooleanField(
        verbose_name='Статус доставки пользователю',
        default=False,

    )


