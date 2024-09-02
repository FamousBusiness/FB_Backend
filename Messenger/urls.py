from django.urls import path
from . import views


urlpatterns = [
    path('', views.MessngerUsersListApiView.as_view(), name='users_list'),
    path('<str:username>/', views.ChatMessengerApiView.as_view(), name='chat_message'),
]
