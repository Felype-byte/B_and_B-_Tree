"""
Aplicação principal - Visualizador de Árvores B e B+.

Ponto de entrada da aplicação. Conecta UI, core e controla o fluxo.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Set, Any
import time
import random
import string
import math

# Importações do Core
from core import (
    BTree, BPlusTree, Tracer, Metrics,
    validate_btree, validate_bplustree, ValidationError,
    generate_unique_random_ints, batch_insert,
    choose_existing_keys, batch_remove
)
# Importações da Interface
from ui import MainWindow, TreeCanvas, StepController


class TreeVisualizerApp:
    """
    Aplicação principal do visualizador.
    Gerencia a lógica de negócios, o estado da árvore e a ponte entre UI e Algoritmos.
    """
    
    def __init__(self):
        # Componentes do Core
        self.tracer = Tracer()
        self.metrics = Metrics()
        self.tree = None
        self.tree_type = "btree"
        self.fanout = 3         
        
        # Cache de chaves existentes para operações rápidas e validação de duplicatas
        self.existing_keys: Set[Any] = set()
        
        # Componentes da UI
        self.root = tk.Tk()
        self.window = MainWindow(self.root)
        self.canvas = TreeCanvas(self.window.canvas)
        self.controller = StepController()
        
        # Inicialização
        self._connect_callbacks()
        self._create_tree()
        self._render_tree()
    
    def _connect_callbacks(self):
        """Conecta os eventos da Interface (botões) aos Métodos desta classe."""
        self.window.on_insert = self.handle_insert
        self.window.on_search = self.handle_search
        self.window.on_remove = self.handle_remove
        self.window.on_random_insert = self.handle_random_insert
        self.window.on_random_remove = self.handle_random_remove
        self.window.on_fanout_change = self.handle_fanout_change
        self.window.on_tree_type_change = self.handle_tree_type_change
        self.window.on_data_type_change = self.handle_data_type_change
        
        self.window.on_step_next = self.handle_step_next
        self.window.on_step_prev = self.handle_step_prev
        self.window.on_reset = self.handle_reset
        self.window.on_play = self.handle_play
    
    def _create_tree(self):
        """Recria a estrutura de dados (Árvore) do zero."""
        if self.tree_type == "btree":
            self.tree = BTree(self.fanout, self.tracer, self.metrics)
        else:
            self.tree = BPlusTree(self.fanout, self.tracer, self.metrics)
        
        self.existing_keys.clear()
        self.metrics.reset_all()
    
    def _render_tree(self, highlight_info=None):
        """Desenha a árvore no canvas e atualiza painéis laterais."""
        try:
            self.canvas.render(self.tree, highlight_info)
            
            # Atualiza o painel de métricas na UI
            # Mostramos 'reads' como métrica principal de acesso
            self.window.update_metrics(
                self.metrics.reads, 
                self.metrics.get_last_elapsed_ms()
            )
        except Exception as e:
            print(f"Erro crítico ao renderizar: {e}")
    
    def _validate_tree(self):
        """Executa a validação estrutural da árvore."""
        if self.tree_type == "btree":
            validate_btree(self.tree)
        else:
            validate_bplustree(self.tree)
    
    def _update_playback_controls(self):
        """Habilita/Desabilita botões de Next/Prev e atualiza mensagens de passo."""
        has_prev = self.controller.can_step_prev()
        has_next = self.controller.can_step_next()
        
        self.window.enable_playback_controls(has_prev, has_next)
        self.window.update_progress(self.controller.get_progress_text())
        
        highlight = self.controller.get_current_highlight()
        message = highlight.get('message', '')
        self.window.update_event_message(message)
    
    # =========================================================================
    # HANDLERS DE CONFIGURAÇÃO (Mudança de Tipo, Fanout, Reset)
    # =========================================================================

    def handle_data_type_change(self, new_type: str) -> bool:
        """
        Chamado ao trocar entre Numérico e Texto.
        Pede confirmação se houver dados, pois isso exige limpar a árvore.
        """
        if len(self.existing_keys) == 0:
            return True

        if messagebox.askyesno("Resetar Árvore?", 
                               f"Mudar para modo '{new_type}' apagará a árvore atual. Continuar?"):
            self._create_tree()
            self._render_tree()
            self.controller.load_events([])
            self._update_playback_controls()
            self.window.show_message("Reset", "Árvore reiniciada para o novo tipo de dado.", "info")
            return True
        return False

    def handle_fanout_change(self, new_fanout: int):
        """Altera o grau (ordem) da árvore."""
        if new_fanout == self.fanout:
            return
        
        if messagebox.askyesno("Confirmar", f"Reiniciar árvore com grau {new_fanout}?"):
            self.fanout = new_fanout
            self._create_tree()
            self._render_tree()
            self.controller.load_events([])
            self._update_playback_controls()
            
            self.window.show_message("Reiniciado", f"Nova árvore criada com fanout n={new_fanout}", "info")
    
    def handle_tree_type_change(self, tree_type: str):
        """Alterna entre B-Tree e B+ Tree."""
        if tree_type == self.tree_type:
            return
        
        tree_name = "Árvore B" if tree_type == "btree" else "Árvore B+"
        if messagebox.askyesno("Confirmar", f"Mudar para {tree_name}? (Reinicia árvore)"):
            self.tree_type = tree_type
            self._create_tree()
            self._render_tree()
            self.controller.load_events([])
            self._update_playback_controls()
            
            self.window.show_message("Reiniciado", f"Nova {tree_name} criada", "info")

    # =========================================================================
    # HANDLERS DE OPERAÇÕES (Inserir, Buscar, Remover)
    # =========================================================================
    
    def handle_insert(self, key: Any):
        """Inserção manual de um único valor."""
        try:
            self.tracer.clear()
            self.metrics.reset_accesses()
            
            # --- PROTEÇÃO 1: Verifica cache local ---
            if key in self.existing_keys:
                self.window.show_message("Aviso", f"Chave '{key}' já existe (Cache).", "warning")
                return
            
            # --- PROTEÇÃO 2: Verifica árvore real (Safety Check) ---
            # Impede o erro de validação 'CKC' ou duplicata interna
            if self.tree.search(key)['found']:
                self.existing_keys.add(key) # Sincroniza se estava faltando
                self.window.show_message("Aviso", f"Chave '{key}' já existe na árvore.", "warning")
                return

            # Executa inserção com cronômetro
            self.metrics.start_timer()
            success = self.tree.insert(key)
            elapsed_ms = self.metrics.stop_timer()
            
            if success:
                self.existing_keys.add(key)
                
                # Validação Estrutural
                try:
                    self._validate_tree()
                except ValidationError as e:
                    messagebox.showerror("Erro de Validação", f"A árvore violou uma invariante:\n{e}")
                
                # Atualiza Interface e Histórico
                events = self.tracer.get_events()
                self.controller.load_events(events)
                
                if events:
                    self.controller.reset()
                    self._render_tree(self.controller.get_current_highlight())
                else:
                    self._render_tree()
                
                self._update_playback_controls()
                
                # Mensagem de Sucesso com Métricas de I/O
                self.window.show_message(
                    "Sucesso",
                    f"Chave '{key}' inserida em {elapsed_ms:.4f} ms!\n"
                    f"I/O: {self.metrics.reads} Reads / {self.metrics.writes} Writes",
                    "info"
                )
            else:
                # Caso raro onde search falhou mas insert retornou False
                self._render_tree()
                self.window.show_message("Aviso", f"Chave '{key}' já existe (Recusado pelo Core).", "warning")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inserir: {e}")
    
    def handle_search(self, key: Any):
        """Busca de um valor."""
        try:
            self.tracer.clear()
            self.metrics.reset_accesses()
            
            self.metrics.start_timer()
            result = self.tree.search(key)
            elapsed_ms = self.metrics.stop_timer()
            
            events = self.tracer.get_events()
            self.controller.load_events(events)
            
            if events:
                self.controller.reset()
                self._render_tree(self.controller.get_current_highlight())
            else:
                self._render_tree()
            
            self._update_playback_controls()
            
            # Monta mensagem de I/O
            msg_io = f"I/O: {self.metrics.reads} Reads" # Busca geralmente não tem Writes
            
            if result['found']:
                self.window.show_message(
                    "Encontrado", 
                    f"Chave '{key}' no nó #{result['node_id']}.\nTempo: {elapsed_ms:.4f} ms\n{msg_io}", 
                    "info"
                )
            else:
                self.window.show_message(
                    "Não Encontrado", 
                    f"Chave '{key}' não está na árvore.\nTempo: {elapsed_ms:.4f} ms\n{msg_io}", 
                    "info"
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar: {e}")
    
    def handle_remove(self, key: Any):
        """Remoção manual de um valor."""
        try:
            self.tracer.clear()
            self.metrics.reset_accesses()
            
            self.metrics.start_timer()
            success = self.tree.delete(key)
            elapsed_ms = self.metrics.stop_timer()
            
            if success:
                self.existing_keys.discard(key)
                
                try:
                    self._validate_tree()
                except ValidationError as e:
                    messagebox.showerror("Erro de Validação", str(e))
                
                events = self.tracer.get_events()
                self.controller.load_events(events)
                
                if events:
                    self.controller.reset()
                    self._render_tree(self.controller.get_current_highlight())
                else:
                    self._render_tree()
                
                self._update_playback_controls()
                
                self.window.show_message(
                    "Sucesso", 
                    f"Chave '{key}' removida em {elapsed_ms:.4f} ms.\n"
                    f"I/O: {self.metrics.reads} Reads / {self.metrics.writes} Writes", 
                    "info"
                )
            else:
                self._render_tree()
                self.window.show_message("Aviso", "Chave não existe.", "warning")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover: {e}")
    
    def handle_random_insert(self, count: int, param1: int, param2: int):
        """
        Inserção em Lote (Aleatória).
        Inclui proteções robustas contra duplicatas e limites matemáticos.
        """
        try:
            mode = self.window.data_type_var.get()
            keys_to_insert = []
            
            # --- MODO NUMÉRICO ---
            if mode == "numeric":
                min_val = param1
                max_val = param2
                # Gera lista de candidatos únicos
                candidates = generate_unique_random_ints(count, min_val, max_val, set())
                
                # Filtra contra a árvore real para garantir integridade
                for k in candidates:
                    if not self.tree.search(k)['found']:
                        keys_to_insert.append(k)
                        self.existing_keys.add(k)
                    if len(keys_to_insert) >= count: 
                        break
            
            # --- MODO STRING ---
            else:
                length = param1
                
                # 1. Limite Matemático (Ex: 1 char = 26 opções)
                try: max_possibilities = int(math.pow(26, length))
                except OverflowError: max_possibilities = float('inf')
                
                if count > max_possibilities:
                    count = max_possibilities
                    self.window.show_message("Aviso", f"Limite atingido. Gerando máx possível: {count} strings.", "warning")

                candidates = set()
                attempts = 0
                max_attempts = count * 200 # Limite de tentativas
                
                while len(candidates) < count and attempts < max_attempts:
                    s = ''.join(random.choices(string.ascii_uppercase, k=length))
                    
                    # Verifica unicidade local (lote) e global (árvore)
                    if s not in candidates:
                        if not self.tree.search(s)['found']: 
                            candidates.add(s)
                            self.existing_keys.add(s)
                    attempts += 1
                
                keys_to_insert = list(candidates)
                
                if len(keys_to_insert) < count:
                    self.window.show_message("Aviso", f"Geradas apenas {len(keys_to_insert)} chaves únicas (Timeout).", "warning")

            if not keys_to_insert:
                return

            # --- INSERÇÃO EM LOTE ---
            # batch_insert agora usa o self.tree.insert, que popula self.metrics
            elapsed_ms, accesses = batch_insert(self.tree, keys_to_insert)
            
            # Validação pós-lote
            try:
                self._validate_tree()
            except ValidationError as e:
                messagebox.showerror("Erro Crítico", f"Erro após inserção em lote:\n{e}")
            
            self._render_tree()
            self.controller.load_events([]) # Limpa eventos (muitos eventos travam a UI)
            self._update_playback_controls()
            
            type_lbl = "números" if mode == "numeric" else "strings"
            
            # Mensagem Final com I/O Acumulado
            self.window.show_message(
                "Concluído",
                f"Inseridos {len(keys_to_insert)} {type_lbl}.\n"
                f"Tempo: {elapsed_ms:.2f} ms\n"
                f"Total I/O: {self.metrics.reads} Reads / {self.metrics.writes} Writes",
                "info"
            )
        
        except ValueError as e:
            self.window.show_message("Erro de Valor", str(e), "error")
        except Exception as e:
            messagebox.showerror("Erro Genérico", f"Erro aleatório: {e}")
    
    def handle_random_remove(self, count: int):
        """Remoção em Lote (Aleatória)."""
        try:
            if not self.existing_keys: 
                return self.window.show_message("Aviso", "Árvore vazia.", "warning")
            
            actual_count = min(count, len(self.existing_keys))
            keys_rem = choose_existing_keys(self.existing_keys, actual_count)
            
            # Executa remoção em lote
            elapsed_ms, accesses, removed_count = batch_remove(self.tree, keys_rem)
            
            # Atualiza cache local
            self.existing_keys.difference_update(keys_rem)
            
            try: 
                self._validate_tree()
            except ValidationError as e: 
                messagebox.showerror("Erro Validação", str(e))
            
            self._render_tree()
            self.controller.load_events([])
            self._update_playback_controls()
            
            self.window.show_message(
                "Concluído", 
                f"Removidas {actual_count} chaves.\n"
                f"Tempo: {elapsed_ms:.2f} ms\n"
                f"Total I/O: {self.metrics.reads} Reads / {self.metrics.writes} Writes", 
                "info"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro remover: {e}")
    
    # =========================================================================
    # HANDLERS DE REPRODUÇÃO (Step-by-Step)
    # =========================================================================
    
    def handle_step_next(self):
        """Avança um passo na visualização."""
        if self.controller.step_next():
            self._render_tree(self.controller.get_current_highlight())
            self._update_playback_controls()
            
    def handle_step_prev(self):
        """Volta um passo na visualização."""
        if self.controller.step_prev():
            self._render_tree(self.controller.get_current_highlight())
            self._update_playback_controls()
            
    def handle_reset(self):
        """Volta para o início da animação."""
        self.controller.reset()
        self._render_tree(self.controller.get_current_highlight())
        self._update_playback_controls()
        
    def handle_play(self):
        """Reprodução automática."""
        def play_step():
            if self.controller.can_step_next():
                self.handle_step_next()
                self.root.after(500, play_step) # 500ms de delay
        play_step()
    
    def run(self):
        """Inicia o loop principal da aplicação."""
        self.root.mainloop()


def main():
    app = TreeVisualizerApp()
    app.run()

if __name__ == "__main__":
    main()