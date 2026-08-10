import tkinter as tk
from tkinter import messagebox
import qrcode

def generar_qr():
    nombre = entry_nombre.get().strip()
    apellido = entry_apellido.get().strip()
    telefono = entry_telefono.get().strip()
    email = entry_email.get().strip()
    web = entry_web.get().strip()
    whatsapp = entry_wa.get().strip()
    instagram = entry_ig.get().strip()
    facebook = entry_fb.get().strip()
    linkedin = entry_li.get().strip()
    
    if not nombre or not telefono:
        messagebox.showerror("Error", "El nombre y el teléfono son obligatorios.")
        return

    # Construir la estructura vCard 3.0 estándar con redes sociales
    vcard_lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{nombre} {apellido}",
        f"N:{apellido};{nombre};;;",
        f"TEL;TYPE=CELL:{telefono}"
    ]

    if email:
        vcard_lines.append(f"EMAIL:{email}")
    if web:
        vcard_lines.append(f"URL:{web}")
    if whatsapp:
        vcard_lines.append(f"URL;TYPE=WhatsApp:https://wa.me/{whatsapp}")
    if instagram:
        vcard_lines.append(f"URL;TYPE=Instagram:https://instagram.com/{instagram.replace('@', '')}")
    if facebook:
        vcard_lines.append(f"URL;TYPE=Facebook:https://facebook.com/{facebook}")
    if linkedin:
        vcard_lines.append(f"URL;TYPE=LinkedIn:https://linkedin.com/in/{linkedin}")

    vcard_lines.append("END:VCARD")
    vcard_data = "\n".join(vcard_lines)

    try:
        # Generar el código QR de manera automática y segura
        qr = qrcode.QRCode(
            version=None,  
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(vcard_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        nombre_archivo = f"contacto_{nombre.lower()}_{apellido.lower()}.png"
        img.save(nombre_archivo)

        messagebox.showinfo("¡Éxito!", f"¡Código QR generado sin errores como '{nombre_archivo}'!")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al generar el QR: {str(e)}")

# Configuración de la interfaz gráfica
ventana = tk.Tk()
ventana.title("Generador de QR vCard")
ventana.geometry("450x620")
ventana.config(padx=15, pady=15)

# Campos de entrada
tk.Label(ventana, text="Nombre:", font=("Arial", 9, "bold")).pack(anchor="w")
entry_nombre = tk.Entry(ventana, width=45)
entry_nombre.pack(pady=2)

tk.Label(ventana, text="Apellido:", font=("Arial", 9, "bold")).pack(anchor="w")
entry_apellido = tk.Entry(ventana, width=45)
entry_apellido.pack(pady=2)

tk.Label(ventana, text="Teléfono Celular (ej: +593...):", font=("Arial", 9, "bold")).pack(anchor="w")
entry_telefono = tk.Entry(ventana, width=45)
entry_telefono.pack(pady=2)

tk.Label(ventana, text="Correo Electrónico:", font=("Arial", 9, "bold")).pack(anchor="w")
entry_email = tk.Entry(ventana, width=45)
entry_email.pack(pady=2)

tk.Label(ventana, text="Sitio Web:", font=("Arial", 9, "bold")).pack(anchor="w")
entry_web = tk.Entry(ventana, width=45)
entry_web.pack(pady=2)

tk.Label(ventana, text="WhatsApp (número con código de país):", font=("Arial", 9, "bold")).pack(anchor="w")
entry_wa = tk.Entry(ventana, width=45)
entry_wa.pack(pady=2)

tk.Label(ventana, text="Instagram (usuario):", font=("Arial", 9, "bold")).pack(anchor="w")
entry_ig = tk.Entry(ventana, width=45)
entry_ig.pack(pady=2)

tk.Label(ventana, text="Facebook (usuario o enlace):", font=("Arial", 9, "bold")).pack(anchor="w")
entry_fb = tk.Entry(ventana, width=45)
entry_fb.pack(pady=2)

tk.Label(ventana, text="LinkedIn (usuario):", font=("Arial", 9, "bold")).pack(anchor="w")
entry_li = tk.Entry(ventana, width=45)
entry_li.pack(pady=2)

# Botón principal
btn_generar = tk.Button(ventana, text="Generar QR de Contacto", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=generar_qr)
btn_generar.pack(pady=20)

ventana.mainloop()
