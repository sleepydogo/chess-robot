import cv2 
import numpy as np 
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.widgets as widgets


# Clase que implementa los algoritmos relacionados al procesamiento de imagenes para la 
# deteccion y seguimiento de piezas
class RoboticEye: 
    class Mascara: 
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([40, 40, 40])
        lower_red = np.array([0, 55, 55])
        upper_red = np.array([255, 255, 255])


    # Aplicar deteccion de bordes utilizando Canny
    def mostrar_contornos(img, min, max, debug = False):
        edges = cv2.Canny(img, min, max, apertureSize=3)
        if debug:
            cv2.imshow('Detector de contornos', edges)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return edges

    def mostrar_imagen(descripcion, image):
        cv2.imshow(str(descripcion), image)
        cv2.waitKey()
        cv2.destroyAllWindows()

    # Rotar la imagen basado en las lineas horizontales, se aplica a la imagen del tablero 
    def rotar_imagen(self, img, debug=False):
        # Convertimos la imagen a gris
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).copy()

        # Aplicar deteccion de bordes utilizando Canny
        edges = self.mostrar_contornos(img_gray, 150, 300, debug)

        # Encontrar las lineas presentes en la imagen utilizando la transformada de Hough
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

        # Calcular el angulo promedio solo de las líneas horizontales detectadas
        angle = np.mean([np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]) for line in lines if abs(line[0][3] - line[0][1]) < abs(line[0][2] - line[0][0])])

        # Rotar la imagen utilizando el ángulo calculado
        (h, w) = img_gray.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle * 180 / np.pi, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        if (debug): 
            self.mostrar_imagen('Imagen en blanco y negro', img_gray)
            self.mostrar_imagen('Imagen rotada', rotated)
            self.mostrar_imagen('Contornos detectados', edges)
        return rotated
    
    # Recibe como argumento la imagen del tablero y una posicion (i,j) del casillero que se desea recortar
    def recortar_casillero(image, i, j):
        width = image.shape[1]
        height = image.shape[0]
        start_y = int((height/8)*i)
        end_y = int((height/8)*i+(height/8))
        start_x = int((width/8)*j)
        end_x = int((width/8)*j+(width/8))
        casillero = image[start_y:end_y, start_x:end_x].copy()
        return casillero

    # Recibe como parametro la imagen de un casillero, una mascara y un area minima y maxima. En base a esto detecta contornos que cumplen con las condiciones de area luego de aplicada la mascara.
    def encontrar_contornos_pieza(self, image, mask, area_max=6000, area_min=200, debug = False):
        img_pieza = image.copy()
        contorno,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        grid_contours = []   
        for contour in contorno:
            if area_max > cv2.contourArea(contour) > area_min:
                grid_contours.append(contour)

        cv2.drawContours(img_pieza, grid_contours, -1, (0, 255, 0), 2)
        
        if (debug): self.mostrar_imagen('Contorno de pieza', img_pieza)

        return len(grid_contours)


    # Recibe por parametro un recorte de un casillero, aplica 2 mascaras que resaltan el color negro y rojo respectivamente y luego aplica un canny a las imagenes con las mascaras, retorna una lista de contornos los cuales estan comprendidos entre area maxima y area minima.
    def detectar_pieza(self, img_casillero, verbose=False, area_max=2000, area_min=800):
        mascara = cv2.inRange(img_casillero, self.Mascara.lower_black, self.Mascara.upper_black).copy()
        contorno = self.encontrar_contornos_pieza(img_casillero, mascara, area_max, area_min)
        
        if verbose: self.mostrar_imagen("Casillero recortado: ", img_casillero)
       
        if contorno > 0:
            if verbose: print('Pieza detectada')
            return 1
        else:
            mascara = cv2.inRange(img_casillero, self.Mascara.lower_red, self.Mascara.upper_red).copy()
            contorno = self.encontrar_contornos_pieza(img_casillero,~mascara,area_max, area_min)

            if contorno > 0:
                if verbose: print('Pieza detectada')
                return 2
            else:
                if verbose: print('Casillero vacio')
                return 0    