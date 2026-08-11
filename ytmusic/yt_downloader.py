import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp

def descargar_contenido(url, formato_salida, ruta_destino):
    def proceso():
        try:
            lbl_estado.config(text="Estado: Descargando...", fg="orange")
            
            # Configuración de yt-dlp según el formato elegido
            ydl_opts = {
                'outtmpl': os.path.join(ruta_destino, '%(title)s.%(ext)s'),
                'progress_hooks': [hook_progreso],
            }

            if formato_salida == "mp3":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                ydl_opts.update({
                    'format': 'bestvideo+bestaudio/best',
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            lbl_estado.config(text="Estado: ¡Descarga completada con éxito!", fg="green")
            messagebox.showinfo("Éxito", "El archivo se ha descargado correctamente.")
        
        except Exception as e:
            lbl_estado.config(text="Estado: Error en la descarga", fg="red")
            messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")

    # Ejecutar en segundo plano para que la ventana no se congele
    threading.Thread(target=proceso).start()

def iniciar_descarga():
    url = entry_url.get().strip()
    formato = var_formato.get()
    ruta = entry_ruta.get().strip()

    if not url:
        messagebox.showwarning("Atención", "Por favor ingresa un enlace de YouTube.")
        return
    if not ruta:
        messagebox.showwarning("Atención", "Por favor selecciona una carpeta de destino.")
        return

    descargar_contenido(url, formato, ruta)

def seleccionar_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        entry_ruta.delete(0, tk.END)
        entry_ruta.insert(0, carpeta)

def hook_progreso(d):
    if d['status'] == 'downloading':
        porcentaje = d.get('_percent_str', '0%').strip()
        lbl_estado.config(text=f"Estado: Descargando... {porcentaje}", fg="blue")

# Configuración de la interfaz gráfica (Tkinter)
ventana = tk.Tk()
ventana.title("Descargador de YouTube (Seguro y Local)")
ventana.geometry("480x380")
ventana.config(padx=20, pady=20)

# URL
tk.Label(ventana, text="Enlace de YouTube:", font=("Arial", 10, "bold")).pack(anchor="w")
entry_url = tk.Entry(ventana, width=55)
entry_url.pack(pady=5)

# Carpeta de destino
tk.Label(ventana, text="Guardar en carpeta:", font=("Arial", 10, "bold")).pack(anchor="w")
frame_ruta = tk.Frame(ventana)
frame_ruta.pack(fill="x", pady=5)

entry_ruta = tk.Entry(frame_ruta, width=42)
entry_ruta.pack(side="left", padx=(0, 5))
entry_ruta.insert(0, os.path.join(os.path.expanduser("~"), "Downloads"))

btn_explorar = tk.Button(frame_ruta, text="Examinar", command=seleccionar_carpeta)
btn_explorar.pack(side="left")

# Formato (MP3 o MP4)
tk.Label(ventana, text="Formato de salida:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
var_formato = tk.StringVar(value="mp3")

frame_radio = tk.Frame(ventana)
frame_radio.pack(anchor="w", pady=5)
tk.Radiobutton(frame_radio, text="Audio MP3 (Alta Calidad)", variable=var_formato, value="mp3").pack(side="left", padx=(0, 20))
tk.Radiobutton(frame_radio, text="Vídeo MP4", variable=var_formato, value="mp4").pack(side="left")

# Botón de Descarga
btn_descargar = tk.Button(ventana, text="Iniciar Descarga", bg="#E53935", fg="white", font=("Arial", 11, "bold"), command=iniciar_descarga)
btn_descargar.pack(pady=20, fill="x")

# Etiqueta de estado
lbl_estado = tk.Label(ventana, text="Estado: Esperando enlace...", fg="gray", font=("Arial", 9))
lbl_estado.pack(anchor="w")

ventana.mainloop()
