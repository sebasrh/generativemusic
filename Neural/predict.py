""" This module generates notes for a midi file using the
    trained neural network """
import pickle
import numpy
import os
import cloudinary
from .midi_utils import convert_midi_to_mp3
from .midi_info import extract_midi_info
from music21 import instrument, note, stream, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import BatchNormalization as BatchNorm
from keras.layers import Activation

from rnn.models import GeneratedMusicAlbum, GeneratedMusic


def generatemusic(number_of_notes, number_of_compositions):
    """ Generate a piano midi file """
    try:
        # load the notes used to train the model
        with open('Neural/notes', 'rb') as filepath:
            notes = pickle.load(filepath)

        if not notes:
            raise ValueError(
                "No training data (notes) available. Cannot generate music.")

        # Get all pitch names
        pitchnames = sorted(set(item for item in notes))

        # Get all pitch names
        n_vocab = len(set(notes))

        network_input, normalized_input = prepare_sequences(
            notes, pitchnames, n_vocab)

        model = create_network(normalized_input, n_vocab)

        print(number_of_compositions)

        album = GeneratedMusicAlbum.objects.create()
        album.epoch = 136

        i = 1

        while i <= number_of_compositions:
            prediction_output = generate_notes(
                model, network_input, pitchnames, n_vocab, number_of_notes)

            midi_stream = create_midi(prediction_output)

            generated_music = save_midi(midi_stream, album.id)

            album.generated_music.add(generated_music)

            i += 1

        album.save()

        print("Melodías generadas", "Contador eliminado")
        print("")

        # Delete the counter file
        os.remove("Neural/counter")

    except Exception as e:
        print(f"An error occurred while generating music: {str(e)}")


def prepare_sequences(notes, pitchnames, n_vocab):
    """ Prepare the sequences used by the Neural Network """
    # map between notes and integers and back
    note_to_int = dict((note, number)
                       for number, note in enumerate(pitchnames))

    sequence_length = 100
    network_input = []
    output = []
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    # reshape the input into a format compatible with LSTM layers
    normalized_input = numpy.reshape(
        network_input, (n_patterns, sequence_length, 1))
    # normalize input
    normalized_input = normalized_input / float(n_vocab)

    return (network_input, normalized_input)


def create_network(network_input, n_vocab):
    """ create the structure of the neural network """
    model = Sequential()
    model.add(LSTM(
        512,
        input_shape=(network_input.shape[1], network_input.shape[2]),
        recurrent_dropout=0.3,
        return_sequences=True
    ))
    model.add(LSTM(512, return_sequences=True, recurrent_dropout=0.3,))
    model.add(LSTM(512))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    # Load the weights to each node
    model.load_weights(
        'Neural/weights-improvement-136-0.8655-bigger.hdf5')
    return model


def generate_notes(model, network_input, pitchnames, n_vocab, number_of_notes):
    """ Generate notes from the neural network based on a sequence of notes """
    # pick a random sequence from the input as a starting point for the prediction
    start = numpy.random.randint(0, len(network_input)-1)

    int_to_note = dict((number, note)
                       for number, note in enumerate(pitchnames))

    pattern = network_input[start]
    prediction_output = []

    # generate x notes
    total_notes = number_of_notes
    print(total_notes)
    for _ in range(total_notes):
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)

        prediction = model.predict(prediction_input, verbose=0)

        index = numpy.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)

        pattern.append(index)
        pattern = pattern[1:len(pattern)]

    return prediction_output


def create_midi(prediction_output):
    """ convert the output from the prediction to notes and create a midi file
        from the notes """
    offset = 0
    output_notes = []

    # create note and chord objects based on the values generated by the model
    for pattern in prediction_output:
        # pattern is a chord
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                # new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        # pattern is a note
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            # new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        # increase offset each iteration so that notes do not stack
        offset += 0.5

    # Create a Part object and assign it to the Electric Guitar instrument
    piano_part = stream.Part()
    piano_part.insert(instrument.Piano())

    # Add the notes to the Part
    for element in output_notes:
        piano_part.append(element)

    # Create the Stream with the Part and convert it to a MIDI file
    midi_stream = stream.Stream()
    midi_stream.append(piano_part)

    return midi_stream


def save_midi(midi_stream, album):
    try:
        counter_file = "Neural/counter"

        # Create or load the counter
        if not os.path.exists(counter_file):
            with open(counter_file, 'wb') as f:
                counter = 0
                pickle.dump(counter, f)
        else:
            with open(counter_file, 'rb') as f:
                counter = int(pickle.load(f))

        # Save the updated counter
        with open(counter_file, 'wb') as f:
            pickle.dump(counter, f)

        # Build file paths
        file_name = f'melody {counter}'
        # Increment the counter
        counter += 1
        file_path = file_name.replace(" ", "_")
        file_midi = f'media/midi_files/{album}/{file_path}.mid'

        # Create the folder if it doesn't exist
        folder_album = f'media/midi_files/{album}'
        if not os.path.exists(folder_album):
            os.makedirs(folder_album)

        # save midi to file
        midi_stream.write('midi', fp=file_midi)

        # SoundFont path
        soundfont_path = "Chorium/Chorium_fork.sf2"

        # Convert midi to wav and mp3
        mp3 = convert_midi_to_mp3(file_midi, soundfont_path)

        # Extract MIDI info
        midi_info = extract_midi_info(file_midi)

        # Upload the generated file to the cloudinary server
        melo = cloudinary.uploader.upload(
            mp3, resource_type="auto", folder=f"melodies_rnn/{album}")

        # Upload the generated file to the database
        new_audio = GeneratedMusic(
            title=file_name,
            key=midi_info['key'],
            tempo=midi_info['tempo'],
            meter=midi_info['meter'],
            duration=midi_info['duration'],
            mel=melo['url'],
        )

        new_audio.save()

        

        print("Melodía generada", "midi:", file_midi, "mp3:", mp3, "eliminados")
        print("")

        # Delete the generated files 
        os.remove(file_midi)
        os.remove(mp3)

        return new_audio

    except Exception as e:
        print(
            f"An error occurred while saving MIDI or updating the database: {str(e)}")
