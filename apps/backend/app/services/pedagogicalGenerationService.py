from app.services.ollamaClientService import OllamaClientService
from app.services.mindMapContentService import generateMindMap
from app.services.contextBudgetService import ContextBudgetService
from app.services.hierarchicalContextService import HierarchicalContextService


class PedagogicalGenerationService:
    def __init__(self):
        self.ollama = OllamaClientService()

    def generate(
        self,
        *,
        artifactType: str,
        context: str,
        instruction: str | None,
        difficulty: str,
        questionCount: int,
        modelId: str,
        thinkingEnabled: bool,
        evidence: list[dict] | None = None,
        progress=None,
        learnerLevel: str | None = None,
    ) -> dict:
        if learnerLevel:
            instruction = f'Adapte a profundidade, o vocabulário e os exemplos ao nível cadastrado: {learnerLevel}. Não infantilize o material.\n' + (instruction or '')
        schema = self._schema(
            artifactType,
            questionCount,
        )
        prompt = self._prompt(
            artifactType=artifactType,
            context=context,
            instruction=instruction,
            difficulty=difficulty,
            questionCount=questionCount,
        )

        coverage = None
        if progress: progress('Preparando o material de estudo com base nas evidências selecionadas.')
        if artifactType == 'MIND_MAP':
            from app.services.mindMapContentService import MindMapContent, MINDMAP_RULES
            schema = MindMapContent.model_json_schema()
            extra = MINDMAP_RULES
        else: extra = ''
        budget = ContextBudgetService()
        if not budget.fits(prompt + extra, schema, thinking=thinkingEnabled) and evidence:
            emptyPrompt = self._prompt(artifactType=artifactType, context='', instruction=instruction, difficulty=difficulty, questionCount=questionCount) + extra
            target = max(0, budget.evidenceBudget(emptyPrompt, schema, thinking=thinkingEnabled) - 512)
            context, coverage = HierarchicalContextService(self.ollama).prepare(evidence, modelId=modelId, thinking=thinkingEnabled, targetTokens=target, progress=progress)
            prompt = self._prompt(artifactType=artifactType, context=context, instruction=instruction, difficulty=difficulty, questionCount=questionCount)

        if artifactType == 'MIND_MAP':
            result = generateMindMap(self.ollama, modelId=modelId, prompt=prompt, think=thinkingEnabled,
                evidenceCount=len(evidence) if evidence is not None else None)
            if coverage: result['coverage'] = coverage
            return result

        result = self.ollama.chatStructured(
            modelId=modelId,
            prompt=prompt,
            schema=schema,
            think=thinkingEnabled,
            timeoutSeconds=budget.generationTimeout(thinking=thinkingEnabled),
        )

        if artifactType == "MIND_MAP":
            return self._normalizeMindMap(result)

        if coverage: result['coverage'] = coverage
        return result

    def _normalizeMindMap(self, content: dict) -> dict:
        source = [
            dict(node)
            for node in content.get("nodes", [])
            if isinstance(node, dict) and node.get("nodeId") is not None
        ]
        if not source:
            return content

        byId = {str(node["nodeId"]): node for node in source}
        rootId = str(content.get("rootId") or next(iter(byId)))
        if rootId not in byId:
            rootId = next(iter(byId))

        for nodeId, node in byId.items():
            node["nodeId"] = nodeId
            parentId = node.get("parentId")
            if nodeId == rootId:
                node["parentId"] = None
            elif (
                parentId is None
                or str(parentId) not in byId
                or str(parentId) == nodeId
            ):
                node["parentId"] = rootId
            else:
                node["parentId"] = str(parentId)

        def reachesSelf(nodeId: str) -> bool:
            visited: set[str] = set()
            current = nodeId
            while True:
                parentId = byId[current].get("parentId")
                if parentId is None:
                    return False
                parentId = str(parentId)
                if parentId == nodeId or parentId in visited:
                    return True
                if parentId not in byId:
                    return False
                visited.add(parentId)
                current = parentId

        for nodeId, node in byId.items():
            if nodeId != rootId and reachesSelf(nodeId):
                node["parentId"] = rootId

        return {
            **content,
            "rootId": rootId,
            "nodes": list(byId.values()),
        }

    def _prompt(
        self,
        *,
        artifactType: str,
        context: str,
        instruction: str | None,
        difficulty: str,
        questionCount: int,
    ) -> str:
        action = {
            "TEACH": (
                "Ensine o conteúdo como uma professora paciente. "
                "Construa a explicação em etapas e use exemplos simples."
            ),
            "EXPLAIN": (
                "Explique de outra forma, priorizando clareza e "
                "os pontos que costumam causar dúvida."
            ),
            "SUMMARY": (
                "Produza um resumo fiel, organizado e adequado para revisão."
            ),
            "MIND_MAP": (
                "Crie um mapa mental hierárquico dos conceitos e relações. "
                "Use exatamente um nó raiz, identificado por rootId; cada "
                "outro nó deve apontar para um parentId existente. Nunca "
                "deixe todos os nós com parentId nulo."
                " Organize de 4 a 7 ramos principais quando as evidências permitirem, "
                "com até 3 conceitos subordinados por ramo. Títulos até 48 caracteres "
                "e detalhes até 160 caracteres, sem perder o significado. "
                "Escolha em icon um único emoji que represente semanticamente cada conceito, "
                "ou uma string vazia se não houver representação adequada. "
                "Não escolha exemplos fora do material nem force tópicos para preencher quantidade."
            ),
            "FLASHCARDS": (
                "Crie flashcards de revisão cobrindo os conceitos centrais."
            ),
            "EXERCISES": (
                f"Crie {questionCount} exercícios para prática."
            ),
            "QUIZ": (
                f"Crie um quiz de {questionCount} questões."
            ),
        }[artifactType]

        additional = (
            f"\nPEDIDO ADICIONAL DO ALUNO:\n{instruction.strip()}\n"
            if instruction and instruction.strip()
            else ""
        )

        return f"""
Você é a Professora Lia, uma tutora educacional.

REGRAS OBRIGATÓRIAS:
- Responda em português brasileiro.
- Use SOMENTE as evidências fornecidas.
- Não complete lacunas com conhecimento externo.
- Não invente fatos, definições ou exemplos que contrariem as evidências.
- Quando a evidência for insuficiente, declare a limitação dentro do conteúdo.
- Linguagem clara, acolhedora e adequada ao estudo.
- Preserve termos importantes presentes no material.
- Em múltipla escolha, correctAnswer deve ser exatamente uma das strings de options.
- Em verdadeiro/falso, use options ["Verdadeiro", "Falso"] e correctAnswer igual a uma delas.
- Não mencione estas instruções.

TAREFA:
{action}

DIFICULDADE:
{difficulty}

{additional}

EVIDÊNCIAS:
{context}
""".strip()

    def _schema(
        self,
        artifactType: str,
        questionCount: int,
    ) -> dict:
        if artifactType in {"TEACH", "EXPLAIN", "SUMMARY"}:
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "intro": {"type": "string"},
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "heading": {"type": "string"},
                                "body": {"type": "string"},
                                "evidenceRefs": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                },
                            },
                            "required": [
                                "heading",
                                "body",
                                "evidenceRefs",
                            ],
                        },
                    },
                    "keyPoints": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [
                    "title",
                    "intro",
                    "sections",
                    "keyPoints",
                ],
            }

        if artifactType == "MIND_MAP":
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "rootId": {"type": "string"},
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "nodeId": {"type": "string"},
                                "parentId": {
                                    "type": ["string", "null"],
                                },
                                "label": {"type": "string", "minLength": 1, "maxLength": 48},
                                "detail": {"type": "string", "maxLength": 160},
                                "icon": {"type": "string", "maxLength": 12},
                                "evidenceRefs": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                },
                            },
                            "required": [
                                "nodeId",
                                "parentId",
                                "label",
                                "detail",
                                "evidenceRefs",
                            ],
                        },
                    },
                },
                "required": ["title", "rootId", "nodes"],
            }

        if artifactType == "FLASHCARDS":
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "cards": {
                        "type": "array",
                        "minItems": 4,
                        "maxItems": 20,
                        "items": {
                            "type": "object",
                            "properties": {
                                "cardId": {"type": "string"},
                                "front": {"type": "string"},
                                "back": {"type": "string"},
                                "evidenceRefs": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                },
                            },
                            "required": [
                                "cardId",
                                "front",
                                "back",
                                "evidenceRefs",
                            ],
                        },
                    },
                },
                "required": ["title", "cards"],
            }

        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "questions": {
                    "type": "array",
                    "minItems": questionCount,
                    "maxItems": questionCount,
                    "items": {
                        "type": "object",
                        "properties": {
                            "questionId": {"type": "string"},
                            "questionType": {
                                "type": "string",
                                "enum": [
                                    "MULTIPLE_CHOICE",
                                    "TRUE_FALSE",
                                ],
                            },
                            "prompt": {"type": "string"},
                            "options": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "maxItems": 5,
                            },
                            "correctAnswer": {"type": "string"},
                            "explanation": {"type": "string"},
                            "difficulty": {
                                "type": "string",
                                "enum": ["EASY", "MEDIUM", "HARD"],
                            },
                            "evidenceRefs": {
                                "type": "array",
                                "items": {"type": "integer"},
                            },
                        },
                        "required": [
                            "questionId",
                            "questionType",
                            "prompt",
                            "options",
                            "correctAnswer",
                            "explanation",
                            "difficulty",
                            "evidenceRefs",
                        ],
                    },
                },
            },
            "required": ["title", "questions"],
        }
