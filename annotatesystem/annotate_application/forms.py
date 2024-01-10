from hashlib import shake_256
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelChoiceField
from transliterate import translit
from .models import *

from .models import MEPHIUser


class DateInput(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(label="Пароль", max_length=60, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтвердите пароль", max_length=60, widget=forms.PasswordInput)

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
    username = forms.CharField(label='Логин', widget=forms.TextInput(
        attrs={'class': 'form-control', "placeholder": "Login", 'type': "text"}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(
        attrs={'class': 'form-control', "placeholder": "Password", 'type': "password"}))

    class Meta:
        model = MEPHIUser
        fields = ('username', 'password')


class CreatePatientForm(forms.ModelForm):
    SEX_TYPE = [
        (1, 'Мужчина'),
        (0, 'Женщина')
    ]

    sex = forms.ChoiceField(choices=SEX_TYPE)

    class Meta:
        model = Patient
        fields = ('number_ill_history', 'first_name', 'last_name', 'patronymic', 'birthday', 'sex')
        widgets = {
            'birthday': DateInput(),
        }

    def save(self, commit=True):
        data = self.cleaned_data
        hashed_str = str(data['number_ill_history']) + data['first_name'] + data['last_name'] + data[
            'patronymic'] + str(data[
                                    'birthday']) + str(data['sex'])
        data['t_md5'] = shake_256(hashed_str.encode()).hexdigest(16)
        data['t_changed'] = '0'
        patient = Patient(number_ill_history=data['number_ill_history'],
                          first_name=data['first_name'],
                          last_name=data['last_name'],
                          patronymic=data['patronymic'],
                          birthday=data['birthday'],
                          sex=data['sex']
                          )
        if commit:
            patient.save()
        return patient


class CreateDiagnosisForm(forms.ModelForm):
    class Meta:
        model = ResearchResult
        fields = ('conclusion', 'patient')


class CreateCellTypeForm(forms.ModelForm):
    class Meta:
        model = CellType
        fields = ('type_name',)


class AddImageForm(forms.ModelForm):
    def save(self, commit=True):
        data = self.cleaned_data
        hashed_str = str(data['medication']) + str(data['scale']) + str(data['patient'])
        data['t_md5'] = shake_256(hashed_str.encode()).hexdigest(16)
        data['t_changed'] = '0'
        patient = CellImage(medication=data['medication'],
                            image=data['image'],
                          scale=data['scale'],
                          patient=data['patient'],
                          t_md5=data['t_md5'],
                          t_changed=data['t_changed']
                          )
        if commit:
            patient.save()
        return patient

    class Meta:
        model = CellImage
        fields = ('patient', 'image', 'medication', 'scale')


class AddMedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ('medication_type', 'patient', 'patient_research')


class AddDictForm(forms.ModelForm):
    class Meta:
        model = DictCellsCharacteristics
        fields = ('characteristic_name', )


class AddTermForm(forms.ModelForm):
    class Meta:
        model = Terms
        fields = ('term_name', 'definition', 'definition')


class AddCellCharacteristicForm(forms.ModelForm):
    class Meta:
        model = CellCharacteristic
        fields = ('dictcharcteristics', 'cell', 'value')


class AddSystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ('medication', 'conditions', 'glass_type', 'artifacts')


class AddPatientResearchForm(forms.ModelForm):
    class Meta:
        model = PatientResearch
        fields = ('date_begin', 'date_end', 'patient', 'researcher')
        widgets = {
            'date_begin': DateInput(),
            'date_end': DateInput(),
        }


class AddMarkerForm(forms.ModelForm):
    class Meta:
        model = Marker
        fields = ('marker_name', 'marker_type')


class AddImmunophenotypingForm(forms.ModelForm):
    class Meta:
        model = Immunophenotyping
        fields = ('marker', 'medication', 'research', 'percent_positive_cells')


class AddResearchedObjectForm(forms.ModelForm):
    class Meta:
        model = ResearchedObject
        fields = ('count_object', 'sprout_type', 'norm')

