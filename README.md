# Visualizador de Árvores B e B+

Sistema interativo de visualização e aprendizado sobre Árvores B e B+ com interface gráfica, rastreamento passo a passo e métricas de desempenho.

## 📋 Características

- ✅ **Árvore B** completa com fanout configurável (3-10)
- ✅ **Árvore B+** completa com encadeamento de folhas
- 🔍 **Busca, Inserção e Remoção** com rastreamento detalhado
- 📊 **Visualização passo a passo** de cada operação
- 📈 **Métricas de desempenho**: acessos a nós e tempo de execução
- 🎲 **Inserções e Remoções aleatórias** em lote para testes
- ✔️ **Validação automática** de invariantes

## 🚀 Instalação

### Requisitos

- Python 3.8 ou superior
- Tkinter (geralmente já incluído na instalação padrão do Python)

### Verificar Tkinter

No Windows, Tkinter já vem instalado com Python. Para verificar:

```bash
python -c "import tkinter; print('Tkinter OK')"
```

Se houver erro, instale Python novamente marcando a opção "tcl/tk and IDLE".

## ▶️ Como Executar

### Executar a Aplicação

```bash
cd src
python app.py
```

Ou, a partir do diretório raiz:

```bash
python src/app.py
```

### Executar Testes Manuais

Antes de usar a GUI, você pode validar o core:

```bash
cd tests
python test_manual_core.py
```

Isso executará uma bateria de testes que verificam:
- Operações básicas de inserção
- Splits e criação de nova raiz
- Operações de busca
- Rejeição de duplicatas
- Diferentes valores de fanout

## 📖 Como Usar

### 1. Configurar a Árvore

**Escolher Fanout (Grau):**
- Use o slider para selecionar o grau `n` (de 3 a 10)
- Clique em "Aplicar & Reiniciar Árvore"
- Lembre-se: `max_keys = n - 1` e `max_children = n`

**Tipo de Chave:**
- **Numérico**: Para chaves inteiras (padrão)
- **String**: Para chaves textuais (comparação lexicográfica)

### 2. Operações Individuais

**Inserir:**
1. Digite uma chave no campo "Chave"
2. Clique em "Inserir"
3. A operação será rastreada e você poderá ver passo a passo

**Buscar:**
1. Digite uma chave no campo "Chave"
2. Clique em "Buscar"
3. O sistema mostrará o caminho percorrido e se a chave foi encontrada

**Remover:**
1. Digite uma chave no campo "Chave"
2. Clique em "Remover"
3. A operação será rastreada mostrando a busca e a remoção (incluindo merges e redistribuição)

### 3. Inserção Aleatória em Lote

1. Configure:
   - **Quantidade**: Número de chaves a inserir (ex: 100)
   - **Min/Max**: Intervalo de valores (ex: 1 a 1000)
2. Clique em "Inserir Aleatório"
3. O sistema mostrará:
   - Tempo total de execução
   - Número de acessos a nós
   - Tempo médio por chave

### 4. Visualização

Após uma operação de **Inserir**, **Buscar** ou **Remover**:

**O que você verá:**
- **Nós destacados** em amarelo quando visitados
- **Chaves destacadas** em verde durante comparação
- **Mensagens descritivas** no topo da tela
- **Progresso** da operação

### 5. Métricas

**Acessos a Nós:**
- Conta quantos nós foram visitados durante a operação
- Métrica educacional para entender complexidade
- Comparável a "número de disk accesses" em bancos de dados

**Tempo do Lote:**
- Tempo total de inserções aleatórias em milissegundos
- Útil para comparar desempenho com diferentes fanouts

## 🎓 Entendendo os Eventos

Durante o modo passo a passo, você verá diferentes tipos de eventos:

| Evento | Descrição |
|--------|-----------|
| **VISIT_NODE** | Entrou em um nó (incrementa contador de acessos) |
| **COMPARE_KEY** | Comparou a chave buscada com uma chave específica do nó |
| **DESCEND** | Decidiu descer para um filho específico |
| **INSERT_IN_LEAF** | Inseriu a chave em uma folha |
| **SPLIT_NODE** | Dividiu um nó cheio em dois |
| **NEW_ROOT** | Criou uma nova raiz (árvore cresceu em altura) |
| **SEARCH_FOUND** | Busca encontrou a chave |
| **SEARCH_NOT_FOUND** | Busca não encontrou a chave |

## 🔧 Estrutura do Projeto

```
SGBD/
├── src/
│   ├── core/              # Lógica das estruturas de dados
│   │   ├── btree.py       # Árvore B (completa)
│   │   ├── bplustree.py   # Árvore B+ (esqueleto)
│   │   ├── trace.py       # Sistema de rastreamento
│   │   ├── metrics.py     # Métricas de desempenho
│   │   ├── validate.py    # Validador de invariantes
│   │   └── random_ops.py  # Operações aleatórias
│   ├── ui/                # Interface gráfica
│   │   ├── widgets.py     # Janela e controles
│   │   ├── canvas_tree.py # Renderização da árvore
│   │   └── controller.py  # Controlador de reprodução
│   └── app.py             # Aplicação principal
├── tests/
│   └── test_manual_core.py
└── README.md
```

## ⚙️ Parâmetros Técnicos

### Fanout (n)

O fanout determina a capacidade da árvore:

| Fanout (n) | Max Keys | Max Children |
|------------|----------|--------------|
| 3 | 2 | 3 |
| 4 | 3 | 4 |
| 5 | 4 | 5 |
| ... | ... | ... |
| 10 | 9 | 10 |

**Regras:**
- Cada nó pode ter no máximo `n-1` chaves
- Cada nó interno pode ter no máximo `n` filhos
- Número de filhos = número de chaves + 1
- Quando um nó atinge `n-1` chaves e tenta adicionar mais uma, ocorre **split**

### Invariantes Validadas

O sistema valida automaticamente:
- ✅ Chaves ordenadas dentro de cada nó
- ✅ Sem duplicatas
- ✅ `len(keys) <= max_keys`
- ✅ Para nós internos: `len(children) = len(keys) + 1`
- ✅ Balanceamento: todas as folhas na mesma profundidade
- ✅ Intervalos corretos: chaves dos filhos respeitam limites

## 🎯 Dicas de Uso

### Para Aprender

1. **Comece com fanout pequeno (n=3):**
   - Splits acontecem mais frequentemente
   - Mais fácil de visualizar

2. **Insira chaves em ordem:**
   - Ex: 10, 20, 30, 40, 50
   - Veja como a árvore cresce

3. **Use o modo passo a passo:**
   - Entenda exatamente onde cada decisão é tomada
   - Veja como o algoritmo escolhe o caminho

4. **Compare fanouts diferentes:**
   - Insira 100 chaves aleatórias com n=3
   - Repita com n=10
   - Compare métricas (acessos e tempo)

### Para Testar Desempenho

1. **Teste com muitos dados:**
   - Insira 1000 ou 10000 chaves
   - Observe como o tempo escala

2. **Varie o intervalo:**
   - Intervalo pequeno (1-100): mais colisões
   - Intervalo grande (1-100000): menos colisões

## ✅ Etapas Concluídas

### Etapa 2: Árvore B+
- [x] Implementar estrutura B+ com encadeamento de folhas
- [x] Operações de busca e inserção
- [x] Varredura sequencial (visualizada via links)
- [x] Range queries

### Etapa 3: Remoção
- [x] Operação de remoção para Árvore B
- [x] Operação de remoção para Árvore B+
- [x] Tratamento de underflow
- [x] Redistribuição e merge de nós

## 📝 Critérios de Conclusão (Etapa 1)

✅ Criar B-Tree com fanout entre 3 e 10  
✅ Inserções sucessivas funcionam sem duplicatas  
✅ Validação de invariantes após cada operação  
✅ Tracer gera eventos "nó a nó, índice por índice"  
✅ Contador de acessos incrementa corretamente  
✅ UI permite visualização passo a passo  
✅ Métricas de tempo para operações em lote  

## 🐛 Resolução de Problemas

**Erro ao executar:**
```
ModuleNotFoundError: No module named 'core'
```
→ Certifique-se de executar `python app.py` dentro da pasta `src/`

**Tkinter não encontrado:**
```
ImportError: No module named 'tkinter'
```
→ Reinstale Python marcando a opção "tcl/tk and IDLE"

**Árvore não aparece:**
→ Tente redimensionar a janela ou inserir algumas chaves primeiro

## 📄 Licença

Projeto educacional - livre para uso acadêmico.

## 👥 Autor

Desenvolvido como material educacional para visualização de estruturas de dados.

---

**Versão:** 1.0.0 (Etapa 1)  
**Data:** Dezembro 2025
