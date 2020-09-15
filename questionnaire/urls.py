"""
urls
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-11
@desc:
"""
from django.urls import path

from questionnaire import views


urlpatterns = [
    path('', views.questionnaire, name='home'),
    path('login/', views.login_page, name='login'),
    path('loginuser/', views.login_user, name='loginUser'),
    path('logout/', views.logout_user, name='logout'),
    path('create/', views.create, name='create'),
    path('save/', views.save, name='save'),
    path('view/', views.view_questionnaire, name='view'),
    path('modify/<str:ri>/', views.modify, name='modify'),
    path('result/', views.result_notify, name='result')
]