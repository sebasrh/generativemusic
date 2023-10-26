from django.forms import ModelForm
from .models import GeneratedMusicAlbum


class GeneratedMusicImageForm(ModelForm):
    class Meta:
        model = GeneratedMusicAlbum
        fields = ['img']
