@echo off
title PathFinder AI - Calistirma Sihirbazi
color 0B
echo =================================================================
echo        PathFinder AI - Akilli Kariyer Planlama Asistani
echo =================================================================
echo.

:: Check Virtual Environment
if not exist venv (
    echo [ BILGI ] Sanal ortam (venv) bulunamadi. Olusturuluyor...
    python -m venv venv
    if errorlevel 1 (
        echo [ HATA ] Python yuklu veya PATH degiskenine ekli olmayabilir!
        pause
        exit /b
    )
    echo [ BILGI ] Sanal ortam olusturuldu. Aktif ediliyor...
    call venv\Scripts\activate
    echo [ BILGI ] Kutuphaneler yukleniyor (Bu islem birkac dakika surebilir)...
    pip install -r requriments.txt
) else (
    echo [ BILGI ] Sanal ortam (venv) tespit edildi. Aktif ediliyor...
    call venv\Scripts\activate
)

:: Check .env Config
if not exist .env (
    echo [ UYARI ] .env dosyasi bulunamadi! .env_example kopyalaniyor...
    copy .env_example .env
    echo.
    echo -------------------------------------------------------------
    echo [ UYARI ] Lutfen yeni olusturulan .env dosyasini acin ve 
    echo          OPENAI_API_KEY anahtarinizi ekleyin.
    echo -------------------------------------------------------------
    echo.
)

echo [ BASARILI ] Sistem hazir! Sunucu baslatiliyor...
echo.
echo >> Tarayicinizdan su adrese gidin: http://127.0.0.1:5000
echo.
python main.py
pause
