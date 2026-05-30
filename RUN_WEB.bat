@echo off
echo ================================
echo     HSD AGENT - Web Version
echo ================================
echo.
echo Install dependencies...
pip install -r requirements.txt
echo.
echo Starting server...
echo.
echo Buka di browser: http://localhost:5000
echo Buka di HP     : http://[IP-PC-KAMU]:5000
echo.
echo Untuk cek IP PC: jalankan ipconfig di CMD
echo.
python app.py
pause
