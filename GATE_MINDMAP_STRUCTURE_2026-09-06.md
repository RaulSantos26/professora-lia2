# Mapas mentais: pacote estrutural

Baseline de rollback: b69fabb. Sem migracao, exclusao de registros ou alteracao de modelos.

## Entregue

- Compositor SVG compartilhado por Estudar e recursos visuais do chat, adaptando o contrato nodes/rootId existente.
- Blocos conectados, altura calculada conforme texto, cores por ordem estrutural, sem palavras-chave de disciplinas/temas no renderer.
- Conteudo completo acessivel em HTML; SVG escapado, sem HTML ou codigo do LLM.
- Dialogo nativo com Escape, zoom e exportacao SVG/PNG local. PNG ate 2400 px de largura, com limite de altura de canvas para conteudos legados extensos.
- Orientacao do Qwen para ramos concisos e icone semantico opcional. Nao ha novos modelos nem dependencia de GPU para diagramacao.
- Imagens antigas associadas preservadas em area recolhida, explicitamente diferenciadas do mapa atualizado.

## Gates

- 103 testes backend, 14 regressao frontend, 6 novos do compositor; typecheck e build aprovados.
- Novo teste incorporado ao Dockerfile do Student Web.
- Navegador isolado com API somente leitura: mapa salvo de Geografia/Recursos naturais, abertura e fechamento via Escape, download PNG, leitura completa mobile e ausencia de overflow horizontal/pageerrors.
- Captura desktop inspecionada: texto e conexoes legiveis, sem sobreposicao nos blocos observados. Documentos extensos exigem rolagem, nao encolhimento ilimitado.
- Implantacao limitada a backend e student-web; backend ONLINE. Gate repetido com sucesso no app efetivo apos inicializacao, com espera explicita pelo historico assincrono. Captura mobile inspecionada com conteudo legivel e completo.

## Limites: nao confundir este pacote com a visao completa

Este e o pipeline estrutural recomendado como MVP no documento do usuario. Nao implementa ainda ilustracoes geradas por ramo, cache semantico de assets, multiplos templates, nem novo contrato canônico LIA_MINDMAP_V1 com auditoria pedagogica completa. Os testes de temas diferentes verificam renderer generico, nao constituem auditoria de duas geracoes reais no Qwen. O mapa salvo usado no gate preserva o conteudo antigo: nao foi reescrito nem validado factualmente.

## Rollback

Reverter este commit por Git revert (preservando outras alteracoes) e reconstruir/recriar somente backend e student-web. Nao remover volumes, nao usar down -v ou reset --hard. Fontes anteriores em b69fabb. Branch de entrega codex/lia2-navegacao-verificada-20260905, sem promover para main automaticamente.
