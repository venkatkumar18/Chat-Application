from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),

    # path('home/',views.home,name='home'),
    path('<int:room>/',views.room,name='room'),
    path('checkview',views.checkview,name='checkview'),
    path('<int:room>/trigger/',views.trigger_celery,name='trigger'),
    path('gethistory',views.get_user_history,name='chathistory'),
]

