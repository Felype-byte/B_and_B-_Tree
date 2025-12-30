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
    y_spacing = 120  # Mais espaço vertical
    leaf_slot_width = 160 # Mais espaço horizontal entre nós (evita sobreposição)
    
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
    Canvas com suporte a Background Image e Centralização.
    """
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.node_width = 80
        self.node_height = 40
        self.key_spacing = 15
        
        # Assets
        self.bg_image_ref = None
        self._load_assets()
        
        # Estado atual da árvore para re-renderizar no resize
        self.current_tree = None
        self.current_highlight = None
        
        # Bind de resize
        self.canvas.bind("<Configure>", self._on_resize)
        
    def _load_assets(self):
        """Carrega assets gráficos."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Background
            bg_path = os.path.join(base_dir, "bg_forest.png")
            if os.path.exists(bg_path):
                pil_img = Image.open(bg_path)
                pil_img = pil_img.resize((2000, 1500), Image.LANCZOS)
                self.bg_image_ref = ImageTk.PhotoImage(pil_img)
                self.canvas.create_image(0, 0, image=self.bg_image_ref, anchor="nw", tags="bg")
                
        except Exception as e:
            print(f"Erro ao carregar assets: {e}")

    def _on_resize(self, event):
        """Re-centraliza a árvore quando a janela muda de tamanho."""
        if self.current_tree:
            self.render(self.current_tree, self.current_highlight)

    def clear(self):
        """Limpa canvas mantendo o background."""
        items = self.canvas.find_all()
        for item in items:
            tags = self.canvas.gettags(item)
            if "bg" not in tags:
                self.canvas.delete(item)
    
    def draw_node(self, x: int, y: int, keys: List[Any], node_id: int,
                  highlight_node: bool = False,
                  highlight_key_index: Optional[int] = None,
                  is_root: bool = False):
        """
        Desenha um nó como folhas (Vetorial).
        """
        num_keys = len(keys)
        if num_keys == 0: return

        # Configuração de Cores (Raiz vs Normal)
        if is_root:
            leaf_width = 65
            leaf_height = 80
            fill_color = "#fdd835" # Ouro
            outline_color = "#f57f17" # Ouro escuro
            detail_color = "#fff59d" # Ouro claro
            stem_color = "#ffd54f"
        else:
            leaf_width = 55 
            leaf_height = 70
            fill_color = "#689f38" # Verde
            outline_color = "#c5e1a5" # Verde claro
            detail_color = "#8bc34a" # Verde médio
            stem_color = "#a1887f"

        spacing = 10 # Espaçamento aumentado conforme pedido
        total_width = num_keys * leaf_width + (num_keys - 1) * spacing
        start_x = x - total_width // 2
        
        # Haste que segura as folhas
        if num_keys > 1:
            points = [
                start_x + leaf_width//2, y,
                start_x + total_width - leaf_width//2, y
            ]
            self.canvas.create_line(
                points,
                fill=stem_color,
                width=6,
                capstyle=tk.ROUND,
                tags=f"node_{node_id}"
            )

        for i, key in enumerate(keys):
            leaf_cx = start_x + i * (leaf_width + spacing) + leaf_width // 2
            leaf_cy = y + 8
            
            # Ajuste de highlight
            current_fill = fill_color
            current_outline = outline_color
            text_color = "white"
            
            if highlight_node and (highlight_key_index is None or highlight_key_index == i):
                current_fill = "#ffd700" 
                current_outline = "#ffff00" # Muito brilhante
                text_color = "black"

            # Desenhar Folha (Polígono)
            pts = [
                 leaf_cx, leaf_cy + leaf_height//2,     # Ponta inferior
                 leaf_cx - leaf_width//2, leaf_cy + leaf_height//6, 
                 leaf_cx - leaf_width//4, leaf_cy - leaf_height//2, 
                 leaf_cx, leaf_cy - leaf_height//1.5,   # Ponta superior
                 leaf_cx + leaf_width//4, leaf_cy - leaf_height//2, 
                 leaf_cx + leaf_width//2, leaf_cy + leaf_height//6, 
            ]
            
            # Sombra
            self.canvas.create_polygon(
                [(x-1, y+2) for x, y in zip(pts[0::2], pts[1::2])],
                fill="#1b1b1b", outline="", tags=f"node_{node_id}"
            )
            
            # Corpo
            self.canvas.create_polygon(
                pts,
                fill=current_fill,
                outline=current_outline,
                width=2,
                smooth=True,
                tags=f"node_{node_id}"
            )
            
            # Nervura/Detalhe
            self.canvas.create_line(
                leaf_cx, leaf_cy + leaf_height//2 - 5,
                leaf_cx, leaf_cy - leaf_height//2 + 10,
                fill=current_outline, width=1,
                tags=f"node_{node_id}"
            )

            # Texto (Outline preto para legibilidade)
            self.canvas.create_text(
                leaf_cx+1, leaf_cy+1,
                text=str(key), font=("Segoe UI", 11, "bold"), fill="black", tags=f"node_{node_id}"
            )
            self.canvas.create_text(
                leaf_cx, leaf_cy,
                text=str(key),
                font=("Segoe UI", 11, "bold"),
                fill=text_color,
                tags=f"node_{node_id}"
            )

        # ID Debug (Com Badge/Placa)
        # Badge de fundo (Círculo ou plaquinha)
        self.canvas.create_oval(
            x - 12, y - 40, 
            x + 12, y - 16,
            fill="#3e2723", # Madeira escura/Pedra
            outline="#d7ccc8", # Borda clara
            width=2,
            tags=f"node_{node_id}"
        )
        # Texto Principal
        self.canvas.create_text(
            x, y - 28,
            text=f"#{node_id}",
            font=("Consolas", 10, "bold"),
            fill="#ffffff", # Branco brilhante
            tags=f"node_{node_id}"
        )
    
    def draw_edge(self, x1: int, y1: int, x2: int, y2: int,
                  highlight: bool = False):
        """
        Desenha aresta cipó.
        """
        if highlight:
            color = "#ffab40" # Laranja néon
            width = 5
        else:
            color = "#d7ccc8" # Bege claro/Cipó seco (Alto contraste no fundo escuro)
            width = 4
        
        y1_adjusted = y1 + 25
        y2_adjusted = y2 - 25
        
        mid_y = (y1_adjusted + y2_adjusted) // 2
        
        self.canvas.create_line(
            x1, y1_adjusted,
            x1, mid_y,
            x2, mid_y,
            x2, y2_adjusted,
            fill=color,
            width=width,
            smooth=True,
            splinesteps=40,
            capstyle=tk.ROUND,
            tags="edge"
        )
    
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
                text="Árvore Vazia - Plante a primeira semente!",
                font=("Segoe UI", 16, "italic"),
                fill="#d7ccc8"
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
            
        offset_x += 40 # Metade de 80 (novo slot)
        offset_y = 50 
        
        # 3. Aplicar offset e desenhar
        all_nodes = tree.get_all_nodes()
        
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
                    highlight_node, highlight_key_index
                )
        
        final_w = max(canvas_w, tree_w + 100)
        final_h = max(600, tree_h + 100)
        self.canvas.configure(scrollregion=(0, 0, final_w, final_h))
