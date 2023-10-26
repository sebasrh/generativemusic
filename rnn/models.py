from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.
class GeneratedMusic(models.Model):
    title = models.CharField(max_length=100)
    key = models.CharField(max_length=50)
    tempo = models.CharField(max_length=10)
    meter = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    duration = models.CharField(max_length=10)
    mel = CloudinaryField('melody')

class GeneratedMusicAlbum(models.Model):
    img = CloudinaryField('image', default='https://res.cloudinary.com/dgb26cwpx/image/upload/v1698017763/album_cover_default_pdxmu4.png')
    generated_music = models.ManyToManyField(GeneratedMusic)
    epoch = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)