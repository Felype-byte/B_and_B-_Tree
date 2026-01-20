"""
Interface gráfica principal - Widgets e janela.

Fornece todos os controles de UI para interação com as árvores.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import os
# from PIL import Image, ImageTk # Removed dependency on images for widgets

class MainWindow:
    """
    Janela principal da aplicação.
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Visualizador de Árvores B e B+")
        self.root.geometry("1200x800")
        
        # --- PALETA DE CORES GLOBAL (PADRÃO BLUE-GREY/INDIGO) ---
        self.colors = {
            "bg_main":       "#eceff1",  # Fundo geral (Blue Grey 50)
            "bg_panel":      "#ffffff",  # Fundo dos painéis (White)
            "fg_text":       "#37474f",  # Texto principal (Blue Grey 800)
            "accent":        "#5c6bc0",  # Cor de destaque/Botões (Indigo 400)
            "accent_hover":  "#3949ab",  # Hover dos botões (Indigo 600)
            "border":        "#cfd8dc",  # Bordas sutis (Blue Grey 100)
            "input_bg":      "#fafafa",  # Fundo dos inputs
            "scroll_bg":     "#cfd8dc",  # Fundo do scroll
            "scroll_fg":     "#78909c",  # Barra do scroll
            "canvas_bg":     "#f4f6f8"   # Fundo do Canvas de desenho
        }
        
        # Configurar Tema
        self._setup_theme()
        
        # Callbacks (serão definidos pelo app.py)
        self.on_insert: Optional[Callable] = None
        self.on_search: Optional[Callable] = None
        self.on_remove: Optional[Callable] = None
        self.on_random_insert: Optional[Callable] = None
        self.on_random_remove: Optional[Callable] = None
        self.on_fanout_change: Optional[Callable] = None
        self.on_tree_type_change: Optional[Callable] = None
        self.on_step_next: Optional[Callable] = None
        self.on_step_prev: Optional[Callable] = None
        self.on_reset: Optional[Callable] = None
        self.on_play: Optional[Callable] = None
        
        # Aplica a cor de fundo principal na janela raiz
        self.root.configure(bg=self.colors["bg_main"])
        self._create_widgets()

    def _setup_theme(self):
        """Configura o tema visual (Cohesive Modern Light)."""
        style = ttk.Style()
        style.theme_use('clam')
        
        c = self.colors # Alias para facilitar
        
        # Configuração Geral
        style.configure(".", background=c["bg_main"], foreground=c["fg_text"], font=("Segoe UI", 10))
        
        # Frames (Containers)
        style.configure("TFrame", background=c["bg_main"])
        style.configure("Panel.TFrame", background=c["bg_panel"])
        
        # Labelframes (Caixas de grupo)
        style.configure("TLabelframe", 
            background=c["bg_panel"], 
            foreground=c["fg_text"], 
            bordercolor=c["border"]
        )
        style.configure("TLabelframe.Label", 
            background=c["bg_panel"], 
            foreground=c["accent"], 
            font=("Segoe UI", 10, "bold")
        )
        
        # Labels (Textos)
        style.configure("TLabel", background=c["bg_panel"], foreground=c["fg_text"])
        # Título com fundo transparente (herda do pai) ou ajustado
        style.configure("Title.TLabel", 
            background=c["bg_panel"], 
            foreground=c["accent"], 
            font=("Segoe UI", 18, "bold")
        )
        
        # Botões (Flat Modern Indigo)
        style.configure("TButton", 
            background=c["accent"], 
            foreground="white", 
            borderwidth=0, 
            focuscolor="none",
            padding=8,
            font=("Segoe UI", 9, "bold")
        )
        style.map("TButton",
            background=[('active', c["accent_hover"]), ('pressed', c["fg_text"])],
            foreground=[('disabled', '#b0bec5')]
        )
        
        # Radiobuttons
        style.configure("TRadiobutton", background=c["bg_panel"], foreground=c["fg_text"])
        style.map("TRadiobutton", 
            background=[('active', c["bg_panel"])],
            foreground=[('active', c["accent"])]
        )
        
        # Entry (Caixas de texto - Otimizadas)
        style.configure("TEntry", 
            fieldbackground=c["input_bg"], 
            foreground=c["fg_text"], 
            insertcolor=c["fg_text"], 
            bordercolor=c["border"],
            lightcolor=c["border"],
            darkcolor=c["border"]
        )
        
        # Scale (Slider)
        style.configure("Horizontal.TScale", 
            background=c["bg_panel"], 
            troughcolor=c["border"], 
            sliderthickness=15
        )
        
        # Scrollbar (Barras de rolagem - Harmônicas)
        style.configure("Vertical.TScrollbar", 
            background=c["scroll_fg"], 
            troughcolor=c["bg_main"], 
            arrowcolor="white",
            bordercolor=c["bg_main"]
        )
        style.configure("Horizontal.TScrollbar", 
            background=c["scroll_fg"], 
            troughcolor=c["bg_main"], 
            arrowcolor="white",
            bordercolor=c["bg_main"]
        )

    def _create_widgets(self):
        """Cria todos os widgets da interface."""
        
        # Maximizar janela para melhor responsividade
        try:
            self.root.state('zoomed')
        except:
            pass 
            
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # === PAINEL DE CONTROLES (ESQUERDA) ===
        # Width levemente maior para conforto
        left_container = ttk.Frame(main_frame, width=320)
        left_container.pack(side=tk.LEFT, fill=tk.Y)
        left_container.pack_propagate(False)
        
        # Canvas para scroll dos controles (Fundo combina com bg_main)
        self.ctrl_canvas = tk.Canvas(
            left_container, 
            bg=self.colors["bg_main"], 
            highlightthickness=0, 
            width=320
        )
        ctrl_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.ctrl_canvas.yview)
        
        ctrl_inner = ttk.Frame(self.ctrl_canvas, style="Panel.TFrame")
        
        # Configurar scroll
        ctrl_inner.bind(
            "<Configure>",
            lambda e: self.ctrl_canvas.configure(scrollregion=self.ctrl_canvas.bbox("all"))
        )
        
        self.ctrl_canvas.create_window((0, 0), window=ctrl_inner, anchor="nw", width=320) 
        self.ctrl_canvas.configure(yscrollcommand=ctrl_scrollbar.set)
        
        # Pack do scroll
        ctrl_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ctrl_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Padding interno (Cria o efeito de "Card" branco sobre fundo cinza)
        pad_frame = ttk.Frame(ctrl_inner, style="Panel.TFrame")
        pad_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(
            pad_frame,
            text="B-Tree Viz",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 25), anchor="w")
        
        # --- Seleção de tipo de árvore ---
        tree_type_frame = ttk.LabelFrame(pad_frame, text=" Estrutura ", padding=15)
        tree_type_frame.pack(fill=tk.X, pady=10)
        
        self.tree_type_var = tk.StringVar(value="btree")
        ttk.Radiobutton(
            tree_type_frame,
            text="Árvore B",
            variable=self.tree_type_var,
            value="btree",
            command=self._on_tree_type_changed
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            tree_type_frame,
            text="Árvore B+",
            variable=self.tree_type_var,
            value="bplustree",
            command=self._on_tree_type_changed
        ).pack(anchor=tk.W, pady=2)
        
        # --- Configuração de Fanout ---
        fanout_frame = ttk.LabelFrame(pad_frame, text=" Grau (Ordem) ", padding=15)
        fanout_frame.pack(fill=tk.X, pady=10)
        
        self.fanout_var = tk.IntVar(value=3)
        
        fanout_header = ttk.Frame(fanout_frame, style="Panel.TFrame")
        fanout_header.pack(fill=tk.X)
        
        fanout_label = ttk.Label(fanout_header, text="n = 3", font=("Segoe UI", 12))
        fanout_label.pack(side=tk.LEFT)
        
        self.fanout_scale = ttk.Scale(
            fanout_frame,
            from_=3,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.fanout_var,
            command=lambda v: self._update_fanout_label(fanout_label, v)
        )
        self.fanout_scale.pack(fill=tk.X, pady=(10, 10))
        
        ttk.Button(
            fanout_frame,
            text="Aplicar Mudança",
            command=self._on_fanout_changed
        ).pack(fill=tk.X)
        
        # --- Operações ---
        ops_frame = ttk.LabelFrame(pad_frame, text=" Operações ", padding=15)
        ops_frame.pack(fill=tk.X, pady=10)
        
        # Key Type hidden mostly, assume numeric for simplicity or keep valid
        # Keeping it internal if needed, but UI cleaner without it if user uses nums usually.
        # Adding simple type selection if robust.
        self.key_type_var = tk.StringVar(value="numeric")

        ttk.Label(ops_frame, text="Valor:").pack(anchor=tk.W)
        self.key_entry = ttk.Entry(ops_frame, font=("Segoe UI", 11))
        self.key_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Grid layout for buttons
        btn_grid = ttk.Frame(ops_frame, style="Panel.TFrame")
        btn_grid.pack(fill=tk.X)
        
        ttk.Button(
            btn_grid,
            text="Inserir",
            command=self._on_insert_clicked
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            btn_grid,
            text="Buscar",
            command=self._on_search_clicked
        ).pack(fill=tk.X, pady=2)
        
        self.remove_btn = ttk.Button(
            btn_grid,
            text="Remover",
            command=self._on_remove_clicked
        )
        self.remove_btn.pack(fill=tk.X, pady=2)
        
        # --- Aleatório ---
        random_frame = ttk.LabelFrame(pad_frame, text=" Aleatório ", padding=15)
        random_frame.pack(fill=tk.X, pady=10)
        
        # Inputs Row
        r_inputs = ttk.Frame(random_frame, style="Panel.TFrame")
        r_inputs.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(r_inputs, text="Qtd:").pack(side=tk.LEFT)
        self.random_count_entry = ttk.Entry(r_inputs, width=5)
        self.random_count_entry.insert(0, "10")
        self.random_count_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(r_inputs, text="Max:").pack(side=tk.LEFT, padx=(5,0))
        self.random_max_entry = ttk.Entry(r_inputs, width=6)
        self.random_max_entry.insert(0, "100") # Simplified max default
        self.random_max_entry.pack(side=tk.LEFT, padx=5)
        
        # Inputs hidden for simplicity (Min usually 1)
        self.random_min_entry = ttk.Entry(r_inputs, width=0)
        self.random_min_entry.insert(0, "1")
        
        ttk.Button(
            random_frame,
            text="Gerar",
            command=self._on_random_insert_clicked
        ).pack(fill=tk.X)

        
        # === FIM DOS CONTROLES ===
        
        # === CANVAS (DIREITA) ===
        canvas_container = ttk.Frame(main_frame)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas clean com cor ajustada ao tema
        self.canvas = tk.Canvas(
            canvas_container,
            bg=self.colors["canvas_bg"], 
            highlightthickness=0
        )
        
        v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas.configure(scrollregion=(0, 0, 2000, 2000))
    
    # === MÉTODOS DE CALLBACK INTERNOS ===
    
    def _update_fanout_label(self, label: ttk.Label, value):
        """Atualiza o label do fanout."""
        n = int(float(value))
        label.config(text=f"n = {n}")
    
    def _on_tree_type_changed(self):
        """Callback quando o tipo de árvore é alterado."""
        if self.on_tree_type_change:
            self.on_tree_type_change(self.tree_type_var.get())
    
    def _on_fanout_changed(self):
        """Callback quando o fanout é alterado."""
        if self.on_fanout_change:
            self.on_fanout_change(self.fanout_var.get())
    
    def _on_insert_clicked(self):
        """Callback do botão Inserir."""
        key = self._parse_key()
        if key is not None and self.on_insert:
            self.on_insert(key)
    
    def _on_search_clicked(self):
        """Callback do botão Buscar."""
        key = self._parse_key()
        if key is not None and self.on_search:
            self.on_search(key)
    
    def _on_remove_clicked(self):
        """Callback do botão Remover."""
        key = self._parse_key()
        if key is not None and self.on_remove:
            self.on_remove(key)
    
    def _on_random_insert_clicked(self):
        """Callback do botão Inserir Aleatório."""
        try:
            count = int(self.random_count_entry.get())
            min_val = int(self.random_min_entry.get())
            max_val = int(self.random_max_entry.get())
            
            if count <= 0:
                messagebox.showerror("Erro", "Quantidade deve ser > 0")
                return
            
            if min_val >= max_val:
                messagebox.showerror("Erro", "Min deve ser < Max")
                return
            
            if self.on_random_insert:
                self.on_random_insert(count, min_val, max_val)
        
        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {e}")
    
    def _on_random_remove_clicked(self):
        """Callback do botão Remover Aleatório. (Simplificado/Oculto na UI principal)"""
        if self.on_random_remove:
            self.on_random_remove(1) # Default 
    
    def _on_next_clicked(self):
        if self.on_step_next: self.on_step_next()
    
    def _on_prev_clicked(self):
        if self.on_step_prev: self.on_step_prev()
    
    def _on_reset_clicked(self):
        if self.on_reset: self.on_reset()
    
    def _on_play_clicked(self):
        if self.on_play: self.on_play()
    
    def _parse_key(self) -> Optional[any]:
        """Faz parse da chave digitada."""
        key_str = self.key_entry.get().strip()
        if not key_str:
            messagebox.showwarning("Aviso", "Digite uma chave")
            return None
        
        if self.key_type_var.get() == "numeric":
            try:
                return int(key_str)
            except ValueError:
                messagebox.showerror("Erro", "Chave deve ser um número inteiro")
                return None
        else:
            return key_str
    
    # === MÉTODOS PÚBLICOS PARA ATUALIZAR UI ===
    
    def update_metrics(self, node_accesses: int, batch_time_ms: Optional[float]):
        pass
    
    def update_progress(self, progress_text: str):
        pass
    
    def update_event_message(self, message: str):
        pass
    
    def enable_playback_controls(self, has_prev: bool, has_next: bool):
        pass
    
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """Mostra uma mensagem ao usuário."""
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)