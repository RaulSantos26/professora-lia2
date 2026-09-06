# Revisão da LIA 2.0 — navegação e qualidade pedagógica

Data da sessão: 05/09/2026 (horário local; execução atravessou a meia-noite UTC).
Repositório: `/mnt/hd_nas/Projetos/professora-lia2`, homeserver.
Baseline Git: `bd4dfcb`. Não é o projeto professora-bianca/LIA 1.0.

## Resultado executivo

A aplicação tem infraestrutura funcional, escopos explícitos e serviços separados, mas ainda não satisfaz o objetivo de material consolidado, semanticamente auditado e adequado a diferentes níveis de aprendizagem. Os testes técnicos existentes não demonstram qualidade pedagógica. A revisão não equivale a uma auditoria completa de segurança ou a testes com crianças.

Foi lido integralmente o relatório técnico de 30/08/2026. Preservados o Qwen 27B, configuração, banco, materiais, serviços e arquivos não rastreados GATE_LIA2_ESTADO_ATUAL_V1_READONLY.sh/.txt. Nenhuma migração ou exclusão de dados neste pacote.

## Estado e diferenças em relação ao relatório

- Backend FastAPI, Student Web Vue/Vite, PostgreSQL, control API/center, ops agent e image-service existem. Z-Image está separado do backend; o relatório recomendava essa separação.
- O 9B continua candidato, não autorização para substituir o 27B. A configuração principal não foi alterada.
- As chamadas de imagem são assíncronas e há ampliação. Entretanto, sucesso de processamento não prova qualidade visual.
- O relatório exige texto determinístico e gate visual. Há rejeição OCR e contingência geométrica, mas isso não garante adequação ao conceito. Não foi repetido gate GPU/coexistência neste pacote frontend.
- Existem especialistas internos, mas a revisão pedagógica implementada é básica. Não é correto anunciar auditoria semântica completa.

## Achados prioritários verificáveis

### 1. Consolidação real de conteúdo — alta prioridade

`apps/backend/app/services/pedagogicalService.py` (`_consolidateEvidenceForPresentation`) agrupa e concatena evidências na apresentação, com limite de 4.000 caracteres. `evidenceCurationService.py` prefere certos resultados Vision/OCR e usa limpeza por regex. Não há nesse fluxo comprovação de reconstrução semântica e auditoria de fidelidade de um documento único.

Próximo pacote: documento canônico versionado por aluno/contexto/matéria/lição, estrutura de conceitos e descrições visuais, proveniência por página/trecho, estados de revisão e publicação. Consumidores devem ler somente a versão aprovada, preservando transcrições e falhas para recuperação. Não apagar nem reprocessar materiais em massa sem inventário e comparação.

Aceite: nenhuma mistura de escopos; conteúdo de todas as páginas representado ou lacuna explícita; texto legível; referências resolvíveis; versão anterior recuperável. Não basta trocar nomes na interface.

### 2. Revisão pedagógica superficial — alta prioridade

`agents/specialists/pedagogicalReviewSpecialist.py` valida resposta não vazia e presença de evidências. Não verifica factualidade, português, adequação ou referências. Atividades em `services/pedagogicalService.py` não passam por esse mesmo revisor. O schema de quiz permite resposta correta sem correspondência obrigatória com as opções.

Próximo pacote: gate comum de completude, referências e coerência de questões; revisão semântica seletiva nos casos ambíguos. Falhas devem produzir mensagem recuperável, não READY enganoso. Medir latência antes de adicionar chamadas de modelo a toda pergunta.

### 3. Ilustrações não validadas conceitualmente — alta prioridade

`apps/imageService/app/imageServiceApplication.py` usa contingência geométrica semelhante para vários temas. A detecção OCR em inglês com limiar de confiança não garante ausência de pseudotexto. `services/imageGenerationService.py` ainda tem decisões baseadas em palavras-chave.

Próximo pacote: briefing do objetivo e contexto da lição, cena própria para o conceito, rótulos pt-BR compostos deterministicamente e contingência identificada. Gate visual fixo: erosão com transporte de sedimentos, relevo, eclipse, cadeia alimentar, anatomia e mapa mental estrutural. Não confundir uma imagem limpa com uma explicação correta.

### 4. Adaptação a públicos diferentes — alta prioridade

`pedagogicalGenerationService.py` e `tutorResponseService.py` não recebem perfil pedagógico explícito suficiente para leitura e acessibilidade. Dificuldade isolada e memória livre não substituem esse contrato.

Próximo pacote: perfil de etapa e autonomia de leitura, sem inferir idade; explicação progressiva, exemplo concreto, vocabulário explicado, prática com feedback e checagem de compreensão. Preservar explicações completas e permitir aprofundamento para jovens e adultos.

### 5. Cobertura de evidências — alta prioridade

`pedagogicalContextService.py` limita evidências e caracteres; pode favorecer itens iniciais e selecionar apenas um grupo de embeddings compatíveis. Os IDs selecionados não equivalem necessariamente aos materiais efetivamente utilizados.

Próximo pacote: cobertura por página/conceito, orçamento explícito, lacunas informadas e referências preservadas depois de agrupamento. Testar material extenso e diferentes grupos de embeddings.

### 6. Navegação e confiabilidade — pacote desta revisão

- Respostas exibiam Markdown literal. Adicionado renderizador seguro de títulos, negrito, listas e blocos de código; sem HTML executável e sem corte da resposta.
- Configuração técnica no chat passou para seção opcional recolhida. Valores e modelos não mudaram.
- Erro de imagem não deve aparecer como 100% concluído. Estados terminais agora têm rótulos próprios.
- Modal de imagem recebe foco ao abrir, permite Escape, mantém Tab no controle e devolve foco ao botão da imagem.
- Ao arquivar, o código limpava a conversa antes de ler seu escopo e apagava a lista exibida. Agora remove localmente somente o item confirmado pela API; falha preserva histórico; troca de conversa durante a requisição não apaga a nova seleção.
- Incluída declaração Vue para verificação TypeScript. O build Docker passa a executar tipagem e testes de regressão antes do Vite.

Limitações: formatação é um subconjunto simples, não Markdown completo (tabelas/listas aninhadas não recebem layout especial). Revisão de todos os fluxos mobile, leitores de tela e atividades continua necessária. O bundle principal de aproximadamente 766 kB gera aviso de tamanho; planejar carregamento sob demanda dos renderizadores pesados.

## Harness, especialistas e Tools encontrados

O `tutorAgentHarness.py` coordena a execução. O registro de especialistas conecta consulta a evidências, geração de resposta e revisão básica. Tools internas continuam sendo o limite de execução. A existência de classes de especialistas não comprova revisão semântica, escopo obrigatório em cada contrato ou auditoria persistida; esses itens precisam de gates próprios. O subagente usado nesta revisão de código não foi instalado como agente da Lia.

## Gates e rollback

- Baseline backend: 99 testes passaram (6 avisos de depreciação).
- Pacote frontend: 9 testes comportamentais passaram, incluindo renderização SSR, HTML inerte, texto longo, arquivamento, falha, troca de conversa e resposta de polling atrasada após arquivamento/reset de escopo.
- `tsc --noEmit`: passou após correção; não substitui vue-tsc nem teste de navegador.
- Build Vite: passou, com aviso de chunk >500 kB.
- `git diff --check`: passou.
- Automação de navegador desktop falhou com `CreateProcessWithLogonW failed: 267`. Alternativa executada com Chromium/Playwright em container isolado: navegação de perfil/contexto/matéria/lição existentes, histórico, listas e negrito, configurações recolhidas, abertura de imagem, Tab/Escape e retorno de foco passaram. Em 1280 px e 390 px não houve erros JavaScript; em 390 px não houve overflow horizontal. Cenário ERROR simulado apenas na resposta interceptada do navegador mostrou Não concluída e não exibiu imagem como pronta. Gravações na API foram bloqueadas durante o gate.
- Inspeção visual das capturas confirmou tamanho do texto, modal e legibilidade do texto determinístico. Corrigido conflito CSS que reduzia o negrito e removida mensagem de erro repetida. Gates repetidos após correção: PASS.
- Capturas e roteiro temporários: `/tmp/lia2-browser-gate-qq4yMJ/` no servidor. A imagem pedagógica antiga continua genérica; este gate aprova sua apresentação, não sua qualidade conceitual.

Rollback do pacote: reverter somente o commit desta revisão e reconstruir/recriar apenas `lia2-student-web` com Compose. Nenhuma reversão de banco, configuração ou modelo é necessária. Baseline de referência: `bd4dfcb`. Preservar arquivos locais não rastreados e qualquer alteração posterior.

Recuperação operacional adicional: `lia2-student-web-rollback:bd4dfcb`, construída com os assets e configuração Nginx copiados do container que estava servindo a versão anterior. O conteúdo Docker da imagem antiga não estava mais disponível para tag/commit direto; a cópia dos arquivos ativos e o build da imagem de recuperação passaram. A imagem de recuperação usa a base Nginx disponível, não promete preservar o digest antigo.

## Ordem recomendada dos próximos pacotes

1. Validação técnica/visual/teclado do pacote de navegação concluída nos cenários acima; manter aceite com usuários reais como etapa distinta.
2. Consolidação canônica com auditoria e escopo, incluindo migração aditiva e publicação reversível.
3. Gate pedagógico compartilhado e perfil de aprendizagem.
4. Ilustração conceitualmente validada, textos determinísticos e contingência explícita.
5. Testes ponta a ponta mobile/desktop com tarefas reais e medição de tempo, erros e compreensão.

Não declarar a plataforma inteira aprovada até esses gates. Uma melhoria de interface não resolve os problemas de conteúdo identificados.
