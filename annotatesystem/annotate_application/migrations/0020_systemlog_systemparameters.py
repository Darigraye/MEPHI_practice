# Generated by Django 4.2.5 on 2023-11-20 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotate_application', '0019_alter_medication_medication_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_sender', models.CharField(db_comment='Логируемый объект', max_length=50, verbose_name='Логируемый объект')),
                ('log_type', models.CharField(choices=[('I', 'INFO'), ('D', 'DEBUG'), ('E', 'ERROR')], db_comment='Тип лога', max_length=1, verbose_name='Тип лога')),
                ('action_text', models.CharField(db_comment='Краткое описание действия', max_length=100, verbose_name='Краткое описание действия')),
                ('description', models.TextField(blank=True, db_comment='Полное описание действия', verbose_name='Полное описание действия')),
                ('t_cdatetime', models.DateTimeField(auto_now_add=True, db_comment='Время создания записи', verbose_name='Время создания записи')),
                ('al_username', models.CharField(db_comment='Имя пользователя, инициирующего действие', verbose_name='Имя пользователя, инициирующего действие')),
                ('status_type', models.CharField(choices=[('S', 'START'), ('F', 'FINISH')], db_comment='Статус выполнения', max_length=1, verbose_name='Статус выполнения')),
            ],
            options={
                'verbose_name': 'Журнал логирования',
                'verbose_name_plural': 'Журнал логирования',
                'db_table': 'al_log',
                'db_table_comment': 'Журнал логирования',
            },
        ),
        migrations.CreateModel(
            name='SystemParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(db_comment='Имя параметра', max_length=50, verbose_name='Имя параметра')),
                ('parameter_value', models.TextField(blank=True, db_comment='Значение, принимаемое параметром', verbose_name='Значение, принимаемое параметром')),
                ('parameter_value_bool', models.BooleanField(blank=True, db_comment='Да/Нет', verbose_name='Да/Нет')),
                ('t_cdatetime', models.DateTimeField(auto_now_add=True, db_comment='Дата создания параметра', verbose_name='Дата создания параметра')),
                ('t_isactive', models.BooleanField(db_comment='Параметр активен', verbose_name='Параметр активен')),
            ],
            options={
                'verbose_name': 'Справочник системных параметров приложения',
                'verbose_name_plural': 'Справочник системных параметров приложения',
                'db_table': 'al_parameter',
                'db_table_comment': 'Справочник системных параметров приложения',
            },
        ),
    ]
