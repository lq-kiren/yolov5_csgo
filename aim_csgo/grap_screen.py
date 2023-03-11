import mss
import cv2.cv2 as cv2
import numpy as np
import win32api

cap = mss.mss()
def grab_screen_mss(monitor):
    return cv2.cvtColor(np.array(cap.grab(monitor)), cv2.COLOR_BGRA2BGR)

def get_parameters():
    x, y = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    return 0, 0, x, y