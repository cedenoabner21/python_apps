import asyncio
import os
import io
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
import edge_tts
from playsound import playsound

VOZ_BIA = "es-ES-AlvaroNeural"

async def _generar_audio(texto: str, archivo_salida: str = "respuesta_temp.mp3"):
    comunicador = edge_tts.Communicate(texto, VOZ_BIA)
    await comunicador.save(archivo_salida)

def hablar(texto: str):
    archivo_temp = "respuesta_temp.mp3"
    try:
        asyncio.run(_generar_audio(texto, archivo_temp))
        playsound(archivo_temp)
        if os.path.exists(archivo_temp):
            os.remove(archivo_temp)
    except Exception as e:
        print(f"⚠️ [Error de Voz]: {e}")

def escuchar_microfono(duracion_segundos: int = 5, frecuencia: int = 44100) -> str:
    """Graba audio desde el micrófono usando sounddevice y lo convierte a texto."""
    try:
        print("\n🎤 Escuchando, señor... (Habla ahora)")
        # Grabación directa desde el micrófono por el tiempo especificado
        grabacion = sd.rec(int(duracion_segundos * frecuencia), samplerate=frecuencia, channels=1, dtype='int16')
        sd.wait()  # Espera a que termine la grabación
        
        print("⚡ Procesando voz a texto...")
        
        # Convertir datos de audio en formato WAV en memoria
        buffer_wav = io.BytesIO()
        wav.write(buffer_wav, frecuencia, grabacion)
        buffer_wav.seek(0)
        
        # Reconocimiento con SpeechRecognition
        reconocedor = sr.Recognizer()
        with sr.AudioFile(buffer_wav) as fuente:
            audio_data = reconocedor.record(fuente)
            texto = reconocedor.recognize_google(audio_data, language="es-ES")
            print(f"Tú (Voz): {texto}")
            return texto

    except sr.UnknownValueError:
        print("BIA: No logré entender lo que dijo, señor.")
        return ""
    except sr.RequestError:
        print("⚠️ [Error]: Fallo en la conexión del reconocimiento de voz.")
        return ""
    except Exception as e:
        print(f"⚠️ [Error de Micrófono]: {e}")
        return ""
        