from app.services.ollamaClientService import OllamaClientService


class TutorPlannerService:
    def __init__(self):
        self.ollama = OllamaClientService()

    def plan(
        self,
        *,
        modelId: str,
        thinkingEnabled: bool,
        message: str,
        contextSummary: str,
    ) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": [
                        "GREETING",
                        "ANSWER",
                        "TEACH",
                        "EXPLAIN",
                        "SUMMARY",
                        "MIND_MAP",
                        "DIAGRAM",
                        "CHART",
                        "ANIMATION_2D",
                        "SCENE_3D",
                        "FLASHCARDS",
                        "EXERCISES",
                        "QUIZ",
                        "PROGRESS",
                    ],
                },
                "tools": {
                    "type": "array",
                    "maxItems": 4,
                    "items": {
                        "type": "string",
                        "enum": [
                            "EVIDENCE_SEARCH",
                            "PROGRESS_READ",
                            "PEDAGOGICAL_CREATE",
                            "VISUAL_CREATE",
                            "IMAGE_GENERATION",
                        ],
                    },
                },
                "reason": {
                    "type": "string",
                },
                "visualType": {
                    "type": [
                        "string",
                        "null",
                    ],
                    "enum": [
                        "MIND_MAP",
                        "DIAGRAM",
                        "CHART",
                        "ANIMATION_2D",
                        "SCENE_3D",
                        None,
                    ],
                },
                "imageMode": {
                    "type": ["string", "null"],
                    "enum": ["ILLUSTRATION", "MIND_MAP_COMPANION", None],
                },
                "pedagogicalType": {
                    "type": [
                        "string",
                        "null",
                    ],
                    "enum": [
                        "TEACH",
                        "EXPLAIN",
                        "SUMMARY",
                        "FLASHCARDS",
                        "EXERCISES",
                        "QUIZ",
                        None,
                    ],
                },
            },
            "required": [
                "intent",
                "tools",
                "reason",
                "visualType",
                "imageMode",
                "pedagogicalType",
            ],
        }

        prompt = f"""
Você é o Planner interno da Professora Lia.

Escolha UMA intenção principal e somente as ferramentas necessárias.

REGRAS:
- GREETING não usa ferramenta.
- PROGRESS usa PROGRESS_READ.
- Perguntas sobre conteúdo, ensino, resumo, mapa, diagrama,
  gráfico, animação, cena 3D, flashcards, exercícios ou quiz
  DEVEM usar EVIDENCE_SEARCH.
- TEACH, EXPLAIN, SUMMARY, FLASHCARDS, EXERCISES e QUIZ:
  use EVIDENCE_SEARCH + PEDAGOGICAL_CREATE.
- MIND_MAP usa EVIDENCE_SEARCH + VISUAL_CREATE + IMAGE_GENERATION, com imageMode MIND_MAP_COMPANION.
- DIAGRAM, CHART, ANIMATION_2D e SCENE_3D usam EVIDENCE_SEARCH + VISUAL_CREATE.
- Quando o aluno pedir imagem, desenho, ilustração, figura ou visual didático, use EVIDENCE_SEARCH + IMAGE_GENERATION, com imageMode ILLUSTRATION.
- ANSWER usa EVIDENCE_SEARCH.
- Não invente ferramentas.
- Não responda ao aluno. Apenas planeje.

CONTEXTO DA CONVERSA:
{contextSummary or "sem contexto anterior"}

MENSAGEM DO ALUNO:
{message}
""".strip()

        return self.ollama.chatStructured(
            modelId=modelId,
            prompt=prompt,
            schema=schema,
            think=thinkingEnabled,
        )
