"""
Sistema de métricas para análise de desempenho.

Este módulo rastreia métricas como número de acessos a nós (leitura/escrita) e tempo
de execução de operações em lote.
"""

import time
from typing import Optional


class Metrics:
    """
    Rastreador de métricas de desempenho e I/O simulado.
    
    Contabiliza acessos a nós (leitura/escrita) e tempo de execução de operações.
    """
    
    def __init__(self):
        self.reads: int = 0   # Contador de leituras
        self.writes: int = 0  # Contador de escritas
        self.last_elapsed_ms: Optional[float] = None
        self._timer_start: Optional[float] = None
    
    def reset_accesses(self):
        """Zera os contadores de acessos a nós (I/O)."""
        self.reads = 0
        self.writes = 0
    
    def count_read(self):
        """Contabiliza leitura de bloco (acesso a nó)."""
        self.reads += 1

    def count_write(self):
        """Contabiliza escrita de bloco (modificação de nó)."""
        self.writes += 1
        
    def tick_node_access(self):
        """
        Incrementa o contador de acessos a nós.
        (Mantido para compatibilidade: conta como uma leitura).
        """
        self.count_read()
    
    def get_node_accesses(self) -> int:
        """
        Retorna o número total de acessos a nós.
        (Mantido para compatibilidade: retorna o total de leituras).
        """
        return self.reads
    
    def start_timer(self):
        """
        Inicia o cronômetro de alta precisão.
        """
        # [MODIFICADO] perf_counter é muito mais preciso que time()
        self._timer_start = time.perf_counter()
    
    def stop_timer(self) -> float:
        """
        Para o cronômetro e retorna o tempo decorrido.
        
        Returns:
            Tempo decorrido em milissegundos
        """
        if self._timer_start is None:
            return 0.0
        
        # [MODIFICADO] Calcula diferença com precisão
        elapsed = (time.perf_counter() - self._timer_start) * 1000  # converter para ms
        self.last_elapsed_ms = elapsed
        self._timer_start = None
        return elapsed
    
    def get_last_elapsed_ms(self) -> Optional[float]:
        """Retorna o tempo da última medição em milissegundos."""
        return self.last_elapsed_ms
    
    def reset_all(self):
        """Reseta todas as métricas."""
        self.reset_accesses()
        self.last_elapsed_ms = None
        self._timer_start = None