from midi2audio import FluidSynth
from pydub import AudioSegment
import os

def convert_midi_to_wav_mp3( file_midi, soundfont_path):

    # Build file paths
    file_wav = file_midi.replace(".mid", ".wav")
    file_mp3 = file_midi.replace(".mid", ".mp3")

    # Initialize FluidSynth
    fs = FluidSynth(soundfont_path)

    # Convert MIDI to WAV
    fs.midi_to_audio(file_midi, file_wav)

    # Load the WAV file
    audio = AudioSegment.from_wav(file_wav)

    # Adjust the duration (remove the last 2 seconds)
    adjusted_audio = audio[:-2000]  # Assuming each second is 1000 milliseconds

    # Adjust the volume (add 10 dB)
    adjusted_audio = adjusted_audio + 10

    # Export to MP3
    adjusted_audio.export(file_mp3, format="mp3")

    # Calculate and store the final duration
    final_duration = len(adjusted_audio) / 1000.0  # Convert milliseconds to seconds

    # Delete the WAV file
    os.remove(file_wav)

    # Return the file paths and the final duration
    return file_wav, file_mp3, final_duration