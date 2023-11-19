from django.urls import path
from .views import *


urlpatterns = [
    path('registration/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('logout/', SignOutView.as_view(), name='logout'),
    path('home/', HomePageView.as_view(), name='home'),
    path('add_patient/', CreatePatientView.as_view(), name='add_patient'),
    path('add_diagnosis/', CreateDiagnosisView.as_view(), name='add_diagnosis'),
    path('<str:username>/', ShowProfileView.as_view(), name='profile')
]
