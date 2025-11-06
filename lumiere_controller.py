# lumiere_controller.py
import time
import flux_led
import multiprocessing

led = flux_led.WifiLedBulb("192.168.1.16")

def effet_lumiere(style):
    if style == "bleu doux":
        led.setRgb(0, 0, 255)
    elif style == "flash intense":
        for _ in range(5):
            led.turnOn()
            led.setRgb(255, 255, 255, brightness=100)
            time.sleep(0.2)
            led.turnOff()
            time.sleep(0.2)
    elif style == "double flash":
        for _ in range(2):
            led.turnOn()
            led.setRgb(255, 255, 0)
            time.sleep(0.3)
            led.turnOff()
            time.sleep(0.3)

def run_lumiere(queue):
    while True:
        if not queue.empty():
            style = queue.get()
            if style == "STOP":
                break
            effet_lumiere(style)
        time.sleep(0.1)

