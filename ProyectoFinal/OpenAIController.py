import openai
import json
from flask import Flask, request, send_file
from io import BytesIO
from pydub import AudioSegment

app = Flask(__name__)


# Configura tu API key de OpenAI


def generate_accompaniment(melody_json, instrument, feelings):
    # Definir el prompt
    prompt = (
        f"Quiero que compongas un acompañamiento, de la misma cantidad de beats maximos, es decir, puedes meter beat intermedios,"
        f"melódico/armónico para la melodía {json.dumps(melody_json)}, que sea para el instrumento '{instrument}', "
        f"que transmita '{feelings}', y que me retornes esta misma estructura de JSON. (solo responde con el JSON, nada mas). "
        f"Responde con un formato igual al de la entrada (start_beat, duration y notes UNICAMENTE)"
    )
    
    # Llamar a la API de OpenAI usando ChatCompletion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "Eres un asistente musical experto."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    # Extraer y parsear el acompañamiento en formato JSON desde la respuesta
    accompaniment_json = response['choices'][0]['message']['content'].strip()
    
    try:
        accompaniment = json.loads(accompaniment_json)
        return accompaniment
    except json.JSONDecodeError:
        return f"Error al decodificar el JSON: {accompaniment_json}"


@app.route('/api/process_audio', methods=['POST'])
def process_audio():
    # Obtener el contenido del POST request
    data = request.get_json()
    audio_structure = data.get('audio')
    parameter_list = data.get('parameters')  # Los parámetros ya llegan como una lista
    
    # Enviar el audio de vuelta al cliente
    return generate_accompaniment(audio_structure, parameter_list[0], parameter_list[1])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



"""
# Ejemplo de estructura de compases
compass_structure = [
    {'start_beat': 1, 'duration': 'negra', 'notes': ['A4', 'C#5', 'E5']},
    {'start_beat': 2, 'duration': 'blanca', 'notes': ['D4']},
    {'start_beat': 3, 'duration': 'redonda', 'notes': ['F#4', 'A4']},
    {'start_beat': 4, 'duration': 'corchea', 'notes': 'E4'},
]

# Llamada a la función
accompaniment = generate_accompaniment(compass_structure, "piano", "felicidad y serenidad")
print(accompaniment)
"""
