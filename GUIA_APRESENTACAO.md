# 🎤 GUIA DE APRESENTAÇÃO - Árvores B e B+

## ⏱️ TEMPO: 7-10 minutos

---

## 📋 ROTEIRO DETALHADO

### 0. PREPARAÇÃO (Antes da apresentação)
- [ ] Laptop carregado e funcionando
- [ ] Aplicação já aberta e testada
- [ ] Backup: Pendrive com executável
- [ ] Dividir falas entre os membros
- [ ] Cronometrar a demo (máximo 10 min)

---

### 1. INTRODUÇÃO (30 segundos)

**Membro 1:**
> "Bom dia/tarde. Somos [Nome 1] e [Nome 2], e vamos apresentar nossa implementação 
> do trabalho de Árvores B e B+. Desenvolvemos uma aplicação interativa em Python 
> com Tkinter que permite visualizar e manipular ambas as estruturas com animação 
> passo a passo de todas as operações."

---

### 2. VISÃO GERAL DA INTERFACE (1 minuto)

**Membro 2:**
> "Nossa interface possui três áreas principais:"

**[Apontar para cada área enquanto explica]**

1. **Controles à esquerda:**
   - Seleção de tipo (B-Tree / B+ Tree)
   - Fanout configurável de 3 a 10
   - Tipo de chave (numérico ou string)
   - Operações manuais e aleatórias

2. **Visualização à direita:**
   - Desenho da árvore em tempo real
   - Destaque de nós e chaves durante operações

3. **Painel inferior:**
   - Métricas (acessos, tempo)
   - Controles de reprodução passo a passo

---

### 3. DEMONSTRAÇÃO: INSERÇÃO COM SPLIT (2 minutos)

**Membro 1:**

**[Configurar fanout = 3]**
> "Vou configurar o fanout para 3, o que significa max_keys = 2. 
> Isso nos permite ver splits rapidamente."

**[Inserir: 10]**
> "Primeira inserção: chave 10."

**[Usar ◀ ▶ para mostrar passos]**
> "Observem aqui os passos: VISIT_NODE, INSERT_IN_LEAF. 
> Cada passo é rastreado para visualização."

**[Inserir: 20, depois 30]**
> "Segunda inserção: 20. Terceira: 30. Agora temos 3 chaves [10, 20, 30]."

**[Inserir: 40 - CAUSARÁ SPLIT!]**
> "Ao inserir 40, a folha está cheia. Vejam o SPLIT_NODE:"
> "- A chave do meio (20) é promovida"
> "- Cria-se uma nova raiz"
> "- Duas folhas resultantes: [10] e [30, 40]"

**[Navegar com ◀ ▶]**
> "Usando os controles, podemos ver cada passo da operação."

---

### 4. DEMONSTRAÇÃO: BUSCA COM DESTAQUE (1 minuto)

**Membro 2:**

**[Buscar chave existente, ex: 30]**
> "Vou buscar a chave 30."

**[Mostrar eventos passo a passo]**
> "Vejam o caminho percorrido:"
> "1. VISIT_NODE na raiz"
> "2. COMPARE_KEY: 30 > 20, então desce à direita"  
> "3. VISIT_NODE na folha"
> "4. SEARCH_FOUND na posição correta"

> "Cada comparação é rastreada com o índice exato, cumprindo o requisito 
> 'nó a nó, índice por índice'."

---

### 5. DEMONSTRAÇÃO: OPERAÇÕES EM LOTE (1-2 minutos)

**Membro 1:**

**[Inserção Aleatória]**
> "Agora vamos popular a árvore rapidamente com inserção aleatória em lote."

**[Configurar: 50 chaves, intervalo 1-1000]**
> "Configurei 50 chaves entre 1 e 1000."

**[Clicar "Inserir Aleatório"]**
> "Ao executar, vejam:"
> "- Timer: mostra o tempo total em milissegundos"
> "- Acessos: contador de visitas a nós"

**[Apontar para métricas]**
> "Neste caso, foram X acessos em Y ms, média de Z ms por chave."

**[Remoção Aleatória]**
> "Agora vou remover 20 chaves aleatoriamente."

**[Clicar "Remover Aleatório"]**
> "IMPORTANTE: O algoritmo sorteia APENAS chaves que existem na árvore, 
> conforme requisitado. Mantemos um conjunto de chaves existentes atualizado."

---

### 6. DEMONSTRAÇÃO: REMOÇÃO COM MERGE (1-2 minutos)

**Membro 2:**

**[Preparar árvore específica ou usar a existente]**
> "Vou demonstrar remoção que causa merge."

**[Remover uma chave que causará underflow]**
> "Ao remover esta chave, o nó fica abaixo do mínimo."

**[Navegar eventos]**
> "Vejam os eventos:"
> "1. DELETE_FOUND"
> "2. DELETE_IN_LEAF"
> "3. UNDERFLOW detectado"
> "4. Tentativa de REDISTRIBUTE"
> "5. Como irmãos também estão no mínimo: MERGE"

> "O merge combina dois nós e puxa o separador do pai."

---

### 7. DEMONSTRAÇÃO: B+ TREE (1 minuto)

**Membro 1:**

**[Alternar para B+ Tree]**
> "Nossa implementação também suporta Árvore B+."

**[Confirmar mudança]**
> "As diferenças principais:"
> "- Dados apenas nas folhas"
> "- Nós internos contêm separadores"
> "- Folhas encadeadas (vejam as setas →)"

**[Inserir algumas chaves]**
> "As mesmas operações funcionam:"
> "- Inserção, busca, remoção"
> "- Animação passo a passo"
> "- Métricas"

**[Se houver tempo: range query]**
> "B+ Tree permite consultas por intervalo eficientes 
> usando o encadeamento de folhas."

---

### 8. RECURSOS TÉCNICOS (30 segundos)

**Membro 2:**

> "Destaques da implementação:"
> "✅ ~2600 linhas de código Python"
> "✅ 11 testes automatizados (100% aprovação)"
> "✅ Validação automática de invariantes após cada operação"
> "✅ Suporte a chaves numéricas e strings"
> "✅ Código documentado com docstrings"

---

### 9. CONCLUSÃO (30 segundos)

**Membro 1:**

> "Em resumo, implementamos:"
> "✅ Árvore B e B+ completas e interativas"
> "✅ Todas as operações: consulta, inclusão, exclusão"
> "✅ Modos manual e aleatório"
> "✅ Visualização passo a passo completa"
> "✅ Timer e contador de acessos"
> "✅ Fanout configurável de 3 a 10"

**Ambos:**
> "Estamos à disposição para perguntas!"

---

## 💡 DICAS PARA APRESENTAÇÃO

### Durante a Demo
1. **Fale devagar e claramente**
2. **Aponte para a tela** enquanto explica
3. **Pause após cada demonstração** (respirar)
4. **Não acelere** se houver tempo
5. **Sorria** e mostre confiança

### Se Der Problema Técnico
- **Plano B**: Pendrive com executável
- **Plano C**: Screenshots/vídeo gravado previamente
- **Mantenha calma**: "Enquanto reinicio, posso explicar..."

### Divisão de Tarefas Sugerida
- **Membro 1**: Introdução, Split, Lote, Conclusão
- **Membro 2**: Interface, Busca, Remoção, B+ Tree

---

## ❓ POSSÍVEIS PERGUNTAS E RESPOSTAS

### Técnicas

**P: Qual a complexidade da busca?**
> R: O(log_n m), onde n é o fanout e m o número de chaves. 
> Com fanout 10 e 1000 chaves, são cerca de 3 níveis apenas.

**P: Como é implementado o split na B+ Tree?**
> R: Na folha, a chave promovida é COPIADA (não removida). 
> Nas internas, a chave é MOVIDA. Essa é uma diferença chave da B-Tree.

**P: Como garante que não há duplicatas?**
> R: Antes de inserir, fazemos uma busca. Se encontrar, retorna False.
> Também validamos com `validate_btree()` após cada operação.

**P: E se tentar remover mais chaves do que existem?**
> R: O handler `handle_random_remove` verifica o tamanho de `existing_keys`.
> Se pedir mais, ajusta para o máximo disponível e avisa o usuário.

**P: Como funciona o rastreamento "índice por índice"?**
> R: Cada evento COMPARE_KEY contém `key_index` - a posição exata da chave 
> sendo comparada. Isso permite destacar visualmente cada comparação.

### Implementação

**P: Por que Tkinter?**
> R: É nativo do Python (não precisa instalar), multiplataforma, e suficiente 
> para visualização 2D. Consideramos PyQt mas optamos pela simplicidade.

**P: Quantas horas trabalharam?**
> R: Aproximadamente [X] horas divididas em 5 etapas ao longo de [Y] semanas.

**P: Qual a parte mais difícil?**
> R: Implementar o delete com todos os casos (redistribuição, merge, shrink).
> Especialmente manter as invariantes e o encadeamento na B+.

---

## 🎯 CHECKLIST PRÉ-APRESENTAÇÃO

### 1 Dia Antes
- [ ] Testar demo completa 3x
- [ ] Cronometrar (deve ser < 10 min)
- [ ] Revisar possíveis perguntas
- [ ] Preparar backup (pendrive)

### 1 Hora Antes
- [ ] Carregar laptop
- [ ] Abrir aplicação e testar
- [ ] Revisar roteiro
- [ ] Respirar fundo! 😊

### Imediatamente Antes
- [ ] Fechar outros programas
- [ ] Desativar notificações
- [ ] Aumentar brilho da tela
- [ ] Posicionar-se para apresentar

---

## 🎬 CRONOMETRAGEM ALVO

| Seção | Tempo | Acumulado |
|-------|-------|-----------|
| Introdução | 30s | 0:30 |
| Visão Geral | 1min | 1:30 |
| Split | 2min | 3:30 |
| Busca | 1min | 4:30 |
| Lote | 1-2min | 6:00 |
| Remoção/Merge | 1-2min | 7:30 |
| B+ Tree | 1min | 8:30 |
| Recursos | 30s | 9:00 |
| Conclusão | 30s | 9:30 |
| **Buffer** | 30s | **10:00** |

---

## ✨ MENSAGEM FINAL

**Vocês implementaram um projeto COMPLETO e de QUALIDADE!**

- Todas as funcionalidades requisitadas ✅
- Código bem estruturado e documentado ✅  
- Testes abrangentes ✅
- UI intuitiva ✅

**Apresentem com CONFIANÇA!**

Boa sorte! 🍀
