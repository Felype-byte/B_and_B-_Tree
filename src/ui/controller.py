"""
Controlador de reprodução passo a passo de eventos.

Gerencia a navegação através dos eventos rastreados (trace) e
fornece informações de highlighting para a UI.
"""

from typing import List, Optional, Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.trace import Event, EventType


class StepController:
    """
    Controla a reprodução passo a passo dos eventos rastreados.
    """
    
    def __init__(self):
        self.events: List[Event] = []
        self.current_index: int = -1
        self.is_playing: bool = False
    
    def load_events(self, events: List[Event]):
        """
        Carrega uma lista de eventos para reprodução.
        
        Args:
            events: Lista de eventos do tracer
        """
        self.events = events.copy()
        self.current_index = -1 if len(events) == 0 else 0
        self.is_playing = False
    
    def has_events(self) -> bool:
        """Retorna True se há eventos carregados."""
        return len(self.events) > 0
    
    def can_step_next(self) -> bool:
        """Retorna True se pode avançar para o próximo evento."""
        return self.current_index < len(self.events) - 1
    
    def can_step_prev(self) -> bool:
        """Retorna True se pode voltar para o evento anterior."""
        return self.current_index > 0
    
    def step_next(self) -> Optional[Dict[str, Any]]:
        """
        Avança para o próximo evento.
        
        Returns:
            Informações de highlighting ou None se não houver próximo evento
        """
        if not self.can_step_next():
            return None
        
        self.current_index += 1
        return self.get_current_highlight()
    
    def step_prev(self) -> Optional[Dict[str, Any]]:
        """
        Volta para o evento anterior.
        
        Returns:
            Informações de highlighting ou None se não houver evento anterior
        """
        if not self.can_step_prev():
            return None
        
        self.current_index -= 1
        return self.get_current_highlight()
    
    def reset(self):
        """Volta para o início da sequência de eventos."""
        if len(self.events) > 0:
            self.current_index = 0
    
    def go_to_end(self):
        """Vai para o último evento."""
        if len(self.events) > 0:
            self.current_index = len(self.events) - 1
    
    def get_current_event(self) -> Optional[Event]:
        """Retorna o evento atual."""
        if 0 <= self.current_index < len(self.events):
            return self.events[self.current_index]
        return None
    
    def get_current_highlight(self) -> Dict[str, Any]:
        """
        Converte o evento atual em informações de highlighting.
        
        Returns:
            Dicionário com informações para destacar na UI:
            - node_id: ID do nó a destacar
            - key_index: Índice da chave a destacar (opcional)
            - descend_from, descend_to: Para destacar arestas (opcional)
            - message: Mensagem descritiva do evento
        """
        event = self.get_current_event()
        if event is None:
            return {}
        
        highlight = {
            'node_id': event.node_id,
            'event_type': event.type.value
        }
        
        # Construir mensagem e informações específicas por tipo de evento
        if event.type == EventType.VISIT_NODE:
            highlight['message'] = f"Visitando nó #{event.node_id}"
            if 'keys' in event.info:
                highlight['message'] += f" - Chaves: {event.info['keys']}"
        
        elif event.type == EventType.COMPARE_KEY:
            key_index = event.info.get('key_index', 0)
            node_key = event.info.get('node_key')
            target_key = event.info.get('target_key')
            
            highlight['key_index'] = key_index
            highlight['message'] = (
                f"Comparando chave #{key_index}: {node_key} com {target_key}"
            )
        
        elif event.type == EventType.DESCEND:
            child_index = event.info.get('child_index', 0)
            target_key = event.info.get('target_key')
            
            highlight['message'] = (
                f"Descendo para filho #{child_index} (buscando {target_key})"
            )
            # Nota: descend_to seria preenchido pela UI se souber qual é o filho
        
        elif event.type == EventType.INSERT_IN_LEAF:
            key = event.info.get('key')
            position = event.info.get('position', 0)
            
            highlight['key_index'] = position
            highlight['message'] = (
                f"Inserindo {key} na posição {position} da folha #{event.node_id}"
            )
        
        elif event.type == EventType.SPLIT_NODE:
            promoted_key = event.info.get('promoted_key')
            left_id = event.info.get('left_id')
            right_id = event.info.get('right_id')
            
            highlight['message'] = (
                f"Split do nó #{event.node_id}: promovendo {promoted_key}, "
                f"criando nós #{left_id} e #{right_id}"
            )
        
        elif event.type == EventType.NEW_ROOT:
            old_root_id = event.info.get('old_root_id')
            promoted_key = event.info.get('promoted_key')
            
            highlight['message'] = (
                f"Criando nova raiz #{event.node_id} com chave {promoted_key} "
                f"(antiga raiz: #{old_root_id})"
            )
        
        elif event.type == EventType.SEARCH_FOUND:
            key = event.info.get('key')
            index = event.info.get('index', 0)
            
            highlight['key_index'] = index
            highlight['message'] = (
                f"✓ Chave {key} encontrada no nó #{event.node_id} "
                f"na posição {index}"
            )
        
        elif event.type == EventType.SEARCH_NOT_FOUND:
            key = event.info.get('key')
            highlight['message'] = f"✗ Chave {key} não encontrada"
        
        # Eventos de deleção
        elif event.type == EventType.DELETE_REQUEST:
            key = event.info.get('key')
            highlight['message'] = f"🗑️ Solicitando remoção da chave {key}"
        
        elif event.type == EventType.DELETE_FOUND:
            key = event.info.get('key')
            key_index = event.info.get('key_index', 0)
            
            highlight['key_index'] = key_index
            highlight['message'] = (
                f"✓ Chave {key} encontrada no nó #{event.node_id} "
                f"na posição {key_index} (será removida)"
            )
        
        elif event.type == EventType.DELETE_IN_LEAF:
            key = event.info.get('key')
            key_index = event.info.get('key_index', 0)
            
            highlight['key_index'] = key_index
            highlight['message'] = (
                f"Removendo {key} da posição {key_index} da folha #{event.node_id}"
            )
        
        elif event.type == EventType.REPLACE_WITH_PREDECESSOR:
            key = event.info.get('key')
            predecessor = event.info.get('predecessor')
            key_index = event.info.get('key_index', 0)
            
            highlight['key_index'] = key_index
            highlight['message'] = (
                f"Substituindo {key} por predecessor {predecessor} "
                f"no nó #{event.node_id}"
            )
        
        elif event.type == EventType.UNDERFLOW:
            num_keys = event.info.get('num_keys', 0)
            min_keys = event.info.get('min_keys', 0)
            
            highlight['message'] = (
                f"⚠️ Underflow no nó #{event.node_id}: "
                f"{num_keys} chaves (mínimo: {min_keys})"
            )
        
        elif event.type == EventType.REDISTRIBUTE:
            from_node = event.info.get('from_node')
            to_node = event.info.get('to_node')
            
            highlight['message'] = (
                f"Redistribuindo chaves: nó #{from_node} → nó #{to_node}"
            )
        
        elif event.type == EventType.MERGE:
            left_id = event.info.get('left_id')
            right_id = event.info.get('right_id')
            separator = event.info.get('separator_key')
            
            highlight['message'] = (
                f"Merge: nós #{left_id} + separador {separator} + #{right_id}"
            )
        
        elif event.type == EventType.SHRINK_ROOT:
            old_root_id = event.info.get('old_root_id')
            new_root_id = event.info.get('new_root_id')
            
            highlight['message'] = (
                f"⬇️ Árvore encolheu: nova raiz #{new_root_id} "
                f"(antiga raiz #{old_root_id} ficou vazia)"
            )
        
        else:
            highlight['message'] = f"Evento: {event.type.value}"
        
        return highlight
    
    def get_progress_text(self) -> str:
        """
        Retorna texto de progresso (ex: "3 / 15").
        
        Returns:
            String com o progresso atual
        """
        if len(self.events) == 0:
            return "0 / 0"
        return f"{self.current_index + 1} / {len(self.events)}"
