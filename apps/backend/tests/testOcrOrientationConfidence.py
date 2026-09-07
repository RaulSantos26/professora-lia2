from PIL import Image
from app.services.ocrAnalysisService import OcrAnalysisService

def page(tmp_path):
    path = tmp_path / 'page.png'
    Image.new('RGB', (120, 80), 'white').save(path)
    return path

def test_wrong_osd_does_not_rotate_good_ocr(tmp_path, monkeypatch):
    path = page(tmp_path); original = path.read_bytes(); service = OcrAnalysisService()
    monkeypatch.setattr(service, '_detectOrientation', lambda _: 180)
    readings = iter([('correct', 94, 10), ('inverted', 41, 10)])
    monkeypatch.setattr(service, '_read', lambda _: next(readings))
    result = service.analyzeAndNormalize(path)
    assert result.orientationDegrees == 0 and result.text == 'correct'
    assert path.read_bytes() == original

def test_low_confidence_compares_all_and_normalizes_winner(tmp_path, monkeypatch):
    path = page(tmp_path); service = OcrAnalysisService()
    monkeypatch.setattr(service, '_detectOrientation', lambda _: 180)
    readings = iter([('bad', 25, 10), ('still bad', 35, 10), ('right', 93, 10), ('wrong', 32, 10)])
    monkeypatch.setattr(service, '_read', lambda _: next(readings))
    result = service.analyzeAndNormalize(path)
    assert result.orientationDegrees == 90 and result.text == 'right'
    with Image.open(path) as image:
        assert image.size == (80, 120)

def test_small_improvement_and_sparse_words_do_not_rotate(tmp_path, monkeypatch):
    path = page(tmp_path); original = path.read_bytes(); service = OcrAnalysisService()
    monkeypatch.setattr(service, '_detectOrientation', lambda _: 90)
    readings = iter([('baseline', 70, 10), ('small gain', 76, 10)])
    monkeypatch.setattr(service, '_read', lambda _: next(readings))
    assert service.analyzeAndNormalize(path).orientationDegrees == 0
    assert path.read_bytes() == original

def test_sparse_candidate_cannot_outvote_complete_page(tmp_path, monkeypatch):
    path = page(tmp_path); service = OcrAnalysisService()
    monkeypatch.setattr(service, '_detectOrientation', lambda _: 180)
    readings = iter([('full', 78, 30), ('one', 99, 1)])
    monkeypatch.setattr(service, '_read', lambda _: next(readings))
    assert service.analyzeAndNormalize(path).orientationDegrees == 0

def test_read_preserves_lines_paragraphs_and_confidence(monkeypatch):
    monkeypatch.setattr('app.services.ocrAnalysisService.pytesseract.image_to_data', lambda *a, **kw: {
        'text': ['Primeira', 'linha', 'Segunda', 'Parágrafo'], 'conf': ['90', '90', '90', '90'],
        'block_num': [1, 1, 1, 1], 'par_num': [1, 1, 1, 2], 'line_num': [1, 1, 2, 1]})
    text, confidence, count = OcrAnalysisService()._read(Image.new('RGB', (120, 80)))
    assert text == 'Primeira linha\nSegunda\n\nParágrafo'
    assert confidence == 90 and count == 4
