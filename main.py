import string, requests, json, pifacecad, time, os
from SimpleCV import Color, Camera, Display

server = 'https://ase2016-group-4-1.appspot.com'
rest = server + '/api/lectures'
response = requests.get(rest)
lectures = json.loads(response.text)

l = -1
g = -1
selectedLecture = ""
selectedGroup = ""
mode = "attendance"
previousMode = "attendance"
url = ""
code = ""
previousCode = ""
urls = []

cad = pifacecad.PiFaceCAD()
cad.lcd.backlight_on()

def select_lecture(event):
    global l, g, selectedLecture, selectedGroup
    l = (l + 1) % len(lectures)
    selectedLecture = get_lecture(l)['title']
    g = -1
    selectedGroup = ""
    display_main()

def select_group(event):
    global l, g, selectedGroup, url
    if(l != -1):
        g = (g + 1) % len(lectures[l]['exerciseGroups'])
        selectedGroup = get_group(l, g)['title']
        url = server + get_group(l, g)['verificationUrl']
        display_main()

def display_main():
    message = ""
    if(selectedLecture != ""):
        message = selectedLecture
    else:
        message = "No lecture"

    if (selectedGroup != ""):
        message = message + "\n" + selectedGroup
    else:
        message = message + "\n" + "No group"
    cad.lcd.clear()
    cad.lcd.write(message)

def change_mode(event):
    global mode, previousMode
    previousMode = mode
    if mode == "attendance":
        mode = "presentation"
    else:
        mode = "attendance"
    writeAndReload("Mode:\n" + mode)

def get_lecture(lectureIndex):
    return lectures[lectureIndex]

def get_group(lectureIndex, groupIndex):
    return get_lecture(lectureIndex)['exerciseGroups'][groupIndex]

def server_is_accessible():
    try:
        r = requests.get(server)
        r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
        return False
    else:
        return True

def print_server_is_accessible(event):
    if (server_is_accessible):
        writeAndReload("Server is \naccessible")
    else:
        writeAndReload("Server is not \naccessible")

def terminate(event):
    event.chip.lcd.clear()
    os._exit(0)

def writeAndReload(message):
    cad.lcd.clear()
    cad.lcd.write(message)
    time.sleep(2)
    display_main()

display_main()

listener = pifacecad.SwitchEventListener(chip=cad)
listener.register(0, pifacecad.IODIR_FALLING_EDGE, select_lecture)
listener.register(1, pifacecad.IODIR_FALLING_EDGE, select_group)
listener.register(2, pifacecad.IODIR_FALLING_EDGE, change_mode)
listener.register(3, pifacecad.IODIR_FALLING_EDGE, print_server_is_accessible)
listener.register(4, pifacecad.IODIR_FALLING_EDGE, terminate)

listener.activate()

cam = Camera()
display = Display()

while (display.isNotDone()):
    img = cam.getImage()
    code = img.findBarcode()
    if(code is not None):
        code = str(code[0].data)
        if (selectedLecture != "" and selectedGroup != "" and (mode != previousMode or code != previousCode)):
            if(mode == "attendance"):
                writeAndReload("Attended!")
            else:
                writeAndReload("Presented!")
            # url = string.replace(url, 'verify', 'unverify')
            u = string.replace(url, 'REPLACE_WITH_TOKEN', code)
            u = string.replace(u, 'REPLACE_WITH_MODE', mode)
            urls.append(u)
            text_file = open("out.txt", "w")
            text_file.write(u)
            text_file.close()
            if(server_is_accessible):
                for ur in urls:
                    r = requests.post(ur, data={}, auth=('Steve', 'dummy'))
                    text_file = open("out.txt", "w")
                    text_file.write('' + str(r.status_code))
                    text_file.close()
                    urls.remove(ur)
            previousMode = mode
            previousCode = code
        elif(selectedLecture == "" and selectedGroup == ""):
            writeAndReload("Please select\nlecture & group!")
        elif(selectedLecture == ""):
            writeAndReload("Please select\na lecture!")
        elif (selectedGroup == ""):
            writeAndReload("Please select\na group!")
        elif(mode == previousMode and code == previousCode):
            if(mode == "attendance"):
                writeAndReload("Already attended!")
            else:
                writeAndReload("Already presented!")
    img.save(display)