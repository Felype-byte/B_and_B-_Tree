"""
Operações aleatórias em lote para testes de desempenho.

Fornece funções para gerar dados aleatórios e executar inserções/remoções
em lote com medição de métricas.
"""

import random
from typing import List, Set, Tuple, Any
from .btree import BTree
from .metrics import Metrics


def generate_unique_random_ints(count: int, lo: int, hi: int, 
                                 existing_set: Set[int]) -> List[int]:
    """
    Gera uma lista de inteiros aleatórios únicos.
    
    Args:
        count: Quantidade de números a gerar
        lo: Limite inferior (inclusive)
        hi: Limite superior (inclusive)
        existing_set: Conjunto de números já existentes (para evitar)
    
    Returns:
        Lista de inteiros únicos
    
    Raises:
        ValueError: Se não houver números suficientes disponíveis
    """
    available = hi - lo + 1 - len(existing_set)
    if count > available:
        raise ValueError(
            f"Não há números suficientes disponíveis. "
            f"Solicitado: {count}, disponível: {available}"
        )
    
    result = []
    attempts = 0
    max_attempts = count * 10  # Evitar loop infinito
    
    while len(result) < count and attempts < max_attempts:
        num = random.randint(lo, hi)
        if num not in existing_set and num not in result:
            result.append(num)
        attempts += 1
    
    if len(result) < count:
        # Fallback: gerar de forma determinística
        all_nums = set(range(lo, hi + 1)) - existing_set
        result = random.sample(list(all_nums), count)
    
    return result


def batch_insert(tree: BTree, values: List[Any]) -> Tuple[float, int]:
    """
    Insere uma lista de valores em lote e retorna métricas.
    
    Args:
        tree: Árvore onde inserir
        values: Lista de valores a inserir
    
    Returns:
        Tupla (tempo_em_ms, acessos_a_nos)
    """
    # Desabilitar tracer para operações em lote (performance)
    tracer_was_enabled = tree.tracer.enabled
    tree.tracer.disable()
    
    # Resetar e iniciar métricas
    initial_accesses = tree.metrics.get_node_accesses()
    tree.metrics.start_timer()
    
    # Inserir todos os valores
    for value in values:
        tree.insert(value)
    
    # Parar timer e calcular delta
    elapsed_ms = tree.metrics.stop_timer()
    final_accesses = tree.metrics.get_node_accesses()
    accesses_delta = final_accesses - initial_accesses
    
    # Restaurar estado do tracer
    if tracer_was_enabled:
        tree.tracer.enable()
    
    return elapsed_ms, accesses_delta


def choose_existing_keys(existing_keys: Set[Any], count: int) -> List[Any]:
    """
    Escolhe chaves existentes aleatoriamente para remoção.
    
    Args:
        existing_keys: Conjunto de chaves existentes na árvore
        count: Quantidade de chaves a escolher
    
    Returns:
        Lista de chaves escolhidas
    
    Note:
        Esta função será usada na implementação de remoção (Etapa futura)
    """
    if count > len(existing_keys):
        count = len(existing_keys)
    
    return random.sample(list(existing_keys), count)


def batch_remove(tree: BTree, values: List[Any]) -> Tuple[float, int]:
    """
    Remove uma lista de valores em lote e retorna métricas.
    
    Args:
        tree: Árvore de onde remover
        values: Lista de valores a remover
    
    Returns:
        Tupla (tempo_em_ms, acessos_a_nos)
    """
    # Desabilitar tracer para operações em lote (performance)
    tracer_was_enabled = tree.tracer.enabled
    tree.tracer.disable()
    
    # Resetar e iniciar métricas
    initial_accesses = tree.metrics.get_node_accesses()
    tree.metrics.start_timer()
    
    # Remover todos os valores
    removed_count = 0
    for value in values:
        if tree.delete(value):
            removed_count += 1
    
    # Parar timer e calcular delta
    elapsed_ms = tree.metrics.stop_timer()
    final_accesses = tree.metrics.get_node_accesses()
    accesses_delta = final_accesses - initial_accesses
    
    # Restaurar estado do tracer
    if tracer_was_enabled:
        tree.tracer.enable()
    
    return elapsed_ms, accesses_delta
