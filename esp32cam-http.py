
import requests, time

url_capturar = 'http://192.168.0.131/capture'
url_descargar = 'http://192.168.0.131/saved-photo'

def solicitarFoto(ruta):
    requests.get(url_capturar)
    # tarda como maximo 5 segundos en procesarla el mcu
    print("Imagen capturada, esperando a que sea procesada por el MCU\n")
    time.sleep(7)
    response = requests.get(url_descargar)
    time.sleep(2)
    if response.status_code == 200:
        with open(ruta, 'wb') as archivo:
            archivo.write(response.content)
        print(f'Imagen descargada como {ruta}\n')
    else:
        print('Error al descargar la imagen')