from django.urls import path
from .views import *


urlpatterns = [
    path('registration/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('logout/', SignOutView.as_view(), name='logout'),
    path('home/', HomePageView.as_view(), name='home'),
    path('add_patient/', CreatePatientView.as_view(), name='add_patient'),
    path('add_diagnosis/', CreateDiagnosisView.as_view(), name='add_diagnosis'),
    path('add_cell_type/', CreateCellTypeView.as_view(), name='add_cell_type'),
    path('add_image/', AddImageView.as_view(), name='add_image'),
    path('add_medication/', AddMedicationView.as_view(), name='add_medication'),
    path('add_dict_characteristics/', AddDictView.as_view(), name='add_dict_characteristics'),
    path('add_terms/', AddTermsView.as_view(), name='add_terms'),
    path('add_cell_characteristic/', AddCellCharacteristicView.as_view(), name='add_cell_characteristic'),
    path('add_system_settings/', AddSystemSettingsView.as_view(), name='add_system_settings'),
    path('add_patient_research/', AddPatientResearchView.as_view(), name='add_patient_research'),
    path('add_marker/', AddMarkerView.as_view(), name='add_marker'),
    path('add_immunophenotipation/', AddImmunoView.as_view(), name='add_immunophenotipation'),
    path('add_researched_object/', AddResearchedObject.as_view(), name='add_researched_object'),
    path('<str:username>/', ShowProfileView.as_view(), name='profile')
]
