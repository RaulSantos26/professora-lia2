from types import SimpleNamespace
from unittest.mock import patch
from app.services.imageReadingGuideService import ImageReadingGuideService, ReadingGuide, PREFIX

def test_guide_contract_and_position_bounds():
    import pytest
    from pydantic import ValidationError
    data=dict(introduction='Leia de cima para baixo.',steps=[dict(title='Usuário',where='Topo',explanation='Visão externa.',x=50,y=20,confidence=.9)],takeaway='São níveis do mesmo sistema.')
    assert ReadingGuide.model_validate(data).steps[0].x==50
    data['steps'][0]['x']=200
    with pytest.raises(ValidationError): ReadingGuide.model_validate(data)

def test_missing_asset_keeps_image_and_original_explanation():
    task=SimpleNamespace(imageMode='ILLUSTRATION',labelsJson=['Explicação visual: Original'],imageTaskId='test')
    ImageReadingGuideService().enrich(task,'missing-file.png')
    assert task.labelsJson[0]=='Explicação visual: Original'
    assert task.labelsJson[-1].startswith('Guia visual indisponível:')

def test_companion_does_not_start_extra_vision():
    task=SimpleNamespace(imageMode='MIND_MAP_COMPANION',labelsJson=['unchanged'])
    with patch('app.services.imageReadingGuideService.CapabilityRouterService') as router:
        ImageReadingGuideService().enrich(task,'unused')
        router.assert_not_called()
    assert task.labelsJson==['unchanged']
