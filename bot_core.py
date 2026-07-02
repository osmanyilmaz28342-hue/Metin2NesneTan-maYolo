"""
bot_core.py — Ana bot döngüsü.
"""

import time, math, cv2
from config import Config, SC_CTRL, SC_G
from screen import ScreenCapture
from detector import Detector
from input_utils import click, press_key, press_combo, hold_key


class BotCore:
    def __init__(self, on_status=None, on_stats=None):
        self.running         = False
        self.screen          = None
        self.detector        = None
        self._on_status      = on_status or (lambda s: print(f"[BOT] {s}"))
        self._on_stats       = on_stats  or (lambda n,t: None)
        self.stone_count     = 0
        self.start_time      = 0
        self.last_skill_time = 0
        self.attack_wait     = Config.ATTACK_WAIT
        self._current_target = None
        self._click_count    = 0
        self._kill_start     = 0
        self._last_click     = 0

    def initialize(self):
        try:
            self._log("Ekran yakalama başlatılıyor...")
            self.screen = ScreenCapture(hwnd=Config.WINDOW_HWND)
            self._log("Tespit motoru yükleniyor...")
            self.detector = Detector()
            self._log("Hazır!")
            return True
        except Exception as e:
            self._log(f"HATA: {e}")
            return False

    def run(self, attack_wait=None):
        if attack_wait is not None:
            self.attack_wait = attack_wait
        self.running         = True
        self.start_time      = time.time()
        self.last_skill_time = time.time()
        self.stone_count     = 0

        while self.running:
            try:
                self._tick()
                self._on_stats(self.stone_count, time.time()-self.start_time)
                time.sleep(Config.LOOP_DELAY)
            except Exception as e:
                self._log(f"Döngü hatası: {e}")
                time.sleep(1.0)

        cv2.destroyAllWindows()

    def stop(self):
        self.running = False

    def _tick(self):
        # Skill kontrolü
        if time.time()-self.last_skill_time > Config.SKILL_INTERVAL:
            self._cast_skills()

        frame  = self.screen.capture()
        h,w    = frame.shape[:2]
        center = (w//2, h//2)

        # Ölüm kontrolü
        respawn = self.detector.find_template(frame, Config.RESTART_BUTTON, 0.7)
        if respawn:
            self._log("Karakter öldü! Yeniden doğma bekleniyor...")
            time.sleep(Config.RESTART_WAIT_TIME)
            rx,ry = self.screen.to_screen(*respawn)
            click(rx,ry)
            time.sleep(3.0)
            self._reset_target()
            return

        # Tespit
        dets   = self.detector.detect(frame)
        target = self.detector.nearest(dets, center)

        # Debug
        if Config.DEBUG_MODE:
            vis = self.detector.draw_debug(frame.copy(), dets, target)
            cv2.imshow("Bot View [Q=cikis]", cv2.resize(vis,(0,0),fx=0.5,fy=0.5))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                return

        if target:
            self._handle(target)
        else:
            self._explore()

    def _handle(self, target):
        tx,ty = self.screen.to_screen(*target.center)
        is_new = True
        if self._current_target:
            lx,ly = self._current_target
            if math.sqrt((tx-lx)**2+(ty-ly)**2) < Config.SAME_TARGET_THRESHOLD:
                is_new = False

        if is_new:
            self._log(f"Yeni hedef: ({tx},{ty}) [{target.source} {target.conf:.2f}]")
            self._current_target = (tx,ty)
            self._click_count    = 0
            self._kill_start     = time.time()

        if time.time()-self._kill_start > Config.MAX_KILL_DURATION:
            self._log("Hedef çok uzun sürdü, atlıyorum.")
            self._reset_target()
            return

        if self._click_count < Config.MAX_CLICKS_PER_TARGET:
            if time.time()-self._last_click > Config.CLICK_COOLDOWN:
                self._log(f"-> Tıklanıyor ({tx},{ty})")
                click(tx,ty)
                self.stone_count   += 1
                self._click_count  += 1
                self._last_click    = time.time()
                time.sleep(self.attack_wait)
                if Config.AUTO_LOOT:
                    for _ in range(Config.BURST_LOOT_COUNT):
                        press_key(Config.LOOT_KEY)
                        time.sleep(Config.LOOT_INTERVAL)

    def _reset_target(self):
        self._current_target = None
        self._click_count    = 0

    def _explore(self):
        self._reset_target()
        from config import DIK_W
        hold_key(DIK_W, 0.4)
        time.sleep(Config.SEARCH_ROTATION_INTERVAL)

    def _cast_skills(self):
        self._log("Skill atılıyor...")
        press_combo(SC_CTRL, SC_G); time.sleep(2.0)
        for k in Config.SKILL_KEYS:
            press_key(k); time.sleep(2.0)
        press_combo(SC_CTRL, SC_G); time.sleep(2.0)
        self.last_skill_time = time.time()
        self._log("Skill tamamlandı.")

    def _log(self, msg):
        self._on_status(msg)
