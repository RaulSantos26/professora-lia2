# LIA2-008 — Pedagogical Engine + Adaptive Learning + Mobile

Release:

```text
0.6.3-pedagogical-adaptive-mobile-thinking-fix02
```

Migration:

```text
0009_createPedagogicalAdaptiveFoundation
```

Down revision:

```text
0008
```

O LIA2-008 é o segundo dos quatro pacotes finais da construção principal da
Professora Lia 2.0.

Roadmap:

```text
007  Multimodal Intelligence + RAG              VALIDADO
008  Pedagogical Engine + Adaptive + Mobile      ESTE PACOTE
009  Agentic Tutor + Student Experience
010  Hardening + Final Release
```

---

## 1. O que muda para o aluno

A Lia deixa de oferecer apenas leitura/RAG e passa a ter um módulo:

```text
Estudar com a Lia
```

Ações disponíveis:

```text
📖 Me ensine
💡 Explicar
📝 Resumo
🧠 Mapa mental
🃏 Flashcards
✏️ Exercícios
🎯 Quiz
```

Cada ação usa somente Evidence/Chunks dos materiais selecionados do aluno.

---

## 2. Motor pedagógico grounded

Fluxo:

```text
Material do aluno
→ Evidence
→ Chunks indexados
→ seleção de contexto
→ modelo TEXT
→ artefato pedagógico estruturado
```

Tipos persistidos:

```text
TEACH
EXPLAIN
SUMMARY
MIND_MAP
FLASHCARDS
EXERCISES
QUIZ
```

Nova tabela:

```text
lia2.pedagogical_artifact
```

O artefato guarda:

```text
Student
tipo
status
progresso
instrução
dificuldade
modelo solicitado
modelo efetivo
materiais-fonte
evidências-fonte
conteúdo estruturado
erros
timestamps
```

---

## 3. Geração assíncrona

A geração pedagógica é processada em segundo plano:

```text
POST
→ QUEUED
→ RUNNING
→ READY / FAILED
```

A UI mostra:

```text
spinner
mensagem
percentual
```

Worker:

```text
PedagogicalWorker
```

Runtime:

```text
LIA2_PEDAGOGICAL_WORKER_ENABLED=true
```

Testes:

```text
LIA2_PEDAGOGICAL_WORKER_ENABLED=false
```

Se o backend reiniciar, artefatos `RUNNING` são recolocados em `QUEUED`.

---

## 4. Me ensine / Explicar / Resumo

Saída canônica:

```text
title
intro
sections[]
keyPoints[]
```

Regras do prompt:

```text
PT-BR obrigatório
somente Evidence
sem preenchimento por conhecimento externo
termos do material preservados
limitação declarada quando a Evidence não sustenta a resposta
```

Quando o aluno informa um foco específico, o contexto é ranqueado
semanticamente antes da geração.

---

## 5. Mapa mental

O mapa não é uma string decorativa.

Estrutura:

```text
rootId
nodes[]
  nodeId
  parentId
  label
  detail
  evidenceRefs
```

A interface renderiza os nós em uma visualização hierárquica responsiva.

---

## 6. Flashcards

Estrutura:

```text
cards[]
  cardId
  front
  back
  evidenceRefs
```

No Student Web:

```text
toque
→ vira cartão
→ pergunta / resposta
```

---

## 7. Exercícios e Quiz

Questões suportadas inicialmente:

```text
MULTIPLE_CHOICE
TRUE_FALSE
```

Cada questão possui internamente:

```text
questionId
prompt
options
correctAnswer
explanation
difficulty
evidenceRefs
```

### Segurança pedagógica

Antes da entrega ao aluno:

```text
correctAnswer
explanation
```

são removidos do contrato público.

Eles só aparecem após a submissão da tentativa.

Nova tabela:

```text
lia2.learning_attempt
```

Armazena:

```text
respostas
nota
acertos
total
resultado
timestamps
```

---

## 8. Aprendizagem adaptativa

Quando a dificuldade é:

```text
AUTO
```

a Lia utiliza o domínio atual da(s) unidade(s):

```text
mastery < 35   → EASY
mastery < 72   → MEDIUM
mastery >= 72  → HARD
```

Após exercícios/quiz:

```text
>= 85%   mastery +12 / confidence +8 / revisão +7 dias
>= 70%   mastery +7  / confidence +4 / revisão +4 dias
>= 50%   mastery +3  / confidence +0 / revisão +2 dias
<  50%   mastery -4  / confidence -5 / revisão +1 dia
```

Status:

```text
LEARNING
REVIEWING
MASTERED
```

Depois da correção, a UI atualiza:

```text
StudentLearningState
Guia da Lia
WorkspaceSummary
```

Se o material não estiver ligado a uma unidade, a tentativa continua válida,
mas a Lia informa que é necessário vincular a unidade para atualizar o
domínio automaticamente.

---

## 9. IA — AUTO / FIXED / CUSTOM

A escolha de modelo deixa de ser ambígua.

### AUTO

```text
A Lia escolhe um modelo compatível por capability.
```

Pode usar:

```text
TEXT       → Qwen
VISION     → Gemma
EMBEDDINGS → Nomic
```

### FIXED

```text
um único modelo
sem fallback silencioso
```

Para análise completa, o modelo precisa cobrir as capabilities necessárias.

Exemplo:

```text
Qwen TEXT/THINKING
+
foto
→ FIXED rejeitado antes do processamento
```

porque faltam:

```text
VISION
EMBEDDINGS
```

Erro:

```text
AI_FIXED_MODEL_CAPABILITY_MISMATCH
```

### CUSTOM

Configuração independente:

```text
Texto       [Qwen / Auto]
Vision      [Gemma / Auto]
Embeddings  [Nomic / Auto]
```

Cada modelo selecionado é validado contra a capability correspondente.

---

## 10. RAG manual sem fallback escondido

Em `Perguntar aos materiais`:

```text
modelo manual
→ estrito
→ não troca silenciosamente
```

No modo automático e com um único material:

```text
RAG
→ respeita a configuração TEXT persistida daquele material
```

---

## 11. Vision em português

O prompt de Vision agora exige:

```text
summary
description
title
```

em português brasileiro.

Texto literalmente presente na imagem pode manter o idioma original.

---

## 12. OCR melhorado para fotos de apostila

Pré-processamento:

```text
grayscale
→ autocontrast
→ upscale 1.5x quando necessário
→ Tesseract por+eng
```

A finalidade é reduzir o ruído observado nas fotos reais de apostila.

---

## 13. Mobile-first

O Student Web passa a possuir uma fundação mobile/tablet real.

Dispositivos-alvo:

```text
celular
tablet
desktop
```

Princípios:

```text
touch-first
sem hover obrigatório
sem scroll horizontal
botões >= 44px
safe areas
portrait
landscape
layout de uma coluna em telas pequenas
```

---

## 14. Tirar foto ou escolher arquivo

No celular:

```text
[ 📷 Tirar foto ]
[ 🖼️ Escolher foto ou arquivo ]
```

`Tirar foto` utiliza:

```html
<input
  type="file"
  accept="image/*"
  capture="environment"
/>
```

O browser/dispositivo decide a experiência nativa de câmera.

A foto não é enviada automaticamente.

Primeiro existe:

```text
preview
tamanho
origem
Refazer foto
Remover
```

Depois:

```text
Enviar e analisar
```

---

## 15. Várias fotos da apostila

O aluno pode:

```text
tirar foto
tirar outra foto
selecionar várias
ordenar
remover
refazer
```

No frontend:

```text
Subir
Descer
```

No backend, um lote de várias imagens recebe:

```text
sourceGroupId
sourceSequence
```

Exemplo:

```text
grupo A
1 → página 1
2 → página 2
3 → página 3
4 → página 4
```

A ordem é persistida e o Motor Pedagógico a respeita.

Quando uma foto pertencente a um grupo é selecionada no módulo Estudar,
o conjunto inteiro é selecionado automaticamente.

---

## 16. Navegação mobile

No 008:

```text
Início
Materiais
Estudar
Progresso
```

O botão `Lia` não foi criado artificialmente neste pacote.

O Tutor conversacional real entra no:

```text
LIA2-009
```

e então ganhará sua própria navegação.

---

## 17. Guia da Lia

O Guia passa de 9 para 10 etapas.

Nova etapa real:

```text
Estudar com a Lia
```

Sequência principal:

```text
...
Materiais
→ Estudar com a Lia
→ Objetivo
→ Escopo
→ Sessão
→ Progresso
```

O Guia considera a etapa concluída quando existe um artefato pedagógico
`READY`.

---

## 18. WorkspaceSummary.v2

Para manter Guia e navegação consistentes:

```text
WorkspaceSummary.v2
```

inclui:

```text
pedagogicalArtifactCount
```

A navegação não depende apenas de contagem local do frontend.

---

## 19. Exclusão permanente e derivados pedagógicos

Ao excluir definitivamente um Material:

```text
LearningAttempt derivados
→ PedagogicalArtifact derivados
→ MaterialProcessingJob
→ Document graph
→ MaterialFile
→ Material
→ arquivos físicos
```

Artefatos `ARCHIVED` também são removidos.

Se existir geração pedagógica:

```text
QUEUED / RUNNING
```

a exclusão é bloqueada com:

```text
PEDAGOGICAL_PROCESSING_ACTIVE
```

---

## 20. Control Center

`ContentMetrics.v3` acrescenta:

```text
pedagogicalArtifacts
pedagogicalJobsActive
pedagogicalJobsFailed
learningAttempts
```

O painel passa a observar também o motor pedagógico.

---

## 21. Migration 0009

Primeiro bootstrap esperado:

```text
Running upgrade 0008 -> 0009
```

Não executar a migration manualmente fora do bootstrap.

---

## 22. Gate pré-bootstrap executado

Validação estática:

```text
Python files                    263
Python syntax errors              0

JSON files                       39
JSON errors                       0

TypeScript files                 49
Vue files                        37
TS/Vue script syntax errors       0

runtime core imports              PASS
files > 1000 lines                0
```

Testes locais executáveis no host:

```text
Backend                          67 passed
Control API                       6 passed
OpsAgent                           2 passed
```

O teste que importa a aplicação FastAPI inteira não foi executado no host
porque o ambiente externo ao container não possui `psycopg`.

O bootstrap Docker é o gate definitivo e executará a suíte completa dentro da
imagem que possui as dependências do projeto.

---

## 23. Jornada funcional consolidada pós-bootstrap

Não validar tela por tela.

Executar uma jornada grande:

### Materiais / mobile

1. abrir em viewport de celular;
2. `Tirar foto`;
3. conferir preview;
4. `Refazer foto`;
5. tirar outras fotos;
6. ordenar as páginas;
7. `Enviar e analisar`;
8. acompanhar percentual;
9. F5 e confirmar continuidade;
10. conferir sequência persistida.

### IA

11. conferir AUTO;
12. tentar FIXED com Qwen em foto e confirmar bloqueio por capability;
13. configurar CUSTOM:
    - TEXT Qwen
    - VISION Gemma
    - EMBEDDINGS Nomic;
14. analisar/reanalisar;
15. conferir modelos efetivos.

### Pedagogia

16. abrir Estudar;
17. criar Me ensine;
18. criar Explicação;
19. criar Resumo;
20. criar Mapa mental;
21. criar Flashcards;
22. criar Exercícios;
23. responder exercícios;
24. conferir nota/correção;
25. criar Quiz;
26. conferir mudança no Progresso;
27. conferir Guia da Lia;
28. F5 durante geração pedagógica.

### Responsividade

29. celular portrait;
30. celular landscape;
31. tablet;
32. desktop;
33. sem scroll horizontal;
34. sem botão cortado;
35. teclado virtual sem esconder ação principal.

### Operação

36. abrir Control Center;
37. conferir artefatos/jobs/tentativas.

---

## 24. Estado antes do deploy

```text
LIA2-008
STATUS: READY_FOR_DEPLOY
```

Aprovação final exige:

```text
bootstrap
+
migration 0008 → 0009
+
build Vue real
+
jornada funcional consolidada
```

---

# 25. Correção pré-instalação — Thinking nativo do Ollama

Esta versão do LIA2-008 substitui o ZIP 0.6.0 anterior **antes de qualquer
implantação**.

Release correta para instalar:

```text
0.6.3-pedagogical-adaptive-mobile-thinking-fix02
```

A migration continua:

```text
0009_createPedagogicalAdaptiveFoundation
```

Não existe migration 0010 porque o 008 anterior ainda não foi implantado.

## Política

```text
AUTO
ON
OFF
```

### AUTO — padrão

```text
modelo efetivo declara THINKING
→ think=true

modelo não declara THINKING
→ think=false
```

Portanto Qwen, Gemma e qualquer outro modelo registrado com a capability
`THINKING` podem usar raciocínio sem regra de execução presa ao nome do
modelo.

### ON — estrito

```text
THINKING é obrigatório
```

O Capability Router exige a capability. Se o modelo manual/fixo não a
possuir:

```text
AI_MODEL_THINKING_UNAVAILABLE
ou
AI_*_CAPABILITY_MISMATCH
```

Não ocorre degradação silenciosa para um modelo sem raciocínio.

### OFF

A requisição Ollama recebe explicitamente:

```json
"think": false
```

## Onde Thinking é usado

```text
Vision
RAG / Perguntar aos materiais
Me ensine
Explicar
Resumo
Mapa mental
Flashcards
Exercícios
Quiz
```

Não se aplica a:

```text
OCR
Embeddings
```

## Privacidade do raciocínio

O Ollama pode devolver separadamente:

```text
message.thinking
message.content
```

A Lia usa apenas:

```text
message.content
```

O `message.thinking`:

```text
não entra no contrato do aluno
não é mostrado na tela
não é persistido como conteúdo
```

Persistimos apenas auditoria segura:

```text
thinkingMode
effectiveThinkingEnabled
```

No Vision:

```text
visionMeta.thinkingEnabled
```

## Transparência na interface

Material:

```text
Raciocínio / Thinking
- Automático
- Sempre usar
- Desativado
```

RAG:

```text
Thinking: ATIVADO / DESATIVADO
```

Artefato pedagógico:

```text
Modelo: <modelo efetivo>
Thinking: ATIVADO / DESATIVADO
```

Vision:

```text
<modelo>
Thinking: ON / OFF
```

Assim o aluno/administrador consegue distinguir:

```text
modelo escolhido
modelo efetivo
raciocínio configurado
raciocínio efetivamente usado
```

## Gemma 4

O Model Registry preserva a capability informada pelo provedor.

Para respostas de `/api/show` que ainda não tragam `THINKING` explicitamente,
a família `gemma4` é enriquecida com `THINKING`, de acordo com a capability
oficial da família no Ollama.

## Testes adicionados

```text
payload think=true
payload think=false
thinking trace não exposto
AUTO em Qwen THINKING
AUTO em Gemma THINKING
AUTO em modelo sem THINKING
ON estrito
OFF
Router VISION + THINKING
Registry Gemma4
FIXED/CUSTOM + THINKING
UI de Material
UI de RAG
UI do Motor Pedagógico
auditoria Vision sem chain-of-thought
```

## Gate pré-bootstrap desta versão

```text
Backend amplo        67 passed
Control API           6 passed
OpsAgent               2 passed

Python syntax          PASS
JSON                   PASS
TypeScript/Vue         PASS
Runtime imports        PASS
files >1000             0
```

O bootstrap no homeserver continua sendo o gate definitivo.

---

# 26. LIA2-008 FIX01 — correção da fronteira de testes Docker

Release:

```text
0.6.3-pedagogical-adaptive-mobile-thinking-fix02
```

A migration permanece:

```text
0009_createPedagogicalAdaptiveFoundation
```

## Falha encontrada no primeiro bootstrap

A suíte `pytest` do container `lia2-backend` incluía quatro verificações que
liam arquivos do frontend diretamente:

```text
materialUploadCard.vue
mobileStudentNavigation.vue
pedagogicalWorkspacePanel.vue
materialWorkspacePanel.vue
```

No repositório completo esses arquivos existem em:

```text
apps/studentWeb/src/...
```

Porém a imagem de teste do backend copia apenas:

```text
apps/backend/app
apps/backend/tests
database
```

Dentro desse container, o caminho calculado pelos testes se tornava:

```text
/studentWeb/src/...
```

e resultava em:

```text
FileNotFoundError
```

Essa falha era de **posicionamento do teste**, não de runtime do backend,
Thinking, banco ou migration.

O bootstrap parava durante:

```text
Executando testes antes da subida
```

e portanto a migration 0009 ainda não era executada.

## Correção arquitetural

Validações de frontend foram removidas da suíte unitária/integrada do backend.

Foi criado:

```text
scripts/validateStudentWebArchitecture.py
```

Esse validador roda no nível do repositório, antes dos testes Docker, onde
existem simultaneamente:

```text
apps/backend
apps/studentWeb
```

Ele valida:

```text
câmera mobile
file picker
preview/refazer
ordenação de fotos
navegação mobile
controles de Thinking
resultado Thinking
fronteira de testes backend/frontend
```

Também existe um guardrail:

> nenhum teste em `apps/backend/tests` pode voltar a depender de arquivos
> físicos do Student Web.

## Sequência do bootstrap após FIX01

```text
pré-requisitos
→ validação arquitetural Student Web no repositório
→ build backend/control/ops
→ pytest backend
→ pytest control
→ pytest ops
→ migration 0009
→ build/subida completa
```

## Gate pré-bootstrap FIX01

```text
Student Web architecture       PASS
backend tests referencing UI      0
Backend host suite             63 passed
Control API                     6 passed
OpsAgent                         2 passed
Python syntax                    PASS
JSON                             PASS
files >1000                       0
```

No container do backend, a expectativa é:

```text
64 passed
```

pois o teste de health que depende da aplicação completa também roda na
imagem Docker com as dependências do backend.

---

# 27. LIA2-008 FIX02 — Vue production build + migration gate

Release:

```text
0.6.3-pedagogical-adaptive-mobile-thinking-fix02
```

Migration vigente:

```text
0009_createPedagogicalAdaptiveFoundation
```

Não existe migration nova.

## Falha encontrada

O bootstrap FIX01 passou por:

```text
Student Web architecture       PASS
backend pytest                 64 passed
Control API                     6 passed
OpsAgent                         2 passed
migration 0008 -> 0009         PASS
```

e falhou no build de produção do Student Web:

```text
[plugin vite:vue] materialUploadCard.vue
TypeError: Cannot read properties of undefined (reading 'type')
```

## Causa

Depois da inclusão do seletor:

```text
Raciocínio / Thinking
```

a árvore Vue ficou semanticamente equivalente a:

```vue
<p v-if="aiMode === 'AUTO'">...</p>

<label>Thinking...</label>
<p>...</p>

<template v-else-if="aiMode === 'FIXED'">
```

Em Vue, `v-else-if` precisa ser irmão imediatamente posterior a um
`v-if`/`v-else-if`.

A presença dos elementos de Thinking entre os dois tornou a cadeia inválida
para o compilador real do Vue.

O transpile isolado de TypeScript não detecta esse tipo de erro porque ele
não executa o compilador do template Vue.

## Correção do template

O formulário passa a usar condições independentes:

```vue
<p v-if="aiMode === 'AUTO'">...</p>

<label>Thinking...</label>

<template v-if="aiMode === 'FIXED'">
  ...
</template>

<div v-if="aiMode === 'CUSTOM'">
  ...
</div>
```

O editor persistido de preferências também foi corrigido para não depender
de uma cadeia `v-else` ambígua.

## Hardening do bootstrap

Antes do FIX02:

```text
backend tests
→ migration
→ build frontend
```

Isso permitiu que uma migration fosse aplicada antes de uma falha de build
Vue.

A partir do FIX02:

```text
repository architecture validation
→ backend/control/ops build
→ backend/control/ops tests
→ Student Web production build
→ Control Center production build
→ migration
→ full build/up
```

Portanto:

> nenhuma migration futura deve ser aplicada antes de o build real dos
> frontends passar.

## Estado do banco após a tentativa anterior

A migration:

```text
0008 -> 0009
```

já foi executada com sucesso no homeserver.

Ao rodar o FIX02, o Alembic deverá apenas confirmar/usar o schema já em
`0009`; não é necessário rollback.

## Gate local FIX02

```text
Student Web architecture       PASS
Backend host suite             63 passed
Control API                     6 passed
OpsAgent                         2 passed

Python syntax                   PASS
JSON                            PASS
TypeScript script syntax        PASS
Vue conditional adjacency       PASS
files >1000                      0
```

O gate definitivo continua sendo o build Docker no homeserver, que agora
ocorre antes da migration.
