from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .forms import *
from .models import *
from .utils import MetaDataMixin


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "auth/registration.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_active = SystemParameters.objects.get(parameter_name="REGISTRATION").t_isactive
        param = SystemParameters.objects.get(parameter_name="REGISTRATION").parameter_value_bool
        context['registration'] = param if is_active else None
        return context



class SignInView(LoginView):
    form_class = SignInForm
    template_name = "auth/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        print(form.get_user().username)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("profile", kwargs={"username": self.request.user.username})


class ShowProfileView(LoginRequiredMixin, DetailView, MetaDataMixin):
    model = MEPHIUser
    template_name = 'auth/show_profile.html'
    slug_url_kwarg = 'login'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caregory'] = MEPHIUserCategory.objects.get(pk=self.object.user_category_id).category_name
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))

    def get_object(self, queryset=None):
        return get_object_or_404(MEPHIUser, username=self.kwargs.get('username'))


class SignOutView(LoginRequiredMixin, LogoutView):
    login_url = reverse_lazy('login')
    template_name = 'auth/logout.html'


class HomePageView(TemplateView):
    template_name = 'general/home_page.html'


class CreatePatientView(CreateView, MetaDataMixin):
    form_class = CreatePatientForm
    template_name = "functions/create_user.html"
    success_url = reverse_lazy('add_patient')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Patient.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class CreateDiagnosisView(CreateView, MetaDataMixin):
    form_class = CreateDiagnosisForm
    template_name = "functions/create_diagnosis.html"
    success_url = reverse_lazy('add_diagnosis')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = ResearchResult.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class CreateCellTypeView(CreateView, MetaDataMixin):
    form_class = CreateCellTypeForm
    template_name = "functions/create_cell_type.html"
    success_url = reverse_lazy('add_cell_type')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = CellType.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddImageView(CreateView, MetaDataMixin):
    form_class = AddImageForm
    template_name = "functions/create_image.html"
    success_url = reverse_lazy('add_image')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = CellImage.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddMedicationView(CreateView, MetaDataMixin):
    form_class = AddMedicationForm
    template_name = "functions/create_medication.html"
    success_url = reverse_lazy('add_medication')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Medication.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddResearchView(CreateView, MetaDataMixin):
    form_class = AddMedicationForm
    template_name = "functions/create_medication.html"
    success_url = reverse_lazy('add_medication')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = PatientResearch.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddDictView(CreateView, MetaDataMixin):
    form_class = AddDictForm
    template_name = "functions/create_dict.html"
    success_url = reverse_lazy('add_dict_characteristics')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = DictCellsCharacteristics.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddTermsView(CreateView, MetaDataMixin):
    form_class = AddTermForm
    template_name = "functions/create_term.html"
    success_url = reverse_lazy('add_terms')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Terms.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddCellCharacteristicView(CreateView, MetaDataMixin):
    form_class = AddCellCharacteristicForm
    template_name = "functions/create_cell_characteristic.html"
    success_url = reverse_lazy('add_cell_characteristic')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = CellCharacteristic.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddSystemSettingsView(CreateView, MetaDataMixin):
    form_class = AddSystemSettingsForm
    template_name = "functions/create_system_settings.html"
    success_url = reverse_lazy('add_system_settings')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = SystemSettings.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddPatientResearchView(CreateView, MetaDataMixin):
    form_class = AddPatientResearchForm
    template_name = "functions/create_patient_research.html"
    success_url = reverse_lazy('add_patient_research')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = PatientResearch.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddMarkerView(CreateView, MetaDataMixin):
    form_class = AddMarkerForm
    template_name = "functions/create_marker.html"
    success_url = reverse_lazy('add_marker')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Marker.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddImmunoView(CreateView, MetaDataMixin):
    form_class = AddImmunophenotypingForm
    template_name = "functions/create_immuno.html"
    success_url = reverse_lazy('add_marker')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Immunophenotyping.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))


class AddResearchedObject(CreateView, MetaDataMixin):
    form_class = AddResearchedObjectForm
    template_name = "functions/create_researched_object.html"
    success_url = reverse_lazy('add_marker')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = ResearchedObject.objects.all()
        context = super().get_context_data(**kwargs)
        additional_context = super().get_user_context()

        return dict(list(context.items()) + list(additional_context.items()))