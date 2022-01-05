# install https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20210811.exe

import numpy as nm
import pytesseract
import cv2
import re
import keyboard as kb
from pywinauto import backend
import pywinauto.keyboard as keyboard
import distutils.spawn
import requests
import ctypes
import subprocess
import os

from PIL    import ImageGrab, Image
from numpy  import not_equal, random
from time   import sleep
from random import randint 
from pywinauto.application import Application
from ctypes.wintypes import BOOL, HWND, LPWSTR, UINT
from clint.textui import progress

PROGRESS_BAR_PIXEL = (875-800, 106-100)    # X, Y
PROGRESS_BAR_GREEN = (60, 150, 60)         # R, G, B
SCREEN_CAPTURE_BOX = (800, 100, 1150, 200) # X, Y, W, H

# messagebox
_user32 = ctypes.WinDLL('user32', use_last_error=True)
_MessageBoxW = _user32.MessageBoxW
_MessageBoxW.restype = UINT  # default return type is c_int, this is not required
_MessageBoxW.argtypes = (HWND, LPWSTR, LPWSTR, UINT)

MB_YESNO = 4

IDYES = 6
IDNO = 7

TESSERACT_EXE = 'tesseract.exe'
TESSERACT_PATH = 'C:\Program Files\Tesseract-OCR'

def MessageBoxW(hwnd, text, caption, utype):
    result = _MessageBoxW(hwnd, text, caption, utype)
    if not result:
        raise ctypes.WinError(ctypes.get_last_error())
    return result

def find_ocr():
   tesseract_exe = distutils.spawn.find_executable(TESSERACT_EXE, TESSERACT_PATH)

   # Make sure tesseract.exe exists, download/install if necessary
   if not tesseract_exe: 
      result = MessageBoxW(None, "Would you like to download and install?", "tesseract.exe not found", MB_YESNO)
      if result == IDYES:
         print("downloading tesseract-OCR")
         file_url = 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20210811.exe'
         r = requests.get(file_url, stream=True)
         with open('tesseract-ocr-w64-setup-v5.0.0-alpha.20210811.exe', 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
               if chunk:
                     f.write(chunk)
                     f.flush()

         print("installing tesseract-OCR")
         p = os.path.abspath(os.getcwd()) + "\\tesseract-ocr-w64-setup-v5.0.0-alpha.20210811.exe"
         process = subprocess.Popen(p , stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
         process.wait()

         if process.returncode != 0:
            print("error installing tesseract-OCR")
            exit()

         return distutils.spawn.find_executable(TESSERACT_EXE, TESSERACT_PATH)

      elif result == IDNO:
         print("tesseract.exe is required to process images and must be installed.")
         exit()
      else:
         print("tesseract.exe is required to process images and must be installed.")
         exit()
   else:
      return tesseract_exe

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

def main():

   # OCR must exist to process the images
   # Path of tesseract executable
   pytesseract.pytesseract.tesseract_cmd = find_ocr()

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

                  # use current img to see if progress bar is green
                  rgb = cap.getpixel((PROGRESS_BAR_PIXEL))

                  # progress bar is green
                  if rgb == PROGRESS_BAR_GREEN:
                     try:
                           kb.press(button)
                           # to keep GTA from detecting non-human key presses, delay a random amount of milliseconds
                           sleep(randint(250,750)/1000)
                           kb.release(button)
                     except:
                           print("Key does not exist")  
                     break
                     
                  cap = screen_capture(bbox=SCREEN_CAPTURE_BOX)

if __name__ == "__main__":
    main()