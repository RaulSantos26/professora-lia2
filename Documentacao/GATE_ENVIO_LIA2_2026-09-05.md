# Gate de envio após arquivamento

Baseline: 858ec87, branch codex/lia2-navegacao-verificada-20260905.

## Causa confirmada

Logs mostraram DELETE 204 da conversa da lição Recursos naturais. O composable mantinha conversation=null e sendMessage retornava sem erro; o componente limpava a pergunta imediatamente ao emitir o evento, sem confirmação da API. O escopo não mudava, então o watcher não criava outra conversa.

## Correção

- Manter contexto selecionado e recriar a conversa ao enviar depois do arquivamento.
- Compartilhar preparação em andamento e ignorar respostas de escopo antigo.
- Retornar confirmação explícita da API para o formulário.
- Limpar o rascunho apenas quando recebido pelo servidor.
- Mostrar envio em andamento e falha junto ao campo; evitar aviso global antigo depois de sucesso.
- Falta de escopo deixa de ser retorno silencioso.

## Evidências

- 12 testes de regressão, TypeScript e build passaram.
- Navegador real contra candidata: conversa vazia de teste arquivada; envio seguinte recriou conversa no mesmo escopo.
- HTTP 503 simulado apenas no navegador: aviso visível e pergunta preservada.
- Tentativa seguinte real: pergunta sobre recursos naturais recebida e resposta exibida (exemplo de rios e geração de energia).
- Conversa de validação identificada como Verificação técnica · Recursos naturais, mantida no histórico. A conversa anterior do usuário não foi apagada pelo teste; a única exclusão feita pelo roteiro foi da conversa vazia criada pelo próprio gate.
- Nenhuma mudança no backend, modelo, configuração ou banco estrutural. A pergunta real e seus resultados são os únicos conteúdos de estudo adicionados pelo gate.

Rollback: reverter este commit e reconstruir somente lia2-student-web; baseline 858ec87. Não reverter nem apagar dados de estudo.
