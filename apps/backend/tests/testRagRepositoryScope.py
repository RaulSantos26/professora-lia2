from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy.dialects import postgresql

from app.repositories.ragRepository import RagRepository


def testCandidateQueryRestrictsLatestVersionActiveEvidenceAndAllScopes():
    captured = []
    session = SimpleNamespace(execute=lambda statement: captured.append(statement) or SimpleNamespace(all=lambda: []))
    scopes = [uuid4() for _ in range(5)]
    assert RagRepository(session).listCandidates(
        studentId=scopes[0], studentLearningContextId=scopes[1],
        studentSubjectId=scopes[2], studentLearningUnitId=scopes[3], materialIds=[scopes[4]],
    ) == []
    sql = str(captured[0].compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
    assert "max(lia2.document_version.version_number)" in sql
    assert '"latestVersionNumber" = lia2.document_version.version_number' in sql
    assert "lia2.document_chunk.status = 'EMBEDDED'" in sql
    assert "lia2.document_chunk.evidence_id IS NULL OR lia2.evidence.status = 'ACTIVE'" in sql
    for field, value in zip(["student_id", "student_learning_context_id", "student_subject_id", "student_learning_unit_id"], scopes):
        assert f"lia2.material.{field} = '{value}'" in sql
    assert str(scopes[4]) in sql
    assert "lia2.document_page.page_number" in sql
    assert "lia2.document_chunk.chunk_index" in sql


def testCandidatePreservesPageAndChunkOrderingMetadata():
    row = SimpleNamespace(
        documentChunkId=uuid4(), evidenceId=None, materialId=uuid4(), title="Material",
        sourceGroupId=None, sourceSequence=1, locator=None, content="texto",
        embedding=[0.1], embeddingModelId="existing", documentPageId=uuid4(), pageNumber=12, chunkIndex=21,
    )
    session = SimpleNamespace(execute=lambda statement: SimpleNamespace(all=lambda: [row]))
    candidate = RagRepository(session).listCandidates(studentId=uuid4(), studentLearningContextId=None,
        studentSubjectId=None, studentLearningUnitId=None, materialIds=[])[0]
    assert (candidate.documentPageId, candidate.pageNumber, candidate.chunkIndex) == (row.documentPageId, 12, 21)
