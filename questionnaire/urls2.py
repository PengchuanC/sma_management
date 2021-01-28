from django.urls import path
from questionnaire import views2 as views


urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('authenticate/', views.post_authenticate, name='authenticate'),
    path('auth/', views.authenticate, name='auth'),
    path('submit/', views.submit, name='submit'),
    path('success/', views.success, name='success'),
]
