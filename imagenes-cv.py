import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.widgets as widgets

class SquareSelection():
    x_initial = 0 
    y_initial = 0 
    x_release = 0 
    y_release = 0 

selec = SquareSelection()

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

# casilla1 : imagen recortada del casillero 
# verbose : imprime las imagenes de los casilleros con los filtros aplicados y contornos detectados
# white : es un booleano, true para detectar piezas rojas, false para piezas negras
def detectar_pieza(casilla1, verbose=False, area_max=2000, area_min=200):
    lower_color_black = np.array([0, 0, 0])
    upper_color_black = np.array([35, 35, 35])
    mascara1 = cv2.inRange(casilla1, lower_color_black, upper_color_black).copy()
    img, contorno = encontrar_contornos_pieza(casilla1,mascara1,area_max, area_min)
    if verbose:
        cv2.imshow(casilla1)
        cv2.imshow(img, 'Contornos')
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