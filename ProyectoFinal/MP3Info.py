import librosa
import pygame

class MP3Info:
    def __init__(self, file_path):
        """Inicializa la clase con la ubicación del archivo MP3, calcula la duración y configura el volumen."""
        self.file_path = file_path  # Ubicación del archivo MP3
        self.duration, self.sr = self._get_duration()  # Duración del MP3 en segundos
        self.volume = 100  # Volumen inicializado en 100
        pygame.mixer.init()  # Inicializa el módulo de sonido de pygame
        self.dictComposition = None
        self.sample = None
        self.is_paused = False  # Bandera para saber si está en pausa
    
    def _get_duration(self):
        """Calcula y devuelve la duración del archivo MP3."""
        try:
            audio, sr = librosa.load(self.file_path, sr=None)
            duration = librosa.get_duration(y=audio, sr=sr)
            return duration, sr
        except Exception as e:
            print(f"Error cargando el archivo MP3: {e}")
            return None, None
    
    def set_volume(self, new_volume):
        """Cambia el volumen del MP3 a un nuevo valor."""
        if 0 <= new_volume <= 200:
            self.volume = new_volume
            pygame.mixer.music.set_volume(self.volume / 50)  # Establece el volumen en pygame
        else:
            raise ValueError("El volumen debe estar entre 0 y 200.")

    def set_dict_composition(self, dictComposition):
        self.dictComposition = dictComposition

    def get_dict_composition(self):
        return self.dictComposition
    
    def get_file_path(self):
        return self.file_path

    def set_sample(self, sample):
        self.sample = sample
    
    def play(self):
        """Reproduce el archivo MP3 desde el principio o reanuda si está en pausa."""
        if not self.is_paused:  # Si no está en pausa, lo reproduce desde el principio
            pygame.mixer.music.load(self.file_path)
            pygame.mixer.music.set_volume(self.volume / 100)
            pygame.mixer.music.play()
        else:  # Si está en pausa, reanuda la reproducción
            pygame.mixer.music.unpause()
            self.is_paused = False
    
    def pause(self):
        """Pausa la reproducción del archivo MP3."""
        pygame.mixer.music.pause()
        self.is_paused = True
    
    def stop(self):
        """Detiene la reproducción del archivo MP3."""
        pygame.mixer.music.stop()
        self.is_paused = False



"""
# Ejemplo de uso
file_path = "la440.mp3"
mp3_info = MP3Info(file_path)

# Imprimir información inicial
info = mp3_info.get_info()
print(f"Información del archivo MP3: {info}")

# Reproducir el archivo MP3
mp3_info.play()

# Cambiar el volumen después de iniciar la reproducción
mp3_info.set_volume(80)

# Pausar el archivo MP3 después de unos segundos (puedes hacer esto en un momento adecuado en tu aplicación)
mp3_info.pause()

# Reanudar la reproducción
mp3_info.play()

# Detener la reproducción
mp3_info.stop()

"""
