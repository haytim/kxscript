import pyautogui, time, datetime, re
import pyperclip
from pynput import keyboard

# Coordinates
FIRST = (283, 286)
LAST  = (430, 286)
ID    = (297, 238)
ROOM  = (256, 582)
CHROME = (961, 1056)
DESC = (100, 900)

BUILDING_NAMES = {
    'HH': 'Lord Home',
    'RBH': 'Robert Bryson',
    'TH': 'Lord Thompson',
    'GBH': 'George Burnett',
    'RSH': 'Robin Smith',
    'AM': 'Anna Macleod',
    'MS': 'Muriel Spark',
    'MF': 'Mary Fergusson',
    'LHH': 'Leonard Horner',
    'CME': 'Christina Miller East',
    'CMW': 'Christina Miller West',
}

def copy_field(pos, triple=False):
    pyautogui.moveTo(*pos, duration=0.05)
    clicks = 3 if triple else 2
    pyautogui.click(clicks=clicks)
    time.sleep(0.05)
    pyautogui.hotkey('ctrl','c')
    time.sleep(0.05)
    return pyperclip.paste()

def type_at(x, y, text, press_enter=False):
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click()
    pyautogui.write(text, interval=0.01)
    if press_enter:
        pyautogui.press('enter')

def parse_room(room_str):
    """Extract building name and floor from room number"""
    room_str = room_str.strip()
    
    # Simple rooms: HH.312, RBH.213, GBH.210, RSH.232, TH.310, HH.G.12
    simple_match = re.match(r'^([A-Z]+)\.([0-9G])\.?(\d+)?', room_str)
    if simple_match:
        building_code = simple_match.group(1)
        floor_part = simple_match.group(2)
        
        if building_code in ['HH', 'RBH', 'TH', 'GBH', 'RSH']:
            building = BUILDING_NAMES.get(building_code, building_code)
            if floor_part == 'G':
                floor = 'Ground'
            else:
                floor = floor_part
            return building, floor
    
    # New rooms: AM.F21A, MS.F31E, MF.F9B
    new_match = re.match(r'^([A-Z]+)\.F(\d+)[A-Z]?', room_str)
    if new_match:
        building_code = new_match.group(1)
        flat_num = int(new_match.group(2))
        
        if building_code == 'MF':
            if 1 <= flat_num <= 7:
                floor = 'Ground'
            elif 8 <= flat_num <= 14:
                floor = '1'
            elif 15 <= flat_num <= 21:
                floor = '2'
            elif 22 <= flat_num <= 28:
                floor = '3'
            else:
                floor = '4'
            return BUILDING_NAMES['MF'], floor
        
        elif building_code == 'MS':
            if 1 <= flat_num <= 8:
                floor = 'Ground'
            elif 9 <= flat_num <= 16:
                floor = '1'
            elif 17 <= flat_num <= 24:
                floor = '2'
            elif 25 <= flat_num <= 32:
                floor = '3'
            else:
                floor = '4'
            return BUILDING_NAMES['MS'], floor
        
        elif building_code == 'AM':
            if 1 <= flat_num <= 5:
                floor = 'Ground'
            elif 6 <= flat_num <= 11:
                floor = '1'
            elif 12 <= flat_num <= 16:
                floor = '2'
            elif 17 <= flat_num <= 21:
                floor = '3'
            else:
                floor = '4'
            return BUILDING_NAMES['AM'], floor
    
    # Old rooms: LHHA.120, LHHB.312, LHHC.213, LHHD.234
    old_match = re.match(r'^LHH[A-D]\.(\d)(\d{2})', room_str)
    if old_match:
        first_digit = int(old_match.group(1))
        if first_digit == 1:
            floor = 'Ground'
        else:
            floor = str(first_digit - 1)
        return BUILDING_NAMES['LHH'], floor
    
    # Weird rooms: CMEC2.F8.01, CMWC3.F8.05, CMEB2.F8.01, CMWB3.F8.05, CMWA2.B.01, CMEA2.B.12, CMWCLG.F1.04
    weird_match = re.match(r'^(CME|CMW)[A-D]?([0-9G]|LG)\.', room_str)
    if weird_match:
        base_building = weird_match.group(1)
        floor_part = weird_match.group(2)
        
        building = BUILDING_NAMES.get(base_building, base_building)
        
        if floor_part == 'G' or floor_part == 'LG':
            floor = 'Ground'
        elif floor_part == 'B':
            floor = 'Ground'  # Assuming B means basement/ground
        else:
            floor = floor_part
        
        return building, floor
    
    # Fallback
    return "Unknown Building", "Unknown"

def main_script():
    print("Script starting in 2 seconds...")
    time.sleep(2)
    
    # Copy fields from source
    first = copy_field(FIRST)
    last  = copy_field(LAST)
    sid   = copy_field(ID)
    room  = copy_field(ROOM)
    
    # Parse room information
    building, floor = parse_room(room)
    
    current_time = datetime.datetime.now().strftime("%H:%M")
    current_datetime = datetime.datetime.now().strftime("%d %b %Y %H:%M")
    
    # Navigate to Chrome (once)
    pyautogui.moveTo(*CHROME, duration=0.1)
    pyautogui.click()
    time.sleep(0.1)
    
    # Sequence of data entry
    fields = [
        (110, 466, "Tim Hayes", False),
        (110, 545, "tlh2000@hw.ac.uk", False),
        (110, 742, "Edinburgh", True),
        (110, 835, building, True),
        (110, 930, floor, True),
        (110, 1020, room.strip(), False),
    ]
    
    for x, y, text, enter in fields:
        type_at(x, y, text, press_enter=enter)
    
    # Page down after room entry
    pyautogui.press('pagedown')
    time.sleep(0.1)
    
    # Continue with remaining fields
    remaining_fields = [
        (110, 515, "Edinburgh Campus - Residences", True),
        (110, 700, "Access - Supporting Student Residents", True),
        (110, 800, current_datetime, False),
    ]
    
    for x, y, text, enter in remaining_fields:
        type_at(x, y, text, press_enter=enter)
    
    # Paste the template
    template = f"""Student's full name: {first.strip()} {last.strip()}
Room: {room.strip()}
HWU ID: {sid.strip()}
Granted access by: RLW Tim & RLW Ovye
Granted access at: {current_time}"""
    
    pyautogui.moveTo(*DESC, duration=0.1)
    pyautogui.click()
    time.sleep(0.05)
    pyautogui.write(template, interval=0.003)
    
    # Page down after description
    pyautogui.press('pagedown')
    time.sleep(0.1)
    
    # Final field
    type_at(110, 662, "No", press_enter=True)
    
    print("Script completed!")

def on_activate():
    print("Hotkey activated! Starting script...")
    main_script()

# Set up hotkey listener (Ctrl+Shift+K)
hotkey = keyboard.GlobalHotKeys({
    '<ctrl>+<shift>+k': on_activate
})

if __name__ == "__main__":
    print("Script loaded. Press Ctrl+Shift+K to start.")
    print("Press Ctrl+C to exit.")
    
    hotkey.start()
    
    try:
        # Keep the script running
        hotkey.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        hotkey.stop()
