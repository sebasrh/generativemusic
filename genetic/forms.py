from django.forms import ModelForm
from .models import Album

class AlbumImageForm(ModelForm):
    class Meta:
        model = Album
        fields = ['img']
