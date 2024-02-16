from django.db import models


class User(models.Model):
    id_telegram = models.CharField(
        max_length=50,
        verbose_name='ID телеграмм',
        unique=True,
        db_index=True)
    username = models.CharField(
        max_length=100,
        verbose_name='Username',
        )
    first_name = models.CharField(
        max_length=60,
        verbose_name='First Name',
        )
    last_name = models.CharField(
        max_length=60,
        verbose_name='Last Name',
        )
    assess = models.IntegerField(
        verbose_name='Доступ к боту',
    )
