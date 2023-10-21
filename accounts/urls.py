from django.urls import path
from accounts import views

urlpatterns = [
    path('signin/', views.signin, name="signin"),
    path('signup/', views.signup, name="signup"),
    path('signup/check_username_availability/', views.check_username_availability,
         name='check_username_availability'),
    path('logout/', views.signout, name="signout")
]
