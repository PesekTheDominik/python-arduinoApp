import serial
import time

class arduino:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
    
    def connectToArduino(self):
        self.ser = serial.Serial(self.port, int(self.baudrate), timeout=float(self.timeout))
        time.sleep(2)

    def TestCmd(self, cmd):
        if not self.ser:
            return 1
        
        