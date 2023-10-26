from music21 import converter

def extract_midi_info(file_path):
    try:
        info_dict = {}

        # Load the MIDI file using music21
        midi_stream = converter.parse(file_path)

        # Extract key
        key = midi_stream.analyze("key")
        tonic = key.tonicPitchNameWithCase
        mode = key.mode
        pitch_with_alteration = tonic.replace('-', 'b')
        info_dict['key'] = f'{pitch_with_alteration} {mode}'

        # Extract tempo
        metronome_mark = midi_stream.metronomeMarkBoundaries()
        if metronome_mark:
            number = metronome_mark[0][2].number
            # referent = metronome_mark[0][2].referent.type
            # info_dict['tempo'] = f"{int(number)} {referent}"
            info_dict['tempo'] = f"{int(number)}"

        # Extract meter
        time_signature = midi_stream.getTimeSignatures()[0]
        info_dict['meter'] = f"{time_signature.numerator}/{time_signature.denominator}"

        # Extract duration (in minutes and seconds)
        duration_in_seconds = midi_stream.duration.quarterLength / number * 60
        #minutes = int(duration_in_seconds // 60)
        #seconds = int(duration_in_seconds % 60)
        info_dict['duration'] = str(duration_in_seconds)

        return info_dict

    except Exception as e:
        print(f"An error occurred while extracting MIDI information: {str(e)}")
