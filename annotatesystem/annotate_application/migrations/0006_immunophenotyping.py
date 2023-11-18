# Generated by Django 4.2.5 on 2023-11-18 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotate_application', '0005_medication'),
    ]

    operations = [
        migrations.CreateModel(
            name='Immunophenotyping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent_positive_cells', models.IntegerField(db_comment='Процент антиген-позитивных клеток', verbose_name='Процент антиген-позитивных клеток')),
                ('marker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='immunophenotyping', to='annotate_application.marker')),
                ('medication', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='immunophenotyping', to='annotate_application.medication')),
                ('research', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='immunophenotyping', to='annotate_application.patientresearch')),
            ],
            options={
                'verbose_name': 'данные иммунофенотипирования',
                'verbose_name_plural': 'данные иммунофенотипирования',
                'db_table': 'al_immunophenotyping',
                'db_table_comment': 'справочник иммунофенотипирования',
            },
        ),
    ]
