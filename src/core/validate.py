"""
Validador de invariantes de Árvores B e B+.

Verifica se a estrutura da árvore mantém todas as propriedades
esperadas (chaves ordenadas, balanceamento, limites de chaves, etc.).
"""

from typing import Set, Any
# Importações relativas para evitar ciclos, pois estamos dentro do pacote core
# O app.py importa de core.validate, e core.validate precisa saber o que é BTree
# Mas para checagem de tipo em tempo de execução, podemos usar duck typing ou imports locais

class ValidationError(Exception):
    """Exceção lançada quando uma invariante é violada."""
    pass


def validate_btree(tree) -> bool:
    """
    Valida todas as invariantes de uma Árvore B.
    """
    if tree.root is None:
        return True
    
    # Conjunto para verificar duplicatas globalmente
    all_keys: Set[Any] = set()
    
    # Verificar altura uniforme (todas as folhas na mesma profundidade)
    leaf_depths = []
    
    def validate_node(node, depth: int, is_root: bool = False):
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
            
            # 5. Validar filhos recursivamente
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
                        # Deve ser < chave atual
                        if child_key >= node.keys[i]:
                            raise ValidationError(
                                f"Chave {child_key} no filho {child.id} não é "
                                f"menor que {node.keys[i]}"
                            )
                else:
                    # Último filho (à direita de todas as chaves)
                    for child_key in child.keys:
                        if len(node.keys) > 0 and child_key <= node.keys[-1]:
                            raise ValidationError(
                                f"Chave {child_key} no último filho {child.id} deveria ser "
                                f"maior que {node.keys[-1]}"
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
    """
    if tree.root is None:
        return True
    
    # Conjunto para verificar duplicatas nas folhas (onde os dados reais estão)
    all_keys = set()
    leaf_depths = []
    # Lista para coletar os nós folhas na ordem que aparecem na árvore (DFS)
    leaf_nodes_dfs = [] 
    
    def validate_node(node, depth: int, is_root: bool = False):
        """Valida um nó recursivamente."""
        
        # 1. Verificar número de chaves
        num_keys = len(node.keys)
        if num_keys > tree.max_keys:
            raise ValidationError(
                f"Nó {node.id} tem {num_keys} chaves, máximo é {tree.max_keys}"
            )
        
        # 2. Verificar que as chaves internas estão ordenadas
        for i in range(len(node.keys) - 1):
            if node.keys[i] >= node.keys[i + 1]:
                raise ValidationError(
                    f"Nó {node.id} tem chaves fora de ordem: {node.keys}"
                )
        
        if node.is_leaf:
            # 3. Verificar duplicatas apenas nas folhas
            for key in node.keys:
                if key in all_keys:
                    raise ValidationError(f"Chave duplicada encontrada na folha: {key}")
                all_keys.add(key)
            
            leaf_nodes_dfs.append(node)
            leaf_depths.append(depth)
        else:
            # 4. Nó interno: verificar número de filhos
            num_children = len(node.children)
            expected_children = num_keys + 1
            
            if num_children != expected_children:
                raise ValidationError(
                    f"Nó interno {node.id} tem {num_keys} chaves mas {num_children} filhos."
                )
            
            # 5. Validar filhos recursivamente
            for i, child in enumerate(node.children):
                validate_node(child, depth + 1, is_root=False)
    
    # Executa validação recursiva
    validate_node(tree.root, 0, is_root=True)
    
    # Verificar altura
    if leaf_depths and len(set(leaf_depths)) > 1:
        raise ValidationError(f"Desbalanceamento: Folhas em níveis {set(leaf_depths)}")
    
    # --- VALIDAÇÃO DA LISTA ENCADEADA (Sequence Set) ---
    # Verifica se tree.first_leaf percorre exatamente os mesmos nós 
    # que encontramos via DFS, na mesma ordem.
    
    current = tree.first_leaf
    count_linked = 0
    
    # Se a árvore tem dados mas first_leaf é None
    if len(leaf_nodes_dfs) > 0 and current is None:
        raise ValidationError("Árvore tem folhas, mas first_leaf é None.")

    while current:
        if count_linked >= len(leaf_nodes_dfs):
            raise ValidationError("A lista encadeada tem mais nós do que a árvore estrutural.")
        
        # O nó da lista encadeada deve ser IDÊNTICO ao nó da DFS naquela posição
        expected_node = leaf_nodes_dfs[count_linked]
        
        if current.id != expected_node.id:
            raise ValidationError(
                f"Quebra de Sequência: Esperado nó #{expected_node.id}, encontrado #{current.id} na lista."
            )
            
        # Validar ordenação entre folhas (Sequence Set deve ser estritamente crescente)
        if current.next_leaf:
            if current.keys and current.next_leaf.keys:
                if current.keys[-1] > current.next_leaf.keys[0]:
                     raise ValidationError(
                        f"Erro de ordenação global: O final da folha #{current.id} ({current.keys[-1]}) "
                        f"é maior que o início da próxima folha #{current.next_leaf.id} ({current.next_leaf.keys[0]})"
                     )
        
        current = current.next_leaf
        count_linked += 1
        
    if count_linked != len(leaf_nodes_dfs):
        raise ValidationError(
            f"A lista encadeada termina prematuramente. Visitou {count_linked} nós, mas existem {len(leaf_nodes_dfs)} folhas."
        )
    
    return True