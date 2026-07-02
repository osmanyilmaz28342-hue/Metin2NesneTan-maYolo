"""
detector.py — YOLOv8 + Cascade + Template matching.
"""

import cv2, os
import numpy as np
from config import Config


class Detection:
    def __init__(self, bbox, center, conf=1.0, source="cascade"):
        self.bbox   = bbox
        self.center = center
        self.conf   = conf
        self.source = source

    def distance_to(self, pt):
        return ((self.center[0]-pt[0])**2 + (self.center[1]-pt[1])**2) ** 0.5


class Detector:
    def __init__(self):
        self.yolo    = None
        self.cascade = None
        self._load()

    def _load(self):
        mode = Config.DETECTION_MODE
        if mode in ("yolo","both"):
            try:
                from ultralytics import YOLO
                if os.path.exists(Config.MODEL_PATH):
                    self.yolo = YOLO(Config.MODEL_PATH)
                    print(f"[OK] YOLO: {Config.MODEL_PATH}")
                else:
                    print(f"[!] Model bulunamadı: {Config.MODEL_PATH}")
            except ImportError:
                print("[!] ultralytics kurulu değil.")

        if mode in ("cascade","both"):
            if os.path.exists(Config.CASCADE_PATH):
                self.cascade = cv2.CascadeClassifier(Config.CASCADE_PATH)
                if self.cascade.empty():
                    self.cascade = None
                else:
                    print(f"[OK] Cascade: {Config.CASCADE_PATH}")
            else:
                print(f"[!] Cascade bulunamadı: {Config.CASCADE_PATH}")

    def detect(self, frame):
        results = []
        mode = Config.DETECTION_MODE
        if mode in ("yolo","both") and self.yolo:
            results = self._yolo(frame)
        if not results and mode in ("cascade","both") and self.cascade is not None:
            results = self._cascade(frame)
        return results

    def _yolo(self, frame):
        out = self.yolo(frame, conf=Config.CONFIDENCE_THRESHOLD, verbose=False)
        dets = []
        for r in out:
            for box in r.boxes:
                x1,y1,x2,y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                dets.append(Detection((x1,y1,x2,y2),((x1+x2)//2,(y1+y2)//2),conf,"yolo"))
        return dets

    def _cascade(self, frame):
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self.cascade.detectMultiScale(
            gray, scaleFactor=Config.CASCADE_SCALE,
            minNeighbors=Config.CASCADE_MIN_NEIGHBORS)
        if len(rects)==0: return []
        boxes = []
        for (x,y,w,h) in rects:
            boxes += [[x,y,w,h]]*2
        grouped,_ = cv2.groupRectangles(boxes, groupThreshold=1, eps=0.5)
        dets = []
        for (x,y,w,h) in grouped:
            dets.append(Detection((x,y,x+w,y+h),(x+w//2,y+h//2),1.0,"cascade"))
        return dets

    def find_template(self, frame, img_path, threshold=0.75):
        """images/ klasöründeki görseli ekranda arar."""
        if not img_path or not os.path.exists(img_path):
            return None
        try:
            tmpl = cv2.imread(img_path)
            if tmpl is None: return None
            res = cv2.matchTemplate(frame, tmpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold:
                h,w = tmpl.shape[:2]
                return (max_loc[0]+w//2, max_loc[1]+h//2)
        except: pass
        return None

    def nearest(self, dets, pt):
        if not dets: return None
        return min(dets, key=lambda d: d.distance_to(pt))

    def draw_debug(self, frame, dets, target=None):
        h,w = frame.shape[:2]
        c   = (w//2, h//2)
        for d in dets:
            x1,y1,x2,y2 = d.bbox
            col = (0,255,0) if d.source=="yolo" else (255,165,0)
            cv2.rectangle(frame,(x1,y1),(x2,y2),col,2)
            cv2.putText(frame,f"{d.source} {d.conf:.2f}",(x1,y1-5),
                        cv2.FONT_HERSHEY_SIMPLEX,0.45,col,1)
        if target:
            cv2.line(frame, c, target.center,(0,0,255),2)
            cv2.drawMarker(frame,target.center,(0,0,255),cv2.MARKER_CROSS,20,2)
        return frame
