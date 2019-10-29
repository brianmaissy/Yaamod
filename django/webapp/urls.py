from django.urls import path, include

from . import views

urlpatterns = [
    path('synagogue', views.SynagogueListCreateView.as_view()),
    path('synagogue/<int:pk>', views.SynagogueDetailView.as_view()),
    path('user', views.UserCreateAPIView.as_view()),
    path('login', views.LoginView.as_view()),
    path('logout', views.LogoutView.as_view()),

    path(r'password_reset/', include('django_rest_passwordreset.urls'))
]
