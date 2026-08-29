import zipfile

from app.services.documentIngestionService import DocumentIngestionService


def testDocxMediaDiscoveryPreservesEmbeddedImages(tmp_path):
    path = tmp_path / "sample.docx"

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "word/media/image1.png",
            b"fake-png-content",
        )
        archive.writestr(
            "word/document.xml",
            b"<document/>",
        )

    service = DocumentIngestionService.__new__(
        DocumentIngestionService
    )

    media = service._extractDocxMedia(path)

    assert len(media) == 1
    assert media[0][0] == "image1.png"
    assert media[0][1] == b"fake-png-content"
