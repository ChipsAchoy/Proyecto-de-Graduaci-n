import requests
from io import BytesIO
from pydub import AudioSegment
import SamplerController
import json

current_acomp = None


def send_to_plugin(api_url, audio_structure, parameters, name, sample, bpm):
    global current_acomp
    # Convertir los parámetros en una lista separada por ';'
    parameter_list = parameters.split(';')
    
    # Empaquetar los datos en el formato adecuado
    data = {
        'audio': audio_structure,
        'parameters': parameter_list  # Enviar como lista
    }
    
    # Enviar el post request a la API
    response = requests.post(api_url, json=data)
    
    # Verificar si la respuesta fue exitosa
    if response.status_code == 200:
        # Recibir el buffer de audio de salida y convertirlo a mp3
        audio_acomp = response.content

        print("Recibido de AI",audio_acomp)

        # Decodificar el byte string a una cadena
        json_string = audio_acomp.decode('utf-8')

        # Convertir la cadena JSON a un diccionario o lista de diccionarios
        data = json.loads(json_string)

        SamplerController.generateAudioFromSampleStructure(sample, data, name, bpm)
        
        print("Audio generado para pista de composicion")

        current_acomp = data
    else:
        print(f"Error en la API: {response.status_code}")
        current_acomp = None


# Ejemplo de uso

"""
api_url = "http://plugin-ip/api/process_audio"
audio_structure = [
    {'start_beat': 1, 'duration': 'negra', 'notes': ['A4', 'C#5', 'E5']},
    {'start_beat': 3, 'duration': 'blanca', 'notes': ['D4']},
    {'start_beat': 4, 'duration': 'corchea', 'notes': ['E4']}
]
parameters = "parametros_modificados_por_el_usuario"
send_to_plugin(api_url, audio_structure, parameters)

"""
