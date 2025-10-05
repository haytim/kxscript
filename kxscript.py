import pyautogui
import pyperclip
import time
import datetime
import re
from pynput import keyboard

# Coordinates
FIRST = (283, 286)
LAST = (430, 286)
ID = (297, 238)
ROOM = (256, 582)
CHROME = (961, 1056)
DESC = (100, 900)

# Building names mapping
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

# Global control flags
running = False
should_exit = False


def copy_field(pos, triple=False):
    """Copy text from a field at given position"""
    pyautogui.moveTo(*pos, duration=0.05)
    clicks = 3 if triple else 2
    pyautogui.click(clicks=clicks)
    time.sleep(0.05)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.05)
    return pyperclip.paste()


def type_at(x, y, text, press_enter=False):
    """Type text at given coordinates"""
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click()
    time.sleep(0.05)
    pyautogui.write(text, interval=0.01)
    if press_enter:
        pyautogui.press('enter')


def parse_room_number(room_str):
    """Parse room number and extract building code and floor"""
    room_str = room_str.strip()
    
    # Weird room numbers: CMEC2.F8.01, CMWCLG.F1.04, etc.
    match = re.match(r'^(CME|CMW)([A-Z])(\d+|LG|G)\.', room_str)
    if match:
        base_code = match.group(1)  # CME or CMW
        block = match.group(2)      # A, B, C, etc. (ignored for building name)
        floor_code = match.group(3) # Floor indicator
        
        # Handle special case CMWCLG (LG = Lower Ground = Ground)
        if floor_code == 'LG' or floor_code == 'G':
            floor = 'Ground'
        else:
            floor = floor_code
        
        building = BUILDING_NAMES.get(base_code, base_code)
        return building, floor
    
    # Old room numbers: LHHA.120, LHHB.312, etc.
    match = re.match(r'^(LHH)([A-D])\.(\d)(\d{2})$', room_str)
    if match:
        base_code = match.group(1)
        block = match.group(2)  # A, B, C, D (ignored for building name)
        first_digit = int(match.group(3))
        
        # In LHH format: 1xx = Ground, 2xx = Floor 1, 3xx = Floor 2, etc.
        if first_digit == 1:
            floor = 'Ground'
        else:
            floor = str(first_digit - 1)
        
        building = BUILDING_NAMES.get(base_code, base_code)
        return building, floor
    
    # New room numbers: AM.F21A, MS.F31E, MF.F9B
    match = re.match(r'^(AM|MS|MF)\.F(\d+)', room_str)
    if match:
        hall_code = match.group(1)
        flat_num = int(match.group(2))
        
        if hall_code == 'MF':  # Mary Fergusson
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
        elif hall_code == 'MS':  # Muriel Spark
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
        elif hall_code == 'AM':  # Anna Macleod
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
        
        building = BUILDING_NAMES.get(hall_code, hall_code)
        return building, floor
    
    # Simple room numbers: HH.312, HH.G.12, RBH.213, etc.
    match = re.match(r'^([A-Z]{2,3})\.([GBg]|\d)', room_str)
    if match:
        building_code = match.group(1)
        floor_code = match.group(2)
        
        if floor_code.upper() == 'G' or floor_code.upper() == 'B':
            floor = 'Ground'
        else:
            floor = floor_code
        
        building = BUILDING_NAMES.get(building_code, building_code)
        return building, floor
    
    # Fallback
    return "Unknown Building", "Unknown"


def run_automation():
    """Main automation routine"""
    global running
    
    print("Starting automation...")
    
    # Copy fields from source
    first = copy_field(FIRST)
    last = copy_field(LAST)
    sid = copy_field(ID)
    room = copy_field(ROOM)
    
    # Parse room information
    building, floor = parse_room_number(room)
    
    # Generate timestamps
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
    
    # Press Page Down after room entry to align pixels
    pyautogui.press('pagedown')
    time.sleep(0.1)
    
    # Continue with remaining fields
    type_at(110, 515, "Edinburgh Campus - Residences", press_enter=True)
    type_at(110, 700, "Access - Supporting Student Residents", press_enter=True)
    type_at(110, 800, current_datetime, press_enter=False)
    
    # Paste the template at DESC location
    template = f"""Student's full name: {first.strip()} {last.strip()}
Room: {room.strip()}
HWU ID: {sid.strip()}
Granted access by: RLW Tim & RLW Ovye
Granted access at: {current_time}"""
    
    pyautogui.moveTo(*DESC, duration=0.1)
    pyautogui.click()
    time.sleep(0.05)
    pyautogui.write(template, interval=0.003)
    
    # Press Page Down after description to align pixels
    pyautogui.press('pagedown')
    time.sleep(0.1)
    
    # Final field
    type_at(110, 662, "No", press_enter=True)
    
    print("Automation completed!")
    running = False


def on_press(key):
    """Handle keyboard hotkeys"""
    global running, should_exit
    
    try:
        # Check for Ctrl+Shift+S to start
        if hasattr(key, 'char'):
            return
        
        # Get current pressed keys
        current_keys = keyboard.Controller().pressed_keys if hasattr(keyboard.Controller(), 'pressed_keys') else set()
        
    except AttributeError:
        pass


def on_activate_start():
    """Hotkey handler for starting automation"""
    global running
    if not running:
        running = True
        print("Hotkey detected: Starting automation...")
        run_automation()


def on_activate_exit():
    """Hotkey handler for exiting program"""
    global should_exit
    print("Hotkey detected: Exiting program...")
    should_exit = True
    return False  # Stop listener


if __name__ == "__main__":
    print("=" * 60)
    print("Room Access Automation Script")
    print("=" * 60)
    print("\nHotkeys:")
    print("  Ctrl+Shift+S - Start automation")
    print("  Ctrl+Shift+Q - Exit program")
    print("\nWaiting for hotkey press...\n")
    
    # Set up global hotkeys
    with keyboard.GlobalHotKeys({
            '<ctrl>+<shift>+s': on_activate_start,
            '<ctrl>+<shift>+q': on_activate_exit
    }) as listener:
        listener.join()
    
    print("\nProgram terminated.")
