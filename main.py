import threading
from AudioTranscriber import AudioTranscriber
import customtkinter as ctk
import AudioRecorder 
import queue
import time
import sys
import TranscriberModels
import subprocess
import urllib.request
import urllib.error
import json

# Carga de la API Key desde keys.py (ignorado en Git) o variables de entorno
try:
    from keys import GEMINI_API_KEY
except ImportError:
    import os
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "TU_GEMINI_API_KEY_AQUI")

# Variables de control inteligente de tráfico (Optimizado al límite de 12s gratuito)
last_transcript_len = 0
is_fetching = False
last_fetch_time = 0

def write_in_textbox(textbox, text):
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)

def update_transcript_UI(transcriber, textbox):
    transcript_string = transcriber.get_transcript()
    write_in_textbox(textbox, transcript_string)
    textbox.after(300, update_transcript_UI, transcriber, textbox)

def fetch_gemini_suggestion(transcript_text, ai_textbox):
    if not transcript_text.strip():
        return
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        # Contexto cambiado a conversaciones casuales y gramaticalmente impecables
        prompt = (
            "Eres un compañero de estudio IA nativo en inglés, con un estilo de comunicación como Gemini: "
            "auténtico, directo, amigable, empático y con un toque de ingenio. Tu objetivo es ayudar al usuario "
            "(You) a responder de forma natural en conversaciones cotidianas.\n\n"
            
            "Analiza el historial provisto abajo, detecta la última intervención de la otra persona (Speaker) "
            "y genera una respuesta sugerida para mí (You).\n\n"
            
            "REGLAS ESTRICTAS DE RESPUESTA:\n"
            "1. Si el diálogo es en inglés, responde estrictamente en un inglés natural, correcto y adaptado a un nivel B1 inicial "
            "(oraciones claras, fluidas y sin estructuras exageradamente complejas).\n"
            "2. Si la conversación es en español, responde en español de forma directa, sin preámbulos, resúmenes ni recapitulaciones.\n"
            "3. Si el contexto del diálogo menciona gramática o vocabulario específico (como 'white lies', 'conditionals' o 'reported speech'), "
            "prioriza el uso natural de esos elementos en la respuesta sugerida.\n"
            "4. Sé extremadamente breve (máximo 2 o 3 oraciones cortas) para mantener el ritmo dinámico y scannable del diálogo.\n\n"
            
            f"HISTORIAL ACTUAL DE LA CONVERSACIÓN:\n{transcript_text}"
        )
        body = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            suggestion = res_data['candidates'][0]['content']['parts'][0]['text']
            ai_textbox.after(0, lambda t=suggestion: write_in_textbox(ai_textbox, t))
            
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            error_msg = f"Google API Error: {error_data['error']['message']}"
        except:
            error_msg = f"HTTP Error {e.code}: {e.reason}"
        ai_textbox.after(0, lambda m=error_msg: write_in_textbox(ai_textbox, m))
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        ai_textbox.after(0, lambda m=error_msg: write_in_textbox(ai_textbox, m))

def force_ai_refresh(transcriber, ai_textbox):
    """Fuerza una petición manual protegiendo el plan gratuito contra spam de clics"""
    global is_fetching, last_fetch_time
    current_transcript = transcriber.get_transcript()
    current_time = time.time()
    time_passed = current_time - last_fetch_time
    
    if not current_transcript.strip():
        write_in_textbox(ai_textbox, "No hay texto suficiente para consultar.")
        return
        
    if time_passed < 12:
        seconds_left = int(12 - time_passed)
        write_in_textbox(ai_textbox, f"¡Freno de seguridad! Espera {seconds_left}s para no bloquear tu cuenta gratuita.")
        return
        
    if not is_fetching:
        is_fetching = True
        last_fetch_time = current_time
        write_in_textbox(ai_textbox, "Consultando a Gemini manualmente...")
        
        def run():
            global is_fetching
            try:
                fetch_gemini_suggestion(current_transcript, ai_textbox)
            finally:
                is_fetching = False
                
        threading.Thread(target=run, daemon=True).start()

def check_for_ai_updates(transcriber, ai_textbox, root):
    global last_transcript_len, is_fetching, last_fetch_time
    current_transcript = transcriber.get_transcript()
    current_time = time.time()
    
    lines = [line.strip() for line in current_transcript.split('\n') if line.strip()]
    last_line_is_speaker = lines[-1].startswith("Speaker:") if lines else False
    
    if len(current_transcript) > last_transcript_len and not is_fetching and last_line_is_speaker:
        if (current_time - last_fetch_time) >= 12:
            last_transcript_len = len(current_transcript)
            last_fetch_time = current_time
            is_fetching = True
            
            def run():
                global is_fetching
                try:
                    fetch_gemini_suggestion(current_transcript, ai_textbox)
                finally:
                    is_fetching = False
                    
            threading.Thread(target=run, daemon=True).start()
        
    root.after(1500, check_for_ai_updates, transcriber, ai_textbox, root)

def clear_context(transcriber, speaker_queue, mic_queue, ai_textbox):
    global last_transcript_len, last_fetch_time
    transcriber.clear_transcript_data()
    write_in_textbox(ai_textbox, "Esperando nueva conversación...")
    last_transcript_len = 0
    last_fetch_time = 0

    with speaker_queue.mutex:
        speaker_queue.queue.clear()
    with mic_queue.mutex:
        mic_queue.queue.clear()

def create_ui_components(root, transcriber, speaker_queue, mic_queue):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    # Nombre personalizado de la ventana
    root.title("sahurin AI")

    # Icono asignado desde tu archivo local
    try:
        root.iconbitmap("sahursin.ico")
    except Exception:
        pass

    root.geometry("1100x600")

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    
    main_frame = ctk.CTkFrame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=0)

    # Panel Izquierdo
    transcript_textbox = ctk.CTkTextbox(
        main_frame, 
        font=("Arial", 18), 
        text_color='#FFFCF2', 
        wrap="word"
    )
    transcript_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Panel Derecho
    ai_textbox = ctk.CTkTextbox(
        main_frame, 
        font=("Arial", 18), 
        text_color='#64B5F6', 
        wrap="word"
    )
    ai_textbox.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    write_in_textbox(ai_textbox, "Esperando a que hable la otra persona (Speaker)...")

    # Botón Izquierdo: Limpiar
    clear_button = ctk.CTkButton(
        main_frame, 
        text="Clear Transcript & AI", 
        command=lambda: clear_context(transcriber, speaker_queue, mic_queue, ai_textbox)
    )
    clear_button.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

    # Botón Derecho: Refrescar Manualmente Seguro
    refresh_button = ctk.CTkButton(
        main_frame,
        text="Force AI Refresh",
        fg_color="#1E88E5",
        hover_color="#1565C0",
        command=lambda: force_ai_refresh(transcriber, ai_textbox)
    )
    refresh_button.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))

    return transcript_textbox, ai_textbox

def main():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("ERROR: The ffmpeg library is not installed. Please install ffmpeg and try again.")
        return

    root = ctk.CTk()
    speaker_queue = queue.Queue()
    mic_queue = queue.Queue()

    user_audio_recorder = AudioRecorder.DefaultMicRecorder()
    user_audio_recorder.record_into_queue(mic_queue)

    time.sleep(2)

    speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
    speaker_audio_recorder.record_into_queue(speaker_queue)

    model = TranscriberModels.get_model('--api' in sys.argv)

    transcriber = AudioTranscriber(user_audio_recorder.source, speaker_audio_recorder.source, model)
    transcribe = threading.Thread(target=transcriber.transcribe_audio_queue, args=(speaker_queue, mic_queue))
    transcribe.daemon = True
    transcribe.start()

    transcript_textbox, ai_textbox = create_ui_components(root, transcriber, speaker_queue, mic_queue)

    print("READY")

    update_transcript_UI(transcriber, transcript_textbox)
    check_for_ai_updates(transcriber, ai_textbox, root)

    root.mainloop()

if __name__ == "__main__":
    main()