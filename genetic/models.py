from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField


class GeneratedMelody(models.Model):
    # Campos para representar la melodía
    title = models.CharField(max_length=255)

    mel = CloudinaryField('melody')
    
    user_rating = models.ManyToManyField('Evaluation')

    average_ratings = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])

    generation = models.PositiveIntegerField(default=1)

    duration = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def average_users_ratings(self):
        ratings = self.user_rating.all()
        if ratings:
            total_calificaciones = sum([c.rating for c in ratings])
            self.average_ratings = round(
                total_calificaciones / len(ratings), 1)
        else:
            self.average_ratings = 0.0
        self.save()

    def user_has_rated(self, user):
        """
        Verifica si el usuario ya ha calificado esta melodía.
        """
        return self.user_rating.filter(user=user).exists()

    def __str__(self):
        return f"{self.title} - id: {self.id} - created: {self.created_at}"

    class Meta:
        ordering = ['-created_at']


class Evaluation(models.Model):
    # Campos para representar la evaluación
    rating = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    mel = models.ForeignKey(GeneratedMelody, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating: {self.rating} - by: {self.user} - for: {self.mel.title}"

    class Meta:
        unique_together = ('user', 'mel')
        ordering = ['-created_at']


class GeneticAlgorithmInfo(models.Model):
    # Campos para registrar información sobre el algoritmo genético
    population_size = models.PositiveIntegerField()
    num_generations = models.PositiveIntegerField()
    num_selected = models.PositiveIntegerField()
    num_children = models.PositiveIntegerField()
    crossover_probability = models.FloatField()
    mutation_probability = models.FloatField()


class MusicalRepresentation(models.Model):
    # Campos para representar la música generada
    key_signature = models.CharField(max_length=5)
    scale_signature = models.CharField(max_length=10)
    tempo = models.PositiveIntegerField()
    has_back_track = models.BooleanField()
    uses_arp_or_scale = models.BooleanField()


class Album(models.Model):
    # Relación con la representación musical
    musical_representation = models.ForeignKey(
        MusicalRepresentation, on_delete=models.CASCADE)

    # Relación con la información sobre el algoritmo genético
    ga_info = models.ForeignKey(GeneticAlgorithmInfo, on_delete=models.CASCADE)

    # Relación con la melodía generada y añadir eliminación en cascada
    melodies = models.ManyToManyField(GeneratedMelody)

    generation_number = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    duration = models.FloatField(default=0.0)

    # Imagen de la portada del álbum (opcional) - Cloudinary Field para almacenar la imagen en la nube y no en el servidor local (media) - https://cloudinary.com/documentation/django_image_and_video_upload
    img = CloudinaryField('image', default='https://res.cloudinary.com/dgb26cwpx/image/upload/v1698017763/album_cover_default_pdxmu4.png')

    def increase_generation_number(self):
        self.generation_number += 1
        self.save()

    def calculate_duration(self):
        total_duration = 0
        for melody in self.melodies.all():
            total_duration += melody.duration
        return total_duration

    def __str__(self):
        return f"Album - created : {self.created_at}"

    class Meta:
        ordering = ['-created_at']
