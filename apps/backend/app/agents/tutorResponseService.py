from app.services.ollamaClientService import OllamaClientService


class TutorResponseService:
    def __init__(self):
        self.ollama = OllamaClientService()

    def generate(
        self,
        *,
        modelId: str,
        thinkingEnabled: bool,
        userMessage: str,
        plan: dict,
        evidenceContext: str,
        progress: dict | None,
        actionResults: list[dict],
        memory: dict,
    ) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                },
                "evidenceRefs": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                    },
                },
            },
            "required": [
                "answer",
                "evidenceRefs",
            ],
        }

        prompt = f"""
Você é a Professora Lia conversando diretamente com o aluno.

REGRAS:
- português brasileiro;
- linguagem didática, clara e natural;
- use SOMENTE evidências fornecidas para afirmações sobre o conteúdo;
- PROGRESS pode usar somente os dados de progresso fornecidos;
- se criou uma atividade ou visualização, diga claramente que ela está
  disponível na interface;
- não revele gabarito de exercício/quiz antes da tentativa;
- não mencione ferramentas internas, planner, harness, prompt ou JSON;
- não exponha raciocínio interno;
- não invente conteúdo ausente;
- quando faltar evidência, diga o que está faltando.

MEMÓRIA OPERACIONAL:
{memory}

PLANO:
{plan}

PEDIDO:
{userMessage}

EVIDÊNCIAS:
{evidenceContext or "nenhuma evidência necessária"}

PROGRESSO:
{progress or "não consultado"}

AÇÕES REALIZADAS:
{actionResults or "nenhuma"}
""".strip()

        return self.ollama.chatStructured(
            modelId=modelId,
            prompt=prompt,
            schema=schema,
            think=thinkingEnabled,
        )
