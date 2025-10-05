import pyautogui, time, datetime
import pyperclip
import re
import keyboard
import sys

# Example absolute coordinates (replace with your own)
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

def exit_program():
    """Exit handler for emergency stop"""
    print("Emergency exit triggered!")
    sys.exit(0)

# Set up emergency exit hotkey (Ctrl+Shift+Q)
keyboard.add_hotkey('ctrl+shift+q', exit_program)

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
    """
    Parse room string and return (building_name, floor_level).
    
    Examples:
    - HH.312 -> ('Lord Home', '3')
    - HH.G.12 -> ('Lord Home', 'Ground')
    - AM.F21A -> ('Anna Macleod', '2')
    - LHHA.123 -> ('Leonard Horner', 'Ground')
    - CMEC2.F8.01 -> ('Christina Miller East', '2')
    - CMWCLG.F1.04 -> ('Christina Miller West', 'Ground')
    """
    room_str = room_str.strip()
    
    # Weird room numbers: CMEC2.F8.01 or CMWCLG.F1.04
    weird_match = re.match(r'^(CME|CMW)([ABCG]?)(\d+|LG)\.', room_str)
    if weird_match:
        prefix = weird_match.group(1)  # CME or CMW
        floor_part = weird_match.group(3)  # The floor number or LG
        
        building = BUILDING_NAMES[prefix]
        
        if floor_part == 'LG' or floor_part == 'G':
            floor = 'Ground'
        else:
            floor = floor_part
        
        return (building, floor)
    
    # Old room numbers: LHHA.120, LHHB.312, etc.
    old_match = re.match(r'^(LHH)[ABCD]\.(\d)(\d{2})', room_str)
    if old_match:
        prefix = old_match.group(1)
        first_digit = int(old_match.group(2))
        
        building = BUILDING_NAMES[prefix]
        
        # Floor mapping: 1->Ground, 2->1, 3->2, etc.
        if first_digit == 1:
            floor = 'Ground'
        else:
            floor = str(first_digit - 1)
        
        return (building, floor)
    
    # New room numbers: AM.F21A, MS.F31E, MF.F9B
    new_match = re.match(r'^(AM|MS|MF)\.F(\d+)', room_str)
    if new_match:
        prefix = new_match.group(1)
        flat_num = int(new_match.group(2))
        
        building = BUILDING_NAMES[prefix]
        
        if prefix == 'MF':  # Mary Fergusson
            if flat_num <= 7:
                floor = 'Ground'
            elif flat_num <= 14:
                floor = '1'
            elif flat_num <= 21:
                floor = '2'
            elif flat_num <= 28:
                floor = '3'
            else:
                floor = '4'
        elif prefix == 'MS':  # Muriel Spark
            if flat_num <= 8:
                floor = 'Ground'
            elif flat_num <= 16:
                floor = '1'
            elif flat_num <= 24:
                floor = '2'
            elif flat_num <= 32:
                floor = '3'
            else:
                floor = '4'
        elif prefix == 'AM':  # Anna Macleod
            if flat_num <= 5:
                floor = 'Ground'
            elif flat_num <= 11:
                floor = '1'
            elif flat_num <= 16:
                floor = '2'
            elif flat_num <= 21:
                floor = '3'
            else:
                floor = '4'
        
        return (building, floor)
    
    # Simple room numbers: HH.312, RBH.213, HH.G.12
    simple_match = re.match(r'^([A-Z]{2,3})\.([GBg]|\d)\.?', room_str)
    if simple_match:
        prefix = simple_match.group(1)
        floor_char = simple_match.group(2)
        
        building = BUILDING_NAMES.get(prefix, prefix)
        
        if floor_char.upper() == 'G' or floor_char.upper() == 'B':
            floor = 'Ground' if floor_char.upper() == 'G' else 'Basement'
        else:
            floor = floor_char
        
        return (building, floor)
    
    # Fallback
    return (room_str, 'Unknown')

# Main execution
try:
    first = copy_field(FIRST)
    last  = copy_field(LAST)
    sid   = copy_field(ID)
    room  = copy_field(ROOM)

    building_name, floor_level = parse_room(room)
    
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
        (110, 835, building_name, True),
        (110, 930, floor_level, True),
        (110, 1020, room.strip(), False),
    ]

    for x, y, text, enter in fields:
        type_at(x, y, text, press_enter=enter)

    # Press Page Down after room entry
    pyautogui.press('pagedown')
    time.sleep(0.1)

    # Continue with remaining fields
    more_fields = [
        (110, 515, "Edinburgh Campus - Residences", True),
        (110, 700, "Access - Supporting Student Residents", True),
        (110, 800, current_datetime, False),  # Date/time
    ]

    for x, y, text, enter in more_fields:
        type_at(x, y, text, press_enter=enter)

    # Paste the template in description field
    template = f"""Student's full name: {first.strip()} {last.strip()}
Room: {room.strip()}
HWU ID: {sid.strip()}
Granted access by: RLW Tim & RLW Ovye
Granted access at: {current_time}"""

    pyautogui.moveTo(*DESC, duration=0.1)
    pyautogui.click()
    time.sleep(0.05)
    pyautogui.write(template, interval=0.003)

    # Press Page Down after description
    pyautogui.press('pagedown')
    time.sleep(0.1)

    # Final field
    type_at(110, 662, "No", press_enter=True)

    print("Script completed successfully!")
    print("Press Ctrl+Shift+Q to exit at any time.")

except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)
