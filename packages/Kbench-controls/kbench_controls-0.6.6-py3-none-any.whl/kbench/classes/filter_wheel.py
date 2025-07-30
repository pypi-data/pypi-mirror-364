import serial
import time

class FilterWheel():
    def __init__(self, filter_port:str = "/dev/ttyUSB0"):
        """
        CLass to control the Thorlabs filter wheel. The wheel has 6 positions:
            - 1: ND?
            - 2: ND?
            - 3: ND?
            - 4: ND?
            - 5: ND?
            - 6: ND?

        Parameters
        ----------
        filter_port : str, optional
            Serial port number. The default is "/dev/ttyUSB2".

        Returns
        -------
        None.

        """
      
        self.session = serial.Serial(filter_port, 115200, timeout=0.1)
        
    def _purge(self):
        """
        Purge all the history of the responses of the filter wheel.
        """
        # Reading the lines actually flush the info after the request
        dummy = self.session.readlines()
    
    def close(self):
        """
        Close the serial connection.
        """
        self.session.close()    

        
    def get(self):
        """
        Get the current info from the filter wheel.

        Returns
        -------
        response : str
            Status of the wheel.

        """
        self._purge() # flush
        self.session.write("pos?\r".encode())
        response = self.session.readline().decode()
        
        return response

        
    def get_pos(self):
        """
        Returns the current position of the filter wheel.

        Returns
        -------
        slot : int
            Current position number of the wheel.

        """
        time.sleep(0.1)
        resp = self.get()
        slot = int(resp[5])
        return slot

    def move(self, slot:int):
        """
        Move the filter wheel to the specified position.

        Parameters
        ----------
        slot : int
            Position number of the wheel to reach.
        """
        print('FILT - Move to position '+str(slot))
        self.session.write(("pos="+str(slot)+"\r").encode())
        self.wait()

    
    def wait(self) -> None:
        """
        Wait for the motor to reach the target position.
        """
        position = ''
        while len(position) == 0:
            position = self.get()
            time.sleep(0.1)
