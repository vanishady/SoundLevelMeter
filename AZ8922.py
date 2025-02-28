import threading
import time
import math

import serial  #Hay que tener instalado la librería PySerial


#Listado de colores para que el texto salga bonito por pantalla.
Red = '\033[91m'
Green = '\033[92m'
Blue = '\033[94m'
Cyan = '\033[96m'
White = '\033[97m'
Yellow = '\033[93m'
Magenta = '\033[95m'
Grey = '\033[90m'
Black = '\033[90m'
Default = '\033[99m'
#You can chain these to get different colors on the same line.
#print('\033[91m' + 'Red  ' + "\033[95m" + 'Magenta  ' + '\033[94m' + 'Blue')
#print(Red + 'Red  ' + Magenta + 'Magenta  ' + Blue + 'Blue  ')

class AZ8922:

    def __init__(self, port):
        self.port = port
        self.ser = None
        self.running = True
        self.connected = True
        self.sound_level = []
        print(Red +"AZ8922: Iniciando la clase.\n",flush=True)

    def get_sonometry(self):
        if self.sound_level:
            sound_level_max = max(self.sound_level)
            sound_level_linear = [math.pow(10,x/20) for x in self.sound_level] 
            sound_level_mean = sum(sound_level_linear) / len(sound_level_linear) 
            sound_level_mean = 20*math.log10(sound_level_mean) 
        else:
            sound_level_max = -1
            sound_level_mean = -1
            
        # Check if the AZ8922 is off.
        # if self.connected and not self.sound_level: logging.warning('AZ8922 is off.')
        
        # Reset the arrays.
        self.sound_level = []
        
        # Round up.
        sound_level_mean = round(sound_level_mean,2)
        
        # logging.info(f'Sonometry AZ8922:{sound_level_mean}') 
        # logging.info('Sonometry AZ8922:%f' % sound_level_mean) 
        # if not self.connected: logging.warning('AZ8922 is disconnected.')
         
        return sound_level_mean, sound_level_max

    def run_thread(self):
        thread = threading.Thread(target=self.sonometro_thread, daemon=True)
        thread.start()

    def stop_thread(self):
        self.running = False
        self.connected = False
        if self.ser is not None: 
            self.ser.close()
            print(Red+"RS232 cerrando el puerto serie.\n",flush=True)
            
    def sonometro_thread(self):
        while self.running:
            try:
                # If disconnected, check connection every 5 seconds.
                if not self.connected: time.sleep(5)
                self.ser = serial.Serial(self.port, 2400, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
                self.connected = True
                print(Red +"RS232 abriendo el puerto serie.\n",flush=True)

                #while(self.connected and self.ser.in_waiting and self.running):
                while(self.connected and self.running):
                    output = self.ser.readline().decode('utf-8', 'ignore')
                    output = output.strip()
                    print(Red +"RS232 read data:"+str(output)+"\n",flush=True)
                    if output.startswith('N:') and output.endswith('dB'):
                        self.sound_level.append(float(output.split(':')[1].split('dB')[0]))

            except (serial.serialutil.SerialException, OSError):
                # Thread is not halted upon sensor disconnection.
                self.connected = False
