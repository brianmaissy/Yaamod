from django.urls import path
import django.contrib.auth.views as auth_views

from . import views

urlpatterns = [
    path('', views.SynagogueList.as_view(), name='synagogue_list'),
    path('synagogue/<int:pk>', views.SynagogueDetail.as_view(),
         name='synagogue_detail'),
    path('member/<int:pk>', views.MemberDetail.as_view(),
         name='member_detail'),

    path('login', views.LoginView.as_view()),
    path('add_user', views.AddUserView.as_view()),
    path('add_synagogue', views.AddSynagogueView.as_view()),
    path('logout', views.LogoutView.as_view()),
    path('reset_password', views.PasswordResetView.as_view()),

    # this should be changed for our own reset confirm page, but the name should anyway be password_reset_confirm
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm')
]
