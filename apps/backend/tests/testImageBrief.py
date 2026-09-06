from datetime import datetime, timezone
from types import SimpleNamespace as S
from uuid import uuid4
import pytest
from app.services.imageBriefService import ImageBriefService
from app.persistence.models.agentThreadModel import AgentThreadModel


def fixture():
    student, threadId, runId = uuid4(), uuid4(), uuid4()
    task = S(studentId=student, agentThreadId=threadId, agentRunId=runId,
             createdAt=datetime.now(timezone.utc), title='consegue fazer uma ilustração',
             prompt='legacy prompt', labelsJson=['Matéria: História', 'Lição: Escrita'],
             evidenceJson=[{'excerpt': 'A escrita registrava trocas em tabuletas de argila.'}])
    thread = S(studentId=student, agentThreadId=threadId)
    run = S(agentThreadId=threadId, effectiveTextModelId='existing-model')
    messages = [S(role='USER', content='Como surgiu a escrita?')]
    session = S(get=lambda kind, key: thread if kind is AgentThreadModel else run,
                scalars=lambda query: S(all=lambda: messages))
    calls = []
    def chat(**kwargs):
        calls.append(kwargs)
        return {'title': 'O registro da escrita', 'scene': 'A historical scribe presses small stylized marks into a clay tablet with a reed stylus, surrounded by clay vessels.',
                'explanation': 'A escrita permitiu registrar informações. Na cena, a tabuleta de argila representa um suporte para conservar registros, como quantidades de produtos trocados.',
                'intrinsicWriting': True}
    return task, session, S(chatStructured=chat), calls, thread


def testBriefUsesSameThreadAndExistingModelSeparatesExplanation():
    task, session, client, calls, _ = fixture()
    scene, policy = ImageBriefService(session, client).prepare(task)
    assert policy == 'IN_SCENE_MARKS'
    assert 'Como surgiu a escrita?' in calls[0]['prompt']
    assert calls[0]['modelId'] == 'existing-model'
    assert 'A escrita permitiu' not in scene
    assert task.labelsJson[-1].startswith('Explicação visual: A escrita permitiu')
    assert task.labelsJson[:2] == ['Matéria: História', 'Lição: Escrita']


def testPreparedBriefIsReusedWithoutExtraModelCall():
    task, session, client, calls, _ = fixture()
    service = ImageBriefService(session, client)
    expected = service.prepare(task)
    assert service.prepare(task) == expected
    assert len(calls) == 1


def testDifferentStudentIsRejectedBeforeCallingModel():
    task, session, client, calls, thread = fixture()
    thread.studentId = uuid4()
    with pytest.raises(ValueError, match='SCOPE_MISMATCH'):
        ImageBriefService(session, client).prepare(task)
    assert calls == []


def testEmptyExplanationDoesNotPublishBrief():
    task, session, _, _, _ = fixture()
    client = S(chatStructured=lambda **kw: {'title': 'Teste', 'scene': 'x' * 90, 'explanation': ''})
    with pytest.raises(ValueError):
        ImageBriefService(session, client).prepare(task)
    assert task.prompt == 'legacy prompt'
