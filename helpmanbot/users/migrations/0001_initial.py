# Generated by Django 4.2.10 on 2024-02-16 09:30

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
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
                (
                    "id_telegram",
                    models.CharField(
                        db_index=True,
                        max_length=50,
                        unique=True,
                        verbose_name="ID телеграмм",
                    ),
                ),
                ("username", models.CharField(max_length=100, verbose_name="Username")),
                (
                    "first_name",
                    models.CharField(max_length=60, verbose_name="First Name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=60, verbose_name="Last Name"),
                ),
                (
                    "assess",
                    models.IntegerField(max_length=1, verbose_name="Доступ к боту"),
                ),
            ],
        ),
    ]
