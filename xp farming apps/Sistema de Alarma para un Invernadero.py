import serial
import time

ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

while True:
    if ser.in_waiting > 0:
        texto_recibido = ser.readline().decode('utf-8').rstrip()
        
        temperatura = float(texto_recibido)
        
        if temperatura > 30:
            print("¡Alerta! La temperatura es demasiado alta: ", temperatura)
        else:
            print("Temperatura normal: ", temperatura)

