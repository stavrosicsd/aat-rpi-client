import string, requests, json, pifacecad, time, os
from SimpleCV import Color, Camera, Display

server = 'https://ase2016-group-4-1.appspot.com'
rest = server + '/api/lectures'
response = requests.get(rest)
lectures = json.loads(response.text)

l = 0
g = -1
selectedLecture = ""
selectedGroup = ""
mode = "attendance"
previousMode = "attendance"
url = ""
code = ""
previousCode = ""

def change_lecture(event):
    global l
    l = (l + 1) % len(lectures)
    lecture = get_lecture(l)['title']

    if len(lecture) > 16:
        lecture = lecture[:16]

    event.chip.lcd.clear()
    event.chip.lcd.write(lecture)

def select_lecture(event):
    global selectedLecture
    selectedLecture = get_lecture(l)['title']
    event.chip.lcd.clear()
    event.chip.lcd.write("Selected Lecture\n" + selectedLecture)

def change_group(event):
    global l, g
    g = (g + 1) % len(lectures[l]['exerciseGroups'])
    group = get_group(l, g)['title']

    if len(group) > 16:
        group = group[:16]

    event.chip.lcd.clear()
    event.chip.lcd.write(group)

def select_group(event):
    global selectedGroup, url
    selectedGroup = get_group(l, g)['title']
    url = server + get_group(l, g)['verificationUrl']
    event.chip.lcd.clear()
    event.chip.lcd.write("Selected Group\n" + selectedGroup)

def change_mode(event):
    global mode, previousMode
    previousMode = mode
    if mode == "attendance":
        mode = "presentation"
    else:
        mode = "attendance"
    event.chip.lcd.clear()
    event.chip.lcd.write("Selected Mode: \n" + mode)
    time.sleep(1)
    event.chip.lcd.clear()
    event.chip.lcd.write("Selected Group: \n" + selectedGroup)

def get_lecture(lectureIndex):
    return lectures[lectureIndex]

def get_group(lectureIndex, groupIndex):
    return get_lecture(lectureIndex)['exerciseGroups'][groupIndex]

def terminate(event):
    event.chip.lcd.clear()
    os._exit(0)

cad = pifacecad.PiFaceCAD()
cad.lcd.backlight_on()
cad.lcd.write(get_lecture(l)['title'])

listener = pifacecad.SwitchEventListener(chip=cad)
listener.register(0, pifacecad.IODIR_FALLING_EDGE, change_lecture)
listener.register(1, pifacecad.IODIR_FALLING_EDGE, select_lecture)
listener.register(2, pifacecad.IODIR_FALLING_EDGE, change_group)
listener.register(3, pifacecad.IODIR_FALLING_EDGE, select_group)
listener.register(4, pifacecad.IODIR_FALLING_EDGE, change_mode)
listener.register(5, pifacecad.IODIR_FALLING_EDGE, terminate)

listener.activate()

cam = Camera()
display = Display()

while (display.isNotDone()):
    img = cam.getImage()
    code = img.findBarcode()
    if(code is not None):
        code = str(code[0].data)
        if (selectedGroup != "" and (mode != previousMode or code != previousCode)):
            # url = string.replace(url, 'verify', 'unverify')
            u = string.replace(url, 'REPLACE_WITH_TOKEN', code)
            u = string.replace(u, 'REPLACE_WITH_MODE', mode)
            r = requests.post(u, data={}, auth=('Steve', 'dummy'))
            text_file = open("out.txt", "w")
            previousMode = mode
            previousCode = code

    img.save(display)