# Generated by Django 4.2.10 on 2024-03-16 19:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("telegram_bot", "0002_alter_customuser_first_name_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ticket", models.IntegerField(verbose_name="тикет обращения")),
                ("description", models.TextField(verbose_name="Описание обращения")),
                (
                    "email",
                    models.EmailField(max_length=254, verbose_name="email вендера"),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="email_photo/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["jpg", "jpeg", "png", "bmp"]
                            ),
                            django.core.validators.MaxValueValidator(
                                5242880, message="Размер не может превышать 50 МБ"
                            ),
                        ],
                        verbose_name="Прикладываемое фото",
                    ),
                ),
                (
                    "send_message",
                    models.BooleanField(verbose_name="Статус доставки пользователю"),
                ),
                (
                    "id_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_item",
                        to="telegram_bot.customuser",
                        verbose_name="Автор обращения",
                    ),
                ),
            ],
        ),
    ]
