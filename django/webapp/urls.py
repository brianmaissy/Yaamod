from django.urls import path

from . import views

urlpatterns = [
    path('', views.SynagogueList.as_view(), name='synagogue_list'),
    path('synagogue/<int:pk>', views.SynagogueDetail.as_view(),
         name='synagogue_detail'),
    path('member/<int:pk>', views.MemberDetail.as_view(),
         name='member_detail'),
]
