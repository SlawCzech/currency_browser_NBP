# Generated by Django 4.2.1 on 2023-05-25 20:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("currency", "0002_load_table_a_currency_names"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="currencyvalue",
            unique_together={("currency_name", "currency_date")},
        ),
    ]