# Generated by Django 4.1.5 on 2023-07-13 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestiontoursinterurbains', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrateur',
            name='email',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='momo_transaction',
            name='id_requete',
            field=models.CharField(max_length=75),
        ),
    ]