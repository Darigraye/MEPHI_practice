from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from transliterate import translit


class MEPHIUser(AbstractBaseUser, PermissionsMixin):
    # бизнес-ключи
    login = models.CharField(_("логин"), unique=True, db_comment="Логин пользователя в системе, формируется по первым буквам ФИО")
    email = models.EmailField(_("емейл адрес"), unique=True, null=False, db_comment="Емейл адрес пользователя")
    phone_number = models.CharField(_("номер телефона"), unique=True, null=False, db_comment="Номер телефона", validators=[RegexValidator(r"^\+?\d{1}[-\s]?\(?\d{3}\)?[-\s]?\d{3}([-\s]?\d{2}){2}$")])
    # бизнес-атрибуты
    first_name = models.CharField(_("имя"), max_length=50, db_comment="Имя пользователя")
    last_name = models.CharField(_("фамилия"), max_length=50, db_comment="Фамилия пользователя")
    patronymic = models.CharField(_("отчество"), max_length=50, null=True, db_comment="Отчество пользователя")
    user_category = models.ForeignKey("MEPHIUserCategory", related_name='mephi_user', on_delete=models.PROTECT)
    # тех. поля
    date_registrate = models.DateTimeField(_("дата регистрации"), auto_now_add=True, db_comment="Дата регистрации пользователя")

    class Meta:
        db_table = "al_user"
        db_table_comment = "таблица зарегистрированных пользователей"
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        get_latest_by = "date_registrate"

    def save(self, *args, **kwargs):
        letters_login = translit(self.first_name, reversed=True)[0] + \
                        translit(self.last_name, reversed=True)[0] + \
                        translit(self.patronymic, reversed=True)[0] + "_"
        matched_by_login = self.objects.filter(login__contains=f"{letters_login}").order_by("-date_registrate")
        self.login = letters_login + str(int(matched_by_login[0].login[3:]) + 1) if matched_by_login else letters_login + "1"
        super().save(*args, **kwargs)

class MEPHIUserCategory(models.Model):
    category_name = models.CharField(_("category name"), max_length=50, unique=True) # бизнес-ключ
    description = models.TextField(blank=True)

    class Meta:
        db_table = "al_user_category"
        db_table_comment = "таблица категорий пользователей"
        verbose_name = _("категория")
        verbose_name_plural = _("категории")
