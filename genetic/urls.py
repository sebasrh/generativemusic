from django.urls import path
from genetic import views

urlpatterns = [
    path('', views.genetic, name="genetic"),
    path('generations/<int:album_id>/',
         views.generations, name="generations"),
]
