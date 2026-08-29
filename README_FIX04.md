# LIA2-007-FIX04 — RAG Query Timeout

Release:

```text
0.5.1-multimodal-rag-fix04
```

Migration:

```text
nenhuma
```

A migration vigente continua:

```text
0008
```

## Falha comprovada

A indexação RAG terminou normalmente:

```text
POST .../index-rag HTTP/1.1" 200
```

A pergunta RAG foi interrompida pelo proxy:

```text
upstream timed out (110: Operation timed out)
while reading response header from upstream
POST .../rag/query
```

e o Student Web devolveu:

```text
HTTP 504
```

Portanto o erro não estava no retrieval nem na indexação. A requisição ficou
aberta aguardando a geração do modelo local e o Nginx atingiu seu limite de
leitura.

## Correção

Student Web nginx:

```text
proxy_connect_timeout 30s
proxy_send_timeout    420s
proxy_read_timeout    420s
```

Backend/Ollama:

```text
LIA2_OLLAMA_CHAT_TIMEOUT_SECONDS=360
LIA2_OLLAMA_EMBEDDING_TIMEOUT_SECONDS=180
```

O backend continua sendo a autoridade do timeout de execução.

Se o modelo ultrapassar o limite de chat:

```json
{
  "contractName": "Error.v1",
  "code": "OLLAMA_TIMEOUT",
  "message": "O modelo demorou mais que o limite configurado...",
  "correlationId": "..."
}
```

HTTP:

```text
504
```

Isso substitui o 504 opaco do proxy por um erro estruturado quando o limite
real do modelo for atingido.

## Por que o proxy é maior que o backend

```text
backend chat timeout = 360 s
nginx read timeout   = 420 s
```

Assim o backend possui margem de 60 segundos para encerrar a chamada e
devolver `Error.v1` antes de o proxy abandonar a conexão.

## Teste pós-bootstrap

Após instalar o FIX04:

```text
1. abrir o mesmo material já indexado
2. Perguntar aos materiais
3. escolher Qwen 3.8 27B
4. perguntar "explique melhor essa matéria..."
5. aguardar a resposta
```

Não é necessário reindexar se os chunks já estiverem `EMBEDDED`.

Se a geração levar menos de 360 segundos:

```text
RagQueryResponse.v1
```

deve aparecer normalmente.

Se ultrapassar 360 segundos:

```text
OLLAMA_TIMEOUT
```

deve aparecer com correlationId.

## Próxima arquitetura

O FIX04 mantém a pergunta RAG síncrona para corrigir o defeito sem aumentar
desnecessariamente o escopo.

No ciclo de experiência do aluno, perguntas longas poderão evoluir para job
assíncrono, preservando o mesmo contrato de Evidence/RAG.

## Gate pré-bootstrap

```text
Python syntax:       PASS
JSON:                PASS
focused pytest:      12 passed
nginx timeout:       PASS
Ollama timeout:      PASS
Error.v1 timeout:    PASS
files >1000:         0
migration 0009:      NÃO CRIADA
```
