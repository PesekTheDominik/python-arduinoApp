import serial
import time

class arduino:
    def setUp(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
    
    def connectToArduino(self):
        try:
            self.ser = serial.Serial(
                self.port,
                int(self.baudrate),
                timeout=float(self.timeout)
            )
            time.sleep(2)
            return True

        except Exception as e:
            return e
        
    def closeCommunication(self):
        if self.ser and self.ser.is_open:
            self.ser.close()    

    def send(self, cmd):
        if not self.ser or not self.ser.is_open:
            return "Not connected"

        try:
            self.ser.write(f"{cmd}\n".encode())

            reply = self.ser.readline().decode().strip()

            if reply:
                return reply

            return False

        except Exception as e:
            return f"Error: {e}"     