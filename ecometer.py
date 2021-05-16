##
##
## ECOMETER S to MQTT - https://www.e-sensorix.io/en/sensors/proteus-ecometer-s-level-measurement-in-rainwater-tank-and-cistern
##
##
## Magnus Nilsson 2021
##
## Based on Martin's (@mafl) code from https://www.python-forum.de/viewtopic.php?t=48402
##
## Further based on the findings of Markus Fritze from https://sarnau.info/communication-protocol-of-the-proteus-ecometer-tek603/
##
##

#!/usr/bin/env python3
import datetime
import logging
import threading
import os
import serial
import struct
import paho.mqtt.client as mqtt

broker = '192.168.X.XX'
port = 1883
topic_1 = "homeassistant/bajstank"
topic_2 = "homeassistant/bajstank_temp"
username = 'mqtt'
password = 'XXXX'

# Define the interface
ECOMETER_SERIAL_PORT = "/dev/ttyUSB0"

ECOMETER_LOG_FILENAME = "ecometer.log"

ITEM_NAMES = [
    "Time",
    "Temp_F",
    "Temp_C",
    "Ullage",
    "UseableLevel",
    "UseableCapacity",
    "UseablePercent",
    "Timestamp",
]

def setup_logger():
    logger = logging.getLogger("Ecometer_Log")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(ECOMETER_LOG_FILENAME)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(file_handler)
    return logger

LOGGER = setup_logger()

#Lite mer MQTT
client = mqtt.Client()
client.username_pw_set(username, password)

class MyEcometer(threading.Thread):
    ecometer_result = []

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):        
        with serial.Serial(ECOMETER_SERIAL_PORT, 115200) as connection:
            while True:                
                # Make sure that are no old bytes left in the input buffer.             
                connection.reset_input_buffer()
                #print("Waiting for data")
                data = connection.read(22)
                #print("Data was receive")
                (magic, _length, _command, _flags,
                    hour, minute, second, _start, _end,
                    temperature, ul_lage, usable_level, capacity, _crc
                ) = struct.unpack(">2shbb3bhhb4h", data)
                if magic == b'SI':
                    result = [
                        {
                            'name' : ITEM_NAMES[0],
                            'value' : f"{hour:02d}:{minute:02d}:{second:02d}"
                        },
                        {
                            'name' : ITEM_NAMES[1],
                            'value' : temperature
                        },
                        {
                            'name' : ITEM_NAMES[2],
                            'value' : (temperature - 40 - 32) / 1.8
                        },
                        {
                            'name' : ITEM_NAMES[3],
                            'value' : ul_lage
                        },
                        {
                            'name' : ITEM_NAMES[4],
                            'value' : usable_level
                        },
                        {
                            'name' : ITEM_NAMES[5],
                            'value' : capacity
                        },
                        {
                            'name' : ITEM_NAMES[6],
                            'value' : usable_level / capacity * 100.01
                        },
                        {
                            'name' : ITEM_NAMES[7],
                            'value' : datetime.datetime.now().timestamp()
                        }
                    ]
                    
                    temp_celsius = (temperature - 40 - 32) / 1.8
                                     
                    client.connect(broker, port)                    
                    client.publish(topic_1, usable_level)
                    client.publish(topic_2, temp_celsius)

                    #Lite logging
                    LOGGER.info(result)
                    #print(usable_level)
                    #print(temp_celsius)

def main():
    my_ecometer = MyEcometer()
    my_ecometer.start()

if __name__ == "__main__":
    main()
