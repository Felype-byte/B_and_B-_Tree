"""
Interface gráfica principal - Widgets e janela.

Fornece todos os controles de UI para interação com as árvores.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import os
from PIL import Image, ImageTk


class MainWindow:
    """
    Janela principal da aplicação.
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Visualizador de Árvores B e B+ - Edição Floresta")
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
        
        self.root.configure(bg="#2b1b17")
        self._create_widgets()

    def _setup_theme(self):
        """Configura o tema visual (Florestal)."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Paleta
        bg_dark = "#2b1b17"      # Madeira escura
        bg_panel = "#3e2723"     # Painel madeira
        fg_text = "#f1f8e9"      # Texto claro
        btn_bg = "#558b2f"       # Verde folha botão
        btn_active = "#689f38"   # Verde claro hover
        
        # Configuração Geral
        style.configure(".", background=bg_dark, foreground=fg_text, font=("Segoe UI", 10))
        
        # Frames
        style.configure("TFrame", background=bg_dark)
        style.configure("Panel.TFrame", background=bg_panel)
        
        # Labelframes
        style.configure("TLabelframe", background=bg_panel, foreground="#a1887f", bordercolor="#5d4037")
        style.configure("TLabelframe.Label", background=bg_panel, foreground="#dcedc8", font=("Segoe UI", 11, "bold"))
        
        # Labels
        style.configure("TLabel", background=bg_panel, foreground=fg_text)
        style.configure("Title.TLabel", background=bg_panel, foreground="#a5d6a7", font=("Segoe UI", 16, "bold"))
        
        # Botões (Estilo Folha)
        style.configure("TButton", 
            background=btn_bg, 
            foreground="white", 
            borderwidth=0, 
            focuscolor="none",
            padding=6,
            font=("Segoe UI", 9, "bold")
        )
        style.map("TButton",
            background=[('active', btn_active), ('pressed', '#33691e')],
            foreground=[('disabled', '#a1887f')]
        )
        
        # Radiobuttons
        style.configure("TRadiobutton", background=bg_panel, foreground=fg_text)
        style.map("TRadiobutton", background=[('active', bg_panel)])
        
        # Entry
        style.configure("TEntry", fieldbackground="#4e342e", foreground="white", insertcolor="white", bordercolor="#8d6e63")
        
        # Scale
        style.configure("Horizontal.TScale", background=bg_panel, troughcolor="#4e342e", sliderthickness=20)
        
        # Scrollbar
        style.configure("Vertical.TScrollbar", background="#5d4037", troughcolor="#2b1b17", arrowcolor="#dcedc8")
        style.configure("Horizontal.TScrollbar", background="#5d4037", troughcolor="#2b1b17", arrowcolor="#dcedc8")

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
        # Container com Scrollbar para os controles
        left_container = ttk.Frame(main_frame, width=350) # Removido estilo para ser neutro
        left_container.pack(side=tk.LEFT, fill=tk.Y)
        left_container.pack_propagate(False)
        
        # Canvas para scroll dos controles E BACKGROUND DE PEDRA
        self.ctrl_canvas = tk.Canvas(left_container, bg="#3e2723", highlightthickness=0, width=320)
        ctrl_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.ctrl_canvas.yview)
        
        # Opção de background removida a pedido do usuário (ficou melhor clean)
        # self.bg_sidebar_ref = ...

        # Frame interno que vai conter os widgets
        # Nota: Tkinter frames padrões não suportam transparência real. 
        # Vamos tentar usar estilo minimalista ou aceitar que os frames terão fundo.
        # Mas o usuário pediu "fundo de pedra".
        ctrl_inner = ttk.Frame(self.ctrl_canvas, style="Panel.TFrame") # Mantendo fundo madeira por enquanto para legibilidade
        
        # Configurar scroll
        ctrl_inner.bind(
            "<Configure>",
            lambda e: self.ctrl_canvas.configure(scrollregion=self.ctrl_canvas.bbox("all"))
        )
        # Centralizar frame interno no canvas para ver a pedra nas bordas?
        self.ctrl_canvas.create_window((15, 15), window=ctrl_inner, anchor="nw", width=300) 
        self.ctrl_canvas.configure(yscrollcommand=ctrl_scrollbar.set)
        
        # Pack do scroll
        ctrl_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ctrl_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Padding interno
        pad_frame = ttk.Frame(ctrl_inner, style="Panel.TFrame")
        pad_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_label = ttk.Label(
            pad_frame,
            text="🌿 Floresta B-Tree",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))
        
        # --- Seleção de tipo de árvore ---
        tree_type_frame = ttk.LabelFrame(pad_frame, text="Tipo de Árvore", padding=10)
        tree_type_frame.pack(fill=tk.X, pady=5)
        
        self.tree_type_var = tk.StringVar(value="btree")
        ttk.Radiobutton(
            tree_type_frame,
            text="Árvore B",
            variable=self.tree_type_var,
            value="btree",
            command=self._on_tree_type_changed
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            tree_type_frame,
            text="Árvore B+",
            variable=self.tree_type_var,
            value="bplustree",
            command=self._on_tree_type_changed
        ).pack(anchor=tk.W)
        
        # --- Configuração de Fanout ---
        fanout_frame = ttk.LabelFrame(pad_frame, text="Fanout (Grau)", padding=10)
        fanout_frame.pack(fill=tk.X, pady=10)
        
        self.fanout_var = tk.IntVar(value=3)
        
        fanout_label = ttk.Label(fanout_frame, text="n = 3", font=("Segoe UI", 12, "bold"))
        fanout_label.pack()
        
        self.fanout_scale = ttk.Scale(
            fanout_frame,
            from_=3,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.fanout_var,
            command=lambda v: self._update_fanout_label(fanout_label, v)
        )
        self.fanout_scale.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            fanout_frame,
            text="Aplicar & Reiniciar",
            command=self._on_fanout_changed
        ).pack(fill=tk.X, pady=5)
        
        # --- Tipo de Chave ---
        key_type_frame = ttk.LabelFrame(pad_frame, text="Tipo de Chave", padding=10)
        key_type_frame.pack(fill=tk.X, pady=5)
        
        self.key_type_var = tk.StringVar(value="numeric")
        ttk.Radiobutton(
            key_type_frame,
            text="Numérico",
            variable=self.key_type_var,
            value="numeric"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            key_type_frame,
            text="String",
            variable=self.key_type_var,
            value="string"
        ).pack(anchor=tk.W)
        
        # --- Operações ---
        ops_frame = ttk.LabelFrame(pad_frame, text="Operações", padding=10)
        ops_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ops_frame, text="Chave:").pack(anchor=tk.W)
        self.key_entry = ttk.Entry(ops_frame)
        self.key_entry.pack(fill=tk.X, pady=5)
        
        btn_frame = ttk.Frame(ops_frame, style="Panel.TFrame")
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Inserir",
            command=self._on_insert_clicked
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        ttk.Button(
            btn_frame,
            text="Buscar",
            command=self._on_search_clicked
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.remove_btn = ttk.Button(
            btn_frame,
            text="Remover",
            command=self._on_remove_clicked
        )
        self.remove_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        # --- Inserção Aleatória (COMPLETO) ---
        random_frame = ttk.LabelFrame(pad_frame, text="Inserção Aleatória", padding=10)
        random_frame.pack(fill=tk.X, pady=5)
        
        rf_top = ttk.Frame(random_frame, style="Panel.TFrame")
        rf_top.pack(fill=tk.X)
        
        ttk.Label(rf_top, text="Qtd:").pack(side=tk.LEFT)
        self.random_count_entry = ttk.Entry(rf_top, width=8)
        self.random_count_entry.insert(0, "10")
        self.random_count_entry.pack(side=tk.LEFT, padx=5)
        
        rf_mid = ttk.Frame(random_frame, style="Panel.TFrame")
        rf_mid.pack(fill=tk.X, pady=5)
        
        ttk.Label(rf_mid, text="Min:").pack(side=tk.LEFT)
        self.random_min_entry = ttk.Entry(rf_mid, width=6)
        self.random_min_entry.insert(0, "1")
        self.random_min_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(rf_mid, text="Max:").pack(side=tk.LEFT, padx=(5,0))
        self.random_max_entry = ttk.Entry(rf_mid, width=6)
        self.random_max_entry.insert(0, "1000")
        self.random_max_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            random_frame,
            text="Inserir Lote",
            command=self._on_random_insert_clicked
        ).pack(fill=tk.X, pady=5)
        
        # --- Remoção Aleatória (COMPLETO) ---
        remove_random_frame = ttk.LabelFrame(pad_frame, text="Remoção Aleatória", padding=10)
        remove_random_frame.pack(fill=tk.X, pady=5)
        
        rr_top = ttk.Frame(remove_random_frame, style="Panel.TFrame")
        rr_top.pack(fill=tk.X)
        
        ttk.Label(rr_top, text="Qtd:").pack(side=tk.LEFT)
        self.remove_count_entry = ttk.Entry(rr_top, width=8)
        self.remove_count_entry.insert(0, "5")
        self.remove_count_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            remove_random_frame,
            text="Remover Aleatório",
            command=self._on_random_remove_clicked
        ).pack(fill=tk.X, pady=5)
        
        # === FIM DOS CONTROLES ===
        
        # === CANVAS (DIREITA) ===
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas temático
        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#2b1b17",  # Fundo Madeira Escura
            highlightthickness=0
        )
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
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
        """Callback do botão Remover Aleatório."""
        try:
            count = int(self.remove_count_entry.get())
            
            if count <= 0:
                messagebox.showerror("Erro", "Quantidade deve ser > 0")
                return
            
            if self.on_random_remove:
                self.on_random_remove(count)
        
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}")
    
    def _on_next_clicked(self):
        """Callback do botão Próximo."""
        if self.on_step_next:
            self.on_step_next()
    
    def _on_prev_clicked(self):
        """Callback do botão Anterior."""
        if self.on_step_prev:
            self.on_step_prev()
    
    def _on_reset_clicked(self):
        """Callback do botão Início."""
        if self.on_reset:
            self.on_reset()
    
    def _on_play_clicked(self):
        """Callback do botão Play."""
        if self.on_play:
            self.on_play()
    
    def _parse_key(self) -> Optional[any]:
        """
        Faz parse da chave digitada.
        
        Returns:
            Chave parseada ou None se inválido
        """
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
        """
        Atualiza labels de métricas.
        (Desabilitado: UI simplificada)
        """
        pass
    
    def update_progress(self, progress_text: str):
        """Atualiza o texto de progresso da reprodução. (Desabilitado)"""
        pass
    
    def update_event_message(self, message: str):
        """Atualiza a mensagem do evento atual. (Desabilitado)"""
        pass
    
    def enable_playback_controls(self, has_prev: bool, has_next: bool):
        """
        Habilita/desabilita controles de reprodução. (Desabilitado)
        """
        pass
    
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """
        Mostra uma mensagem ao usuário.
        
        Args:
            title: Título da mensagem
            message: Conteúdo da mensagem
            msg_type: Tipo ('info', 'warning', 'error')
        """
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
