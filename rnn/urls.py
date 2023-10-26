from django.urls import path
from rnn import views

urlpatterns = [
     path('', views.rnn, name="rnn"),
     path('generated/<int:album_id>/', views.generated, name='generations'),
     path('delete/<int:album_id>/', views.delete_rnn, name='delete_rnn'),
     path('upload/<int:album_id>/', views.uploadAlbumCover, name='uploadAlbumCover'),
]
