import pypdfium2 as pdfium
from pypdf import PdfWriter


def testPdfiumCanRenderPageToPillow(tmp_path):
    pdfPath = tmp_path / "sample.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=300, height=200)

    with pdfPath.open("wb") as stream:
        writer.write(stream)

    document = pdfium.PdfDocument(str(pdfPath))

    try:
        assert len(document) == 1

        page = document[0]
        bitmap = page.render(scale=1.0)
        image = bitmap.to_pil()

        assert image.width > 0
        assert image.height > 0
    finally:
        document.close()
