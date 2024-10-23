import librosa
import soundfile as sf
import numpy as np

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

def generate_percussion_sequence(audio, sr, bpm, compass):
    """Genera una secuencia de percusión a partir de una estructura de compás con silencios incluidos."""
    final_audio = np.array([])
    last_beat_end = 0
    
    for entry in compass:
        start_beat = entry['start_beat']  # En qué beat del compás empieza el sonido de percusión
        duration = entry['duration']      # Duración de la figura musical
        
        # Calcular la duración del silencio entre el último beat procesado y el nuevo
        silence_duration = (start_beat - last_beat_end) * (60 / bpm)
        
        # Generar silencio si hay un espacio entre beats
        if silence_duration > 0:
            silence_audio = np.zeros(int(silence_duration * sr))
            final_audio = np.concatenate([final_audio, silence_audio])
        
        # Ajustar el sample a la figura musical correspondiente
        figure_audio = sample_to_musical_figure(audio, sr, bpm, duration)
        final_audio = np.concatenate([final_audio, figure_audio])
        
        # Actualizar el último beat procesado
        last_beat_end = start_beat + get_duration(bpm, duration) * bpm / 60
    
    return final_audio



def save_sample(sample, sr, output_path):
    sf.write(output_path, sample, sr)

    
"""
# Ejemplo de uso
file_path = "hihat.mp3"  # El archivo de sonido del instrumento de percusión
output_path = "percussion_sequence_with_silence.mp3"
bpm = 120

# Cargar el archivo de percusión
audio, sr = load_audio(file_path)

# Estructura de compás para la secuencia de percusión
compass_structure = [
    {'start_beat': 1, 'duration': 'negra'},    # Sonido en el primer beat
    # Beat 2 está vacío (silencio)
    {'start_beat': 3, 'duration': 'corchea'},  # Sonido en el tercer beat
    {'start_beat': 4, 'duration': 'negra'},    # Sonido en el cuarto beat
]

# Generar la secuencia de percusión basada en la estructura de compás
final_audio = generate_percussion_sequence(audio, sr, bpm, compass_structure)

# Guardar el resultado final
save_sample(final_audio, sr, output_path)

print(f"Secuencia de percusión guardada en '{output_path}'")

"""
