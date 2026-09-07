from PIL import Image
from app.services.ocrAnalysisService import OcrAnalysisService

def testOcrServiceDetectsOrientationAndReturnsText(tmp_path, monkeypatch):
    imagePath = tmp_path / 'page.png'
    Image.new('RGB', (120, 80), 'white').save(imagePath)
    monkeypatch.setattr('app.services.ocrAnalysisService.pytesseract.image_to_osd', lambda image, config=None: 'Rotate: 90\n')
    def data(image, **kwargs):
        confidence = 95 if image.height > image.width else 30
        words = ['Tecido', 'conjuntivo', 'sustenta', 'e', 'conecta', 'estruturas']
        return {'text': words, 'conf': [confidence] * 6, 'block_num': [1] * 6, 'par_num': [1] * 6, 'line_num': [1] * 6}
    monkeypatch.setattr('app.services.ocrAnalysisService.pytesseract.image_to_data', data)
    result = OcrAnalysisService().analyzeAndNormalize(imagePath)
    assert result.orientationDegrees == 90
    assert result.text == 'Tecido conjuntivo sustenta e conecta estruturas'
    assert result.confidence == 95 and result.wordCount == 6
