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

