from copy import deepcopy
from uuid import uuid4
from types import SimpleNamespace
from contextlib import nullcontext
from unittest.mock import patch
import pytest
from app.services.mindMapContentService import MindMapContent, generateMindMap
from app.services.mindMapAssetService import MindMapAssetService

def content(title='Assunto não cadastrado'):
    return {'title': title, 'rootId': 'root', 'nodes': [
        {'nodeId': 'root', 'parentId': None, 'label': title, 'detail': 'Síntese fiel.', 'visualDescription': 'A concrete scene representing the central concept.'},
        {'nodeId': 'a', 'parentId': 'root', 'label': 'Conceito A', 'detail': 'Explicação em português.', 'visualDescription': 'A different concrete scene of the first concept.'},
        {'nodeId': 'b', 'parentId': 'a', 'label': 'Evidência', 'detail': 'Detalhe preservado.'}]}

@pytest.mark.parametrize('title', ['Movimentos', 'Linguagem', 'Tema inédito'])
def test_generic_canonical_contract(title):
    result = MindMapContent.model_validate(content(title)).model_dump()
    assert result['contractName'] == 'LIA_MINDMAP_V1'
    assert result['language'] == 'pt-BR'
    assert result['relationship'] == 'PARALLEL'

@pytest.mark.parametrize('kind', ['cycle','duplicate','missing','long','duplicate_title'])
def test_invalid_contract_rejected(kind):
    data = content()
    if kind == 'cycle': data['nodes'][1]['parentId'] = 'b'
    elif kind == 'duplicate': data['nodes'][2]['nodeId'] = 'a'
    elif kind == 'missing': data['nodes'][1]['parentId'] = 'absent'
    elif kind == 'long': data['nodes'][1]['detail'] = 'x' * 241
    else: data['nodes'].append({**data['nodes'][1], 'nodeId': 'c'})
    with pytest.raises(ValueError): MindMapContent.model_validate(data)

def test_bounded_model_repair_without_subject_rules():
    calls = []
    class Client:
        def chatStructured(self, **args):
            calls.append(args)
            return {} if len(calls) == 1 else content()
    result = generateMindMap(Client(), modelId='existing-model', prompt='Material', think=False)
    assert len(calls) == 2 and result['rootId'] == 'root'
    assert calls[0]['modelId'] == 'existing-model'

def test_model_task_ids_are_not_trusted():
    data = content(); data['nodes'][1]['imageTaskId'] = str(uuid4())
    assert 'imageTaskId' not in MindMapContent.model_validate(data).model_dump()['nodes'][1]

class Session:
    def __init__(self, cached=None): self.created = []; self.cached = cached; self.locks = []
    def begin_nested(self): return nullcontext()
    def execute(self, query, args): self.locks.append(args['key'])
    def scalar(self, query): return self.cached
    def add(self, task): task.imageTaskId = uuid4(); self.created.append(task)
    def flush(self): pass

def attach(session, data=None):
    with patch('app.services.mindMapAssetService.StudentContentOwnershipService', autospec=True) as owner:
        owner.return_value.assertUnitBelongsToStudent.return_value = (SimpleNamespace(title='Lição'), SimpleNamespace(name='Matéria'), None)
        result = MindMapAssetService(session).attach(data or content(), studentId=uuid4(), unitId=uuid4(), materialIds=[uuid4()], evidence=[], artifactId=uuid4())
    return result

def test_only_root_and_branches_queued_and_prompt_is_scene_only():
    session = Session(); result = attach(session)
    assert len(session.created) == 2
    assert 'imageTaskId' not in result['nodes'][2]
    assert all(t.prompt.startswith('LIA_SCENE_V2:NO_TEXT\n') for t in session.created)
    assert all('Explicação em português' not in t.prompt for t in session.created)
    assert len(session.locks) == 2

def test_cached_tasks_reused_without_new_gpu_jobs():
    cached = SimpleNamespace(imageTaskId=uuid4())
    session = Session(cached); result = attach(session)
    assert not session.created
    assert result['nodes'][0]['imageTaskId'] == str(cached.imageTaskId)

def test_scope_rejection_is_not_silenced():
    with patch('app.services.mindMapAssetService.StudentContentOwnershipService', autospec=True) as owner:
        owner.return_value.assertUnitBelongsToStudent.side_effect = ValueError('scope')
        with pytest.raises(ValueError): MindMapAssetService(Session()).attach(content(), studentId=uuid4(), unitId=uuid4(), materialIds=[], evidence=[])
