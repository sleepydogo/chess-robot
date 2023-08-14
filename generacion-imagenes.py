import requests
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.widgets as widgets
import os

class SquareSelection():
    x_initial = 0 
    y_initial = 0 
    x_release = 0 
    y_release = 0 

selec = SquareSelection()

fig = plt.figure()
ax = fig.add_subplot(111)

url_capturar = 'http://192.168.0.131/capture'
url_descargar = 'http://192.168.0.131/saved-photo'

def showImg(img, text='image'):
    cv2.namedWindow(text, cv2.WINDOW_KEEPRATIO)
    cv2.imshow(text, img)
    cv2.waitKey()
    cv2.destroyAllWindows()
    
def mostrarContornos(img,min,max, bool):
    # Aplicar deteccion de bordes utilizando Canny
    edges = cv2.Canny(img, min, max, apertureSize=3)
    if bool:
        showImg(edges, 'Detector de contornos')
    return edges

def rotarImagen(img, verbose=False):
    # Convertimos la imagen a gris
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).copy()

    if (verbose): cv2.imshow('Imagen en blanco y negro', img_gray)

    # Aplicar deteccion de bordes utilizando Canny
    edges = mostrarContornos(img_gray, 150, 300, verbose)

    if (verbose): cv2.imshow('Contornos detectados', edges)

    # Encontrar las lineas presentes en la imagen utilizando la transformada de Hough
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

    # Calcular el angulo promedio solo de las líneas horizontales detectadas
    angle = np.mean([np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]) for line in lines if abs(line[0][3] - line[0][1]) < abs(line[0][2] - line[0][0])])

    # Rotar la imagen utilizando el ángulo calculado
    (h, w) = img_gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle * 180 / np.pi, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    if (verbose): cv2.imshow('Imagen rotada', rotated)
    
    return rotated
    
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
    upper_color_black = np.array([35, 35, 35])
    mascara1 = cv2.inRange(casilla1, lower_color_black, upper_color_black).copy()
    img, contorno = encontrarContornosPieza(casilla1,mascara1,area_max, area_min)
    if verbose:
        showImg(casilla1)
        showImg(img, 'Contornos')
    if contorno > 0:
        if verbose: print('Pieza detectada')
        return 1
    else:
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([255, 255, 255])

        mascara1 = cv2.inRange(casilla1, lower_red, upper_red).copy()
        img, contorno = encontrarContornosPieza(casilla1,mascara1,area_max, area_min)

        if contorno > 0:
            if verbose: print('Pieza detectada')
            return 2
        else:
            if verbose: print('Casillero vacio')
            return 0    
        
def solicitarFoto(ruta):
    requests.get(url_capturar)
    # tarda como maximo 5 segundos en procesarla el mcu
    print("Imagen capturada, esperando a que sea procesada por el MCU\n")
    time.sleep(7)
    response = requests.get(url_descargar)
    if response.status_code == 200:
        with open(ruta, 'wb') as archivo:
            archivo.write(response.content)
        print(f'Imagen descargada como {ruta}\n')
    else:
        print('Error al descargar la imagen')


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

def tienen_mismos_numeros(array1, array2):
    conjunto1 = set(array1)
    conjunto2 = set(array2)
    return conjunto1 == conjunto2

def determinarPuntos(mov0, mov1):

    matriz_mov_tipos = np.array([[1,-1],  # mov negro 0 
                            [2,-1],  # pieza blanca come pieza negra 1 
                            [1,1],   # pieza negra come pieza blanca 2
                            [2,-2]])  # mov blanco 3 


    res = mov0 - mov1

    print(res)

    puntos = np.zeros((2,3), dtype=int)
    cont = 0

    # puntos =  [indice][res, x, y]
    for i in range(8):
        for j in range(8):
            if (res[i][j] != 0):
                print(cont)
                puntos[cont][0] = res[i][j] 
                puntos[cont][1] = i
                puntos[cont][2] = j
                cont = cont + 1

    diferencias = np.array([puntos[0][0], puntos[1][0]])

    caso = -1

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
        for i in range(2):
            if (puntos[i][0] == 2): 
                origen[0] = puntos[i][1]
                origen[1] = puntos[i][2]
            else:
                destino[0] = puntos[i][1]
                destino[1] = puntos[i][2]
    elif (caso == 2):
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
    return origen, destino

def main():

    tablero = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], 
           ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], 
           ['.', '.', '.', '.', '.', '.', '.', '.'], 
           ['.', '.', '.', '.', '.', '.', '.', '.'], 
           ['.', '.', '.', '.', '.', '.', '.', '.'], 
           ['.', '.', '.', '.', '.', '.', '.', '.'], 
           ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], 
           ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]
    
    matriz_numerica_t0 = np.array([[1, 1, 1, 1, 1, 1, 1, 1],
                                   [1, 1, 1, 1, 1, 1, 1, 1],
                                   [0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0],
                                   [2, 2, 2, 2, 2, 2, 2, 2],
                                   [2, 2, 2, 2, 2, 2, 2, 2]])
    matriz_numerica_t1 = np.zeros((8, 8), dtype=int)
            

    print("Bienvenido.. \n")
    print("Debe calibrar el tablero para empezar a usar el software...\n")
    ruta = "/home/tom/universidad/LIDI/cv-tablero/temp.jpg"
    
    while True:
        select = input("\nPresione 'r' para recalibrar manualmente \nPresione 't' para capturar las imagenes \nPresione 'q' para salir \n -- ")
        if str(select) == "t":
            print("Procesando ... \n")
            # enviamos un get para que se capture la foto
            solicitarFoto(ruta)
            image = cv2.imread(ruta)

            print("Aplicando algoritmos de computer vision ... \n Resultado \n")
            
            image = image[(selec.y_initial):(selec.y_release), (selec.x_initial):(selec.x_release)].copy()
            image = rotarImagen(image)
            for i in range(8):
                for j in range(8):
                    casillero = recortarCasillero(image, i,j)
                    matriz_numerica_t1[i][j] = detectarPieza(casillero, False, 6000, 400)

            origen, destino = determinarPuntos(matriz_numerica_t0, matriz_numerica_t1)

            tablero[destino[0]][destino[1]] = tablero[origen[0]][origen[1]]
            tablero[origen[0]][origen[1]] = '.'
            
            print(matriz_numerica_t0, matriz_numerica_t1)

            for i in range(8):
                print(tablero[i])
            
            matriz_numerica_t0 = matriz_numerica_t1.copy()
            print(matriz_numerica_t0, matriz_numerica_t1)
        elif str(select) == "r":
            while (True):
                print("Capturando imagen...\n")
                solicitarFoto(ruta)
                img2 = cv2.imread(ruta)
                image2 = rotarImagen(img2)
                cv2.imwrite(ruta, image2)
                calibrar(ruta)
                ok = input("Se ha recortado bien la imagen? \n s para si - n para no \n \t-- ") 
                if ok=='s': 
                    print(selec.x_initial, selec.y_initial, selec.x_release, selec.y_release)
                    break
        elif str(select) == "q":
            os.remove(ruta)
            print("Saliendo ...")
            return 0  

if __name__ == "__main__":
    main()

# TODO: Recalibramiento.
#       Enviar desde el esp la imagen en blanco y negro.
#       


#def detectarTableroAutomaticamente(img, borde_x=0, borde_y=0, verbose=False):
#    edges = mostrarContornos(img, 150, 300, verbose)
#
#    if (verbose): showImg(edges, 'Mascara, hsv, imagen rotada')
#
#    # Se encuentran los contornos
#    contorno,_ = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#    cont = 0
#
#    cropped_image = None
#    booleano = True
#    for c in contorno:
#        area = cv2.contourArea(c)
#        if (area > 200000):
#            cont = cont + 1
#            x,y,w,h = cv2.boundingRect(c)
#            # Recortamos el contorno encontrado.
#            if (booleano):
#                # rotamos la imagen encontrada
#                cropped_image = img[(y+borde_y):(y+h-borde_y), (x+borde_x):(x+w-borde_x)].copy()
#                if (verbose): showImg(cropped_image, "Imagen recortada")
#                booleano = False
#            area = cv2.contourArea(c)
#    
#    if ~booleano:
#        if (verbose): showImg(cropped_image, 'Imagen rotada y recortada')
#        return cropped_image
#    else:
#        return 0
