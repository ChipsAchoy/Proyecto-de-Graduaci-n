import pygame
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import MP3Info
import APIClient
import PluginInterface
import threading
import SamplerController
import MixController
#import PianoRollController

# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana
WIDTH, HEIGHT = 1200, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini DAW")

# Colores
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
LIGHT_GRAY = (220, 220, 220)
GREEN = (0, 255, 0)

# Fuentes
font = pygame.font.SysFont('Arial', 16)

# Tamaños de las secciones
RIBBON_HEIGHT = 40
RIBBON_HEIGHT_EXTENDED = 80
TRACK_HEIGHT = 80
CONTROL_HEIGHT = 50



# Rectángulos para los botones del ribbon
archivo_rect = pygame.Rect(20, 10, 80, 30)
interfaz_rect = pygame.Rect(120, 10, 80, 30)
plugins_rect = pygame.Rect(220, 10, 80, 30)

# Estado para el menú desplegable de "Archivo"
archivo_menu_open = False

# Rectángulos para las opciones "Importar" y "Exportar"
importar_rect = pygame.Rect(20, RIBBON_HEIGHT, 80, 30)
exportar_rect = pygame.Rect(20, RIBBON_HEIGHT + 30, 80, 30)

# Crear rectángulos para los botones
play_rects = []
pause_rects = []
stop_rects = []
edit_rects = []
volume_sliders = []
general_play_rect = pygame.Rect(WIDTH - 160, HEIGHT - CONTROL_HEIGHT, 140, CONTROL_HEIGHT)


# Almacenar las pistas dinámicamente
tracks = []  # Comenzamos con 3 pistas
bpms = [] 
compass_structures = []
mp3_objects = []
volume_values = []  # Valores iniciales de volumen (una por cada pista)
samples = []
current_compass_struct = []
saved_structure = []
editables = []
file_path = None

# Crear botón para agregar nueva pista
add_track_button_rect = None
compose_button_rect = None

# Variable global para almacenar la IP de la interfaz
interface_ip = None


# Crear botones para el ribbon (Archivo, Interfaz, Plugins)
def draw_ribbon():
    pygame.draw.rect(window, GRAY, (0, 0, WIDTH, RIBBON_HEIGHT))
    archivo_text = font.render('Archivo', True, BLACK)
    interfaz_text = font.render('Interfaz', True, BLACK)
    plugins_text = font.render('Plugins', True, BLACK)
    
    window.blit(archivo_text, (archivo_rect.x, archivo_rect.y))
    window.blit(interfaz_text, (interfaz_rect.x, interfaz_rect.y))
    window.blit(plugins_text, (plugins_rect.x, plugins_rect.y))

# Mostrar el menú desplegable para "Archivo"
def draw_archivo_menu():
    pygame.draw.rect(window, LIGHT_GRAY, (20, RIBBON_HEIGHT, 80, 60))  # Fondo del menú
    importar_text = font.render('Importar', True, BLACK)
    exportar_text = font.render('Exportar', True, BLACK)
    
    window.blit(importar_text, (importar_rect.x + 10, importar_rect.y + 5))
    window.blit(exportar_text, (exportar_rect.x + 10, exportar_rect.y + 5))


def draw_track_controls(y_offset, track_num):
    pygame.draw.rect(window, GRAY, (0, y_offset, WIDTH, TRACK_HEIGHT))
    
    # Agregar el número de pista
    track_label = font.render(f'Pista {track_num}', True, BLACK)
    window.blit(track_label, (10, y_offset + 10))  # Posicionar el número de pista

    # Dibujar los botones de reproducción
    play_button = font.render('Reproducir', True, BLACK)
    pause_button = font.render('Pausar', True, BLACK)
    stop_button = font.render('Detener', True, BLACK)
    #track_length = font.render(f'Longitud: 00:00', True, BLACK)
    
    # Definir los rectángulos para los botones de reproducción
    play_rect = pygame.Rect(120, y_offset + 10, 100, 30)
    pause_rect = pygame.Rect(220, y_offset + 10, 100, 30)
    stop_rect = pygame.Rect(320, y_offset + 10, 100, 30)
    
    # Dibujar los botones de reproducción
    window.blit(play_button, (play_rect.x, play_rect.y))
    window.blit(pause_button, (pause_rect.x, pause_rect.y))
    window.blit(stop_button, (stop_rect.x, stop_rect.y))
    #window.blit(track_length, (420, y_offset + 10))

    # Guardar los rectángulos si es la primera vez que los creamos
    if len(play_rects) <= track_num - 1:
        play_rects.append(play_rect)
        pause_rects.append(pause_rect)
        stop_rects.append(stop_rect)

    # Dibujar el slider de volumen
    pygame.draw.line(window, BLACK, (550, y_offset + 25), (750, y_offset + 25), 3)
    slider_position = 550 + int((volume_values[track_num - 1] / 200) * 200)
    pygame.draw.circle(window, GREEN, (slider_position, y_offset + 25), 10)
    volume_text = font.render(f'Volumen: {volume_values[track_num - 1]}', True, BLACK)
    window.blit(volume_text, (770, y_offset + 10))
    
    if len(volume_sliders) <= track_num - 1:
        volume_sliders.append(pygame.Rect(550, y_offset + 15, 200, 20))

    # Si editable es True, agregar un botón para editar la pista
    """ 
    if editable:
        edit_button = font.render('Editar', True, BLACK)
        edit_rect = pygame.Rect(880, y_offset + 10, 100, 30)  # Posición y tamaño del botón de edición
        window.blit(edit_button, (edit_rect.x, edit_rect.y))

        # Guardar el rectángulo del botón de edición si es la primera vez
        edit_rects.append(edit_rect)

    else:
        edit_rects.append(None)

    """

def draw_add_track_button():
    global add_track_button_rect, compose_button_rect
    y_offset = RIBBON_HEIGHT_EXTENDED + len(tracks) * (TRACK_HEIGHT + 10) + 20

    # Botón "Grabar nueva pista"
    add_track_button_rect = pygame.Rect(20, y_offset, 160, 40)
    pygame.draw.rect(window, BLUE, add_track_button_rect)
    add_track_text = font.render('Grabar nueva pista', True, WHITE)
    window.blit(add_track_text, (add_track_button_rect.x + 10, add_track_button_rect.y + 10))

    # Botón "Componer nueva pista"
    compose_button_rect = pygame.Rect(200, y_offset, 160, 40)
    pygame.draw.rect(window, BLUE, compose_button_rect)
    compose_text = font.render('Componer nueva pista', True, WHITE)
    window.blit(compose_text, (compose_button_rect.x + 10, compose_button_rect.y + 10))
    
    return compose_button_rect


# Crear botón para reproducir todas las pistas
def draw_general_play_button():
    pygame.draw.rect(window, BLUE, general_play_rect)
    play_all_button = font.render('Reproducir Todo', True, WHITE)
    window.blit(play_all_button, (WIDTH - 140, HEIGHT - CONTROL_HEIGHT + 15))



def open_file_dialog():
    global mp3_objects, bpms, compass_structures, volume_values, samples, editables
    # Inicializar tkinter y ocultar la ventana principal
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana de tkinter

    # Abrir el cuadro de diálogo de selección de archivos
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo de audio",
        filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg"), ("Todos los archivos", "*.*")]
    )
    
    if file_path:
        print(f"Archivo seleccionado: {file_path}")
        mp3_info = MP3Info.MP3Info(file_path)
        mp3_objects += [mp3_info]
        tracks.append(len(tracks) + 1)  # Añadir una nueva pista
        volume_values.append(100)
        bpms += [0]
        compass_structures += [None]
        samples += [None]
        editables += [False]
        print("Agregar nueva pista")


        
        # Aquí podrías cargar o procesar el archivo seleccionado según lo requieras
    else:
        print("No se seleccionó ningún archivo")


def play_all():
    to_play = []
    for mp3 in mp3_objects:
        to_play += [mp3.get_file_path()]

    if to_play != []:
        MixController.combine_files_with_volumes(to_play, volume_values, "output.mp3")
        print("Reproduciendo todas las pistas")
        MP3Info.MP3Info("output.mp3").play()
    


def start_recording(effect):
    print("Iniciando grabación...")
    APIClient.send_start(effect)
    ########################################
    threading.Thread(target=play_all).start()

        
    

def stop_recording(name):

    global mp3_objects, bpms, compass_structures, volume_values, samples, editables, tracks

    print("Grabación detenida.")
    buffer = APIClient.send_stop()
    APIClient.save_as_mp3(name, buffer, 48000)
    mp3_info = MP3Info.MP3Info(name)
    mp3_objects += [mp3_info]
    bpms += [0] 
    compass_structures += [None]
    tracks.append(len(tracks) + 1)  # Añadir una nueva pista
    volume_values.append(100)
    samples+= [None]
    editables += [False]
    print("Agregar nueva pista")



def open_recording_window():
    recording_window = tk.Tk()
    recording_window.title("Grabación de nueva pista")
    
    # Ajustar el tamaño de la ventana (por ejemplo, 400x300 píxeles)
    recording_window.geometry("400x300")
    
    # Etiqueta para el nombre del archivo
    name_label = tk.Label(recording_window, text="Nombre del archivo:")
    name_label.pack()
    
    # Entrada para el nombre del archivo
    name_entry = tk.Entry(recording_window)
    name_entry.pack()

    # Etiqueta para la selección de efecto
    effect_label = tk.Label(recording_window, text="Selecciona un efecto:")
    effect_label.pack(pady=10)
    
    # Lista desplegable con los efectos
    effects = ["noeffect", "delay", "reverb", "distortion"]
    selected_effect = tk.StringVar(recording_window)
    selected_effect.set(effects[0])  # Valor predeterminado

    effect_menu = tk.OptionMenu(recording_window, selected_effect, *effects)
    effect_menu.pack(pady=10)
    
    # Botón para empezar a grabar
    record_button = tk.Button(recording_window, text="Grabar", command=lambda:threading.Thread(start_recording(selected_effect.get())).start(), width=20, height=2)
    record_button.pack(pady=10)

    # Botón para detener la grabación
    stop_button = tk.Button(recording_window, text="Detener", command=lambda: threading.Thread(stop_recording(name_entry.get())).start(), width=20, height=2)
    stop_button.pack(pady=10)

    recording_window.mainloop()




# Función para abrir la ventana de Tkinter para ingresar la IP
def open_interface_window():
    def save_ip():
        global interface_ip
        interface_ip = ip_entry.get()  # Obtener la IP ingresada por el usuario
        print(f"IP de la interfaz guardada: {interface_ip}")
        interface_window.destroy()  # Cerrar la ventana una vez guardada la IP
    
    # Crear la ventana de Tkinter
    interface_window = tk.Tk()
    interface_window.title("Configuración de Interfaz")

    interface_window.geometry("300x150")

    # Etiqueta y campo de entrada para la IP
    ip_label = tk.Label(interface_window, text="Ingrese la IP de la interfaz:")
    ip_label.pack(pady=10)
    
    ip_entry = tk.Entry(interface_window)
    ip_entry.pack(pady=10)

    # Botón para guardar la IP
    save_button = tk.Button(interface_window, text="Guardar", command=save_ip)
    save_button.pack(pady=10)

    interface_window.mainloop()

def open_plugin_window():
    global mp3_objects, bpms, compass_structures, volume_values, samples, editables, sample
    # Crear ventana de Tkinter
    plugin_window = tk.Tk()
    plugin_window.title("Configuración del Plugin")

    # Ajustar tamaño de la ventana
    plugin_window.geometry("400x600")

    # Etiqueta y entrada para la IP del plugin
    ip_label = tk.Label(plugin_window, text="IP del Plugin:")
    ip_label.pack(pady=10)
    ip_entry = tk.Entry(plugin_window, width=30)
    ip_entry.pack(pady=10)

    # Etiqueta y entrada para el número de pista
    track_label = tk.Label(plugin_window, text="Número de pista compuesta a enviar:")
    track_label.pack(pady=10)
    track_entry = tk.Entry(plugin_window, width=30)
    track_entry.pack(pady=10)

    # Etiqueta y entrada para los parámetros
    params_label = tk.Label(plugin_window, text="Parámetros:")
    params_label.pack(pady=10)
    params_entry = tk.Entry(plugin_window, width=30)
    params_entry.pack(pady=10)

    # Etiqueta y entrada para el nombre del MP3 resultante
    mp3_label = tk.Label(plugin_window, text="Nombre del archivo MP3 a recibir:")
    mp3_label.pack(pady=10)
    mp3_entry = tk.Entry(plugin_window, width=30)
    mp3_entry.pack(pady=10)

    sample = None

    # Función para abrir un selector de archivo y guardar el sample seleccionado
    def select_sample():
        global sample
        file_path = filedialog.askopenfilename(
            title="Seleccionar Sample",
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg"), ("All Files", "*.*")]
        )
        if file_path:
            sample = file_path  # Asigna el archivo seleccionado a la variable sample
            sample_label.config(text=f"Sample seleccionado: {file_path.split('/')[-1]}")  # Muestra solo el nombre del archivo

    # Botón para abrir el selector de archivos para el sample
    select_sample_button = tk.Button(plugin_window, text="Seleccionar Sample", command=select_sample)
    select_sample_button.pack(pady=10)

    # Etiqueta para mostrar el archivo seleccionado
    sample_label = tk.Label(plugin_window, text="Sample no seleccionado")
    sample_label.pack(pady=10)


    def generateNewTrackFromPlugin():

        #prueba = [{'start_beat': 1, 'duration': 'negra', 'notes': ['E2']}, {'start_beat': 2, 'duration': 'negra', 'notes': ['D3']}, {'start_beat': 3, 'duration': 'blanca', 'notes': ['A2']}, {'start_beat': 5, 'duration': 'redonda', 'notes': ['F3']}]

        PluginInterface.send_to_plugin(ip_entry.get(), compass_structures[int(track_entry.get())-1],
                                                                        params_entry.get(), mp3_entry.get(), sample, 
                                                                        bpms[int(track_entry.get()) -1])
        # Crear la instancia MP3Info y añadir una nueva pista
        mp3_info = MP3Info.MP3Info(mp3_entry.get())
        mp3_objects.append(mp3_info)
        tracks.append(len(tracks) + 1)  # Añadir una nueva pista
        volume_values.append(100)
        bpms.append(bpms[int(track_entry.get()) -1])
        compass_structures.append(PluginInterface.current_acomp)
        samples.append(sample)
        editables.append(False)
        print("Nueva pista añadida")
        


    # Botón para enviar la configuración del plugin
    send_button = tk.Button(plugin_window, text="Enviar al plugin", width=20, height=2,
                            command=generateNewTrackFromPlugin)
    send_button.pack(pady=20)

    

    plugin_window.mainloop()

"""

EDITANDO LAS IMPORTACIONES


"""
def open_composition_window(index, new):
    global mp3_objects, bpms, compass_structures, volume_values, samples, editables, tracks, file_path, current_compass_struct, saved_structure

    current_compass_struct = []
    
    compose_window = tk.Tk()
    compose_window.title("Componer nueva pista")
    
    # Ajustar el tamaño de la ventana
    compose_window.geometry("500x400")
    
    # Selector de BPM
    bpm_label = tk.Label(compose_window, text="BPM:")
    bpm_label.pack()
    bpm_entry = tk.Entry(compose_window)
    bpm_entry.pack()

    name_label = tk.Label(compose_window, text="Nombre de la pista (MP3):")
    name_label.pack()
    name_entry = tk.Entry(compose_window)
    name_entry.pack()
    
    # Selector de sample (File selector)
    def select_sample():
        global file_path
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:  # Si se selecciona un archivo
            sample_label.config(text=f"Sample seleccionado: {file_path.split('/')[-1]}")  # Mostrar el nombre del archivo
    
    sample_label = tk.Label(compose_window, text="Sample:")
    sample_label.pack()
    sample_button = tk.Button(compose_window, text="Seleccionar sample", command=lambda: threading.Thread(target=select_sample).start())
    sample_button.pack()

    if not new:
        sample_label.config(text=f"Sample seleccionado: {samples[index]}")  # Mostrar el nombre del archivo
        bpm_entry.insert(0, str(bpms[index]))  # Corregir el orden de los argumentos

    # Función para abrir la ventana del piano roll
    def open_piano_roll(index_p, new_p):
        global current_compass_struct

        # Crear la ventana principal de composición
        root = tk.Tk()
        root.title("Piano Roll Beat por Beat")

        # Ajustar el tamaño de la ventana
        root.geometry("1200x800")

        # Crear un contenedor scrolleable para los beats
        canvas = tk.Canvas(root)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Crear un marco dentro del canvas
        main_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=main_frame, anchor="nw")

        # Hacer la ventana scrolleable
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        main_frame.bind("<Configure>", on_frame_configure)

        # Botón para agregar un nuevo beat
        def add_beat():
            global current_compass_struct

            # Crear un marco para cada nuevo beat
            beat_frame = tk.Frame(main_frame)
            beat_frame.pack(fill="x", pady=5)

            # Campo de entrada para el beat de inicio
            start_beat_label = tk.Label(beat_frame, text="Beat de inicio:")
            start_beat_label.pack(side="top", padx=10)
            start_beat_entry = tk.Entry(beat_frame)
            start_beat_entry.pack(side="top", padx=10)

            # Selector de duración (solo una duración por beat)
            duration_menu = ttk.Combobox(beat_frame)
            duration_menu['values'] = ['semicorchea', 'corchea', 'negra', 'blanca', 'redonda']
            duration_menu.set('negra')  # Valor por defecto
            duration_menu.pack(side="top", padx=10)

            # Agregar notas iniciales al beat
            beat_info = {
                'start_beat': len(current_compass_struct) + 1,  # Por defecto, agregar al final
                'duration': duration_menu,
                'notes': [],
                'start_beat_entry': start_beat_entry  # Referencia para obtener el valor más tarde
            }
            current_compass_struct.append(beat_info)

            # Botón para agregar más notas dentro del mismo beat (vertical)
            add_note_button = tk.Button(beat_frame, text="Agregar Nota", command=lambda: add_note(beat_info, beat_frame))
            add_note_button.pack(side="top", pady=5)

        # Función para agregar una nota dentro de un beat
        def add_note(beat_info, beat_frame):
            global current_compass_struct
            # Crear un frame para las notas dentro del beat (vertical)
            note_frame = tk.Frame(beat_frame)
            note_frame.pack(side="top", padx=10, pady=2)

            # Selector de nota con sostenidos
            note_menu = ttk.Combobox(note_frame, width=10)
            note_menu['values'] = [
                f"{note}{octave}" for octave in range(2, 7) for note in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            ]
            note_menu.pack(side="top", padx=10)

            # Aquí se añade la nota seleccionada al beat_info cuando se guarda
            beat_info['notes'].append(note_menu)  # Guardar la referencia al combobox de notas

        # Función para guardar la composición
        def save_composition():
            global current_compass_struct, saved_structure
            saved_structure = []
            
            for beat in current_compass_struct:
                # Obtener el valor actual de duración del combobox
                duration_value = beat['duration'].get()  # Captura directamente el valor
                # Obtener las notas actuales de cada beat
                notes_value = [note_menu.get() for note_menu in beat['notes']]  # Captura todas las notas
                # Obtener el beat de inicio introducido por el usuario
                start_beat_value = beat['start_beat_entry'].get() or beat['start_beat']

                # Crear el objeto de beat a guardar
                beat_data = {
                    'start_beat': int(start_beat_value),  # Convertir a int
                    'duration': duration_value,  # Guardar duración correcta
                    'notes': notes_value  # Guardar notas
                }
                
                saved_structure.append(beat_data)

            messagebox.showinfo("Guardado", "Composición guardada correctamente.")
            print(saved_structure)  # Imprimir la estructura guardada

        def load_notes(beat_info, beat, beat_frame):
            # Agregar las notas al beat, con un pequeño retardo para cada una
            for note in beat['notes']:
                add_note(beat_info, beat_frame)  # Crear un combobox para cada nota
                beat_info['notes'][-1].set(note)  # Establecer el valor de la nota

        # Función para importar una estructura
        def import_structure():
            global current_compass_struct
            try:
                for beat in current_compass_struct:
                    # Crear un marco para cada nuevo beat
                    beat_frame = tk.Frame(main_frame)
                    beat_frame.pack(fill="x", pady=5)

                    # Selector de duración
                    duration_menu = ttk.Combobox(beat_frame)
                    duration_menu['values'] = ['semicorchea', 'corchea', 'negra', 'blanca', 'redonda']
                    duration_menu.set(beat['duration'])  # Valor del beat importado
                    duration_menu.pack(side="top", padx=10)

                    # Campo de entrada para el beat de inicio
                    start_beat_entry = tk.Entry(beat_frame)
                    start_beat_entry.insert(0, beat['start_beat'])  # Valor del beat importado
                    start_beat_entry.pack(side="top", padx=10)

                    # Agregar notas iniciales al beat
                    beat_info = {'start_beat': beat['start_beat'], 'duration': duration_menu, 'notes': [], 'start_beat_entry': start_beat_entry}
                    current_compass_struct.append(beat_info)

                    # Cargar las notas de manera incremental
                    root.after(100, lambda beat_info=beat_info, beat=beat: load_notes(beat_info, beat, beat_frame))

            except Exception:
                messagebox.showerror("Error", "Mal formato")


        # Botón para agregar un nuevo beat
        add_beat_button = tk.Button(root, text="Agregar Beat", command=add_beat)
        add_beat_button.pack(pady=10)

        # Botón para guardar la composición
        save_button = tk.Button(root, text="Guardar Composición", command=lambda:threading.Thread(save_composition()).start())
        save_button.pack(pady=10)

        if not new_p:
            current_compass_struct = compass_structures[index_p]
            print(current_compass_struct)
            if not isinstance(current_compass_struct, list):
                messagebox.showerror("Error", "Estructura de compases no válida.")
                return
            import_structure()

        root.mainloop()

    # Botón para abrir el piano roll
    piano_roll_button = tk.Button(compose_window, text="Ir al Piano Roll",command=lambda: open_piano_roll(index, new))
    piano_roll_button.pack(pady=10)

    # Botón para salvar cambios
    def save_changes():
        global mp3_objects, bpms, compass_structures, volume_values, samples, editables, sample, tracks

        if new:
            SamplerController.generateAudioFromSampleStructure(file_path, saved_structure, name_entry.get(), int(bpm_entry.get()))
            mp3_objects.append(MP3Info.MP3Info(name_entry.get()))
            bpms.append(bpm_entry.get())
            samples.append(file_path)
            compass_structures.append(saved_structure)
            volume_values.append(100)
            editables.append(False)
            tracks.append(len(tracks)+1)

        else:
            SamplerController.generateAudioFromSampleStructure(file_path, saved_structure, name_entry.get(), int(bpm_entry.get()))
            mp3_objects[index] = MP3Info.MP3Info(name_entry.get())
            bpms[index] = bpm_entry.get()
            samples[index] = file_path
            compass_structures[index] = saved_structure

        compose_window.destroy()

    save_button = tk.Button(compose_window, text="Salvar cambios", command=save_changes)
    save_button.pack(pady=10)

    compose_window.mainloop()


# Bucle principal
while True:
    window.fill(WHITE)
    
    # Dibujar el ribbon
    draw_ribbon()
    
    # Dibujar el menú de Archivo si está abierto
    if archivo_menu_open:
        draw_archivo_menu()

    # Dibujar controles de las pistas
    for i, track in enumerate(tracks):
        y_offset = RIBBON_HEIGHT_EXTENDED + i * (TRACK_HEIGHT + 10)
        draw_track_controls(y_offset, track)
    
    # Dibujar el botón de "Agregar nueva pista" y "Componer nueva pista"
    draw_add_track_button()
    
    # Dibujar botón para reproducir todas las pistas
    draw_general_play_button()

    # Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Si se hace clic en el botón de "Exportar"
            if archivo_menu_open and exportar_rect.collidepoint(mouse_pos):
                print("Exportar")
            
            # Revisar si se hace clic en los botones de control de cada pista
            for idx, play_rect in enumerate(play_rects):
                if play_rect.collidepoint(mouse_pos):
                    print(f"Reproduciendo pista {idx}")
                    mp3_objects[idx].play()
            for idx, pause_rect in enumerate(pause_rects):
                if pause_rect.collidepoint(mouse_pos):
                    print(f"Pausando pista {idx}")
                    mp3_objects[idx].pause()
            for idx, stop_rect in enumerate(stop_rects):
                if stop_rect.collidepoint(mouse_pos):
                    print(f"Deteniendo pista {idx}")
                    mp3_objects[idx].stop()

            """ 
            for idx, edit_rect in enumerate(edit_rects):
                if edit_rect != None:
                    if edit_rect.collidepoint(mouse_pos):
                        print(f"Editando pista {idx}")
                        threading.Thread(target=lambda: open_composition_window(idx, False)).start()
                        break
            """

                    

            # Ajustar el volumen de la pista correspondiente al slider
            for idx, slider in enumerate(volume_sliders):
                if slider.collidepoint(mouse_pos):
                    # Obtener la posición del ratón dentro del slider
                    slider_x = mouse_pos[0] - slider.x
                    # Limitar el valor del volumen entre 0 y 200
                    volume_value = max(0, min(200, int((slider_x / slider.width) * 200)))
                    volume_values[idx] = volume_value
                    # Ajustar el volumen del mp3
                    mp3_objects[idx].set_volume(volume_value)  # Asumiendo que set_volume acepta valores entre 0 y 1
                    print(f"Volumen de la pista {idx} ajustado a {volume_value}")
                    
            # Si se hace clic en el botón de "Importar" del menú de archivo
            if archivo_menu_open and importar_rect.collidepoint(mouse_pos):
                threading.Thread(target=open_file_dialog).start()

            # Clic en el botón para agregar una nueva pista
            if add_track_button_rect.collidepoint(mouse_pos):
                threading.Thread(target=open_recording_window).start()

            # Clic en el botón para componer una nueva pista
            if compose_button_rect.collidepoint(mouse_pos):
                print("Componiendo nueva pista")
                threading.Thread(target=lambda: open_composition_window(None, True)).start()
                

            # Si se hace clic en el botón de reproducir todas las pistas
            if general_play_rect.collidepoint(mouse_pos):
                threading.Thread(target=play_all).start()

            # Si se hace clic en el botón de "Interfaz"
            if interfaz_rect.collidepoint(mouse_pos):
                # Abrir la ventana de configuración de IP
                threading.Thread(target=open_interface_window).start()
                

            # Si se hace clic en el botón de "Plguin"
            if plugins_rect.collidepoint(mouse_pos):
                # Abrir la ventana de configuración de plugin
                threading.Thread(target=open_plugin_window).start()

            # Si se hace clic en el botón de "Archivo"
            if archivo_rect.collidepoint(mouse_pos):
                archivo_menu_open = not archivo_menu_open  # Alternar el menú

            

    # Actualizar la pantalla
    pygame.display.flip()
