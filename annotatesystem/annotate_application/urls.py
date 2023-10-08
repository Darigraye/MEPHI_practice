from django.urls import path
from .views import SignUpView, SignInView, ShowProfileView, SignOutView


urlpatterns = [
    path('registration/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('logout/', SignOutView.as_view(), name='logout'),
    path('<str:login>/', ShowProfileView.as_view(), name='profile')
]
