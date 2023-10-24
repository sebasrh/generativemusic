# representation.py
# Composición Evolutiva
# representation.py es responsable de los datos de representación musical.

import random
import os
import cloudinary
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
from algorithm.music_data import *
from algorithm.midi_utils import convert_midi_to_mp3
from genetic.models import GeneratedMelody


class representation:
    """
    La clase representation contiene todos los argumentos necesarios de la línea de comandos para el archivo representation.py.
    Solo se crea una instancia para el programa de composición evolutiva.
    El objeto de representación simplifica el paso de los argumentos de representación.
    """

    def __init__(self, key_signature, scale_signature, tempo, back_track, arp_or_scale):
        """
        Inicializa una instancia de la clase representation con los argumentos dados por la línea de comandos.
        Entrada: key_signature: str, la armadura de clave para el programa | tempo: int, el tempo en pulsos por minuto (BPM)
        back_track: bool, habilita la pista de acompañamiento durante la reproducción | arp_or_scale: bool, dicta si la pista de acompañamiento reproduce
        un arpegio o una escala (Verdadero = arp, Falso = escala).
        Salida: Instancia de la clase representation
        """
        self.key_signature = key_signature
        self.scale_signature = scale_signature
        self.tempo = tempo
        self.back_track = back_track
        self.arp_or_scale = arp_or_scale
        self.melody_counter = 0

        return

    def melody_to_midi(self, melody, filename, folder):
        """
        Convierte un objeto Melody en un archivo MIDI que se puede reproducir y guardar.
        Entrada: melody: Melody, el objeto de melodía para convertir a MIDI | filename: str, el nombre de archivo (sin incluir la ruta) para el archivo MIDI
        Salida: guarda un archivo MIDI en el disco si filename no es Nada
        """
        # Imprime los argumentos de representación para la melodía actual
        print("Argumentos de representación para la melodía actual:")
        print(self.key_signature, 'key')
        print(self.scale_signature, 'scale')
        print(self.tempo, 'bpm')
        print(self.back_track, 'backing track')
        print(self.arp_or_scale, 'arp or scale')
        print(self.melody_counter, 'melody counter')

        mid = MidiFile(
            type=1)  # El Tipo 1 significa un archivo MIDI multipista síncrono
        track = MidiTrack(name="Lead")
        mid.tracks.append(track)
        track.append(MetaMessage('key_signature', key=self.key_signature))
        tempo = bpm2tempo(self.tempo)
        track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
        ticks_per_beat = mid.ticks_per_beat

        for measure in melody.melody_list:
            for note in measure.measure_list:
                beat_val = note.beats * ticks_per_beat
                beat_val = int(beat_val)
                if note.note_pitch == 128:
                    # Silencio
                    track.append(Message('note_off', note=60,
                                 velocity=note.velocity, time=0))
                    track.append(Message('note_off', note=60,
                                 velocity=note.velocity, time=beat_val))

                else:
                    # Nota activa
                    track.append(
                        Message('note_on', note=note.note_pitch, velocity=note.velocity, time=0))
                    track.append(
                        Message('note_off', note=note.note_pitch, velocity=0, time=beat_val))

        # Pista de Acompañamiento
        if self.back_track is True:
            self.add_backing_track(mid)
            print("Pista de acompañamiento agregada")

        # Guarda en ./midi_out/ si se proporciona un nombre de archivo
        if filename:
            filename = f"{folder}/{filename}"
            mid.save(filename)

        return

    def add_backing_track(self, mid):
        """
        Función auxiliar para melody_to_midi(). Agrega una pista de acompañamiento a un archivo MIDI multipista.
        La pista de acompañamiento es una escala o arpegio ascendente repetido basado en la tonalidad del programa.
        Entrada: Un objeto multitrack MidiFile
        Salida: El archivo MIDI con la pista de acompañamiento
        """
        ticks_per_beat = mid.ticks_per_beat
        backing_track = MidiTrack(name="Backing")
        mid.tracks.append(backing_track)
        length_of_background = (int(BEATS_P_MEASURE) * MEASURES_P_MELODY * 2)

        scale = SCALES[self.scale_signature][self.key_signature]
        if self.arp_or_scale:
            for beat in range(length_of_background):
                ar_pitch = NOTE_TO_MIDI[scale[0]]
                if (beat % 4) == 1:
                    ar_pitch = NOTE_TO_MIDI[scale[2]]
                elif (beat % 4) == 2:
                    ar_pitch = NOTE_TO_MIDI[scale[4]]
                elif (beat % 4) == 3:
                    ar_pitch = NOTE_TO_MIDI[scale[7]]
                backing_track.append(
                    Message('note_on', note=ar_pitch, velocity=42, time=0))
                ar_beat = 0.5 * ticks_per_beat
                ar_beat = int(ar_beat)
                backing_track.append(
                    Message('note_off', note=ar_pitch, velocity=0, time=ar_beat))
        else:
            step = 0
            for beat in range(length_of_background):
                ar_pitch = NOTE_TO_MIDI[scale[step]]
                backing_track.append(
                    Message('note_on', note=ar_pitch, velocity=42, time=0))
                ar_beat = 0.5 * ticks_per_beat
                ar_beat = int(ar_beat)
                backing_track.append(
                    Message('note_off', note=ar_pitch, velocity=0, time=ar_beat))
                step += 1
                if step >= 8:
                    step = 0

        return

    def generate_melody(self, input_mel, album):

        # Título de la melodía
        title = f"melody_{self.melody_counter}"
        self.melody_counter += 1

        # Nombre del archivo MIDI 
        midi_file = f"{title}.mid"

        # Crea una carpeta para guardar los archivos de la melodía si no existe
        folder = f"media/melodies/{album.id}/{album.generation_number}"

        if not os.path.exists(folder):
            os.makedirs(folder)

        # Convierte la melodía en un archivo MIDI
        self.melody_to_midi(input_mel, midi_file, folder)

        # Convierte el archivo MIDI en un archivo WAV y MP3
        midi = f"{folder}/{midi_file}"

        # Ruta del soundfont a utilizar 
        soundfont_path = "algorithm/Chorium/Chorium_fork.sf2"

        # Convierte el archivo MIDI en un archivo WAV y MP3
        mp3, final_duration = convert_midi_to_mp3(midi, soundfont_path)
        
        # Sube el archivo MP3 a Cloudinary
        melo = cloudinary.uploader.upload(mp3, resource_type="auto", folder=f"melodies/{album.id}/{album.generation_number}/")

        # Crea una instancia de GeneratedMelody
        mel = GeneratedMelody(
            title=title,
            # Guarda el archivo MP3 en Cloudinary
            mel=melo['url'],
            generation=album.generation_number,
            duration=final_duration,
        )

        # Guarda la melodía en la base de datos
        mel.save()
        album.melodies.add(mel)

# Clase Note
class Note:
    """
    La clase Note representa una 'nota' en teoría musical. Cada objeto Note tiene tres variables miembro
    note_pitch: int, el tono de la nota como un valor MIDI (0-127, 128 representa un silencio)
    beats: float, la duración de la nota [2.0 = negra, 1.0 = corchea, 0.5 = semicorchea, 0.25 = fusa]
    velocity: int, la cantidad de "fuerza" utilizada para tocar la nota. Esta es la dinámica de la nota [53 = MP, 64 = MF, 80 = F, 96 = FF]
    """

    def __init__(self, note_pitch=None, beats=None, velocity=None):
        """
        Inicializa un miembro de la clase Note. Puede ser inicializado con valores específicos o tener
        sus atributos asignados aleatoriamente al ser inicializado.
        note_pitch puede darse como str o int, se almacenará como int
        """

        if note_pitch is None:
            note_str = random.choice(NOTE_RANGE)
            # Asigna un valor a la nota si no se proporciona ninguno
            note_pitch = NOTE_TO_MIDI[note_str]
        else:
            if type(note_pitch) is str:
                if note_pitch not in NOTE_RANGE:
                    raise Exception(
                        "Error:", note_pitch, " fuera del rango de notas y no es un silencio")
                    # Asegura que un tono dado esté dentro del rango definido
                else:
                    note_pitch = NOTE_TO_MIDI[note_pitch]
            elif type(note_pitch) is int:
                if MIDI_TO_NOTE[note_pitch] not in NOTE_RANGE:
                    raise Exception(
                        "Error:", note_pitch, " fuera del rango de notas y no es un silencio")
            else:
                raise Exception("Error:", note_pitch,
                                " debe ser una cadena o un entero")

        if beats is None:
            # Asigna una longitud a la nota si no se proporciona ninguna
            beats = random.choice(BEAT_VALUES)
        elif beats not in BEAT_VALUES:
            raise Exception("Error: %f Número inválido de pulsos", beats)
            # Asegura que un pulso dado esté dentro del rango

        if velocity is None:
            velocity = random.choice(VELOCITY_RANGE)
        elif velocity < 0 or velocity > 127:
            raise Exception("Error: Velocidad fuera de límites. Rango 0-127")

        self.note_pitch = note_pitch
        self.beats = beats
        self.velocity = velocity
        return

    def pitch_shift(self, increment=1,  up=True):
        """
        Cambia el tono de la nota hacia arriba o hacia abajo según el incremento
        Entrada: increment: int, la cantidad de semitonos para cambiar el tono de la nota
        up: bool, Verdadero cambia el tono hacia arriba, Falso cambia el tono hacia abajo
        Salida: el note_pitch se cambia
        """
        if up:
            # Cambia el tono hacia arriba # incrementa los semitonos
            self.note_pitch += increment
        else:
            # Cambia el tono hacia abajo # incrementa los semitonos
            self.note_pitch -= increment
            pass
        return

    def __str__(self):
        """
        To string method for printing notes.
        """
        return "Pitch: " + MIDI_TO_NOTE[self.note_pitch] + " | Beats: " + str(self.beats) + " | Velocity: " + str(self.velocity)

# Clase Measure


class Measure:
    """
    La clase Measure representa una medida en notación musical. Cada objeto de medida tiene una variable miembro.
    measure_list: lista, la lista de objetos Note contenidos en la medida
    La cantidad de Notas que una Medida puede contener está determinada por BEATS_P_MEASURE
    """

    def __init__(self, measure_list=None):
        """
        Inicializa un objeto de la clase Measure. 
        Entrada: measure_list: lista, la lista de objetos Note contenidos en la medida
        Si measure_list es Nada, la Medida se poblará con Notas aleatorias.
        Salida: Objeto de la clase Measure
        """

        self.measure_list = []
        if measure_list is None:
            total_beats = 0.0
            while total_beats != BEATS_P_MEASURE:
                current_beat = random.choice(BEAT_VALUES)
                while total_beats + current_beat > BEATS_P_MEASURE:
                    current_beat = random.choice(BEAT_VALUES)
                new_note = Note(beats=current_beat)
                self.measure_list.append(new_note)
                total_beats += current_beat
            return
        else:
            total_beats = 0.0
            for note in measure_list:
                total_beats += note.beats
                if total_beats > BEATS_P_MEASURE:
                    raise Exception(
                        "Error: Número de pulsos en la lista dada mayor que ", BEATS_P_MEASURE, " ", total_beats)
                else:
                    self.measure_list.append(note)
            return

    def __str__(self):
        """
        To string method for Measure class. 
        """
        to_str = "Notes in Measure:\n"
        for m_note in self.measure_list:
            to_str += str(m_note) + "\n"
        return to_str

# Clase Melody


class Melody:
    """
    La clase Melody representa una melodía musical. Las melodías tienen dos variables miembro.
    key: str, la armadura de clave de la melodía
    melody_list = None, la lista de Medidas en la melodía.
    El número de medidas en una melodía está definido por MEASURES_P_MELODY.
    """

    def __init__(self, scale, key, melody_list=None, filename=None):
        """
        Inicializa un objeto de la clase Measure.
        Entrada: key: str, la armadura de clave de la melodía | melody_list: lista, la lista de Medidas en la melodía
        filename: str, el nombre de archivo para el archivo MIDI a abrir
        Si se proporciona un nombre de archivo, el MIDI se abrirá y se convertirá en un objeto Melody
        Salida: Objeto de la clase Melody
        """

        self.key = key
        self.scale = scale

        # Solo se puede dar un nombre de archivo o melody_list, no ambos
        if filename is not None and melody_list is not None:
            raise Exception(
                "Error: Solo se puede dar una melody_list o un nombre de archivo")

        # Si se proporciona un nombre de archivo, abre el archivo MIDI
        if filename:
            filename = "midi_out/" + filename
            mid_file = MidiFile(filename)
            self.melody_list = midi_to_melody(mid_file)
            return

        # elif melody_list no se proporciona, genera una nueva melodía
        elif melody_list is None:
            self.melody_list = new_melody(self.scale, self.key)

        # else verifica que la lista de melodía dada sea válida
        else:
            if len(melody_list) > MEASURES_P_MELODY:
                raise Exception("Error: Melodía más larga que ",
                                MEASURES_P_MELODY)
            else:
                self.melody_list = melody_list

        return

    def len(self):
        """
        Devuelve el número de medidas en el objeto Melody
        """
        return len(self.melody_list)

    def copy(self):
        """
        Devuelve un nuevo objeto Melody que es una copia del objeto de melodía actual
        Esta función es necesaria para las operaciones de cruzamiento
        """
        return Melody(self.scale, self.key, melody_list=self.melody_list)

    def cross_mel(self, mel2, change_first_half):
        """
        Función auxiliar para cx_music. Intercambia la mitad de las medidas de la melodía actual con las medidas de mel2.
        Entrada: self: Melody, la primera melodía | mel2: Melody, la segunda melodía
        change_first_half: bool, dicta si la primera o segunda mitad de las medidas debe ser intercambiada 
        (Verdadero para la primera mitad, Falso para la segunda)
        """
        if change_first_half: # Si se debe cambiar la primera mitad de las medidas de la melodía actual con las medidas de mel2 
            # Intercambia la primera mitad de la melodía por la primera mitad de mel2 
            end = MEASURES_P_MELODY // 2 
            i = 0 # Iterador 
            while i < end:
                self.melody_list[i] = mel2.melody_list[i]
                i += 1
            pass
        else:
            # Intercambia la segunda mitad de la melodía por la segunda mitad de mel2
            i = MEASURES_P_MELODY // 2
            while i < MEASURES_P_MELODY:
                self.melody_list[i] = mel2.melody_list[i]
                i += 1
            pass
        
        return

    def __str__(self):
        """
        To string method for melody class. Returns a string representation of a Melody.
        """
        to_str = "Melody:\n"
        for msr in self.melody_list:
            to_str += str(msr)
        return to_str


def shift_scale(scale, key):
    """
    Devuelve una lista de notas en una escala desplazada dos octavas hacia arriba
    Entrada: key: str, la armadura utilizada para obtener la escala del diccionario SCALES
    Salida: shifted_scale: lista, lista de 8 notas desplazadas dos octavas hacia arriba
    """
    scale = SCALES[scale][key]
    shifted_scale = []

    for ori_note in scale:
        num = int(ori_note[1]) + 2
        shifted_note = ori_note[0] + str(num)
        if len(ori_note) == 3:
            shifted_note += ori_note[2]
        shifted_scale.append(shifted_note)

    return shifted_scale


def calculate_pitch(prev_pitch, interval, ascend_or_descend):
    """
    Función auxiliar para get_new_pitch(). Devuelve un nuevo tono basado en el tono previo
    Entrada: prev_pitch: int, el tono anterior | interval: int, el intervalo para cambiar el nuevo tono | ascend_or_descend: int, dicta si el tono se desplaza hacia arriba o hacia abajo
    Salida: new_pitch: int, el tono de la nueva nota
    """
    upper_bound = 84 - interval
    lower_bound = 60 + interval
    new_pitch = 0

    if prev_pitch >= upper_bound:
        # Anula el valor de ascend_or_descend si estamos en el límite
        new_pitch = prev_pitch - interval
    elif prev_pitch <= lower_bound:
        # Anula el valor de ascend_or_descend si estamos en el límite
        new_pitch = prev_pitch + interval
    elif ascend_or_descend == 0:
        new_pitch = prev_pitch - interval
    else:
        new_pitch = prev_pitch - interval

    return new_pitch


def get_new_pitch(prev_pitch, ascend_or_descend, scale):
    """
    Función auxiliar para get_new_note_pitch(). Utiliza el tono anterior para dictar el tono de la nueva nota.
    Los tonos también pueden ser un silencio o un tono completamente nuevo en la escala, no asociado con el tono anterior.
    Entrada: prev_pitch: int, el valor del tono anterior | ascend_or_descend: int, dicta si el tono se desplaza hacia arriba o hacia abajo (0 = descend, 1 = ascend)
    scale: lista, los tonos disponibles en la escala actual
    Salida: new_pitch: int, el tono de la nueva nota
    """
    new_pitch = 0
    if prev_pitch == 128:
        # Si los 2 tonos anteriores son silencios, tono nuevo aleatorio
        option = 6
    else:
        # Si no, el tono anterior podría afectar al nuevo tono
        option = random.randint(0, 8)

    if option == 0:
        # repetir
        new_pitch = prev_pitch
    elif option == 1:
        # paso
        new_pitch = calculate_pitch(prev_pitch, 2, ascend_or_descend)

    elif option == 2:
        # tercera
        new_pitch = calculate_pitch(prev_pitch, 3, ascend_or_descend)

    elif option == 3:
        # saltar
        skip = random.randint(1, 4)
        new_pitch = calculate_pitch(prev_pitch, skip, ascend_or_descend)

    elif option == 4:
        # Octava
        new_pitch = calculate_pitch(prev_pitch, 12, ascend_or_descend)

    elif option == 5:
        # salto
        jump = random.randint(4, 14)
        new_pitch = calculate_pitch(prev_pitch, jump, ascend_or_descend)

    elif option == 6:
        # aleatorio
        pitch_str = random.choice(scale)
        new_pitch = NOTE_TO_MIDI[pitch_str]

    else:
        # silencio
        new_pitch = 128

    return new_pitch


def get_new_note_pitch(prev_pitch, ascend_or_descend, scale):
    """
    Función auxiliar para next_note(). Genera el tono de la siguiente nota considerando la nota anterior y ascend_or_descend.
    Verifica que el nuevo tono esté dentro de los límites de la clave de sol. 
    Entrada: prev_pitch: int, el valor del tono anterior | ascend_or_descend: int, dicta si el tono se desplaza hacia arriba o hacia abajo (0 = descend, 1 = ascend)
    scale: lista, los tonos disponibles en la escala actual
    Salida: new_pitch: int, el tono de la nueva nota
    """

    new_pitch = get_new_pitch(prev_pitch, ascend_or_descend, scale)
    while MIDI_TO_NOTE[new_pitch] not in NOTE_RANGE:
        new_pitch = get_new_pitch(prev_pitch, ascend_or_descend, scale)

    return new_pitch


def get_new_beat(prev_beats):
    """
    Función auxiliar para get_new_note_beat(). Devuelve un valor flotante para la duración de la nueva nota.
    Entrada: prev_beats: float, la duración de la nota anterior
    Salida: new_beat: float, la duración de la nueva nota
    """
    option = random.randint(0, 5)
    new_beat = 0.0
    if option < 1:
        # Repetir el valor de duración
        new_beat = prev_beats
    elif option >= 1 and option < 4:
        new_beat = random.choice([2.0, 1.0])
    else:
        new_beat = random.choice([.5, .25])

    return new_beat


def get_new_note_beat(prev_beats, measure_beats):
    """
    Función auxiliar para next_note(). Genera la duración de la nueva nota.
    Esta función asegura que el valor de duración de la nota encaje en la medida actual.
    Entrada: prev_beats: float, la duración de la nota anterior | measure_beats: int, suma actual de duraciones en la medida que se está generando
    Salida: new_beat: float, la duración de la nueva nota
    """
    new_beat = get_new_beat(prev_beats)

    while measure_beats + new_beat > BEATS_P_MEASURE:
        new_beat = get_new_beat(prev_beats)

    return new_beat


def get_new_note_velocity(prev_velocity, ascend_or_descend):
    """
    Función auxiliar para next_note(). Genera la velocidad de la nueva nota.
    Considera la dinámica de la nota anterior para determinar el volumen de la nueva nota.
    Entrada: prev_velocity: int, la dinámica de la nota anterior | ascend_or_descend: int, dicta si el volumen aumenta o disminuye (0 = disminuir, 1 = aumentar)
    Salida: new_velocity: int, la dinámica de la nueva nota
    """
    option = random.randint(0, 4)
    new_velocity = 0
    if option < 2:
        # Mantener la dinámica
        new_velocity = prev_velocity
    else:
        # Cambio de dinámica
        if prev_velocity == 96:
            # No se puede aumentar más
            new_velocity = 80
        elif prev_velocity == 53:
            # No se puede disminuir más
            new_velocity = 64
        elif ascend_or_descend == 0:
            if prev_velocity == 64:
                new_velocity = 53
            else:
                new_velocity = 64
        else:
            if prev_velocity == 64:
                new_velocity = 80
            else:
                new_velocity = 96

    return new_velocity


def next_note(prev, measure_beats, scale):
    """
    Función auxiliar para new_melody(). Genera la siguiente nota que se agregará a la note_list, basada en la nota anterior
    Entrada: prev: Note, el objeto Note anterior | measure_beats: int, suma actual de duraciones en la medida que se está generando
    scale: list, los tonos disponibles en la escala actual
    Salida: new_note_list: list, la lista que contiene los valores de la nueva nota donde new_note_list = [Note, Beats, Velocity]
    """
    new_note_list = [0, 0.0, 0]  # Nota, Duración, Dinámica

    ascend_or_descend = random.randint(0, 1)  # Ascender = 1, Descender = 0

    new_note_list[0] = get_new_note_pitch(
        prev.note_pitch, ascend_or_descend, scale)

    new_note_list[1] = get_new_note_beat(prev.beats, measure_beats)

    new_note_list[2] = get_new_note_velocity(prev.velocity, ascend_or_descend)

    return new_note_list


def new_melody(scale, key):
    """
    Función auxiliar para la clase Melody. Genera una melody_list completamente poblada
    Entrada: key: str, la armadura para la melodía
    Salida: melody_list: list, la melody_list interna poblada con MEASURES_P_MELODY cantidad de compases
    """
    note_list = []  # Contiene todas las notas generadas
    sum_beats = 0.0  # Suma total de duraciones
    max_beats = BEATS_P_MEASURE * MEASURES_P_MELODY * 1.0
    # Desplaza la escala al rango de la clave de sol
    scale = shift_scale(scale, key)
    note_index = 0
    new_note_list = [0, 0.0, 0]  # Nota, Duración, Dinámica
    measure_beats = 0.0  # Lleva el registro de la cantidad de duraciones en el compás actual

    while sum_beats < max_beats:

        if note_index == 0:
            # Caso inicial
            # Establece el tono inicial dentro de la escala
            new_note_list[0] = scale[random.randint(2, 7)]
            # Inicia la melodía con notas largas
            new_note_list[1] = random.choice([2.0, 1.0])
            new_note_list[2] = random.choice(
                [53, 96])  # Comienza suave o fuerte

        else:
            # Caso normal
            prev = note_list[note_index-1]
            if prev.note_pitch == 128 and len(note_list) > 2:
                # Si el tono anterior fue un silencio, usar el tono en note_index-2
                prev = note_list[note_index-2]

            # Llama a la función next_note
            new_note_list = next_note(prev, measure_beats, scale)

        note_list.append(
            Note(new_note_list[0], new_note_list[1], new_note_list[2]))
        sum_beats += new_note_list[1]
        measure_beats += new_note_list[1]
        if measure_beats == BEATS_P_MEASURE:
            measure_beats = 0.0
        note_index += 1
        new_note_list = [0, 0.0, 0]  # Nota, Duración, Dinámica

    # Llama a la función build_melody() para convertir la note_list en una melody_list
    return build_melody(note_list)


def midi_to_melody(mid_file):
    """
    Función auxiliar para la clase Melody init(). Toma el archivo MIDI dado y devuelve un objeto de la clase Melody
    Entrada: mid_file: MidiFile, el objeto de archivo MIDI
    Salida: melody_list: list, la melody_list interna poblada con MEASURES_P_MELODY cantidad de compases
    """
    tempo = 0
    key_signature = ""

    # Obtener los metadatos
    for message in mid_file:
        if message.is_meta:
            if message.type == 'key_signature':
                key_signature = message.key
            elif message.type == 'set_tempo':
                tempo = message.tempo
        else:
            break

    # Leer todas las notas
    note_list = []
    rest = False
    # Importar solo la pista principal, no la pista de acompañamiento
    melody_track = mid_file.tracks[0]
    new_note_list = [0, 0.0, 0]  # Nota, Duración, Dinámica
    new_note = True

    for message in melody_track:
        if message.is_meta:
            pass
        elif MIDI_TO_NOTE[message.note] not in NOTE_RANGE:
            pass
        else:
            if new_note:
                # Obtener los valores cuando se enciende la nota
                new_note_list[0] = message.note
                # Especialmente para la dinámica
                new_note_list[2] = message.velocity
                new_note = False
            if message.time != 0:
                if rest:
                    new_note_list[0] = "Rest"
                    rest = False

                val_duracion = message.time
                # val_duracion = nota.duración * ticks_por_compás
                # por lo que nota.duración = val_duracion / ticks_por_compás
                ticks_por_compás = mid_file.ticks_per_beat
                duración = val_duracion / ticks_por_compás

                new_note_list[1] = duración

                note_list.append(
                    Note(new_note_list[0], new_note_list[1], new_note_list[2]))

                new_note = True
            elif message.type == 'note_off':
                rest = True

    return build_melody(note_list)


def build_melody(note_list):
    """
    Función auxiliar para la clase Melody init(). Llamada por midi_to_melody() y new_melody().
    Toma una note_list dada y devuelve una melody_list poblada con MEASURES_P_MELODY cantidad de compases
    Entrada: note_list: list, lista de objetos de nota
    Salida: melody_list: list, la melody_list interna poblada con MEASURES_P_MELODY cantidad de compases
    """
    measure_list = []
    measure_beats = 0.0
    sum_beats = 0.0
    melody_list = []

    max_beats = BEATS_P_MEASURE * MEASURES_P_MELODY * 1.0
    for note in note_list:
        measure_beats += note.beats
        sum_beats += note.beats
        measure_list.append(note)
        if measure_beats == BEATS_P_MEASURE:
            melody_list.append(Measure(measure_list))
            measure_beats = 0.0
            measure_list = []

    if sum_beats > max_beats:
        raise Exception(
            "Error: Las duraciones en note_list exceden ", max_beats)
    else:
        return melody_list


def save_list_of_melodies(rep_obj, the_mel_list, group_name, mel_num):
    """
    Función auxiliar para save_best_melodies(). Utiliza el rep_obj dado para escribir las melodías en la lista dada en el disco.
    Devuelve el número actualizado de melodías (mel_num).
    Entrada: rep_obj: representación, la instancia del objeto de representación del programa | the_mel_list: list, la lista de melodías
    group_name: str, el nombre del grupo o lista | mel_num: int, el número de melodías escritas hasta ahora
    Salida: mel_num: int, el número actualizado de melodías escritas hasta ahora
    """
    folder = f"algorithm/midi_out"

    for melody in the_mel_list:
        filename = f"{group_name}_{str(mel_num)}.mid"
        rep_obj.melody_to_midi(melody, filename, folder)
        mel_num += 1
    return mel_num


def save_best_melodies(rep_obj, population):
    """
    Función auxiliar para run_genetic_algorithm(). Escribe las mejores melodías generadas por el programa en el directorio ./midi_out/
    Entrada: rep_obj: representación, la instancia del objeto de representación del programa | population: list, una población de DEAP que contiene la última generación de melodías
    hall_of_fame: deap.tools.support.ParetoFront, objeto hall_of_fame de DEAP que contiene melodías calificadas con 5/5 por el usuario
    Salida: No se devuelve nada. Los archivos MIDI se escriben en ./midi_out/
    """
    mel_num = 0
    mel_num = save_list_of_melodies(
        rep_obj, population, "population", mel_num)

    return

