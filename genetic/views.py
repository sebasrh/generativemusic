from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import pickle
import json
import cloudinary
import os
import shutil
from algorithm.gen_alg import algorithm_args, generate_population, evolve_population
from algorithm.representation import representation
from algorithm.main import main
from .models import Album, Evaluation
from .forms import AlbumImageForm


def save_population(population, album):
    # Carpeta para guardar los archivos
    folder = f"algorithm/midi_out/{album.id}"

    # Si la carpeta no existe, crearla
    if not os.path.exists(folder):
        os.mkdir(folder)

    # Nombre del archivo pickle
    file_name = f"{folder}/population_{album.generation_number}.pkl"

    # Guardar la población en un archivo pickle
    with open(file_name, "wb") as file:
        pickle.dump(population, file)

    # Nombre del archivo txt
    file_name = f"{folder}/population_{album.generation_number}.txt"

    # Guardar la población en archivos de texto
    with open(file_name, "w") as file:
        for melody in population:
            file.write(str(melody) + "\n")

    # Guardar el archivo txt en Cloudinary
    cloudinary.uploader.upload(file_name, resource_type="auto",
                               public_id=f"algorithm/{album.id}/population_{album.generation_number}.txt")


def load_population(album):
    # Carpeta para cargar los archivos
    folder = f"algorithm/midi_out/{album.id}"

    # Nombre del archivo pickle
    file_name = f"{folder}/population_{album.generation_number}.pkl"

    # Cargar la población desde el archivo pickle
    with open(file_name, "rb") as file:
        population = pickle.load(file)

    return population


@login_required
def genetic(request):
    user = request.user
    if user.is_superuser and request.method == 'POST':

        album = main()

        args_1 = album.musical_representation
        args_2 = album.ga_info

        rep_obj = representation(args_1.key_signature, args_1.scale_signature, args_1.tempo,
                                 args_1.has_back_track, args_1.uses_arp_or_scale)

        alg_args = algorithm_args(args_2.population_size,
                                  args_2.num_generations, args_2.num_selected, args_2.num_children, args_2.crossover_probability, args_2.mutation_probability)

        # Generar la población inicial
        population = generate_population(rep_obj, alg_args)

        # Guardar la población inicial
        save_population(population, album)

        # generar melodias
        for melody in population:
            representation.generate_melody(rep_obj, melody, album)

        # Calcular la duración de la música generada
        album.duration = album.calculate_duration()

        # Guardar la música generada
        album.save()

        return redirect('genetic')

    elif request.method == 'GET':
        albums = Album.objects.all().order_by('-created_at')
        return render(request, 'genetic.html', {'albums': albums, 'user': user})

    else:
        # Si el usuario no es superusuario, redirigir a la página de inicio
        return redirect('index')


@login_required
def delete_genetic(request, album_id):
    user = request.user
    if user.is_superuser and request.method == 'POST':
        try:
            album = get_object_or_404(Album, pk=album_id)

            # Eliminar los archivos de la carpeta midi_out
            folder_pop = f"algorithm/midi_out/{album.id}/"
            if os.path.exists(folder_pop):
                # eliminar la carpeta aunque no esté vacía
                shutil.rmtree(f"{folder_pop}")

            # Eliminar el album de la carpeta media/melodies
            folder_album = f"media/melodies/{album.id}/"
            if os.path.exists(folder_album):
                # eliminar la carpeta aunque no esté vacía
                shutil.rmtree(f"{folder_album}")

            # Eliminar el álbum
            album.melodies.all().delete()
            album.musical_representation.delete()
            album.ga_info.delete()
            album.delete()

            return redirect('genetic')

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
    album = get_object_or_404(Album, pk=album_id)

    if user.is_superuser and request.method == 'POST':
        try:
            # Obtener la imagen del formulario
            form = AlbumImageForm(request.POST, request.FILES, instance=album)

            # Verificar si el formulario es válido
            if form.is_valid():
                form.save()
                return redirect('genetic')
            else:
                form = AlbumImageForm(instance=album)

        except Exception as e:
            response_data = {
                'success': False,
                'error_message': str(e)
            }
            return JsonResponse(response_data, status=400)

    elif user.is_superuser and request.method == 'GET':

        # Obtener el formulario
        form = AlbumImageForm(instance=album)

        return render(request, 'uploadAlbumCover.html', {'form': form, 'user': user})

    else:
        # Si el usuario no es superusuario, redirigir a la página de inicio
        return redirect('index')


@login_required
def generations(request, album_id):
    user = request.user

    # Obtén el objeto Album por su clave primaria (id)
    album = get_object_or_404(Album, pk=album_id)

    # Obtener la última generación de melodías
    latest_generation = album.melodies.filter(
        generation=album.generation_number).order_by('created_at')

    # Consultar para obtener las calificaciones del usuario actual
    user_ratings = Evaluation.objects.filter(
        user=user, mel__in=latest_generation)

    user_ratings_data = {}  # Un diccionario para almacenar los datos de calificación

    # Iterar sobre las calificaciones del usuario y almacenarlas en el diccionario
    for rating in user_ratings:
        user_ratings_data[rating.mel.id] = rating.rating

    user_ratings_json = json.dumps(user_ratings_data)  # Convertir a JSON

    # Verificar si el usuario ya ha calificado las melodías
    for melody in latest_generation:
        melody.user_has_rated = melody.user_has_rated(user)

    return render(request, 'generations.html', {'melodies': latest_generation, 'user_ratings': user_ratings_json, 'user': user, 'album': album})


@login_required
def evaluate(request, album_id, melody_id):
    user = request.user
    if request.method == 'POST':
        try:
            # Obtener el objeto Album por su clave primaria (id)
            album = Album.objects.get(pk=album_id)

            # Obtener el objeto Melody por su clave primaria (id)
            melody = album.melodies.get(pk=melody_id)

            # Verifica si el usuario ya ha calificado esta melodía
            if melody.user_has_rated(user):
                response_data = {
                    'success': False,
                    'error_message': 'El usuario ya ha calificado esta melodía.'
                }
                return JsonResponse(response_data, status=400)

            else:
                # Obtener la calificación del usuario
                rating = request.POST.get('ratings')

                # Crear una nueva calificación
                evaluation = Evaluation(
                    user=user, mel=melody, rating=rating)
                evaluation.save()

                # Agregar la calificación a la melodía
                melody.user_rating.add(evaluation)

                # Actualizar la calificación promedio de la melodía
                melody.average_users_ratings()

                response_data = {
                    'success': True,
                    'average_rating': melody.average_ratings,
                    'users_ratings_count': melody.user_rating.all().count()
                }
                # Registro de éxito
                return JsonResponse(response_data, status=200)

        except Exception as e:
            response_data = {
                'success': False,
                'error_message': str(e)
            }
            return JsonResponse(response_data, status=400)


@login_required
def evolve(request, album_id):
    user = request.user
    if user.is_superuser and request.method == 'POST':
        try:
            # Obtener el objeto Album por su clave primaria (id)
            album = get_object_or_404(
                Album, pk=album_id)

            # Verificar si el número de generación actual es mayor que el número total de generaciones
            if album.generation_number > album.ga_info.num_generations:
                response_data = {
                    'success': False,
                    'error_message': 'The number of generations has been reached'
                }
                return JsonResponse(response_data, status=400)

            # Si el número de generación actual es menor que el número total de generaciones, evolucionar
            else:
                args_1 = album.musical_representation
                args_2 = album.ga_info

                rep_obj = representation(args_1.key_signature, args_1.scale_signature, args_1.tempo,
                                         args_1.has_back_track, args_1.uses_arp_or_scale)

                alg_args = algorithm_args(args_2.population_size,
                                          args_2.num_generations, args_2.num_selected, args_2.num_children, args_2.crossover_probability, args_2.mutation_probability)

                # Cargar la población actual
                population = load_population(album)

                # Obtener todas las melodías
                mels = album.melodies.all()

                # Lista de promedios de calificaciones de melodías en mels (GeneratedMelody)
                avg_ratings = [mel.average_ratings for mel in mels]

                # Asignar el promedio de calificaciones como fitness a cada melodía en la población
                for ind, avg_rating in zip(population, avg_ratings):
                    ind.fitness.values = (avg_rating,)

                # Evolucionar la población actual y obtener la nueva población
                new_pop = evolve_population(population, alg_args)

                # Actualizar el número de generación
                album.increase_generation_number()

                # generar melodias
                for melody in new_pop:
                    representation.generate_melody(
                        rep_obj, melody, album)

                # Guardar la nueva población
                save_population(new_pop, album)

                return redirect('generations', album_id=album_id)
        except Exception as e:
            # Manejar errores adecuadamente y mostrar mensajes de error
            response_data = {
                'success': False,
                'error_message': str(e)
            }
            return JsonResponse(response_data, status=400)

    else:
        # Si el usuario no es superusuario, redirigir a la página de inicio
        return redirect('index')


# Vista de las 10 mejores melodías de todos los albums
@login_required
def top_rated(request):
    if request.method == 'GET':
        # Obtener todos los albums
        albums = Album.objects.all()

        # Obtener todas las melodías de todos los albums
        melodies = []

        # Iterar sobre los albums y obtener todas las melodías
        for album in albums:
            melodies += album.melodies.all()

        # Obtener las melodías calificadas
        top_rated_melodies = [mel for mel in melodies if mel.average_ratings > 0.0]

        # Ordenar las melodías por calificación promedio y número de calificaciones
        top_rated_melodies.sort(key=lambda x: (x.average_ratings, x.user_rating.all().count()), reverse=True)

        # Obtener las 10 mejores melodías
        top_rated_melodies = top_rated_melodies[:10]

        # Obtener el álbum de cada melodía
        for melody in top_rated_melodies:
            melody.album = melody.album_set.first()
            
        # Si no hay melodías, mostrar un mensaje
        if not top_rated_melodies:
            return render(request, 'top_rated.html', {'message': 'No hay melodías calificadas'})

        return render(request, 'top_rated.html', {'melodies': top_rated_melodies})
