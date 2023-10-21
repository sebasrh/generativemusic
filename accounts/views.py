from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse

# Create your views here.


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'GET':
            return render(request, 'signup.html', {'form': UserCreationForm()})
        else:
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            error = validate_signup_data(username, password1, password2)

            if error:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': error
                })
            else:
                user = User.objects.create_user(
                    username=username, password=password1)
                user.save()
                login(request, user)
                return redirect('index')


def signin(request):
    # Si el usuario no está autenticado, mostrar la página de inicio de sesión
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'GET':
            return render(request, 'signin.html', {
                'form': AuthenticationForm
            })
        else:
            user = authenticate(
                request, username=request.POST["username"], password=request.POST["password"])

            if user is None:
                return render(request, 'signin.html', {
                    'form': AuthenticationForm,
                    'error': 'Nombre de usuario o contraseña incorrectos'
                })
            else:
                login(request, user)
                return redirect('index')


def check_username_availability(request):
    if request.method == 'POST':
        username = request.POST['username']
        try:
            User.objects.get(username=username)
            # El nombre de usuario ya existe
            return JsonResponse({'is_taken': True})
        except User.DoesNotExist:
            # El nombre de usuario no existe
            return JsonResponse({'is_taken': False})
    # Si no es una solicitud POST, devuelve un error
    return JsonResponse({'error': 'Invalid request'})


def validate_signup_data(username, password1, password2):
    error = None

    # Validaciones para los campos obligatorios
    if not username and not password1 and not password2:
        error = 'Todos los campos son obligatorios'

    # Validaciones para el nombre de usuario
    elif User.objects.filter(username=username).exists():
        error = 'El nombre de usuario ya está en uso'
    elif not username:
        error = 'Se requiere un nombre de usuario'
    elif len(username) < 4:
        error = 'El nombre de usuario debe tener al menos 4 caracteres'
    elif len(username) > 20:
        error = 'El nombre de usuario debe tener como máximo 20 caracteres'

    # Validaciones para la contraseña
    elif not password1:
        error = 'Se requiere una contraseña'
    elif len(password1) < 8:
        error = 'La contraseña debe tener al menos 8 caracteres'
    elif len(password1) > 20:
        error = 'La contraseña debe tener como máximo 20 caracteres'
    elif not password2:
        error = 'Se requiere la confirmación de contraseña'
    elif password1 != password2:
        error = 'Las contraseñas no coinciden'

    return error


@login_required
def signout(request):
    logout(request)
    return redirect('signin')
