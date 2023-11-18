from hashlib import shake_256
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from transliterate import translit
from .models import Patient

from .models import MEPHIUser


class DateInput(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(label="Пароль",max_length=60, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтвердите пароль",max_length=60, widget=forms.PasswordInput)

    def save(self, commit=True):
        data = self.cleaned_data
        letters_login = translit(data['first_name'], reversed=True)[0] + \
                        translit(data['last_name'], reversed=True)[0] + \
                        translit(data['patronymic'], reversed=True)[0] + "_"
        matched_by_login = MEPHIUser.objects.filter(username__contains=f"{letters_login}").order_by("-date_registrate")
        data['username'] = letters_login + str(
            int(matched_by_login[0].username[4:]) + 1) if matched_by_login else letters_login + "1"
        user = MEPHIUser(username=data['username'],
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
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control', "placeholder": "Login",'type': "text"}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', "placeholder": "Password",  'type':"password"}))

    class Meta:
        model = MEPHIUser
        fields = ('username', 'password')

class CreatePatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ('number_ill_history', 'first_name', 'last_name', 'patronymic', 'birthday', 'sex')
        widgets = {
            'birthday': DateInput(),
        }

    def save(self, commit=True):
        data = self.cleaned_data
        hashed_str = str(data['number_ill_history']) + data['first_name'] + data['last_name'] + data['patronymic'] + str(data[
                'birthday']) + str(data['sex'])
        data['t_md5'] = shake_256(hashed_str.encode()).hexdigest(16)
        data['t_changed'] = '0'
        patient = Patient(number_ill_history=data['number_ill_history'],
                          first_name=data['first_name'],
                          last_name=data['last_name'],
                          patronymic=data['patronymic'],
                          birthday=data['birthday'],
                          sex=data['sex'],
                          t_md5=data['t_md5'],
                          t_changed=data['t_changed'])
        if commit:
            patient.save()
        return patient
