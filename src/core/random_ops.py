"""
Módulo: core.random_ops
Utilitários para operações em lote (Batch Operations).

Suporta:
- Geração de Números Inteiros
- Geração de Strings
- Inserção e Remoção em Lote para B-Tree e B+ Tree
"""
import random
import time
import string
from typing import List, Set, Tuple, Any

# =============================================================================
# GERADORES DE DADOS
# =============================================================================

def generate_unique_random_ints(count: int, min_val: int, max_val: int, 
                                existing_keys: Set[Any]) -> List[int]:
    """
    Gera uma lista de inteiros aleatórios únicos que ainda não existem na árvore.
    """
    candidates = set()
    
    # Proteção: intervalo inválido ou pequeno demais
    try:
        range_size = max_val - min_val + 1
        if range_size < count:
            return [] 
    except TypeError:
        return []

    needed = count
    attempts = 0
    max_attempts = count * 50
    
    while len(candidates) < needed and attempts < max_attempts:
        val = random.randint(min_val, max_val)
        if val not in existing_keys and val not in candidates:
            candidates.add(val)
        attempts += 1
        
    return list(candidates)

def generate_random_strings(count: int, length: int, existing_keys: Set[Any]) -> List[str]:
    """
    Gera uma lista de strings aleatórias únicas (Letras Maiúsculas).
    """
    candidates = set()
    attempts = 0
    max_attempts = count * 50
    
    while len(candidates) < count and attempts < max_attempts:
        # Gera string aleatória ex: "ABC"
        s = ''.join(random.choices(string.ascii_uppercase, k=length))
        
        if s not in existing_keys and s not in candidates:
            candidates.add(s)
        attempts += 1
        
    return list(candidates)

def choose_existing_keys(existing_keys: Set[Any], count: int) -> List[Any]:
    """
    Sorteia N chaves do conjunto de chaves existentes para remoção.
    Funciona para qualquer tipo (int ou str).
    """
    if not existing_keys:
        return []
    
    # Se pedir para remover mais do que existe, retorna tudo o que tem
    k = min(count, len(existing_keys))
    
    return random.sample(list(existing_keys), k)


# EXECUTORES DE LOTE (BATCH)


def batch_insert(tree, keys: List[Any]) -> Tuple[float, int]:
    """
    Insere uma lista de valores em lote.
    
    Args:
        tree: Instância da BTree ou BPlusTree (Duck Typing)
        keys: Lista de chaves a inserir
        
    Returns:
        Tuple: (tempo_ms, total_io_ops)
    """
    # Desabilitar tracer visual para performance máxima durante o lote
    tracer_was_enabled = getattr(tree.tracer, 'enabled', False)
    if hasattr(tree.tracer, 'disable'):
        tree.tracer.disable()
    
    # Resetar métricas de acesso para contar apenas esta operação
    tree.metrics.reset_accesses()
    
    start = time.perf_counter()
    
    for k in keys:
        tree.insert(k)
    
    end = time.perf_counter()
    
    # Restaurar estado do tracer
    if tracer_was_enabled and hasattr(tree.tracer, 'enable'):
        tree.tracer.enable()
        
    total_time = (end - start) * 1000
    total_ops = tree.metrics.reads + tree.metrics.writes
    
    return total_time, total_ops

def batch_remove(tree, keys: List[Any]) -> Tuple[float, int, int]:
    """
    Remove uma lista de valores em lote.
    
    Args:
        tree: Instância da BTree ou BPlusTree
        keys: Lista de chaves a remover
        
    Returns:
        Tuple: (tempo_ms, total_io_ops, qtd_sucesso)
    """
    tracer_was_enabled = getattr(tree.tracer, 'enabled', False)
    if hasattr(tree.tracer, 'disable'):
        tree.tracer.disable()
    
    tree.metrics.reset_accesses()
    
    start = time.perf_counter()
    success_count = 0
    
    for k in keys:
        if tree.delete(k):
            success_count += 1
            
    end = time.perf_counter()
    
    if tracer_was_enabled and hasattr(tree.tracer, 'enable'):
        tree.tracer.enable()
        
    total_time = (end - start) * 1000
    total_ops = tree.metrics.reads + tree.metrics.writes
    
    return total_time, total_ops, success_count