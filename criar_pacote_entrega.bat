@echo off
REM Script para criar pacote de entrega automaticamente

echo ========================================
echo CRIADOR DE PACOTE DE ENTREGA
echo Visualizador de Arvores B e B+
echo ========================================
echo.

REM Solicitar nomes dos alunos
set /p ALUNO1="Digite o nome do Aluno 1 (sem espacos): "
set /p ALUNO2="Digite o nome do Aluno 2 (sem espacos): "

set NOME_PACOTE=ImplementacaoArvoresB_%ALUNO1%_%ALUNO2%

echo.
echo Nome do pacote: %NOME_PACOTE%
echo.

REM Criar pasta de entrega
set PASTA_ENTREGA=E:\SGBD\ENTREGA
set PASTA_DESTINO=%PASTA_ENTREGA%\%NOME_PACOTE%

echo Criando pasta de entrega...
if not exist "%PASTA_ENTREGA%" mkdir "%PASTA_ENTREGA%"
if exist "%PASTA_DESTINO%" (
    echo Removendo versao antiga...
    rmdir /s /q "%PASTA_DESTINO%"
)
mkdir "%PASTA_DESTINO%"

echo.
echo Copiando arquivos...
echo.

REM Copiar dist (executavel)
echo [1/8] Copiando executavel...
xcopy "E:\SGBD\dist" "%PASTA_DESTINO%\dist\" /E /I /Q /Y

REM Copiar src (codigo-fonte)
echo [2/8] Copiando codigo-fonte...
xcopy "E:\SGBD\src" "%PASTA_DESTINO%\src\" /E /I /Q /Y

REM Copiar tests
echo [3/8] Copiando testes...
xcopy "E:\SGBD\tests" "%PASTA_DESTINO%\tests\" /E /I /Q /Y

REM Copiar documentacao
echo [4/8] Copiando README.md...
copy "E:\SGBD\README.md" "%PASTA_DESTINO%\" /Y >nul

echo [5/8] Copiando QUICKSTART.md...
copy "E:\SGBD\QUICKSTART.md" "%PASTA_DESTINO%\" /Y >nul

echo [6/8] Copiando INSTRUCOES.txt...
copy "E:\SGBD\INSTRUÇÕES.txt" "%PASTA_DESTINO%\" /Y >nul

REM Copiar launchers
echo [7/8] Copiando run.py...
copy "E:\SGBD\run.py" "%PASTA_DESTINO%\" /Y >nul

echo [8/8] Copiando run.bat...
copy "E:\SGBD\run.bat" "%PASTA_DESTINO%\" /Y >nul

echo.
echo ========================================
echo LIMPANDO ARQUIVOS DESNECESSARIOS
echo ========================================
echo.

REM Remover __pycache__
echo Removendo __pycache__...
for /d /r "%PASTA_DESTINO%" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM Remover .pyc
echo Removendo arquivos .pyc...
del /s /q "%PASTA_DESTINO%\*.pyc" 2>nul

echo.
echo ========================================
echo CRIANDO ARQUIVO ZIP
echo ========================================
echo.

REM Criar ZIP usando PowerShell
powershell -Command "Compress-Archive -Path '%PASTA_DESTINO%' -DestinationPath '%PASTA_ENTREGA%\%NOME_PACOTE%.zip' -Force"

echo.
echo ========================================
echo PACOTE CRIADO COM SUCESSO!
echo ========================================
echo.
echo Localizacao: %PASTA_ENTREGA%\%NOME_PACOTE%.zip
echo.

REM Mostrar tamanho do ZIP
for %%A in ("%PASTA_ENTREGA%\%NOME_PACOTE%.zip") do (
    set TAMANHO=%%~zA
)

echo Tamanho do ZIP: %TAMANHO% bytes
echo.

REM Calcular tamanho em MB
powershell -Command "$size = (Get-Item '%PASTA_ENTREGA%\%NOME_PACOTE%.zip').Length / 1MB; Write-Host \"Tamanho em MB: $([math]::Round($size, 2)) MB\" -ForegroundColor Yellow"

echo.
echo ========================================
echo PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Abrir: %PASTA_ENTREGA%
echo 2. Testar o executavel em outra maquina
echo 3. Enviar %NOME_PACOTE%.zip por e-mail
echo.

REM Perguntar se quer abrir a pasta
set /p ABRIR="Deseja abrir a pasta de entrega? (S/N): "
if /i "%ABRIR%"=="S" (
    explorer "%PASTA_ENTREGA%"
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul
