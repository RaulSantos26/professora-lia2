from app.services.documentIngestionService import DocumentIngestionService


def testDocumentChunkingKeepsContent():
    service = DocumentIngestionService.__new__(DocumentIngestionService)
    service.CHUNK_SIZE = 50

    text = (
        "Primeiro parágrafo com conteúdo relevante.\n"
        "Segundo parágrafo com outro conteúdo relevante.\n"
        "Terceiro parágrafo para completar o teste."
    )

    chunks = service._chunks(text)

    assert len(chunks) >= 2
    assert "Primeiro" in chunks[0]
    assert "".join(chunks).replace("\n", "") != ""
