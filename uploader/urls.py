from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('logout/', views.user_logout, name='user_logout'),
    path('retrieve-corpus/', views.retrieve_corpus, name='retrieve_corpus'),
    path('word_frequency_table/', views.word_frequency_table, name='word_frequency_table'),
]