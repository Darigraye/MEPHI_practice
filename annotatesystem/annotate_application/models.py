from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import RegexValidator


def image_directory_path(instance, filename):
    return f"image/%Y/%m/%d/{instance.t_md5}-{filename}"


def cell_directory_path(instance, filename):
    return f"cell/%Y/%m/%d/{instance.t_md5}-{filename}"


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


class PatientResearch(models.Model):
    date_begin = models.DateTimeField(_("дата начала исследования"), db_comment="дата начала исследования")
    date_end = models.DateTimeField(_("дата окончания исследования"), db_comment="дата окончания исследования")
    patient = models.ForeignKey(Patient, related_name="research", on_delete=models.PROTECT)
    researcher = models.ForeignKey(MEPHIUser, related_name="research", on_delete=models.PROTECT)

    class Meta:
        db_table = "al_patient_research"
        db_table_comment = "справочник исследования пациента"
        verbose_name = _("исследование")
        verbose_name_plural = _("исследования")


class Medication(models.Model):
    MEDICATION_TYPES = [
        ('1', 'Тип 1'),
        ('2', 'Тип 2'),
        ('3', 'Тип 3')
    ]

    medication_type = models.CharField(_("Тип препарата"), choices=MEDICATION_TYPES, db_comment="Тип препарата")
    patient_research = models.ForeignKey(PatientResearch, related_name="medication", on_delete=models.PROTECT)

    class Meta:
        db_table = "al_medication"
        db_table_comment = "справочник препаратов"
        verbose_name = _("препарат")
        verbose_name_plural = _("препараты")


class Immunophenotyping(models.Model):
    marker = models.ForeignKey(Marker, related_name="immunophenotyping", on_delete=models.PROTECT)
    medication = models.ForeignKey(Medication, related_name="immunophenotyping", on_delete=models.PROTECT)
    research = models.ForeignKey(PatientResearch, related_name="immunophenotyping", on_delete=models.PROTECT)
    percent_positive_cells = models.IntegerField(_("Процент антиген-позитивных клеток"), db_comment="Процент антиген-позитивных клеток")

    class Meta:
        db_table = "al_immunophenotyping"
        db_table_comment = "справочник иммунофенотипирования"
        verbose_name = _("данные иммунофенотипирования")
        verbose_name_plural = _("данные иммунофенотипирования")


class CellImage(models.Model, SCD2ModelMixin):
    image = models.ImageField(upload_to=image_directory_path, blank=True, verbose_name='Фото')
    medication = models.ForeignKey(Medication, related_name="cellimage", on_delete=models.PROTECT)
    scale = models.IntegerField(_("Масштаб"), db_comment="Масштаб")

    class Meta:
        db_table = "al_cell_image"
        db_table_comment = "справочник изображений клеток"
        verbose_name = _("изображение клетки")
        verbose_name_plural = _("изображения клеток")


class SystemSettings(models.Model):
    GLASS_TYPES = [
        ('1', 'Тип 1'),
        ('2', 'Тип 2'),
        ('3', 'Тип 3')
    ]

    medication = models.ForeignKey(Medication, related_name="systemsettings", on_delete=models.PROTECT)
    conditions = models.TextField(_("Условия подготовки препарата"), db_comment="Условия подготовки препарата")
    glass_type = models.CharField(_("Тип стекла"),  choices=GLASS_TYPES, db_comment="Тип стекла")
    artifacts = models.TextField(_("Артефакты"), db_comment="Артефакты")

    class Meta:
        db_table = "al_settings"
        db_table_comment = "настройки системы"
        verbose_name = _("параметр системы")
        verbose_name_plural = _("параметр системы")


class CellMarking(models.Model):
    image = models.ForeignKey(CellImage, related_name="cellmarking", on_delete=models.PROTECT)
    marking = models.ForeignKey(Marking, related_name="cellmarking", on_delete=models.PROTECT)
    comment = models.TextField(_("Комментарий"), blank=True, db_comment="Комментарий")

    class Meta:
        db_table = "al_cell_marking"
        db_table_comment = "маркировка изображения"
        unique_together = ('image', 'marking')


class Cell(models.Model):
    CELL_TYPES = [
        ('1', 'Тип 1'),
        ('2', 'Тип 2'),
        ('3', 'Тип 3')
    ]

    marking = models.ForeignKey(CellMarking, related_name="cell", on_delete=models.PROTECT)
    image = models.ImageField(upload_to=image_directory_path, blank=True, verbose_name='Фото')
    scale = models.IntegerField(_("Масштаб"), db_comment="Масштаб")
    cell_type = models.CharField(_("Тип клетки"),  choices=CELL_TYPES, db_comment="Тип клетки")

    class Meta:
        db_table = "al_cell"
        db_table_comment = "справочник клеток"
        verbose_name = _("клетка")
        verbose_name_plural = _("клетки")


class CellCharacteristic(models.Model):
    dictcharcteristics = models.ForeignKey(DictCellsCharacteristics, related_name="cellcharacteristic", on_delete=models.PROTECT)
    cell = models.ForeignKey(Cell, related_name="cellcharacteristic", on_delete=models.PROTECT)
    value = models.CharField(_("Значение"), db_comment="Значение")

    class Meta:
        db_table = "al_cell_characteristic"
        db_table_comment = "справочник характеристик клеток"
        verbose_name = _("характеристика")
        verbose_name_plural = _("характиристики")


class MorphologicalResearch(models.Model):
    RESEARCH_TYPES = [
        ('1', 'Тип 1'),
        ('2', 'Тип 2'),
        ('3', 'Тип 3')
    ]

    research_obj = models.ForeignKey(ResearchedObject, related_name="morfresearch", on_delete=models.PROTECT)
    medication = models.ForeignKey(Medication, related_name="morfresearch", on_delete=models.PROTECT)
    number_cells = models.IntegerField(_("Количество клеток"), db_comment="Количество клеток")
    leukocyte = models.BooleanField(_("Лейкоцит"), db_comment="Лейкоцит")
    research_type = models.CharField(_("Тип исследования"),  choices=RESEARCH_TYPES, db_comment="Тип клетки")
    value = models.CharField(_("Значение"), db_comment="Значение")
    description = models.TextField(_("Описание"), blank=True, db_comment="Описание")

    class Meta:
        db_table = "al_morfological"
        db_table_comment = "справочник морфологического исследования"
        verbose_name = _("морфологическое исследование")
        verbose_name_plural = _("морфологические исследования")
