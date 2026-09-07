import io
import json
import urllib.error
from unittest.mock import patch
import pytest
from app.domain.common.domainError import DomainError
from app.services.contextBudgetService import ContextBudgetService
from app.services.ollamaClientService import OllamaClientService
from app.services.hierarchicalContextService import HierarchicalContextService

def test_small_and_measured_mid_prompt_fit():
    budget = ContextBudgetService()
    assert budget.fits('conteúdo ' * 700, {'type':'object'})
    assert budget.fits('material de estudo ' * 1480, {'type':'object'})
    assert not budget.fits('conteúdo ' * 15000, {'type':'object'})

def test_schema_and_thinking_are_budgeted():
    budget = ContextBudgetService()
    assert budget.evidenceBudget('curto', {}, thinking=True) < budget.evidenceBudget('curto', {}, thinking=False)
    assert not budget.fits('curto', {'description':'x' * 50000})
    assert budget.estimate('x'*500) == 500

def test_long_task_deadline_matches_output_reserve_without_disabling_thinking():
    budget = ContextBudgetService()
    assert budget.generationTimeout(thinking=False) >= 6144 / 6 + 180
    assert budget.generationTimeout(thinking=True) >= 8192 / 6 + 180

def test_oversized_prompt_never_reaches_provider():
    client = OllamaClientService()
    with patch.object(client, '_post') as post:
        with pytest.raises(DomainError) as err: client.chatStructured(modelId='existing', prompt='x'*60000, schema={})
    assert err.value.code == 'OLLAMA_CONTEXT_EXCEEDED'; post.assert_not_called()

def test_options_explicit_and_output_limit_never_success():
    client = OllamaClientService()
    with patch.object(client, '_post', return_value={'message':{'content':'{}'},'done_reason':'length'}) as post:
        with pytest.raises(DomainError) as err: client.chatStructured(modelId='existing', prompt='curto', schema={}, think=True)
    payload = post.call_args.args[1]
    assert payload['options']['num_ctx'] == 24576
    assert payload['options']['num_predict'] == 8192 and payload['think'] is True
    assert err.value.code == 'OLLAMA_OUTPUT_LIMIT'

def test_http_context_error_sanitized():
    error = urllib.error.HTTPError('http://local', 400, 'bad', {}, io.BytesIO(b'request (12140 tokens) exceeds the available context size (8192 tokens)'))
    with patch('urllib.request.urlopen', side_effect=error):
        with pytest.raises(DomainError) as err: OllamaClientService()._post('/api/chat', {'model':'existing'}, 1)
    assert err.value.code == 'OLLAMA_CONTEXT_EXCEEDED'
    assert '12140' not in err.value.message and 'HTTP' not in err.value.message

def test_hierarchical_last_segment_and_global_refs_preserved():
    calls = []
    class Client:
        def chatStructured(self, **args):
            calls.append(args)
            import re
            refs = json.loads(re.search(r'globais, sem renumerá-los: (\[[^\]]+\])', args['prompt']).group(1))
            return {'topics':[{'heading':'Síntese', 'facts':['Conceitos preservados'], 'evidenceRefs':refs}], 'limitations':[]}
    evidence = [{'excerpt': ('Conceito importante. ' * 400) + (' ÚLTIMO_CONCEITO' if i==3 else ''), 'materialTitle':'Fonte', 'locator':str(i)} for i in range(4)]
    output, ledger = HierarchicalContextService(Client()).prepare(evidence, modelId='existing', thinking=False, targetTokens=7000)
    assert any('ÚLTIMO_CONCEITO' in c['prompt'] for c in calls)
    assert ledger['sourceRefs'] == [1,2,3,4]
    assert ledger['processedSegments'] == ledger['segmentCount']

def test_hierarchical_invalid_references_fail_explicitly():
    class Client:
        def chatStructured(self, **args): return {'topics':[{'evidenceRefs':[999]}]}
    with pytest.raises(DomainError) as err:
        HierarchicalContextService(Client()).prepare([{'excerpt':'Conteúdo'}],modelId='existing',thinking=False,targetTokens=7000)
    assert err.value.code == 'SYNTHESIS_EVIDENCE_INVALID'

def test_context_rejects_selected_material_from_another_lesson():
    from types import SimpleNamespace
    from uuid import uuid4
    from app.services.pedagogicalContextService import PedagogicalContextService
    from unittest.mock import Mock
    service=PedagogicalContextService.__new__(PedagogicalContextService)
    material=SimpleNamespace(materialId=uuid4(),studyEnabled=True,studentLearningContextId=uuid4(),studentSubjectId=uuid4(),studentLearningUnitId=uuid4())
    service.materialRepository=Mock()
    service.materialRepository.listByStudentId.return_value=[material]
    with pytest.raises(DomainError) as err:
        service.build(studentId=uuid4(),materialIds=[material.materialId],studentLearningContextId=material.studentLearningContextId,
            studentSubjectId=material.studentSubjectId,studentLearningUnitId=uuid4())
    assert err.value.code=='PEDAGOGICAL_SCOPE_MISMATCH'
