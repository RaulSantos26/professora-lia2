from app.contracts.visionAnalysisContract import VisionAnalysisContract


def testVisionContractPreservesOrientationTextAndDiagram():
    result = VisionAnalysisContract.model_validate(
        {
            "orientationDegrees": 90,
            "extractedText": "Tecido conjuntivo",
            "summary": "Página de apostila.",
            "visualElements": [
                {
                    "elementType": "DIAGRAM",
                    "title": "Tipos de tecido",
                    "description": "Diagrama educacional.",
                    "labels": [
                        "adiposo",
                        "ósseo",
                    ],
                }
            ],
        }
    )

    assert result.orientationDegrees == 90
    assert result.extractedText == "Tecido conjuntivo"
    assert result.visualElements[0].elementType == "DIAGRAM"
