from django.urls import path
from .views import SignUpView, SignInView, ShowProfileView, SignOutView, HomePageView


urlpatterns = [
    path('registration/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('logout/', SignOutView.as_view(), name='logout'),
    path('home/', HomePageView.as_view(), name='home'),
    path('<str:username>/', ShowProfileView.as_view(), name='profile')
]
