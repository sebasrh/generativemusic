from django.urls import path
from rnn import views

urlpatterns = [
     path('', views.rnn, name="rnn"),
]
