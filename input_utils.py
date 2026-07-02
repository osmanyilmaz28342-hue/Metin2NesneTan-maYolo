"""
input_utils.py — DirectInput fare ve klavye.
"""

import ctypes, time, random

MOUSEEVENTF_MOVE     = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004
KEYEVENTF_SCANCODE   = 0x0008
KEYEVENTF_KEYUP      = 0x0002

SendInput = ctypes.windll.user32.SendInput
user32    = ctypes.windll.user32
SCREEN_W  = user32.GetSystemMetrics(0)
SCREEN_H  = user32.GetSystemMetrics(1)
PUL       = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk",ctypes.c_ushort),("wScan",ctypes.c_ushort),
                ("dwFlags",ctypes.c_ulong),("time",ctypes.c_ulong),("dwExtraInfo",PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg",ctypes.c_ulong),("wParamL",ctypes.c_short),("wParamH",ctypes.c_ushort)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx",ctypes.c_long),("dy",ctypes.c_long),("mouseData",ctypes.c_ulong),
                ("dwFlags",ctypes.c_ulong),("time",ctypes.c_ulong),("dwExtraInfo",PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki",KeyBdInput),("mi",MouseInput),("hi",HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type",ctypes.c_ulong),("ii",Input_I)]

def _mouse(flags, x=0, y=0):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    dx = int(x*65535/SCREEN_W) if x else 0
    dy = int(y*65535/SCREEN_H) if y else 0
    ii_.mi = MouseInput(dx,dy,0,flags,0,ctypes.pointer(extra))
    SendInput(1,ctypes.pointer(Input(ctypes.c_ulong(0),ii_)),ctypes.sizeof(Input))

def _key(scan, flags):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0,scan,KEYEVENTF_SCANCODE|flags,0,ctypes.pointer(extra))
    SendInput(1,ctypes.pointer(Input(ctypes.c_ulong(1),ii_)),ctypes.sizeof(Input))

def click(x, y):
    _mouse(MOUSEEVENTF_MOVE|MOUSEEVENTF_ABSOLUTE, x, y)
    time.sleep(0.05)
    _mouse(MOUSEEVENTF_LEFTDOWN)
    time.sleep(random.uniform(0.05,0.12))
    _mouse(MOUSEEVENTF_LEFTUP)

def press_key(scan):
    _key(scan, 0)
    time.sleep(random.uniform(0.08,0.18))
    _key(scan, KEYEVENTF_KEYUP)
    time.sleep(0.05)

def hold_key(scan, duration):
    _key(scan, 0)
    time.sleep(duration)
    _key(scan, KEYEVENTF_KEYUP)

def press_combo(mod, key):
    _key(mod,0); time.sleep(0.1)
    _key(key,0); time.sleep(random.uniform(0.05,0.1))
    _key(key,KEYEVENTF_KEYUP); time.sleep(0.1)
    _key(mod,KEYEVENTF_KEYUP); time.sleep(0.1)
