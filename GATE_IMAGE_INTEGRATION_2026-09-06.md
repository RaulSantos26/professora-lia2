# Gate: integracao Lia / Z-Image — 2026-09-06

## Escopo

Mantidos Qwen 27B, Tongyi-MAI/Z-Image-Turbo, offload sequencial, dimensoes e passos. Sem migracao, exclusao de materiais ou mudanca estrutural do banco.

- ImageBriefService prepara cena concreta a partir do pedido, ultimas seis mensagens da mesma conversa, materia/licao e evidencias, usando o modelo efetivo do run. Valida pertencimento de conversa/run/aluno e contrato estruturado.
- A cena e enviada separadamente da explicacao em portugues. O briefing persistido evita nova chamada de planejamento em retomadas.
- Explicacao real aparece durante a geracao e permanece disponivel em caso de falha. Nao e mais substituida pelo pedido generico.
- NO_TEXT permanece padrao. IN_SCENE_MARKS admite pequenas marcas interiores quando indispensaveis ao assunto; nao autoriza titulos ou legendas geradas pelo modelo de imagem.
- Worker persiste progresso durante polling. Reabrir conversa com imagem pendente retoma atualizacao automatica, restrita aos IDs dessa conversa.

## Gates executados

- Backend: 103 testes aprovados (6 avisos preexistentes).
- Politica OCR: 4 testes aprovados no runtime do servico de imagem.
- Student Web: TypeScript, 14 testes e build aprovados. Aviso de bundle maior que 500 kB permanece.
- Planejamento real no Qwen, sem escrita no banco: pedido generico em Historia / Escrita virou cena de tablete de argila e estilete, com explicacao separada.
- Reprocessado somente job anteriormente falho 9197a7bb-dd9c-43ff-99a1-39ae29aa6edd. Resultado READY, asset disponivel, sem erro de qualidade.
- Navegador contra app implantado: explicacao visivel, imagem ampliada em desktop 1280x900 e celular 390x844, sem pageerrors. Capturas inspecionadas: cena coerente, sem titulos falsos embutidos; explicacao legivel fora do bitmap.
- Primeira sessao antiga de navegador expirou sem atualizar imagem: identificada ausencia de polling ao abrir chat concluido. Corrigido e coberto por dois testes (retomada e isolamento); novo gate de navegador aprovado.
- Backend ONLINE; backend, imagem e frontend running=true, restart=0, oom=false. Servico de imagem READY / IDLE, fila vazia apos teste.

## Limites e riscos

OCR e tolerancia espacial sao heuristicas, nao auditoria semantica infalivel. As marcas na argila sao ilustrativas, nao uma transcricao historica. O planejamento adiciona uma chamada ao modelo ja instalado. Primeiro uso apos reinicio teve carregamento/offload demorado; nao foi prometida latencia fixa. O fallback geometrico existente nao foi redesenhado nem validado como solucao geral. Nao ha garantia de qualidade conceitual para todos os assuntos; novos pedidos ainda exigem observacao pedagógica.

## Implantacao e rollback

Recriados somente lia2-backend, lia2-image-service e lia2-student-web. Baseline anterior: 0d0ef8b. Para rollback operacional, usar checkout/worktree separado desse commit, reconstruir os tres servicos e recria-los preservando volumes/configuracao; nao usar reset --hard no checkout de trabalho nem remover volumes. Sem down -v. Jobs e material existentes devem ser preservados; a imagem reprocessada continua no mesmo registro.

Publicacao limitada a branch codex/lia2-navegacao-verificada-20260905. Nao promover automaticamente para main.
