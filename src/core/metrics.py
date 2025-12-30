"""
Sistema de métricas para análise de desempenho.

Este módulo rastreia métricas como número de acessos a nós e tempo
de execução de operações em lote.
"""

import time
from typing import Optional


class Metrics:
    """
    Rastreador de métricas de desempenho.
    
    Contabiliza acessos a nós e tempo de execução de operações.
    """
    
    def __init__(self):
        self.node_accesses: int = 0
        self.last_elapsed_ms: Optional[float] = None
        self._timer_start: Optional[float] = None
    
    def reset_accesses(self):
        """Zera o contador de acessos a nós."""
        self.node_accesses = 0
    
    def tick_node_access(self):
        """Incrementa o contador de acessos a nós."""
        self.node_accesses += 1
    
    def get_node_accesses(self) -> int:
        """Retorna o número total de acessos a nós."""
        return self.node_accesses
    
    def start_timer(self):
        """Inicia o cronômetro."""
        self._timer_start = time.time()
    
    def stop_timer(self) -> float:
        """
        Para o cronômetro e retorna o tempo decorrido.
        
        Returns:
            Tempo decorrido em milissegundos
        """
        if self._timer_start is None:
            return 0.0
        
        elapsed = (time.time() - self._timer_start) * 1000  # converter para ms
        self.last_elapsed_ms = elapsed
        self._timer_start = None
        return elapsed
    
    def get_last_elapsed_ms(self) -> Optional[float]:
        """Retorna o tempo da última medição em milissegundos."""
        return self.last_elapsed_ms
    
    def reset_all(self):
        """Reseta todas as métricas."""
        self.node_accesses = 0
        self.last_elapsed_ms = None
        self._timer_start = None
