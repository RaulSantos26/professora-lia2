from app.services.documentIngestionService import DocumentProcessingError


def testDocumentProcessingErrorCarriesSafeMessage():
    error = DocumentProcessingError(
        code="PDF_PARSE_ERROR",
        safeMessage="PDF inválido.",
    )

    assert error.code == "PDF_PARSE_ERROR"
    assert error.safeMessage == "PDF inválido."
