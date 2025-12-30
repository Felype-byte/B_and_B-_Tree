# Script para gerar executável Windows com PyInstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GERADOR DE EXECUTÁVEL - Visualizador de Árvores B/B+" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se PyInstaller está instalado
Write-Host "Verificando PyInstaller..." -ForegroundColor Yellow
$pyinstallerInstalled = python -m pip show pyinstaller 2>$null

if (-not $pyinstallerInstalled) {
    Write-Host "PyInstaller não encontrado. Instalando..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    Write-Host ""
}

Write-Host "Gerando executável..." -ForegroundColor Green
Write-Host ""

# Opção 1: Pasta com arquivos (recomendado - mais rápido para executar)
Write-Host "Opção selecionada: Pasta com arquivos" -ForegroundColor Cyan
Write-Host "Comando: pyinstaller --windowed --name VisualizadorArvoresB run.py" -ForegroundColor Gray
Write-Host ""

python -m PyInstaller --clean --windowed `
    --name "VisualizadorArvoresB" `
    --icon NONE `
    --add-data "src;src" `
    run.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EXECUTÁVEL GERADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Localização: dist\VisualizadorArvoresB\" -ForegroundColor Yellow
Write-Host "Executável: dist\VisualizadorArvoresB\VisualizadorArvoresB.exe" -ForegroundColor Yellow
Write-Host ""
Write-Host "Testando executável..." -ForegroundColor Yellow

# Perguntar se quer testar
$test = Read-Host "Deseja testar o executável agora? (S/N)"

if ($test -eq "S" -or $test -eq "s") {
    Write-Host "Abrindo aplicação..." -ForegroundColor Green
    Start-Process "dist\VisualizadorArvoresB\VisualizadorArvoresB.exe"
} else {
    Write-Host "Você pode testar manualmente executando:" -ForegroundColor Cyan
    Write-Host "  dist\VisualizadorArvoresB\VisualizadorArvoresB.exe" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Testar o executável em outra máquina Windows" -ForegroundColor Yellow
Write-Host "2. Criar ZIP com:" -ForegroundColor Yellow
Write-Host "   - dist\VisualizadorArvoresB\" -ForegroundColor White
Write-Host "   - src\" -ForegroundColor White
Write-Host "   - tests\" -ForegroundColor White  
Write-Host "   - README.md" -ForegroundColor White
Write-Host "   - QUICKSTART.md" -ForegroundColor White
Write-Host "   - INSTRUÇÕES.txt" -ForegroundColor White
Write-Host "3. Enviar por e-mail conforme especificado" -ForegroundColor Yellow
Write-Host ""

Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
