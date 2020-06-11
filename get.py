import RPi.GPIO as GPIO
import time
from time import sleep
import pyaudio
import wave
import os
import sys
import smbus
trig=17
button1=5
button2=6
light1=13
light2=19
class MLX90614():
    MLX90614_TA=0x06
    MLX90614_TOBJ1=0x07
    MLX90614_TOBJ2=0x08
    comm_retries = 5
    comm_sleep_amount = 0.1
    def __init__(self, address=0x5a, bus_num=1):
        self.bus_num = bus_num
        self.address = address
        self.bus = smbus.SMBus(bus=bus_num)
    def read_reg(self, reg_addr):
        for i in range(self.comm_retries):
            try:
                return self.bus.read_word_data(self.address, reg_addr)
            except IOError as e:
                sleep(self.comm_sleep_amount)
    def get_amb_temp(self):
        data = self.read_reg(self.MLX90614_TA)
        return (data*0.02) - 273.15
    def get_obj_temp(self):
        data = self.read_reg(self.MLX90614_TOBJ1)
        return (data*0.02) - 273.15
def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(trig,GPIO.OUT,initial=GPIO.HIGH)
    GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(light1, GPIO.OUT)
    GPIO.output(light1, GPIO.HIGH)
    GPIO.setup(light2, GPIO.OUT)
    GPIO.output(light2, GPIO.HIGH)
    pass
def beep(seconds):
    GPIO.output(trig,GPIO.LOW) 
    time.sleep(seconds)
    GPIO.output(trig,GPIO.HIGH) 
def beepBatch(seconds,timespan,counts):
    for i in range(counts):
        beep(seconds)
        time.sleep(timespan)
def record(button,count):
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 10
    if button==5:
         WAVE_OUTPUT_FILENAME = "data"+str(count)+".wav"
    else:
         WAVE_OUTPUT_FILENAME = str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+".wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    print("recording...")
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if GPIO.input(button) == 1:
            break;
    print("done")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
init()
#beep(0.1)
beepBatch(0.1,0.3,3)
sensor = MLX90614()
if os.path.exists('data.txt'):
    size = os.path.getsize('data.txt')
    if  size == 0:
        count = 1
    else:
        find = open("data.txt","r+")
        lines = find.readlines()
        count = int(lines[-1][0]) + 1
        find.close()
else:
    count = 1
while True:
    if GPIO.input(button1) == 0:
        GPIO.output(light1, GPIO.LOW)
        file = open("data.txt","a+")
        file.write(str(count)+' '+str(sensor.get_obj_temp())+' '+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+'\n')
        file.close()
        record(button1,count)
        count+=1
        beep(0.1)
    else:
        GPIO.output(light1, GPIO.HIGH)
    if GPIO.input(button2) == 0:
        GPIO.output(light2, GPIO.LOW)
        record(button2,0)
        beep(0.1)
    else:
        GPIO.output(light2, GPIO.HIGH)
GPIO.cleanup()