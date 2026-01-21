"""
Interface gráfica principal - Widgets e janela.

Fornece todos os controles de UI para interação com as árvores.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable, Optional
import os

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
        
        # [NOVO] Callback para validar mudança de tipo de dado (pede reset)
        self.on_data_type_change: Optional[Callable] = None
        
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
        left_container = ttk.Frame(main_frame, width=320)
        left_container.pack(side=tk.LEFT, fill=tk.Y)
        left_container.pack_propagate(False)
        
        # Canvas para scroll dos controles
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
        
        # Padding interno (Card branco)
        pad_frame = ttk.Frame(ctrl_inner, style="Panel.TFrame")
        pad_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(
            pad_frame,
            text="B-Tree Viz",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # --- Configuração de Fanout (Comum a ambos) ---
        fanout_frame = ttk.LabelFrame(pad_frame, text=" Grau (Ordem) ", padding=15)
        fanout_frame.pack(fill=tk.X, pady=(0, 10))
        
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

        # --- Seleção de Estrutura (Comum a ambos) ---
        tree_type_frame = ttk.LabelFrame(pad_frame, text=" Estrutura ", padding=15)
        tree_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.tree_type_var = tk.StringVar(value="btree")
        ttk.Radiobutton(
            tree_type_frame, text="Árvore B", variable=self.tree_type_var, value="btree",
            command=self._on_tree_type_changed
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            tree_type_frame, text="Árvore B+", variable=self.tree_type_var, value="bplustree",
            command=self._on_tree_type_changed
        ).pack(anchor=tk.W, pady=2)

        # --- SELEÇÃO DE TIPO DE DADO (MENU ADAPTATIVO) ---
        dtype_frame = ttk.LabelFrame(pad_frame, text=" Tipo de Dado ", padding=15)
        dtype_frame.pack(fill=tk.X, pady=10)
        
        self.data_type_var = tk.StringVar(value="numeric")
        self.last_data_type = "numeric"  # [NOVO] Guarda o estado anterior para reverter se cancelar
        
        ttk.Radiobutton(
            dtype_frame, text="Numérico", variable=self.data_type_var, value="numeric",
            command=self._toggle_data_mode
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Radiobutton(
            dtype_frame, text="Texto (String)", variable=self.data_type_var, value="string",
            command=self._toggle_data_mode
        ).pack(side=tk.LEFT)

        # ==========================================================
        # CONTAINER NUMÉRICO
        # ==========================================================
        self.numeric_container = ttk.Frame(pad_frame, style="Panel.TFrame")
        
        # Operações Numéricas
        num_ops_frame = ttk.LabelFrame(self.numeric_container, text=" Operações (Num) ", padding=15)
        num_ops_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(num_ops_frame, text="Valor Inteiro:").pack(anchor=tk.W)
        self.num_entry = ttk.Entry(num_ops_frame, font=("Segoe UI", 11))
        self.num_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Botões Numéricos
        self._create_ops_buttons(num_ops_frame)
        
        # Aleatório Numérico
        num_random_frame = ttk.LabelFrame(self.numeric_container, text=" Aleatório (Num) ", padding=15)
        num_random_frame.pack(fill=tk.X, pady=10)
        
        # Inputs Row
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
        
        ttk.Label(nr_inputs, text="Min:").pack(side=tk.LEFT, padx=(5,0))
        self.random_min_entry = ttk.Entry(nr_inputs, width=6)
        self.random_min_entry.insert(0, "1")
        self.random_min_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            num_random_frame, text="Gerar Números",
            command=self._on_random_insert_clicked
        ).pack(fill=tk.X, pady=(0, 2))

        ttk.Button(
            num_random_frame, text="Remover (Qtd)",
            command=self._on_random_remove_clicked
        ).pack(fill=tk.X)

        # ==========================================================
        # CONTAINER STRING
        # ==========================================================
        self.string_container = ttk.Frame(pad_frame, style="Panel.TFrame")
        
        # Operações String
        str_ops_frame = ttk.LabelFrame(self.string_container, text=" Operações (Texto) ", padding=15)
        str_ops_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(str_ops_frame, text="Texto:").pack(anchor=tk.W)
        self.str_entry = ttk.Entry(str_ops_frame, font=("Segoe UI", 11))
        self.str_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Botões String
        self._create_ops_buttons(str_ops_frame)
        
        # Aleatório String
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
        self.str_random_len_entry.insert(0, "3") # Default 3 letras
        self.str_random_len_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            str_random_frame, text="Gerar Strings",
            command=self._on_random_insert_clicked
        ).pack(fill=tk.X, pady=(0, 2))

        ttk.Button(
            str_random_frame, text="Remover (Qtd)",
            command=self._on_random_remove_clicked
        ).pack(fill=tk.X)

        # Inicializa mostrando o numérico
        self.numeric_container.pack(fill=tk.BOTH, expand=True)
        
        # === FIM DOS CONTROLES ===
        
        # === CANVAS (DIREITA) ===
        canvas_container = ttk.Frame(main_frame)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- BARRA DE STATUS / PLAYBACK (Topo do Canvas) ---
        playback_frame = ttk.Frame(canvas_container, style="Panel.TFrame", padding=10)
        playback_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Grid para alinhar controles
        playback_frame.columnconfigure(1, weight=1)
        
        # Botões de Controle (Esquerda)
        pb_btns = ttk.Frame(playback_frame, style="Panel.TFrame")
        pb_btns.pack(side=tk.LEFT)
        
        self.btn_reset = ttk.Button(pb_btns, text="⏮", width=3, command=self._on_reset_clicked)
        self.btn_reset.pack(side=tk.LEFT, padx=2)
        
        self.btn_prev = ttk.Button(pb_btns, text="◀", width=3, command=self._on_prev_clicked)
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        
        self.btn_play = ttk.Button(pb_btns, text="▶", width=3, command=self._on_play_clicked)
        self.btn_play.pack(side=tk.LEFT, padx=2)
        
        self.btn_next = ttk.Button(pb_btns, text="▶", width=3, command=self._on_next_clicked)
        self.btn_next.pack(side=tk.LEFT, padx=2)
        
        # Mensagens de Status (Centro/Direita)
        info_frame = ttk.Frame(playback_frame, style="Panel.TFrame")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15)
        
        self.lbl_event = ttk.Label(info_frame, text="Pronto.", font=("Segoe UI", 11, "bold"), foreground=self.colors["accent"])
        self.lbl_event.pack(anchor="w")
        
        self.lbl_progress = ttk.Label(info_frame, text="", font=("Segoe UI", 9))
        self.lbl_progress.pack(anchor="w")
        
        # Métricas (Direita)
        stats_frame = ttk.Frame(playback_frame, style="Panel.TFrame")
        stats_frame.pack(side=tk.RIGHT)
        
        self.lbl_metrics = ttk.Label(stats_frame, text="I/O: 0", font=("Consolas", 10))
        self.lbl_metrics.pack(anchor="e")
        self.lbl_time = ttk.Label(stats_frame, text="0 ms", font=("Consolas", 10))
        self.lbl_time.pack(anchor="e")

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
    
    def _create_ops_buttons(self, parent):
        """Helper para criar os botões padrão de Inserir/Buscar/Remover."""
        btn_grid = ttk.Frame(parent, style="Panel.TFrame")
        btn_grid.pack(fill=tk.X)
        
        ttk.Button(btn_grid, text="Inserir", command=self._on_insert_clicked).pack(fill=tk.X, pady=2)
        ttk.Button(btn_grid, text="Buscar", command=self._on_search_clicked).pack(fill=tk.X, pady=2)
        ttk.Button(btn_grid, text="Remover", command=self._on_remove_clicked).pack(fill=tk.X, pady=2)

    def _toggle_data_mode(self):
        """
        Alterna a visibilidade dos containers.
        [MODIFICADO] Solicita confirmação ao controlador antes de mudar.
        """
        new_mode = self.data_type_var.get()
        
        # Se não mudou nada, ignora
        if new_mode == self.last_data_type:
            return

        # [NOVO] Verifica com o controlador se pode trocar (exibe confirmação de reset)
        if self.on_data_type_change:
            should_proceed = self.on_data_type_change(new_mode)
            if not should_proceed:
                # Se o usuário cancelar (clicar em 'No'), volta o botão para o estado anterior
                self.data_type_var.set(self.last_data_type)
                return

        # Se confirmou, atualiza o estado e troca os painéis
        self.last_data_type = new_mode
        
        if new_mode == "numeric":
            self.string_container.pack_forget()
            self.numeric_container.pack(fill=tk.BOTH, expand=True)
        else:
            self.numeric_container.pack_forget()
            self.string_container.pack(fill=tk.BOTH, expand=True)

    # === MÉTODOS DE CALLBACK INTERNOS ===
    
    def _update_fanout_label(self, label: ttk.Label, value):
        n = int(float(value))
        label.config(text=f"n = {n}")
    
    def _on_tree_type_changed(self):
        if self.on_tree_type_change:
            self.on_tree_type_change(self.tree_type_var.get())
    
    def _on_fanout_changed(self):
        if self.on_fanout_change:
            self.on_fanout_change(self.fanout_var.get())
    
    def _on_insert_clicked(self):
        key = self._parse_key()
        if key is not None and self.on_insert:
            self.on_insert(key)
    
    def _on_search_clicked(self):
        key = self._parse_key()
        if key is not None and self.on_search:
            self.on_search(key)
    
    def _on_remove_clicked(self):
        key = self._parse_key()
        if key is not None and self.on_remove:
            self.on_remove(key)
    
    def _on_random_insert_clicked(self):
        """Callback adaptativo para Numérico ou String."""
        try:
            mode = self.data_type_var.get()
            
            if mode == "numeric":
                count = int(self.random_count_entry.get())
                min_val = int(self.random_min_entry.get())
                max_val = int(self.random_max_entry.get())
                
                if count <= 0: raise ValueError("Quantidade deve ser > 0")
                if min_val >= max_val: raise ValueError("Min deve ser < Max")
                
                if self.on_random_insert:
                    self.on_random_insert(count, min_val, max_val)
            
            else: # string
                count = int(self.str_random_count_entry.get())
                length = int(self.str_random_len_entry.get())
                
                if count <= 0: raise ValueError("Quantidade deve ser > 0")
                if length <= 0: raise ValueError("Tamanho deve ser > 0")
                if length > 10: raise ValueError("Tamanho máx sugerido: 10")

                if self.on_random_insert:
                    self.on_random_insert(count, length, 0) # 0 é dummy para max_val
        
        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {e}")
    
    def _on_random_remove_clicked(self):
        """
        Callback adaptativo para remover quantidade aleatória.
        Usa um dialog para perguntar a quantidade, evitando remover tudo acidentalmente
        se o usuário esquecer de alterar o campo de inserção.
        """
        try:
            # Pergunta explicitamente ao usuário
            count = simpledialog.askinteger(
                "Remover Aleatoriamente",
                "Quantos itens deseja remover?",
                minvalue=1,
                parent=self.root
            )
            
            # Se usuário cancelou (None) ou digitou invalido
            if count is None:
                return
                
            if self.on_random_remove:
                self.on_random_remove(count)
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}") 
    
    def _on_next_clicked(self):
        if self.on_step_next: self.on_step_next()
    
    def _on_prev_clicked(self):
        if self.on_step_prev: self.on_step_prev()
    
    def _on_reset_clicked(self):
        if self.on_reset: self.on_reset()
    
    def _on_play_clicked(self):
        if self.on_play: self.on_play()
    
    def _parse_key(self) -> Optional[any]:
        """Faz parse da chave dependendo do modo ativo."""
        mode = self.data_type_var.get()
        
        if mode == "numeric":
            key_str = self.num_entry.get().strip()
            if not key_str:
                messagebox.showwarning("Aviso", "Digite um número")
                return None
            try:
                return int(key_str)
            except ValueError:
                messagebox.showerror("Erro", "Chave deve ser um número inteiro")
                return None
        else: # string
            key_str = self.str_entry.get().strip()
            if not key_str:
                messagebox.showwarning("Aviso", "Digite um texto")
                return None
            return key_str[:15] # Limite de segurança visual
    
    # === MÉTODOS PÚBLICOS PARA ATUALIZAR UI ===
    
    def update_metrics(self, node_accesses: int, batch_time_ms: Optional[float]):
        io_text = f"Reads: {node_accesses}" 
        self.lbl_metrics.config(text=io_text)
        
        if batch_time_ms is not None:
            self.lbl_time.config(text=f"{batch_time_ms:.2f} ms")
    
    def update_progress(self, progress_text: str):
        self.lbl_progress.config(text=f"Passo: {progress_text}")
    
    def update_event_message(self, message: str):
        self.lbl_event.config(text=message)
    
    def enable_playback_controls(self, has_prev: bool, has_next: bool):
        state_prev = "normal" if has_prev else "disabled"
        state_next = "normal" if has_next else "disabled"
        
        self.btn_prev.config(state=state_prev)
        self.btn_next.config(state=state_next)
    
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """Mostra uma mensagem ao usuário."""
        if msg_type == "info":
            messagebox.showinfo(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)