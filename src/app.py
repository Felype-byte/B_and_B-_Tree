"""
Aplicação principal - Visualizador de Árvores B e B+.

Ponto de entrada da aplicação. Conecta UI, core e controla o fluxo.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Set, Any

from core import (
    BTree, BPlusTree, Tracer, Metrics,
    validate_btree, validate_bplustree, ValidationError,
    generate_unique_random_ints, batch_insert,
    choose_existing_keys, batch_remove
)
from ui import MainWindow, TreeCanvas, StepController


class TreeVisualizerApp:
    """
    Aplicação principal do visualizador.
    """
    
    def __init__(self):
        # Core components
        self.tracer = Tracer()
        self.metrics = Metrics()
        self.tree = None
        self.tree_type = "btree"
        self.fanout = 3
        
        # Rastrear chaves existentes (para operações aleatórias)
        self.existing_keys: Set[Any] = set()
        
        # UI components
        self.root = tk.Tk()
        self.window = MainWindow(self.root)
        self.canvas = TreeCanvas(self.window.canvas)
        self.controller = StepController()
        
        # Conectar callbacks
        self._connect_callbacks()
        
        # Criar árvore inicial
        self._create_tree()
        
        # Render inicial
        self._render_tree()
    
    def _connect_callbacks(self):
        """Conecta os callbacks da UI com os handlers."""
        self.window.on_insert = self.handle_insert
        self.window.on_search = self.handle_search
        self.window.on_remove = self.handle_remove
        self.window.on_random_insert = self.handle_random_insert
        self.window.on_random_remove = self.handle_random_remove
        self.window.on_fanout_change = self.handle_fanout_change
        self.window.on_tree_type_change = self.handle_tree_type_change
        self.window.on_step_next = self.handle_step_next
        self.window.on_step_prev = self.handle_step_prev
        self.window.on_reset = self.handle_reset
        self.window.on_play = self.handle_play
    
    def _create_tree(self):
        """Cria uma nova árvore com as configurações atuais."""
        if self.tree_type == "btree":
            self.tree = BTree(self.fanout, self.tracer, self.metrics)
        else:
            self.tree = BPlusTree(self.fanout, self.tracer, self.metrics)
        
        self.existing_keys.clear()
        self.metrics.reset_all()
    
    def _render_tree(self, highlight_info=None):
        """Renderiza a árvore no canvas."""
        try:
            self.canvas.render(self.tree, highlight_info)
            self.window.update_metrics(
                self.metrics.get_node_accesses(),
                self.metrics.get_last_elapsed_ms()
            )
        except Exception as e:
            print(f"Erro ao renderizar árvore: {e}")
    
    def _validate_tree(self):
        """Valida a árvore usando o validador apropriado."""
        if self.tree_type == "btree":
            validate_btree(self.tree)
        else:
            validate_bplustree(self.tree)
    
    def _update_playback_controls(self):
        """Atualiza os controles de reprodução."""
        has_prev = self.controller.can_step_prev()
        has_next = self.controller.can_step_next()
        
        self.window.enable_playback_controls(has_prev, has_next)
        self.window.update_progress(self.controller.get_progress_text())
        
        # Atualizar mensagem do evento
        highlight = self.controller.get_current_highlight()
        message = highlight.get('message', '')
        self.window.update_event_message(message)
    
    # === HANDLERS DE OPERAÇÕES ===
    
    def handle_insert(self, key: Any):
        """Handler para inserção de chave."""
        try:
            # Limpar tracer e métricas
            self.tracer.clear()
            self.metrics.reset_accesses()
            
            # Tentar inserir
            success = self.tree.insert(key)
            
            if success:
                self.existing_keys.add(key)
                
                # Validar árvore
                try:
                    validate_btree(self.tree)
                except ValidationError as e:
                    messagebox.showerror(
                        "Erro de Validação",
                        f"A árvore violou uma invariante:\n{e}"
                    )
                
                # Carregar eventos no controller
                events = self.tracer.get_events()
                self.controller.load_events(events)
                
                # Renderizar estado inicial
                if events:
                    self.controller.reset()
                    highlight = self.controller.get_current_highlight()
                    self._render_tree(highlight)
                else:
                    self._render_tree()
                
                self._update_playback_controls()
                
                self.window.show_message(
                    "Sucesso",
                    f"Chave {key} inserida com sucesso!\n"
                    f"Use os controles de reprodução para ver passo a passo.",
                    "info"
                )
            else:
                self._render_tree() # Limpar highlights anteriores
                self.window.show_message(
                    "Aviso",
                    f"Chave {key} já existe na árvore.",
                    "warning"
                )
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao inserir: {e}")
    
    def handle_search(self, key: Any):
        """Handler para busca de chave."""
        try:
            # Limpar tracer e métricas
            self.tracer.clear()
            self.metrics.reset_accesses()
            
            # Buscar
            result = self.tree.search(key)
            
            # Carregar eventos no controller
            events = self.tracer.get_events()
            self.controller.load_events(events)
            
            # Renderizar estado inicial
            if events:
                self.controller.reset()
                highlight = self.controller.get_current_highlight()
                self._render_tree(highlight)
            else:
                self._render_tree()
            
            self._update_playback_controls()
            
            # Mensagem de resultado
            if result['found']:
                self.window.show_message(
                    "Encontrado",
                    f"Chave {key} encontrada no nó #{result['node_id']}, "
                    f"posição {result['index']}.\n"
                    f"Acessos a nós: {self.metrics.get_node_accesses()}",
                    "info"
                )
            else:
                self.window.show_message(
                    "Não Encontrado",
                    f"Chave {key} não está na árvore.\n"
                    f"Acessos a nós: {self.metrics.get_node_accesses()}",
                    "info"
                )
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar: {e}")
    
    def handle_remove(self, key: Any):
        """Handler para remoção de chave."""
        try:
            # Limpar tracer e métricas
            self.tracer.clear()
            self.metrics.reset_accesses()
            
            # Tentar remover
            success = self.tree.delete(key)
            
            if success:
                self.existing_keys.discard(key)
                
                # Validar árvore
                try:
                    validate_btree(self.tree)
                except ValidationError as e:
                    messagebox.showerror(
                        "Erro de Validação",
                        f"A árvore violou uma invariante:\n{e}"
                    )
                
                # Carregar eventos no controller
                events = self.tracer.get_events()
                self.controller.load_events(events)
                
                # Renderizar estado inicial
                if events:
                    self.controller.reset()
                    highlight = self.controller.get_current_highlight()
                    self._render_tree(highlight)
                else:
                    self._render_tree()
                
                self._update_playback_controls()
                
                self.window.show_message(
                    "Sucesso",
                    f"Chave {key} removida com sucesso!\n"
                    f"Use os controles de reprodução para ver passo a passo.",
                    "info"
                )
            else:
                self._render_tree() # Limpar highlights anteriores para evitar confusão
                self.window.show_message(
                    "Aviso",
                    f"Chave {key} não existe na árvore.",
                    "warning"
                )
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover: {e}")
    
    def handle_random_insert(self, count: int, min_val: int, max_val: int):
        """Handler para inserção aleatória."""
        try:
            # Gerar chaves únicas
            keys = generate_unique_random_ints(
                count, min_val, max_val, self.existing_keys
            )
            
            # Inserir em lote
            elapsed_ms, accesses = batch_insert(self.tree, keys)
            
            # Atualizar conjunto de chaves existentes
            self.existing_keys.update(keys)
            
            # Validar árvore
            try:
                validate_btree(self.tree)
            except ValidationError as e:
                messagebox.showerror(
                    "Erro de Validação",
                    f"A árvore violou uma invariante após inserção aleatória:\n{e}"
                )
            
            # Renderizar (sem eventos, pois tracer estava desabilitado)
            self._render_tree()
            
            # Limpar controller (não há eventos)
            self.controller.load_events([])
            self._update_playback_controls()
            
            # Mostrar estatísticas
            self.window.show_message(
                "Inserção Concluída",
                f"Inseridas {len(keys)} chaves aleatórias.\n"
                f"Tempo: {elapsed_ms:.2f} ms\n"
                f"Acessos a nós: {accesses}\n"
                f"Média: {elapsed_ms/len(keys):.3f} ms/chave",
                "info"
            )
        
        except ValueError as e:
            self.window.show_message("Erro", str(e), "error")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na inserção aleatória: {e}")
    
    def handle_random_remove(self, count: int):
        """Handler para remoção aleatória."""
        try:
            # Verificar se há chaves suficientes
            if len(self.existing_keys) == 0:
                self.window.show_message(
                    "Aviso",
                    "A árvore está vazia. Não há chaves para remover.",
                    "warning"
                )
                return
            
            # Ajustar quantidade se necessário
            actual_count = min(count, len(self.existing_keys))
            if actual_count < count:
                messagebox.showwarning(
                    "Aviso",
                    f"Árvore tem apenas {len(self.existing_keys)} chaves. "
                    f"Removendo {actual_count} chaves."
                )
            
            # Escolher chaves existentes
            keys_to_remove = choose_existing_keys(self.existing_keys, actual_count)
            
            # Remover em lote
            elapsed_ms, accesses = batch_remove(self.tree, keys_to_remove)
            
            # Atualizar conjunto de chaves existentes
            self.existing_keys.difference_update(keys_to_remove)
            
            # Validar árvore
            try:
                validate_btree(self.tree)
            except ValidationError as e:
                messagebox.showerror(
                    "Erro de Validação",
                    f"A árvore violou uma invariante após remoção aleatória:\n{e}"
                )
            
            # Renderizar (sem eventos, pois tracer estava desabilitado)
            self._render_tree()
            
            # Limpar controller (não há eventos)
            self.controller.load_events([])
            self._update_playback_controls()
            
            # Mostrar estatísticas
            self.window.show_message(
                "Remoção Concluída",
                f"Removidas {actual_count} chaves aleatórias.\n"
                f"Tempo: {elapsed_ms:.2f} ms\n"
                f"Acessos a nós: {accesses}\n"
                f"Média: {elapsed_ms/actual_count:.3f} ms/chave",
                "info"
            )
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na remoção aleatória: {e}")
    
    def handle_fanout_change(self, new_fanout: int):
        """Handler para mudança de fanout."""
        if new_fanout == self.fanout:
            return
        
        confirm = messagebox.askyesno(
            "Confirmar",
            f"Alterar fanout de {self.fanout} para {new_fanout} "
            f"irá reiniciar a árvore. Continuar?"
        )
        
        if confirm:
            self.fanout = new_fanout
            self._create_tree()
            self._render_tree()
            self.controller.load_events([])
            self._update_playback_controls()
            
            self.window.show_message(
                "Árvore Reiniciada",
                f"Nova árvore criada com fanout n={new_fanout}",
                "info"
            )
    
    def handle_tree_type_change(self, tree_type: str):
        """Handler para mudança de tipo de árvore."""
        if tree_type == self.tree_type:
            return
        
        # Confirmar mudança pois vai perder dados
        tree_name = "Árvore B" if tree_type == "btree" else "Árvore B+"
        confirm = messagebox.askyesno(
            "Confirmar",
            f"Alterar para {tree_name} irá reiniciar a árvore. Continuar?"
        )
        
        if confirm:
            self.tree_type = tree_type
            self._create_tree()
            self._render_tree()
            self.controller.load_events([])
            self._update_playback_controls()
            
            self.window.show_message(
                "Árvore Reiniciada",
                f"Nova {tree_name} criada com fanout n={self.fanout}",
                "info"
            )
    
    # === HANDLERS DE REPRODUÇÃO ===
    
    def handle_step_next(self):
        """Handler para próximo passo."""
        highlight = self.controller.step_next()
        if highlight:
            self._render_tree(highlight)
            self._update_playback_controls()
    
    def handle_step_prev(self):
        """Handler para passo anterior."""
        highlight = self.controller.step_prev()
        if highlight:
            self._render_tree(highlight)
            self._update_playback_controls()
    
    def handle_reset(self):
        """Handler para voltar ao início."""
        self.controller.reset()
        highlight = self.controller.get_current_highlight()
        self._render_tree(highlight)
        self._update_playback_controls()
    
    def handle_play(self):
        """Handler para reprodução automática."""
        def play_step():
            if self.controller.can_step_next():
                self.handle_step_next()
                # Agendar próximo passo após delay
                self.root.after(500, play_step)  # 500ms de delay
        
        play_step()
    
    def run(self):
        """Inicia o loop principal da aplicação."""
        self.root.mainloop()


def main():
    """Ponto de entrada principal."""
    app = TreeVisualizerApp()
    app.run()


if __name__ == "__main__":
    main()
