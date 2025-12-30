@echo off
echo ========================================
echo GERADOR DE EXECUTAVEL
echo Visualizador de Arvores B e B+
echo ========================================
echo.
echo Verificando PyInstaller...

python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    python -m pip install pyinstaller
)

echo.
echo Gerando executavel...
echo.

python -m PyInstaller --clean --windowed --name "VisualizadorArvoresB" run.py

echo.
echo ========================================
echo EXECUTAVEL GERADO!
echo ========================================
echo.
echo Localizacao: dist\VisualizadorArvoresB\
echo.
echo Pressione qualquer tecla para testar...
pause >nul

start dist\VisualizadorArvoresB\VisualizadorArvoresB.exe

echo.
echo Aplicacao aberta!
echo.
pause
