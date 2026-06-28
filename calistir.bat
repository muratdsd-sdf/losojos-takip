@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Los Ojos veri toplama basliyor...
echo.
python collector.py
if errorlevel 1 (
  echo.
  echo Python bulunamadi veya hata olustu.
  echo Python kurulu degilse once python.org adresinden kurun.
)
echo.
echo ----- Bitti. Bu pencereyi kapatabilirsiniz. -----
pause
