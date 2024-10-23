import librosa

# Diccionario de notas y sus equivalentes en semitonos (con respecto a A4 = 440 Hz)
note_to_semitone = {
    'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1,
    'A': 0, 'A#': 1, 'B': 2
}

# Función para convertir una nota en notación C4, C#4, D4, etc., a semitonos relativos a A4
def note_to_semitones(note):
    note_part = note[:-1]
    octave = int(note[-1])
    semitone_diff = note_to_semitone[note_part] + (octave - 4) * 12
    return semitone_diff

# Escalas mayores y menores (semitonos desde la tónica)
scales = {
    "C Major": [0, 2, 4, 5, 7, 9, 11],
    "G Major": [0, 2, 4, 5, 7, 9, 11],
    "D Major": [0, 2, 4, 6, 7, 9, 11],
    "A Major": [0, 2, 4, 6, 7, 9, 11],
    "E Major": [0, 2, 4, 6, 7, 9, 11],
    "F Major": [0, 2, 3, 5, 7, 8, 10],
    "B Major": [0, 2, 4, 6, 7, 9, 11],
    "C Minor": [0, 2, 3, 5, 7, 8, 10],
    "G Minor": [0, 2, 3, 5, 7, 8, 10],
    "D Minor": [0, 2, 3, 5, 7, 8, 10],
    "A Minor": [0, 2, 3, 5, 7, 8, 10],
    "E Minor": [0, 2, 3, 5, 7, 8, 10],
    "B Minor": [0, 2, 3, 5, 7, 8, 10]
}

def extract_notes_from_compass(compass_structure):
    """Extrae todas las notas de la estructura de compases."""
    notes = []
    for item in compass_structure:
        notes.extend(item['notes'] if isinstance(item['notes'], list) else [item['notes']])
    return notes

def notes_to_semitones(notes):
    """Convierte una lista de notas en sus correspondientes semitonos."""
    return [note_to_semitones(note) for note in notes]

def detect_key(notes_semitones):
    """Detecta la tonalidad comparando las notas con las escalas y tomando en cuenta la tónica."""
    unique_semitones = set([note % 12 for note in notes_semitones])
    
    best_match = None
    best_match_score = 0

    # Comparamos las notas con cada escala, considerando la tónica
    for key, scale_intervals in scales.items():
        tonic = note_to_semitones(key.split()[0] + '4') % 12  # Obtener semitono de la tónica de la escala
        scale_semitones = [(tonic + interval) % 12 for interval in scale_intervals]  # Mover la escala a la tónica
        match_score = len(unique_semitones.intersection(scale_semitones))
        
        if match_score > best_match_score:
            best_match_score = match_score
            best_match = key
    
    return best_match

# Ejemplo de estructura de compases
compass_structure = [
    {'start_beat': 1, 'duration': 'negra', 'notes': ['A4', 'C#5', 'E5']},  # Acorde en el primer beat
    {'start_beat': 2, 'duration': 'blanca', 'notes': ['D4']},              # Nota individual en el segundo beat
    {'start_beat': 3, 'duration': 'redonda', 'notes': ['F#4', 'A4']},      # Acorde en el tercer beat
    {'start_beat': 4, 'duration': 'corchea', 'notes': ['E4', 'G#5']}       # Nota individual en el cuarto beat
]

# Extraer todas las notas de los compases
notes = extract_notes_from_compass(compass_structure)

# Convertir las notas a semitonos
semitones = notes_to_semitones(notes)

# Detectar la tonalidad
detected_key = detect_key(semitones)
print(f"La tonalidad detectada es: {detected_key}")
