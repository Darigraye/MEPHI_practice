from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .forms import SignUpForm, SignInForm, CreatePatientForm
from .models import MEPHIUser, MEPHIUserCategory


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "auth/registration.html"


class SignInView(LoginView):
    form_class = SignInForm
    template_name = "auth/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        print(form.get_user().login)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("profile", kwargs={"login": self.request.user.login})


class ShowProfileView(LoginRequiredMixin, DetailView):
    model = MEPHIUser
    template_name = 'auth/show_profile.html'
    slug_url_kwarg = 'login'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caregory'] = MEPHIUserCategory.objects.get(pk=self.object.user_category_id).category_name
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(MEPHIUser, login=self.kwargs.get('login'))


class SignOutView(LoginRequiredMixin, LogoutView):
    login_url = reverse_lazy('login')
    template_name = 'auth/logout.html'


class HomePageView(TemplateView):
    template_name = 'general/home_page.html'


class CreatePatientView(CreateView):
    form_class = CreatePatientForm
    template_name = "general/create_user.html"
