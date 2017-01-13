import requests
import json
import pifacecad
import time

response = requests.get('https://ase2016-cb66d.firebaseio.com/greetings.json')
root = json.loads(response.text)

i = 0
selectedGroup = ""
mode = "Attendance"

def change_group(event):
    global i
    i = (i + 1) % len(root['greeting'])
    greeting = root['greeting'][i]['content']

    if len(greeting) > 16:
        greeting = greeting[:16]

    event.chip.lcd.clear()
    event.chip.lcd.write(greeting)

def select_group(event):
    global selectedGroup
    selectedGroup = root['greeting'][i]['content']
    event.chip.lcd.clear()
    event.chip.lcd.write("Selected Group: \n" + selectedGroup)

def change_mode(event):
    global mode
    if mode == "Attendance":
        mode = "Presentation"
    else:
        mode = "Attendance"
    event.chip.lcd.clear()
    event.chip.lcd.write("Selected Mode: \n" + mode)
    time.sleep(3)
    event.chip.lcd.clear()
    event.chip.lcd.write("Selected Group: \n" + selectedGroup)

cad = pifacecad.PiFaceCAD()
cad.lcd.backlight_on()
cad.lcd.write(root['greeting'][i]['content'])

listener = pifacecad.SwitchEventListener(chip=cad)
listener.register(0, pifacecad.IODIR_FALLING_EDGE, change_group)
listener.register(1, pifacecad.IODIR_FALLING_EDGE, select_group)
listener.register(4, pifacecad.IODIR_FALLING_EDGE, change_mode)
listener.activate()