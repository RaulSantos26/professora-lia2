# LIA 2.0 — contexto, captura e mapas

Base: aa36cf8, branch codex/lia2-navegacao-verificada-20260905. Projeto efetivo Linux /mnt/hd_nas/Projetos/professora-lia2. Não envolve LIA 1.0.

## Diagnóstico medido

- Runner Qwen 27B estava em 8192 tokens; chamada real excedia com 12140.
- Canary com num_ctx=24576 recebeu 12139 tokens sem HTTP400. O canary de64 tokens não foi considerado resposta completa.
- RTX5060Ti16GB: após canary ~14761MiB usados,1088MiB livres; swap não aumentou. Janela declarada262144 não foi adotada.
- Geração completa encontrou também timeout360s a ~7.45tokens/s. Tarefas pedagógicas longas agora têm prazo central proporcional à reserva, máximo externalizado1800s, sem desligar Thinking.
- OCR de páginas legíveis fora extraído invertido. Auditoria em cópias temporárias encontrou21 páginas com texto/confiança>93% e uma sem texto. Confiança OCR não equivale a revisão humana de cada palavra.

## Implementação

- ContextBudgetService central:24576 contexto,6144 saída,8192 total com Thinking,1536 margem; schema e imagem entram no orçamento. Estimativa conservadora UTF8, não tokenizer exato.
- OllamaClient controla num_ctx/num_predict, recusa excesso antes da rede, distingue OLLAMA_CONTEXT_EXCEEDED e saída truncada; logs de contagens sem prompt integral.
- Tarefas globais usam sínteses hierárquicas com referências globais e aviso de cobertura. Perguntas específicas EXPLAIN mantêm busca relevante. Intermediários ficam em memória: falha/reinício requer refazer lotes, sem checkpoint persistente neste pacote.
- MIND_MAP pelo tutor e Estudar compartilha contrato canônico, português em SVG/HTML determinístico, exportação PNG/SVG, tela cheia, leitura acessível. Z-Image gera apenas figuras por ramo, independentes do texto; falha de figura não impede ler o mapa.
- OCR compara confiança antes de girar. RAG usa última versão, evidência ativa e escopo aluno/contexto/matéria/lição; revisão de uma página não exclui outras páginas. Blocos superados permanecem no banco e não aparecem como texto atual.
- scripts/repairOcrEvidence.py: simulação por padrão; revisão exige escopo/qualidade e preserva originais, com manifesto e modo rollback.
- Modelos, container Ollama, banco e migrations preservados; schema0014.

## Evidências de verificação já concluídas

- Backend136 testes PASS; frontend29 testes/typecheck/build PASS; política de imagem4 testes PASS.
- Navegador candidato: mapa legado, tela cheia/Escape, PNG e leitura390px sem overflow/erro JS PASS.
- SUMMARY real da matéria extensa:67 segmentos processados,5 lotes, consolidação final JSON válida em português; níveis ANSI/SPARC, modelos e segurança cobertos. A síntese não promete reproduzir cada detalhe.
- Reparação OCR: dry-run21 páginas PASS, sem escrita na simulação.
- Não houve repetição de toda suíte após solicitação do usuário para economizar créditos.

## Rollback

Imagens reconstruídas do commit aa36cf8 disponíveis com tag rollback-aa36cf8 para backend, student-web e image-service. Nenhuma restauração de banco é necessária para código. Reparação de evidências é reversível usando manifesto local: arquivar evidências novas e reativar antigas, sem excluir registros.

## Limites de aceite

A checagem pós-publicação deve confirmar saúde, contexto explícito, fonte revisada ativa e isolamento. Geração integral de TEACH, todas as figuras Z-Image e mapa novo da pós-graduação ainda não foram aprovados visualmente; não confundir testes unitários/build com esse aceite. Materiais muito grandes podem levar vários minutos; não foi feita medição de300 páginas. Metadados de release continuam os existentes, com commit/fingerprints como identificação do pacote.

## Publicação realizada

Em07/09/2026 foram recriados somente backend, student-web e image-service. Gate pós-publicação PASS: backend ONLINE, frontend HTTP200, política24576, schema0014,21 páginas revisadas/34 novos chunks indexados,80 chunks ativos no material (incluindo evidências visuais já existentes),21 evidências OCR originais preservadas como SUPERSEDED. Consulta cruzada de outro aluno retornou zero resultados. Manifesto da revisão permanece no servidor em /tmp/lia2-browser-gate-qq4yMJ/martaOcrRepairManifest.json; os dados originais continuam no banco.
