"""
gui.py — Pencere seçici + kontrol paneli.
"""

import tkinter as tk
from tkinter import ttk
import threading, time, os
from bot_core import BotCore
from config import Config
from screen import list_windows


class BotGUI:
    def __init__(self, root):
        self.root       = root
        self.bot        = None
        self.bot_thread = None
        self._windows   = []  # [(hwnd, title), ...]

        root.title("Metin2 Bot")
        root.geometry("520x600")
        root.resizable(False, False)

        self._build()
        self._refresh_windows()

    # ──────────────────────────────────────────
    # UI İNŞASI
    # ──────────────────────────────────────────
    def _build(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=8, pady=6)

        self._tab_main(nb)
        self._tab_settings(nb)
        self._tab_log(nb)

    # — Ana sekme ——————————————————————————————
    def _tab_main(self, nb):
        f = ttk.Frame(nb, padding=10)
        nb.add(f, text="  Ana Panel  ")

        # Başlık
        ttk.Label(f, text="🪨  Metin2 Taş Botu",
                  font=("Segoe UI", 15, "bold")).pack(pady=(0,8))

        # ── Pencere Seçici ──────────────────────
        wf = ttk.LabelFrame(f, text="Oyun Penceresi", padding=(8,6))
        wf.pack(fill="x", pady=4)

        self.var_window = tk.StringVar()
        self.cb_window  = ttk.Combobox(wf, textvariable=self.var_window,
                                       state="readonly", width=48)
        self.cb_window.pack(side="left", padx=(0,6))

        ttk.Button(wf, text="🔄", width=3,
                   command=self._refresh_windows).pack(side="left")

        # ── Model Seçici ───────────────────────
        mf = ttk.LabelFrame(f, text="Tespit Modeli", padding=(8,6))
        mf.pack(fill="x", pady=4)

        self.var_model = tk.StringVar()
        self.cb_model  = ttk.Combobox(mf, textvariable=self.var_model,
                                      state="readonly", width=40)
        self.cb_model.pack(side="left", padx=(0,6))
        self._refresh_models()

        mode_f = ttk.Frame(mf)
        mode_f.pack(side="left")
        self.var_mode = tk.StringVar(value="both")
        for m in ("both","yolo","cascade"):
            ttk.Radiobutton(mode_f, text=m, variable=self.var_mode,
                            value=m).pack(side="left", padx=2)

        # ── İstatistikler ──────────────────────
        sf = ttk.LabelFrame(f, text="İstatistikler", padding=(8,6))
        sf.pack(fill="x", pady=4)

        self.lbl_time   = ttk.Label(sf, text="Süre        :  00:00:00",
                                    font=("Consolas",11))
        self.lbl_time.pack(anchor="w")
        self.lbl_stones = ttk.Label(sf, text="Kırılan Taş :  0",
                                    font=("Consolas",11))
        self.lbl_stones.pack(anchor="w")
        self.lbl_status = ttk.Label(sf, text="Durum       :  Hazır",
                                    font=("Consolas",10), foreground="gray")
        self.lbl_status.pack(anchor="w")

        # ── Butonlar ──────────────────────────
        bf = ttk.Frame(f)
        bf.pack(pady=14)

        self.btn_start = ttk.Button(bf, text="▶  BAŞLAT", width=16,
                                    command=self._start)
        self.btn_start.pack(side="left", padx=8)

        self.btn_stop = ttk.Button(bf, text="■  DURDUR", width=16,
                                   command=self._stop, state="disabled")
        self.btn_stop.pack(side="left", padx=8)

        ttk.Label(f, text="Failsafe: fareyi sol üst köşeye götür → bot durur",
                  font=("Arial",8), foreground="gray").pack(side="bottom", pady=4)

    # — Ayarlar sekmesi ———————————————————————
    def _tab_settings(self, nb):
        f = ttk.Frame(nb, padding=12)
        nb.add(f, text="  Ayarlar  ")

        def row(parent, label, var, **kw):
            r = ttk.Frame(parent); r.pack(fill="x", pady=3)
            ttk.Label(r, text=label, width=26, anchor="w").pack(side="left")
            ttk.Entry(r, textvariable=var, **kw).pack(side="left")
            return r

        self.var_attack  = tk.StringVar(value=str(Config.ATTACK_WAIT))
        self.var_conf    = tk.StringVar(value=str(Config.CONFIDENCE_THRESHOLD))
        self.var_cooldown= tk.StringVar(value=str(Config.CLICK_COOLDOWN))
        self.var_skill   = tk.StringVar(value=str(Config.SKILL_INTERVAL))

        gf = ttk.LabelFrame(f, text="Genel", padding=(8,6)); gf.pack(fill="x", pady=4)
        row(gf, "Saldırı süresi (s):",   self.var_attack,   width=6)
        row(gf, "Tıklama cooldown (s):", self.var_cooldown, width=6)
        row(gf, "Skill aralığı (s):",    self.var_skill,    width=6)

        df = ttk.LabelFrame(f, text="Tespit", padding=(8,6)); df.pack(fill="x", pady=4)
        row(df, "YOLO güven eşiği:",     self.var_conf,     width=6)

        lf = ttk.LabelFrame(f, text="Diğer", padding=(8,6)); lf.pack(fill="x", pady=4)
        self.var_loot  = tk.BooleanVar(value=Config.AUTO_LOOT)
        self.var_debug = tk.BooleanVar(value=Config.DEBUG_MODE)
        ttk.Checkbutton(lf, text="Otomatik Loot (Q tuşu)",
                        variable=self.var_loot).pack(anchor="w")
        ttk.Checkbutton(lf, text="Debug modu (tespit kutularını göster)",
                        variable=self.var_debug).pack(anchor="w")

    # — Log sekmesi ——————————————————————————
    def _tab_log(self, nb):
        f = ttk.Frame(nb, padding=6)
        nb.add(f, text="  Konsol  ")

        self.log_box = tk.Text(f, height=28, font=("Consolas",9),
                               state="disabled", bg="#1e1e1e", fg="#d4d4d4",
                               insertbackground="white")
        self.log_box.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(f, command=self.log_box.yview)
        self.log_box["yscrollcommand"] = sb.set

        ttk.Button(f, text="Temizle",
                   command=self._clear_log).pack(side="right", pady=4)

    # ──────────────────────────────────────────
    # PENCERE / MODEL YENİLEME
    # ──────────────────────────────────────────
    def _refresh_windows(self):
        self._windows = list_windows()
        titles = [t for (_,t) in self._windows]
        self.cb_window["values"] = titles
        # Metin2 otomatik seç
        for i, t in enumerate(titles):
            if "metin" in t.lower() or "metin2" in t.lower():
                self.cb_window.current(i)
                return
        if titles:
            self.cb_window.current(0)

    def _refresh_models(self):
        pts = []
        if os.path.isdir("models"):
            pts = [f"models/{f}" for f in os.listdir("models") if f.endswith(".pt")]
        pts.append("cascade_only")
        self.cb_model["values"] = pts
        # varsayılan: best1.pt varsa onu seç (daha hızlı)
        for i,p in enumerate(pts):
            if "best1" in p or "yolov8n" in p:
                self.cb_model.current(i); return
        if pts: self.cb_model.current(0)

    # ──────────────────────────────────────────
    # KONTROL
    # ──────────────────────────────────────────
    def _start(self):
        # Pencere seç
        sel_title = self.var_window.get()
        hwnd = None
        for (h, t) in self._windows:
            if t == sel_title:
                hwnd = h; break

        if not hwnd:
            self._set_status("Pencere seçilmedi!")
            return

        # Config güncelle
        Config.WINDOW_HWND           = hwnd
        Config.WINDOW_TITLE          = sel_title
        Config.DETECTION_MODE        = self.var_mode.get()
        Config.DEBUG_MODE            = self.var_debug.get()
        Config.AUTO_LOOT             = self.var_loot.get()

        model = self.var_model.get()
        if model == "cascade_only":
            Config.DETECTION_MODE = "cascade"
        else:
            Config.MODEL_PATH     = model

        try: Config.ATTACK_WAIT           = float(self.var_attack.get())
        except: pass
        try: Config.CLICK_COOLDOWN        = float(self.var_cooldown.get())
        except: pass
        try: Config.SKILL_INTERVAL        = float(self.var_skill.get())
        except: pass
        try: Config.CONFIDENCE_THRESHOLD  = float(self.var_conf.get())
        except: pass

        self.bot = BotCore(on_status=self._set_status, on_stats=self._set_stats)

        if not self.bot.initialize():
            self._set_status("Başlatma başarısız!")
            return

        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self._set_status(f"Çalışıyor → {sel_title}")

        self.bot_thread = threading.Thread(
            target=self.bot.run, args=(Config.ATTACK_WAIT,), daemon=True)
        self.bot_thread.start()

    def _stop(self):
        if self.bot: self.bot.stop()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self._set_status("Durduruldu.")

    # ──────────────────────────────────────────
    # GÜNCELLEME
    # ──────────────────────────────────────────
    def _set_status(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.root.after(0, lambda: (
            self.lbl_status.config(text=f"Durum       :  {msg}"),
            self._append_log(f"[{ts}] {msg}")
        ))

    def _set_stats(self, n, elapsed):
        m,s = divmod(int(elapsed),60)
        h,m = divmod(m,60)
        ts  = f"{h:02}:{m:02}:{s:02}"
        self.root.after(0, lambda: (
            self.lbl_time.config(text=f"Süre        :  {ts}"),
            self.lbl_stones.config(text=f"Kırılan Taş :  {n}"),
        ))

    def _append_log(self, text):
        self.log_box.config(state="normal")
        self.log_box.insert("end", text+"\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0","end")
        self.log_box.config(state="disabled")


def main():
    root = tk.Tk()
    BotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
