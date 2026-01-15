"""
Validador de invariantes de Árvores B e B+.

Verifica se a estrutura da árvore mantém todas as propriedades
esperadas (chaves ordenadas, balanceamento, limites de chaves, etc.).
"""

from typing import Set, Any
from .btree import BTree, BTreeNode


class ValidationError(Exception):
    """Exceção lançada quando uma invariante é violada."""
    pass


def validate_btree(tree: BTree) -> bool:
    """
    Valida todas as invariantes de uma Árvore B.
    
    Args:
        tree: Árvore a ser validada
    
    Returns:
        True se todas as invariantes forem satisfeitas
    
    Raises:
        ValidationError: Se alguma invariante for violada
    """
    if tree.root is None:
        return True
    
    # Conjunto para verificar duplicatas globalmente
    all_keys: Set[Any] = set()
    
    # Verificar altura uniforme (todas as folhas na mesma profundidade)
    leaf_depths = []
    
    def validate_node(node: BTreeNode, depth: int, is_root: bool = False):
        """Valida um nó recursivamente."""
        
        # 1. Verificar número de chaves
        num_keys = len(node.keys)
        if num_keys > tree.max_keys:
            raise ValidationError(
                f"Nó {node.id} tem {num_keys} chaves, máximo é {tree.max_keys}"
            )
        
        # Para não-raiz, verificar mínimo de chaves (aplicável após deleções)
        # Na fase atual (só inserção), não aplicamos esta validação
        
        # 2. Verificar que as chaves estão ordenadas
        for i in range(len(node.keys) - 1):
            if node.keys[i] >= node.keys[i + 1]:
                raise ValidationError(
                    f"Nó {node.id} tem chaves fora de ordem: "
                    f"{node.keys[i]} >= {node.keys[i + 1]}"
                )
        
        # 3. Verificar duplicatas
        for key in node.keys:
            if key in all_keys:
                raise ValidationError(f"Chave duplicada encontrada: {key}")
            all_keys.add(key)
        
        # 4. Se não é folha, verificar número de filhos
        if not node.is_leaf:
            num_children = len(node.children)
            expected_children = num_keys + 1
            
            if num_children != expected_children:
                raise ValidationError(
                    f"Nó {node.id} tem {num_keys} chaves mas {num_children} filhos, "
                    f"esperado {expected_children} filhos"
                )
            
            # 5. Verificar que chaves dos filhos estão nos intervalos corretos
            for i, child in enumerate(node.children):
                validate_node(child, depth + 1, is_root=False)
                
                # Verificar intervalo de chaves do filho
                if i < len(node.keys):
                    # Filho à esquerda da chave node.keys[i]
                    for child_key in child.keys:
                        if i > 0:
                            # Deve ser >= chave anterior
                            if child_key < node.keys[i - 1]:
                                raise ValidationError(
                                    f"Chave {child_key} no filho {child.id} está "
                                    f"abaixo do limite inferior {node.keys[i - 1]}"
                                )
                        # Deve ser < chave atual (para filho à esquerda)
                        if i < len(node.children) - 1 and child_key >= node.keys[i]:
                            raise ValidationError(
                                f"Chave {child_key} no filho {child.id} não está "
                                f"menor que {node.keys[i]}"
                            )
                else:
                    # Último filho (à direita de todas as chaves)
                    for child_key in child.keys:
                        if len(node.keys) > 0 and child_key < node.keys[-1]:
                            raise ValidationError(
                                f"Chave {child_key} no último filho {child.id} está "
                                f"abaixo do limite {node.keys[-1]}"
                            )
        else:
            # É folha - registrar profundidade
            leaf_depths.append(depth)
    
    # Validar a partir da raiz
    validate_node(tree.root, 0, is_root=True)
    
    # Verificar que todas as folhas estão na mesma profundidade
    if leaf_depths and len(set(leaf_depths)) > 1:
        raise ValidationError(
            f"Folhas em profundidades diferentes: {set(leaf_depths)} "
            f"(árvore não está balanceada)"
        )
    
    return True


def validate_bplustree(tree) -> bool:
    """
    Valida todas as invariantes de uma Árvore B+.
    
    Args:
        tree: Árvore B+ a ser validada
    
    Returns:
        True se todas as invariantes forem satisfeitas
    
    Raises:
        ValidationError: Se alguma invariante for violada
    """
    from .bplustree import BPlusTree, BPlusTreeNode
    
    if not isinstance(tree, BPlusTree):
        raise ValueError("Fornecido objeto que não é BPlusTree")
    
    if tree.root is None:
        return True
    
    # Conjunto para verificar duplicatas nas folhas
    all_keys = set()
    leaf_depths = []
    leaf_nodes = []
    
    def validate_node(node: BPlusTreeNode, depth: int, is_root: bool = False):
        """Valida um nó recursivamente."""
        
        # 1. Verificar número de chaves
        num_keys = len(node.keys)
        if num_keys > tree.max_keys:
            raise ValidationError(
                f"Nó {node.id} tem {num_keys} chaves, máximo é {tree.max_keys}"
            )
        
        # 2. Verificar que as chaves estão ordenadas
        for i in range(len(node.keys) - 1):
            if node.keys[i] >= node.keys[i + 1]:
                raise ValidationError(
                    f"Nó {node.id} tem chaves fora de ordem: "
                    f"{node.keys[i]} >= {node.keys[i + 1]}"
                )
        
        if node.is_leaf:
            # 3. Verificar duplicatas apenas nas folhas (onde os dados estão)
            for key in node.keys:
                if key in all_keys:
                    raise ValidationError(f"Chave duplicada encontrada: {key}")
                all_keys.add(key)
            
            # Registrar folha para verificar encadeamento
            leaf_nodes.append(node)
            leaf_depths.append(depth)
        else:
            # 4. Nó interno: verificar número de filhos
            num_children = len(node.children)
            expected_children = num_keys + 1
            
            if num_children != expected_children:
                raise ValidationError(
                    f"Nó interno {node.id} tem {num_keys} chaves mas {num_children} filhos, "
                    f"esperado {expected_children} filhos"
                )
            
            # 5. Validar filhos recursivamente
            for i, child in enumerate(node.children):
                validate_node(child, depth + 1, is_root=False)
    
    # Validar a partir da raiz
    validate_node(tree.root, 0, is_root=True)
    
    # Verificar que todas as folhas estão na mesma profundidade
    if leaf_depths and len(set(leaf_depths)) > 1:
        raise ValidationError(
            f"Folhas em profundidades diferentes: {set(leaf_depths)} "
            f"(árvore não está balanceada)"
        )
    
    # Verificar encadeamento de folhas via first_leaf
    if tree.first_leaf:
        current = tree.first_leaf
        count = 0
        while current:
            count += 1
            if current.is_leaf is False:
                 raise ValidationError(f"Nó na lista encadeada {current.id} não é marcado como folha")
            
            if current.next_leaf:
                # Verificar se o próximo tem chaves maiores ou iguais
                if current.keys and current.next_leaf.keys:
                    if current.keys[-1] > current.next_leaf.keys[0]:
                         raise ValidationError(
                            f"Erro de ordenação na lista encadeada: "
                            f"Folha {current.id} (max {current.keys[-1]}) > "
                            f"Folha {current.next_leaf.id} (min {current.next_leaf.keys[0]})"
                         )
            current = current.next_leaf
            
        if count != len(leaf_nodes):
             raise ValidationError(
                f"Lista encadeada tem {count} nós, mas árvore tem {len(leaf_nodes)} folhas. "
                f"Possível quebra de link."
             )
        
        # Última folha deve ter next_leaf = None
        if leaf_nodes_sorted[-1].next_leaf is not None:
            raise ValidationError(
                f"Última folha {leaf_nodes_sorted[-1].id} deve ter next_leaf=None"
            )
    
    return True

