from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import RegexValidator


class SCD2ModelMixin:
    begin_date = models.DateTimeField(_("Дата начала актуальности записи"), auto_now_add=True,
                                      db_comment="Дата начала актуальности записи")
    end_date = models.DateTimeField(_("Дата окончания актуальности записи"), null=True,
                                    db_comment="Дата окончания актуальности записи")
    t_changed = models.IntegerField(_("Состояние записи"),
                                    db_comment="Состояние записи 0 - добавлена, 1 - изменена 2 - удалена")
    t_md5 = models.CharField(_("Хэш"), max_length=32, db_comment="Хэш")


class MEPHIUserCategory(models.Model):
    category_name = models.CharField(_("category name"), max_length=50, unique=True)  # бизнес-ключ
    description = models.TextField(blank=True)

    @classmethod
    def get_default_pk(cls):
        return cls.objects.get_or_create(category_name="Пользователь",
                                         defaults=dict(description="Стандартный пользователь. Имеет права на чтение общедоступных справочников"))[0].pk

    class Meta:
        db_table = "al_user_category"
        db_table_comment = "таблица категорий пользователей"
        verbose_name = _("категория")
        verbose_name_plural = _("категории")


class MEPHIUser(AbstractBaseUser, PermissionsMixin):
    # поля настройки фреймворка
    USERNAME_FIELD = 'username'
    # бизнес-атрибуты
    username = models.CharField(_("логин"), unique=True,
                             db_comment="Логин пользователя в системе, формируется по первым буквам ФИО")
    email = models.EmailField(_("емейл адрес"), unique=True, null=False, db_comment="Емейл адрес пользователя")
    phone_number = models.CharField(_("номер телефона"), unique=True, null=False, db_comment="Номер телефона",
                                    validators=[
                                        RegexValidator(r"^\+?\d{1}[-\s]?\(?\d{3}\)?[-\s]?\d{3}([-\s]?\d{2}){2}$")])
    first_name = models.CharField(_("имя"), max_length=50, db_comment="Имя пользователя")
    last_name = models.CharField(_("фамилия"), max_length=50, db_comment="Фамилия пользователя")
    patronymic = models.CharField(_("отчество"), max_length=50, null=True, db_comment="Отчество пользователя")
    user_category = models.ForeignKey("MEPHIUserCategory", related_name='mephi_user', on_delete=models.PROTECT,
                                      default=MEPHIUserCategory.get_default_pk)
    # тех. поля
    date_registrate = models.DateTimeField(_("дата регистрации"), auto_now_add=True,
                                           db_comment="Дата регистрации пользователя")

    # менеджер для запросов к бд
    objects = UserManager()

    class Meta:
        db_table = "al_user"
        db_table_comment = "таблица зарегистрированных пользователей"
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        get_latest_by = "date_registrate"

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})


class Patient(models.Model):
    # бизнес-атрибуты
    number_ill_history = models.IntegerField(_("номер истории болезни"), db_comment="Номер истории болезни")
    first_name = models.CharField(_("имя"), max_length=50, db_comment="Имя пользователя")
    last_name = models.CharField(_("фамилия"), max_length=50, db_comment="Фамилия пользователя")
    patronymic = models.CharField(_("отчество"), max_length=50, null=True, db_comment="Отчество пользователя")
    birthday = models.DateTimeField(_("дата рождения"), db_comment="Дата рождения")
    sex = models.BooleanField(_("пол"), db_comment="Пол 1 - мужской, 0 - женский")

    class Meta:
        db_table = "al_patient"
        db_table_comment = "таблица пациентов"
        verbose_name = _("пациент")
        verbose_name_plural = _("пациенты")


class Marker(models.Model):
    MARKER_TYPES = [
        ('1', 'Тип 1'),
        ('2', 'Тип 2'),
        ('3', 'Тип 3')
    ]

    marker_name = models.CharField(_("название маркера"), max_length=50, db_comment="Название маркера")
    marker_type = models.CharField(_("Тип маркера"), max_length=2, choices=MARKER_TYPES, db_comment="Тип маркера")

    class Meta:
        db_table = "al_marker"
        db_table_comment = "справочник маркеров"
        verbose_name = _("маркер")
        verbose_name_plural = _("маркеры")


class Marking(models.Model):
    MARKING_TYPES = [
        ('1', 'Тип 1'),
        ('2', 'Тип 2'),
        ('3', 'Тип 3')
    ]

    colour = models.CharField(_("Цвет"), max_length=6, db_comment="Цвет")
    x1 = models.IntegerField(_("X1"), db_comment="X1")
    x2 = models.IntegerField(_("X2"), db_comment="X2")
    y1 = models.IntegerField(_("Y1"), db_comment="Y1")
    y2 = models.IntegerField(_("Y2"), db_comment="Y2")
    description = models.TextField(_("Описание"), blank=True, db_comment="Описание")

    class Meta:
        db_table = "al_marking"
        db_table_comment = "таблица маркировок"
        verbose_name = _("маркировка")
        verbose_name_plural = _("маркировки")


class Terms(models.Model, SCD2ModelMixin):
    term_name = models.CharField(_("Наименование термина"), max_length=50, db_comment="Наименование термина")
    definition = models.TextField(_("Определение"), db_comment="Определение")
    description = models.TextField(_("Описание"), blank=True, db_comment="Описание")

    class Meta:
        db_table = "al_term"
        db_table_comment = "таблица терминов и определений"
        verbose_name = _("термин")
        verbose_name_plural = _("термины")


class DictCellsCharacteristics(models.Model):
    characteristic_name = models.CharField(_("Наименование характеристики"), db_comment="Наименование характеристики")

    class Meta:
        db_table = "al_dict_cell_characteristic"
        db_table_comment = "словарь характеристик клеток"
        verbose_name = _("характеристика")
        verbose_name_plural = _("характеристики")


class ResearchedObject(models.Model):
    SPROUT_TYPES = [
        ('1', 'Тип 1'),
        ('2', 'Тип 2'),
        ('3', 'Тип 3')
    ]
    count_object = models.IntegerField(_("Количество объектов"), db_comment="Количество объектов")
    sprout_type = models.CharField(_("Тип ростка"), choices=SPROUT_TYPES, db_comment="Тип ростка")
    norm = models.CharField(_("Норма"), db_comment="Норма")

    class Meta:
        db_table = "al_researched_object"
        db_table_comment = "справочник объектов исследования"
        verbose_name = _("объект исследования")
        verbose_name_plural = _("объекты исследования")


class ResearchResult(models.Model):
    conclusion = models.TextField(_("Заключение"), db_comment="Заключение")

    class Meta:
        db_table = "al_research_result"
        db_table_comment = "справочник результатов исследования"
        verbose_name = _("результат исследования")
        verbose_name_plural = _("результаты исследования")


