# Generated by Django 4.1.5 on 2023-08-14 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestiontoursinterurbains', '0002_alter_momo_transaction_message_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='momo_transaction',
            name='reference_operateur_id',
            field=models.BigIntegerField(null=True),
        ),
    ]
