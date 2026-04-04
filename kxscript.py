import pyautogui
import time
import datetime
import pyperclip
import re
from pynput import keyboard
import sys
import subprocess
import platform
import threading

pyautogui.FAILSAFE = True

script_running = False
exit_program = False
last_run_time = 0  # Track last run time to prevent rapid re-triggers

FIRST = (283, 286)
LAST = (430, 286)
ID = (297, 238)
ROOM = (256, 582)
DESC = (110, 800)

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

def parse_room_info(room_number):
    room_number = room_number.strip()
    
    # Simple room numbers: HH.312, RBH.213, GBH.210, RSH.232, TH.310, HH.G.12
    simple_pattern = r'^([A-Z]+)\.([0-9G])\.?(\d*)$'
    match = re.match(simple_pattern, room_number)
    if match:
        building_code = match.group(1)
        floor_char = match.group(2)
        if building_code in BUILDING_NAMES:
            building_name = BUILDING_NAMES[building_code]
            if floor_char == 'G':
                floor_level = 'G'
            else:
                floor_level = floor_char
            return building_name, floor_level
    
    # New room numbers: AM.F21A, MS.F31E, MF.F9B
    new_pattern = r'^(AM|MS|MF)\.F(\d+)[A-Z]?$'
    match = re.match(new_pattern, room_number)
    if match:
        building_code = match.group(1)
        flat_num = int(match.group(2))
        building_name = BUILDING_NAMES[building_code]
        
        if building_code == 'MF':
            if 1 <= flat_num <= 7:
                floor_level = 'G'
            elif 8 <= flat_num <= 14:
                floor_level = '1'
            elif 15 <= flat_num <= 21:
                floor_level = '2'
            elif 22 <= flat_num <= 28:
                floor_level = '3'
            else:
                floor_level = '4'
        elif building_code == 'MS':
            if 1 <= flat_num <= 8:
                floor_level = 'G'
            elif 9 <= flat_num <= 16:
                floor_level = '1'
            elif 17 <= flat_num <= 24:
                floor_level = '2'
            elif 25 <= flat_num <= 32:
                floor_level = '3'
            else:
                floor_level = '4'
        elif building_code == 'AM':
            if 1 <= flat_num <= 5:
                floor_level = 'G'
            elif 6 <= flat_num <= 11:
                floor_level = '1'
            elif 12 <= flat_num <= 16:
                floor_level = '2'
            elif 17 <= flat_num <= 21:
                floor_level = '3'
            else:
                floor_level = '4'
        
        return building_name, floor_level
    
    # Old room numbers: LHHA.120, LHHB.312, LHHC.213, LHHD.234
    old_pattern = r'^LHH[A-D]\.(\d)(\d{2})$'
    match = re.match(old_pattern, room_number)
    if match:
        floor_digit = int(match.group(1))
        building_name = BUILDING_NAMES['LHH']
        
        if floor_digit == 1:
            floor_level = 'G'
        elif floor_digit == 2:
            floor_level = '1'
        elif floor_digit == 3:
            floor_level = '2'
        elif floor_digit == 4:
            floor_level = '3'
        else:
            floor_level = str(floor_digit - 1)
        
        return building_name, floor_level
    
    # Weird room numbers: CMEC2.F8.01, CMWC3.F8.05, CMEB2.F8.01, CMWB3.F8.05, CMWA2.B.01, CMEA2.B.12, CMWCLG.F1.04
    weird_pattern = r'^(CME|CMW)[A-Z]?([0-9G]|LG|B)\..*$'
    match = re.match(weird_pattern, room_number)
    if match:
        building_code = match.group(1)
        floor_char = match.group(2)
        building_name = BUILDING_NAMES[building_code]
        
        if floor_char == 'G' or floor_char == 'LG':
            floor_level = 'G'
        else:
            floor_level = floor_char
        
        return building_name, floor_level
    
    return "Unknown Building", "Unknown Floor"

def copy_field_with_select_all(pos):
    """Copy field using click, Ctrl+A, Ctrl+C"""
    pyautogui.moveTo(*pos, duration=0.1)
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    return pyperclip.paste()

def copy_field_with_double_click(pos):
    """Copy field using double click, Ctrl+C"""
    pyautogui.moveTo(*pos, duration=0.1)
    time.sleep(0.1)
    pyautogui.click(clicks=2)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    return pyperclip.paste()

def type_at(x, y, text, press_enter=False):
    """Type text at specific coordinates with 0.5-second delay before spaces"""
    pyautogui.moveTo(x, y, duration=0.1)
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.15)
    
    # Split text by spaces to handle multi-word entries efficiently
    words = text.split(' ')
    
    for i, word in enumerate(words):
        # Type the word quickly (no interval between characters)
        pyautogui.typewrite(word, interval=0)
        
        # If not the last word, add space with delay
        if i < len(words) - 1:
            time.sleep(0.5)  # 0.5 second delay before space
            pyautogui.press('space')
    
    time.sleep(0.3)
    
    if press_enter:
        pyautogui.press('enter')
        time.sleep(0.2)

def select_edinburgh():
    """Select Edinburgh from location dropdown"""
    print("  Selecting Edinburgh...")
    pyautogui.moveTo(200, 682, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)  # Wait for list to load
    pyautogui.moveTo(280, 583, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)  # Wait for confirmation

def select_building(building_name):
    """Select building from dropdown with search"""
    print(f"  Selecting building: {building_name}...")
    pyautogui.moveTo(200, 760, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)
    pyautogui.moveTo(300, 405, duration=0.1)
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.write(building_name, interval=0.005)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1.5)
    pyautogui.moveTo(280, 758, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)

def select_floor_level(floor_level):
    """Select floor level from dropdown with search"""
    print(f"  Selecting floor level: {floor_level}...")
    pyautogui.moveTo(200, 840, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)
    pyautogui.moveTo(300, 580, duration=0.1)
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.write(floor_level, interval=0.005)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1.5)  # Wait for loading
    pyautogui.moveTo(280, 842, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)

def select_campus_residences():
    """Select Edinburgh Campus - Residences"""
    print("  Selecting Edinburgh Campus - Residences...")
    pyautogui.moveTo(200, 363, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)
    pyautogui.moveTo(280, 483, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)

def select_access_support():
    """Select Access - Supporting Student Residents"""
    print("  Selecting Access - Supporting Student Residents...")
    pyautogui.moveTo(205, 523, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)
    pyautogui.moveTo(280, 480, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)

def select_final_field():
    """Select final field (No)"""
    print("  Selecting final field...")
    pyautogui.moveTo(205, 1025, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)
    pyautogui.moveTo(280, 980, duration=0.1)
    pyautogui.click()
    time.sleep(1.5)

def focus_chrome_window():
    """
    Focus Chrome window using platform-specific methods
    """
    print("Attempting to focus Chrome window...")
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Method 1: Use PowerShell to bring Chrome to front
            print("  Using Windows method...")
            # Try different Chrome process names
            for chrome_name in ["chrome", "Chrome"]:
                try:
                    powershell_cmd = f'''
                    $wshell = New-Object -ComObject wscript.shell;
                    $wshell.AppActivate("{chrome_name}")
                    '''
                    subprocess.run(["powershell", "-Command", powershell_cmd], 
                                 capture_output=True, timeout=2)
                    time.sleep(0.2)
                    print(f"  Attempted to focus using AppActivate('{chrome_name}')")
                except:
                    continue
            
            # Method 2: Try using window title matching
            try:
                # This works if you know part of the Chrome window title
                powershell_cmd = '''
                Add-Type @"
                    using System;
                    using System.Runtime.InteropServices;
                    public class Win {
                        [DllImport("user32.dll")]
                        public static extern bool SetForeGWindow(IntPtr hWnd);
                        [DllImport("user32.dll")]
                        public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
                    }
"@
                $chrome = Get-Process | Where-Object {$_.ProcessName -like "*chrome*"} | Select-Object -First 1
                if ($chrome) {
                    $handle = $chrome.MainWindowHandle
                    [Win]::SetForeGWindow($handle)
                }
                '''
                subprocess.run(["powershell", "-Command", powershell_cmd], 
                             capture_output=True, timeout=3)
                time.sleep(0.2)
                print("  Chrome window focused successfully")
                return True
            except Exception as e:
                print(f"  PowerShell method failed: {e}")
        
        # Fallback: Simple click method
        print("  Using fallback click method...")
        print("  Please ensure Chrome window is visible on screen")
        time.sleep(1)
        return True
        
    except Exception as e:
        print(f"  Error focusing Chrome: {e}")
        print("  Continuing anyway - please ensure Chrome is visible")
        time.sleep(1)
        return False

def run_automation():
    global script_running, last_run_time
    
    # Prevent multiple simultaneous runs
    if script_running:
        print("Script is already running! Ignoring this trigger.")
        return
    
    # Prevent rapid re-triggers (must wait at least 3 seconds since last run)
    current_time = time.time()
    if current_time - last_run_time < 3.0:
        print(f"Too soon since last run. Please wait {3.0 - (current_time - last_run_time):.1f} more seconds.")
        return
    
    script_running = True
    last_run_time = current_time
    print("Starting automation...")
    
    # Add a delay to ensure hotkey is fully released
    time.sleep(0.5)
    
    try:
        # Copy fields from source
        print("Copying fields...")
        first = copy_field_with_select_all(FIRST)
        last = copy_field_with_select_all(LAST)
        sid = copy_field_with_select_all(ID)
        room = copy_field_with_double_click(ROOM)
        
        # Parse room information
        building_name, floor_level = parse_room_info(room)
        print(f"Parsed room: {room} -> Building: {building_name}, Floor: {floor_level}")
        
        current_time_str = datetime.datetime.now().strftime("%H:%M")
        current_datetime = datetime.datetime.now().strftime("%d %b %Y %H:%M")
        
        # Focus Chrome with better reliability
        print("Switching to Chrome...")
        focus_chrome_window()
        time.sleep(0.2)  # Extra delay to ensure Chrome is ready
        
        # Enter initial fields with delays
        print("Entering initial fields...")
        initialFields = [
            (110, 416, "Tim Hayes", False),
            (110, 495, "tlh2000@hw.ac.uk", False),
        ]

        for i, (x, y, text, enter) in enumerate(initialFields):
            print(f"  Field {i+1}/{len(initialFields)}: {text[:20]}...")
            type_at(x, y, text, press_enter=enter)
            time.sleep(0.2)  # Additional delay between fields
        
        # Select Edinburgh (new checkbox-style UI)
        print("Selecting location fields...")
        select_edinburgh()
        time.sleep(0.2)
        
        # Select building (new checkbox-style UI with search)
        select_building(building_name)
        time.sleep(0.2)
        
        # Select floor level (new checkbox-style UI with search)
        select_floor_level(floor_level)
        time.sleep(0.2)
        
        # Enter room number
        print("Entering room number...")
        type_at(110, 920, room.strip(), press_enter=False)
        time.sleep(0.2)
        
        # Page down to next section
        print("Pressing Page Down...")
        pyautogui.press('pagedown')
        time.sleep(0.15)
        
        # Select campus residences (new checkbox-style UI)
        print("Selecting campus and access fields...")
        select_campus_residences()
        time.sleep(0.2)
        
        # Select access support (new checkbox-style UI)
        select_access_support()
        time.sleep(0.2)
        
        # Enter date
        print("Entering date...")
        pyautogui.moveTo(120, 620, duration=0.1)
        time.sleep(0.1)
        pyautogui.click()
        time.sleep(0.1)
        pyautogui.write(current_datetime, interval=0.005)
        time.sleep(0.2)
        
        # Paste the template
        print("Pasting template...")
        template = f"""Student's full name: {first.strip()} {last.strip()}
Room: {room.strip()}
HWU ID: {sid.strip()}
Granted access by: RLW Tim & RLW Ovye
Granted access at: {current_time_str}"""
        
        pyautogui.moveTo(120, 720, duration=0.1)
        time.sleep(0.1)
        pyautogui.click()
        time.sleep(0.1)
        pyautogui.write(template, interval=0.005)
        time.sleep(0.2)
        
        # Select final field (No)
        print("Selecting final field...")
        select_final_field()
        time.sleep(0.2)
        
        print("Automation completed successfully!")
        print("Waiting 3 seconds before accepting new runs...")
        
        # Add delay before allowing next run to prevent accidental double-trigger
        time.sleep(2.0)
        
    except pyautogui.FailSafeException:
        print("\n!!! FAIL-SAFE TRIGGERED !!!")
        print("Mouse moved to screen corner - automation stopped for safety.")
        print("This is a safety feature. Script is ready for next run.")
    except Exception as e:
        print(f"Error during automation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        script_running = False
        print("Ready for next automation run.\n")

def on_activate_start():
    """Called when start hotkey is pressed"""
    # Run in a separate thread to prevent blocking the hotkey listener
    if not script_running:
        print("\n[START HOTKEY PRESSED]")
        thread = threading.Thread(target=run_automation, daemon=True)
        thread.start()
    else:
        print("Automation already in progress, ignoring hotkey.")

def on_activate_exit():
    """Called when exit hotkey is pressed"""
    global exit_program
    print("\n[EXIT HOTKEY PRESSED] - Exiting program...")
    exit_program = True
    return False

def main():
    """Main entry point with hotkey listeners"""
    global exit_program
    
    print("=" * 60)
    print("PyAutoGUI Automation Script")
    print("=" * 60)
    print("\nHotkeys:")
    print("  Ctrl + Shift + S : Start automation")
    print("  Ctrl + Shift + Q : Exit program")
    print("\nMove mouse to top-left corner for emergency stop!")
    print("=" * 60)
    print("\nWaiting for hotkey press...\n")
    
    # Set up hotkey listeners with proper key combination
    start_combo = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+<shift>+s'),
        on_activate_start
    )
    exit_combo = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+<shift>+q'),
        on_activate_exit
    )
    
    def for_canonical(f):
        return lambda k: f(listener.canonical(k))
    
    # Create listener
    with keyboard.Listener(
        on_press=for_canonical(lambda key: (
            start_combo.press(key),
            exit_combo.press(key)
        )),
        on_release=for_canonical(lambda key: (
            start_combo.release(key),
            exit_combo.release(key)
        ))
    ) as listener:
        
        # Keep the program running until exit_program is True
        while not exit_program:
            time.sleep(0.1)
        
        listener.stop()
    
    print("\nProgram terminated.")
    sys.exit(0)

if __name__ == "__main__":
    main()
