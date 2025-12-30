"""
Script de inicialização do Visualizador de Árvores B e B+.
Execute este arquivo para abrir a aplicação.
"""

import sys
import os

# Adicionar src ao path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Importar e executar aplicação
from app import main

if __name__ == "__main__":
    print("=" * 60)
    print("VISUALIZADOR DE ÁRVORES B E B+")
    print("=" * 60)
    print("\nIniciando interface gráfica...")
    print("Aguarde a janela abrir...\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAplicação fechada pelo usuário.")
    except Exception as e:
        print(f"\n\nErro ao executar aplicação: {e}")
        import traceback
        traceback.print_exc()
