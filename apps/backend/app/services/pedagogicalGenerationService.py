from app.services.ollamaClientService import OllamaClientService


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
    ) -> dict:
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

        result = self.ollama.chatStructured(
            modelId=modelId,
            prompt=prompt,
            schema=schema,
            think=thinkingEnabled,
        )

        if artifactType == "MIND_MAP":
            return self._normalizeMindMap(result)

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
                                "label": {"type": "string"},
                                "detail": {"type": "string"},
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
