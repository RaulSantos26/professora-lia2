# LIA2-009 FIX01 — Docker test path boundary

Release:

```text
0.7.1-agentic-tutor-visual-learning-fix01
```

Migration vigente:

```text
0010_createAgenticTutorVisualFoundation
```

Down revision:

```text
0009
```

Não existe migration nova.

## Falha encontrada no primeiro bootstrap do 009

O backend Docker foi construído corretamente e a suíte chegou a:

```text
1 failed, 80 passed
```

Falha:

```text
testAgenticTutorArchitecture.py::testAgentDoesNotPersistReasoningTrace
IndexError: 1
```

Causa:

```python
ROOT = Path(__file__).parents[1]
ROOT.parents[1]
```

No repositório, `ROOT` possui profundidade suficiente e o teste passava.

Dentro da imagem Docker:

```text
/app/tests/testAgenticTutorArchitecture.py
```

logo:

```text
ROOT = /app
ROOT.parents[0] = /
ROOT.parents[1] = inexistente
```

O erro era do teste, não do Agent Harness, Visual Engine, Thinking ou migration.

## Correção

O teste agora procura a migration em dois layouts suportados:

```text
/app/database/migrations/versions/0010...
```

e:

```text
<repo>/database/migrations/versions/0010...
```

sem depender da profundidade do diretório pai.

## Novo guardrail

`validateStudentWebArchitecture.py` também protege a fronteira Docker do backend.

Ele falha antes do build se algum teste em:

```text
apps/backend/tests
```

voltar a usar:

```text
ROOT.parents[...]
```

para escapar do root do backend.

## Simulação Docker exata

Antes de empacotar o FIX01 foi criada a mesma topologia usada pela imagem:

```text
/app
├── app
├── tests
└── database
```

A suíte de backend foi executada a partir de `/app`.

Resultado:

```text
80 passed
```

Também foram repetidos:

```text
Backend host suite              80 passed
Control API                      6 passed
OpsAgent                          2 passed
Repository architecture          PASS
TypeScript                       54
Vue                              44
TS/Vue script errors              0
files >1000                       0
```

## Estado do banco

O bootstrap que falhou parou durante:

```text
lia2-backend pytest -q
```

e não chegou a:

```text
Validando builds de produção...
Aplicando migrations...
```

Portanto:

```text
schema atual esperado = 0009
migration pendente    = 0010
```

Não faça rollback e não crie migration 0011.

---

# LIA2-009 — Agentic Tutor + Student Experience + Visual Learning Engine

Release:

```text
0.7.0-agentic-tutor-visual-learning
```

Migration:

```text
0010_createAgenticTutorVisualFoundation
```

Down revision:

```text
0009
```

Status antes do deploy:

```text
READY_FOR_DEPLOY
```

O 009 transforma a Lia de um conjunto de módulos pedagógicos em uma tutora
conversacional capaz de orquestrar evidências, progresso, atividades e
visualizações, preservando contratos, isolamento por aluno/contexto e
rastreabilidade.

---

## 1. O que entra no 009

```text
Tutor conversacional real
Agent Harness
Planner
Skill Registry
Tools
Tool Calls auditáveis
Guardrails
Memória operacional
Threads persistidas por contexto
Visual Learning Engine
Mapa mental SVG interativo
Diagrama SVG
Gráfico Canvas
Animação Canvas
Cena 3D Three.js
Python/NetworkX para grafos/layout
Control Center agentic metrics
```

---

## 2. Jornada do Tutor

Fluxo canônico:

```text
Student
→ Lia Thread
→ User Message
→ Agent Run
→ Capability Router
→ Planner
→ Guardrails
→ Skill
→ Tool Calls
→ Evidence / Progress / Artifact / Visual
→ Grounded Response
→ Assistant Message
→ Operational Memory
```

O frontend continua sem conhecer a implementação interna do agente.

---

## 3. Persistência por aluno e contexto

Nova estrutura:

```text
Student
└── AgentThread
    ├── StudentLearningContext
    ├── StudentSubject
    └── StudentLearningUnit
```

Uma conversa pode estar ligada a:

```text
Aluno
→ ENEM 2026
→ Biologia
→ Tecidos
```

Ao voltar à mesma combinação de aluno/contexto/matéria/unidade, o Student Web
procura a thread existente e a reabre.

Outra unidade ou outro aluno recebe outra thread.

A criação de thread valida propriedade e hierarquia:

```text
contexto pertence ao aluno
matéria pertence ao contexto/aluno
unidade pertence à matéria/aluno
```

---

## 4. Tabelas novas

### lia2.agent_thread

Persiste conversa e memória operacional.

### lia2.agent_message

Persiste:

```text
USER / ASSISTANT
content
citations
visualTaskIds
actions
timestamps
```

### lia2.agent_run

Execução assíncrona:

```text
QUEUED
RUNNING
READY
FAILED
CANCELLED
```

com:

```text
stage
progressPercent
modelo solicitado/efetivo
Thinking solicitado/efetivo
planJson
erros
timestamps
```

### lia2.agent_tool_call

Auditoria de cada ferramenta:

```text
toolName
STARTED / COMPLETED / FAILED
request
response
error
timestamps
```

### lia2.visual_task

Persistência dos recursos visuais:

```text
MIND_MAP
DIAGRAM
CHART
ANIMATION_2D
SCENE_3D
```

com:

```text
renderer
specJson
evidenceJson
sourceMaterialIds
modelo efetivo
Thinking efetivo
```

---

## 5. Agent Harness

Arquivo principal:

```text
apps/backend/app/agents/tutorAgentHarness.py
```

Responsabilidade:

```text
modelo
→ planning
→ guardrails
→ skills
→ tools
→ grounded final response
→ memory
```

O Harness não deixa o modelo acessar diretamente banco, arquivos ou UI.

---

## 6. Planner

`TutorPlannerService` produz estrutura controlada:

```text
intent
tools[]
reason
visualType
pedagogicalType
```

Intenções:

```text
GREETING
ANSWER
TEACH
EXPLAIN
SUMMARY
MIND_MAP
DIAGRAM
CHART
ANIMATION_2D
SCENE_3D
FLASHCARDS
EXERCISES
QUIZ
PROGRESS
```

---

## 7. Skills

`TutorSkillRegistry` separa intenção de implementação:

```text
conversationSkill
groundedAnswerSkill
pedagogicalSkill
visualLearningSkill
progressSkill
```

Modelos não são agentes e Skills não dependem de um nome específico de modelo.

---

## 8. Tools

Tools permitidas no 009:

```text
EVIDENCE_SEARCH
PROGRESS_READ
PEDAGOGICAL_CREATE
VISUAL_CREATE
```

### EVIDENCE_SEARCH

Consulta somente chunks do Student e filtros do contexto/thread.

### PROGRESS_READ

Consulta:

```text
status
mastery
confidence
studyCount
lastStudiedAt
nextReviewAt
```

### PEDAGOGICAL_CREATE

Cria, usando o motor do 008:

```text
Me ensine
Explicar
Resumo
Flashcards
Exercícios
Quiz
```

### VISUAL_CREATE

Cria uma `VisualTask`.

---

## 9. Tool Calls auditáveis

`AgentToolExecutor` grava:

```text
STARTED
→ COMPLETED / FAILED
```

O request e response são persistidos em formato controlado.

Contextos textuais grandes são truncados antes da auditoria.

---

## 10. Guardrails

`TutorAgentGuardrails`:

```text
máximo de 4 tool calls por run
somente tools registradas
conteúdo pedagógico exige Evidence
PROGRESS usa dados operacionais de progresso
GREETING não exige Evidence
```

Não existe ferramenta genérica arbitrária.

---

## 11. Memória operacional

A memória da thread guarda somente informações úteis para continuidade:

```text
lastIntent
lastSkill
recentTopics
recentMaterialIds
```

Não guarda chain-of-thought.

O objetivo é lembrar:

```text
o que está sendo estudado
qual foi a última intenção
quais materiais estavam em uso
```

sem transformar raciocínio interno do modelo em dado de produto.

---

## 12. Thinking

O 009 preserva a política do 008:

```text
AUTO
ON
OFF
```

Aplica Thinking a:

```text
Planner
Resposta final
Visual generation
Pedagogical generation
```

quando a capability/modelo permitir.

Não se aplica a:

```text
OCR
Embeddings
```

A interface mostra modelo efetivo e Thinking efetivo, sem mostrar o conteúdo
do raciocínio interno.

---

## 13. Visual Learning Engine

Contrato:

```text
VisualTask.v1
```

Tipos e renderers:

```text
MIND_MAP       → SVG
DIAGRAM        → SVG
CHART          → Canvas
ANIMATION_2D   → Canvas
SCENE_3D       → Three.js
```

A escolha tecnológica depende do valor pedagógico do formato.

Three.js não é utilizado em mapas mentais apenas para produzir um efeito 3D.

---

## 14. Mapa mental SVG interativo

O mapa mental do módulo `Estudar` também deixa de usar os cards HTML/CSS do
008 e passa a utilizar o renderer SVG interativo.

Capacidades:

```text
conexões reais
zoom
pan
centralizar
selecionar nó
ver detalhes
touch/pointer
```

O contrato semântico continua:

```text
rootId
nodes[]
  nodeId
  parentId
  label
  detail
```

---

## 15. Python + NetworkX

O backend inclui:

```text
networkx==3.6.1
```

A Skill:

```text
VisualLayoutSkill
```

usa grafos para organizar mapa mental/diagrama antes da renderização.

O LLM define:

```text
conceitos
relações
conteúdo
```

A Skill Python define:

```text
níveis
ordem de grafo
geometria determinística
```

Isso evita depender do LLM para adivinhar coordenadas/pixels.

---

## 16. Diagrama SVG

`DiagramSvgRenderer` apresenta:

```text
nodes
edges
setas
seleção de conceito
detalhes
```

O layout é preparado pelo backend.

---

## 17. Gráfico Canvas

`ChartCanvasRenderer` suporta inicialmente:

```text
BAR
LINE
```

A Lia só deve criar gráfico quando as Evidence contiverem valores
quantitativos comparáveis.

---

## 18. Animação Canvas

`AnimationCanvasRenderer` suporta objetos:

```text
CIRCLE
RECTANGLE
```

Movimentos:

```text
STATIC
ORBIT
LINEAR
```

Controles:

```text
Pausar
Continuar
Reiniciar
```

É a fundação para exemplos como:

```text
órbitas 2D
movimentos
ciclos
processos
```

---

## 19. Three.js

O Student Web inclui:

```text
three 0.185.1
```

`ThreeSceneRenderer` suporta inicialmente:

```text
SPHERE
BOX
CYLINDER
```

e:

```text
OrbitControls
rotação
órbita
zoom
pan
touch
```

Aplicações adequadas:

```text
Sistema Solar
Terra/Lua
moléculas
formas geométricas
estruturas espaciais
```

---

## 20. Tutor no Student Web

Nova seção real:

```text
LIA_TUTOR
```

Navegação mobile:

```text
Início
Materiais
Estudar
Lia
Progresso
```

Desktop também possui card próprio `Lia`.

---

## 21. Conversa contextual

Ao abrir Lia:

```text
selected student
+
selected material/context/subject/unit
→ procura thread correspondente
→ reabre conversa anterior
```

Se não existir:

```text
cria nova thread
```

Portanto a continuidade da mesma matéria/aluno fica persistida.

---

## 22. Recursos criados pela conversa

Uma resposta da Lia pode possuir:

```text
citations
visualTaskIds
actions
```

VisualTask aparece inline na conversa.

Uma atividade pedagógica criada pela Lia pode ser aberta em:

```text
Estudar
```

sem duplicar o motor pedagógico.

---

## 23. Guide da Lia

O Guia passa de 10 para 11 etapas.

Inclui:

```text
Materiais
→ Estudar com a Lia
→ Conversar com a Lia
→ Objetivo
...
```

`LIA_TUTOR` é considerado concluído quando existe ao menos uma mensagem
ASSISTANT persistida para o Student.

---

## 24. WorkspaceSummary.v3

Novos campos:

```text
agentThreadCount
visualTaskCount
```

---

## 25. ContentMetrics.v4

Control Center ganha:

```text
agentThreads
agentRunsActive
agentRunsFailed
agentToolCalls
visualTasks
```

---

## 26. Worker do Tutor

Runtime:

```text
LIA2_AGENT_TUTOR_WORKER_ENABLED=true
LIA2_AGENT_TUTOR_POLL_SECONDS=1.0
```

Durante testes:

```text
LIA2_AGENT_TUTOR_WORKER_ENABLED=false
```

Runs `RUNNING` são recolocados em `QUEUED` depois de restart.

---

## 27. Migration 0010

Primeiro bootstrap esperado:

```text
Running upgrade 0009 -> 0010
```

O bootstrap mantém o hardening do 008:

```text
repo architecture validation
→ backend/control/ops tests
→ production build Student Web
→ production build Control Center
→ migration
→ full build/up
```

Ou seja: build real de frontend antes da migration.

---

## 28. Gate pré-bootstrap

Executado sobre o pacote:

```text
Python files                    300
Python syntax errors              0

JSON files                       44
JSON errors                       0

Backend host suite              78 passed
Control API                       6 passed
OpsAgent                           2 passed
Core runtime imports              PASS

TypeScript                       54
Vue                              44
TS/Vue script errors              0

Student Web architecture          PASS
Vue directive structural gate     PASS
files >1000                       0
```

Maior arquivo:

```text
educationCoreView.vue             994
```

O teste de health/full FastAPI import continua reservado para a imagem Docker
porque o host desta sessão não possui psycopg.

---

## 29. Gate funcional pós-bootstrap

Executar em uma jornada grande:

### Persistência

1. abrir aluno + matéria/unidade;
2. abrir Lia;
3. conversar;
4. F5;
5. sair e voltar;
6. confirmar que a mesma thread e mensagens reaparecem.

### Grounding

7. perguntar sobre material;
8. conferir Evidence;
9. perguntar algo não sustentado e confirmar limitação.

### Agentic

10. pedir explicação;
11. pedir resumo;
12. pedir exercícios;
13. abrir atividade em Estudar;
14. perguntar progresso.

### Visual

15. pedir mapa mental interativo;
16. testar zoom/pan/nó;
17. pedir diagrama;
18. pedir gráfico em material quantitativo;
19. pedir animação 2D quando o tema suportar;
20. pedir cena 3D em tema espacial adequado.

### Resiliência

21. F5 durante AgentRun;
22. confirmar retomada;
23. testar no celular portrait;
24. testar landscape/tablet/desktop.

### Operação

25. Control Center:
    - threads
    - runs
    - failures
    - tool calls
    - visual tasks.

Somente após esta jornada:

```text
LIA2-009
STATUS: VALIDADO
```

---

## 30. Próximo pacote

Após validar o 009:

```text
LIA2-010
Hardening + Final Release
```

Foco:

```text
lifespan FastAPI
warnings/deprecations
observabilidade final
performance
recovery
segurança
testes de carga/concorrência
polimento UX
release final
```
