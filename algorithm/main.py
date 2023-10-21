# main.py
# Composición Evolutiva
# main.py es responsable de inicializar el programa, así como de manejar los argumentos de línea de comandos

# from algorithm.representation import representation
# from algorithm.gen_alg import algorithm_args, run_genetic_algorithm
from genetic.models import GeneticAlgorithmInfo, MusicalRepresentation, Album
import random

key_sig = ["Cb", "Gb", "Db", "Ab", "Eb", "Bb",
           "F", "C", "G", "D", "A", "E", "B", "F#", "C#"]

scales_sig = ["major", "minor"]

bpm = [60, 70, 80, 90, 100, 110, 120, 130, 140, 160]

bt = ['t', 'f']

aos = ['t', 'f']

bt = ['True', 'False']

aos = ['True', 'False']

def main():
    """
    Inputs de la representación musical
    """
    key_signature = random.choice(key_sig)

    scale_signature = random.choice(scales_sig)

    tempo = random.choice(bpm)

    back_track = random.choice(bt)
    
    arp_or_scale = random.choice(aos)

    # Crear objetos y argumentos
    rep_model = MusicalRepresentation(
        key_signature=key_signature,
        scale_signature=scale_signature,
        tempo=tempo,
        has_back_track=back_track,
        uses_arp_or_scale=arp_or_scale
    )
    rep_model.save()

    """
    Inputs del algoritmo genético
    """

    # Número de melodías en la población inicial
    popsize = 20

    # Número de generaciones 
    ngen = 20

    # Número de individuos seleccionados para la próxima generación  
    mu = 10 # 50% de la población inicial

    # Número de hijos producidos en cada generación 
    lambda_ = 18 # 90% de la población inicial

    # Probabilidad de descendencia por cruce (0-1)
    cxpb = 0.8

    # Probabilidad de descendencia por mutación (0-1)
    mutpb = 0.1

    # Crear objetos y argumentos
    alg_model = GeneticAlgorithmInfo(
        population_size=popsize,
        num_generations=ngen,
        num_selected=mu,
        num_children=lambda_,
        crossover_probability=cxpb,
        mutation_probability=mutpb
    )
    alg_model.save()

    # Crear objeto global GeneratedMusic
    generated_music = Album(
        musical_representation=rep_model,
        ga_info=alg_model
    )
    generated_music.save()

    return generated_music
