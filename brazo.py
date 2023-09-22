
import serial
import time
import csv


class RoboticArm:

    arduino = None
    data = None
    
    calibrar_STR =  'G28 \r\n'.encode()
    cerrar_STR =    'M3 \r\n'.encode()
    abrir_STR =     'M5 \r\n'.encode()
    HOME = 'G1 X0 Y240 Z180 \r\n'.encode()
    REST = 'G1 X0 Y100 Z150 \r\n'.encode()

    # Estas son las alturas a las que se posiciona la pinza
    z_superior = [85,120,130]   # por encima de la pieza
    z_inferior = [60, 70]       # lo que debe bajar para agarrarla 
    
    # Division de filas por las alturas de posicionamiento
    filas_bajas = [0,1,2]
    filas_medias = [3,4,5]
    filas_altas = [6,7]
    def create_comand(self, row, col, verbose=False):
        posx, posy = self.data[row][col].split(';')
        command = 'G1 '+ posx + ' ' + posy
        if row in self.filas_bajas: 
            command = command + ' Z85 \r\n'
        elif row in self.filas_medias: 
            command = command + ' Z120 \r\n'
        else: 
            command = command + ' Z130 \r\n'
        if verbose: print(command)
        return command.encode()


    def calibrar(self):
        print('calibrando...')
        self.arduino.write(self.calibrar_STR)
        self.arduino.readline()
        self.arduino.write(self.REST)
        self.arduino.readline()
        return

    def abrirPinza(self): 
        self.arduino.write(self.abrir_STR)
        self.arduino.readline()
        return

    def cerrarPinza(self): 
        self.arduino.write(self.cerrar_STR)
        self.arduino.readline()
        return
    
    def home(self):
        self.arduino.write(self.HOME)
        self.arduino.readline()
        time.sleep(0.5)
        self.arduino.write(self.REST)
        self.arduino.readline()

    def init(self):
        def create_matrix():
            with open("rutinas-movimiento.csv", "r") as csvfile:
                csv_reader = csv.reader(csvfile)
                data = []
                for row in csv_reader:
                    data.append(row)
            return data
        self.arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        self.data = create_matrix()
        self.arduino.reset_output_buffer()
        message = self.arduino.readline().decode('UTF-8')
        print(message)
        self.abrirPinza()
        self.cerrarPinza()
        self.abrirPinza()
        self.calibrar()
    
    def bajarPinza(self, posx_ini):
        if (posx_ini in self.filas_bajas):
            self.arduino.write()
        
    def posicionamiento_origen(self, x, y, verbose=False):
        posx, posy = self.data[x][y].split(';')
        command = 'G1 '+ posx + ' ' + posy
        if x in self.filas_bajas: 
            command = command + ' Z85 \r\n'
        elif x in self.filas_medias: 
            command = command + ' Z120 \r\n'
        else: 
            command = command + ' Z130 \r\n'
        if verbose: print(command)
        return command.encode()

    def bajarPinza(self, x):
        if x in self.filas_bajas: 
            self.arduino.write('G1 Z60 \r\n'.encode())
        else:
            self.arduino.write('G1 Z70 \r\n'.encode())


    def mover(self, posx_ini, posy_ini, posx_fin, posy_fin):
        command = self.posicionamiento_origen(posx_ini, posy_ini)
        self.arduino.write(command)
        self.arduino.readline()
        self.bajarPinza(posx_ini)
        self.arduino.readline()
        self.abrirPinza()
        self.cerrarPinza()
        self.arduino.readline()
        self.arduino.write('G1 Z160 \r\n'.encode())
        self.arduino.readline()
        command = self.posicionamiento_origen(posx_fin, posy_fin)
        self.arduino.write(command)
        self.arduino.readline()
        self.bajarPinza(posx_ini)
        self.arduino.readline()
        self.cerrarPinza()
        self.abrirPinza()
        self.arduino.readline()
        self.arduino.write('G1 Z130 \r\n'.encode())
        self.arduino.readline()
        self.home()
        return 0


    def close(self):
        self.arduino.close()
        print('Se ha cerrado la conexion serial exitosamente..')

    def sacarPieza(self, posx_ini, posy_ini):
        command = self.posicionamiento_origen(posx_ini, posy_ini)
        self.arduino.write(command)
        self.arduino.readline()
        self.bajarPinza(posx_ini)
        self.arduino.readline()
        self.abrirPinza()
        self.cerrarPinza()
        self.arduino.readline()
        self.arduino.write('G1 Z160 \r\n'.encode())
        self.arduino.readline()
        self.arduino.write('G1 X-170 Y220 \r\n'.encode())
        self.arduino.readline()
        self.home()

def main():
    arm = RoboticArm()
    arm.init()
    arm.mover(1,4,3,4)
    arm.close()
    return 

if __name__ == "__main__":
    main()

