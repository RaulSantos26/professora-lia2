from app.services.ollamaClientService import OllamaClientService


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
    ) -> dict:
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
- posições geométricas serão calculadas por uma Skill Python;
- referências de evidência devem usar índices 1..N.

TIPO VISUAL:
{visualType}

PEDIDO DO ALUNO:
{instruction}

EVIDÊNCIAS:
{evidenceContext}
""".strip()

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
