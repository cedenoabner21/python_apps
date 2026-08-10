import os
import subprocess
import json
import sys
import shutil
import ollama
from pathlib import Path
import modulo_voz as voz
from ddgs import DDGS
import subprocess
import re


# Cambiar el título de la consola en Windows
if sys.platform == "win32":
    os.system("title B.I.A.")

# ==========================================
# 1. SEGURIDAD Y ENTORNO
# ==========================================
CARPETA_WORKSPACE = Path("./mi_workspace_ia").resolve()
CARPETA_WORKSPACE.mkdir(exist_ok=True)

# Papelera de reciclaje local dentro del workspace
PAPELERA_LOCAL = CARPETA_WORKSPACE / "recycle_bin"
PAPELERA_LOCAL.mkdir(exist_ok=True)

RUTA_HISTORIAL = CARPETA_WORKSPACE / "historial_memoria.json"

def es_ruta_segura(ruta_solicitada: str) -> Path:
    """Garantiza que la IA solo opere dentro del workspace."""
    ruta_absoluta = (CARPETA_WORKSPACE / ruta_solicitada).resolve()
    if CARPETA_WORKSPACE not in ruta_absoluta.parents and ruta_absoluta != CARPETA_WORKSPACE:
        raise PermissionError("Acceso Bloqueado: Intento de salir del espacio seguro.")
    return ruta_absoluta

# ==========================================
# 2. GESTIÓN DEL HISTORIAL EN DISCO (AHORRO DE RAM)
# ==========================================
def cargar_historial_disco(limite_mensajes: int = 6) -> list:
    if not RUTA_HISTORIAL.exists():
        return []
    try:
        with open(RUTA_HISTORIAL, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos[-limite_mensajes:]
    except Exception:
        return []

def guardar_mensaje_disco(rol: str, contenido: str):
    historial_completo = []
    if RUTA_HISTORIAL.exists():
        try:
            with open(RUTA_HISTORIAL, "r", encoding="utf-8") as f:
                historial_completo = json.load(f)
        except Exception:
            historial_completo = []

    historial_completo.append({"role": rol, "content": contenido})

    with open(RUTA_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(historial_completo, f, ensure_ascii=False, indent=2)

# ==========================================
# 3. HERRAMIENTAS REALES DEL SISTEMA
# ==========================================
MAPA_APLICACIONES = {
    "krita": ["krita", "dibujar", "dibujo"],
    "chrome": ["chrome", "navegador", "google chrome"],
    "notepad": ["bloc de notas", "notepad", "notas", "texto"],
    "calc": ["calculadora", "calc"],
    "code": ["vscode", "visual studio", "codigo", "programar"]
}

RUTAS_EXPLICITAS = {
    "krita": r"C:\Program Files\Krita (x64)\bin\krita.exe",  # Ajusta la ruta a tu ejecutable si no está en el PATH
    "chrome": "chrome.exe",
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "code": "code"
}
def procesar_comando_directo(texto: str) -> tuple[bool, str]:
    """
    Analiza si el texto coincide con una intención directa de abrir una app.
    Retorna (Exito, Mensaje_Respuesta).
    """
    texto_limpio = texto.lower().strip()

    # Verificamos si hay intención de abrir/ejecutar
    verbos = ["abre", "abrir", "ejecuta", "ejecutar", "lanza", "inicia", "iniciar", "quiero"]
    tiene_intencion = any(verbo in texto_limpio for verbo in verbos)

    if not tiene_intencion:
        return False, ""

    # Identificar la aplicación
    for app_id, palabras_clave in MAPA_APLICACIONES.items():
        for kw in palabras_clave:
            if kw in texto_limpio:
                ejecutable = RUTAS_EXPLICITAS.get(app_id, app_id)
                try:
                    subprocess.Popen(ejecutable, shell=True)
                    return True, f"Abriendo {app_id.capitalize()} de inmediato, señor."
                except Exception as e:
                    return True, f"Intenté abrir {app_id}, pero ocurrió un error al ejecutarlo."

    return False, ""

def buscar_en_internet(consulta: str) -> str:
    """Busca en la red si no hay suficiente contexto local."""
    try:
        # Usamos el cliente con timeout y contexto estructurado
        with DDGS() as ddgs:
            # region='wt-wt' busca globalmente sin restringir por país
            resultados = list(ddgs.text(consulta, region='wt-wt', max_results=3))
            
            if not resultados:
                return "No se encontraron resultados en la red, señor."
            
            texto_resultados = ""
            for res in resultados:
                texto_resultados += f"- {res.get('title', '')}: {res.get('body', '')}\n"
            return texto_resultados
            
    except Exception as e:
        # Si falla por problemas de red o tiempo de espera
        return "ERROR_CONEXION"

def crear_archivo(ruta: str, contenido: str = "") -> str:
    try:
        ruta_valida = es_ruta_segura(ruta)
        ruta_valida.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta_valida, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Éxito: Archivo '{ruta_valida.name}' creado."
    except Exception as e:
        return f"Error al crear archivo: {str(e)}"

def leer_archivo(ruta: str) -> str:
    try:
        ruta_valida = es_ruta_segura(ruta)
        if not ruta_valida.exists():
            return f"Error: El archivo '{ruta_valida.name}' no existe."
        with open(ruta_valida, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al leer archivo: {str(e)}"

def editar_archivo(ruta: str, contenido: str, modo: str = "sobrescribir") -> str:
    try:
        ruta_valida = es_ruta_segura(ruta)
        if not ruta_valida.exists():
            return f"Error: El archivo '{ruta_valida.name}' no existe."
        
        modo_apertura = "a" if modo == "agregar" else "w"
        with open(ruta_valida, modo_apertura, encoding="utf-8") as f:
            if modo == "agregar":
                f.write("\n" + contenido)
            else:
                f.write(contenido)
        return f"Éxito: Archivo '{ruta_valida.name}' editado."
    except Exception as e:
        return f"Error al editar archivo: {str(e)}"

def borrar_archivo(ruta: str) -> str:
    try:
        ruta_valida = es_ruta_segura(ruta)
        if not ruta_valida.exists():
            return f"Error: El elemento '{ruta_valida.name}' no existe."
        
        if ruta_valida.is_dir():
            shutil.rmtree(ruta_valida)
        else:
            os.remove(ruta_valida)
        return f"Éxito: '{ruta_valida.name}' ha sido eliminado."
    except Exception as e:
        return f"Error al borrar: {str(e)}"

def crear_carpeta(nombre_carpeta: str) -> str:
    try:
        ruta_valida = es_ruta_segura(nombre_carpeta)
        ruta_valida.mkdir(parents=True, exist_ok=True)
        return f"Éxito: Carpeta '{ruta_valida.name}' creada."
    except Exception as e:
        return f"Error al crear carpeta: {str(e)}"

def mover_elemento(origen: str, destino: str = "recycle_bin") -> str:
    try:
        ruta_origen = es_ruta_segura(origen)
        if not ruta_origen.exists():
            return f"Error: El origen '{ruta_origen.name}' no existe."
        
        ruta_destino = es_ruta_segura(destino)
        ruta_destino.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(ruta_origen), str(ruta_destino / ruta_origen.name))
        return f"Éxito: '{ruta_origen.name}' movido a '{ruta_destino.name}'."
    except Exception as e:
        return f"Error al mover elemento: {str(e)}"

def abrir_aplicacion(nombre_app: str) -> str:
    try:
        apps = {
            "bloc de notas": "notepad.exe",
            "notepad": "notepad.exe",
            "calculadora": "calc.exe",
            "cmd": "cmd.exe",
            "vscode": "code"
        }
        ejecutable = apps.get(nombre_app.lower(), nombre_app)
        subprocess.Popen(ejecutable, shell=True)
        return f"Éxito: Aplicación '{nombre_app}' abierta."
    except Exception as e:
        return f"Error al abrir aplicación: {str(e)}"

herramientas_disponibles = {
    'crear_archivo': crear_archivo,
    'leer_archivo': leer_archivo,
    'editar_archivo': editar_archivo,
    'borrar_archivo': borrar_archivo,
    'crear_carpeta': crear_carpeta,
    'mover_elemento': mover_elemento,
    'abrir_aplicacion': abrir_aplicacion,
    'buscar_en_internet': buscar_en_internet
}

# ==========================================
# 4. SYSTEM PROMPT (Optimizado para BIA)
# ==========================================
PERSONALIDAD = """
Eres BIA, una Inteligencia Artificial asistente personal ejecutándose localmente.

REGLAS DE IDENTIDAD Y PROTOCOLO:
1. TRATAMIENTO: Dirígete SIEMPRE al usuario como "señor".
2. ESTILO: Tono refinado, pragmático, formal y con un leve toque de humor sarcástico elegante.
3. CONCISIÓN OBLIGATORIA: Respuestas de máximo 2 a 3 oraciones. Sé directo.
4. PERFIL DEL USUARIO: Es un joven nacido en 2009 (estudiante / programador).
5. USO DE RED: Si te preguntan sobre eventos recientes, noticias, datos en tiempo real o temas de los que no tengas contexto preciso, DEBES usar la herramienta de búsqueda en internet.

EJEMPLOS DE RESPUESTA:
- Confirmación: "Claro, señor. Procesando la solicitud de inmediato."
- Sin red/contexto: "Me temo que no tengo suficiente información al respecto, señor, y no hay acceso a internet en este momento."

REGLAS STRICTAS DE HERRAMIENTAS:
Si el usuario pide una acción o información que requiere internet, responde EXCLUSIVAMENTE un JSON en una sola línea.

FORMATOS JSON PERMITIDOS:
- Buscar en red: {"accion": "buscar_en_internet", "consulta": "clima actual o noticia"}
- Crear archivo: {"accion": "crear_archivo", "ruta": "test.txt", "contenido": "texto"}
- Leer archivo: {"accion": "leer_archivo", "ruta": "test.txt"}
- Editar archivo: {"accion": "editar_archivo", "ruta": "test.txt", "contenido": "texto", "modo": "sobrescribir"}
- Borrar elemento: {"accion": "borrar_archivo", "ruta": "test.txt"}
- Crear carpeta: {"accion": "crear_carpeta", "nombre_carpeta": "mi_carpeta"}
- Mover/Papelera: {"accion": "mover_elemento", "origen": "test.txt", "destino": "recycle_bin"}
- Abrir app: {"accion": "abrir_aplicacion", "nombre_app": "notepad"}

Si la solicitud es conversación normal que puedes responder con tu conocimiento base, responde en texto plano.
"""

# No olvides agregar esta importación al puro inicio del archivo core.py:
# import modulo_voz as voz

print("--- B.I.A. INICIADA (Modo Voz y Texto) ---")

while True:
    entrada = input(">")
    if not entrada:
        continue

    es_comando_directo, respuesta_directa = procesar_comando_directo(entrada)

    if es_comando_directo:
        print(f"\n⚡ [Comando Directo]: {respuesta_directa}")
        voz.hablar(respuesta_directa)
        guardar_mensaje_disco("user", entrada)
        guardar_mensaje_disco("assistant", respuesta_directa)
        continue

    # 2. PROCESAMIENTO CON IA (Si no fue un comando directo de apertura)
    # Aquí continúa tu código habitual enviando 'entrada' a Ollama...

    mensajes_contexto = [{"role": "system", "content": PERSONALIDAD}]
    mensajes_contexto.extend(cargar_historial_disco(limite_mensajes=6))

    try:
        respuesta = ollama.chat(
            model='qwen2.5-coder:3b',
            messages=mensajes_contexto,
            options={
                'num_ctx': 1536,
                'temperature': 0.3,
                'top_p': 0.9
            }
        )
    except Exception as e:
        print("\n⚠️ [Error]: No se pudo conectar con Ollama.")
        continue

    texto_ia = respuesta['message']['content'].strip()

    # Evaluación de ejecución de herramientas JSON
    if texto_ia.startswith("{") and texto_ia.endswith("}"):
        try:
            datos = json.loads(texto_ia)
            accion = datos.get("accion")

            if accion in herramientas_disponibles:
                
                print(f"🤖 [BIA]: Ejecutando orden ({accion})...")
                if accion == "buscar_en_internet":
                    res = buscar_en_internet(datos.get("consulta", ""))
                    if res == "ERROR_CONEXION":
                        msg_error = "Me temo que no tengo contexto sobre ese tema, señor, y no cuento con conexión a internet para consultar en este momento."
                        print(f"\nBIA: {msg_error}")
                        voz.hablar(msg_error)
                        guardar_mensaje_disco("assistant", msg_error)
                        continue
                elif accion == "crear_archivo":
                    res = crear_archivo(datos.get("ruta", "archivo.txt"), datos.get("contenido", ""))
                elif accion == "leer_archivo":
                    res = leer_archivo(datos.get("ruta", ""))
                elif accion == "editar_archivo":
                    res = editar_archivo(datos.get("ruta", ""), datos.get("contenido", ""), datos.get("modo", "sobrescribir"))
                elif accion == "borrar_archivo":
                    res = borrar_archivo(datos.get("ruta", ""))
                elif accion == "crear_carpeta":
                    res = crear_carpeta(datos.get("nombre_carpeta", "nueva_carpeta"))
                elif accion == "mover_elemento":
                    res = mover_elemento(datos.get("origen", ""), datos.get("destino", "recycle_bin"))
                elif accion == "abrir_aplicacion":
                    res = abrir_aplicacion(datos.get("nombre_app", ""))
                else:
                    res = "Acción no reconocida."

                print(f"⚙️ [Sistema]: {res}")
                
                guardar_mensaje_disco("assistant", f"Acción ejecutada: {res}")
                mensajes_contexto.append({"role": "assistant", "content": f"Acción ejecutada: {res}"})
                
                # Segunda llamada para generar la confirmación hablada
                confirmacion = ollama.chat(
                    model='qwen2.5-coder:3b',
                    messages=mensajes_contexto,
                    options={
                        'num_ctx': 1536,
                        'temperature': 0.3,
                        'top_p': 0.9
                    }
                )
                texto_confirmacion = confirmacion['message']['content'].strip()
                guardar_mensaje_disco("assistant", texto_confirmacion)
                print(f"\nBIA: {texto_confirmacion}")
                voz.hablar(texto_confirmacion)
                continue

        except json.JSONDecodeError:
            pass

    # Respuesta conversacional estándar
    guardar_mensaje_disco("assistant", texto_ia)
    print(f"\nBIA: {texto_ia}")
    voz.hablar(texto_ia)
