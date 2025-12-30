"""
Implementação completa de Árvore B+ com fanout configurável (3-10).

Diferenças principais da Árvore B:
- Apenas folhas armazenam chaves de dados
- Nós internos contém apenas separadores (cópias de chaves)
- Folhas são encadeadas via next_leaf
- Todas as operações terminam nas folhas
"""

from typing import List, Optional, Tuple, Any
from .trace import Tracer, EventType
from .metrics import Metrics


class BPlusTreeNode:
    """
    Nó de uma Árvore B+.
    
    Attributes:
        id: Identificador único do nó
        keys: Lista de chaves (dados em folhas, separadores em internos)
        children: Lista de filhos (vazia em folhas)
        is_leaf: Se o nó é folha
        next_leaf: Ponteiro para próxima folha (apenas folhas)
    """
    
    _id_counter = 0
    
    def __init__(self, is_leaf: bool = True):
        self.id = BPlusTreeNode._id_counter
        BPlusTreeNode._id_counter += 1
        self.keys: List[Any] = []
        self.children: List['BPlusTreeNode'] = []
        self._is_leaf = is_leaf
        self.next_leaf: Optional['BPlusTreeNode'] = None  # Apenas para folhas
    
    @property
    def is_leaf(self) -> bool:
        return self._is_leaf
    
    def __repr__(self):
        return f"BPlusNode(id={self.id}, keys={self.keys}, is_leaf={self.is_leaf})"


class BPlusTree:
    """
    Árvore B+ com encadeamento de folhas.
    
    Implementa busca, inserção e remoção com rastreamento completo
    de eventos para visualização passo a passo.
    """
    
    def __init__(self, fanout_n: int, tracer: Optional[Tracer] = None,
                 metrics: Optional[Metrics] = None):
        """
        Inicializa a Árvore B+.
        
        Args:
            fanout_n: Grau da árvore (número máximo de filhos), entre 3 e 10
            tracer: Rastreador de eventos
            metrics: Rastreador de métricas
        
        Raises:
            ValueError: Se fanout_n não estiver entre 3 e 10
        """
        if not (3 <= fanout_n <= 10):
            raise ValueError(f"Fanout deve estar entre 3 e 10, recebido: {fanout_n}")
        
        self.fanout_n = fanout_n
        self.max_children = fanout_n
        self.max_keys = fanout_n - 1
        self.min_keys = (fanout_n + 1) // 2 - 1
        
        self.root = BPlusTreeNode(is_leaf=True)
        self.tracer = tracer or Tracer()
        self.metrics = metrics or Metrics()
        
        # Referência para a primeira folha (para varredura sequencial)
        self.first_leaf = self.root
    
    def search(self, key: Any) -> dict:
        """
        Busca uma chave na árvore B+.
        
        Args:
            key: Chave a ser buscada
        
        Returns:
            Dicionário com: found (bool), node_id (int), index (int), path (list)
        """
        path = []
        node = self.root
        
        # Descer até a folha
        while node is not None:
            # Emitir evento: visitando nó
            self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
            self.metrics.tick_node_access()
            path.append(node.id)
            
            # Se for folha, procurar a chave aqui
            if node.is_leaf:
                for i, node_key in enumerate(node.keys):
                    self.tracer.emit(EventType.COMPARE_KEY, node.id, {
                        'key_index': i,
                        'node_key': node_key,
                        'target_key': key
                    })
                    
                    if key == node_key:
                        self.tracer.emit(EventType.SEARCH_FOUND, node.id, {
                            'key': key,
                            'index': i
                        })
                        return {
                            'found': True,
                            'node_id': node.id,
                            'index': i,
                            'path': path
                        }
                
                # Não encontrado na folha
                self.tracer.emit(EventType.SEARCH_NOT_FOUND, node.id, {'key': key})
                return {
                    'found': False,
                    'node_id': node.id,
                    'index': -1,
                    'path': path
                }
            
            # Nó interno: encontrar filho para descer
            child_index = 0
            for i, node_key in enumerate(node.keys):
                self.tracer.emit(EventType.COMPARE_KEY, node.id, {
                    'key_index': i,
                    'node_key': node_key,
                    'target_key': key
                })
                
                if key < node_key:
                    child_index = i
                    break
            else:
                child_index = len(node.keys)
            
            # Emitir evento: descendo
            self.tracer.emit(EventType.DESCEND, node.id, {
                'child_index': child_index,
                'target_key': key
            })
            
            node = node.children[child_index]
        
        return {'found': False, 'node_id': -1, 'index': -1, 'path': path}
    
    def insert(self, key: Any) -> bool:
        """
        Insere uma chave na árvore B+.
        
        Args:
            key: Chave a ser inserida
        
        Returns:
            True se inseriu com sucesso, False se a chave já existe
        """
        # Verificar se já existe
        result = self.search(key)
        if result['found']:
            return False
        
        # Limpar eventos da busca
        self.tracer.clear()
        
        # Se a raiz está cheia, fazer split primeiro
        if len(self.root.keys) >= self.max_keys:
            old_root = self.root
            self.root = BPlusTreeNode(is_leaf=False)
            self.root.children.append(old_root)
            self._split_child(self.root, 0)
            
            # Atualizar first_leaf se necessário
            if old_root == self.first_leaf:
                # A primeira folha agora é o lado esquerdo do split
                self.first_leaf = self.root.children[0]
                current = self.first_leaf
                while not current.is_leaf:
                    current = current.children[0]
                self.first_leaf = current
        
        # Inserir na árvore
        self._insert_non_full(self.root, key)
        return True
    
    def _insert_non_full(self, node: BPlusTreeNode, key: Any):
        """
        Insere em um nó que tem espaço garantido.
        
        Args:
            node: Nó onde inserir
            key: Chave a inserir
        """
        # Emitir evento: visitando nó
        self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
        self.metrics.tick_node_access()
        
        if node.is_leaf:
            # Inserir na folha
            pos = self._find_insert_pos(node.keys, key)
            node.keys.insert(pos, key)
            self.tracer.emit(EventType.INSERT_IN_LEAF, node.id, {
                'key': key,
                'position': pos,
                'keys_after': node.keys.copy()
            })
        else:
            # Encontrar filho apropriado
            child_index = self._find_child_index(node.keys, key)
            
            # Emitir evento: descendo
            self.tracer.emit(EventType.DESCEND, node.id, {
                'child_index': child_index,
                'target_key': key
            })
            
            # Se o filho está cheio, fazer split primeiro
            if len(node.children[child_index].keys) >= self.max_keys:
                self._split_child(node, child_index)
                # Após o split, pode precisar ir para o próximo filho
                if key > node.keys[child_index]:
                    child_index += 1
            
            # Recursivamente inserir no filho
            self._insert_non_full(node.children[child_index], key)
    
    def _split_child(self, parent: BPlusTreeNode, child_index: int):
        """
        Faz split de um filho cheio (B+ Tree específico).
        
        Args:
            parent: Nó pai
            child_index: Índice do filho a fazer split
        """
        full_child = parent.children[child_index]
        mid = len(full_child.keys) // 2
        
        # Criar novo nó à direita
        new_child = BPlusTreeNode(is_leaf=full_child.is_leaf)
        
        if full_child.is_leaf:
            # Split de folha: chave promovida é COPIADA (não removida)
            promoted_key = full_child.keys[mid]
            
            # Dividir chaves
            new_child.keys = full_child.keys[mid:]
            full_child.keys = full_child.keys[:mid]
            
            # Encadear folhas
            new_child.next_leaf = full_child.next_leaf
            full_child.next_leaf = new_child
        else:
            # Split de nó interno: chave promovida é MOVIDA
            promoted_key = full_child.keys[mid]
            
            # Dividir chaves (não incluir a promovida)
            new_child.keys = full_child.keys[mid + 1:]
            full_child.keys = full_child.keys[:mid]
            
            # Dividir filhos
            new_child.children = full_child.children[mid + 1:]
            full_child.children = full_child.children[:mid + 1]
        
        # Inserir chave promovida no pai
        parent.keys.insert(child_index, promoted_key)
        parent.children.insert(child_index + 1, new_child)
        
        # Emitir evento
        self.tracer.emit(EventType.SPLIT_NODE, full_child.id, {
            'promoted_key': promoted_key,
            'left_id': full_child.id,
            'right_id': new_child.id,
            'left_keys': full_child.keys.copy(),
            'right_keys': new_child.keys.copy(),
            'is_leaf_split': full_child.is_leaf
        })
    
    def delete(self, key: Any) -> bool:
        """
        Remove uma chave da árvore B+.
        
        Args:
            key: Chave a ser removida
        
        Returns:
            True se removeu com sucesso, False se a chave não existe
        """
        # Emitir evento de solicitação
        self.tracer.emit(EventType.DELETE_REQUEST, None, {'key': key})
        
        # Verificar se existe
        result = self._search_with_path(key)
        if not result['found']:
            self.tracer.emit(EventType.SEARCH_NOT_FOUND, None, {'key': key})
            return False
        
        # Limpar eventos da busca
        self.tracer.clear()
        self.tracer.emit(EventType.DELETE_REQUEST, None, {'key': key})
        
        # Executar deleção
        self._delete_internal(self.root, key)
        
        # Se a raiz ficou vazia e tem um filho, reduzir altura
        if len(self.root.keys) == 0 and len(self.root.children) > 0:
            old_root = self.root
            self.root = self.root.children[0]
            self.tracer.emit(EventType.SHRINK_ROOT, self.root.id, {
                'old_root_id': old_root.id,
                'new_root_id': self.root.id
            })
            
            # Atualizar first_leaf
            current = self.root
            while not current.is_leaf:
                current = current.children[0]
            self.first_leaf = current
        
        return True
    
    def _search_with_path(self, key: Any) -> dict:
        """Busca sem emitir eventos de trace."""
        enabled = self.tracer.enabled
        self.tracer.disable()
        result = self.search(key)
        if enabled:
            self.tracer.enable()
        return result
    
    def _delete_internal(self, node: BPlusTreeNode, key: Any):
        """
        Lógica recursiva de deleção (B+ Tree específica).
        
        Args:
            node: Nó atual
            key: Chave a remover
        """
        # Emitir evento: visitando nó
        self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
        self.metrics.tick_node_access()
        
        if node.is_leaf:
            # Encontrar e remover chave da folha
            key_idx = None
            for i, k in enumerate(node.keys):
                self.tracer.emit(EventType.COMPARE_KEY, node.id, {
                    'key_index': i,
                    'node_key': k,
                    'target_key': key
                })
                if k == key:
                    key_idx = i
                    break
            
            if key_idx is not None:
                self.tracer.emit(EventType.DELETE_FOUND, node.id, {
                    'key': key,
                    'key_index': key_idx
                })
                node.keys.pop(key_idx)
                self.tracer.emit(EventType.DELETE_IN_LEAF, node.id, {
                    'key': key,
                    'key_index': key_idx,
                    'keys_after': node.keys.copy()
                })
        else:
            # Nó interno: encontrar filho onde a chave deve estar
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
            
            child = node.children[child_idx]
            
            # Se o filho vai ficar em underflow, corrigir primeiro
            if len(child.keys) <= self.min_keys:
                self._fix_child_underflow(node, child_idx)
                # Reencontrar índice
                child_idx = 0
                for i, k in enumerate(node.keys):
                    if key < k:
                        child_idx = i
                        break
                else:
                    child_idx = len(node.keys)
            
            # Recursivamente deletar do filho
            self._delete_internal(node.children[child_idx], key)
    
    def _fix_child_underflow(self, parent: BPlusTreeNode, child_idx: int):
        """
        Corrige underflow de um filho.
        
        Args:
            parent: Nó pai
            child_idx: Índice do filho em underflow
        """
        child = parent.children[child_idx]
        
        self.tracer.emit(EventType.UNDERFLOW, child.id, {
            'num_keys': len(child.keys),
            'min_keys': self.min_keys
        })
        
        # Tentar redistribuir do irmão esquerdo
        if child_idx > 0:
            left_sibling = parent.children[child_idx - 1]
            if len(left_sibling.keys) > self.min_keys:
                self._redistribute_from_left(parent, child_idx)
                return
        
        # Tentar redistribuir do irmão direito
        if child_idx < len(parent.children) - 1:
            right_sibling = parent.children[child_idx + 1]
            if len(right_sibling.keys) > self.min_keys:
                self._redistribute_from_right(parent, child_idx)
                return
        
        # Merge
        if child_idx > 0:
            self._merge_with_left(parent, child_idx)
        else:
            self._merge_with_right(parent, child_idx)
    
    def _redistribute_from_left(self, parent: BPlusTreeNode, child_idx: int):
        """Redistribui do irmão esquerdo (B+ específico)."""
        child = parent.children[child_idx]
        left_sibling = parent.children[child_idx - 1]
        
        if child.is_leaf:
            # Folha: mover última chave do irmão esquerdo
            child.keys.insert(0, left_sibling.keys.pop())
            # Atualizar separador no pai
            parent.keys[child_idx - 1] = child.keys[0]
        else:
            # Interno: rotação com pai
            child.keys.insert(0, parent.keys[child_idx - 1])
            parent.keys[child_idx - 1] = left_sibling.keys.pop()
            child.children.insert(0, left_sibling.children.pop())
        
        self.tracer.emit(EventType.REDISTRIBUTE, left_sibling.id, {
            'from_node': left_sibling.id,
            'to_node': child.id,
            'parent_id': parent.id,
            'parent_key_index': child_idx - 1
        })
    
    def _redistribute_from_right(self, parent: BPlusTreeNode, child_idx: int):
        """Redistribui do irmão direito (B+ específico)."""
        child = parent.children[child_idx]
        right_sibling = parent.children[child_idx + 1]
        
        if child.is_leaf:
            # Folha: mover primeira chave do irmão direito
            child.keys.append(right_sibling.keys.pop(0))
            # Atualizar separador no pai
            parent.keys[child_idx] = right_sibling.keys[0]
        else:
            # Interno: rotação com pai
            child.keys.append(parent.keys[child_idx])
            parent.keys[child_idx] = right_sibling.keys.pop(0)
            child.children.append(right_sibling.children.pop(0))
        
        self.tracer.emit(EventType.REDISTRIBUTE, right_sibling.id, {
            'from_node': right_sibling.id,
            'to_node': child.id,
            'parent_id': parent.id,
            'parent_key_index': child_idx
        })
    
    def _merge_with_left(self, parent: BPlusTreeNode, child_idx: int):
        """Merge com irmão esquerdo (B+ específico)."""
        child = parent.children[child_idx]
        left_sibling = parent.children[child_idx - 1]
        separator = parent.keys.pop(child_idx - 1)
        
        if child.is_leaf:
            # Folhas: simplesmente concatenar
            left_sibling.keys.extend(child.keys)
            left_sibling.next_leaf = child.next_leaf
        else:
            # Internos: incluir separador
            left_sibling.keys.append(separator)
            left_sibling.keys.extend(child.keys)
            left_sibling.children.extend(child.children)
        
        parent.children.pop(child_idx)
        
        self.tracer.emit(EventType.MERGE, left_sibling.id, {
            'left_id': left_sibling.id,
            'right_id': child.id,
            'parent_id': parent.id,
            'separator_key': separator,
            'merged_keys': left_sibling.keys.copy()
        })
    
    def _merge_with_right(self, parent: BPlusTreeNode, child_idx: int):
        """Merge com irmão direito (B+ específico)."""
        child = parent.children[child_idx]
        right_sibling = parent.children[child_idx + 1]
        separator = parent.keys.pop(child_idx)
        
        if child.is_leaf:
            # Folhas: simplesmente concatenar
            child.keys.extend(right_sibling.keys)
            child.next_leaf = right_sibling.next_leaf
        else:
            # Internos: incluir separador
            child.keys.append(separator)
            child.keys.extend(right_sibling.keys)
            child.children.extend(right_sibling.children)
        
        parent.children.pop(child_idx + 1)
        
        self.tracer.emit(EventType.MERGE, child.id, {
            'left_id': child.id,
            'right_id': right_sibling.id,
            'parent_id': parent.id,
            'separator_key': separator,
            'merged_keys': child.keys.copy()
        })
    
    def _find_insert_pos(self, keys: List[Any], key: Any) -> int:
        """Encontra posição de inserção."""
        for i, k in enumerate(keys):
            if key < k:
                return i
        return len(keys)
    
    def _find_child_index(self, keys: List[Any], key: Any) -> int:
        """Encontra índice do filho."""
        for i, k in enumerate(keys):
            if key < k:
                return i
        return len(keys)
    
    def range_query(self, start_key: Any, end_key: Any) -> List[Any]:
        """
        Busca por intervalo usando encadeamento de folhas.
        
        Args:
            start_key: Chave inicial (inclusiva)
            end_key: Chave final (inclusiva)
        
        Returns:
            Lista de chaves no intervalo
        """
        result = []
        
        # Encontrar primeira folha que pode conter start_key
        node = self.root
        while not node.is_leaf:
            child_idx = 0
            for i, k in enumerate(node.keys):
                if start_key < k:
                    child_idx = i
                    break
            else:
                child_idx = len(node.keys)
            node = node.children[child_idx]
        
        # Percorrer folhas usando next_leaf
        while node is not None:
            for key in node.keys:
                if start_key <= key <= end_key:
                    result.append(key)
                elif key > end_key:
                    return result
            node = node.next_leaf
        
        return result
    
    def sequential_scan(self) -> List[Any]:
        """
        Varredura sequencial de todas as chaves.
        
        Returns:
            Lista de todas as chaves em ordem
        """
        result = []
        node = self.first_leaf
        
        while node is not None:
            result.extend(node.keys)
            node = node.next_leaf
        
        return result
    
    def to_levels(self) -> List[List[str]]:
        """Representação da árvore por níveis (BFS)."""
        if self.root is None:
            return []
        
        levels = []
        queue = [(self.root, 0)]
        
        while queue:
            node, level = queue.pop(0)
            
            while len(levels) <= level:
                levels.append([])
            
            # Adicionar representação do nó
            node_str = f"[{','.join(map(str, node.keys))}]"
            if node.is_leaf and node.next_leaf:
                node_str += "→"  # Indicar encadeamento
            levels[level].append(node_str)
            
            # Adicionar filhos à fila
            for child in node.children:
                queue.append((child, level + 1))
        
        return levels
    
    def get_all_nodes(self) -> List[BPlusTreeNode]:
        """Retorna todos os nós da árvore (BFS)."""
        if self.root is None:
            return []
        
        nodes = []
        queue = [self.root]
        
        while queue:
            node = queue.pop(0)
            nodes.append(node)
            queue.extend(node.children)
        
        return nodes
