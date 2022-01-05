# install https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20210811.exe

import numpy as nm
import pytesseract
import cv2
import re
import keyboard as kb
import pywinauto
from pywinauto import backend
import pywinauto.keyboard as keyboard
import win32gui
import win32con
import win32api
import win32process
import ctypes

from PIL    import ImageGrab, Image
from numpy  import not_equal, random
from time   import sleep
from random import randint 
from pywinauto.application import Application

PROGRESS_BAR_PIXEL = (875-800, 106-100)    # X, Y
PROGRESS_BAR_GREEN = (60, 150, 60)         # R, G, B
SCREEN_CAPTURE_BOX = (800, 100, 1150, 200) # X, Y, W, H

# Path of tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def screen_capture(bbox=(0,0,1920,1080), show=False, save=False):
    screen_cap = ImageGrab.grab(bbox)
    if show: screen_cap.show()
    if save: screen_cap.save(bitmap_format='png')
    return screen_cap

def imgToString(bbox=(0,0,1920,1080)):

    cap = screen_capture(bbox, show=False, save=False)

    # Converted the image to monochrome for it to be easily 
    # read by the OCR and obtained the output String.
    tesstr = pytesseract.image_to_string( cv2.cvtColor(nm.array(cap), cv2.COLOR_BGR2GRAY), 
                                          lang ='eng').strip().lower()
    return cap, tesstr

# app = Application().connect(handle=handle)
# for dlg in app.windows():
#     #print(dlg)
#     #print(pywinauto.handleprops.dumpwindow(dlg))
#     #dlg.send_chars("F")
#     print(ord('W'))
#     dlg.send_message(win32con.WM_KEYDOWN, 0x11, 0)
#     dlg.send_message(win32con.WM_CHAR, 0x11, 0)
#     dlg.send_message(win32con.WM_KEYUP, 0x11, 0)

# fiveM = app.top_window()[0]
# fiveM.send_keystrokes("F8")

while(True):

    cap, tess_str = imgToString(bbox=SCREEN_CAPTURE_BOX)
    
    if len(tess_str): print(tess_str)

    # find matching text
    if "press" in tess_str or "line" in tess_str or "green" in tess_str:
        found_key = re.search(r"\[([A-Za-z]+)\]", tess_str)

        # find key needed to press
        if found_key:
            button = found_key.group(1)

            # tight loop to find when progress bar is green
            while(True):

                # use current img to see if progress bar fffis green
                rgb = cap.getpixel((PROGRESS_BAR_PIXEL))

                if rgb == PROGRESS_BAR_GREEN:
                    try:
                        kb.press(button)
                        sleep(randint(250,750)/1000)
                        kb.release(button)
                    except:
                        print("Key does not exist")  
                    break
                    
                cap = screen_capture(bbox=SCREEN_CAPTURE_BOX)