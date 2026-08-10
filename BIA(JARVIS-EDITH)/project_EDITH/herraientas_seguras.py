import os
from pathlib import Path

# Define la ÚNICA carpeta donde la IA tiene permitido trabajar
CARPETA_WORKSPACE = Path("./mi_workspace_ia").resolve()
CARPETA_WORKSPACE.mkdir(exist_ok=True)  # Se crea automáticamente si no existe

def es_ruta_segura(ruta_solicitada: str) -> Path:
    """Valida que la ruta solicitada por la IA esté estrictamente dentro de la carpeta permitida."""
    # Convierte la ruta en absoluta y resuelve accesos directos
    ruta_absoluta = (CARPETA_WORKSPACE / ruta_solicitada).resolve()
    
    # Comprueba que la carpeta del workspace sea el ancestro de la ruta solicitada
    if CARPETA_WORKSPACE not in ruta_absoluta.parents and ruta_absoluta != CARPETA_WORKSPACE:
        raise PermissionError(f"Acceso Bloqueado: La IA intentó acceder fuera del espacio asignado ({ruta_solicitada}).")
    
    return ruta_absoluta

# --- HERRAMIENTAS QUE LE DARÁS A TU AGENTE ---

def leer_codigo(nombre_archivo: str):
    try:
        ruta = es_ruta_segura(nombre_archivo)
        if not ruta.exists():
            return "El archivo no existe."
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return str(e)

def guardar_codigo(nombre_archivo: str, contenido: str):
    try:
        ruta = es_ruta_segura(nombre_archivo)
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return f"Archivo guardado exitosamente en: {ruta.name}"
    except Exception as e:
        return str(e)

# Ejemplo de prueba:
# Intentar guardar un archivo permitido -> FUNCIONA
print(guardar_codigo("main.py", "print('Hola desde Arduino o Python')"))

# Intentar acceder a otra parte de la PC -> BLOQUEADO
print(guardar_codigo("../../../Windows/System32/test.txt", "hacked"))
