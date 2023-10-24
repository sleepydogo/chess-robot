
import cv2

def mostrar_contornos(img,min,max, bool):
    # Aplicar deteccion de bordes utilizando Canny
    edges = cv2.Canny(img, min, max, apertureSize=3)
    if bool:
        cv2.imshow('Detector de contornos', edges)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()
    return edges