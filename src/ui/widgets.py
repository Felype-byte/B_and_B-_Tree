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
        
        self.root.configure(bg="#121212")
        self._create_widgets()

    def _setup_theme(self):
        """Configura o tema visual (Clean Modern)."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Paleta Modern Dark
        bg_dark = "#121212"      # Fundo Principal
        bg_panel = "#1e1e1e"     # Painéis
        fg_text = "#e0e0e0"      # Texto Principal
        accent_color = "#3700b3" # Roxo Profundo (Primary)
        accent_light = "#6200ea" # Roxo Claro (Hover)
        border_color = "#333333" # Bordas sutis
        
        # Configuração Geral
        style.configure(".", background=bg_dark, foreground=fg_text, font=("Segoe UI", 10))
        
        # Frames
        style.configure("TFrame", background=bg_dark)
        style.configure("Panel.TFrame", background=bg_panel)
        
        # Labelframes
        style.configure("TLabelframe", background=bg_panel, foreground="#b0bec5", bordercolor=border_color)
        style.configure("TLabelframe.Label", background=bg_panel, foreground="#81d4fa", font=("Segoe UI", 10, "bold"))
        
        # Labels
        style.configure("TLabel", background=bg_panel, foreground=fg_text)
        style.configure("Title.TLabel", background=bg_panel, foreground="#ffffff", font=("Segoe UI", 16, "bold"))
        
        # Botões (Flat Modern)
        style.configure("TButton", 
            background=accent_color, 
            foreground="white", 
            borderwidth=0, 
            focuscolor="none",
            padding=8,
            font=("Segoe UI", 9, "bold")
        )
        style.map("TButton",
            background=[('active', accent_light), ('pressed', '#000000')],
            foreground=[('disabled', '#555555')]
        )
        
        # Radiobuttons
        style.configure("TRadiobutton", background=bg_panel, foreground=fg_text)
        style.map("TRadiobutton", background=[('active', bg_panel)])
        
        # Entry
        style.configure("TEntry", fieldbackground="#2c2c2c", foreground="white", insertcolor="white", bordercolor=border_color)
        
        # Scale
        style.configure("Horizontal.TScale", background=bg_panel, troughcolor="#2c2c2c", sliderthickness=15)
        
        # Scrollbar
        style.configure("Vertical.TScrollbar", background="#2c2c2c", troughcolor="#121212", arrowcolor="#e0e0e0")
        style.configure("Horizontal.TScrollbar", background="#2c2c2c", troughcolor="#121212", arrowcolor="#e0e0e0")

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
        
        # Canvas para scroll dos controles
        self.ctrl_canvas = tk.Canvas(left_container, bg="#1e1e1e", highlightthickness=0, width=320)
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
        
        # Padding interno
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
        
        # Canvas clean
        self.canvas = tk.Canvas(
            canvas_container,
            bg="#121212", 
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
