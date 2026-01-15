@echo off
echo Gerando executavel...
python -m PyInstaller VisualizadorArvoresB.spec --noconfirm --clean
echo.
echo ==========================================
echo CONCLUIDO!
echo O executavel esta na pasta: dist\VisualizadorArvoresB\VisualizadorArvoresB.exe
echo ==========================================
pause
