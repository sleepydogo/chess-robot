
import serial
import time
import csv


class RoboticArm:

    SERIAL_DEV = None
    DATA = None

    CALIBRAR =  'G28 \r\n'.encode('ascii')
    CERRAR_PINZA =    'M3 \r\n'.encode('ascii')
    ABRIR_PINZA =     'M5 \r\n'.encode('ascii')
    HOME = 'G1 X0 Y240 Z180 \r\n'.encode('ascii')
    REST = 'G1 X0 Y100 Z150 \r\n'.encode('ascii')

    # Estas son las alturas a las que se posiciona la pinza
    #z_superior = [85,120,130]    por encima de la pieza
    #z_inferior = [60, 70]        lo que debe bajar para agarrarla 
    

    def create_comand(self, row, col, h, verbose=False):
        posx, posy = self.DATA[row][col].split(';')
        command = 'G1 ' +posx+ ' ' +posy+ ' Z%d \r\n' % h
        if verbose: print(command)
        return command.encode('ascii')


    def calibrar(self):
        print('Calibrando...')
        self.SERIAL_DEV.write(self.CALIBRAR)
        self.SERIAL_DEV.readline()
        self.SERIAL_DEV.write(self.REST)
        self.SERIAL_DEV.readline()
        return

    def abrirPinza(self): 
        self.SERIAL_DEV.write(self.ABRIR_PINZA)
        self.SERIAL_DEV.readline()
        return

    def cerrarPinza(self): 
        self.SERIAL_DEV.write(self.CERRAR_PINZA)
        self.SERIAL_DEV.readline()
        return
    
    def home(self):
        self.SERIAL_DEV.write(self.HOME)
        self.SERIAL_DEV.readline()
        time.sleep(0.5)
        
    def rest(self):
        self.SERIAL_DEV.write(self.REST)
        self.SERIAL_DEV.readline()
        time.sleep(0.5)
    
    def create_matrix(self):
        with open("rutinas-movimiento.csv", "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            DATA = []
            for row in csv_reader:
                DATA.append(row)
        self.DATA = DATA
        print("MATRIZ CARGADA..")

    def init(self):
        self.SERIAL_DEV = serial.Serial('/dev/ttyACM0', 9600, timeout=3.0)
        self.create_matrix()
        self.SERIAL_DEV.flush()
        message = self.SERIAL_DEV.readline().decode('UTF-8')
        print(message)
        self.cerrarPinza()
        self.abrirPinza()
        self.calibrar()

    def mover(self, posx_ini, posy_ini, posx_fin, posy_fin):
        # Posiciona en x,y a 120 de altura
        command = self.create_comand(posx_ini, posy_ini, 120)
        self.SERIAL_DEV.write(command)
        time.sleep(2)
        self.SERIAL_DEV.write('G1 Z70 \r\n'.encode('ascii'))
        self.cerrarPinza()
        if 2 >= posx_ini:
            self.SERIAL_DEV.write('G1 Z80 \r\n'.encode('ascii'))
        else:
            self.SERIAL_DEV.write('G1 Z140 \r\n'.encode('ascii'))
        time.sleep(2)
        try: 
            resp = self.SERIAL_DEV.readline().decode()
            print("Respuesta: %s " % resp)
        except:
            pass
        command = self.create_comand(posx_fin, posy_fin, 130)
        self.SERIAL_DEV.write(command)
        time.sleep(2)
        self.SERIAL_DEV.write('G1 Z70 \r\n'.encode('ascii'))
        self.abrirPinza()
        if 2 >= posx_fin:
            self.SERIAL_DEV.write('G1 Z80 \r\n'.encode('ascii'))
        else:
            self.SERIAL_DEV.write('G1 Z140 \r\n'.encode('ascii'))
        time.sleep(2)
        try: 
            resp = self.SERIAL_DEV.readline().decode()
            print("Respuesta: %s " % resp)
        except:
            pass
        self.rest()


    def close(self):
        self.SERIAL_DEV.close()
        time.sleep(5)
        print('Se ha cerrado la conexion serial exitosamente..')

    def sacarPieza(self, posx_ini, posy_ini):
        command = self.create_comand(posx_ini, posy_ini, 120)
        self.SERIAL_DEV.write(command)
        time.sleep(2)
        self.SERIAL_DEV.write('G1 Z70 \r\n'.encode('ascii'))
        self.cerrarPinza()
        self.SERIAL_DEV.write('G1 Z180 \r\n'.encode('ascii'))
        self.SERIAL_DEV.readline()
        time.sleep(0.5)
        self.home()
        self.SERIAL_DEV.write('G1 X-200 Y200 \r\n'.encode('ascii'))
        self.SERIAL_DEV.readline()
        self.abrirPinza()
        self.SERIAL_DEV.readline()
        self.rest()


# TEST: Movimiento por columnas
def test_avance_columnas(arm):
    for i in range(8):
        arm.mover(1,i,0,i)
        arm.mover(2,i,1,i)
        arm.mover(3,i,2,i)
        arm.mover(4,i,3,i)
        arm.mover(5,i,4,i)
        arm.mover(6,i,5,i)
        arm.mover(7,i,6,i)

# TEST: Avance progresivo de peones
def test_avance_peones(arm):
    for i in range(7):
        arm.mover(7-i,0,7-i-1,0)
        arm.mover(7-i,1,7-i-1,1)
        arm.mover(7-i,2,7-i-1,2)
        arm.mover(7-i,3,7-i-1,3)
        arm.mover(7-i,4,7-i-1,4)
        arm.mover(7-i,5,7-i-1,5)
        arm.mover(7-i,6,7-i-1,6)
        arm.mover(7-i,7,7-i-1,7)
        arm.calibrar()
        arm.create_matrix()
    return 0

def choca_piezas(arm):
    for i in range(7):
        print()
    return 0

def main():
    arm = RoboticArm()
    arm.init()

    arm.sacarPieza(0,0)
    


    arm.close()
    

if __name__ == "__main__":
    main()

