import cv2
import numpy as np
import requests
import time
import os
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.widgets as widgets

verbose = False


class SquareSelection():
    x_initial = 272 
    y_initial = 140
    x_release = 959
    y_release = 831

selec = SquareSelection()

def tienen_mismos_numeros(array1, array2):
    conjunto1 = set(array1)
    conjunto2 = set(array2)
    return conjunto1 == conjunto2

def determinar_puntos(mov0, mov1, cont_peon_capturas=0):
    matriz_mov_tipos = np.array([[1,-1],  # mov negro 0 
                            [2,-1],  # pieza blanca come pieza negra 1 
                            [1,1],   # pieza negra come pieza blanca 2
                            [2,-2]])  # mov blanco 3 

    res = mov0 - mov1

    puntos = np.zeros((2,3), dtype=int)
    cont = 0

    # estructura de la variable puntos -->  [indice][res, x, y]
    for i in range(8):
        for j in range(8):
            if (res[i][j] != 0):
                if cont == 2:
                    return None, None, False, False
                puntos[cont][0] = res[i][j] 
                puntos[cont][1] = i
                puntos[cont][2] = j
                cont = cont + 1
                
    diferencias = np.array([puntos[0][0], puntos[1][0]])

    caso = -1
    captura = False
    for i in range(4):
        if (tienen_mismos_numeros(diferencias, matriz_mov_tipos[i])):
            caso = i
            break

    origen =  np.zeros((2), dtype=int)
    destino = np.zeros((2), dtype=int)

    if (caso == 0):
        for i in range(2):
            if (puntos[i][0] == 1): 
                origen[0] = int(puntos[i][1])
                origen[1] = int(puntos[i][2])
            else:
                destino[0] = int(puntos[i][1])
                destino[1] = int(puntos[i][2])
    elif (caso == 1):
        cont_peon_capturas = cont_peon_capturas + 1
        captura = True
        for i in range(2):
            if (puntos[i][0] == 2): 
                origen[0] = puntos[i][1]
                origen[1] = puntos[i][2]
            else:
                destino[0] = puntos[i][1]
                destino[1] = puntos[i][2]
    elif (caso == 2):
        cont_peon_capturas = cont_peon_capturas + 1
        captura = True
        for i in range(2):
            if (mov1[puntos[i][1]][puntos[i][2]] == 0): 
                origen[0] = puntos[i][1]
                origen[1] = puntos[i][2]
            else:
                destino[0] = puntos[i][1]
                destino[1] = puntos[i][2]
    elif (caso == 3):
        for i in range(2):
            if (puntos[i][0] == 2): 
                origen[0] = puntos[i][1]
                origen[1] = puntos[i][2]
            else:
                destino[0] = puntos[i][1]
                destino[1] = puntos[i][2]
    return origen, destino, True, captura

def guardar_valores_en_archivo(filename, valores):
    with open(filename, 'w') as archivo:
        for valor in valores:
            archivo.write(str(valor) + '\n')

def calibrar(filename):
    def onselect(eclick, erelease):
        if eclick.ydata>erelease.ydata:
            eclick.ydata,erelease.ydata=erelease.ydata,eclick.ydata
        if eclick.xdata>erelease.xdata:
            eclick.xdata,erelease.xdata=erelease.xdata,eclick.xdata
        ax.set_ylim(erelease.ydata,eclick.ydata)
        ax.set_xlim(eclick.xdata,erelease.xdata)
        fig.canvas.draw()
        selec.x_initial = int(eclick.xdata)
        selec.y_initial = int(eclick.ydata) 
        selec.x_release = int(erelease.xdata) 
        selec.y_release = int(erelease.ydata)
        guardar_valores_en_archivo('config.log', [selec.x_initial, selec.x_release, selec.y_initial, selec.y_release])
    input(" Seleccione en la imagen el tablero ...")
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = Image.open(filename)
    arr = np.asarray(im)
    plt_image = plt.imshow(arr)
    rs = widgets.RectangleSelector(
        ax, onselect, interactive=True,
        props = dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True))
    plt.show()
    plt.close()

def mostrar_contornos(img, min, max):
    # Aplicar deteccion de bordes utilizando Canny
    edges = cv2.Canny(img, min, max, apertureSize=3)
    if verbose:
        cv2.imshow('Detector de contornos', edges)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()
    return edges

def rotar_imagen(img):
    # Convertimos la imagen a gris
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).copy()

    if verbose: 
        cv2.imshow('Imagen en blanco y negro', img_gray)
        cv2.waitKey()
        cv2.destroyAllWindows()

    # Aplicar deteccion de bordes utilizando Canny
    edges = mostrar_contornos(img_gray, 150, 300)

    if verbose: 
        cv2.imshow('Contornos detectados', edges)
        cv2.waitKey()
        cv2.destroyAllWindows()

    # Encontrar las lineas presentes en la imagen utilizando la transformada de Hough
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

    # Calcular el angulo promedio solo de las líneas horizontales detectadas
    angle = np.mean([np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]) for line in lines if abs(line[0][3] - line[0][1]) < abs(line[0][2] - line[0][0])])

    # Rotar la imagen utilizando el ángulo calculado
    (h, w) = img_gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle * 180 / np.pi, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    if verbose: 
        cv2.imshow('Imagen rotada', rotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return rotated

# Recibe una imagen como parametro aplica una mascara que binariza los colores rojos.
def detectar_color_rojo(img):
    imagen_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Definir el rango de rojo en el espacio de color HSV
    rojo_bajo = np.array([0, 100, 100])
    rojo_alto = np.array([10, 255, 255])

    rojo_bajo1 = np.array([170, 100, 100])
    rojo_alto1 = np.array([179, 255, 255])

    # Crea una máscara para los píxeles que caen dentro del rango de rojo
    mascara1= cv2.inRange(imagen_hsv, rojo_bajo, rojo_alto)
    mascara2 = cv2.inRange(imagen_hsv, rojo_bajo1, rojo_alto1)

    mascara = cv2.add(mascara1, mascara2)

    resultado = cv2.bitwise_and(img, img, mask=mascara)

    return mascara

# Recibe una imagen como parametro aplica una mascara que binariza los colores negros
def detectar_color_negro(img):
    # Convierte la imagen a espacio de color HSV
    imagen_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Definir el rango de rojo en el espacio de color HSV
    negro_bajo = np.array([0, 0, 0])
    negro_alto = np.array([179, 255, 100])

    # Crea una máscara para los píxeles que caen dentro del rango de rojo
    mascara = cv2.inRange(imagen_hsv, negro_bajo, negro_alto)

    return mascara

def encontrar_contornos_pieza(image, mask, area_max=6000, area_min=200):
    retorno = image.copy()
    contorno,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    grid_contours = []   
    for contour in contorno:
        if area_max > cv2.contourArea(contour) > area_min:
            grid_contours.append(contour)

    cv2.drawContours(retorno, grid_contours, -1, (0, 255, 0), 2)
    
    return len(grid_contours)

#mascaras

def detectar_pieza(casilla1, area_max=6000, area_min=900):
    mascara_negra = detectar_color_negro(casilla1.copy())
    mascara_roja = detectar_color_rojo(casilla1.copy())

    cantidad_contornos = encontrar_contornos_pieza(casilla1, mascara_negra, area_max, area_min)

    if cantidad_contornos > 0:
        if verbose: print('Pieza detectada')
        return 1
    else:
        cantidad_contornos = encontrar_contornos_pieza(casilla1, ~mascara_roja, area_max, area_min)

        if cantidad_contornos > 0:
            if verbose: print('Pieza detectada')
            return 2
        else:
            if verbose: print('Casillero vacio')
            return 0    

def solicitar_foto(ruta):
    requests.get('http://192.168.0.131/capture')
    print("Imagen capturada, esperando a que sea procesada por el MCU\n")
    time.sleep(7)
    response = requests.get('http://192.168.0.131/saved-photo')
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

def recortar_casillero(image, i, j):
    width = image.shape[1]
    height = image.shape[0]
    start_y = int((height/8)*i)
    end_y = int((height/8)*i+(height/8))
    start_x = int((width/8)*j)
    end_x = int((width/8)*j+(width/8))
    casillero = image[start_y:end_y, start_x:end_x].copy()
    return casillero

def actualizar_tablero(tablero, ruta, matriz_numerica_t0, matriz_numerica_t1, cont_jugadas, cont_peon_capturas):
    print("Procesando ... \n")
    for i in range(12):  
        print("Intento " + str(i) + "\n")
        solicitar_foto(ruta)
        image = cv2.imread(ruta)

        print("Aplicando algoritmos de computer vision ... \n Resultado \n")
        image = rotar_imagen(image)

        image = image[(selec.y_initial):(selec.y_release), (selec.x_initial):(selec.x_release)].copy()

        image = rotar_imagen(image)

        cv2.imwrite(ruta, image)

        for i in range(8):
            for j in range(8):
                casillero = recortar_casillero(image, i,j)
                #areas
                matriz_numerica_t1[i][j] = detectar_pieza(casillero, 6500, 700)

        print('Tablero numerico :  \n', matriz_numerica_t1)

        origen, destino, status, _ = determinar_puntos(matriz_numerica_t0, matriz_numerica_t1, cont_peon_capturas)
        
        if status: break
    if status:
        tablero[destino[0]][destino[1]] = tablero[origen[0]][origen[1]]
        tablero[origen[0]][origen[1]] = '.'

        print("Resultado: \n Tablero leido exitosamente!\n")                
        for i in range(8):
            print(tablero[i])   
        cont_jugadas = cont_jugadas + 1

        return status, tablero, matriz_numerica_t0, matriz_numerica_t1, cont_jugadas, cont_peon_capturas
    else: 
        exit(1)

def iniciar_matrices():
    m1 = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], 
          ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], 
          ['.', '.', '.', '.', '.', '.', '.', '.'], 
          ['.', '.', '.', '.', '.', '.', '.', '.'], 
          ['.', '.', '.', '.', '.', '.', '.', '.'], 
          ['.', '.', '.', '.', '.', '.', '.', '.'], 
          ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], 
          ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]
    
    m2 = np.array([[1, 1, 1, 1, 1, 1, 1, 1],
                   [1, 1, 1, 1, 1, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [2, 2, 2, 2, 2, 2, 2, 2],
                   [2, 2, 2, 2, 2, 2, 2, 2]])
    m3 = np.zeros((8, 8), dtype=int)
    return m1.copy(),m2.copy(),m3.copy()


tablero, matriz_numerica_t0, matriz_numerica_t1 = iniciar_matrices()
matriz_numerica_mov_ia = None
cont_jugadas = 0
cont_peon_capturas = 0
ruta = os.getcwd() + '/temp.jpg'

solicitar_foto(ruta)
img2 = cv2.imread(ruta)
image2 = rotar_imagen(img2)
cv2.imwrite(ruta, image2)
calibrar(ruta)


lectura_correcta, tablero, matriz_numerica_t0, matriz_numerica_t1, cont_jugadas, cont_peon_capturas = actualizar_tablero(tablero.copy(), ruta, matriz_numerica_t0.copy(), matriz_numerica_t1.copy(), cont_jugadas, cont_peon_capturas)  
               
def test_case():
    # Carga la imagen
    imagen = cv2.imread('temp.jpg')
    cv2.imshow('Original', imagen)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    rojo = detectar_color_rojo(imagen.copy())

    cv2.imshow('Detección de Rojo', rojo)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    negro = detectar_color_negro(imagen.copy())

    cv2.imshow('Detección de negro', negro)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

