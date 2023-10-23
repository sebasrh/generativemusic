from django.contrib import admin
from .models import Evaluation, GeneratedMelody, GeneticAlgorithmInfo, MusicalRepresentation, Album

# Add filters and search fields for each model


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('rating', 'user', 'melody', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'melody__title')

    def melody(self, obj):
        return obj.mel.title


@admin.register(GeneratedMelody)
class MelodyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'generation','display_user_ratings',
                    'average_ratings', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'generation')

    def display_user_ratings(self, obj):
        return ', '.join([str(evaluation.rating) for evaluation in obj.user_rating.all()])

    display_user_ratings.short_description = 'User Ratings'


@admin.register(GeneticAlgorithmInfo)
class GeneticAlgorithmInfoAdmin(admin.ModelAdmin):
    list_display = ('population_size', 'num_generations',
                    'num_selected', 'num_children', 'crossover_probability', 'mutation_probability')
    search_fields = ('id',)


@admin.register(MusicalRepresentation)
class MusicalRepresentationAdmin(admin.ModelAdmin):
    list_display = ('key_signature', 'scale_signature', 'tempo',
                    'has_back_track', 'uses_arp_or_scale')
    list_filter = ('key_signature', 'scale_signature', 'tempo',
                   'has_back_track', 'uses_arp_or_scale')
    search_fields = ('key_signature', 'scale_signature')


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_musical_representation',
                    'display_ga_info', 'display_melodies', 'created_at')
    list_filter = ('musical_representation__key_signature', 'created_at')
    search_fields = ('musical_representation__key_signature', )

    def display_musical_representation(self, obj):
        return f"{obj.musical_representation.key_signature} - {obj.musical_representation.scale_signature} - Tempo: {obj.musical_representation.tempo}"

    display_musical_representation.short_description = 'Musical Representation'

    def display_ga_info(self, obj):
        return f"Pop. Size: {obj.ga_info.population_size}, Generations: {obj.ga_info.num_generations}"

    display_ga_info.short_description = 'Genetic Algorithm Info'

    def display_melodies(self, obj):
        return ', '.join([str(melody.id) for melody in obj.melodies.all()])

    display_melodies.short_description = 'Melodies'
