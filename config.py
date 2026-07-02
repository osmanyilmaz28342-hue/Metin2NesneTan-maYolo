"""
config.py — Tüm bot ayarları.
"""

import ctypes

# ─── DirectInput Scan Kodları ────────────────────────────────────────────────
DIK_1        = 0x02
DIK_2        = 0x03
DIK_3        = 0x04
DIK_4        = 0x05
DIK_Q        = 0x10
DIK_W        = 0x11
DIK_E        = 0x12
DIK_R        = 0x13
DIK_G        = 0x22
DIK_LCONTROL = 0x1D
DIK_SPACE    = 0x39
DIK_F1       = 0x3B
DIK_F2       = 0x3C

SC_1    = DIK_1
SC_2    = DIK_2
SC_3    = DIK_3
SC_4    = DIK_4
SC_F1   = DIK_F1
SC_F2   = DIK_F2
SC_CTRL = DIK_LCONTROL
SC_G    = DIK_G


class Config:
    # Pencere (GUI'den doldurulur)
    WINDOW_TITLE       = "Metin2"
    WINDOW_HWND        = None   # GUI pencere seçiciden gelir

    # Tespit
    DETECTION_MODE        = "both"         # "yolo" | "cascade" | "both"
    MODEL_PATH            = "models/best1.pt"
    CONFIDENCE_THRESHOLD  = 0.50
    CASCADE_PATH          = "cascade.xml"
    CASCADE_SCALE         = 1.2
    CASCADE_MIN_NEIGHBORS = 5

    # Referans görseller (images/ klasöründen)
    IMG_TARGET          = "images/target.png"
    IMG_SELECTED_METIN  = "images/selectedmetin.png"
    IMG_FALSE_METIN     = "images/falsemetin.png"
    IMG_FULLHP_METIN    = "images/FullhpMetin.png"
    RESTART_BUTTON      = "restart_button.png"

    # Davranış
    ATTACK_WAIT            = 5.0
    WAIT_AFTER_CLICK       = 2.0
    LOOP_DELAY             = 0.3
    CLICK_COOLDOWN         = 6.4
    MAX_CLICKS_PER_TARGET  = 1
    SAME_TARGET_THRESHOLD  = 60
    MAX_KILL_DURATION      = 25.0
    RESTART_WAIT_TIME      = 5.0

    # Loot
    AUTO_LOOT        = True
    LOOT_KEY         = DIK_Q
    BURST_LOOT_COUNT = 1
    LOOT_INTERVAL    = 0.01

    # Skill
    SKILL_INTERVAL = 1500
    SKILL_KEYS     = [SC_1, SC_2]

    # Keşif
    SEARCH_ROTATION_INTERVAL = 1.5

    # Debug
    DEBUG_MODE = False
