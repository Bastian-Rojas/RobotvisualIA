import time
import cv2
from ultralytics import YOLO
import serial
import sys
import argparse
import os
import logging
import serial.tools.list_ports
import numpy as np
import signal

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# =======================
# Función para Detectar el Puerto Serial de Arduino
# =======================

def detectar_puerto_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Puedes ajustar los criterios según el Arduino que uses
        if 'Arduino' in port.description or 'CH340' in port.description or 'Silicon Labs' in port.description:
            return port.device
    return None


# =======================
# Configuración de Serial
# =======================

parser = argparse.ArgumentParser(description='Control del robot con YOLO y Arduino.')
parser.add_argument('--port', type=str, default=None, help='Puerto serial para el Arduino')
parser.add_argument('--baud', type=int, default=9600, help='Tasa de baudios para la comunicación serial')
parser.add_argument('--model', type=str, default='best.pt', help='Ruta al modelo YOLO')
args = parser.parse_args()

if args.port:
    SERIAL_PORT = args.port
else:
    SERIAL_PORT = detectar_puerto_arduino()

BAUD_RATE = args.baud
MODEL_PATH = args.model

if SERIAL_PORT is None:
    logging.error("No se encontró un dispositivo Arduino conectado. Especifica el puerto manualmente usando --port.")
    sys.exit()

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Esperar a que la conexión se establezca
    logging.info(f"Conectado al Arduino en {SERIAL_PORT} a {BAUD_RATE} baudios.")
except serial.SerialException as e:
    logging.error(f"No se pudo conectar al puerto serial {SERIAL_PORT}: {e}")
    sys.exit()

# =======================
# Inicialización del Modelo YOLO
# =======================

if not os.path.exists(MODEL_PATH):
    logging.error(f"Modelo YOLO no encontrado en {MODEL_PATH}. Asegúrate de que el archivo exista.")
    ser.close()
    sys.exit()

try:
    model = YOLO(MODEL_PATH)
    logging.info("Modelo YOLO cargado exitosamente.")
except Exception as e:
    logging.error(f"Error al cargar el modelo YOLO: {e}")
    ser.close()
    sys.exit()


# =======================
# Funciones de Control
# =======================

def enviar_comando(comando):
    """
    Envía un comando al Arduino a través de la comunicación serial.
    Args:
        comando (str): Comando a enviar (e.g., 'FORWARD', 'BACKWARD').
    """
    try:
        comando_bytes = (comando + '\n').encode('utf-8')
        ser.write(comando_bytes)
        logging.info(f"Enviado comando: {comando}")
    except Exception as e:
        logging.error(f"Error al enviar comando '{comando}': {e}")


def adelante():
    enviar_comando('FORWARD')


def atras():
    enviar_comando('BACKWARD')


def giro_izquierda():
    enviar_comando('TURN_LEFT')


def giro_derecha():
    enviar_comando('TURN_RIGHT')


def detener():
    enviar_comando('STOP')


# =======================
# Función de Procesamiento de Visión
# =======================

def procesar_vision(frame):
    """
    Procesa el cuadro de video utilizando el modelo YOLO para detectar objetos.
    Args:
        frame (numpy.ndarray): Cuadro de video capturado.
    Returns:
        resultados: Resultados de la detección de objetos.
    """
    resultados = model.predict(frame, imgsz=640, conf=0.85)
    return resultados


# =======================
# Función para Recibir Distancia
# =======================

def recibir_distancia():
    """
    Lee la distancia enviada por el Arduino a través de la comunicación serial.
    Returns:
        distancia (float): Distancia medida en centímetros.
    """
    try:
        if ser.in_waiting > 0:
            linea = ser.readline().decode('utf-8').rstrip()
            if linea.startswith("DIST:"):
                distancia_str = linea.split(":")[1]
                if distancia_str == "INF":
                    return float('inf')
                distancia = float(distancia_str)
                return distancia
    except Exception as e:
        logging.error(f"Error al recibir distancia: {e}")
    return None


# =======================
# Función para Dibujar Detecciones en el Cuadro de Video
# =======================

def dibujar_detecciones(frame, resultados):
    """
    Dibuja las detecciones de YOLO en el cuadro de video.
    Args:
        frame (numpy.ndarray): Cuadro de video.
        resultados: Resultados de la detección de objetos.
    Returns:
        frame: Cuadro de video con las detecciones dibujadas.
    """
    for resultado in resultados:
        boxes = resultado.boxes
        for box in boxes:
            # Extraer información de la detección
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            # Asegurar que 'clase' sea un entero escalar
            clase = int(box.cls.cpu().numpy())
            confianza = float(box.conf.cpu().numpy())
            nombre_clase = model.names[clase]

            # Dibujar el rectángulo
            color = (0, 255, 0)  # Verde para las cajas
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Escribir el nombre de la clase y la confianza
            label = f"{nombre_clase} {confianza:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)  # Fondo para el texto
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    return frame


# =======================
# Función para Detener Motores al Cerrar el Script
# =======================

def stop_on_exit(signum, frame):
    """
    Función para manejar señales de terminación y enviar comando de parada.
    """
    logging.info("Recibida señal de terminación. Deteniendo motores...")
    detener()
    time.sleep(1)  # Esperar a que el comando se envíe
    ser.close()
    cap.release()
    cv2.destroyAllWindows()
    logging.info("Conexión serial cerrada, cámara liberada y ventanas cerradas.")
    sys.exit()


# Registrar señales de terminación
signal.signal(signal.SIGINT, stop_on_exit)  # Ctrl+C
signal.signal(signal.SIGTERM, stop_on_exit)  # Señales de terminación


# =======================
# Bucle Principal
# =======================

def main():
    try:
        logging.info("Iniciando el bucle principal. Presiona 'q' en la ventana de video para detener.")
        while True:
            # Leer distancia del Arduino
            distancia = recibir_distancia()
            if distancia is not None:
                if distancia == float('inf'):
                    logging.info("No se detectaron obstáculos cercanos.")
                else:
                    logging.info(f"Distancia recibida: {distancia} cm")
            else:
                logging.warning("No se recibió distancia válida.")
                distancia = float('inf')  # Asumir que no hay obstáculo

            # Capturar cuadro de la cámara
            ret, frame = cap.read()
            if not ret:
                logging.error("No se pudo leer el cuadro de la cámara.")
                break

            # Procesar la visión
            resultados = procesar_vision(frame)

            # Implementar lógica basada en los resultados de la detección
            objetos_detectados = False
            for resultado in resultados:
                boxes = resultado.boxes
                for box in boxes:
                    clase = int(box.cls.cpu().numpy())  # Corregido a entero escalar
                    confianza = float(box.conf.cpu().numpy())  # Convertir a float
                    nombre_clase = model.names[clase]
                    if confianza >= 0.85:
                        objetos_detectados = True
                        break
                if objetos_detectados:
                    break

            # Decidir el movimiento basado en la distancia y detección de objetos
            if distancia < 20:
                logging.info("Obstáculo cercano detectado. Retrocediendo y girando.")
                atras()
                time.sleep(0.5)
                giro_izquierda()
                time.sleep(0.5)
            elif objetos_detectados:
                logging.info("Objetos detectados mediante visión. Deteniendo el robot.")
                detener()
                time.sleep(0.5)
            else:
                logging.info("Ruta despejada. Avanzando.")
                adelante()
                time.sleep(0.1)  # Pequeña pausa para evitar sobrecargar la CPU

            # Dibujar las detecciones en el cuadro de video
            frame_dibujado = dibujar_detecciones(frame, resultados)

            # Mostrar el cuadro de video con detecciones
            cv2.imshow('Captura de Video - Detecciones YOLO', frame_dibujado)

            # Verificar si el usuario presionó 'q' para salir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Deteniendo el programa por la acción del usuario.")
                break

    except Exception as e:
        logging.error(f"Error inesperado: {e}")

    finally:
        # Enviar comando de parada y liberar recursos
        logging.info("Enviando comando de parada antes de cerrar...")
        detener()
        time.sleep(1)  # Esperar a que el comando se envíe
        ser.close()
        cap.release()
        cv2.destroyAllWindows()
        logging.info("Conexión serial cerrada, cámara liberada y ventanas cerradas.")


if __name__ == "__main__":
    # Inicializar la cámara
    cap = cv2.VideoCapture(0)  # Asegúrate de que la cámara esté conectada y configurada

    if not cap.isOpened():
        logging.error("No se pudo abrir la cámara.")
        sys.exit()

    main()