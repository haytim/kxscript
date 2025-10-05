import pyautogui, time, datetime
import pyperclip
import re

# Coordinate positions
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

def parse_room(room_code):
    """Parse room code to extract building name and floor number."""
    room_code = room_code.strip()
    
    # Simple room numbers: HH.312, RBH.213, etc.
    simple_match = re.match(r'^([A-Z]+)\.([G\d])(\d+)?$', room_code)
    if simple_match:
        building_code = simple_match.group(1)
        floor_indicator = simple_match.group(2)
        
        building = BUILDING_NAMES.get(building_code, building_code)
        
        if floor_indicator == 'G':
            floor = 'Ground'
        else:
            floor = floor_indicator
        
        return building, floor
    
    # New room numbers: AM.F21A, MS.F31E, MF.F9B
    new_match = re.match(r'^([A-Z]+)\.F(\d+)[A-Z]?$', room_code)
    if new_match:
        building_code = new_match.group(1)
        flat_num = int(new_match.group(2))
        
        building = BUILDING_NAMES.get(building_code, building_code)
        
        # Calculate floor based on building and flat number
        if building_code == 'MF':  # Mary Fergusson
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
        elif building_code == 'MS':  # Muriel Spark
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
        elif building_code == 'AM':  # Anna Macleod
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
        else:
            floor = '?'
        
        return building, floor
    
    # Old room numbers: LHHA.120, LHHB.312, etc.
    old_match = re.match(r'^(LHH)[A-D]\.(\d)(\d+)$', room_code)
    if old_match:
        building_code = old_match.group(1)
        first_digit = int(old_match.group(2))
        
        building = BUILDING_NAMES.get(building_code, building_code)
        
        # Floor calculation: 1=Ground, 2=1st, 3=2nd, etc.
        if first_digit == 1:
            floor = 'Ground'
        else:
            floor = str(first_digit - 1)
        
        return building, floor
    
    # Weird room numbers: CMEC2.F8.01, CMWB3.F8.05, etc.
    weird_match = re.match(r'^(CME|CMW)[A-C]([G\d])\.', room_code)
    if weird_match:
        building_code = weird_match.group(1)
        floor_indicator = weird_match.group(2)
        
        building = BUILDING_NAMES.get(building_code, building_code)
        
        if floor_indicator == 'G':
            floor = 'Ground'
        else:
            floor = floor_indicator
        
        return building, floor
    
    # If no pattern matches, return as-is
    return room_code, '?'

# Copy fields from KX system
first = copy_field(FIRST)
last  = copy_field(LAST)
sid   = copy_field(ID)
room  = copy_field(ROOM)

# Parse room info
building_name, floor_number = parse_room(room)

# Format timestamps
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
    (110, 930, floor_number, True),
    (110, 1020, room.strip(), False),
    (110, 515, "Edinburgh Campus - Residences", True),
    (110, 700, "Access - Supporting Student Residents", True),
    (110, 800, current_datetime, False),
]

for x, y, text, enter in fields:
    type_at(x, y, text, press_enter=enter)

# Paste the template after the date field
template = f"""Student's full name: {first.strip()} {last.strip()}
Room: {room.strip()}
HWU ID: {sid.strip()}
Granted access by: RLW Tim & RLW Ovye
Granted access at: {current_time}"""

pyautogui.moveTo(*DESC, duration=0.1)
pyautogui.click()
time.sleep(0.05)
pyautogui.write(template, interval=0.003)

# Final field
type_at(110, 662, "No", press_enter=True)
