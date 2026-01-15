from PIL import Image, ImageTk
import os
import tkinter as tk
from typing import Dict, Tuple, List, Optional, Any
from math import pow

def layout_tree(root_node, get_children_func) -> Tuple[Dict[int, Tuple[int, int]], int, int]:
    """
    Calcula posições (x, y) relativas (centro em 0, ou começando de 0).
    Args:
        root_node: Nó raiz
        get_children_func: Função que retorna filhos
    Returns:
        Tuple (Positions Dict, Tree Width, Tree Height)
    """
    if root_node is None:
        return {}, 0, 0
    
    # 1. Coletar nós e níveis
    nodes_by_level = {}
    leaves = []
    queue = [(root_node, 0)]
    all_nodes = []
    max_level = 0
    
    while queue:
        node, level = queue.pop(0)
        all_nodes.append(node)
        if level not in nodes_by_level:
            nodes_by_level[level] = []
        nodes_by_level[level].append(node)
        max_level = max(max_level, level)
        
        children = get_children_func(node)
        if not children:
            leaves.append(node)
        else:
            for child in children:
                queue.append((child, level + 1))
    
    # 2. Configurações
    y_spacing = 100 
    leaf_slot_width = 110 # Compactado para visual moderno
    
    positions = {}
    
    # 3. Posicionar Folhas (Relative X)
    for i, leaf in enumerate(leaves):
        x = i * leaf_slot_width
        y = 50 + max_level * y_spacing
        positions[leaf.id] = (x, y)
    
    # 4. Bottom-Up para pais
    for level in range(max_level - 1, -1, -1):
        for node in nodes_by_level[level]:
            children = get_children_func(node)
            if children:
                first = children[0]
                last = children[-1]
                if first.id in positions and last.id in positions:
                    x = (positions[first.id][0] + positions[last.id][0]) // 2
                    y = 50 + level * y_spacing
                    positions[node.id] = (int(x), int(y))
    
    # Calcular largura total
    tree_width = len(leaves) * leaf_slot_width
    tree_height = 50 + max_level * y_spacing + 100
    
    return positions, tree_width, tree_height


class TreeCanvas:
    """
    Canvas moderno com suporte a nodes arredondados.
    """
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.node_height = 40
        
        # Cores (Modern Dark Palette)
        self.colors = {
            "bg": "#121212",
            "node_fill": "#2c2c2c",
            "node_outline": "#3700b3",
            "node_text": "#ffffff",
            "highlight_fill": "#bb86fc",
            "highlight_outline": "#ffffff",
            "highlight_text": "#000000",
            "edge": "#444444",
            "edge_highlight": "#03dac6",
            "root_fill": "#cf6679", # Variação para raiz
        }
        
        # Estado atual da árvore para re-renderizar no resize
        self.current_tree = None
        self.current_highlight = None
        
        # Bind de resize
        self.canvas.bind("<Configure>", self._on_resize)
        
    def _on_resize(self, event):
        """Re-centraliza a árvore quando a janela muda de tamanho."""
        if self.current_tree:
            self.render(self.current_tree, self.current_highlight)

    def clear(self):
        """Limpa canvas."""
        self.canvas.delete("all")
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Cria um retângulo com bordas arredondadas (helper customizado)."""
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]

        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_node(self, cx: int, cy: int, keys: List[Any], node_id: int,
                  highlight_node: bool = False,
                  highlight_key_index: Optional[int] = None,
                  is_root: bool = False):
        """
        Desenha um nó estilo 'Pill' (Cápsula).
        """
        if not keys: return

        # Configuração de estilo
        fill_color = self.colors["node_fill"]
        outline_color = self.colors["node_outline"]
        text_color = self.colors["node_text"]
        
        if is_root:
             fill_color = "#332940" # Roxo escuro
        
        if highlight_node:
             outline_color = self.colors["highlight_outline"]
             # Se for highlight geral do node
             if highlight_key_index is None:
                 fill_color = self.colors["highlight_fill"]
                 text_color = self.colors["highlight_text"]

        # Dimensões dinâmicas baseadas no conteúdo
        # Largura estimada por chave
        key_width = 35
        padding = 20
        total_width = max(60, len(keys) * key_width + padding)
        total_height = 40
        
        x1 = cx - total_width // 2
        y1 = cy - total_height // 2
        x2 = cx + total_width // 2
        y2 = cy + total_height // 2
        
        # Sombra suave (simples, offset)
        self.create_rounded_rect(x1+3, y1+3, x2+3, y2+3, radius=20, fill="#000000", tags=f"node_{node_id}")

        # Corpo do Nó
        self.create_rounded_rect(x1, y1, x2, y2, radius=20, 
                                 fill=fill_color, outline=outline_color, width=2,
                                 tags=f"node_{node_id}")
        
        # Desenhar chaves
        # Distribuir chaves uniformemente
        section_width = total_width / len(keys)
        
        for i, key in enumerate(keys):
            # Pos x da chave
            kx = x1 + (i * section_width) + (section_width / 2)
            ky = cy
            
            # Highlight específico da chave (Bola ao redor da chave)
            if highlight_node and highlight_key_index == i:
                 self.canvas.create_oval(kx-12, ky-12, kx+12, ky+12, fill=self.colors["highlight_fill"], outline="")
                 k_text_color = self.colors["highlight_text"]
            else:
                 k_text_color = text_color
            
            self.canvas.create_text(
                kx, ky,
                text=str(key),
                font=("Segoe UI", 11, "bold"),
                fill=k_text_color,
                tags=f"node_{node_id}"
            )
            
            # Separadores verticais (sutis) entre chaves
            if i < len(keys) - 1:
                sep_x = x1 + (i + 1) * section_width
                self.canvas.create_line(sep_x, y1+8, sep_x, y2-8, fill="#444444", width=1)

        # ID Badge (Pequeno, acima)
        self.canvas.create_text(
            cx, y1 - 10,
            text=f"#{node_id}",
            font=("Consolas", 8),
            fill="#666666",
            tags=f"node_{node_id}"
        )
    
    def draw_edge(self, x1: int, y1: int, x2: int, y2: int,
                  highlight: bool = False):
        """
        Desenha aresta (linha curva suave).
        """
        if highlight:
            color = self.colors["edge_highlight"]
            width = 3
        else:
            color = self.colors["edge"]
            width = 2
        
        # Ajuste para sair da parte de baixo do nó e entrar no topo
        start_y = y1 + 20 # Metade da altura do nó
        end_y = y2 - 20
        
        # Bezier Curve vertical
        self.canvas.create_line(
            x1, start_y,
            x2, end_y,
            fill=color,
            width=width,
            smooth=True,
            # tags="edge" # Removed tags to prevent deletion issues if simplified
        )
        
        # Opcional: Curva mais bonita (Cubic Bezier)
        # Pontos de controle
        # cp1 = (x1, start_y + 50)
        # cp2 = (x2, end_y - 50)
        # self.canvas.create_line(x1, start_y, x1, start_y+40, x2, end_y-40, x2, end_y, smooth=True, ...)
    
    def render(self, tree, highlight_info: Optional[Dict] = None):
        """
        Renderiza com centralização dinâmica.
        """
        self.current_tree = tree
        self.current_highlight = highlight_info
        
        self.clear()
        
        if tree.root is None:
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            self.canvas.create_text(
                cw//2, ch//2,
                text="Plante uma semente",
                font=("Segoe UI", 16),
                fill="#444444"
            )
            return
        
        # 1. Obter layout base
        positions, tree_w, tree_h = layout_tree(tree.root, lambda node: node.children)
        
        # 2. Calcular Offset para Centralizar
        canvas_w = self.canvas.winfo_width()
        if canvas_w < 50: canvas_w = 1200
        
        if tree_w < canvas_w:
            offset_x = (canvas_w - tree_w) // 2
        else:
            offset_x = 50
            
        offset_x += 55 # Margem extra
        offset_y = 50 
        
        # 3. Aplicar offset e desenhar
        all_nodes = tree.get_all_nodes()

        # [NOVO] Desenhar conexões de folhas (Apenas para B+ Tree)
        # Verifica se é BPlusTree checando se existe atributo first_leaf
        if hasattr(tree, 'first_leaf') and tree.first_leaf:
            current = tree.first_leaf
            while hasattr(current, 'next_leaf') and current.next_leaf:
                next_node = current.next_leaf
                if current.id in positions and next_node.id in positions:
                    x1, y1 = positions[current.id]
                    x2, y2 = positions[next_node.id]
                    
                    # Ajustar coordenadas com offset
                    ax1, ay1 = x1 + offset_x, y1 + offset_y
                    ax2, ay2 = x2 + offset_x, y2 + offset_y
                    
                    # Desenhar seta
                    # Sair da direita do 1º, entrar na esquerda do 2º
                    # assumindo altura via self.node_height (aprox 40)
                    
                    # Ponto de saída (Direita do nó 1)
                    # Largura estimada do nó (recalcular ou estimar fixo/dinamico)
                    # Vamos desenhar uma linha reta ou curva entre os centros por baixo ou pelo meio
                    # Melhor: Seta conectando as laterais
                    
                    # Como layout é por níveis, folhas estão no mesmo Y geralmente.
                    # Mas layout_tree pode retornar Y levemente diferente se árvore desbalanceada (não deveria em B+)
                    
                    self.canvas.create_line(
                        ax1 + 20, ay1 + 25, # Um pouco abaixo do centro
                        ax2 - 20, ay2 + 25,
                        fill="#03dac6", # Teal highlight
                        width=2,
                        arrow=tk.LAST,
                        dash=(4, 2), # Tracejado
                        smooth=True,
                        tags="btree_link"
                    )
                
                current = next_node
        
        # Arestas
        for node in all_nodes:
            if node.id in positions:
                rx, ry = positions[node.id]
                x1, y1 = rx + offset_x, ry + offset_y
                children = node.children
                for child in children:
                    if child.id in positions:
                        cx, cy = positions[child.id]
                        x2, y2 = cx + offset_x, cy + offset_y
                        
                        highlight_edge = False
                        if highlight_info:
                            if (highlight_info.get('descend_from') == node.id and
                                highlight_info.get('descend_to') == child.id):
                                highlight_edge = True
                        self.draw_edge(x1, y1, x2, y2, highlight_edge)

        # Nós
        for node in all_nodes:
            if node.id in positions:
                rx, ry = positions[node.id]
                x, y = rx + offset_x, ry + offset_y
                
                highlight_node = False
                highlight_key_index = None
                if highlight_info and highlight_info.get('node_id') == node.id:
                    highlight_node = True
                    highlight_key_index = highlight_info.get('key_index')
                
                self.draw_node(
                    x, y, node.keys, node.id,
                    highlight_node=highlight_node,
                    highlight_key_index=highlight_key_index,
                    is_root=(tree.root.id == node.id)
                )
        
        final_w = max(canvas_w, tree_w + 100)
        final_h = max(600, tree_h + 100)
        self.canvas.configure(scrollregion=(0, 0, final_w, final_h))

