# Generated by Django 4.2.10 on 2024-02-16 09:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="assess",
            field=models.IntegerField(verbose_name="Доступ к боту"),
        ),
    ]
