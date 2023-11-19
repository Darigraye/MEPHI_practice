# Generated by Django 4.2.5 on 2023-11-18 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotate_application', '0011_alter_cellcharacteristic_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='sex',
            field=models.BooleanField(choices=[('1', 'Мужчина'), ('0', 'Женщина')], db_comment='Пол 1 - мужской, 0 - женский', verbose_name='пол'),
        ),
    ]
