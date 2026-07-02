# Metin2NesneTan-maYolo
# Metin2 Taş Botu v2.0

Metin2'de "metin taşı" avlamayı otomatikleştiren, ekran görüntüsü işleme ve nesne tespiti (YOLOv8 + Haar Cascade) tabanlı bir masaüstü bot. Windows üzerinde çalışan basit bir Tkinter arayüzü ile pencereni seçip botu başlatıp durdurabilirsin.

> ⚠️ **Uyarı:** Bu araç oyun içi eylemleri otomatikleştirir. Çoğu MMO'da (Metin2 dahil) botlama kullanım şartlarına aykırıdır ve hesabının banlanmasına yol açabilir. Sorumluluk tamamen kullanıcıya aittir; bu proje eğitim/araştırma amaçlı paylaşılmaktadır.

## Özellikler

- **Çift tespit motoru:** YOLOv8 modeli (`models/*.pt`) ve/veya Haar Cascade (`cascade.xml`), ikisi birlikte de kullanılabilir (`both` modu).
- **Pencere bazlı ekran yakalama:** `win32gui`/`win32ui` ile hedef pencereyi doğrudan yakalar; bulunamazsa `mss` ile tam ekran yakalamaya düşer.
- **Otomatik hedefleme:** Ekran merkezine en yakın taşı bulup tıklar, aynı hedefi tekrar tekrar tıklamayı `SAME_TARGET_THRESHOLD` ve `MAX_KILL_DURATION` ile sınırlar.
- **Otomatik loot ve skill atma:** Taş kırıldıktan sonra loot tuşuna basar; belirli aralıklarla skill kombolarını otomatik tetikler.
- **Ölüm/restart tespiti:** Şablon eşleştirme (`restart_button.png`) ile karakterin öldüğünü anlar ve yeniden doğma butonuna tıklar.
- **Keşif modu:** Ekranda hedef bulunamazsa karakteri ileri yürütüp döner.
- **DirectInput tabanlı girdi simülasyonu:** Fare tıklamaları ve tuş basışları `SendInput` API'si üzerinden, rastgele gecikmelerle gerçekleştirilir.
- **GUI kontrol paneli:** Pencere/model seçimi, canlı istatistikler (süre, kırılan taş sayısı), ayarlanabilir parametreler (saldırı süresi, cooldown, güven eşiği vb.) ve canlı konsol logu.
- **Debug modu:** Tespit kutularını ve seçilen hedefi gösteren canlı bir OpenCV penceresi açar.

## Proje Yapısı

```
metin2bot_final/
├── main.py            # Giriş noktası, gui.main() çağırır
├── gui.py              # Tkinter arayüzü (pencere/model seçici, ayarlar, log)
├── bot_core.py          # Ana bot döngüsü (tespit → hedefleme → tıklama → loot)
├── detector.py          # YOLOv8 + Cascade + şablon eşleştirme mantığı
├── screen.py            # HWND bazlı ekran yakalama (win32 / mss fallback)
├── input_utils.py        # DirectInput fare/klavye simülasyonu
├── config.py            # Tüm ayarlar (tuş kodları, eşikler, süreler)
├── cascade.xml           # Haar Cascade tespit modeli
├── models/              # YOLOv8 ağırlıkları (.pt)
├── images/              # Şablon eşleştirme referans görselleri
├── restart_button.png     # Ölüm sonrası "yeniden doğ" butonu şablonu
├── requirements.txt       # Python bağımlılıkları
└── calistir.bat          # Windows için otomatik kurulum + çalıştırma scripti
```

## Gereksinimler

- Windows (ekran yakalama ve girdi simülasyonu Windows API'lerine dayanır: `pywin32`, `SendInput`)
- Python 3.10+
- Bağımlılıklar (`requirements.txt`):
  - `opencv-python`
  - `numpy`
  - `mss`
  - `pywin32`
  - `ultralytics`

## Kurulum ve Çalıştırma

### Hızlı başlangıç (Windows)

`calistir.bat` dosyasına çift tıkla. Script otomatik olarak:
1. Python kurulu mu kontrol eder,
2. Gerekli kütüphaneler eksikse `pip install -r requirements.txt` ile kurar,
3. `main.py`'yi başlatır.

### Manuel kurulum

```bash
pip install -r requirements.txt
python main.py
```

## Kullanım

1. Botu başlatmadan önce Metin2'yi aç ve bir taş avlama bölgesine git.
2. GUI'de **Oyun Penceresi** açılır listesinden Metin2 penceresini seç (başlığında "metin" geçen pencere otomatik seçilir).
3. **Tespit Modeli** kısmından bir YOLO modeli (`models/*.pt`) ya da sadece cascade seç; tespit modunu (`both` / `yolo` / `cascade`) belirle.
4. **Ayarlar** sekmesinden saldırı süresi, tıklama cooldown'u, skill aralığı ve YOLO güven eşiği gibi parametreleri ihtiyacına göre ayarla.
5. **BAŞLAT** butonuna bas. Bot; ekranı tarar, en yakın taşı bulur, tıklar, loot alır ve gerektiğinde skill atar.
6. **DURDUR** butonuyla veya fareyi ekranın sol üst köşesine götürerek (failsafe) botu istediğin an durdurabilirsin.
7. **Konsol** sekmesinden canlı log akışını takip edebilirsin.

## Yapılandırma (`config.py`)

Önemli parametreler:

| Ayar | Açıklama |
|---|---|
| `DETECTION_MODE` | `"yolo"`, `"cascade"` veya `"both"` |
| `CONFIDENCE_THRESHOLD` | YOLO tespitleri için minimum güven skoru |
| `ATTACK_WAIT` | Tıklamadan sonra beklenecek süre (sn) |
| `CLICK_COOLDOWN` | İki tıklama arasındaki minimum süre (sn) |
| `MAX_KILL_DURATION` | Bir hedefe ayrılacak maksimum süre (sn) |
| `AUTO_LOOT` / `LOOT_KEY` | Otomatik loot açık/kapalı ve tuşu |
| `SKILL_INTERVAL` / `SKILL_KEYS` | Skill atma aralığı ve kullanılacak tuşlar |
| `DEBUG_MODE` | Tespit kutularını gösteren canlı görüntü penceresi |

Bu değerlerin çoğu GUI'nin **Ayarlar** sekmesinden de değiştirilebilir.

## Notlar

- `models/` klasöründeki `.pt` dosyaları farklı eğitim aşamalarına ait YOLOv8 ağırlıklarıdır; en güncel/performanslı olanı GUI'den seçebilirsin.
- Ekran yakalama önce pencere tabanlı (`win32`) modda dener; pencere bulunamazsa veya hata alınırsa otomatik olarak tam ekran (`mss`) moduna geçer.
- Girdi simülasyonu rastgele gecikmeler içerir; bu, sabit zamanlamalı bir botun daha kolay ayırt edilmesini önlemeye yöneliktir, ancak tespit edilmeyeceğinin garantisi yoktur.
