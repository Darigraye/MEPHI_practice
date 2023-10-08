from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from transliterate import translit

from .models import MEPHIUser


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(max_length=60, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=60, widget=forms.PasswordInput)

    def save(self, commit=True):
        data = self.cleaned_data
        letters_login = translit(data['first_name'], reversed=True)[0] + \
                        translit(data['last_name'], reversed=True)[0] + \
                        translit(data['patronymic'], reversed=True)[0] + "_"
        matched_by_login = MEPHIUser.objects.filter(login__contains=f"{letters_login}").order_by("-date_registrate")
        data['login'] = letters_login + str(
            int(matched_by_login[0].login[4:]) + 1) if matched_by_login else letters_login + "1"
        user = MEPHIUser(login=data['login'],
                         email=data['email'],
                         phone_number=data['phone_number'],
                         first_name=data['first_name'],
                         last_name=data['last_name'],
                         patronymic=data['patronymic'])
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user

    class Meta:
        model = MEPHIUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number', 'patronymic')


class SignInForm(AuthenticationForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = MEPHIUser
        fields = ('login', 'password')
