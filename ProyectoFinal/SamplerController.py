import librosa
import soundfile as sf
import numpy as np

# Diccionario de notas y sus equivalentes en semitonos (con respecto a A4 = 440 Hz)
note_to_semitone = {
    'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1,
    'A': 0, 'A#': 1, 'B': 2
}

def note_to_semitones(note):
    """Convierte una nota en notación C3, C#3, D3, etc., a semitonos relativos a A4."""
    note_part = note[:-1]
    octave = int(note[-1])
    semitone_diff = note_to_semitone[note_part] + (octave - 4) * 12
    return semitone_diff

def load_audio(file_path):
    """Carga un archivo de audio en formato mp3."""
    audio, sr = librosa.load(file_path, sr=None)
    return audio, sr

def get_duration(bpm, figure):
    """Calcula la duración de las figuras musicales en segundos para un BPM dado."""
    beats_per_second = bpm / 60
    if figure == "negra":
        return 1 / beats_per_second
    elif figure == "blanca":
        return 2 / beats_per_second
    elif figure == "redonda":
        return 4 / beats_per_second
    elif figure == "corchea":
        return 0.5 / beats_per_second
    elif figure == "semicorchea":
        return 0.25 / beats_per_second
    else:
        raise ValueError(f"Figura musical '{figure}' no reconocida")

def normalize_audio(audio):
    """Normaliza el volumen del audio."""
    return librosa.util.normalize(audio)

def sample_to_musical_figure(audio, sr, bpm, figure, min_duration_sec=0.1):
    """Ajusta el sample a una figura musical específica manteniendo las propiedades del sonido."""
    duration_sec = get_duration(bpm, figure)
    original_duration = librosa.get_duration(y=audio, sr=sr)
    
    time_stretch_factor = original_duration / duration_sec
    
    if duration_sec < min_duration_sec:
        duration_sec = min_duration_sec
        time_stretch_factor = original_duration / duration_sec
    
    stretched_audio = librosa.effects.time_stretch(y=audio, rate=time_stretch_factor)
    
    return normalize_audio(stretched_audio)

def estimate_base_note(audio, sr):
    """Estima la nota base (frecuencia fundamental) del audio."""
    f0, voiced_flag, voiced_probs = librosa.pyin(audio, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    f0 = f0[voiced_flag]
    
    if len(f0) > 0:
        f0_mean = f0.mean()
        note = librosa.hz_to_note(f0_mean)
        return note
    return None

def change_pitch_to_note(audio, sr, base_note, target_note):
    """Cambia el pitch del audio a una nueva nota."""
    base_semitones = note_to_semitones(base_note)
    target_semitones = note_to_semitones(target_note)
    
    semitone_shift = target_semitones - base_semitones
    shifted_audio = librosa.effects.pitch_shift(y=audio, sr=sr, n_steps=semitone_shift)
    
    return normalize_audio(shifted_audio)

def create_chord(audio, sr, base_note, chord_notes):
    """Crea un acorde tocando múltiples notas simultáneamente."""
    chord_audio = np.zeros_like(audio)
    
    for note in chord_notes:
        shifted_audio = change_pitch_to_note(audio, sr, base_note, note)
        chord_audio += shifted_audio
    
    return normalize_audio(chord_audio)

def generate_compass_structure(audio, sr, base_note, bpm, compass):
    """Genera una secuencia de compases y acordes a partir de una estructura, incluyendo silencios."""
    final_audio = np.array([])
    last_beat_end = 0  # Último beat procesado


    print(bpm)
    print(compass)
    
    for entry in compass:
        start_beat = int(entry['start_beat'])  # En qué beat del compás empieza la nota
        duration = entry['duration']      # Duración de la figura musical
        notes = entry['notes']            # Puede ser una sola nota o un acorde (lista de notas)
        bpm = int(bpm)

        # Calcular la duración del silencio entre el último beat procesado y el nuevo
        silence_duration = (start_beat - last_beat_end) * (60 / bpm)
        
        # Generar silencio si hay un espacio entre beats
        if silence_duration > 0:
            silence_audio = np.zeros(int(silence_duration * sr))
            final_audio = np.concatenate([final_audio, silence_audio])

        # Crear la figura musical con las notas o el acorde correspondiente
        if isinstance(notes, list):  # Si es un acorde
            chord_audio = create_chord(audio, sr, base_note, notes)
            figure_audio = sample_to_musical_figure(chord_audio, sr, bpm, duration)
        else:  # Si es una sola nota
            pitched_audio = change_pitch_to_note(audio, sr, base_note, notes)
            figure_audio = sample_to_musical_figure(pitched_audio, sr, bpm, duration)
        
        # Agregar la figura musical al audio final
        final_audio = np.concatenate([final_audio, figure_audio])
        
        # Actualizar el último beat procesado
        last_beat_end = start_beat + get_duration(bpm, duration) * bpm / 60
    
    return final_audio

def save_sample(sample, sr, output_path):
    """Guarda el audio generado en formato mp3."""
    sf.write(output_path, sample, sr)



def generateAudioFromSampleStructure(file_path, compass_structure, output_path, bpm):

    
    audio, sr = load_audio(file_path)

    # Estimar la nota base del audio
    base_note = estimate_base_note(audio, sr)
    if base_note:
        print(f"Nota base estimada: {base_note}")
    else:
        print("No se pudo estimar una nota base válida.")
        base_note = 'A4'  # Nota por defecto
    
    """
    # Estructura de compás: cada entrada tiene 'start_beat', 'duration', y 'notes' (acorde o nota individual)
    compass_structure = [
        {'start_beat': 1, 'duration': 'negra', 'notes': ['A3', 'A4','C#5', 'E5']},  # Acorde en el primer beat
        # Beat 2 está vacío (silencio)
        {'start_beat': 3, 'duration': 'blanca', 'notes': ['D4']},              # Nota individual en el tercer beat
        {'start_beat': 4, 'duration': 'corchea', 'notes': 'E4'},               # Nota individual en el cuarto beat
    ]
    """
    # Generar la secuencia basada en la estructura de compases, incluyendo silencios
    final_audio = generate_compass_structure(audio, sr, base_note, bpm, compass_structure)

    # Guardar el resultado final
    save_sample(final_audio, sr, output_path)


"""
# Ejemplo de uso
file_path = "la440.mp3"
output_path = "melodia_con_silencios.mp3"
bpm = 90



print(f"Melodía con acordes, compases y silencios guardada en '{output_path}'")
"""