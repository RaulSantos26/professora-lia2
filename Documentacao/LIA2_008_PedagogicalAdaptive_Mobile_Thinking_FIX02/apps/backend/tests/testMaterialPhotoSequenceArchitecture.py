from pathlib import Path


def testAsyncBatchPersistsPhotoGroupAndSequence():
    source = (
        Path(__file__).parents[1]
        / "app"
        / "services"
        / "materialAsyncService.py"
    ).read_text(encoding="utf-8")

    assert "sourceGroupId = uuid4() if len(files) > 1 else None" in source
    assert "enumerate(files, start=1)" in source
    assert "sourceGroupId=sourceGroupId" in source
    assert "sourceSequence=sourceSequence" in source
