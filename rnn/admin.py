from django.contrib import admin
from .models import GeneratedMusic, GeneratedMusicAlbum

# Register your models here.
class GeneratedMusicAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)

admin.site.register(GeneratedMusic, GeneratedMusicAdmin)

class GeneratedMusicAlbumAdmin(admin.ModelAdmin):
    readonly_fields = ("created",)

admin.site.register(GeneratedMusicAlbum, GeneratedMusicAlbumAdmin)