"""
Testes manuais de Árvore B+.

Verifica operações básicas da B+ Tree e compara com B-Tree.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import BPlusTree, Tracer, Metrics, validate_bplustree, ValidationError


def test_basic_insertion():
    """Testa inserção básica em B+ Tree."""
    print("="*80)
    print("TESTE 1: Inserção Básica em B+ Tree")
    print("="*80)
    
    tracer = Tracer()
    tree = BPlusTree(fanout_n=3, tracer=tracer)
    
    print(f"\nÁrvore B+ criada: fanout={tree.fanout_n}, max_keys={tree.max_keys}")
    
    keys_to_insert = [10, 20, 30, 40, 50]
    
    for key in keys_to_insert:
        print(f"\n{'='*60}")
        print(f"Inserindo chave: {key}")
        print(f"{'='*60}")
        
        tracer.clear()
        success = tree.insert(key)
        print(f"Resultado: {'Sucesso' if success else 'Falha (duplicata)'}")
        
        # Validar árvore
        try:
            validate_bplustree(tree)
            print("✓ Validação: OK")
        except ValidationError as e:
            print(f"✗ Validação FALHOU: {e}")
            return False
        
        # Mostrar estrutura
        levels = tree.to_levels()
        print("\nÁrvore por níveis:")
        for i, level in enumerate(levels):
            print(f"  Nível {i}: {' '.join(level)}")
    
    # Testar varredura sequencial
    print("\n" + "="*60)
    print("Varredura Sequencial:")
    all_keys = tree.sequential_scan()
    print(f"Chaves em ordem: {all_keys}")
    
    if all_keys != sorted(keys_to_insert):
        print("✗ ERRO: Varredura sequencial não retornou chaves em ordem!")
        return False
    else:
        print("✓ Varredura sequencial OK")
    
    return True


def test_search_operations():
    """Testa operações de busca em B+ Tree."""
    print("\n" + "="*80)
    print("TESTE 2: Operações de Busca em B+ Tree")
    print("="*80)
    
    tracer = Tracer()
    tree = BPlusTree(fanout_n=4, tracer=tracer)
    
    # Inserir chaves (sem rastreamento)
    tracer.disable()
    keys = [50, 30, 70, 20, 40, 60, 80, 10, 25]
    for key in keys:
        tree.insert(key)
    tracer.enable()
    
    print(f"\nÁrvore com {len(keys)} chaves:")
    levels = tree.to_levels()
    for i, level in enumerate(levels):
        print(f"  Nível {i}: {' '.join(level)}")
    
    # Buscar chaves
    search_keys = [25, 70, 10, 100]
    
    for key in search_keys:
        print(f"\n{'-'*60}")
        print(f"Buscando chave: {key}")
        print(f"{'-'*60}")
        
        tracer.clear()
        result = tree.search(key)
        
        if result['found']:
            print(f"✓ ENCONTRADA na folha #{result['node_id']}, posição {result['index']}")
        else:
            print(f"✗ NÃO ENCONTRADA")
    
    return True


def test_range_query():
    """Testa range query em B+ Tree."""
    print("\n" + "="*80)
    print("TESTE 3: Range Query em B+ Tree")
    print("="*80)
    
    tree = BPlusTree(fanout_n=4)
    
    # Inserir chaves
    keys = list(range(10, 101, 10))  # 10, 20, 30, ..., 100
    for key in keys:
        tree.insert(key)
    
    print(f"\nÁrvore com chaves: {keys}")
    
    # Range queries
    test_ranges = [
        (20, 50),
        (10, 30),
        (60, 100),
        (25, 75)
    ]
    
    for start, end in test_ranges:
        result = tree.range_query(start, end)
        expected = [k for k in keys if start <= k <= end]
        
        print(f"\nRange [{start}, {end}]:")
        print(f"  Resultado: {result}")
        print(f"  Esperado: {expected}")
        
        if result == expected:
            print("  ✓ OK")
        else:
            print("  ✗ ERRO!")
            return False
    
    return True


def test_deletion():
    """Testa remoção em B+ Tree."""
    print("\n" + "="*80)
    print("TESTE 4: Remoção em B+ Tree")
    print("="*80)
    
    tracer = Tracer()
    tree = BPlusTree(fanout_n=3, tracer=tracer)
    
    # Inserir chaves
    keys = [10, 20, 30, 40, 50, 60, 70]
    for key in keys:
        tree.insert(key)
    
    print("\nÁrvore antes da remoção:")
    levels = tree.to_levels()
    for i, level in enumerate(levels):
        print(f"  Nível {i}: {' '.join(level)}")
    
    # Remover chave
    tracer.clear()
    success = tree.delete(40)
    
    print(f"\nRemoção de 40: {'Sucesso' if success else 'Falhou'}")
    
    try:
        validate_bplustree(tree)
        print("✓ Validação: OK")
    except ValidationError as e:
        print(f"✗ Validação FALHOU: {e}")
        return False
    
    print("\nÁrvore após remoção:")
    levels = tree.to_levels()
    for i, level in enumerate(levels):
        print(f"  Nível {i}: {' '.join(level)}")
    
    # Verificar varredura sequencial
    remaining = tree.sequential_scan()
    expected = [k for k in keys if k != 40]
    
    if remaining == expected:
        print(f"\n✓ Varredura sequencial OK: {remaining}")
        return True
    else:
        print(f"\n✗ ERRO: Esperado {expected}, obtido {remaining}")
        return False


def main():
    """Executa todos os testes de B+ Tree."""
    print("\n" + "="*80)
    print("TESTES DE ÁRVORE B+")
    print("="*80)
    
    tests = [
        ("Inserção Básica", test_basic_insertion),
        ("Operações de Busca", test_search_operations),
        ("Range Query", test_range_query),
        ("Remoção", test_deletion),
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
    print("RESUMO DOS TESTES DE B+ TREE")
    print("="*80)
    
    for test_name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{status:12s} | {test_name}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ TODOS OS TESTES DE B+ TREE PASSARAM!")
    else:
        print("✗ ALGUNS TESTES FALHARAM")
    print("="*80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
