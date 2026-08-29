from PIL import Image

from app.services.ocrAnalysisService import OcrAnalysisService


def testOcrServiceDetectsOrientationAndReturnsText(
    tmp_path,
    monkeypatch,
):
    imagePath = tmp_path / "page.png"
    Image.new(
        "RGB",
        (120, 80),
        "white",
    ).save(imagePath)

    service = OcrAnalysisService()

    monkeypatch.setattr(
        "app.services.ocrAnalysisService.pytesseract.image_to_osd",
        lambda image, config=None: (
            "Page number: 0\n"
            "Orientation in degrees: 270\n"
            "Rotate: 90\n"
        ),
    )
    monkeypatch.setattr(
        "app.services.ocrAnalysisService.pytesseract.image_to_string",
        lambda image, lang=None, config=None: "Tecido conjuntivo",
    )

    result = service.analyzeAndNormalize(imagePath)

    assert result.orientationDegrees == 90
    assert result.text == "Tecido conjuntivo"
