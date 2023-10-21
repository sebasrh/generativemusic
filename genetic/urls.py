from django.urls import path
from genetic import views

urlpatterns = [
    path('', views.genetic, name="genetic"),
    path('generations/<int:generations_id>/',
         views.generations, name="generations"),
]
