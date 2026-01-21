"""
Módulo: core.bplustree
Implementação Robusta e Completa de Árvore B+ (B Plus Tree).

Diferenças Fundamentais para B-Tree:
------------------------------------
1.  **Dados nas Folhas:** Todas as chaves reais (dados) residem nas folhas.
    Nós internos contêm apenas chaves separadoras (índices) para guiar a busca.
2.  **Duplicação:** As chaves separadoras nos nós internos podem aparecer novamente
    nas folhas (propriedade de redundância).
3.  **Sequence Set:** As folhas são ligadas entre si (Linked List) através do
    ponteiro `next_leaf`, permitindo varredura sequencial eficiente (Range Query).

Estratégias de Implementação:
-----------------------------
-   **Inserção:** Bottom-Up estrito. Insere na folha. Se estourar, divide e propaga
    o índice para o pai. Se a raiz estourar, a árvore cresce em altura.
-   **Remoção:** Recursiva com tratamento de Underflow. Se uma folha ficar com
    menos de min_keys, tenta pegar emprestado (Borrow) de irmãos adjacentes.
    Se não der, faz fusão (Merge) e propaga a remoção do índice para o pai.
    O tratamento difere se o nó é folha ou interno.

Métricas (I/O Simulation):
--------------------------
-   count_read(): Leitura de nó.
-   count_write(): Gravação de nó.
"""

from typing import List, Optional, Tuple, Any, Union
from .trace import Tracer, EventType
from .metrics import Metrics
import bisect


class BPlusTreeNode:
    """
    Representa uma Página (Nó) da Árvore B+.
    """
    _id_counter = 0
    
    def __init__(self, is_leaf: bool = True):
        self.id = BPlusTreeNode._id_counter
        BPlusTreeNode._id_counter += 1
        
        # Lista de chaves (separadores em internos, dados em folhas)
        self.keys: List[Any] = []
        
        # Lista de filhos (nós internos)
        self.children: List['BPlusTreeNode'] = []
        
        self._is_leaf = is_leaf
        
        # Ponteiro para a próxima folha (apenas se is_leaf=True)
        self.next_leaf: Optional['BPlusTreeNode'] = None
        
        # Ponteiro para o pai (útil para algoritmos complexos de B+)
        self.parent: Optional['BPlusTreeNode'] = None
    
    @property
    def is_leaf(self) -> bool:
        return self._is_leaf
    
    def __repr__(self):
        return f"BPlusNode(id={self.id}, keys={self.keys}, leaf={self.is_leaf})"


class BPlusTree:
    """
    Controlador da Árvore B+.
    """
    
    def __init__(self, fanout_n: int, tracer: Optional[Tracer] = None, 
                 metrics: Optional[Metrics] = None):
        """
        Inicializa a Árvore B+.
        
        Args:
            fanout_n (int): Ordem da árvore (máximo de filhos).
        """
        if not (3 <= fanout_n <= 10):
            raise ValueError(f"Fanout deve estar entre 3 e 10, recebido: {fanout_n}")
        
        self.fanout = fanout_n
        
        # Definições de Capacidade
        # Max chaves = m - 1
        self.max_keys = fanout_n - 1
        # Min chaves = ceil(m/2) - 1
        self.min_keys = (fanout_n + 1) // 2 - 1
        
        self.root = BPlusTreeNode(is_leaf=True)
        self.tracer = tracer or Tracer()
        self.metrics = metrics or Metrics()
        
        # Ponteiro para o início da lista encadeada (Range Queries)
        self.first_leaf = self.root
    
    # =========================================================================
    # SEARCH (Busca)
    # =========================================================================
    
    def search(self, key: Any) -> dict:
        """
        Busca uma chave na árvore. Retorna metadados para a UI.
        """
        path = []
        node = self.root
        
        while node is not None:
            # [I/O] Leitura: Carregando nó
            self.metrics.count_read()
            self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
            path.append(node.id)
            
            if node.is_leaf:
                # Busca sequencial/binária na folha
                for i, k in enumerate(node.keys):
                    self.tracer.emit(EventType.COMPARE_KEY, node.id, {
                        'key_index': i, 'node_key': k, 'target_key': key
                    })
                    if k == key:
                        self.tracer.emit(EventType.SEARCH_FOUND, node.id, {'key': key, 'index': i})
                        return {'found': True, 'node_id': node.id, 'index': i, 'path': path}
                
                # Não encontrou na folha
                self.tracer.emit(EventType.SEARCH_NOT_FOUND, node.id, {'key': key})
                return {'found': False, 'node_id': node.id, 'index': -1, 'path': path}
            
            else:
                # Nó Interno: Navegar pelos separadores
                # Encontrar o primeiro filho cuja chave separadora é > key
                child_idx = 0
                while child_idx < len(node.keys) and key >= node.keys[child_idx]:
                    child_idx += 1
                
                self.tracer.emit(EventType.DESCEND, node.id, {
                    'child_index': child_idx, 'target_key': key
                })
                node = node.children[child_idx]
                
        return {'found': False, 'node_id': -1, 'index': -1, 'path': path}

    # =========================================================================
    # INSERT (Inserção Bottom-Up)
    # =========================================================================

    def insert(self, key: Any) -> bool:
        """
        Insere uma chave na árvore.
        """
        # 1. Verificar duplicata
        search_res = self._search_silent(key)
        if search_res['found']:
            return False
        
        self.tracer.clear()
        
        # 2. Localizar a folha correta
        leaf = self._find_leaf_node(key)
        
        # 3. Inserir na folha
        self._insert_in_leaf(leaf, key)
        
        # 4. Verificar e tratar Overflow (Split) propagando para cima
        if len(leaf.keys) > self.max_keys:
            self._split_leaf(leaf)
            
        return True

    def _find_leaf_node(self, key: Any) -> BPlusTreeNode:
        """Desce a árvore até encontrar a folha que deve conter a chave."""
        node = self.root
        while not node.is_leaf:
            self.metrics.count_read() # [I/O] Leitura na descida
            self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
            
            idx = 0
            while idx < len(node.keys) and key >= node.keys[idx]:
                idx += 1
            
            self.tracer.emit(EventType.DESCEND, node.id, {'child_index': idx, 'target_key': key})
            node = node.children[idx]
            
        # [I/O] Leitura da folha final
        self.metrics.count_read()
        self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
        return node

    def _insert_in_leaf(self, leaf: BPlusTreeNode, key: Any):
        """Insere ordenado na folha."""
        bisect.insort(leaf.keys, key)
        
        # [I/O] Escrita: Folha alterada
        self.metrics.count_write()
        
        self.tracer.emit(EventType.INSERT_IN_LEAF, leaf.id, {
            'key': key, 'keys_after': leaf.keys.copy()
        })

    def _split_leaf(self, leaf: BPlusTreeNode):
        """
        Divide uma folha cheia.
        Estratégia B+: Copia a chave mediana para o pai (Copy Up).
        """
        mid = len(leaf.keys) // 2
        
        # Novo nó folha (irmão à direita)
        new_leaf = BPlusTreeNode(is_leaf=True)
        new_leaf.parent = leaf.parent
        
        # Divisão de chaves
        # Na folha, a chave mediana fica na direita e é COPIADA para cima.
        new_leaf.keys = leaf.keys[mid:]
        leaf.keys = leaf.keys[:mid]
        
        # Manter Sequence Set (Lista Encadeada)
        new_leaf.next_leaf = leaf.next_leaf
        leaf.next_leaf = new_leaf
        
        # Chave a ser promovida (cópia)
        promoted_key = new_leaf.keys[0]
        
        # [I/O] Escritas: Leaf, NewLeaf
        self.metrics.count_write()
        self.metrics.count_write()
        
        self.tracer.emit(EventType.SPLIT_NODE, leaf.id, {
            'promoted_key': promoted_key,
            'left_id': leaf.id, 'right_id': new_leaf.id,
            'left_keys': leaf.keys.copy(), 'right_keys': new_leaf.keys.copy(),
            'is_leaf_split': True
        })
        
        # Inserir no pai
        self._insert_in_parent(leaf, promoted_key, new_leaf)

    def _split_internal(self, node: BPlusTreeNode):
        """
        Divide um nó interno cheio.
        Estratégia B+: Move a chave mediana para o pai (Push Up).
        """
        mid = len(node.keys) // 2
        promoted_key = node.keys[mid] # Esta chave SAI do nível atual
        
        new_node = BPlusTreeNode(is_leaf=False)
        new_node.parent = node.parent
        
        # Divisão de chaves (excluindo a mediana)
        new_node.keys = node.keys[mid + 1:]
        node.keys = node.keys[:mid]
        
        # Divisão de filhos
        new_node.children = node.children[mid + 1:]
        node.children = node.children[:mid + 1]
        
        # Atualizar pai dos filhos movidos
        for child in new_node.children:
            child.parent = new_node
            # [I/O] Escrita: Atualização de ponteiro no filho (metadado)
            self.metrics.count_write()
            
        # [I/O] Escritas: Node, NewNode
        self.metrics.count_write()
        self.metrics.count_write()
        
        self.tracer.emit(EventType.SPLIT_NODE, node.id, {
            'promoted_key': promoted_key,
            'left_id': node.id, 'right_id': new_node.id,
            'left_keys': node.keys.copy(), 'right_keys': new_node.keys.copy(),
            'is_leaf_split': False
        })
        
        # Propagar para cima
        self._insert_in_parent(node, promoted_key, new_node)

    def _insert_in_parent(self, left_child: BPlusTreeNode, key: Any, right_child: BPlusTreeNode):
        """
        Gerencia a inserção da chave promovida no pai.
        """
        parent = left_child.parent
        
        # Caso Base: Se não tem pai, a raiz foi dividida
        if parent is None:
            new_root = BPlusTreeNode(is_leaf=False)
            new_root.keys = [key]
            new_root.children = [left_child, right_child]
            
            left_child.parent = new_root
            right_child.parent = new_root
            
            self.root = new_root
            
            # [I/O] Escrita: Nova Raiz
            self.metrics.count_write()
            self.metrics.count_write() # Atualizar ponteiros dos filhos
            self.metrics.count_write()
            
            self.tracer.emit(EventType.NEW_ROOT, self.root.id, {
                'promoted_key': key,
                'left_child': left_child.id,
                'right_child': right_child.id
            })
            return
        
        # Inserir ordenado no pai
        insert_idx = 0
        while insert_idx < len(parent.keys) and parent.keys[insert_idx] < key:
            insert_idx += 1
            
        parent.keys.insert(insert_idx, key)
        parent.children.insert(insert_idx + 1, right_child)
        right_child.parent = parent
        
        # [I/O] Escrita: Pai atualizado
        self.metrics.count_write()
        
        # Verificar Overflow no pai
        if len(parent.keys) > self.max_keys:
            self._split_internal(parent)

    # =========================================================================
    # DELETE (Remoção com Tratamento de Underflow Completo)
    # =========================================================================

    def delete(self, key: Any) -> bool:
        """
        Remove uma chave da árvore B+.
        """
        # Verificar existência (silencioso para não poluir trace)
        search_res = self._search_silent(key)
        if not search_res['found']:
            self.tracer.emit(EventType.SEARCH_NOT_FOUND, None, {'key': key})
            return False
        
        self.tracer.clear()
        self.tracer.emit(EventType.DELETE_REQUEST, None, {'key': key})
        
        # Localizar folha
        leaf = self._find_leaf_node(key)
        
        # Remover da folha
        self._delete_entry(leaf, key)
        
        return True

    def _delete_entry(self, node: BPlusTreeNode, key: Any, pointer: Optional[BPlusTreeNode] = None):
        """
        Método genérico para remover entrada (Chave + Ponteiro) de um nó.
        """
        # [I/O] Leitura ao acessar nó para deleção
        self.metrics.count_read()
        
        # Remover chave e ponteiro (se for interno)
        if node.is_leaf:
            if key in node.keys:
                node.keys.remove(key)
                self.metrics.count_write() # Escrita: folha
                self.tracer.emit(EventType.DELETE_IN_LEAF, node.id, {'key': key, 'keys_after': node.keys.copy()})
        else:
            # Em nó interno, removemos a chave e o ponteiro associado
            if key in node.keys:
                idx = node.keys.index(key)
                node.keys.pop(idx)
                # Se um ponteiro foi passado para remoção (caso de merge), remove-o
                if pointer:
                    if pointer in node.children:
                        node.children.remove(pointer)
                # [I/O] Escrita: interno
                self.metrics.count_write()

        # Checar se nó é a raiz e tratar encolhimento
        if node == self.root:
            self._adjust_root()
            return

        # Checar Underflow
        if len(node.keys) < self.min_keys:
            self._handle_underflow(node)

    def _adjust_root(self):
        """Se a raiz ficar vazia, reduz altura."""
        if len(self.root.keys) == 0:
            if not self.root.is_leaf:
                # A nova raiz é o único filho restante
                new_root = self.root.children[0]
                new_root.parent = None
                old_root = self.root
                self.root = new_root
                
                # [I/O] Escrita: Nova raiz
                self.metrics.count_write()
                
                self.tracer.emit(EventType.SHRINK_ROOT, self.root.id, {
                    'old_root_id': old_root.id, 'new_root_id': self.root.id
                })
            else:
                # Árvore vazia, nada a fazer
                pass

    def _handle_underflow(self, node: BPlusTreeNode):
        """
        Trata underflow via Borrow (Redistribuição) ou Merge.
        """
        parent = node.parent
        # Encontrar índice do nó no pai
        idx = parent.children.index(node)
        
        self.tracer.emit(EventType.UNDERFLOW, node.id, {'min_keys': self.min_keys})
        
        # Tentar Borrow do Irmão Esquerdo
        if idx > 0:
            left_sibling = parent.children[idx - 1]
            if len(left_sibling.keys) > self.min_keys:
                self._borrow_from_left(node, left_sibling, parent, idx - 1)
                return
        
        # Tentar Borrow do Irmão Direito
        if idx < len(parent.children) - 1:
            right_sibling = parent.children[idx + 1]
            if len(right_sibling.keys) > self.min_keys:
                self._borrow_from_right(node, right_sibling, parent, idx)
                return
        
        # Se não der borrow, MERGE.
        # Preferir merge com a esquerda
        if idx > 0:
            left_sibling = parent.children[idx - 1]
            # Merge node into left_sibling
            self._merge_nodes(left_sibling, node, parent, idx - 1)
        else:
            right_sibling = parent.children[idx + 1]
            # Merge right_sibling into node
            self._merge_nodes(node, right_sibling, parent, idx)

    def _borrow_from_left(self, node: BPlusTreeNode, sibling: BPlusTreeNode, 
                          parent: BPlusTreeNode, separator_idx: int):
        """Empresta do irmão esquerdo."""
        if node.is_leaf:
            # Move última chave do irmão para início do nó
            borrowed_key = sibling.keys.pop()
            node.keys.insert(0, borrowed_key)
            # Atualiza separador no pai (cópia da nova menor chave do nó)
            parent.keys[separator_idx] = node.keys[0]
        else:
            # Interno: Rotação através do pai
            # Chave do pai desce
            node.keys.insert(0, parent.keys[separator_idx])
            # Chave do irmão sobe para o pai
            parent.keys[separator_idx] = sibling.keys.pop()
            # Mover filho
            child_to_move = sibling.children.pop()
            child_to_move.parent = node
            node.children.insert(0, child_to_move)
            self.metrics.count_write() # update child parent ptr
            
        # [I/O] Escritas: Node, Sibling, Parent
        self.metrics.count_write(); self.metrics.count_write(); self.metrics.count_write()
        
        self.tracer.emit(EventType.REDISTRIBUTE, sibling.id, {
            'to_node': node.id, 'parent_id': parent.id
        })

    def _borrow_from_right(self, node: BPlusTreeNode, sibling: BPlusTreeNode, 
                           parent: BPlusTreeNode, separator_idx: int):
        """Empresta do irmão direito."""
        if node.is_leaf:
            # Move primeira chave do irmão para fim do nó
            borrowed_key = sibling.keys.pop(0)
            node.keys.append(borrowed_key)
            # Atualiza separador no pai (nova menor chave do irmão)
            parent.keys[separator_idx] = sibling.keys[0]
        else:
            # Interno
            node.keys.append(parent.keys[separator_idx])
            parent.keys[separator_idx] = sibling.keys.pop(0)
            child_to_move = sibling.children.pop(0)
            child_to_move.parent = node
            node.children.append(child_to_move)
            self.metrics.count_write()
            
        # [I/O] Escritas
        self.metrics.count_write(); self.metrics.count_write(); self.metrics.count_write()
        
        self.tracer.emit(EventType.REDISTRIBUTE, sibling.id, {
            'to_node': node.id, 'parent_id': parent.id
        })

    def _merge_nodes(self, left_node: BPlusTreeNode, right_node: BPlusTreeNode, 
                     parent: BPlusTreeNode, separator_idx: int):
        """
        Funde right_node em left_node.
        Remove right_node da árvore.
        Propaga a remoção do separador para o pai.
        """
        separator_key = parent.keys[separator_idx]
        
        if left_node.is_leaf:
            # Fusão de folhas: concatena chaves
            left_node.keys.extend(right_node.keys)
            left_node.next_leaf = right_node.next_leaf
        else:
            # Fusão interna: Chave do pai desce para o meio
            left_node.keys.append(separator_key)
            left_node.keys.extend(right_node.keys)
            left_node.children.extend(right_node.children)
            # Atualizar pais dos filhos movidos
            for child in right_node.children:
                child.parent = left_node
                self.metrics.count_write()
        
        # [I/O] Escritas: left_node absorveu
        self.metrics.count_write()
        
        self.tracer.emit(EventType.MERGE, left_node.id, {
            'left_id': left_node.id, 'right_id': right_node.id, 
            'separator_key': separator_key
        })
        
        # Remover a chave separadora e o ponteiro para right_node do pai
        # Atenção: Chamada recursiva para tratar underflow no pai
        self._delete_entry(parent, separator_key, pointer=right_node)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _search_silent(self, key: Any) -> dict:
        """Busca sem emitir eventos (usado internamente)."""
        old_trace = self.tracer.enabled
        self.tracer.disable()
        res = self.search(key)
        if old_trace: self.tracer.enable()
        return res

    def to_levels(self) -> List[List[str]]:
        """Retorna estrutura em níveis (BFS)."""
        if self.root is None: return []
        levels = []
        queue = [(self.root, 0)]
        while queue:
            node, lvl = queue.pop(0)
            while len(levels) <= lvl: levels.append([])
            
            s = f"[{','.join(map(str, node.keys))}]"
            if node.is_leaf and node.next_leaf: s += "→"
            levels[lvl].append(s)
            
            for c in node.children: queue.append((c, lvl + 1))
        return levels

    def get_all_nodes(self) -> List[BPlusTreeNode]:
        """Retorna lista plana de nós."""
        if self.root is None: return []
        nodes = []
        queue = [self.root]
        while queue:
            n = queue.pop(0)
            nodes.append(n)
            queue.extend(n.children)
        return nodes

    def sequential_scan(self) -> List[Any]:
        """Varredura via Linked List das folhas."""
        res = []
        curr = self.first_leaf
        while curr:
            self.metrics.count_read()
            res.extend(curr.keys)
            curr = curr.next_leaf
        return res