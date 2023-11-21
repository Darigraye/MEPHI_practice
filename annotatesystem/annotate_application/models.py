import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import RegexValidator

from django.db.models.signals import pre_save
from django.dispatch import receiver


def image_directory_path(instance, filename):
    return f"image/{datetime.date.today().year}/{datetime.date.today().month}/{datetime.date.today().day}/{instance.t_md5}-{filename}"


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

    def __str__(self):
        return self.category_name

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
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # менеджер для запросов к бд
    objects = UserManager()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value

    def __str__(self):
        return self.username

    class Meta:
        db_table = "al_user"
        db_table_comment = "таблица зарегистрированных пользователей"
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        get_latest_by = "date_registrate"

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})


class Patient(models.Model):
    SEX_TYPE = [
        (1, 'Мужчина'),
        (0, 'Женщина')
    ]

    # бизнес-атрибуты
    number_ill_history = models.IntegerField(_("номер истории болезни"), db_comment="Номер истории болезни")
    first_name = models.CharField(_("имя"), max_length=50, db_comment="Имя пользователя")
    last_name = models.CharField(_("фамилия"), max_length=50, db_comment="Фамилия пользователя")
    patronymic = models.CharField(_("отчество"), max_length=50, null=True, db_comment="Отчество пользователя")
    birthday = models.DateTimeField(_("дата рождения"), db_comment="Дата рождения")
    sex = models.IntegerField(_("пол"), choices=SEX_TYPE, db_comment="Пол 1 - мужской, 0 - женский")

    def __str__(self):
        return f"{self.first_name} {self.last_name}, номер истории болезни: {self.number_ill_history}"

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

    def __str__(self):
        return self.marker_name

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

    def __str__(self):
        return self.description

    class Meta:
        db_table = "al_marking"
        db_table_comment = "таблица маркировок"
        verbose_name = _("маркировка")
        verbose_name_plural = _("маркировки")


class Terms(models.Model, SCD2ModelMixin):
    term_name = models.CharField(_("Наименование термина"), max_length=50, db_comment="Наименование термина")
    definition = models.TextField(_("Определение"), db_comment="Определение")
    description = models.TextField(_("Описание"), blank=True, db_comment="Описание")

    def __str__(self):
        return self.term_name

    class Meta:
        db_table = "al_term"
        db_table_comment = "таблица терминов и определений"
        verbose_name = _("термин")
        verbose_name_plural = _("термины")


class DictCellsCharacteristics(models.Model):
    characteristic_name = models.CharField(_("Наименование характеристики"), db_comment="Наименование характеристики")

    def __str__(self):
        return self.characteristic_name

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

    def __str__(self):
        return self.sprout_type

    class Meta:
        db_table = "al_researched_object"
        db_table_comment = "справочник объектов исследования"
        verbose_name = _("объект исследования")
        verbose_name_plural = _("объекты исследования")


class ResearchResult(models.Model):
    conclusion = models.TextField(_("Заключение"), db_comment="Заключение")
    research = models.ForeignKey("PatientResearch", related_name="researchresult", null=True, on_delete=models.PROTECT)
    patient = models.ForeignKey("Patient", related_name="researchresult", null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.conclusion

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

    def __str__(self):
        return f"{self.date_begin}-{self.date_end}"

    class Meta:
        db_table = "al_patient_research"
        db_table_comment = "справочник исследования пациента"
        verbose_name = _("исследование")
        verbose_name_plural = _("исследования")


class Medication(models.Model):
    medication_type = models.CharField(_("Тип препарата"), db_comment="Тип препарата")
    patient_research = models.ForeignKey(PatientResearch, related_name="medication", on_delete=models.PROTECT)
    patient = models.ForeignKey(Patient, related_name="medication", null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.medication_type

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

    def __str__(self):
        return self.percent_positive_cells

    class Meta:
        db_table = "al_immunophenotyping"
        db_table_comment = "справочник иммунофенотипирования"
        verbose_name = _("данные иммунофенотипирования")
        verbose_name_plural = _("данные иммунофенотипирования")


class CellImage(models.Model):
    image = models.ImageField(upload_to=image_directory_path, blank=True, verbose_name='Фото')
    medication = models.ForeignKey(Medication, related_name="cellimage", on_delete=models.PROTECT)
    patient = models.ForeignKey(Patient, related_name='cellimage', null=True, on_delete=models.PROTECT)
    scale = models.IntegerField(_("Масштаб"), db_comment="Масштаб")

    begin_date = models.DateTimeField(_("Дата начала актуальности записи"), auto_now_add=True, null=True,
                                      db_comment="Дата начала актуальности записи")
    end_date = models.DateTimeField(_("Дата окончания актуальности записи"), null=True,
                                    db_comment="Дата окончания актуальности записи")
    t_changed = models.IntegerField(_("Состояние записи"), null=True,
                                    db_comment="Состояние записи 0 - добавлена, 1 - изменена 2 - удалена")
    t_md5 = models.CharField(_("Хэш"), null=True, max_length=32, db_comment="Хэш")

    def __str__(self):
        return self.image

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
    artifacts = models.IntegerField(_("Артефакты"), db_comment="Артефакты")

    def __str__(self):
        return self.conditions

    class Meta:
        db_table = "al_settings"
        db_table_comment = "настройки системы"
        verbose_name = _("параметр системы")
        verbose_name_plural = _("параметр системы")


class CellMarking(models.Model):
    image = models.ForeignKey(CellImage, related_name="cellmarking", on_delete=models.PROTECT)
    marking = models.ForeignKey(Marking, related_name="cellmarking", on_delete=models.PROTECT)
    comment = models.TextField(_("Комментарий"), blank=True, db_comment="Комментарий")

    def __str__(self):
        return self.comment

    class Meta:
        db_table = "al_cell_marking"
        db_table_comment = "маркировка изображения"
        unique_together = ('image', 'marking')
        verbose_name = _("маркировка клетки")
        verbose_name_plural = _("маркировки клеток")


class Cell(models.Model):
    marking = models.ForeignKey(CellMarking, related_name="cell", on_delete=models.PROTECT)
    image = models.ImageField(upload_to=image_directory_path, blank=True, verbose_name='Фото')
    scale = models.IntegerField(_("Масштаб"), db_comment="Масштаб")
    cell_type = models.ForeignKey("CellType",  related_name="cell", on_delete=models.PROTECT)

    def __str__(self):
        return self.image

    class Meta:
        db_table = "al_cell"
        db_table_comment = "справочник клеток"
        verbose_name = _("клетка")
        verbose_name_plural = _("клетки")


class CellCharacteristic(models.Model):
    dictcharcteristics = models.ForeignKey(DictCellsCharacteristics, related_name="cellcharacteristic", on_delete=models.PROTECT)
    cell = models.ForeignKey(Cell, related_name="cellcharacteristic", on_delete=models.PROTECT)
    value = models.CharField(_("Значение"), db_comment="Значение")

    def __str__(self):
        return self.value

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

    def __str__(self):
        return self.description

    class Meta:
        db_table = "al_morfological"
        db_table_comment = "справочник морфологического исследования"
        verbose_name = _("морфологическое исследование")
        verbose_name_plural = _("морфологические исследования")


class CellType(models.Model):
    type_name = models.CharField(_("Название типа"), max_length=50, db_comment="Название типа")

    def __str__(self):
        return self.type_name

    class Meta:
        db_table = "al_cell_type"
        db_table_comment = "справочник типов клеток"
        verbose_name = _("тип клетки")
        verbose_name_plural = _("типы клетки")


class SystemLog(models.Model):
    LOG_TYPE = [
        ('I', "INFO"),
        ('D', "DEBUG"),
        ('E', "ERROR")
    ]
    STATUS_TYPE = [
        ('S', 'START'),
        ('F', 'FINISH')
    ]

    object_sender = models.CharField(_("Логируемый объект"), max_length=50, db_comment="Логируемый объект")
    log_type = models.CharField(_("Тип лога"), max_length=1, choices=LOG_TYPE, db_comment="Тип лога")
    action_text = models.CharField(_("Краткое описание действия"), max_length=100, db_comment="Краткое описание действия")
    description = models.TextField(_("Полное описание действия"), blank=True, db_comment="Полное описание действия")
    t_cdatetime = models.DateTimeField(_("Время создания записи"), auto_now_add=True, db_comment="Время создания записи")
    al_username = models.CharField(_("Имя пользователя, инициирующего действие"), db_comment="Имя пользователя, инициирующего действие")
    status_type = models.CharField(_("Статус выполнения"), max_length=1, choices=STATUS_TYPE, db_comment="Статус выполнения")

    def __str__(self):
        return f"{self.object_sender}-({self.log_type}): {self.action_text} {self.t_cdatetime}"

    class Meta:
        db_table = "al_log"
        db_table_comment = "Журнал логирования"
        verbose_name = _("Журнал логирования")
        verbose_name_plural = _("Журнал логирования")


class SystemParameters(models.Model):
    parameter_name = models.CharField(_("Имя параметра"), max_length=50, db_comment="Имя параметра")
    parameter_value = models.TextField(_("Значение, принимаемое параметром"), blank=True, db_comment="Значение, принимаемое параметром")
    parameter_value_bool = models.BooleanField(_("Да/Нет"), blank=True, db_comment="Да/Нет")
    t_cdatetime = models.DateTimeField(_("Дата создания параметра"), auto_now_add=True, db_comment="Дата создания параметра")
    t_isactive = models.BooleanField(_("Параметр активен"), db_comment="Параметр активен")

    def __str__(self):
        return self.parameter_name

    class Meta:
        db_table = "al_parameter"
        db_table_comment = "Справочник системных параметров приложения"
        verbose_name = _("Справочник системных параметров приложения")
        verbose_name_plural = _("Справочник системных параметров приложения")


@receiver(pre_save, sender=CellType)
def cell_type_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="CellType",
                        log_type="I",
                        action_text="Сохранение нового типа клетки",
                        description=f"Сохранение нового типа клетки: {instance.type_name}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=MorphologicalResearch)
def morf_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="MorphologicalResearch",
                        log_type="I",
                        action_text="Сохранение морфологического исследования",
                        description=f"Сохранение морфологического исследования {instance.description}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=CellCharacteristic)
def cell_characteristic_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="CellCharacteristic",
                        log_type="I",
                        action_text="Сохранение характеристики клетки",
                        description=f"Сохранение характеристики клетки со значением {instance.value}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=Cell)
def cell_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="Cell",
                        log_type="I",
                        action_text="Сохранение клетки",
                        description=f"Сохранение  клетки типа {instance.cell_type}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=CellMarking)
def cell_marking_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="CellMarking",
                        log_type="I",
                        action_text="Сохранение маркировки клетки",
                        description=f"Сохранение маркировки клетки типа {instance.comment}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=SystemSettings)
def system_settings_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="SystemSettings",
                        log_type="I",
                        action_text="Сохранение системных настроек",
                        description=f"Сохранение системных настроек",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=CellImage)
def cell_image_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="CellImage",
                        log_type="I",
                        action_text="Сохранение изображения клетки",
                        description=f"Сохранение изображения клетки {instance.image}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=Immunophenotyping)
def immunophenotyping_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="Immunophenotyping",
                        log_type="I",
                        action_text="Сохранение иммунофенотипа",
                        description=f"Сохранение иммунофенотипа, процент положительных клеток равен {instance.percent_positive_cells}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=Medication)
def medication_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="Medication",
                        log_type="I",
                        action_text="Сохранение препарата",
                        description=f"Сохранение препарата {instance.medication_type}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=PatientResearch)
def patient_research_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="PatientResearch",
                        log_type="I",
                        action_text="Сохранение исследование пациента",
                        description=f"Сохранение исследование пациента с идентификатором {instance.pk}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=ResearchResult)
def research_result_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="ResearchResult",
                        log_type="I",
                        action_text="Сохранение заключения",
                        description=f"Сохранение заключения {instance.conclusion}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=ResearchedObject)
def research_object_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="ResearchedObject",
                        log_type="I",
                        action_text="Сохранение исследуемого объекта",
                        description=f"Сохранение исследуемого объекта c типом ростка {instance.sprout_type}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=DictCellsCharacteristics)
def dict_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="DictCellsCharacteristics",
                        log_type="I",
                        action_text="Сохранение характеристики клетки",
                        description=f"Сохранение характеристики клетки {instance.characteristic_name}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=Terms)
def terms_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="Terms",
                        log_type="I",
                        action_text="Сохранение определения",
                        description=f"Сохранение определения {instance.term_name}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=Marking)
def marking_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="Marking",
                        log_type="I",
                        action_text="Сохранение маркировки",
                        description=f"Сохранение маркировки с координатами: ({instance.x1}, {instance.y1}) ({instance.x2}, {instance.y2})",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=Marker)
def marker_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="Marker",
                        log_type="I",
                        action_text="Сохранение маркера",
                        description=f"Сохранение маркера {instance.marker_name}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=Patient)
def patient_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="Patient",
                        log_type="I",
                        action_text="Сохранение пациента",
                        description=f"Сохранение пациента {instance.first_name} {instance.last_name} {instance.patronymic} номер истории болезни: {instance.number_ill_history}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=MEPHIUser)
def user_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="MEPHIUser",
                        log_type="I",
                        action_text="Сохранение/обновление информации о пользователе в базе данных",
                        description=f"Сохранение/обновление информации о пользователе в базе данных в базе данных {instance.first_name} {instance.last_name} {instance.patronymic} email: {instance.email}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()


@receiver(pre_save, sender=MEPHIUserCategory)
def user_category_save(sender, instance, *args, **kwargs):
    is_active = SystemParameters.objects.get(parameter_name="LOGGING").t_isactive
    param = SystemParameters.objects.get(parameter_name="LOGGING").parameter_value_bool
    if is_active:
        log = SystemLog(object_sender="MEPHIUserCategory",
                        log_type="I",
                        action_text="Сохранение новой категории пользователя в базе данных",
                        description=f"Сохранение пользователя в базе данных {instance.first_name} {instance.last_name} {instance.patronymic} email: {instance.email}",
                        al_username="commita_bu",
                        status_type="S"
                        )
        log.save()
