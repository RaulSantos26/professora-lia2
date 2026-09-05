import unicodedata

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
                    "enum": ["ILLUSTRATION", None],
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
- MIND_MAP usa EVIDENCE_SEARCH + VISUAL_CREATE. Nunca use IMAGE_GENERATION para mapa mental.
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

        plan = self.ollama.chatStructured(
            modelId=modelId,
            prompt=prompt,
            schema=schema,
            think=thinkingEnabled,
        )
        return self.enforceVisualIntent(plan=plan, message=message)

    @staticmethod
    def enforceVisualIntent(*, plan: dict, message: str) -> dict:
        """Ensure explicit student requests reach the internal visual tools."""
        normalized = unicodedata.normalize("NFKD", message).encode(
            "ascii", "ignore"
        ).decode("ascii").casefold()
        adjusted = dict(plan)

        if "mapa mental" in normalized:
            adjusted.update(
                {
                    "intent": "MIND_MAP",
                    "tools": [
                        "EVIDENCE_SEARCH",
                        "VISUAL_CREATE",
                    ],
                    "visualType": "MIND_MAP",
                    "imageMode": None,
                }
            )
            return adjusted

        illustrationTerms = (
            "ilustracao",
            "imagem",
            "desenho",
            "figura",
            "visual didatico",
        )
        if any(term in normalized for term in illustrationTerms):
            adjusted.update(
                {
                    "tools": [
                        "EVIDENCE_SEARCH",
                        "IMAGE_GENERATION",
                    ],
                    "imageMode": "ILLUSTRATION",
                }
            )

        return adjusted
