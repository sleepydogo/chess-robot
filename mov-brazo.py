
import serial
import time
import csv
import keyboard





class RoboticArm:

    arduino = None
    data = None
    
    calibrar_STR =  'G28 \r\n'.encode()
    cerrar_STR =    'M3 \r\n'.encode()
    abrir_STR =     'M5 \r\n'.encode()
    home = 'G1 X0 Y240 Z180 \r\n'.encode()

    def create_comand(self, row, col, verbose=False):
        posx, posy = self.data[row][col].split(';')
        command = 'G1 '+ posx + ' ' + posy + ' Z80 \r\n'
        if verbose: print(command)
        return command.encode()


    def calibrar(self):
        print('calibrando...')
        self.arduino.write(self.calibrar_STR)
        message = self.arduino.readline().decode('UTF-8')
        print(message)
        message = self.arduino.readline().decode('UTF-8')
        print(message)
        time.sleep(0.5)
        return

    def abrirPinza(self): 
        self.arduino.write(self.abrir_STR)
        time.sleep(0.5)
        return

    def cerrarPinza(self): 
        self.arduino.write(self.cerrar_STR)
        time.sleep(0.5)
        return
    
    def init(self):
        def create_matrix():
            with open("rutinas-movimiento.csv", "r") as csvfile:
                csv_reader = csv.reader(csvfile)
                data = []
                for row in csv_reader:
                    data.append(row)
            return data
        
        self.arduino = serial.Serial('/dev/ttyACM0', 115200, bytesize=8, timeout=1)
        self.data = create_matrix()
        message = self.arduino.readline().decode('UTF-8')
        print(message)
        self.arduino.reset_output_buffer()
        self.abrirPinza()
        self.cerrarPinza()
        self.abrirPinza()
        self.calibrar()
        message = self.arduino.readline().decode('UTF-8')
        print(message)

    def mover(self, posx_ini, posy_ini, posx_fin, posy_fin):
        command = self.create_comand(posx_ini, posy_ini,True)
        self.arduino.write(command)
        self.arduino.write('G1 Z70'.encode())
        self.abrirPinza()
        self.cerrarPinza()
        self.arduino.write('G1 Z110'.encode())
        self.arduino.write(self.home)
        command = self.create_comand(posx_fin, posy_fin,True)
        self.arduino.write(command)
        self.arduino.write('G1 Z70'.encode())
        self.cerrarPinza()
        self.abrirPinza()
        self.arduino.write('G1 Z120'.encode())
        self.arduino.write(self.home)

    def close(self):
        self.arduino.close()
        print('Se ha cerrado la conexion serial exitosamente..')


def main():
    arm = RoboticArm()
    arm.init()
    arm.mover(6,2,4,2)
    arm.close()
    return 

if __name__ == "__main__":
    main()

