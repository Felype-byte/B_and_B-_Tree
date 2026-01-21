"""
Módulo: core.btree
Implementação Robusta de Árvore B (Standard B-Tree).

Características Principais:

1.  **Armazenamento Misto:** Diferente da B+, na B-Tree as chaves e dados residem em qualquer nó 
    (interno ou folha). Não há duplicação de chaves.

2.  **Inserção (Estratégia Bottom-Up):**
    A inserção desce recursivamente até encontrar a folha correta. A chave é inserida.
    Se o nó transbordar (overflow), ele é dividido na volta da recursão (pós-ordem),
    promovendo a chave mediana para o pai. Se a raiz transbordar, a árvore cresce em altura.
    *Vantagem:* Garante balanceamento perfeito visual e estrutural.

3.  **Remoção (Estratégia Top-Down Proativa):**
    Ao descer na árvore para deletar uma chave, garantimos que o nó destino tenha
    chaves suficientes (pelo menos t). Se tiver apenas o mínimo (t-1), realizamos
    um empréstimo (rotação) ou fusão (merge) antes de descer.
    *Vantagem:* Evita o complexo processo de "backtracking" (voltar e corrigir) se
    um nó ficar vazio lá em baixo.

4.  **Instrumentação (Metrics & Trace):**
    - count_read(): Simula o custo de I/O ao acessar um nó.
    - count_write(): Simula o custo de I/O ao gravar um nó modificado.
"""

from typing import List, Optional, Tuple, Any
from .trace import Tracer, EventType
from .metrics import Metrics


class BTreeNode:
    """
    Representa uma Página (Bloco de Disco) da Árvore B.
    
    Attributes:
        id (int): Identificador único para fins de visualização.
        keys (List[Any]): Lista ordenada de chaves.
        children (List[BTreeNode]): Lista de ponteiros para filhos.
        _is_leaf (bool): Flag para otimizar verificações.
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
        """Retorna True se o nó é folha (sem filhos)."""
        return self._is_leaf
    
    def __repr__(self):
        return f"BNode(id={self.id}, keys={self.keys}, leaf={self.is_leaf})"


class BTree:
    """
    Controlador da Árvore B.
    Gerencia a raiz e coordena operações de I/O lógicas.
    """
    
    def __init__(self, fanout_n: int, tracer: Optional[Tracer] = None, 
                 metrics: Optional[Metrics] = None):
        """
        Inicializa a Árvore B.
        
        Args:
            fanout_n: Ordem da árvore (número máximo de filhos).
            tracer: Ferramenta de rastreamento visual.
            metrics: Ferramenta de estatísticas de desempenho.
        """
        if not (3 <= fanout_n <= 10):
            raise ValueError(f"Fanout deve estar entre 3 e 10, recebido: {fanout_n}")
        
        self.fanout = fanout_n
        
        # Propriedades CLRS
        # Max Filhos = m
        # Max Chaves = m - 1
        # Min Chaves = ceil(m/2) - 1
        self.max_children = fanout_n
        self.max_keys = fanout_n - 1
        self.min_keys = (fanout_n + 1) // 2 - 1
        
        self.root = BTreeNode(is_leaf=True)
        self.tracer = tracer or Tracer()
        self.metrics = metrics or Metrics()
    

    #Busca
  
    
    def search(self, key: Any) -> dict:
        """
        Busca uma chave na árvore.
        
        Returns:
            dict: {found, node_id, index, path}
        """
        return self._search_recursive(self.root, key, path=[])

    def _search_recursive(self, node: BTreeNode, key: Any, path: List[int]) -> dict:
        """
        Executa a busca recursiva.
        Complexidade: O(log N) acessos a disco.
        """
        # [I/O] Leitura: Carregando nó na memória
        self.metrics.count_read()
        self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
        
        path.append(node.id)
        
        # Busca sequencial dentro da página (memória RAM)
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            # Evento visual apenas
            self.tracer.emit(EventType.COMPARE_KEY, node.id, {
                'key_index': i, 'node_key': node.keys[i], 'target_key': key
            })
            i += 1
        
        # Verifica se encontrou
        if i < len(node.keys):
            self.tracer.emit(EventType.COMPARE_KEY, node.id, {
                'key_index': i, 'node_key': node.keys[i], 'target_key': key
            })
            if key == node.keys[i]:
                self.tracer.emit(EventType.SEARCH_FOUND, node.id, {'key': key, 'index': i})
                return {'found': True, 'node_id': node.id, 'index': i, 'path': path}
        
        # Se é folha e não achou
        if node.is_leaf:
            self.tracer.emit(EventType.SEARCH_NOT_FOUND, node.id, {'key': key})
            return {'found': False, 'node_id': node.id, 'index': -1, 'path': path}
        
        # Descer para o filho
        self.tracer.emit(EventType.DESCEND, node.id, {'child_index': i, 'target_key': key})
        return self._search_recursive(node.children[i], key, path)


    #Inserção Bottom-Up


    def insert(self, key: Any) -> bool:
        """
        Insere uma chave na árvore.
        Usa estratégia Bottom-Up para garantir crescimento pela raiz.
        """
        # 1. Verificar duplicata (B-Tree padrão não aceita duplicatas)
        prev_enabled = self.tracer.enabled
        self.tracer.disable()
        exists = self.search(key)['found']
        if prev_enabled: self.tracer.enable()
        
        if exists: return False
        
        self.tracer.clear()
        
        # 2. Inserção Recursiva (desce até folha, trata split na volta)
        self._insert_recursive(self.root, key)
        
        # 3. Tratamento de Overflow na Raiz
        # Se após a recursão a raiz estourou, a árvore cresce em altura.
        if len(self.root.keys) > self.max_keys:
            old_root = self.root
            new_root = BTreeNode(is_leaf=False)
            new_root.children.append(old_root)
            self.root = new_root
            
            # [I/O] Escrita: Nova raiz criada
            self.metrics.count_write()
            
            # Divide a antiga raiz e promove a mediana para a nova raiz
            self._split_child(new_root, 0)
            
            self.tracer.emit(EventType.NEW_ROOT, self.root.id, {
                'old_root_id': old_root.id, 
                'promoted_key': self.root.keys[0]
            })
            
        return True

    def _insert_recursive(self, node: BTreeNode, key: Any):
        """
        Desce a árvore até a folha apropriada e insere a chave.
        Verifica overflow APÓS inserir (na volta da recursão).
        """
        # [I/O] Leitura: Visitando nó para decidir caminho
        self.metrics.count_read()
        self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
        
        if node.is_leaf:
            # Caso Base: Inserção ordenada na folha
            pos = 0
            while pos < len(node.keys) and key > node.keys[pos]:
                pos += 1
            node.keys.insert(pos, key)
            
            # [I/O] Escrita: Gravação da folha modificada
            self.metrics.count_write()
            
            self.tracer.emit(EventType.INSERT_IN_LEAF, node.id, {
                'key': key, 
                'position': pos, 
                'keys_after': node.keys.copy()
            })
        else:
            # Caso Recursivo: Encontrar filho correto
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            
            self.tracer.emit(EventType.DESCEND, node.id, {
                'child_index': i, 'target_key': key
            })
            
            # Chamada Recursiva
            self._insert_recursive(node.children[i], key)
            
            # Verificar se o filho onde inserimos acabou estourando
            if len(node.children[i].keys) > self.max_keys:
                self._split_child(node, i)

    def _split_child(self, parent: BTreeNode, i: int):
        """
        Divide um nó filho cheio em dois e sobe a mediana para o pai.
        
        Args:
            parent: Nó pai que receberá a chave promovida.
            i: Índice do filho cheio na lista de filhos do pai.
        """
        full_child = parent.children[i]
        
        # Encontrar mediana
        mid = len(full_child.keys) // 2
        mid_key = full_child.keys[mid]
        
        # Criar novo nó irmão (recebe a metade direita)
        new_node = BTreeNode(is_leaf=full_child.is_leaf)
        new_node.keys = full_child.keys[mid+1:]
        
        # Se não for folha, move filhos correspondentes também
        if not full_child.is_leaf:
            new_node.children = full_child.children[mid+1:]
            full_child.children = full_child.children[:mid+1] # Mantém filhos da esq
            
        # Nó original fica com metade esquerda (remove mediana e direita)
        full_child.keys = full_child.keys[:mid]
        
        # Conectar no pai
        parent.children.insert(i + 1, new_node)
        parent.keys.insert(i, mid_key)
        
        # [I/O] 3 Escritas:
        # 1. Nó original (cortado)
        # 2. Novo nó (criado)
        # 3. Pai (atualizado com chave e ponteiro)
        self.metrics.count_write()
        self.metrics.count_write()
        self.metrics.count_write()
        
        self.tracer.emit(EventType.SPLIT_NODE, full_child.id, {
            'promoted_key': mid_key,
            'left_id': full_child.id,
            'right_id': new_node.id,
            'left_keys': full_child.keys.copy(),
            'right_keys': new_node.keys.copy()
        })


    #Remoção Top-Down


    def delete(self, key: Any) -> bool:
        """
        Remove uma chave da árvore.
        
        Estratégia: Top-Down Proativa.
        Garante que, antes de descer para um nó, ele tenha pelo menos 't' chaves.
        Isso assegura que a remoção em uma folha nunca causará underflow que
        precise propagar para cima.
        """
        # Verificar existência
        prev_enabled = self.tracer.enabled
        self.tracer.disable()
        exists = self.search(key)['found']
        if prev_enabled: self.tracer.enable()
        
        if not exists:
            self.tracer.emit(EventType.SEARCH_NOT_FOUND, None, {'key': key})
            return False
        
        self.tracer.clear()
        self.tracer.emit(EventType.DELETE_REQUEST, None, {'key': key})
        
        # Iniciar recursão
        self._delete_recursive(self.root, key)
        
        # Pós-remoção: Se raiz ficar vazia
        if len(self.root.keys) == 0:
            if not self.root.is_leaf:
                # Raiz vazia com filhos -> Árvore encolhe
                old_root = self.root
                self.root = self.root.children[0]
                
                # [I/O] Escrita: Nova raiz
                self.metrics.count_write()
                
                self.tracer.emit(EventType.SHRINK_ROOT, self.root.id, {
                    'old_root_id': old_root.id, 
                    'new_root_id': self.root.id
                })
            else:
                # Árvore vazia
                pass
                
        return True

    def _delete_recursive(self, node: BTreeNode, key: Any):
        """
        Algoritmo central de remoção (CLRS).
        """
        # [I/O] Leitura
        self.metrics.count_read()
        self.tracer.emit(EventType.VISIT_NODE, node.id, {'keys': node.keys.copy()})
        
        # Encontrar chave
        idx = 0
        while idx < len(node.keys) and key > node.keys[idx]:
            idx += 1
        
        # No chave
        if idx < len(node.keys) and key == node.keys[idx]:
            self.tracer.emit(EventType.DELETE_FOUND, node.id, {'key': key, 'key_index': idx})
            
            if node.is_leaf:
                # CASO 1: Remover de folha
                node.keys.pop(idx)
                
                # [I/O] Escrita
                self.metrics.count_write()
                self.tracer.emit(EventType.DELETE_IN_LEAF, node.id, {
                    'key': key, 'keys_after': node.keys.copy()
                })
            else:
                # CASO 2: Remover de nó interno (Substituição)
                self._delete_internal_node_key(node, key, idx)
        
        # --- A CHAVE NÃO ESTÁ NESTE NÓ (DESCER) ---
        else:
            if node.is_leaf:
                return # Should not happen
            
            # Filho para onde vamos descer
            child = node.children[idx]
            
            # GARANTIA PROATIVA:
            # Se o filho tem apenas o mínimo de chaves, encha-o antes de descer.
            if len(child.keys) <= self.min_keys:
                self._fill_child(node, idx)
                
                # O índice pode ter mudado após merge/rotação
                if idx > len(node.keys): 
                    idx = len(node.keys)
                elif idx < len(node.keys) and key > node.keys[idx]:
                    idx += 1
            
            self.tracer.emit(EventType.DESCEND, node.id, {'child_index': idx, 'target_key': key})
            self._delete_recursive(node.children[idx], key)

    def _delete_internal_node_key(self, node: BTreeNode, key: Any, idx: int):
        """
        Trata remoção em nó interno substituindo por Predecessor ou Sucessor.
        """
        left_child = node.children[idx]
        right_child = node.children[idx + 1]
        
        # 2a. Usar Predecessor (se filho esq tem chaves extras)
        if len(left_child.keys) > self.min_keys:
            predecessor = self._get_predecessor(left_child)
            
            self.tracer.emit(EventType.REPLACE_WITH_PREDECESSOR, node.id, {
                'key': key, 'predecessor': predecessor, 'key_index': idx
            })
            
            node.keys[idx] = predecessor
            # [I/O] Escrita
            self.metrics.count_write()
            
            self._delete_recursive(left_child, predecessor)
            
        # 2b. Usar Sucessor (se filho dir tem chaves extras)
        elif len(right_child.keys) > self.min_keys:
            successor = self._get_successor(right_child)
            
            self.tracer.emit(EventType.REPLACE_WITH_PREDECESSOR, node.id, {
                'key': key, 'predecessor': successor, 'key_index': idx, 'msg': "Substituindo por Sucessor"
            })
            
            node.keys[idx] = successor
            # [I/O] Escrita
            self.metrics.count_write()
            
            self._delete_recursive(right_child, successor)
            
        # 2c. Ambos no mínimo -> Merge
        else:
            self._merge_children(node, idx)
            # A chave desceu. Deletar do novo nó fundido.
            self._delete_recursive(node.children[idx], key)

    def _get_predecessor(self, node: BTreeNode) -> Any:
        """Retorna maior chave da subárvore (descida à direita)."""
        curr = node
        while not curr.is_leaf:
            # [I/O] Opcional: contar navegação auxiliar
            self.metrics.count_read()
            curr = curr.children[-1]
        return curr.keys[-1]

    def _get_successor(self, node: BTreeNode) -> Any:
        """Retorna menor chave da subárvore (descida à esquerda)."""
        curr = node
        while not curr.is_leaf:
            self.metrics.count_read()
            curr = curr.children[0]
        return curr.keys[0]

    def _fill_child(self, parent: BTreeNode, idx: int):
        """
        Preenche um filho com poucas chaves usando Borrow ou Merge.
        """
        # Tentar Borrow do irmão esquerdo
        if idx > 0 and len(parent.children[idx - 1].keys) > self.min_keys:
            self._borrow_from_prev(parent, idx)
        
        # Tentar Borrow do irmão direito
        elif idx < len(parent.children) - 1 and len(parent.children[idx + 1].keys) > self.min_keys:
            self._borrow_from_next(parent, idx)
            
        # Fazer Merge
        else:
            if idx < len(parent.children) - 1:
                self._merge_children(parent, idx)
            else:
                self._merge_children(parent, idx - 1)

    def _borrow_from_prev(self, parent: BTreeNode, idx: int):
        """Rotação à Direita."""
        child = parent.children[idx]
        sibling = parent.children[idx - 1]
        
        # Chave do pai desce
        child.keys.insert(0, parent.keys[idx - 1])
        if not child.is_leaf: 
            child.children.insert(0, sibling.children.pop())
        
        # Chave do irmão sobe
        parent.keys[idx - 1] = sibling.keys.pop()
        
        # [I/O] 3 Escritas
        self.metrics.count_write(); self.metrics.count_write(); self.metrics.count_write()
        
        self.tracer.emit(EventType.REDISTRIBUTE, sibling.id, {
            'from_node': sibling.id, 'to_node': child.id, 'parent_id': parent.id
        })

    def _borrow_from_next(self, parent: BTreeNode, idx: int):
        """Rotação à Esquerda."""
        child = parent.children[idx]
        sibling = parent.children[idx + 1]
        
        # Chave do pai desce
        child.keys.append(parent.keys[idx])
        if not child.is_leaf: 
            child.children.append(sibling.children.pop(0))
        
        # Chave do irmão sobe
        parent.keys[idx] = sibling.keys.pop(0)
        
        # [I/O] 3 Escritas
        self.metrics.count_write(); self.metrics.count_write(); self.metrics.count_write()
        
        self.tracer.emit(EventType.REDISTRIBUTE, sibling.id, {
            'from_node': sibling.id, 'to_node': child.id, 'parent_id': parent.id
        })

    def _merge_children(self, parent: BTreeNode, idx: int):
        """
        Funde children[idx] e children[idx+1] usando a chave separadora do pai.
        """
        left = parent.children[idx]
        right = parent.children[idx + 1]
        separator = parent.keys.pop(idx)
        
        # Unir no nó da esquerda
        left.keys.append(separator)
        left.keys.extend(right.keys)
        
        if not left.is_leaf:
            left.children.extend(right.children)
            
        # Remover nó da direita
        parent.children.pop(idx + 1)
        
        # [I/O] 2 Escritas: Pai e Nó Fundido
        self.metrics.count_write()
        self.metrics.count_write()
        
        self.tracer.emit(EventType.MERGE, left.id, {
            'left_id': left.id, 'right_id': right.id, 
            'separator_key': separator, 'parent_id': parent.id
        })


    def to_levels(self) -> List[List[str]]:
        """Retorna estrutura em níveis para visualização."""
        if self.root is None: return []
        levels = []
        queue = [(self.root, 0)]
        while queue:
            node, lvl = queue.pop(0)
            while len(levels) <= lvl: levels.append([])
            levels[lvl].append(f"[{','.join(map(str, node.keys))}]")
            if not node.is_leaf:
                for c in node.children: queue.append((c, lvl + 1))
        return levels

    def get_all_nodes(self) -> List[BTreeNode]:
        """Retorna todos os nós (lista plana)."""
        if self.root is None: return []
        nodes = []
        queue = [self.root]
        while queue:
            n = queue.pop(0)
            nodes.append(n)
            if not n.is_leaf: queue.extend(n.children)
        return nodes
    
    def get_height(self) -> int:
        """Calcula altura da árvore."""
        h = 0
        node = self.root
        while node:
            h += 1
            if node.is_leaf: break
            node = node.children[0]
        return h

    def range_query(self, start_key: Any, end_key: Any) -> List[Any]:
        """Busca por intervalo (In-Order Traversal)."""
        result = []
        self._in_order_range(self.root, start_key, end_key, result)
        return result

    def _in_order_range(self, node: BTreeNode, start: Any, end: Any, acc: List[Any]):
        if not node: return
        self.metrics.count_read()
        i = 0
        while i < len(node.keys):
            if not node.is_leaf and node.keys[i] >= start:
                self._in_order_range(node.children[i], start, end, acc)
            
            if start <= node.keys[i] <= end:
                acc.append(node.keys[i])
            
            if node.keys[i] > end: return 
            i += 1
            
        if not node.is_leaf:
            self._in_order_range(node.children[i], start, end, acc)