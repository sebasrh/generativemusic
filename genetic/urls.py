from django.urls import path
from genetic import views

urlpatterns = [
     path('', views.genetic, name="genetic"),
     path('generations/<int:album_id>/',
          views.generations, name="generations"),
     path('generations/<int:album_id>/evolve/', views.evolve, name="evolve"),

     path('generations/<int:album_id>/evaluate/<int:melody_id>/',
          views.evaluate, name="evaluate"),
]
