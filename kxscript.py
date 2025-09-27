import pyautogui, time, datetime
import pyperclip

# Example absolute coordinates (replace with your own)
FIRST = (283, 286)
LAST  = (430, 286)
ID    = (297, 238)
ROOM  = (256, 582)
DESC  = (100, 420)
CHROME = (961, 1056)

def copy_field(pos, triple=False):
    pyautogui.moveTo(*pos, duration=0.05)
    clicks = 3 if triple else 2
    pyautogui.click(clicks=clicks)
    time.sleep(0.05)
    pyautogui.hotkey('ctrl','c')
    time.sleep(0.05)
    return pyperclip.paste()

first = copy_field(FIRST)
last  = copy_field(LAST)
sid   = copy_field(ID)
room  = copy_field(ROOM)

current_time = datetime.datetime.now().strftime("%H:%M")

template = f"""Student's full name: {first.strip()} {last.strip()}
Room: {room.strip()}
HWU ID: {sid.strip()}
Granted access by: RLW Tim
Granted access at: {current_time}"""

pyautogui.moveTo(*CHROME, duration=0.1)
pyautogui.click()
pyautogui.moveTo(*DESC, duration=0.1)
pyautogui.click()
time.sleep(0.05)
pyautogui.write(template, interval=0.003)
