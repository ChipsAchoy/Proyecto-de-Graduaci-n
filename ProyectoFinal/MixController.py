import librosa
import soundfile as sf
import numpy as np

def load_audio(file_path):
    """Carga un archivo de audio (mp3 o wav) y lo devuelve junto con la tasa de muestreo."""
    audio, sr = librosa.load(file_path, sr=None)
    return audio, sr

def adjust_volume(audio, volume_percentage):
    """Ajusta el volumen del audio en función del porcentaje dado."""
    if volume_percentage < 0:
        volume_percentage = 0
    elif volume_percentage > 200:
        volume_percentage = 200
    # Normalizamos el volumen a un rango de 0 a 2 (siendo 100% el volumen original)
    return audio * (volume_percentage / 100)

def pad_to_match_length(audios):
    """Iguala la longitud de los audios mediante padding (relleno de ceros) para combinarlos."""
    max_length = max([len(audio) for audio in audios])
    padded_audios = [np.pad(audio, (0, max_length - len(audio)), mode='constant') for audio in audios]
    return padded_audios

def combine_audios(audio_list):
    """Combina una lista de audios (matrices numpy) en un solo audio sumando los valores."""
    combined_audio = np.sum(np.array(audio_list), axis=0)
    return librosa.util.normalize(combined_audio)

def save_audio(output_path, audio, sr):
    """Guarda el audio resultante en formato mp3."""
    sf.write(output_path, audio, sr)

def combine_files_with_volumes(file_paths, volumes, output_path):
    """Combina múltiples archivos de audio, ajustando sus volúmenes respectivos."""
    audios = []
    sample_rate = None
    
    # Cargar y ajustar el volumen de cada archivo
    for i, file_path in enumerate(file_paths):
        audio, sr = load_audio(file_path)
        if sample_rate is None:
            sample_rate = sr
        elif sample_rate != sr:
            raise ValueError(f"Los archivos de audio deben tener la misma tasa de muestreo. El archivo {file_path} tiene una tasa diferente.")
        
        # Ajustar el volumen en base al valor proporcionado
        volume_adjusted_audio = adjust_volume(audio, volumes[i])
        audios.append(volume_adjusted_audio)
    
    # Asegurarnos de que todos los audios tengan la misma longitud
    padded_audios = pad_to_match_length(audios)
    
    # Combinar los audios
    combined_audio = combine_audios(padded_audios)
    
    # Guardar el resultado final
    save_audio(output_path, combined_audio, sample_rate)
    print(f"Archivo combinado guardado en '{output_path}'")

# Ejemplo de uso
"""
file_paths = ["audio1.mp3", "audio2.wav", "audio3.mp3"]  # Archivos de entrada
volumes = [100, 150, 75]  # Volumen de cada archivo: 100% para el primero, 150% para el segundo, 75% para el tercero
output_path = "audio_combinado.mp3"

combine_files_with_volumes(file_paths, volumes, output_path)
"""
