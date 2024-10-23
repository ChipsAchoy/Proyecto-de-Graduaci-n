import socket
import struct
import wave
import numpy as np
from pydub import AudioSegment
from pydub.playback import play

# Configuración del socket
HOST = 'localhost'
PORT = 12345

def send_signal(sock, signal):
    """Envía una señal al servidor."""
    sock.sendall(signal.encode('utf-8'))

def receive_buffer(sock, chunk_size=1024):
    """Recibe el buffer de audio del servidor."""
    buffer = bytearray()
    while True:
        chunk = sock.recv(chunk_size)
        if not chunk:
            break
        buffer.extend(chunk)
    return buffer

def save_as_wav(filename, buffer, sample_rate):
    """Guarda el buffer como un archivo WAV."""
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # Tamaño del sample en bytes (2 bytes para 16-bit)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(buffer)

def save_as_mp3(filename, buffer, sample_rate):
    """Guarda el buffer como un archivo MP3 usando pydub."""
    # Convertir el buffer a un array numpy
    audio_data = np.frombuffer(buffer, dtype=np.int16)
    audio_segment = AudioSegment(
        data=audio_data.tobytes(),
        sample_width=2,
        frame_rate=sample_rate,
        channels=1
    )
    audio_segment.export(filename, format='mp3')

def main():
    # Crear el socket y conectarse al servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Enviar señal para iniciar grabación con efecto
        effect = "reverb"  # Cambiar al efecto deseado o "noeffect"
        send_signal(s, f"start:{effect}")

        # Esperar la grabación y la señal para detenerla
        input("Presiona ENTER para detener la grabación...")
        send_signal(s, "stop")

        # Recibir el buffer de audio
        print("Recibiendo buffer de audio...")
        audio_buffer = receive_buffer(s)

        # Seleccionar el formato para guardar el archivo
        format_choice = input("¿Qué formato quieres para el archivo? (wav/mp3): ").strip().lower()
        filename = "output"

        # Guardar el archivo según el formato elegido
        if format_choice == 'wav':
            save_as_wav(filename + ".wav", audio_buffer, SAMPLE_RATE)
        elif format_choice == 'mp3':
            save_as_mp3(filename + ".mp3", audio_buffer, SAMPLE_RATE)
        else:
            print("Formato no soportado")

        print(f"Archivo guardado como {filename}.{format_choice}")

if __name__ == "__main__":
    main()