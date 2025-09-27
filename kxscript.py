import pyautogui, time, datetime

# Example absolute coordinates (replace with your own)
FIRST = (283, 286)
LAST  = (410, 220)
ID    = (190, 200)
ROOM  = (230, 600)
DESC  = (620, 340)

def copy_field(pos, triple=False):
    pyautogui.moveTo(*pos, duration=0.25)
    clicks = 3 if triple else 2
    pyautogui.click(clicks=clicks)
    time.sleep(0.15)
    pyautogui.hotkey('ctrl','c')
    time.sleep(0.15)
    return pyautogui.paste()  # requires pyperclip or python3.10+ on some OS; safer: import pyperclip

first = copy_field(FIRST)
last  = copy_field(LAST)
sid   = copy_field(ID)
room  = copy_field(ROOM)

template = f"""Student's full name: {first.strip()} {last.strip()}
Room: {room.strip()}
HWU ID: {sid.strip()}
Granted access by: RLW Tim
Granted access at: {datetime.datetime.now():%Y-%m-%d %H:%M}"""

pyautogui.moveTo(*DESC, duration=0.3)
pyautogui.click()
time.sleep(0.1)
pyautogui.hotkey('ctrl','a')
time.sleep(0.05)
pyautogui.write(template, interval=0.003)
