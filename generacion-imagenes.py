import requests
import keyboard
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt

def showImg(img, text='image'):
    cv2.namedWindow(text, cv2.WINDOW_KEEPRATIO)
    cv2.imshow(text, img)
    cv2.resizeWindow(text, 700, 700)
    cv2.waitKey()
    cv2.destroyAllWindows()
    
def mostrarContornos(img,min,max, bool):
    # Aplicar deteccion de bordes utilizando Canny
    edges = cv2.Canny(img, min, max, apertureSize=3)
    if bool:
        showImg(edges, 'Detector de contornos')
    return edges

def rotarRecortarImagen(img, borde_x=10, borde_y=10, verbose=False):
    # Convertimos la imagen a gris
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if (verbose): showImg(img_gray, 'Imagen en blanco y negro')

    # Aplicar deteccion de bordes utilizando Canny
    edges = mostrarContornos(img_gray, 150, 300, verbose)

    if (verbose): showImg(edges, 'Contornos detectados')

    # Encontrar las lineas presentes en la imagen utilizando la transformada de Hough
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

    # Calcular el angulo promedio solo de las líneas horizontales detectadas
    angle = np.mean([np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]) for line in lines if abs(line[0][3] - line[0][1]) < abs(line[0][2] - line[0][0])])

    # Rotar la imagen utilizando el ángulo calculado
    (h, w) = img_gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle * 180 / np.pi, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    if (verbose): showImg(rotated, 'Imagen rotada')

    edges = mostrarContornos(rotated, 150, 300, verbose)

    if (verbose): showImg(edges, 'Mascara, hsv, imagen rotada')

    # Se encuentran los contornos
    contorno,_ = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cont = 0

    cropped_image = None
    booleano = True
    for c in contorno:
        area = cv2.contourArea(c)
        if (area > 20000):
            cont = cont + 1
            x,y,w,h = cv2.boundingRect(c)
            # Recortamos el contorno encontrado.
            if (booleano):
                # rotamos la imagen encontrada
                cropped_image = rotated[(y+borde_y):(y+h-borde_y), (x+borde_x):(x+w-borde_x)].copy()
                if (verbose): showImg(cropped_image, "Imagen recortada")
                booleano = False
            area = cv2.contourArea(c)
    
    if ~booleano:
        if (verbose): showImg(cropped_image, 'Imagen rotada y recortada')
        return cropped_image
    else:
        return 0
    
def recortarCasillero(image, i, j):
    width = image.shape[1]
    height = image.shape[0]
    start_y = int((height/8)*i)
    end_y = int((height/8)*i+(height/8))
    start_x = int((width/8)*j)
    end_x = int((width/8)*j+(width/8))
    casillero = image[start_y:end_y, start_x:end_x].copy()
    return casillero

def encontrarContornosPieza(image, mask, area_max=6000, area_min=200):
    retorno = image.copy()
    contorno,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    grid_contours = []   
    for contour in contorno:
        if area_max > cv2.contourArea(contour) > area_min:
            grid_contours.append(contour)

    cv2.drawContours(retorno, grid_contours, -1, (0, 255, 0), 2)
    return retorno, len(grid_contours)

# casilla1 : imagen recortada del casillero 
# verbose : imprime las imagenes de los casilleros con los filtros aplicados y contornos detectados
# white : es un booleano, true para detectar piezas rojas, false para piezas negras
def detectarPieza(casilla1, verbose=False, area_max=2000, area_min=200):
    lower_color_black = np.array([0, 0, 0])
    upper_color_black = np.array([90, 90, 90])
    mascara1 = cv2.inRange(casilla1, lower_color_black, upper_color_black).copy()
    img, contorno = encontrarContornosPieza(casilla1,mascara1,area_max, area_min)
    if verbose:
        showImg(casilla1)
        showImg(img, 'Contornos')
    if contorno > 0:
        if verbose: print('Pieza detectada')
        return 'b'
    else:
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([255, 255, 255])

        mascara1 = cv2.inRange(casilla1, lower_red, upper_red).copy()
        img, contorno = encontrarContornosPieza(casilla1,~mascara1,area_max, area_min)

        if contorno > 0:
            if verbose: print('Pieza detectada')
            return 'r'
        else:
            if verbose: print('Casillero vacio')
            return '.'    
        
def descargar_imagen(url, nombre_archivo):
    response = requests.get(url)
    if response.status_code == 200:
        with open(nombre_archivo, 'wb') as archivo:
            archivo.write(response.content)
        print(f'Imagen descargada como {nombre_archivo}')
    else:
        print('Error al descargar la imagen')


def main():
    print("Bienvenido .. \n     Presione 'q' para salir ")
    url_capturar = 'http://192.168.0.131/capture'
    url_descargar = 'http://192.168.0.131/saved-photo'
    nombre_archivo = input("Ingrese nombre del tablero: ")
    print("\n Presione 'espacio' para capturar las imagenes")
    while True:
        if keyboard.is_pressed('space'):
            print("\n Procesando ...")
            # enviamos un get para que se capture la foto
            requests.get(url_capturar)
            # tarda como maximo 5 segundos en procesarla el mcu
            print("\n Imagen capturada, esperando a que sea procesada por el MCU")
            time.sleep(7)
            nombre = nombre_archivo + ".jpg"
            descargar_imagen(url_descargar, nombre)
            
            img = cv2.imread("/home/tom/universidad/LIDI/cv-tablero/" + nombre)
            
            print("\n Aplicando algoritmos de computer vision ... \n Resultado \n")
            
            image = rotarRecortarImagen(img, 15,15)

            if isinstance(image, np.ndarray):
                plt.imshow(image)
                plt.show()
                matriz = np.empty((8, 8), dtype=str)
                for i in range(8):
                    for j in range(8):
                        cropped_image = recortarCasillero(image, i,j)
                        matriz[i][j] = detectarPieza(cropped_image, False, 6000, 400)
                print(matriz)
            else:
                print("Hubo un error al procesar la imagen..") 
        elif keyboard.is_pressed('q'):
            print("Saliendo ...")
            return 0  

if __name__ == "__main__":
    main()



