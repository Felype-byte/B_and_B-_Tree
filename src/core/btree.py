"""
Implementação de Árvore B com fanout configurável (3-10).

Suporta operações de busca e inserção com rastreamento completo
de eventos para visualização passo a passo.
"""

from typing import List, Optional, Tuple, Any
from .trace import Tracer, EventType
from .metrics import Metrics


class BTreeNode:
    """
    Nó de uma Árvore B.
    
    Attributes:
        id: Identificador único do nó
        keys: Lista de chaves ordenadas
        children: Lista de referências para filhos (vazia em folhas)
    """
    
    _id_counter = 0
    
    def __init__(self, is_leaf: bool = True):
        self.id = BTreeNode._id_counter
        BTreeNode._id_counter += 1
        self.keys: List[Any] = []
        self.children: List['BTreeNode'] = []
        self._is_leaf = is_leaf
    
    @property
    def is_leaf(self) -> bool:
        """Retorna True se o nó é uma folha."""
        return len(self.children) == 0
    
    def __repr__(self):
        return f"Node(id={self.id}, keys={self.keys}, is_leaf={self.is_leaf})"


class BTree:
    """
    Árvore B com fanout configurável.
    
    Implementa busca e inserção com split automático e rastreamento
    completo de eventos para visualização educacional.
    """
    
    def __init__(self, fanout_n: int, tracer: Optional[Tracer] = None, 
                 metrics: Optional[Metrics] = None):
        """
        Inicializa a Árvore B.
        
        Args:
            fanout_n: Grau da árvore (número máximo de filhos), deve estar entre 3 e 10
            tracer: Rastreador de eventos (opcional)
            metrics: Rastreador de métricas (opcional)
        
        Raises:
            ValueError: Se fanout_n não estiver entre 3 e 10
        """
        if not (3 <= fanout_n <= 10):
            raise ValueError(f"Fanout deve estar entre 3 e 10, recebido: {fanout_n}")
        
        self.fanout_n = fanout_n
        self.max_children = fanout_n
        self.max_keys = fanout_n - 1
        self.min_keys = (fanout_n + 1) // 2 - 1  # Para futuras operações de delete
        
        self.root = BTreeNode(is_leaf=True)
        self.tracer = tracer or Tracer()
        self.metrics = metrics or Metrics()
    
    def search(self, key: Any) -> dict:
        """
        Busca uma chave na árvore.
        
        Args:
            key: Chave a ser buscada
        
        Returns:
            Dicionário com: found (bool), node_id (int), index (int), path (list)
        """
        path = []
        node = self.root
        
        while node is not None:
            # Emitir evento: visitando nó
            self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
            self.metrics.tick_node_access()
            path.append(node.id)
            
            # Buscar a chave no nó
            found_index = None
            for i, node_key in enumerate(node.keys):
                # Emitir evento: comparando com chave
                self.tracer.emit(EventType.COMPARE_KEY, node.id, {
                    'key_index': i,
                    'node_key': node_key,
                    'target_key': key
                })
                
                if key == node_key:
                    found_index = i
                    break
                elif key < node_key:
                    break
            
            # Se encontrou
            if found_index is not None:
                self.tracer.emit(EventType.SEARCH_FOUND, node.id, {
                    'key': key,
                    'index': found_index
                })
                return {
                    'found': True,
                    'node_id': node.id,
                    'index': found_index,
                    'path': path
                }
            
            # Se é folha e não encontrou
            if node.is_leaf:
                self.tracer.emit(EventType.SEARCH_NOT_FOUND, node.id, {'key': key})
                return {
                    'found': False,
                    'node_id': node.id,
                    'index': -1,
                    'path': path
                }
            
            # Encontrar filho para descer
            child_index = 0
            for i, node_key in enumerate(node.keys):
                if key < node_key:
                    child_index = i
                    break
            else:
                child_index = len(node.keys)
            
            # Emitir evento: descendo para filho
            self.tracer.emit(EventType.DESCEND, node.id, {
                'child_index': child_index,
                'target_key': key
            })
            
            node = node.children[child_index]
        
        return {'found': False, 'node_id': -1, 'index': -1, 'path': path}
    
    def insert(self, key: Any) -> bool:
        """
        Insere uma chave na árvore.
        
        Args:
            key: Chave a ser inserida
        
        Returns:
            True se inseriu com sucesso, False se a chave já existe
        """
        # Verificar se já existe (não permitir duplicatas)
        result = self.search(key)
        if result['found']:
            return False
        
        # Limpar eventos da busca anterior (vamos traçar a inserção)
        self.tracer.clear()
        
        # Inserção recursiva (Bottom-Up)
        self._insert_recursive(self.root, key)
        
        # Verificar se a raiz estourou
        if len(self.root.keys) > self.max_keys:
            old_root = self.root
            self.root = BTreeNode(is_leaf=False)
            self.root.children.append(old_root)
            self._split_child(self.root, 0)
            self.tracer.emit(EventType.NEW_ROOT, self.root.id, {
                'old_root_id': old_root.id,
                'promoted_key': self.root.keys[0]
            })
            
        return True
    
    def _insert_recursive(self, node: BTreeNode, key: Any):
        """
        Lógica recursiva de inserção (Bottom-Up).
        
        Args:
            node: Nó atual
            key: Chave a inserir
        """
        # Emitir evento: visitando nó
        self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
        self.metrics.tick_node_access()
        
        if node.is_leaf:
            # Folha: Inserir diretamente
            pos = self._find_insert_pos(node.keys, key)
            node.keys.insert(pos, key)
            self.tracer.emit(EventType.INSERT_IN_LEAF, node.id, {
                'key': key,
                'position': pos,
                'keys_after': node.keys.copy()
            })
        else:
            # Nó Interno: Descer para o filho apropriado
            child_index = self._find_child_index(node.keys, key)
            
            # Emitir evento: descendo
            self.tracer.emit(EventType.DESCEND, node.id, {
                'child_index': child_index,
                'target_key': key
            })
            
            # Recurso no filho
            self._insert_recursive(node.children[child_index], key)
            
            # Check-back (pós-recursão): O filho estourou?
            if len(node.children[child_index].keys) > self.max_keys:
                self._split_child(node, child_index)
    
    def _split_child(self, parent: BTreeNode, child_index: int):
        """
        Faz split de um filho cheio.
        
        Args:
            parent: Nó pai
            child_index: Índice do filho a fazer split
        """
        full_child = parent.children[child_index]
        mid = len(full_child.keys) // 2
        
        # Chave promovida (vai para o pai)
        promoted_key = full_child.keys[mid]
        
        # Criar novo nó à direita
        new_child = BTreeNode(is_leaf=full_child.is_leaf)
        new_child.keys = full_child.keys[mid + 1:]
        full_child.keys = full_child.keys[:mid]
        
        # Se não for folha, dividir os filhos também
        if not full_child.is_leaf:
            new_child.children = full_child.children[mid + 1:]
            full_child.children = full_child.children[:mid + 1]
        
        # Inserir chave promovida no pai
        parent.keys.insert(child_index, promoted_key)
        parent.children.insert(child_index + 1, new_child)
        
        # Emitir evento: split
        self.tracer.emit(EventType.SPLIT_NODE, full_child.id, {
            'promoted_key': promoted_key,
            'left_id': full_child.id,
            'right_id': new_child.id,
            'left_keys': full_child.keys.copy(),
            'right_keys': new_child.keys.copy()
        })
    
    def _find_insert_pos(self, keys: List[Any], key: Any) -> int:
        """
        Encontra a posição de inserção em uma lista de chaves ordenadas.
        
        Args:
            keys: Lista de chaves ordenadas
            key: Chave a inserir
        
        Returns:
            Índice onde a chave deve ser inserida
        """
        for i, k in enumerate(keys):
            if key < k:
                return i
        return len(keys)
    
    def _find_child_index(self, keys: List[Any], key: Any) -> int:
        """
        Encontra o índice do filho para descer durante inserção.
        
        Args:
            keys: Lista de chaves do nó
            key: Chave a inserir
        
        Returns:
            Índice do filho
        """
        for i, k in enumerate(keys):
            if key < k:
                return i
        return len(keys)
    
    def delete(self, key: Any) -> bool:
        """
        Remove uma chave da árvore.
        
        Args:
            key: Chave a ser removida
        
        Returns:
            True se removeu com sucesso, False se a chave não existe
        """
        # Emitir evento de solicitação de remoção
        self.tracer.emit(EventType.DELETE_REQUEST, None, {'key': key})
        
        # Verificar se existe
        result = self.search(key)
        if not result['found']:
            self.tracer.emit(EventType.SEARCH_NOT_FOUND, None, {'key': key})
            return False
            
        # Limpar eventos da busca (manter apenas eventos de delete)
        self.tracer.clear()
        self.tracer.emit(EventType.DELETE_REQUEST, None, {'key': key})
        
        # Executar deleção recursiva (Bottom-Up)
        self._delete_recursive(self.root, key)
        
        # Se a raiz ficou vazia e não é folha (tem filhos), reduzir altura
        # Nota: Se for folha vazia, significa que a árvore ficou vazia (exceto se for recém criada)
        if len(self.root.keys) == 0 and not self.root.is_leaf:
            old_root = self.root
            self.root = old_root.children[0]
            self.tracer.emit(EventType.SHRINK_ROOT, self.root.id, {
                'old_root_id': old_root.id,
                'new_root_id': self.root.id
            })
        
        return True
    
    def _delete_recursive(self, node: BTreeNode, key: Any):
        """
        Lógica recursiva de deleção (Bottom-Up).
        
        Args:
            node: Nó atual
            key: Chave a remover
        """
        # Emitir evento: visitando nó
        self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
        self.metrics.tick_node_access()
        
        # Encontrar índice da chave no nó
        key_idx = -1
        for i, k in enumerate(node.keys):
            self.tracer.emit(EventType.COMPARE_KEY, node.id, {
                'key_index': i,
                'node_key': k,
                'target_key': key
            })
            if k == key:
                key_idx = i
                break
            elif k > key:
                break
        
        if key_idx != -1:
            # CASO 1: Chave encontrada neste nó
            self.tracer.emit(EventType.DELETE_FOUND, node.id, {
                'key': key,
                'key_index': key_idx
            })
            
            if node.is_leaf:
                # 1a: Folha - remover diretamente
                node.keys.pop(key_idx)
                self.tracer.emit(EventType.DELETE_IN_LEAF, node.id, {
                    'key': key,
                    'key_index': key_idx,
                    'keys_after': node.keys.copy()
                })
            else:
                # 1b: Nó Interno - substituir por predecessor
                predecessor = self._get_predecessor(node, key_idx)
                
                self.tracer.emit(EventType.REPLACE_WITH_PREDECESSOR, node.id, {
                    'key': key,
                    'predecessor': predecessor,
                    'key_index': key_idx
                })
                
                # Substituir chave pelo predecessor
                node.keys[key_idx] = predecessor
                
                # Remover predecessor da subárvore esquerda (recursivamente)
                # O predecessor está garantido na subárvore children[key_idx]
                self._delete_recursive(node.children[key_idx], predecessor)
                
                # Verificar underflow no filho após o retorno
                if len(node.children[key_idx].keys) < self.min_keys:
                    self._handle_underflow(node, key_idx)
                    
        else:
            # CASO 2: Chave não está neste nó
            if node.is_leaf:
                # Não deveria acontecer se verificamos search() antes
                return
            
            # Encontrar filho onde a chave deve estar
            child_idx = 0
            for i, k in enumerate(node.keys):
                if key < k:
                    child_idx = i
                    break
            else:
                child_idx = len(node.keys)
            
            # Emitir evento: descendo
            self.tracer.emit(EventType.DESCEND, node.id, {
                'child_index': child_idx,
                'target_key': key
            })
            
            # Recursão
            self._delete_recursive(node.children[child_idx], key)
            
            # Backtracking: Verificar underflow no filho
            if len(node.children[child_idx].keys) < self.min_keys:
                self._handle_underflow(node, child_idx)

    def _get_predecessor(self, node: BTreeNode, key_idx: int) -> Any:
        # Método auxiliar para encontrar predecessor (simplesmente desce tudo a direita)
        current = node.children[key_idx]
        while not current.is_leaf:
            current = current.children[-1]
        return current.keys[-1]

    def _handle_underflow(self, parent: BTreeNode, child_idx: int):
        """
        Corrige underflow de um filho através de redistribuição ou merge.
        
        Args:
            parent: Nó pai
            child_idx: Índice do filho em underflow
        """
        child = parent.children[child_idx]
        
        # Emitir evento de underflow
        self.tracer.emit(EventType.UNDERFLOW, child.id, {
            'num_keys': len(child.keys),
            'min_keys': self.min_keys
        })
        
        # Tentar pegar emprestado do irmão esquerdo
        if child_idx > 0:
            left_sibling = parent.children[child_idx - 1]
            if len(left_sibling.keys) > self.min_keys:
                self._redistribute_from_left(parent, child_idx)
                return
        
        # Tentar pegar emprestado do irmão direito
        if child_idx < len(parent.children) - 1:
            right_sibling = parent.children[child_idx + 1]
            if len(right_sibling.keys) > self.min_keys:
                self._redistribute_from_right(parent, child_idx)
                return
        
        # Não conseguiu redistribuir - fazer merge
        # Preferir merge com irmão esquerdo
        if child_idx > 0:
            self._merge_with_left(parent, child_idx)
        else:
            self._merge_with_right(parent, child_idx)
    
    def _redistribute_from_left(self, parent: BTreeNode, child_idx: int):
        """
        Redistribui chaves do irmão esquerdo.
        
        Args:
            parent: Nó pai
            child_idx: Índice do filho
        """
        child = parent.children[child_idx]
        left_sibling = parent.children[child_idx - 1]
        
        # Puxar chave do pai para o filho
        child.keys.insert(0, parent.keys[child_idx - 1])
        
        # Subir última chave do irmão esquerdo para o pai
        parent.keys[child_idx - 1] = left_sibling.keys.pop()
        
        # Se não for folha, mover último filho também
        if not child.is_leaf:
            child.children.insert(0, left_sibling.children.pop())
        
        self.tracer.emit(EventType.REDISTRIBUTE, left_sibling.id, {
            'from_node': left_sibling.id,
            'to_node': child.id,
            'parent_id': parent.id,
            'parent_key_index': child_idx - 1
        })
    
    def _redistribute_from_right(self, parent: BTreeNode, child_idx: int):
        """
        Redistribui chaves do irmão direito.
        
        Args:
            parent: Nó pai
            child_idx: Índice do filho
        """
        child = parent.children[child_idx]
        right_sibling = parent.children[child_idx + 1]
        
        # Puxar chave do pai para o filho
        child.keys.append(parent.keys[child_idx])
        
        # Subir primeira chave do irmão direito para o pai
        parent.keys[child_idx] = right_sibling.keys.pop(0)
        
        # Se não for folha, mover primeiro filho também
        if not child.is_leaf:
            child.children.append(right_sibling.children.pop(0))
        
        self.tracer.emit(EventType.REDISTRIBUTE, right_sibling.id, {
            'from_node': right_sibling.id,
            'to_node': child.id,
            'parent_id': parent.id,
            'parent_key_index': child_idx
        })
    
    def _merge_with_left(self, parent: BTreeNode, child_idx: int):
        """
        Faz merge do filho com o irmão esquerdo.
        
        Args:
            parent: Nó pai
            child_idx: Índice do filho
        """
        child = parent.children[child_idx]
        left_sibling = parent.children[child_idx - 1]
        
        # Puxar chave separadora do pai
        separator = parent.keys.pop(child_idx - 1)
        
        # Merge: left_sibling + separator + child
        left_sibling.keys.append(separator)
        left_sibling.keys.extend(child.keys)
        
        if not child.is_leaf:
            left_sibling.children.extend(child.children)
        
        # Remover child dos filhos do pai
        parent.children.pop(child_idx)
        
        self.tracer.emit(EventType.MERGE, left_sibling.id, {
            'left_id': left_sibling.id,
            'right_id': child.id,
            'parent_id': parent.id,
            'separator_key': separator,
            'merged_keys': left_sibling.keys.copy()
        })
    
    def _merge_with_right(self, parent: BTreeNode, child_idx: int):
        """
        Faz merge do filho com o irmão direito.
        
        Args:
            parent: Nó pai
            child_idx: Índice do filho
        """
        child = parent.children[child_idx]
        right_sibling = parent.children[child_idx + 1]
        
        # Puxar chave separadora do pai
        separator = parent.keys.pop(child_idx)
        
        # Merge: child + separator + right_sibling
        child.keys.append(separator)
        child.keys.extend(right_sibling.keys)
        
        if not child.is_leaf:
            child.children.extend(right_sibling.children)
        
        # Remover right_sibling dos filhos do pai
        parent.children.pop(child_idx + 1)
        
        self.tracer.emit(EventType.MERGE, child.id, {
            'left_id': child.id,
            'right_id': right_sibling.id,
            'parent_id': parent.id,
            'separator_key': separator,
            'merged_keys': child.keys.copy()
        })
    
    def to_levels(self) -> List[List[str]]:
        """
        Retorna representação da árvore por níveis (BFS).
        
        Returns:
            Lista de níveis, cada nível é uma lista de strings representando nós
        """
        if self.root is None:
            return []
        
        levels = []
        queue = [(self.root, 0)]
        
        while queue:
            node, level = queue.pop(0)
            
            # Expandir lista de níveis se necessário
            while len(levels) <= level:
                levels.append([])
            
            # Adicionar representação do nó
            node_str = f"[{','.join(map(str, node.keys))}]"
            levels[level].append(node_str)
            
            # Adicionar filhos à fila
            for child in node.children:
                queue.append((child, level + 1))
        
        return levels
    
    def get_all_nodes(self) -> List[BTreeNode]:
        """
        Retorna todos os nós da árvore (BFS).
        
        Returns:
            Lista de todos os nós
        """
        if self.root is None:
            return []
        
        nodes = []
        queue = [self.root]
        
        while queue:
            node = queue.pop(0)
            nodes.append(node)
            queue.extend(node.children)
        
        return nodes
