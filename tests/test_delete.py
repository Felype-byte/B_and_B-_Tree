"""
Testes de deleção para Árvore B.

Verifica operações de remoção com diferentes cenários.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import BTree, Tracer, Metrics, validate_btree, ValidationError, EventType


def test_delete_from_leaf():
    """Testa remoção de chave em folha sem underflow."""
    print("="*80)
    print("TESTE: Remoção de Folha Simples")
    print("="*80)
    
    tracer = Tracer()
    tree = BTree(fanout_n=3, tracer=tracer)
    
    # Inserir chaves
    for key in [10, 20, 30, 40, 50]:
        tree.insert(key)
    
    print("\nÁrvore antes da remoção:")
    levels = tree.to_levels()
    for i, level in enumerate(levels):
        print(f"  Nível {i}: {' '.join(level)}")
    
    # Remover chave de folha
    tracer.clear()
    success = tree.delete(40)
    
    print(f"\nRemoção de 40: {'Sucesso' if success else 'Falhou'}")
    
    try:
        validate_btree(tree)
        print("✓ Validação: OK")
    except ValidationError as e:
        print(f"✗ Validação FALHOU: {e}")
        return False
    
    print("\nÁrvore após remoção:")
    levels = tree.to_levels()
    for i, level in enumerate(levels):
        print(f"  Nível {i}: {' '.join(level)}")
    
    # Verificar eventos
    events = tracer.get_events()
    print(f"\nEventos: {len(events)}")
    for event in events:
        print(f"  - {event.type.value}: {event.info}")
    
    return True


def test_delete_with_merge():
    """Testa remoção que causa merge."""
    print("\n" + "="*80)
    print("TESTE: Remoção com Merge")
    print("="*80)
    
    tracer = Tracer()
    tree = BTree(fanout_n=3, tracer=tracer)
    
    # Criar árvore que permita merge
    for key in [10, 20, 30, 40, 50, 60, 70]:
        tree.insert(key)
    
    print("\nÁrvore antes da remoção:")
    levels = tree.to_levels()
    for i, level in enumerate(levels):
        print(f"  Nível {i}: {' '.join(level)}")
    
    # Remover para causar underflow e merge
    tracer.clear()
    success = tree.delete(50)
    
    print(f"\nRemoção de 50: {'Sucesso' if success else 'Falhou'}")
    
    try:
        validate_btree(tree)
        print("✓ Validação: OK")
    except ValidationError as e:
        print(f"✗ Validação FALHOU: {e}")
        return False
    
    print("\nÁrvore após remoção:")
    levels = tree.to_levels()
    for i, level in enumerate(levels):
        print(f"  Nível {i}: {' '.join(level)}")
    
    # Verificar se houve merge
    events = tracer.get_events()
    merge_events = [e for e in events if e.type == EventType.MERGE]
    print(f"\nEventos de MERGE: {len(merge_events)}")
    
    return True


def test_delete_nonexistent():
    """Testa remoção de chave que não existe."""
    print("\n" + "="*80)
    print("TESTE: Remoção de Chave Inexistente")
    print("="*80)
    
    tracer = Tracer()
    tree = BTree(fanout_n=3, tracer=tracer)
    
    for key in [10, 20, 30]:
        tree.insert(key)
    
    # Tentar remover chave inexistente
    success = tree.delete(99)
    
    print(f"\nTentativa de remover 99: {'Sucesso' if success else 'Falhou (esperado)'}")
    
    if not success:
        print("✓ OK: Chave inexistente não foi removida")
        return True
    else:
        print("✗ ERRO: Chave inexistente foi considerada removida!")
        return False


def main():
    """Executa todos os testes de deleção."""
    print("\n" + "="*80)
    print("TESTES DE DELEÇÃO - ÁRVORE B")
    print("="*80)
    
    tests = [
        ("Remoção de Folha Simples", test_delete_from_leaf),
        ("Remoção com Merge", test_delete_with_merge),
        ("Remoção de Chave Inexistente", test_delete_nonexistent),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ EXCEÇÃO em {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "="*80)
    print("RESUMO DOS TESTES DE DELEÇÃO")
    print("="*80)
    
    for test_name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{status:12s} | {test_name}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ TODOS OS TESTES DE DELEÇÃO PASSARAM!")
    else:
        print("✗ ALGUNS TESTES FALHARAM")
    print("="*80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
