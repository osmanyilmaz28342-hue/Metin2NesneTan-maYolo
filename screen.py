"""
screen.py — Seçili pencereyi yakalar (hwnd bazlı).
"""

import numpy as np
import cv2

try:
    import win32gui, win32ui, win32con
    WIN32_OK = True
except ImportError:
    WIN32_OK = False

try:
    import mss
    MSS_OK = True
except ImportError:
    MSS_OK = False


def list_windows():
    """Ekranda görünen tüm pencerelerin (hwnd, başlık) listesini döndürür."""
    windows = []
    if not WIN32_OK:
        return windows
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title.strip():
                windows.append((hwnd, title))
    win32gui.EnumWindows(cb, None)
    return windows


class ScreenCapture:
    def __init__(self, hwnd=None):
        self.hwnd     = hwnd
        self.offset_x = 0
        self.offset_y = 0
        self.w = 0
        self.h = 0
        self.mode = "mss"

        if hwnd and WIN32_OK:
            self._init_hwnd(hwnd)
        elif MSS_OK:
            self.mode = "mss"
        else:
            raise RuntimeError("pywin32 veya mss kurulu değil!")

    def _init_hwnd(self, hwnd):
        try:
            rect = win32gui.GetWindowRect(hwnd)
            self.offset_x = rect[0]
            self.offset_y = rect[1]
            self.w = rect[2] - rect[0]
            self.h = rect[3] - rect[1]
            self.mode = "win32"
        except Exception as e:
            print(f"[!] Pencere hatası: {e} — mss moduna geçildi.")
            self.mode = "mss"

    def capture(self) -> np.ndarray:
        if self.mode == "win32":
            return self._win32()
        return self._mss()

    def _win32(self):
        try:
            # Pencere taşınmış olabilir, her seferinde güncelle
            rect = win32gui.GetWindowRect(self.hwnd)
            self.offset_x = rect[0]; self.offset_y = rect[1]
            self.w = rect[2]-rect[0]; self.h = rect[3]-rect[1]

            wDC   = win32gui.GetWindowDC(self.hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC   = dcObj.CreateCompatibleDC()
            bmp   = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(dcObj, self.w, self.h)
            cDC.SelectObject(bmp)
            cDC.BitBlt((0,0),(self.w,self.h),dcObj,(0,0),win32con.SRCCOPY)
            img = np.frombuffer(bmp.GetBitmapBits(True), dtype=np.uint8)
            img = img.reshape((self.h, self.w, 4))[...,:3]
            dcObj.DeleteDC(); cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(bmp.GetHandle())
            return np.ascontiguousarray(img)
        except Exception as e:
            print(f"[!] Win32 yakalama hatası: {e}")
            return self._mss()

    def _mss(self):
        with mss.mss() as sct:
            shot = np.array(sct.grab(sct.monitors[1]))
            return cv2.cvtColor(shot, cv2.COLOR_BGRA2BGR)

    def to_screen(self, x, y):
        """Pencere-içi koordinatı ekran koordinatına çevirir."""
        return (x + self.offset_x, y + self.offset_y)
