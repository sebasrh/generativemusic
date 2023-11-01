from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .forms import GeneratedMusicImageForm
from .models import GeneratedMusicAlbum
import os
import shutil
from Neural.predict import generatemusic
# Create your views here.


@login_required
def rnn(request):
    user = request.user
    if user.is_superuser and request.method == 'POST':

        generatemusic(25, 20) # 25 notas, 20 melodías

        return redirect('rnn')

    elif request.method == 'GET':
        albums = GeneratedMusicAlbum.objects.all().order_by('created')
        return render(request, 'rnn.html', {'albums': albums, 'user': user})
    else:
        # Si el usuario no es superusuario, redirigir a la página de inicio
        return redirect('index')


@login_required
def generated(request, album_id):
    user = request.user

    # Obtén el objeto Album por su clave primaria (id)
    album = get_object_or_404(GeneratedMusicAlbum, pk=album_id)

    # Obtener las melodías generadas
    melodies = album.generated_music.all()

    # Duración del álbum
    duration = 0.0

    # Obtener la duración total del álbum
    for melody in melodies:
        duration += float(melody.duration)

    album.duration = duration

    return render(request, 'generated.html', {'melodies': melodies, 'user': user, 'album': album})


@login_required
def delete_rnn(request, album_id):
    user = request.user
    if user.is_superuser and request.method == 'POST':
        try:
            album = get_object_or_404(GeneratedMusicAlbum, pk=album_id)

            # Eliminar el album de la carpeta media
            folder_album = f'media/midi_files/{album.id}'
            if os.path.exists(folder_album):
                print("Eliminando carpeta del album", folder_album)
                shutil.rmtree(folder_album)

            # Eliminar el album de la base de datos
            album.generated_music.all().delete()
            album.delete()

            return redirect('rnn')

        except Exception as e:
            response_data = {
                'success': False,
                'error_message': str(e),
            }
            return JsonResponse(response_data, status=400)
    else:
        # Si el usuario no es superusuario, redirigir a la página de inicio
        return redirect('index')


@login_required
def uploadAlbumCover(request, album_id):
    # Obtener el usuario actual
    user = request.user

    # Obtener el objeto Album por su clave primaria (id)
    album = get_object_or_404(GeneratedMusicAlbum, pk=album_id)

    if user.is_superuser and request.method == 'POST':
        try:
            # Obtener la imagen del formulario
            form = GeneratedMusicImageForm(
                request.POST, request.FILES, instance=album)

            # Verificar si el formulario es válido
            if form.is_valid():
                form.save()
                return redirect('rnn')
            else:
                form = GeneratedMusicImageForm(instance=album)

        except Exception as e:
            response_data = {
                'success': False,
                'error_message': str(e)
            }
            return JsonResponse(response_data, status=400)

    elif user.is_superuser and request.method == 'GET':

        # Obtener el formulario
        form = GeneratedMusicImageForm(instance=album)

        return render(request, 'uploadAlbumCover.html', {'form': form, 'album': album})
    else:
        # Si el usuario no es superusuario, redirigir a la página de inicio
        return redirect('index')
