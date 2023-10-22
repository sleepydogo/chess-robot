import requests
import cv2
from serial_dev import ESP32CAM
import time


class Network:

    class ESP32CAM: 
        IP = None
        URL_CAPTURE = '/capture'
        URL_DOWNLOAD = '/saved-photo'

        def init(self, ip):
            self.IP = ip

    mcu = ESP32CAM

    def solicitar_foto(self, ruta):
        requests.get(mcu.url_capturar)
        print("Imagen capturada, esperando a que sea procesada por el MCU\n")
        time.sleep(4)
        response = requests.get(mcu.url_descargar)
        time.sleep(2)
        if response.status_code == 200:
            with open(ruta, 'wb') as archivo:
                archivo.write(response.content)
            # Rotacion de imagen
            imagen = cv2.imread(ruta)
            angulo_rotacion = 90
            alto, ancho = imagen.shape[:2]
            centro = (ancho // 2, alto // 2)
            matriz_rotacion = cv2.getRotationMatrix2D(centro, angulo_rotacion, 1.0)
            imagen_rotada = cv2.warpAffine(imagen, matriz_rotacion, (ancho, alto))
            cv2.imwrite(ruta, imagen_rotada)

            print(f'Imagen descargada como {ruta}\n')
        else:
            print('Error al descargar la imagen')


    def init(self, ip):
        self.mcu.MCU_IP = ip