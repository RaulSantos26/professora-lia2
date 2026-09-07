from app.services.ollamaClientService import OllamaClientService
from app.services.mindMapContentService import generateMindMap


class VisualGenerationService:
    def __init__(self):
        self.ollama = OllamaClientService()

    def generate(
        self,
        *,
        visualType: str,
        evidenceContext: str,
        instruction: str,
        modelId: str,
        thinkingEnabled: bool,
        researchReferences: list[dict] | None = None,
        evidence: list[dict] | None = None,
    ) -> dict:
        if visualType == 'MIND_MAP' and evidence:
            # Both entry points share the same full-material budget and contract.
            from app.services.pedagogicalGenerationService import PedagogicalGenerationService
            generator = PedagogicalGenerationService()
            generator.ollama = self.ollama
            return generator.generate(artifactType='MIND_MAP', context=evidenceContext,
                instruction=instruction, difficulty='AUTO', questionCount=8,
                modelId=modelId, thinkingEnabled=thinkingEnabled, evidence=evidence)
        schema = self._schema(visualType)

        prompt = f"""
Você é o Visual Learning Engine da Professora Lia.

Crie uma especificação visual educacional estruturada.
Use SOMENTE as evidências fornecidas.

REGRAS:
- português brasileiro;
- não invente fatos ausentes;
- preserve terminologia do material;
- priorize clareza didática;
- retorne somente a estrutura pedida;
- não produza HTML, SVG, JavaScript ou Three.js;
- descreva personagens, objetos e cenário pelo papel semântico, nunca como
  formas geométricas genéricas;
- em ANIMATION_2D, organize uma narrativa em 3 momentos observáveis;
- posições geométricas serão calculadas por uma Skill Python;
- referências de evidência devem usar índices 1..N.
- Em MIND_MAP, use uma raiz e 4 a 7 ramos principais se as evidências permitirem,
  até 3 conceitos subordinados por ramo, títulos curtos e explicações concisas.
  Escolha um único emoji em icon pela semântica do conceito, ou string vazia.
  Nunca invente conteúdo para preencher a quantidade de ramos.

TIPO VISUAL:
{visualType}

PEDIDO DO ALUNO:
{instruction}

EVIDÊNCIAS:
{evidenceContext}

REFERÊNCIAS VISUAIS CONTROLADAS (somente para enriquecer a representação;
as evidências do aluno continuam sendo a fonte de verdade):
{researchReferences or []}
""".strip()

        if visualType == 'MIND_MAP':
            return generateMindMap(self.ollama, modelId=modelId, prompt=prompt, think=thinkingEnabled)

        return self.ollama.chatStructured(
            modelId=modelId,
            prompt=prompt,
            schema=schema,
            think=thinkingEnabled,
        )

    def _schema(self, visualType: str) -> dict:
        if visualType == "MIND_MAP":
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

        if visualType == "DIAGRAM":
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "nodeId": {"type": "string"},
                                "label": {"type": "string"},
                                "detail": {"type": "string"},
                                "evidenceRefs": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                },
                            },
                            "required": [
                                "nodeId",
                                "label",
                                "detail",
                                "evidenceRefs",
                            ],
                        },
                    },
                    "edges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "sourceId": {"type": "string"},
                                "targetId": {"type": "string"},
                                "label": {"type": "string"},
                            },
                            "required": [
                                "sourceId",
                                "targetId",
                                "label",
                            ],
                        },
                    },
                },
                "required": ["title", "nodes", "edges"],
            }

        if visualType == "CHART":
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "chartType": {
                        "type": "string",
                        "enum": ["BAR", "LINE"],
                    },
                    "xLabel": {"type": "string"},
                    "yLabel": {"type": "string"},
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "series": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "values": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                },
                            },
                            "required": ["name", "values"],
                        },
                    },
                    "notes": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [
                    "title",
                    "chartType",
                    "xLabel",
                    "yLabel",
                    "categories",
                    "series",
                    "notes",
                ],
            }

        if visualType == "ANIMATION_2D":
            return {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "objects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "objectId": {"type": "string"},
                                "label": {"type": "string"},
                                "role": {
                                    "type": "string",
                                    "enum": [
                                        "HERO", "CREATURE", "DEITY",
                                        "MESSENGER", "ITEM", "SCENERY",
                                        "TEXT", "CONCEPT"
                                    ],
                                },
                                "shape": {
                                    "type": "string",
                                    "enum": [
                                        "CIRCLE",
                                        "RECTANGLE",
                                    ],
                                },
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "size": {"type": "number"},
                                "motion": {
                                    "type": "string",
                                    "enum": [
                                        "STATIC",
                                        "ORBIT",
                                        "LINEAR",
                                    ],
                                },
                                "speed": {"type": "number"},
                                "orbitRadius": {"type": "number"},
                                "parentId": {
                                    "type": ["string", "null"],
                                },
                            },
                            "required": [
                                "objectId",
                                "label",
                                "role",
                                "shape",
                                "x",
                                "y",
                                "size",
                                "motion",
                                "speed",
                                "orbitRadius",
                                "parentId",
                            ],
                        },
                    },
                },
                "required": [
                    "title",
                    "description",
                    "objects",
                ],
            }

        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "objects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "objectId": {"type": "string"},
                            "label": {"type": "string"},
                            "primitive": {
                                "type": "string",
                                "enum": [
                                    "SPHERE",
                                    "BOX",
                                    "CYLINDER",
                                ],
                            },
                            "position": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "z": {"type": "number"},
                                },
                                "required": ["x", "y", "z"],
                            },
                            "scale": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "z": {"type": "number"},
                                },
                                "required": ["x", "y", "z"],
                            },
                            "orbit": {
                                "type": [
                                    "object",
                                    "null",
                                ],
                                "properties": {
                                    "radius": {"type": "number"},
                                    "speed": {"type": "number"},
                                    "centerObjectId": {
                                        "type": [
                                            "string",
                                            "null",
                                        ],
                                    },
                                },
                            },
                            "rotationSpeed": {"type": "number"},
                        },
                        "required": [
                            "objectId",
                            "label",
                            "primitive",
                            "position",
                            "scale",
                            "orbit",
                            "rotationSpeed",
                        ],
                    },
                },
            },
            "required": [
                "title",
                "description",
                "objects",
            ],
        }
