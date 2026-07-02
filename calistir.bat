@echo off
chcp 65001 >nul
title Metin2 Bot
cd /d "%~dp0"

echo.
echo  ====================================
echo       Metin2 Tas Botu v2.0
echo  ====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi!
    echo https://www.python.org adresinden Python 3.10+ kur.
    pause & exit /b 1
)

echo [OK] Python mevcut:
python --version

python -c "import cv2, ultralytics" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] Kutuphaneler kuruluyor, bir dakika bekle...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [HATA] Kurulum basarisiz!
        pause & exit /b 1
    )
    echo [OK] Kurulum tamamlandi.
)

echo.
echo [OK] Baslatiliyor...
echo      Durdurmak: GUI'deki DURDUR butonu
echo      Failsafe : fareyi sol ust koseye gotur
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [HATA] Bot beklenmedik sekilde kapandi!
    echo Konsol sekmesindeki log mesajlarini kontrol et.
)

pause
