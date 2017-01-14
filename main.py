import requests
import json
import pifacecad
import time
import os

response = requests.get('https://ase2016-cb66d.firebaseio.com/groups.json')
root = json.loads(response.text)

i = 0
selectedGroup = ""
mode = "Attendance"

def change_group(event):
    global i
    i = (i + 1) % len(root['group'])
    group = get_group(i)

    if len(group) > 16:
        group = group[:16]

    event.chip.lcd.clear()
    event.chip.lcd.write(group)

def select_group(event):
    global selectedGroup
    selectedGroup = get_group(i)
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
    time.sleep(1)
    event.chip.lcd.clear()
    event.chip.lcd.write("Selected Group: \n" + selectedGroup)

def get_group(index):
    return root['group'][index]['title']

def terminate(event):
    event.chip.lcd.clear()
    os._exit(0)

cad = pifacecad.PiFaceCAD()
cad.lcd.backlight_on()
cad.lcd.write(get_group(i))

listener = pifacecad.SwitchEventListener(chip=cad)
listener.register(0, pifacecad.IODIR_FALLING_EDGE, change_group)
listener.register(1, pifacecad.IODIR_FALLING_EDGE, select_group)
listener.register(2, pifacecad.IODIR_FALLING_EDGE, change_mode)
listener.register(4, pifacecad.IODIR_FALLING_EDGE, terminate)

listener.activate()