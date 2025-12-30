# 🌳 Visualizador de Árvores B e B+ - Guia Rápido

## 🚀 Como Executar

### Opção 1: Launcher Simples (Recomendado)
```bash
# Windows
run.bat

# Ou diretamente
python run.py
```

### Opção 2: Executar diretamente
```bash
cd src
python app.py
```

### Opção 3: Executar testes primeiro
```bash
python tests/test_manual_core.py
```

## ✅ Status da Implementação

**ETAPA 1: COMPLETA E TESTADA** ✅

- ✅ Árvore B com fanout 3-10
- ✅ Inserção com split automático
- ✅ Busca com rastreamento
- ✅ Sistema de eventos passo a passo
- ✅ Métricas de desempenho
- ✅ Interface gráfica completa
- ✅ Validação de invariantes
- ✅ Testes: 4/4 aprovados (100%)

## 📁 Estrutura

```
SGBD/
├── run.py              # ⭐ Launcher principal
├── run.bat             # ⭐ Launcher Windows
├── README.md           # Documentação completa
├── src/
│   ├── app.py          # Aplicação principal
│   ├── core/           # Lógica (btree, trace, metrics, etc.)
│   └── ui/             # Interface (widgets, canvas, controller)
└── tests/
    └── test_manual_core.py  # Testes completos
```

## 🎯 Primeiros Passos

1. **Execute** `python run.py`
2. **Configure** fanout (3-5 para ver splits)
3. **Insira** algumas chaves (ex: 10, 20, 30, 40, 50)
4. **Use** os botões ◀▶ para ver passo a passo
5. **Experimente** inserção aleatória

## 📊 Resultados dos Testes

```
✓ PASSOU | Operações Básicas
✓ PASSOU | Operações de Busca
✓ PASSOU | Rejeição de Duplicatas
✓ PASSOU | Diferentes Fanouts

✅ TODOS OS TESTES PASSARAM!
```

## 📖 Documentação

- **README.md**: Guia completo de uso
- **task.md**: Checklist de implementação
- **walkthrough.md**: Análise detalhada
- **implementation_plan.md**: Plano técnico

## 🔧 Requisitos

- Python 3.8+
- Tkinter (incluído no Python padrão)

## 💡 Dicas

- Use **fanout 3** para ver mais splits
- Use **fanout 10** para árvore mais larga
- **Inserção aleatória** popula rapidamente
- **Modo passo a passo** mostra cada decisão
- **Métricas** mostram acessos e tempo

## 🐛 Problemas?

Se encontrar erros de import:
```bash
# Certifique-se de executar do diretório raiz
cd e:\SGBD
python run.py
```

## 🎓 Próximas Etapas

- [ ] Árvore B+ com encadeamento de folhas
- [ ] Operação de remoção
- [ ] Range queries

---

**Versão:** 1.0.0 - Etapa 1 Completa  
**Data:** 26/12/2025
