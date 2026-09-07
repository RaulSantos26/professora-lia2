"""Canonical semantic map contract; no model-selected geometry or executable markup."""
import logging
import time
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from app.domain.common.domainError import DomainError

logger = logging.getLogger(__name__)

class MindMapNode(BaseModel):
    nodeId: str = Field(min_length=1, max_length=80)
    parentId: str | None
    label: str = Field(min_length=1, max_length=64)
    detail: str = Field(max_length=240)
    icon: str = Field(default='', max_length=12)
    visualDescription: str = Field(default='', max_length=600)
    evidenceRefs: list[int] = Field(default_factory=list, max_length=20)

class MindMapContent(BaseModel):
    contractName: Literal['LIA_MINDMAP_V1'] = 'LIA_MINDMAP_V1'
    language: Literal['pt-BR'] = 'pt-BR'
    title: str = Field(min_length=1, max_length=160)
    rootId: str
    relationship: Literal['PARALLEL', 'SEQUENCE'] = 'PARALLEL'
    nodes: list[MindMapNode] = Field(min_length=2, max_length=29)

    @model_validator(mode='after')
    def validateTree(self):
        byId = {n.nodeId: n for n in self.nodes}
        if len(byId) != len(self.nodes) or self.rootId not in byId:
            raise ValueError('IDs duplicados ou raiz inexistente')
        roots = [n for n in self.nodes if n.parentId is None]
        if len(roots) != 1 or roots[0].nodeId != self.rootId:
            raise ValueError('Use exatamente uma raiz')
        branches = [n for n in self.nodes if n.parentId == self.rootId]
        if not 1 <= len(branches) <= 7:
            raise ValueError('Use entre um e sete ramos principais, conforme evidências')
        if len({n.label.strip().casefold() for n in branches}) != len(branches):
            raise ValueError('Títulos de ramos repetidos')
        for node in self.nodes:
            if not node.label.strip() or any(i < 1 for i in node.evidenceRefs):
                raise ValueError('Título vazio ou referência inválida')
            seen = set(); current = node
            while current.parentId is not None:
                if current.nodeId in seen or current.parentId not in byId:
                    raise ValueError('Ciclo ou conexão inválida')
                seen.add(current.nodeId); current = byId[current.parentId]
            if len(seen) > 2:
                raise ValueError('Use raiz, ramo e até três conceitos por ramo; sem profundidade extra')
        for branch in branches:
            if sum(n.parentId == branch.nodeId for n in self.nodes) > 3:
                raise ValueError('Máximo de três conceitos subordinados por ramo')
        return self

MINDMAP_RULES = '''
MAPA MENTAL: contrato LIA_MINDMAP_V1, português brasileiro, uma raiz e ramos distintos.
Organize 4 a 7 ramos quando o material permitir; não invente ramos para preencher espaço.
Cada ramo tem até 3 conceitos subordinados; não crie níveis mais profundos.
Escolha relationship SEQUENCE somente se a relação real for uma sequência ordenada;
caso contrário PARALLEL. Não escolha layout por nome de tema ou disciplina.
Use títulos curtos e até 2 frases curtas por detail, adequados ao nível informado.
Em visualDescription da raiz e de CADA ramo, descreva em inglês uma ilustração concreta,
com objetos e ações coerentes com o conceito e as evidências. Nunca peça o mapa inteiro,
cartaz, gráfico com texto ou legenda. Não repita os bullets como prompt de imagem.
Para conceitos que não tenham representação visual fiel, use visualDescription vazia.
Nas folhas use visualDescription vazia. icon é opcional, um emoji semanticamente adequado.
Não escreva coordenadas, URLs, código, nomes de arquivo nem imageTaskId.
'''

def generateMindMap(client, *, modelId, prompt, think, evidenceCount=None):
    from app.services.contextBudgetService import ContextBudgetService
    started = time.monotonic()
    for attempt in range(2):
        result = client.chatStructured(modelId=modelId, prompt=prompt + MINDMAP_RULES,
            schema=MindMapContent.model_json_schema(), think=think,
            timeoutSeconds=ContextBudgetService().generationTimeout(thinking=think))
        try:
            content = MindMapContent.model_validate(result).model_dump()
            if evidenceCount is not None and any(ref > evidenceCount for node in content['nodes'] for ref in node['evidenceRefs']):
                raise ValueError('Referência fora das evidências fornecidas')
            logger.info('mindmap_content_validated model=%s nodes=%s attempt=%s duration=%.2f',
                modelId, len(content['nodes']), attempt + 1, time.monotonic() - started)
            return content
        except ValueError:
            logger.warning('mindmap_contract_invalid attempt=%s', attempt + 1)
            prompt += '\nRevise a estrutura: IDs únicos, uma raiz, até sete ramos sem títulos repetidos e até três folhas por ramo. Respeite os limites de texto do schema.'
    raise DomainError(code='MIND_MAP_VALIDATION_FAILED', message='A Lia não conseguiu organizar o mapa com clareza. Tente novamente; seus materiais foram preservados.', httpStatus=422)
