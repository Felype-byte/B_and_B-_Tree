"""
Interface gráfica principal - Widgets e janela.

Fornece todos os controles de UI para interação com as árvores.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Tuple, List, Any
import os

# Funcao de layout
def layout_tree(root_node, get_children_func) -> Tuple[Dict[int, Tuple[int, int]], int, int]:
    """
    Calcula posições (x, y) com espaçamento dinâmico baseado no conteúdo.
    """
    if root_node is None:
        return {}, 0, 0
    
    def get_node_width(node):
        chars_count = sum(len(str(k)) for k in node.keys)
        # Largura estimada: Padding (30) + Texto (10/char) + Separadores (15/item)
        estimated_width = 30 + (chars_count * 10) + (len(node.keys) * 15)
        return max(60, estimated_width)

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
    node_gap = 30 
    
    positions = {}
    
    # 3. Posicionar Folhas
    current_x = 50 
    
    for leaf in leaves:
        width = get_node_width(leaf)
        x = current_x + (width / 2)
        y = 50 + max_level * y_spacing
        positions[leaf.id] = (x, y)
        current_x += width + node_gap
    
    tree_width = current_x
    
    # 4. Bottom-Up para pais
    for level in range(max_level - 1, -1, -1):
        for node in nodes_by_level[level]:
            children = get_children_func(node)
            if children:
                first_child = children[0]
                last_child = children[-1]
                
                if first_child.id in positions and last_child.id in positions:
                    x_start = positions[first_child.id][0]
                    x_end = positions[last_child.id][0]
                    x = (x_start + x_end) / 2
                    y = 50 + level * y_spacing
                    positions[node.id] = (int(x), int(y))
            else:
                positions[node.id] = (current_x, 50 + level * y_spacing)
                current_x += 80

    tree_height = 50 + max_level * y_spacing + 100
    return positions, tree_width, tree_height


class TreeCanvas:
    """Canvas para desenho da árvore com correção de curvas."""
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.node_height = 40
        
        self.colors = {
            "bg": "#f4f6f8", "node_fill": "#ffffff", "node_outline": "#90a4ae", 
            "node_text": "#37474f", "highlight_fill": "#ffe082", "highlight_outline": "#ffb300", 
            "highlight_text": "#3e2723", "edge": "#b0bec5", "edge_highlight": "#009688", 
            "root_fill": "#e1bee7",    
        }
        
        self.current_tree = None
        self.current_highlight = None
        self.current_scale = 1.0
        
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-4>", self.zoom)
        self.canvas.bind("<Button-5>", self.zoom)
        
    def _on_resize(self, event):
        if self.current_tree:
            self.render(self.current_tree, self.current_highlight)

    def zoom(self, event):
        scale_factor = 1.0
        if event.delta > 0 or event.num == 4: scale_factor = 1.1
        elif event.delta < 0 or event.num == 5: scale_factor = 0.9
        
        new_total_scale = self.current_scale * scale_factor
        if new_total_scale < 0.2 or new_total_scale > 4.0: return

        self.current_scale = new_total_scale
        self.canvas.scale("all", event.x, event.y, scale_factor, scale_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def clear(self):
        self.canvas.delete("all")
        self.canvas.configure(bg=self.colors["bg"])
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_node(self, cx: int, cy: int, keys: List[Any], node_id: int, highlight_node: bool = False, highlight_key_index: Optional[int] = None, is_root: bool = False):
        if not keys: return

        fill_color = self.colors["node_fill"]
        outline_color = self.colors["node_outline"]
        text_color = self.colors["node_text"]
        
        if is_root: fill_color = self.colors["root_fill"]
        
        if highlight_node:
             outline_color = self.colors["highlight_outline"]
             if highlight_key_index is None:
                 fill_color = self.colors["highlight_fill"]
                 text_color = self.colors["highlight_text"]

        chars_count = sum(len(str(k)) for k in keys)
        total_width = max(60, 30 + (chars_count * 10) + (len(keys) * 15))
        total_height = 40
        
        x1, y1 = cx - total_width // 2, cy - total_height // 2
        x2, y2 = cx + total_width // 2, cy + total_height // 2
        
        self.create_rounded_rect(x1+3, y1+3, x2+3, y2+3, radius=20, fill="#cfd8dc", tags=f"node_{node_id}")
        self.create_rounded_rect(x1, y1, x2, y2, radius=20, fill=fill_color, outline=outline_color, width=2, tags=f"node_{node_id}")
        
        section_width = total_width / len(keys)
        
        for i, key in enumerate(keys):
            kx = x1 + (i * section_width) + (section_width / 2)
            ky = cy
            
            if highlight_node and highlight_key_index == i:
                 self.canvas.create_oval(kx-12, ky-12, kx+12, ky+12, fill=self.colors["highlight_fill"], outline="")
                 k_text_color = self.colors["highlight_text"]
            else:
                 k_text_color = text_color
            
            txt_val = str(key)
            if len(txt_val) > 5: txt_val = txt_val[:4] + "…"

            self.canvas.create_text(kx, ky, text=txt_val, font=("Segoe UI", 10, "bold"), fill=k_text_color, tags=f"node_{node_id}")
            
            if i < len(keys) - 1:
                sep_x = x1 + (i + 1) * section_width
                self.canvas.create_line(sep_x, y1+8, sep_x, y2-8, fill="#cfd8dc", width=1)

        self.canvas.create_text(cx, y1 - 10, text=f"#{node_id}", font=("Consolas", 8), fill="#90a4ae", tags=f"node_{node_id}")
    
    def draw_edge(self, x1: int, y1: int, x2: int, y2: int, highlight: bool = False):
        """
        Desenha aresta com correção de ancoragem para evitar 'quebras'.
        """
        color = self.colors["edge_highlight"] if highlight else self.colors["edge"]
        width = 3 if highlight else 2
        
        start_y = y1 + 20
        end_y = y2 - 20
        offset_y = (end_y - start_y) * 0.5
        
        cp1 = (x1, start_y + offset_y)
        cp2 = (x2, end_y - offset_y)
        
        # Repetimos (x1, start_y) e (x2, end_y) duas vezes na lista de pontos.
        # Isso força a Spline do Tkinter a passar EXATAMENTE por esses pontos (ancoragem)
        self.canvas.create_line(
            x1, start_y, x1, start_y,  #  Âncora Inicial
            cp1[0], cp1[1], 
            cp2[0], cp2[1], 
            x2, end_y, x2, end_y,      #  Âncora Final
            fill=color,
            width=width,
            smooth=True,
            capstyle=tk.ROUND
        )
    
    def render(self, tree, highlight_info: Optional[Dict] = None):
        self.current_tree = tree
        self.current_highlight = highlight_info
        self.clear()
        
        if tree.root is None:
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            self.canvas.create_text(cw//2, ch//2, text="Plante uma semente", font=("Segoe UI", 16), fill="#90a4ae")
            return
        
        positions, tree_w, tree_h = layout_tree(tree.root, lambda node: node.children)
        
        canvas_w = self.canvas.winfo_width()
        if canvas_w < 50: canvas_w = 1200
        
        offset_x = (canvas_w - tree_w) // 2 if tree_w < canvas_w else 50
        offset_x += 50
        offset_y = 50 
        
        all_nodes = tree.get_all_nodes()

        # Conexões B+ (Folhas)
        if hasattr(tree, 'first_leaf') and tree.first_leaf:
            current = tree.first_leaf
            while hasattr(current, 'next_leaf') and current.next_leaf:
                next_node = current.next_leaf
                if current.id in positions and next_node.id in positions:
                    x1, y1 = positions[current.id]
                    x2, y2 = positions[next_node.id]
                    ax1, ay1 = x1 + offset_x, y1 + offset_y
                    ax2, ay2 = x2 + offset_x, y2 + offset_y
                    
                    self.canvas.create_line(
                        ax1 + 20, ay1 + 25, ax2 - 20, ay2 + 25,
                        fill="#00796b", width=2, arrow=tk.LAST, dash=(4, 2), smooth=True, tags="btree_link"
                    )
                current = next_node
        
        # Arestas
        for node in all_nodes:
            if node.id in positions:
                rx, ry = positions[node.id]
                x1, y1 = rx + offset_x, ry + offset_y
                for child in node.children:
                    if child.id in positions:
                        cx, cy = positions[child.id]
                        x2, y2 = cx + offset_x, cy + offset_y
                        
                        highlight_edge = False
                        if highlight_info:
                            if (highlight_info.get('descend_from') == node.id and highlight_info.get('descend_to') == child.id):
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
                
                self.draw_node(x, y, node.keys, node.id, highlight_node=highlight_node, highlight_key_index=highlight_key_index, is_root=(tree.root.id == node.id))
        
        if self.current_scale != 1.0:
            self.canvas.scale("all", 0, 0, self.current_scale, self.current_scale)

        final_w = max(canvas_w, tree_w * self.current_scale + 200)
        final_h = max(600, tree_h * self.current_scale + 200)
        self.canvas.configure(scrollregion=(0, 0, final_w, final_h))


class MainWindow:
    """Janela principal da aplicação."""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Visualizador de Árvores B e B+")
        self.root.geometry("1200x800")
        
        self.colors = {
            "bg_main": "#eceff1", "bg_panel": "#ffffff", "fg_text": "#37474f",
            "accent": "#5c6bc0", "accent_hover": "#3949ab", "border": "#cfd8dc",
            "input_bg": "#fafafa", "scroll_bg": "#cfd8dc", "scroll_fg": "#78909c",
            "canvas_bg": "#f4f6f8"
        }
        
        self._setup_theme()
        
        self.on_insert: Optional[Callable] = None
        self.on_search: Optional[Callable] = None
        self.on_remove: Optional[Callable] = None
        self.on_random_insert: Optional[Callable] = None
        self.on_random_remove: Optional[Callable] = None
        self.on_fanout_change: Optional[Callable] = None
        self.on_tree_type_change: Optional[Callable] = None
        self.on_data_type_change: Optional[Callable] = None
        self.on_step_next: Optional[Callable] = None
        self.on_step_prev: Optional[Callable] = None
        self.on_reset: Optional[Callable] = None
        self.on_play: Optional[Callable] = None
        
        self.root.configure(bg=self.colors["bg_main"])
        self._create_widgets()

    def _setup_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        c = self.colors
        style.configure(".", background=c["bg_main"], foreground=c["fg_text"], font=("Segoe UI", 10))
        style.configure("TFrame", background=c["bg_main"])
        style.configure("Panel.TFrame", background=c["bg_panel"])
        style.configure("TLabelframe", background=c["bg_panel"], foreground=c["fg_text"], bordercolor=c["border"])
        style.configure("TLabelframe.Label", background=c["bg_panel"], foreground=c["accent"], font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=c["bg_panel"], foreground=c["fg_text"])
        style.configure("Title.TLabel", background=c["bg_panel"], foreground=c["accent"], font=("Segoe UI", 18, "bold"))
        style.configure("TButton", background=c["accent"], foreground="white", borderwidth=0, focuscolor="none", padding=8, font=("Segoe UI", 9, "bold"))
        style.map("TButton", background=[('active', c["accent_hover"]), ('pressed', c["fg_text"])], foreground=[('disabled', '#b0bec5')])
        style.configure("TRadiobutton", background=c["bg_panel"], foreground=c["fg_text"])
        style.map("TRadiobutton", background=[('active', c["bg_panel"])], foreground=[('active', c["accent"])])
        style.configure("TEntry", fieldbackground=c["input_bg"], foreground=c["fg_text"], insertcolor=c["fg_text"], bordercolor=c["border"], lightcolor=c["border"], darkcolor=c["border"])
        style.configure("Horizontal.TScale", background=c["bg_panel"], troughcolor=c["border"], sliderthickness=15)
        style.configure("Vertical.TScrollbar", background=c["scroll_fg"], troughcolor=c["bg_main"], arrowcolor="white", bordercolor=c["bg_main"])
        style.configure("Horizontal.TScrollbar", background=c["scroll_fg"], troughcolor=c["bg_main"], arrowcolor="white", bordercolor=c["bg_main"])

    def _create_widgets(self):
        try: self.root.state('zoomed')
        except: pass 
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_container = ttk.Frame(main_frame, width=320)
        left_container.pack(side=tk.LEFT, fill=tk.Y)
        left_container.pack_propagate(False)
        
        self.ctrl_canvas = tk.Canvas(left_container, bg=self.colors["bg_main"], highlightthickness=0, width=320)
        ctrl_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.ctrl_canvas.yview)
        ctrl_inner = ttk.Frame(self.ctrl_canvas, style="Panel.TFrame")
        
        ctrl_inner.bind("<Configure>", lambda e: self.ctrl_canvas.configure(scrollregion=self.ctrl_canvas.bbox("all")))
        self.ctrl_canvas.create_window((0, 0), window=ctrl_inner, anchor="nw", width=320) 
        self.ctrl_canvas.configure(yscrollcommand=ctrl_scrollbar.set)
        ctrl_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ctrl_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        pad_frame = ttk.Frame(ctrl_inner, style="Panel.TFrame")
        pad_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = ttk.Label(pad_frame, text="B-Tree Viz", style="Title.TLabel")
        title_label.pack(pady=(0, 20), anchor="w")
        
        fanout_frame = ttk.LabelFrame(pad_frame, text=" Grau (Ordem) ", padding=15)
        fanout_frame.pack(fill=tk.X, pady=(0, 10))
        self.fanout_var = tk.IntVar(value=3)
        fanout_header = ttk.Frame(fanout_frame, style="Panel.TFrame")
        fanout_header.pack(fill=tk.X)
        fanout_label = ttk.Label(fanout_header, text="n = 3", font=("Segoe UI", 12))
        fanout_label.pack(side=tk.LEFT)
        self.fanout_scale = ttk.Scale(fanout_frame, from_=3, to=10, orient=tk.HORIZONTAL, variable=self.fanout_var, command=lambda v: self._update_fanout_label(fanout_label, v))
        self.fanout_scale.pack(fill=tk.X, pady=(10, 10))
        ttk.Button(fanout_frame, text="Aplicar Mudança", command=self._on_fanout_changed).pack(fill=tk.X)

        tree_type_frame = ttk.LabelFrame(pad_frame, text=" Estrutura ", padding=15)
        tree_type_frame.pack(fill=tk.X, pady=(0, 10))
        self.tree_type_var = tk.StringVar(value="btree")
        ttk.Radiobutton(tree_type_frame, text="Árvore B", variable=self.tree_type_var, value="btree", command=self._on_tree_type_changed).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(tree_type_frame, text="Árvore B+", variable=self.tree_type_var, value="bplustree", command=self._on_tree_type_changed).pack(anchor=tk.W, pady=2)

        dtype_frame = ttk.LabelFrame(pad_frame, text=" Tipo de Dado ", padding=15)
        dtype_frame.pack(fill=tk.X, pady=10)
        self.data_type_var = tk.StringVar(value="numeric")
        self.last_data_type = "numeric"
        ttk.Radiobutton(dtype_frame, text="Numérico", variable=self.data_type_var, value="numeric", command=self._toggle_data_mode).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(dtype_frame, text="Texto (String)", variable=self.data_type_var, value="string", command=self._toggle_data_mode).pack(side=tk.LEFT)

        self.numeric_container = ttk.Frame(pad_frame, style="Panel.TFrame")
        num_ops_frame = ttk.LabelFrame(self.numeric_container, text=" Operações (Num) ", padding=15)
        num_ops_frame.pack(fill=tk.X, pady=10)
        ttk.Label(num_ops_frame, text="Valor Inteiro:").pack(anchor=tk.W)
        self.num_entry = ttk.Entry(num_ops_frame, font=("Segoe UI", 11))
        self.num_entry.pack(fill=tk.X, pady=(5, 15))
        self._create_ops_buttons(num_ops_frame)
        num_random_frame = ttk.LabelFrame(self.numeric_container, text=" Aleatório (Num) ", padding=15)
        num_random_frame.pack(fill=tk.X, pady=10)
        nr_inputs = ttk.Frame(num_random_frame, style="Panel.TFrame")
        nr_inputs.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(nr_inputs, text="Qtd:").pack(side=tk.LEFT)
        self.random_count_entry = ttk.Entry(nr_inputs, width=5)
        self.random_count_entry.insert(0, "10")
        self.random_count_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(nr_inputs, text="Max:").pack(side=tk.LEFT, padx=(5,0))
        self.random_max_entry = ttk.Entry(nr_inputs, width=6)
        self.random_max_entry.insert(0, "100") 
        self.random_max_entry.pack(side=tk.LEFT, padx=5)
        self.random_min_entry = ttk.Entry(nr_inputs, width=0)
        self.random_min_entry.insert(0, "1")
        ttk.Button(num_random_frame, text="Gerar Números", command=self._on_random_insert_clicked).pack(fill=tk.X)

        self.string_container = ttk.Frame(pad_frame, style="Panel.TFrame")
        str_ops_frame = ttk.LabelFrame(self.string_container, text=" Operações (Texto) ", padding=15)
        str_ops_frame.pack(fill=tk.X, pady=10)
        ttk.Label(str_ops_frame, text="Texto:").pack(anchor=tk.W)
        self.str_entry = ttk.Entry(str_ops_frame, font=("Segoe UI", 11))
        self.str_entry.pack(fill=tk.X, pady=(5, 15))
        self._create_ops_buttons(str_ops_frame)
        str_random_frame = ttk.LabelFrame(self.string_container, text=" Aleatório (Texto) ", padding=15)
        str_random_frame.pack(fill=tk.X, pady=10)
        sr_inputs = ttk.Frame(str_random_frame, style="Panel.TFrame")
        sr_inputs.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(sr_inputs, text="Qtd:").pack(side=tk.LEFT)
        self.str_random_count_entry = ttk.Entry(sr_inputs, width=5)
        self.str_random_count_entry.insert(0, "10")
        self.str_random_count_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(sr_inputs, text="Tam:").pack(side=tk.LEFT, padx=(5,0))
        self.str_random_len_entry = ttk.Entry(sr_inputs, width=5)
        self.str_random_len_entry.insert(0, "3")
        self.str_random_len_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(str_random_frame, text="Gerar Strings", command=self._on_random_insert_clicked).pack(fill=tk.X)

        self.numeric_container.pack(fill=tk.BOTH, expand=True)
        
        canvas_container = ttk.Frame(main_frame)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_container, bg=self.colors["canvas_bg"], highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.configure(scrollregion=(0, 0, 2000, 2000))
    
    def _create_ops_buttons(self, parent):
        btn_grid = ttk.Frame(parent, style="Panel.TFrame")
        btn_grid.pack(fill=tk.X)
        ttk.Button(btn_grid, text="Inserir", command=self._on_insert_clicked).pack(fill=tk.X, pady=2)
        ttk.Button(btn_grid, text="Buscar", command=self._on_search_clicked).pack(fill=tk.X, pady=2)
        ttk.Button(btn_grid, text="Remover", command=self._on_remove_clicked).pack(fill=tk.X, pady=2)

    def _toggle_data_mode(self):
        new_mode = self.data_type_var.get()
        if new_mode == self.last_data_type: return
        if self.on_data_type_change:
            if not self.on_data_type_change(new_mode):
                self.data_type_var.set(self.last_data_type)
                return
        self.last_data_type = new_mode
        if new_mode == "numeric":
            self.string_container.pack_forget()
            self.numeric_container.pack(fill=tk.BOTH, expand=True)
        else:
            self.numeric_container.pack_forget()
            self.string_container.pack(fill=tk.BOTH, expand=True)

    def _update_fanout_label(self, label: ttk.Label, value):
        n = int(float(value))
        label.config(text=f"n = {n}")
    
    def _on_tree_type_changed(self):
        if self.on_tree_type_change: self.on_tree_type_change(self.tree_type_var.get())
    def _on_fanout_changed(self):
        if self.on_fanout_change: self.on_fanout_change(self.fanout_var.get())
    def _on_insert_clicked(self):
        key = self._parse_key()
        if key is not None and self.on_insert: self.on_insert(key)
    def _on_search_clicked(self):
        key = self._parse_key()
        if key is not None and self.on_search: self.on_search(key)
    def _on_remove_clicked(self):
        key = self._parse_key()
        if key is not None and self.on_remove: self.on_remove(key)
    
    def _on_random_insert_clicked(self):
        try:
            mode = self.data_type_var.get()
            if mode == "numeric":
                count = int(self.random_count_entry.get())
                min_val = int(self.random_min_entry.get())
                max_val = int(self.random_max_entry.get())
                if count <= 0 or min_val >= max_val: raise ValueError("Valores inválidos")
                if self.on_random_insert: self.on_random_insert(count, min_val, max_val)
            else:
                count = int(self.str_random_count_entry.get())
                length = int(self.str_random_len_entry.get())
                if count <= 0 or length <= 0: raise ValueError("Valores inválidos")
                if self.on_random_insert: self.on_random_insert(count, length, 0)
        except ValueError as e: messagebox.showerror("Erro", str(e))
    
    def _on_random_remove_clicked(self):
        if self.on_random_remove: self.on_random_remove(1) 
    def _on_next_clicked(self):
        if self.on_step_next: self.on_step_next()
    def _on_prev_clicked(self):
        if self.on_step_prev: self.on_step_prev()
    def _on_reset_clicked(self):
        if self.on_reset: self.on_reset()
    def _on_play_clicked(self):
        if self.on_play: self.on_play()
    
    def _parse_key(self) -> Optional[any]:
        mode = self.data_type_var.get()
        if mode == "numeric":
            key_str = self.num_entry.get().strip()
            if not key_str:
                messagebox.showwarning("Aviso", "Digite um número")
                return None
            try: return int(key_str)
            except ValueError: messagebox.showerror("Erro", "Chave deve ser número"); return None
        else:
            key_str = self.str_entry.get().strip()
            if not key_str:
                messagebox.showwarning("Aviso", "Digite um texto")
                return None
            return key_str 
    
    def update_metrics(self, node_accesses: int, batch_time_ms: Optional[float]): pass
    def update_progress(self, progress_text: str): pass
    def update_event_message(self, message: str): pass
    def enable_playback_controls(self, has_prev: bool, has_next: bool): pass
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        if msg_type == "info": messagebox.showinfo(title, message)
        elif msg_type == "warning": messagebox.showwarning(title, message)
        elif msg_type == "error": messagebox.showerror(title, message)