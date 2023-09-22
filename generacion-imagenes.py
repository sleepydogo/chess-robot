import requests
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.widgets as widgets
import os
import chess, chess.engine

from brazo import RoboticArm

class SquareSelection():
    x_initial = 0 
    y_initial = 0 
    x_release = 0 
    y_release = 0 

class Esp32cam():
    ip_esp = None
    url_capturar =  None
    url_descargar = None

selec = SquareSelection()
mcu = Esp32cam()

fig = plt.figure()
ax = fig.add_subplot(111)
   
def mostrar_contornos(img,min,max, bool):
    # Aplicar deteccion de bordes utilizando Canny
    edges = cv2.Canny(img, min, max, apertureSize=3)
    if bool:
        cv2.imshow('Detector de contornos', edges)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return edges

def rotar_imagen(img, verbose=False):
    # Convertimos la imagen a gris
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).copy()

    if (verbose): 
        cv2.imshow('Imagen en blanco y negro', img_gray)
        cv2.waitKey()
        cv2.destroyAllWindows()

    # Aplicar deteccion de bordes utilizando Canny
    edges = mostrar_contornos(img_gray, 150, 300, verbose)

    if (verbose): 
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

    if (verbose): 
        cv2.imshow('Imagen rotada', rotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return rotated
    
def recortar_casillero(image, i, j):
    width = image.shape[1]
    height = image.shape[0]
    start_y = int((height/8)*i)
    end_y = int((height/8)*i+(height/8))
    start_x = int((width/8)*j)
    end_x = int((width/8)*j+(width/8))
    casillero = image[start_y:end_y, start_x:end_x].copy()
    return casillero

def encontrar_contornos_pieza(image, mask, area_max=6000, area_min=200):
    retorno = image.copy()
    contorno,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    grid_contours = []   
    for contour in contorno:
        if area_max > cv2.contourArea(contour) > area_min:
            grid_contours.append(contour)

    cv2.drawContours(retorno, grid_contours, -1, (0, 255, 0), 2)
    return retorno, len(grid_contours)

def detectar_pieza(casilla1, verbose=False, area_max=2000, area_min=200):
    lower_color_black = np.array([0, 0, 0])
    upper_color_black = np.array([35, 35, 35])
    mascara1 = cv2.inRange(casilla1, lower_color_black, upper_color_black).copy()
    img, contorno = encontrar_contornos_pieza(casilla1,mascara1,area_max, area_min)
    if verbose:
        cv2.imshow("Casillero recortado: ", casilla1)
        cv2.waitKey(0)
        cv2.destroyAllWindows()        
    if contorno > 0:
        if verbose: print('Pieza detectada')
        return 1
    else:
        lower_red = np.array([0, 45, 45])
        upper_red = np.array([255, 255, 255])

        mascara1 = cv2.inRange(casilla1, lower_red, upper_red).copy()
        img, contorno = encontrar_contornos_pieza(casilla1,~mascara1,area_max, area_min)

        if contorno > 0:
            if verbose: print('Pieza detectada')
            return 2
        else:
            if verbose: print('Casillero vacio')
            return 0    
              
def solicitar_foto(ruta):
    requests.get(mcu.url_capturar)
    print("Imagen capturada, esperando a que sea procesada por el MCU\n")
    time.sleep(7)
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
                    return None, None, False
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

def matriz_a_fen(tablero):
    fen = ""
    for fila in tablero:
        vacios = 0
        for celda in fila:
            if celda == ".":
                vacios += 1
            else:
                if vacios > 0:
                    fen += str(vacios)
                    vacios = 0
                fen += celda
        if vacios > 0:
            fen += str(vacios)
        fen += "/"
    fen = fen[:-1]  # Eliminar la barra diagonal final
    return fen

def mejor_movimiento(fen):
    engine = chess.engine.SimpleEngine.popen_uci(os.getcwd() + "/Stockfish/src/stockfish")
    tablero = chess.Board(fen)
    result = engine.play(tablero, chess.engine.Limit(time=2.0))  
    print("Movimiento a realizar --> " + str(result.move) + "\n")
    engine.quit()
    return result

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

def actualizar_tablero(tablero, ruta, matriz_numerica_t0, matriz_numerica_t1, cont_jugadas, cont_peon_capturas, debug=False):
    print("Procesando ... \n")
    for i in range(5):  
        print("Intento " + str(i) + "\n")
        solicitar_foto(ruta)
        image = cv2.imread(ruta)

        print("Aplicando algoritmos de computer vision ... \n Resultado \n")
        image = rotar_imagen(image)
        image = image[(selec.y_initial):(selec.y_release), (selec.x_initial):(selec.x_release)].copy()

        for i in range(8):
            for j in range(8):
                casillero = recortar_casillero(image, i,j)
                matriz_numerica_t1[i][j] = detectar_pieza(casillero, False, 6000, 600)

        print('Tablero numerico :  \n', matriz_numerica_t1)

        origen, destino, status = determinar_puntos(matriz_numerica_t0, matriz_numerica_t1, cont_peon_capturas)
        
        if status: break
        if i == 4 and not status: 
            print("Ha fallado el reconocimiento.. Intente recalibrando \n")
            break
    if status:
        tablero[destino[0]][destino[1]] = tablero[origen[0]][origen[1]]
        tablero[origen[0]][origen[1]] = '.'

        print("Resultado: \n Tablero leido exitosamente!\n")                
        for i in range(8):
            print(tablero[i])   
        cont_jugadas = cont_jugadas + 1

        return status, tablero, matriz_numerica_t0, matriz_numerica_t1, cont_jugadas, cont_peon_capturas

def tablero_a_matriz_numerica(tablero):
    matriz = np.zeros((8, 8), dtype=int)
    matriz2 = np.zeros((8, 8), dtype=str)
    cont = 0
    for i in range(0, len(tablero.__str__()), 2):
        if (tablero.__str__()[i].isalpha()):
            if (tablero.__str__()[i].isupper()):
                matriz[i//16][cont] = 2
            elif (tablero.__str__()[i].islower()):
                matriz[i//16][cont] = 1
            matriz2[i//16][cont] = "."
        matriz2[i//16][cont] = tablero.__str__()[i]
        cont = cont + 1 
        if (cont == 8): cont = 0
    return matriz, matriz, matriz2

def extraer_contadores_string_fen(fen):
    parts = fen.split('-')
    number_list = parts[1].split()
    numbers = [int(number) for number in number_list]
    return numbers[0],numbers[1] 


def main():
    debug = False        

    print(f"""
      ____       _           _   _                 ____ _                   
     |  _ \ ___ | |__   ___ | |_(_) ___           / ___| |__   ___  ___ ___ 
     | |_) / _ \| '_ \ / _ \| __| |/ __|  _____  | |   | '_ \ / _ \/ __/ __|
     |  _ < (_) | |_) | (_) | |_| | (__  |_____| | |___| | | |  __/\__ \__ \\
     |_| \_\___/|_.__/ \___/ \__|_|\___|          \____|_| |_|\___||___/___/

          
    ---------------------- sleepydogo, v1.1 ---------------------------------
          """)
    print("Bienvenido.. \n")
    print("Debe calibrar el tablero para empezar a usar el software...\n")
    #desahilitado para las pruebas, TODO: activar
    #mcu.ip_esp = input("Ingrese el ip del ESP32-cam: ")
    mcu.ip_esp = "192.168.0.131"
    mcu.url_capturar = 'http://'+ str(mcu.ip_esp)+ '/capture'
    mcu.url_descargar = 'http://'+ str(mcu.ip_esp)+ '/saved-photo'
    try: 
        print("Intentando establecer conexion con el dispositivo ...\n")
        response = requests.get(mcu.url_capturar)
        time.sleep(2)
    except requests.exceptions.RequestException as e:
        print("No se ha podido establecer conexion con el MCU ...\n")
        return 0
    print("Se ha establecido la conexion correctamente!\n")        
    ruta = os.getcwd() + "/temp.jpg"
    
    while True:
        select = input(" \n--Menu: \n r - para recalibrar manualmente \n j - para jugar \n d - activar o desactivar el modo debugger \n q - para salir\n \n -- ")
        if select == 'j':
            arm = RoboticArm()
            arm.init()
            tablero, matriz_numerica_t0, matriz_numerica_t1 = iniciar_matrices()
            matriz_numerica_mov_ia = None
            cont_jugadas = 0
            cont_peon_capturas = 0
            chessboard = chess.Board()
            while (True):
                captura = input("Presione enter para capturar el tablero, 'q' para salir \n")    
                if captura == "q":
                    os.remove(ruta)
                    print("Saliendo ...")
                    arm.close()
                    break
                # Procesamiento jugada roja
                # Leo el tablero
                lectura_correcta, tablero, matriz_numerica_t0, matriz_numerica_t1, cont_jugadas, cont_peon_capturas = actualizar_tablero(tablero.copy(), ruta, matriz_numerica_t0.copy(), matriz_numerica_t1.copy(), cont_jugadas, cont_peon_capturas, debug)  
                if (lectura_correcta):
                    matriz_numerica_mov_ia = matriz_numerica_t1
                    # Lo transformo a fen
                    fen = matriz_a_fen(tablero) + str(" b KQkq - " + str(cont_peon_capturas) + " " + str(cont_jugadas))
                    print(fen)
                    chessboard = chess.Board(fen)
                    # Ingreso el string fen al chess engine
                    move = mejor_movimiento(fen)
                    # Pusheo el movimiento al tablero 
                    chessboard.push_san(str(move.move))
                    matriz_numerica_t0, matriz_numerica_t1, tablero  = tablero_a_matriz_numerica(chessboard)
                    print('matriz numerica 0: ', matriz_numerica_mov_ia)
                    print('matriz numerica 1: ', matriz_numerica_t1)
                    cont_peon_capturas, cont_jugadas = extraer_contadores_string_fen(chessboard.fen())
                    for i in range(8):
                        print(tablero[i])
                    origen, destino, status, captura = determinar_puntos(matriz_numerica_mov_ia, matriz_numerica_t1)
                    print('ORIGEN BRAZO: ', origen,'\n DESTINO  BRAZO: ', destino)
                    if captura:
                        arm.sacarPieza(7-destino[0], 7-destino[1])
                    arm.mover(7-origen[0], 7-origen[1], 7-destino[0], 7-destino[1])
                else: 
                    os.remove(ruta)
                    print("Saliendo ...")
                    arm.close()
                    break
        elif select == "r":
            while (True):
                print("Capturando imagen...\n")
                solicitar_foto(ruta)
                img2 = cv2.imread(ruta)
                image2 = rotar_imagen(img2)
                cv2.imwrite(ruta, image2)
                calibrar(ruta)
                ok = input("Se ha recortado bien la imagen? \n s para si - n para no \n \t-- ") 
                if ok=='s': 
                    print(selec.x_initial, selec.y_initial, selec.x_release, selec.y_release)
                    break
        elif select == "d":
            if debug: 
                debug = False
                print("Debug desactivado\n")
            else: 
                debug = True
                print("Debug activado\n")
        elif select == "q":
            print("Saliendo ...")
            break
    return 0  
        

if __name__ == "__main__":
    main()