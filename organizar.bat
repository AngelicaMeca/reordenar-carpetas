@echo off
chcp 65001 >nul
rem Doble clic: ordena Descargas.
rem Arrastrar una carpeta sobre este archivo: ordena esa carpeta.
python "%~dp0organizar.py" %*
pause
