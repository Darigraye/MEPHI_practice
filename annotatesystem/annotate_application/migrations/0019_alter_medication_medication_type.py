# Generated by Django 4.2.5 on 2023-11-19 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotate_application', '0018_cellimage_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medication',
            name='medication_type',
            field=models.CharField(db_comment='Тип препарата', verbose_name='Тип препарата'),
        ),
    ]
