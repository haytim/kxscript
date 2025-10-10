import pyautogui
import time
import datetime
import pyperclip
import re
from pynput import keyboard
import sys
import subprocess
import platform

pyautogui.FAILSAFE = True

script_running = False
exit_program = False

FIRST = (283, 286)
LAST = (430, 286)
ID = (297, 238)
ROOM = (256, 582)
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
                floor_level = 'Ground'
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
                floor_level = 'Ground'
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
                floor_level = 'Ground'
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
                floor_level = 'Ground'
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
            floor_level = 'Ground'
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
            floor_level = 'Ground'
        elif floor_char == 'B':
            floor_level = 'Basement'
        else:
            floor_level = floor_char
        
        return building_name, floor_level
    
    return "Unknown Building", "Unknown Floor"

def copy_field(pos, triple=False):
    pyautogui.moveTo(*pos, duration=0.1)
    time.sleep(0.1)
    clicks = 3 if triple else 2
    pyautogui.click(clicks=clicks)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.2)
    return pyperclip.paste()

def type_at(x, y, text, press_enter=False):
    pyautogui.moveTo(x, y, duration=0.2)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(0.3)
    pyautogui.write(text, interval=0.02)
    time.sleep(1)
    if press_enter:
        pyautogui.press('enter')
        time.sleep(0.3)

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
                    time.sleep(0.5)
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
                        public static extern bool SetForegroundWindow(IntPtr hWnd);
                        [DllImport("user32.dll")]
                        public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
                    }
"@
                $chrome = Get-Process | Where-Object {$_.ProcessName -like "*chrome*"} | Select-Object -First 1
                if ($chrome) {
                    $handle = $chrome.MainWindowHandle
                    [Win]::SetForegroundWindow($handle)
                }
                '''
                subprocess.run(["powershell", "-Command", powershell_cmd], 
                             capture_output=True, timeout=3)
                time.sleep(0.8)
                print("  Chrome window focused successfully")
                return True
            except Exception as e:
                print(f"  PowerShell method failed: {e}")
        
        elif system == "Darwin":  # macOS
            print("  Using macOS method...")
            subprocess.run(["osascript", "-e", 
                          'tell application "Google Chrome" to activate'], 
                         capture_output=True, timeout=2)
            time.sleep(0.5)
            print("  Chrome activated on macOS")
            return True
        
        elif system == "Linux":
            print("  Using Linux method...")
            # Try wmctrl first (most reliable)
            try:
                subprocess.run(["wmctrl", "-a", "Chrome"], 
                             capture_output=True, timeout=2)
                time.sleep(0.5)
                print("  Chrome focused using wmctrl")
                return True
            except:
                # Fallback to xdotool
                try:
                    subprocess.run(["xdotool", "search", "--name", "Chrome", 
                                  "windowactivate"], 
                                 capture_output=True, timeout=2)
                    time.sleep(0.5)
                    print("  Chrome focused using xdotool")
                    return True
                except:
                    print("  Install wmctrl or xdotool for better window focusing")
        
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
    global script_running
    
    if script_running:
        print("Script is already running!")
        return
    
    script_running = True
    print("Starting automation...")
    
    try:
        # Copy fields from source
        print("Copying fields...")
        first = copy_field(FIRST)
        last = copy_field(LAST)
        sid = copy_field(ID)
        room = copy_field(ROOM)
        
        # Parse room information
        building_name, floor_level = parse_room_info(room)
        print(f"Parsed room: {room} -> Building: {building_name}, Floor: {floor_level}")
        
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_datetime = datetime.datetime.now().strftime("%d %b %Y %H:%M")
        
        # Focus Chrome with better reliability
        print("Switching to Chrome...")
        focus_chrome_window()
        time.sleep(0.5)  # Extra delay to ensure Chrome is ready
        
        # Enter initial fields with delays
        print("Entering initial fields...")
        fields = [
            (110, 416, "Tim Hayes", False),
            (110, 495, "tlh2000@hw.ac.uk", False),
            (110, 692, "Edinburgh", True),
            (110, 785, building_name, True),
            (110, 880, floor_level, True),
            (110, 970, room.strip(), False),
        ]
        
        for i, (x, y, text, enter) in enumerate(fields):
            print(f"  Field {i+1}/{len(fields)}: {text[:20]}...")
            type_at(x, y, text, press_enter=enter)
            time.sleep(1.5)  # Additional delay between fields
        
        # Wait for all fields to be entered before page down
        print("Waiting before Page Down...")
        time.sleep(1.5)
        print("Pressing Page Down (after room entry)...")
        pyautogui.press('pagedown')
        time.sleep(2)
        
        # Continue with remaining fields
        print("Entering remaining fields...")
        remaining_fields = [
            (110, 415, "Edinburgh Campus - Residences", True),
            (110, 605, "Access - Supporting Student Residents", True),
            (110, 705, current_datetime, False),
        ]
        
        for i, (x, y, text, enter) in enumerate(remaining_fields):
            print(f"  Field {i+1}/{len(remaining_fields)}: {text[:30]}...")
            type_at(x, y, text, press_enter=enter)
            time.sleep(2.8)
        
        # Paste the template after the date field
        print("Pasting template...")
        template = f"""Student's full name: {first.strip()} {last.strip()}
Room: {room.strip()}
HWU ID: {sid.strip()}
Granted access by: RLW Tim & RLW Ovye
Granted access at: {current_time}"""
        
        time.sleep(0.3)
        pyautogui.moveTo(*DESC, duration=0.2)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(0.3)
        pyautogui.write(template, interval=0.005)
        time.sleep(2)
        
        # Wait before page down
        print("Waiting before Page Down...")
        time.sleep(1.5)
        print("Pressing Page Down (after description)...")
        pyautogui.press('pagedown')
        time.sleep(2)
        
        # Final field
        print("Entering final field...")
        type_at(110, 665, "No", press_enter=True)
        time.sleep(0.3)
        
        print("Automation completed successfully!")
        
    except Exception as e:
        print(f"Error during automation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        script_running = False

def on_activate_start():
    """Called when start hotkey is pressed"""
    print("\n[START HOTKEY PRESSED]")
    run_automation()

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
