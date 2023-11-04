# gen_alg.py
# Composición Evolutiva
# gen_alg.py contiene el código para los datos y funciones del algoritmo genético.

import random
from deap import base, creator, tools
from algorithm.representation import Melody


class algorithm_args:
    """
    El objeto algorithm_args contiene todos los argumentos del algoritmo recibidos.
    algorithm_args simplifica la cantidad de argumentos que deben enviarse a las funciones.
    """

    def __init__(self, pop_size, ngen, mu, lambda_, cxpb, mutpb):
        """
        Inicializa el objeto algorithm_args con los argumentos dados.
        Entrada: pop_size: int, el tamaño de la población inicial
        ngen: int, el número de generaciones que se ejecutará el algoritmo genético
        mu: int, el número de individuos a seleccionar para la próxima generación
        lambda_: int, establece el número de hijos a producir en cada generación
        cxpb: float, la probabilidad de que un descendiente sea producido por cruce
        mutpb: float, la probabilidad de que un descendiente sea producido por mutación |
        Salida: objeto algorithm_args
        """
        self.pop_size = pop_size
        self.ngen = ngen
        self.mu = mu
        self.lambda_ = lambda_
        self.cxpb = cxpb
        self.mutpb = mutpb
        return


toolbox = base.Toolbox()  # Toolbox de deap


def cx_music(input_mel1, input_mel2):
    """
    cx_music() realiza una operación de cruce en dos melodías dadas
    Entrada: input_mel1: Melody, la primera melodía | input_mel2: Melody, la segunda melodía
    Salida: child1: Melody, [[Primera mitad de las medidas de input_mel2], [Segunda mitad de las medidas de input_mel1]] 
    child2, Melody: [[Primera mitad de las medidas de input_mel1], [Segunda mitad de las medidas de input_mel2]]
    """
    # Hacer copia temporal de input_mel1 para el segundo hijo
    mel_copy = input_mel1.copy()

    # Hijo 1
    input_mel1.cross_mel(input_mel2, True)

    # Hijo 2
    input_mel2.cross_mel(mel_copy, False)

    print("Cruce realizado")

    return input_mel1, input_mel2


def mut_melody(input_mel):
    """
    mut_melody() muta una melodía dada. La función itera sobre toda la melodía
    realizando una moneda al aire en cada nota determinando si debe desplazarse hacia arriba o hacia abajo.
    Entrada: input_mel: Melody, la melodía a mutar
    Salida: input_mel: Melody, la melodía mutada
    """
    for measure in input_mel.melody_list:
        for note in measure.measure_list:
            if random.random() < 0.5:
                if note.note_pitch != 84 and note.note_pitch != 128:
                    note.pitch_shift()
            else:
                if note.note_pitch != 60 and note.note_pitch != 128:
                    note.pitch_shift(up=False)

    print("Mutación realizada")

    return input_mel,


def generate_population(rep_obj, alg_args):
    """
    Genera la población inicial de melodías.
    Entrada: rep_obj: representation, contiene los argumentos de representación necesarios
    alg_args: algorithm_args, contiene los argumentos necesarios del algoritmo genético
    Salida: population: list, una lista de melodías
    """
    # La función de fitness tiene un peso, maximizar las buenas melodías
    # los pesos deben ser tuplas, pero solo tenemos un parámetro para maximizar
    creator.create("FitnessMax", base.Fitness, weights=(1.0, ))
    # La clase Melody debe heredar de la clase FitnessMax
    creator.create("Melody", Melody, fitness=creator.FitnessMax)

    # La clase Melody debe registrarse en el Toolbox de deap
    toolbox.register("melody", creator.Melody,
                     scale=rep_obj.scale_signature, key=rep_obj.key_signature)
    toolbox.register("population", tools.initRepeat, list, toolbox.melody)

    # Crear la población inicial
    population = toolbox.population(n=alg_args.pop_size)

    return population


def evolve_population(population, alg_args):
    """
    Crea una nueva generación de melodías a partir de la población actual.
    Entrada: population: list, una lista de melodías |
    alg_args: algorithm_args, contiene los argumentos necesarios del algoritmo genético.
    Salida: population: list, una lista de melodías
    """

    for i in range(len(population)):
        print('individuo')
        print(population[i].fitness.values)

    toolbox.register("mate", cx_music)  # Cruce
    toolbox.register("mutate", mut_melody)  # Mutación
    toolbox.register("select", tools.selRoulette)  # Selección por ruleta

    # La cantidad de individuos elite que se mantendrán en la siguiente generación
    num_elite = 2 # 10% de la población inicial

    # Seleccionar los individuos elite
    elite = tools.selBest(population, num_elite)

    for ind in elite:
        print('elite')
        print(ind.fitness.values)

    # Clonar los individuos elite 
    elite_clone = list(map(toolbox.clone, elite))

    # Seleccionar los padres
    seleted = toolbox.select(population, alg_args.mu)

    for ind in seleted:
        print('seleccionados')
        print(ind.fitness.values)

    # Clonar los padres para la descendencia
    seleted_clone = list(map(toolbox.clone, seleted))

    # Descendencia
    offspring = []

    # Generar la descendencia
    while len(offspring) < alg_args.lambda_:
        # Seleccionar dos padres
        ind1, ind2 = random.sample(seleted_clone, 2)

        # Cruzar los padres
        if random.random() < alg_args.cxpb:
            ind1, ind2 = toolbox.mate(ind1, ind2)

            # Eliminar la aptitud de los hijos
            del ind1.fitness.values
            del ind2.fitness.values

        # Agregar los hijos a la descendencia
        offspring.append(ind1)
        offspring.append(ind2)

    # Mutar la descendencia
    for mutant in offspring:
        if random.random() < alg_args.mutpb:
            toolbox.mutate(mutant)
            del mutant.fitness.values

    # Agregar los individuos elite a la descendencia
    offspring.extend(elite_clone)

    for ind in offspring:
        print('descendencia')
        print(ind.fitness.values)

    # Reemplazar la población actual con la descendencia
    population[:] = offspring

    return population

