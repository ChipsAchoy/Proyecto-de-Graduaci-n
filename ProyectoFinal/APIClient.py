import requests
import struct
import wave
import numpy as np
from pydub import AudioSegment

# Configuración de la API
API_URL = 'http://192.168.0.21:9876'

def send_start(effect):
    """Envía una solicitud HTTP para iniciar la grabación con un efecto específico."""
    try:
        response = requests.post(f'{API_URL}/start', json={'effect': effect})
        if response.status_code == 200:
            print(f"Grabación iniciada con efecto: {effect}")
        else:
            print(f"Error al iniciar la grabación: {response.text}")
    except Exception as e:
        print(f"Error al enviar solicitud de inicio: {e}")

def send_stop():
    """Envía una solicitud HTTP para detener la grabación y recibir el buffer de audio."""
    try:
        response = requests.post(f'{API_URL}/stop', stream=True)
        if response.status_code == 200:
            print("Grabación detenida, recibiendo buffer de audio...")
            return response.content  # Recibe el buffer de audio
        else:
            print(f"Error al detener la grabación: {response.text}")
    except Exception as e:
        print(f"Error al enviar solicitud de detener: {e}")
    return None

def save_as_mp3(filename, buffer, sample_rate):
    """Guarda el buffer como un archivo MP3 usando pydub."""
    try:
        # Convertir el buffer a un array numpy con dtype float32
        audio_data = np.frombuffer(buffer, dtype=np.float32)
        
        # Asegurarse de que los valores estén en el rango [-1.0, 1.0] (opcional, en caso de que aún se vean fuera de rango)
        audio_data = np.clip(audio_data, -1.0, 1.0)

        # Convertir los valores a bytes para que Pydub pueda manejarlos
        audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()

        # Crear el objeto AudioSegment a partir de los bytes
        audio_segment = AudioSegment(
            data=audio_bytes,
            sample_width=2,  # 2 bytes para int16
            frame_rate=sample_rate,
            channels=1
        )
        # Guardar el archivo en formato MP3
        audio_segment.export(filename, format='mp3')
        print(f"Archivo MP3 guardado como {filename}")
    except Exception as e:
        print(f"Error al guardar MP3: {e}")


"""
def main():
    while True:
        command = input("Ingresa 'start' para iniciar la grabación o 'stop' para detenerla: ").strip().lower()

        if command == "start":
            effect = input("Elige el efecto (noeffect, reverb, delay, distortion, chorus): ").strip().lower()
            send_start(effect)

        elif command == "stop":
            audio_buffer = send_stop()
            if audio_buffer:
                sample_rate = 44100  # Define la frecuencia de muestreo utilizada
                save_as_mp3('output.mp3', audio_buffer, sample_rate)

        elif command == "exit":
            print("Saliendo...")
            break

        else:
            print("Comando no reconocido.")

if __name__ == "__main__":
    main()
"""
