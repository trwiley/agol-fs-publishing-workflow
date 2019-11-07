# --> open_arcmap.py <--
# A set of clicks and keystrokes that opens arcmap and signs into AGOL with credentials privided in the form of command line arguments.
# Uses plaintext for passwords, use at your own risk.

import pyautogui
from time import sleep
import sys



def open_and_login(username, password):
    # Pause for one second in between movements
    pyautogui.PAUSE = 1

    # open arcmap
    pyautogui.click(25, 1060)
    pyautogui.typewrite("arcmap")
    pyautogui.click(50, 500)
    sleep(20)

    # close out of the screen that prompts you to open a file, go to file > sign in.
    pyautogui.click(1200, 700)
    pyautogui.click(20, 25)
    pyautogui.click(20, 225)

    # put in username and password and click "enter"
    pyautogui.typewrite(username)
    pyautogui.typewrite(['tab'])
    pyautogui.typewrite(password)
    pyautogui.typewrite(['enter'])


def main():
    open_and_login(sys.argv[1], sys.argv)