"""
Sistema de rastreamento de eventos para visualização passo a passo.

Este módulo fornece o modelo de eventos e a classe Tracer para capturar
cada passo da execução das operações na árvore (busca, inserção, etc.).
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class EventType(Enum):
    """Tipos de eventos rastreados durante operações na árvore."""
    VISIT_NODE = "visit_node"           # Entrou em um nó
    COMPARE_KEY = "compare_key"         # Comparou com uma chave específica
    DESCEND = "descend"                 # Decidiu descer para um filho
    INSERT_IN_LEAF = "insert_in_leaf"   # Inseriu chave em uma folha
    SPLIT_NODE = "split_node"           # Fez split de um nó
    NEW_ROOT = "new_root"               # Criou nova raiz
    SEARCH_FOUND = "search_found"       # Busca encontrou a chave
    SEARCH_NOT_FOUND = "search_not_found"  # Busca não encontrou
    
    # Eventos de deleção
    DELETE_REQUEST = "delete_request"   # Solicitação de remoção
    DELETE_FOUND = "delete_found"       # Chave encontrada para remoção
    DELETE_IN_LEAF = "delete_in_leaf"   # Remover chave de folha
    REPLACE_WITH_PREDECESSOR = "replace_with_predecessor"  # Substituir por predecessor
    UNDERFLOW = "underflow"             # Nó ficou abaixo do mínimo
    REDISTRIBUTE = "redistribute"       # Redistribuição entre irmãos
    MERGE = "merge"                     # Merge de nós
    SHRINK_ROOT = "shrink_root"         # Raiz encolheu (altura diminuiu)


@dataclass
class Event:
    """
    Representa um evento durante a execução de uma operação.
    
    Attributes:
        type: Tipo do evento (EventType)
        node_id: ID do nó envolvido
        info: Informações adicionais específicas do evento
        op_id: ID da operação (opcional, para agrupar eventos)
    """
    type: EventType
    node_id: Optional[int]
    info: Dict[str, Any]
    op_id: Optional[int] = None
    
    def __repr__(self):
        return f"Event({self.type.value}, node={self.node_id}, info={self.info})"


class Tracer:
    """
    Rastreador de eventos para operações na árvore.
    
    Captura cada passo da execução (visitas a nós, comparações, splits, etc.)
    para permitir visualização passo a passo na UI.
    """
    
    def __init__(self):
        self.events: List[Event] = []
        self.enabled: bool = True
        self.current_op_id: int = 0
    
    def clear(self):
        """Limpa todos os eventos registrados."""
        self.events = []
        self.current_op_id += 1
    
    def emit(self, event_type: EventType, node_id: Optional[int] = None, 
             info: Optional[Dict[str, Any]] = None):
        """
        Emite um novo evento.
        
        Args:
            event_type: Tipo do evento
            node_id: ID do nó envolvido (se aplicável)
            info: Informações adicionais do evento
        """
        if not self.enabled:
            return
        
        event = Event(
            type=event_type,
            node_id=node_id,
            info=info or {},
            op_id=self.current_op_id
        )
        self.events.append(event)
    
    def get_events(self) -> List[Event]:
        """Retorna todos os eventos registrados."""
        return self.events.copy()
    
    def get_event_count(self) -> int:
        """Retorna o número de eventos registrados."""
        return len(self.events)
    
    def enable(self):
        """Ativa o rastreamento de eventos."""
        self.enabled = True
    
    def disable(self):
        """Desativa o rastreamento de eventos (útil para operações em lote)."""
        self.enabled = False
