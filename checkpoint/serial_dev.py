
# author: sleepydogo

class ESP32CAM: 
    IP = None
    URL_CAPTURE = '/capture'
    URL_DOWNLOAD = '/saved-photo'
    
    def init(self, ip):
        self.IP = ip