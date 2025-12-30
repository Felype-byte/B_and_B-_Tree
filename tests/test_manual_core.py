"""
Testes manuais do core (BTree) antes da GUI.

Este arquivo valida o funcionamento básico das operações da árvore B
e o sistema de rastreamento de eventos.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import BTree, Tracer, Metrics, validate_btree, ValidationError, EventType


def print_tree_levels(tree):
    """Imprime a árvore por níveis."""
    levels = tree.to_levels()
    print("\nÁrvore por níveis:")
    for i, level in enumerate(levels):
        print(f"  Nível {i}: {' '.join(level)}")


def print_events(tracer):
    """Imprime os eventos rastreados."""
    events = tracer.get_events()
    print(f"\nEventos rastreados ({len(events)}):")
    for i, event in enumerate(events):
        print(f"  {i+1}. {event.type.value:20s} | Node #{event.node_id} | {event.info}")


def test_basic_operations():
    """Testa operações básicas de inserção e busca."""
    print("="*80)
    print("TESTE 1: Operações Básicas com n=3")
    print("="*80)
    
    # Criar árvore com fanout 3 (max_keys = 2)
    tracer = Tracer()
    metrics = Metrics()
    tree = BTree(fanout_n=3, tracer=tracer, metrics=metrics)
    
    print(f"\nÁrvore criada: fanout={tree.fanout_n}, max_keys={tree.max_keys}")
    
    # Sequência de inserções que causará splits
    keys_to_insert = [10, 20, 30, 40, 50, 25, 35, 15]
    
    for key in keys_to_insert:
        print(f"\n{'='*80}")
        print(f"Inserindo chave: {key}")
        print(f"{'='*80}")
        
        tracer.clear()
        metrics.reset_accesses()
        
        success = tree.insert(key)
        print(f"Resultado: {'Sucesso' if success else 'Falha (duplicata)'}")
        
        # Validar árvore
        try:
            validate_btree(tree)
            print("✓ Validação: OK")
        except ValidationError as e:
            print(f"✗ Validação FALHOU: {e}")
            return False
        
        # Mostrar estrutura
        print_tree_levels(tree)
        
        # Mostrar eventos
        print_events(tracer)
        
        print(f"Acessos a nós: {metrics.get_node_accesses()}")
    
    return True


def test_search_operations():
    """Testa operações de busca."""
    print("\n" + "="*80)
    print("TESTE 2: Operações de Busca")
    print("="*80)
    
    tracer = Tracer()
    metrics = Metrics()
    tree = BTree(fanout_n=4, tracer=tracer, metrics=metrics)
    
    # Inserir algumas chaves (sem rastreamento para economizar output)
    tracer.disable()
    keys = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45]
    for key in keys:
        tree.insert(key)
    tracer.enable()
    
    print(f"\nÁrvore com {len(keys)} chaves:")
    print_tree_levels(tree)
    
    # Buscar chaves existentes
    search_keys = [25, 70, 10, 100]
    
    for key in search_keys:
        print(f"\n{'-'*80}")
        print(f"Buscando chave: {key}")
        print(f"{'-'*80}")
        
        tracer.clear()
        metrics.reset_accesses()
        
        result = tree.search(key)
        
        if result['found']:
            print(f"✓ ENCONTRADA no nó #{result['node_id']}, posição {result['index']}")
        else:
            print(f"✗ NÃO ENCONTRADA")
        
        print(f"Acessos a nós: {metrics.get_node_accesses()}")
        print(f"Caminho percorrido: {result['path']}")
        
        # Verificar eventos detalhados
        events = tracer.get_events()
        visit_count = sum(1 for e in events if e.type == EventType.VISIT_NODE)
        compare_count = sum(1 for e in events if e.type == EventType.COMPARE_KEY)
        print(f"Eventos: {visit_count} visitas, {compare_count} comparações")
    
    return True


def test_duplicate_rejection():
    """Testa rejeição de duplicatas."""
    print("\n" + "="*80)
    print("TESTE 3: Rejeição de Duplicatas")
    print("="*80)
    
    tracer = Tracer()
    tree = BTree(fanout_n=3, tracer=tracer)
    
    # Inserir chaves
    keys = [10, 20, 30]
    for key in keys:
        tree.insert(key)
    
    print("\nÁrvore inicial:")
    print_tree_levels(tree)
    
    # Tentar inserir duplicatas
    for key in [10, 20, 30]:
        print(f"\nTentando inserir duplicata: {key}")
        success = tree.insert(key)
        if success:
            print(f"✗ ERRO: Duplicata {key} foi aceita!")
            return False
        else:
            print(f"✓ OK: Duplicata {key} foi rejeitada")
    
    return True


def test_different_fanouts():
    """Testa com diferentes valores de fanout."""
    print("\n" + "="*80)
    print("TESTE 4: Diferentes Fanouts")
    print("="*80)
    
    keys = list(range(1, 16))  # 1 a 15
    
    for fanout in [3, 4, 5]:
        print(f"\n{'-'*80}")
        print(f"Testando com fanout n={fanout} (max_keys={fanout-1})")
        print(f"{'-'*80}")
        
        tracer = Tracer()
        tracer.disable()  # Desabilitar para reduzir output
        
        tree = BTree(fanout_n=fanout, tracer=tracer)
        
        for key in keys:
            tree.insert(key)
        
        try:
            validate_btree(tree)
            print("✓ Validação: OK")
        except ValidationError as e:
            print(f"✗ Validação FALHOU: {e}")
            return False
        
        print_tree_levels(tree)
        
        # Contar nós
        all_nodes = tree.get_all_nodes()
        leaf_count = sum(1 for n in all_nodes if n.is_leaf)
        internal_count = len(all_nodes) - leaf_count
        
        print(f"Total de nós: {len(all_nodes)} ({internal_count} internos, {leaf_count} folhas)")
    
    return True


def main():
    """Executa todos os testes."""
    print("\n" + "="*80)
    print("TESTES MANUAIS DO CORE - ÁRVORE B")
    print("="*80)
    
    tests = [
        ("Operações Básicas", test_basic_operations),
        ("Operações de Busca", test_search_operations),
        ("Rejeição de Duplicatas", test_duplicate_rejection),
        ("Diferentes Fanouts", test_different_fanouts),
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
    print("RESUMO DOS TESTES")
    print("="*80)
    
    for test_name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{status:12s} | {test_name}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ TODOS OS TESTES PASSARAM!")
    else:
        print("✗ ALGUNS TESTES FALHARAM")
    print("="*80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
