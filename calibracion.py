import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.widgets as widgets


fig = plt.figure()
ax = fig.add_subplot(111)


class SquareSelection():
    x_initial = 0 
    y_initial = 0 
    x_release = 0 
    y_release = 0 

selec = SquareSelection()

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

def calibrar(filename):
    input(" Seleccione en la imagen el tablero ...")
    im = Image.open(filename)
    arr = np.asarray(im)
    plt_image = plt.imshow(arr)
    rs = widgets.RectangleSelector(
        ax, onselect, interactive=True,
        props = dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True))
    plt.show()

calibrar("/home/tom/universidad/LIDI/cv-tablero/tom.jpg")

